"""
聚类分析模块

高延时聚集区检测和链路聚类分析
"""

import polars as pl
import numpy as np
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ClusterResult:
    """聚类结果"""
    cluster_id: int
    link_ids: List[str]
    time_windows: List[Tuple[str, str]]
    high_latency_count: int
    avg_latency_ms: float


class LatencyClusterAnalyzer:
    """延时聚类分析器"""
    
    def __init__(
        self,
        latency_threshold_ms: float = 5.0,
        time_window_ms: int = 100,
        min_cluster_size: int = 5
    ):
        """
        初始化聚类分析器
        
        Args:
            latency_threshold_ms: 高延时阈值（毫秒）
            time_window_ms: 时间窗口大小（毫秒）
            min_cluster_size: 最小聚类大小
        """
        self.latency_threshold_ms = latency_threshold_ms
        self.time_window_ms = time_window_ms
        self.min_cluster_size = min_cluster_size
    
    def detect_high_latency_periods(
        self,
        df: pl.DataFrame,
        latency_col: str = "roundTripTimeMs"
    ) -> pl.DataFrame:
        """
        检测高延时时间段
        
        Args:
            df: 包含延时数据的 DataFrame
            latency_col: 延时列名
            
        Returns:
            标记高延时的 DataFrame
        """
        return df.with_columns(
            (pl.col(latency_col) > self.latency_threshold_ms).alias("is_high_latency")
        )
    
    def cluster_by_time_window(
        self,
        df: pl.DataFrame,
        timestamp_col: str = "tgwBackTime"
    ) -> pl.DataFrame:
        """
        按时间窗口聚类
        
        Args:
            df: 输入 DataFrame
            timestamp_col: 时间戳列（纳秒）
            
        Returns:
            添加了 time_window_id 列的 DataFrame
        """
        # 将纳秒转换为毫秒并分窗
        return df.with_columns(
            (pl.col(timestamp_col) // (self.time_window_ms * 1_000_000))
            .cast(pl.Int64)
            .alias("time_window_id")
        )
    
    def identify_high_latency_clusters(
        self,
        df: pl.DataFrame,
        link_col: str = "counter"
    ) -> List[ClusterResult]:
        """
        识别高延时聚集区
        
        Args:
            df: 包含延时数据的 DataFrame
            link_col: 链路标识列
            
        Returns:
            聚类结果列表
        """
        # 标记高延时
        df_marked = self.detect_high_latency_periods(df)
        
        # 按时间窗口分组
        df_clustered = self.cluster_by_time_window(df_marked)
        
        # 筛选高延时窗口
        high_latency_windows = (
            df_clustered
            .filter(pl.col("is_high_latency"))
            .group_by("time_window_id", link_col)
            .agg(
                pl.col("roundTripTimeMs").mean().alias("avg_latency"),
                pl.col("roundTripTimeMs").count().alias("count"),
            )
            .filter(pl.col("count") >= self.min_cluster_size)
            .sort("time_window_id")
        )
        
        # 转换为 ClusterResult
        clusters = []
        cluster_id = 0
        
        for row in high_latency_windows.iter_rows(named=True):
            clusters.append(ClusterResult(
                cluster_id=cluster_id,
                link_ids=[row[link_col]],
                time_windows=[(str(row["time_window_id"]), str(row["time_window_id"]))],
                high_latency_count=int(row["count"]),
                avg_latency_ms=float(row["avg_latency"])
            ))
            cluster_id += 1
        
        return clusters
    
    def calculate_link_similarity(
        self,
        df: pl.DataFrame,
        link_col: str = "counter",
        latency_col: str = "roundTripTimeMs"
    ) -> pl.DataFrame:
        """
        计算链路相似度
        
        基于延时模式的相关性
        
        Args:
            df: 输入 DataFrame
            link_col: 链路标识列
            latency_col: 延时列
            
        Returns:
            相似度矩阵 DataFrame
        """
        # 按链路和时间窗口聚合
        windowed = (
            df
            .with_columns(
                (pl.col("tgwBackTime") // (100_000_000)).cast(pl.Int64).alias("time_bucket")
            )
            .group_by(link_col, "time_bucket")
            .agg(pl.col(latency_col).mean().alias("avg_latency"))
        )
        
        # 获取所有链路
        links = windowed[link_col].unique().to_list()
        
        # 计算相关系数矩阵
        similarity_data = []
        for i, link_a in enumerate(links):
            for link_b in links[i:]:
                df_a = windowed.filter(pl.col(link_col) == link_a)
                df_b = windowed.filter(pl.col(link_col) == link_b)
                
                # 合并时间桶
                merged = df_a.join(df_b, on="time_bucket", suffix="_b")
                
                if len(merged) < 3:
                    continue
                
                # 计算相关系数
                corr = np.corrcoef(
                    merged["avg_latency"].to_numpy(),
                    merged["avg_latency_b"].to_numpy()
                )[0, 1]
                
                similarity_data.append({
                    "link_a": link_a,
                    "link_b": link_b,
                    "similarity": corr if not np.isnan(corr) else 0.0,
                    "overlap_count": len(merged)
                })
        
        return pl.DataFrame(similarity_data)
    
    def merge_similar_links(
        self,
        similarity_df: pl.DataFrame,
        threshold: float = 0.8
    ) -> List[List[str]]:
        """
        合并相似链路
        
        Args:
            similarity_df: 相似度矩阵
            threshold: 相似度阈值
            
        Returns:
            链路组列表
        """
        # 筛选高相似度对
        similar_pairs = (
            similarity_df
            .filter(pl.col("similarity") >= threshold)
            .filter(pl.col("link_a") != pl.col("link_b"))
        )
        
        # 使用并查集合并
        parent = {}
        
        def find(x):
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # 合并相似链路
        for row in similar_pairs.iter_rows(named=True):
            union(row["link_a"], row["link_b"])
        
        # 分组
        groups = {}
        for link in similarity_df["link_a"].unique().to_list() + similarity_df["link_b"].unique().to_list():
            root = find(link)
            if root not in groups:
                groups[root] = []
            groups[root].append(link)
        
        return [g for g in groups.values() if len(g) > 1]


# 便捷函数
def find_high_latency_clusters(
    df: pl.DataFrame,
    threshold_ms: float = 5.0
) -> List[ClusterResult]:
    """快速查找高延时聚集区"""
    analyzer = LatencyClusterAnalyzer(latency_threshold_ms=threshold_ms)
    return analyzer.identify_high_latency_clusters(df)


def analyze_link_similarity(
    df: pl.DataFrame,
    similarity_threshold: float = 0.8
) -> List[List[str]]:
    """快速分析链路相似度并合并"""
    analyzer = LatencyClusterAnalyzer()
    similarity = analyzer.calculate_link_similarity(df)
    return analyzer.merge_similar_links(similarity, similarity_threshold)
