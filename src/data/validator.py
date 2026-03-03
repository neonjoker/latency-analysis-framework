"""
数据验证和清洗模块

提供数据质量检查、空值检测、异常值处理等功能
"""

import polars as pl
from typing import List, Optional, Tuple
from datetime import datetime


class DataValidator:
    """数据验证器"""
    
    # 必需列
    REQUIRED_COLUMNS = [
        "clientInsertReqTimestamp",
        "tgwOutTime", 
        "tgwBackTime",
    ]
    
    # 延时列（毫秒）
    LATENCY_MS_COLUMNS = [
        "tgwProcessTime",
        "counterProcessTime",
        "roundTripTime",
    ]
    
    def __init__(self):
        self.validation_errors = []
        self.warnings = []
    
    def check_required_columns(self, df: pl.DataFrame) -> Tuple[bool, List[str]]:
        """
        检查必需列是否存在
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            (是否通过，缺失的列列表)
        """
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        return len(missing) == 0, missing
    
    def check_null_values(
        self, 
        df: pl.DataFrame,
        columns: Optional[List[str]] = None
    ) -> dict:
        """
        检查空值
        
        Args:
            df: 输入 DataFrame
            columns: 要检查的列，None 表示检查所有列
            
        Returns:
            每列的空值数量统计
        """
        cols = columns or df.columns
        null_counts = {}
        for col in cols:
            if col in df.columns:
                null_counts[col] = df[col].null_count()
        return null_counts
    
    def check_timestamp_format(
        self, 
        df: pl.DataFrame,
        timestamp_col: str = "clientInsertReqTimestamp"
    ) -> Tuple[bool, int]:
        """
        检查时间戳格式
        
        Args:
            df: 输入 DataFrame
            timestamp_col: 时间戳列名
            
        Returns:
            (是否有效，无效行数)
        """
        if timestamp_col not in df.columns:
            return False, len(df)
        
        # 检查是否有负值或异常大的值
        try:
            invalid = df.filter(
                (pl.col(timestamp_col) < 0) | 
                (pl.col(timestamp_col) > 9999999999999)
            ).height
            return invalid == 0, invalid
        except Exception:
            return False, len(df)
    
    def detect_outliers(
        self,
        df: pl.DataFrame,
        column: str,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pl.DataFrame:
        """
        检测异常值
        
        Args:
            df: 输入 DataFrame
            column: 要检测的列
            method: 方法 ("iqr" 或 "zscore")
            threshold: 阈值
            
        Returns:
            标记异常值的 DataFrame（添加 is_outlier 列）
        """
        if column not in df.columns:
            return df.with_columns(pl.lit(False).alias("is_outlier"))
        
        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            
            return df.with_columns(
                ((pl.col(column) < lower) | (pl.col(column) > upper)).alias("is_outlier")
            )
        
        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()
            if std == 0:
                return df.with_columns(pl.lit(False).alias("is_outlier"))
            
            z_scores = ((pl.col(column) - mean) / std).abs()
            return df.with_columns(
                (z_scores > threshold).alias("is_outlier")
            )
        
        else:
            raise ValueError(f"未知的方法：{method}")
    
    def clean_data(
        self,
        df: pl.DataFrame,
        remove_nulls: bool = True,
        remove_outliers: bool = False,
        outlier_columns: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """
        清洗数据
        
        Args:
            df: 输入 DataFrame
            remove_nulls: 是否移除空值
            remove_outliers: 是否移除异常值
            outlier_columns: 检测异常值的列
            
        Returns:
            清洗后的 DataFrame
        """
        result = df.clone()
        
        # 移除空值
        if remove_nulls:
            result = result.drop_nulls()
        
        # 移除异常值
        if remove_outliers and outlier_columns:
            for col in outlier_columns:
                if col in result.columns:
                    result = self.detect_outliers(result, col)
                    result = result.filter(~pl.col("is_outlier"))
                    result = result.drop("is_outlier")
        
        return result
    
    def validate_full(
        self,
        df: pl.DataFrame
    ) -> dict:
        """
        完整验证
        
        Args:
            df: 输入 DataFrame
            
        Returns:
            验证报告
        """
        report = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns,
            "required_columns_ok": True,
            "missing_columns": [],
            "null_counts": {},
            "timestamp_valid": True,
            "invalid_timestamps": 0,
            "warnings": []
        }
        
        # 检查必需列
        ok, missing = self.check_required_columns(df)
        report["required_columns_ok"] = ok
        report["missing_columns"] = missing
        
        # 检查空值
        report["null_counts"] = self.check_null_values(df)
        
        # 检查时间戳
        valid, invalid = self.check_timestamp_format(df)
        report["timestamp_valid"] = valid
        report["invalid_timestamps"] = invalid
        
        # 生成警告
        if not ok:
            report["warnings"].append(f"缺少必需列：{missing}")
        if invalid > 0:
            report["warnings"].append(f"发现 {invalid} 行无效时间戳")
        
        return report


# 便捷函数
def validate(df: pl.DataFrame) -> dict:
    """快速验证数据"""
    validator = DataValidator()
    return validator.validate_full(df)


def clean(
    df: pl.DataFrame,
    remove_nulls: bool = True,
    remove_outliers: bool = False
) -> pl.DataFrame:
    """快速清洗数据"""
    validator = DataValidator()
    return validator.clean_data(df, remove_nulls, remove_outliers)
