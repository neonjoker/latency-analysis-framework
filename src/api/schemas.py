"""
API 数据模型

使用 Pydantic 定义请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class DataQueryRequest(BaseModel):
    """数据查询请求"""
    start_date: date
    end_date: date
    counters: Optional[List[str]] = None
    columns: Optional[List[str]] = None


class DataQueryResponse(BaseModel):
    """数据查询响应"""
    success: bool
    row_count: int
    columns: List[str]
    data: List[Dict[str, Any]]
    message: Optional[str] = None


class LatencyAnalysisRequest(BaseModel):
    """延时分析请求"""
    start_date: date
    end_date: date
    counter: Optional[str] = None


class LatencyStats(BaseModel):
    """延时统计"""
    mean: float
    median: float
    std: float
    min: float
    max: float
    p95: float
    p99: float


class LatencyAnalysisResponse(BaseModel):
    """延时分析响应"""
    success: bool
    tgw_process: Optional[LatencyStats] = None
    counter_process: Optional[LatencyStats] = None
    round_trip: Optional[LatencyStats] = None
    distribution: Optional[List[Dict[str, Any]]] = None


class ClusterAnalysisResponse(BaseModel):
    """聚类分析响应"""
    success: bool
    clusters: List[Dict[str, Any]]
    similar_links: List[List[str]]


class AnomalyAnalysisResponse(BaseModel):
    """异常分析响应"""
    success: bool
    summary: Dict[str, Any]
    anomalies: Dict[str, List[Dict[str, Any]]]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    timestamp: datetime
