"""
数据加载器测试
"""

import pytest
import polars as pl
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.loader import ParquetLoader, get_loader


class TestParquetLoader:
    """ParquetLoader 测试类"""
    
    def test_init(self):
        """测试初始化"""
        loader = ParquetLoader()
        assert loader.data_dir == Path("/mnt/f/latency_project")
    
    def test_get_available_dates(self):
        """测试获取可用日期"""
        loader = ParquetLoader()
        dates = loader.get_available_dates()
        assert isinstance(dates, list)
        # 应该有数据文件
        assert len(dates) > 0
    
    def test_load_file(self):
        """测试加载单文件"""
        loader = ParquetLoader()
        dates = loader.get_available_dates()
        
        if dates:
            df = loader.load_file(dates[0])
            assert isinstance(df, pl.DataFrame)
            assert len(df) > 0
    
    def test_load_file_with_columns(self):
        """测试加载指定列"""
        loader = ParquetLoader()
        dates = loader.get_available_dates()
        
        if dates:
            columns = ["counter", "roundTripTimeMs"]
            df = loader.load_file(dates[0], columns=columns)
            assert set(df.columns) == set(columns)
    
    def test_get_loader(self):
        """测试便捷函数"""
        loader = get_loader()
        assert isinstance(loader, ParquetLoader)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
