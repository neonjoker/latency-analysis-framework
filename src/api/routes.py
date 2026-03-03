"""
API 路由

定义 RESTful API 端点
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import polars as pl
from datetime import date

from .schemas import (
    DataQueryRequest, DataQueryResponse,
    LatencyAnalysisRequest, LatencyAnalysisResponse, LatencyStats,
    ClusterAnalysisResponse, AnomalyAnalysisResponse,
    HealthResponse
)
from ..data.loader import ParquetLoader
from ..analysis.latency import LatencyCalculator
from ..analysis.clustering import LatencyClusterAnalyzer
from ..analysis.anomaly import AnomalyDetector

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now()
    )


@router.get("/api/dates")
async def get_available_dates():
    """获取可用日期列表"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        dates = loader.get_available_dates()
        return {"success": True, "dates": [d.isoformat() for d in dates]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/counters")
async def get_available_counters():
    """获取可用柜台列表"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        # 读取一天的数据获取柜台列表
        dates = loader.get_available_dates()
        if not dates:
            return {"success": True, "counters": []}
        
        df = loader.load_file(dates[0])
        counters = df["counter"].unique().to_list() if "counter" in df.columns else []
        return {"success": True, "counters": counters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/data/query", response_model=DataQueryResponse)
async def query_data(request: DataQueryRequest):
    """查询数据"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date, request.columns)
        
        if request.counters:
            df = df.filter(pl.col("counter").is_in(request.counters))
        
        # 转换为字典列表（限制行数）
        limit = 1000
        df_limited = df.limit(limit)
        data = df_limited.to_dicts()
        
        return DataQueryResponse(
            success=True,
            row_count=len(df),
            columns=df.columns,
            data=data,
            message=f"Showing {len(data)} of {len(df)} rows"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze/latency", response_model=LatencyAnalysisResponse)
async def analyze_latency(request: LatencyAnalysisRequest):
    """延时分析"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date)
        
        if request.counter:
            df = df.filter(pl.col("counter") == request.counter)
        
        # 计算延时
        calc = LatencyCalculator()
        df = calc.calculate_all(df)
        
        # 获取统计
        stats_df = calc.get_statistics(df)
        
        def make_stats(row: dict) -> LatencyStats:
            return LatencyStats(
                mean=row.get("mean", 0),
                median=row.get("median", 0),
                std=row.get("std", 0),
                min=row.get("min", 0),
                max=row.get("max", 0),
                p95=row.get("p95", 0),
                p99=row.get("p99", 0)
            )
        
        # 获取分布
        dist_df = calc.get_latency_distribution(df)
        
        return LatencyAnalysisResponse(
            success=True,
            tgw_process=make_stats(stats_df.row(0, named=True)) if "tgwProcessTimeMs_mean" in stats_df.columns else None,
            counter_process=make_stats(stats_df.row(0, named=True)) if "counterProcessTimeMs_mean" in stats_df.columns else None,
            round_trip=make_stats(stats_df.row(0, named=True)) if "roundTripTimeMs_mean" in stats_df.columns else None,
            distribution=dist_df.to_dicts() if len(dist_df) > 0 else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze/clustering", response_model=ClusterAnalysisResponse)
async def analyze_clustering(request: LatencyAnalysisRequest):
    """聚类分析"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date)
        
        analyzer = LatencyClusterAnalyzer()
        clusters = analyzer.identify_high_latency_clusters(df)
        similar = analyzer.analyze_link_similarity(df)
        merged = analyzer.merge_similar_links(similar)
        
        return ClusterAnalysisResponse(
            success=True,
            clusters=[{
                "cluster_id": c.cluster_id,
                "link_ids": c.link_ids,
                "high_latency_count": c.high_latency_count,
                "avg_latency_ms": c.avg_latency_ms
            } for c in clusters],
            similar_links=merged
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze/anomaly", response_model=AnomalyAnalysisResponse)
async def analyze_anomaly(request: LatencyAnalysisRequest):
    """异常检测"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date)
        
        detector = AnomalyDetector()
        anomalies = detector.detect_all(df)
        summary = detector.get_summary(anomalies)
        
        return AnomalyAnalysisResponse(
            success=True,
            summary=summary,
            anomalies={
                k: [{
                    "anomaly_type": a.anomaly_type,
                    "severity": a.severity,
                    "time_start": a.time_start,
                    "time_end": a.time_end,
                    "affected_links": a.affected_links,
                    "description": a.description,
                    "score": a.score
                } for a in v]
                for k, v in anomalies.items()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据文件夹管理 ====================

import os
from pathlib import Path

# 允许的根目录
ALLOWED_ROOT = Path("/mnt/f")

# 当前数据目录（可动态修改）
current_data_dir = Path("/mnt/f/latency_project")


@router.get("/api/folders")
async def get_available_folders():
    """获取可用数据文件夹列表"""
    try:
        folders = []
        
        # 扫描 /mnt/f/ 下包含 parquet 文件的文件夹
        if ALLOWED_ROOT.exists():
            for item in ALLOWED_ROOT.iterdir():
                if item.is_dir():
                    try:
                        parquet_count = len(list(item.glob("*.parquet")))
                        if parquet_count > 0:
                            folders.append({
                                "name": item.name,
                                "path": str(item),
                                "parquet_count": parquet_count
                            })
                    except PermissionError:
                        continue
        
        # 添加默认目录
        default_folder = {
            "name": "latency_project (默认)",
            "path": str(Path("/mnt/f/latency_project")),
            "parquet_count": len(list(Path("/mnt/f/latency_project").glob("*.parquet")))
        }
        folders.insert(0, default_folder)
        
        return {"success": True, "folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/folders/validate")
async def validate_folder(path: str):
    """验证文件夹路径"""
    try:
        # 安全检查：防止路径遍历
        full_path = Path(path).resolve()
        
        # 必须在 /mnt/f/ 下
        if not str(full_path).startswith(str(ALLOWED_ROOT)):
            return {
                "success": False,
                "valid": False,
                "error": "路径必须在 /mnt/f/ 目录下"
            }
        
        # 检查是否存在
        if not full_path.exists():
            return {
                "success": True,
                "valid": False,
                "error": "文件夹不存在"
            }
        
        # 检查是否是目录
        if not full_path.is_dir():
            return {
                "success": True,
                "valid": False,
                "error": "不是目录"
            }
        
        # 统计 parquet 文件
        parquet_count = len(list(full_path.glob("*.parquet")))
        
        return {
            "success": True,
            "valid": True,
            "path": str(full_path),
            "parquet_count": parquet_count,
            "message": f"找到 {parquet_count} 个 parquet 文件"
        }
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "error": str(e)
        }


@router.get("/api/folders/current")
async def get_current_folder():
    """获取当前数据文件夹"""
    return {
        "success": True,
        "path": str(current_data_dir),
        "name": current_data_dir.name
    }


@router.post("/api/folders/set")
async def set_current_folder(path: str):
    """设置当前数据文件夹"""
    global current_data_dir
    
    try:
        # 验证路径
        full_path = Path(path).resolve()
        
        if not str(full_path).startswith(str(ALLOWED_ROOT)):
            raise HTTPException(status_code=400, detail="路径必须在 /mnt/f/ 目录下")
        
        if not full_path.exists() or not full_path.is_dir():
            raise HTTPException(status_code=400, detail="文件夹不存在或不是目录")
        
        parquet_count = len(list(full_path.glob("*.parquet")))
        if parquet_count == 0:
            raise HTTPException(status_code=400, detail="文件夹中没有 parquet 文件")
        
        current_data_dir = full_path
        
        return {
            "success": True,
            "path": str(current_data_dir),
            "name": current_data_dir.name,
            "parquet_count": parquet_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
