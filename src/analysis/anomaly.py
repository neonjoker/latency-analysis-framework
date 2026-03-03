"""
异常检测模块

检测糖葫芦现象、microburst、链路阻塞等异常模式
"""

import polars as pl
import numpy as np
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class AnomalyResult:
    """异常检测结果"""
    anomaly_type: str
    severity: str  # "low", "medium", "high"
    time_start: str
    time_end: str
    affected_links: List[str]
    description: str
    score: float  # 0-1 异常评分


class AnomalyDetector:
    """异常检测器"""
    
    def __init__(
        self,
        high_latency_threshold_ms: float = 5.0,
        microburst_window_ms: int = 5,
        microburst_count_threshold: int = 50
    ):
        """
        初始化异常检测器
        
        Args:
            high_latency_threshold_ms: 高延时阈值
            microburst_window_ms: Microburst 检测窗口（毫秒）
            microburst_count_threshold: Microburst 数量阈值
        """
        self.high_latency_threshold_ms = high_latency_threshold_ms
        self.microburst_window_ms = microburst_window_ms
        self.microburst_count_threshold = microburst_count_threshold
    
    def detect_tanghulu(
        self,
        df: pl.DataFrame,
        link_col: str = "counter",
        timestamp_col: str = "tgwBackTime",
        latency_col: str = "roundTripTimeMs"
    ) -> List[AnomalyResult]:
        """
        检测糖葫芦现象
        
        糖葫芦现象：连续的高延时数据点，可能是同一个包发出的
        
        Args:
            df: 输入 DataFrame
            link_col: 链路标识列
            timestamp_col: 时间戳列
            latency_col: 延时列
            
        Returns:
            异常结果列表
        """
        anomalies = []
        
        # 筛选高延时数据
        high_latency = df.filter(pl.col(latency_col) > self.high_latency_threshold_ms)
        
        if len(high_latency) == 0:
            return anomalies
        
        # 按链路分组
        for link in high_latency[link_col].unique().to_list():
            link_data = (
                high_latency
                .filter(pl.col(link_col) == link)
                .sort(timestamp_col)
            )
            
            # 检测连续高延时
            timestamps = link_data[timestamp_col].to_numpy()
            latencies = link_data[latency_col].to_numpy()
            
            if len(timestamps) < 3:
                continue
            
            # 计算时间间隔
            time_diffs = np.diff(timestamps)
            
            # 查找连续的小间隔（糖葫芦串）
            consecutive = []
            current_group = [0]
            
            for i in range(1, len(time_diffs)):
                # 如果时间间隔很小（< 1ms），认为是连续的
                if time_diffs[i] < 1_000_000:  # 1ms in nanoseconds
                    current_group.append(i)
                else:
                    if len(current_group) >= 3:
                        consecutive.append(current_group)
                    current_group = [i]
            
            if len(current_group) >= 3:
                consecutive.append(current_group)
            
            # 生成异常报告
            for group in consecutive:
                start_idx = group[0]
                end_idx = group[-1]
                
                anomalies.append(AnomalyResult(
                    anomaly_type="tanghulu",
                    severity="medium" if len(group) < 10 else "high",
                    time_start=str(timestamps[start_idx]),
                    time_end=str(timestamps[end_idx]),
                    affected_links=[link],
                    description=f"检测到 {len(group)} 个连续高延时点",
                    score=min(1.0, len(group) / 20)
                ))
        
        return anomalies
    
    def detect_microburst(
        self,
        df: pl.DataFrame,
        link_col: str = "counter",
        timestamp_col: str = "tgwOutTime"
    ) -> List[AnomalyResult]:
        """
        检测 Microburst
        
        短时间内大量请求
        
        Args:
            df: 输入 DataFrame
            link_col: 链路标识列
            timestamp_col: 时间戳列
            
        Returns:
            异常结果列表
        """
        anomalies = []
        
        # 按时间窗口聚合
        windowed = (
            df
            .with_columns(
                (pl.col(timestamp_col) // (self.microburst_window_ms * 1_000_000))
                .cast(pl.Int64)
                .alias("time_window")
            )
            .group_by("time_window", link_col)
            .agg(pl.col(timestamp_col).count().alias("request_count"))
            .filter(pl.col("request_count") >= self.microburst_count_threshold)
            .sort("time_window")
        )
        
        for row in windowed.iter_rows(named=True):
            window_start_ns = int(row["time_window"]) * self.microburst_window_ms * 1_000_000
            window_end_ns = window_start_ns + self.microburst_window_ms * 1_000_000
            
            anomalies.append(AnomalyResult(
                anomaly_type="microburst",
                severity="high" if row["request_count"] > 100 else "medium",
                time_start=str(window_start_ns),
                time_end=str(window_end_ns),
                affected_links=[row[link_col]],
                description=f"{self.microburst_window_ms}ms 内 {row['request_count']} 个请求",
                score=min(1.0, row["request_count"] / 200)
            ))
        
        return anomalies
    
    def detect_link_blockage(
        self,
        df: pl.DataFrame,
        link_col: str = "counter",
        tgw_out_col: str = "tgwOutTime",
        tgw_back_col: str = "tgwBackTime"
    ) -> List[AnomalyResult]:
        """
        检测链路阻塞
        
        tgwBackTime/tgwOutTime 比例异常，表明消息返回 TGW 后堵住
        
        Args:
            df: 输入 DataFrame
            link_col: 链路标识列
            tgw_out_col: TGW 发出时间
            tgw_back_col: TGW 返回时间
            
        Returns:
            异常结果列表
        """
        anomalies = []
        
        # 计算时间窗口内的比例
        windowed = (
            df
            .with_columns(
                (pl.col(tgw_back_col) // (100_000_000)).cast(pl.Int64).alias("time_bucket"),
                ((pl.col(tgw_back_col) - pl.col(tgw_out_col)) / 1_000_000).alias("back_diff_ms"),
                ((pl.col(tgw_out_col).shift(-1) - pl.col(tgw_out_col)) / 1_000_000).alias("out_diff_ms")
            )
            .filter(pl.col("out_diff_ms") > 0)
            .with_columns(
                (pl.col("back_diff_ms") / pl.col("out_diff_ms")).alias("ratio")
            )
        )
        
        # 检测比例 > 1 的情况（返回时间间隔 < 发出时间间隔）
        blockage = (
            windowed
            .filter(pl.col("ratio") > 1.5)
            .group_by(link_col, "time_bucket")
            .agg(
                pl.col("ratio").mean().alias("avg_ratio"),
                pl.col("ratio").max().alias("max_ratio"),
                pl.col("ratio").count().alias("count"),
            )
            .filter(pl.col("count") >= 3)
        )
        
        for row in blockage.iter_rows(named=True):
            anomalies.append(AnomalyResult(
                anomaly_type="link_blockage",
                severity="medium" if row["avg_ratio"] < 3 else "high",
                time_start=str(int(row["time_bucket"]) * 100_000_000),
                time_end=str(int(row["time_bucket"]) * 100_000_000 + 100_000_000),
                affected_links=[row[link_col]],
                description=f"链路阻塞检测，平均比例 {row['avg_ratio']:.2f}",
                score=min(1.0, row["avg_ratio"] / 10)
            ))
        
        return anomalies
    
    def detect_all(
        self,
        df: pl.DataFrame
    ) -> Dict[str, List[AnomalyResult]]:
        """
        检测所有异常类型
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            按类型分组的异常结果
        """
        return {
            "tanghulu": self.detect_tanghulu(df),
            "microburst": self.detect_microburst(df),
            "link_blockage": self.detect_link_blockage(df),
        }
    
    def get_summary(
        self,
        anomalies: Dict[str, List[AnomalyResult]]
    ) -> dict:
        """
        获取异常摘要
        
        Args:
            anomalies: 异常结果字典
            
        Returns:
            摘要统计
        """
        summary = {
            "total_anomalies": 0,
            "by_type": {},
            "by_severity": {"low": 0, "medium": 0, "high": 0},
            "affected_links": set()
        }
        
        for anomaly_type, results in anomalies.items():
            count = len(results)
            summary["total_anomalies"] += count
            summary["by_type"][anomaly_type] = count
            
            for result in results:
                summary["by_severity"][result.severity] += 1
                summary["affected_links"].update(result.affected_links)
        
        summary["affected_links"] = list(summary["affected_links"])
        return summary


# 便捷函数
def detect_anomalies(df: pl.DataFrame) -> Dict[str, List[AnomalyResult]]:
    """快速检测所有异常"""
    detector = AnomalyDetector()
    return detector.detect_all(df)


def get_anomaly_summary(df: pl.DataFrame) -> dict:
    """快速获取异常摘要"""
    detector = AnomalyDetector()
    anomalies = detector.detect_all(df)
    return detector.get_summary(anomalies)
