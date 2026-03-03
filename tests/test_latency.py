"""
延时计算模块测试
"""

import pytest
import polars as pl
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analysis.latency import LatencyCalculator, calculate_latencies


class TestLatencyCalculator:
    """LatencyCalculator 测试类"""
    
    def test_init(self):
        """测试初始化"""
        calc = LatencyCalculator()
        assert calc.time_unit == "ns"
    
    def test_calculate_all(self):
        """测试计算所有延时指标"""
        # 创建测试数据
        df = pl.DataFrame({
            "tgwOutTime": [1000000000, 2000000000],
            "tgwBackTime": [1005000000, 2010000000],
            "rspTransactTime": [1003000000, 2008000000],
            "clientInsertReqTimestamp": [995000000, 1990000000]
        })
        
        calc = LatencyCalculator()
        result = calc.calculate_all(df)
        
        # 检查列是否存在
        assert "tgwProcessTimeMs" in result.columns
        assert "counterProcessTimeMs" in result.columns
        assert "roundTripTimeMs" in result.columns
        assert "networkLatencyMs" in result.columns
    
    def test_get_statistics(self):
        """测试获取统计"""
        df = pl.DataFrame({
            "tgwProcessTimeMs": [1.0, 2.0, 3.0, 4.0, 5.0],
            "counter": ["A", "A", "B", "B", "B"]
        })
        
        calc = LatencyCalculator()
        stats = calc.get_statistics(df, group_by="counter")
        
        assert len(stats) == 2  # 两个柜台
    
    def test_calculate_latencies(self):
        """测试便捷函数"""
        df = pl.DataFrame({
            "tgwOutTime": [1000000000],
            "tgwBackTime": [1005000000],
            "rspTransactTime": [1003000000],
            "clientInsertReqTimestamp": [995000000]
        })
        
        result = calculate_latencies(df)
        assert "tgwProcessTimeMs" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
