"""
延时计算模块

计算各类延时指标：TGW 处理延时、柜台处理延时、往返延时等
"""

import polars as pl
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class LatencyMetrics:
    """延时指标数据类"""
    tgw_process_ms: str  # TGW 处理延时
    counter_process_ms: str  # 柜台处理延时
    round_trip_ms: str  # 往返延时
    network_latency_ms: str  # 网络延时


class LatencyCalculator:
    """延时计算器"""
    
    # 时间戳列（纳秒）
    TS_TGW_OUT = "tgwOutTime"
    TS_TGW_BACK = "tgwBackTime"
    TS_COUNTER = "rspTransactTime"
    TS_CLIENT = "clientInsertReqTimestamp"
    
    def __init__(self, time_unit: str = "ns"):
        """
        初始化延时计算器
        
        Args:
            time_unit: 时间单位 ("ns"=纳秒，"us"=微秒，"ms"=毫秒)
        """
        self.time_unit = time_unit
        self.unit_multipliers = {
            "ns": 1,
            "us": 1_000,
            "ms": 1_000_000
        }
    
    def _to_milliseconds(self, col: str) -> pl.Expr:
        """将时间列转换为毫秒"""
        multiplier = self.unit_multipliers[self.time_unit]
        return (pl.col(col) / multiplier).cast(pl.Float64)
    
    def calculate_tgw_process_time(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        计算 TGW 处理延时
        
        TGW 处理延时 = tgwBackTime - tgwOutTime
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            添加了 tgwProcessTimeMs 列的 DataFrame
        """
        return df.with_columns(
            (
                (pl.col(self.TS_TGW_BACK) - pl.col(self.TS_TGW_OUT)) 
                / self.unit_multipliers[self.time_unit]
            ).alias("tgwProcessTimeMs")
        )
    
    def calculate_counter_process_time(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        计算柜台处理延时
        
        柜台处理延时 = rspTransactTime - tgwOutTime
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            添加了 counterProcessTimeMs 列的 DataFrame
        """
        if self.TS_COUNTER not in df.columns:
            return df.with_columns(pl.lit(None).alias("counterProcessTimeMs"))
        
        return df.with_columns(
            (
                (pl.col(self.TS_COUNTER) - pl.col(self.TS_TGW_OUT)) 
                / self.unit_multipliers[self.time_unit]
            ).alias("counterProcessTimeMs")
        )
    
    def calculate_round_trip_time(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        计算往返延时
        
        往返延时 = tgwBackTime - clientInsertReqTimestamp
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            添加了 roundTripTimeMs 列的 DataFrame
        """
        return df.with_columns(
            (
                (pl.col(self.TS_TGW_BACK) - pl.col(self.TS_CLIENT)) 
                / self.unit_multipliers[self.time_unit]
            ).alias("roundTripTimeMs")
        )
    
    def calculate_network_latency(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        计算网络延时（估算）
        
        网络延时 ≈ (tgwBackTime - tgwOutTime) / 2
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            添加了 networkLatencyMs 列的 DataFrame
        """
        return df.with_columns(
            (
                (pl.col(self.TS_TGW_BACK) - pl.col(self.TS_TGW_OUT)) 
                / (2 * self.unit_multipliers[self.time_unit])
            ).alias("networkLatencyMs")
        )
    
    def calculate_all(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        计算所有延时指标
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            添加了所有延时指标列的 DataFrame
        """
        result = df
        result = self.calculate_tgw_process_time(result)
        result = self.calculate_counter_process_time(result)
        result = self.calculate_round_trip_time(result)
        result = self.calculate_network_latency(result)
        return result
    
    def get_statistics(
        self,
        df: pl.DataFrame,
        group_by: Optional[str] = None
    ) -> pl.DataFrame:
        """
        获取延时统计
        
        Args:
            df: 包含延时指标的 DataFrame
            group_by: 分组列（如 "counter"）
            
        Returns:
            统计结果 DataFrame
        """
        latency_cols = [
            "tgwProcessTimeMs",
            "counterProcessTimeMs", 
            "roundTripTimeMs",
            "networkLatencyMs"
        ]
        
        # 过滤存在的列
        existing_cols = [c for c in latency_cols if c in df.columns]
        
        if not existing_cols:
            raise ValueError("没有找到延时指标列，请先运行 calculate_all()")
        
        # 构建统计表达式
        stats_exprs = []
        for col in existing_cols:
            stats_exprs.extend([
                pl.col(col).mean().alias(f"{col}_mean"),
                pl.col(col).median().alias(f"{col}_median"),
                pl.col(col).std().alias(f"{col}_std"),
                pl.col(col).min().alias(f"{col}_min"),
                pl.col(col).max().alias(f"{col}_max"),
                pl.col(col).quantile(0.95).alias(f"{col}_p95"),
                pl.col(col).quantile(0.99).alias(f"{col}_p99"),
            ])
        
        if group_by and group_by in df.columns:
            return df.group_by(group_by).agg(stats_exprs)
        else:
            return df.select(stats_exprs)
    
    def get_latency_distribution(
        self,
        df: pl.DataFrame,
        column: str = "roundTripTimeMs",
        bins: int = 50
    ) -> pl.DataFrame:
        """
        获取延时分布
        
        Args:
            df: 输入 DataFrame
            column: 延时列名
            bins: 分箱数量
            
        Returns:
            分布数据 DataFrame
        """
        if column not in df.columns:
            raise ValueError(f"列 {column} 不存在")
        
        # 创建分箱
        min_val = df[column].min()
        max_val = df[column].max()
        
        if min_val is None or max_val is None:
            return pl.DataFrame()
        
        bin_width = (max_val - min_val) / bins
        
        return (
            df
            .with_columns(
                ((pl.col(column) - min_val) / bin_width).floor().cast(pl.Int32).alias("bin")
            )
            .group_by("bin")
            .agg(
                pl.col(column).count().alias("count"),
                pl.col(column).mean().alias("mean_latency"),
            )
            .sort("bin")
            .with_columns(
                (pl.col("bin") * bin_width + min_val).alias("bin_start"),
                ((pl.col("bin") + 1) * bin_width + min_val).alias("bin_end"),
            )
        )


# 便捷函数
def calculate_latencies(df: pl.DataFrame) -> pl.DataFrame:
    """快速计算所有延时指标"""
    calculator = LatencyCalculator()
    return calculator.calculate_all(df)


def get_latency_stats(df: pl.DataFrame, group_by: Optional[str] = None) -> pl.DataFrame:
    """快速获取延时统计"""
    calculator = LatencyCalculator()
    return calculator.get_statistics(df, group_by)
