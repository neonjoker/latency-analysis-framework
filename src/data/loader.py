"""
数据加载模块

使用 Polars 高效加载 Parquet 文件
"""

import polars as pl
from pathlib import Path
from datetime import timedelta
from typing import List, Optional
from datetime import date


class ParquetLoader:
    """Parquet 文件加载器"""
    
    def __init__(self, data_dir: str = "/mnt/f/latency_project"):
        self.data_dir = Path(data_dir)
    
    def get_available_dates(self) -> List[date]:
        """获取可用的数据日期列表"""
        dates = []
        for f in self.data_dir.glob("*.parquet"):
            try:
                date_str = f.stem[:8]  # YYYYMMDD
                dates.append(date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:])))
            except (ValueError, IndexError):
                continue
        return sorted(dates)
    
    def load_file(self, date: date, columns: Optional[List[str]] = None) -> pl.DataFrame:
        """
        加载单日的 Parquet 文件
        
        Args:
            date: 数据日期
            columns: 要加载的列，None 表示全部
            
        Returns:
            Polars DataFrame
        """
        date_str = date.strftime("%Y%m%d")
        file_path = self.data_dir / f"{date_str}_target_counters.parquet"
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在：{file_path}")
        
        if columns:
            return pl.read_parquet(file_path, columns=columns)
        return pl.read_parquet(file_path)
    
    def load_date_range(
        self, 
        start_date: date, 
        end_date: date,
        columns: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """
        加载日期范围内的所有数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            columns: 要加载的列
            
        Returns:
            合并后的 DataFrame
        """
        dfs = []
        current = start_date
        while current <= end_date:
            try:
                df = self.load_file(current, columns)
                df = df.with_columns(pl.lit(current).alias("trade_date"))
                dfs.append(df)
            except FileNotFoundError:
                pass
            # 修复：去掉 .date() 调用，直接使用 timedelta
            current = current + timedelta(days=1)
        
        if not dfs:
            raise ValueError("指定范围内没有找到数据文件")
        
        return pl.concat(dfs)


# 便捷函数
def get_loader() -> ParquetLoader:
    """获取默认数据加载器"""
    return ParquetLoader()
