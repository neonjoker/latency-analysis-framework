"""
API 路由

定义 RESTful API 端点
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import polars as pl
from datetime import date
import os
from pathlib import Path

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
from .config import config, validate_folder_path

router = APIRouter()

# 当前数据目录（可动态修改）
# 默认使用配置文件中的路径，如无配置则使用当前目录
default_path = config.get_default_path()
if default_path:
    current_data_dir = Path(default_path)
else:
    current_data_dir = Path.cwd()


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


@router.get("/api/folders")
async def get_available_folders():
    """获取可用数据文件夹列表（跨平台）"""
    try:
        folders = []
        
        # 获取配置的允许根目录
        allowed_roots = config.get_allowed_roots()
        
        if allowed_roots:
            # 如果配置了允许的根目录，只扫描这些目录
            for root in allowed_roots:
                root_path = Path(root)
                if root_path.exists() and root_path.is_dir():
                    try:
                        for item in root_path.iterdir():
                            if item.is_dir():
                                parquet_count = len(list(item.glob("*.parquet")))
                                if parquet_count > 0:
                                    folders.append({
                                        "name": item.name,
                                        "path": str(item),
                                        "parquet_count": parquet_count
                                    })
                    except (PermissionError, OSError):
                        continue
        else:
            # 未配置允许根目录时，扫描常见数据位置
            scan_paths = []
            
            # Windows
            for drive in "CDEFGHIJ":
                drive_path = Path(f"{drive}:\\")
                if drive_path.exists():
                    scan_paths.append(drive_path)
            
            # Unix/Linux/macOS
            unix_paths = [
                Path("/mnt/f"),
                Path("/mnt/data"),
                Path("/data"),
                Path("/home"),
                Path("/Volumes"),  # macOS 外接驱动器
            ]
            scan_paths.extend([p for p in unix_paths if p.exists()])
            
            # 扫描这些路径
            for scan_path in scan_paths:
                try:
                    for item in scan_path.iterdir():
                        if item.is_dir():
                            parquet_count = len(list(item.glob("*.parquet")))
                            if parquet_count > 0:
                                folders.append({
                                    "name": str(item),
                                    "path": str(item),
                                    "parquet_count": parquet_count
                                })
                except (PermissionError, OSError):
                    continue
        
        # 添加当前目录（如果有 parquet 文件）
        current_parquet_count = len(list(current_data_dir.glob("*.parquet")))
        if current_parquet_count > 0:
            folders.insert(0, {
                "name": f"{current_data_dir.name} (当前)",
                "path": str(current_data_dir),
                "parquet_count": current_parquet_count
            })
        
        return {"success": True, "folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/folders/validate")
async def validate_folder(path: str):
    """验证文件夹路径（跨平台）"""
    try:
        # 使用新的跨平台验证函数
        is_valid, message = validate_folder_path(path)
        
        if is_valid:
            full_path = Path(path).resolve()
            parquet_count = len(list(full_path.glob("*.parquet")))
            return {
                "success": True,
                "valid": True,
                "path": str(full_path),
                "parquet_count": parquet_count,
                "message": message
            }
        else:
            return {
                "success": True,
                "valid": False,
                "error": message
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
    """设置当前数据文件夹（跨平台）"""
    global current_data_dir
    
    try:
        # 验证路径
        is_valid, message = validate_folder_path(path)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        full_path = Path(path).resolve()
        parquet_count = len(list(full_path.glob("*.parquet")))
        
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


@router.get("/api/counters")
async def get_available_counters():
    """获取可用柜台列表"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        dates = loader.get_available_dates()
        if not dates:
            return {"success": True, "counters": []}
        
        df = loader.load_file(dates[0])
        counters = df["counter"].unique().to_list() if "counter" in df.columns else []
        return {"success": True, "counters": counters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/data/query")
async def query_data(request: DataQueryRequest):
    """查询数据"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date, request.columns)
        
        if request.counters:
            df = df.filter(pl.col("counter").is_in(request.counters))
        
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


@router.post("/api/analyze/latency")
async def analyze_latency(request: LatencyAnalysisRequest):
    """延时分析"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date)
        
        if request.counter:
            df = df.filter(pl.col("counter") == request.counter)
        
        calc = LatencyCalculator()
        df = calc.calculate_all(df)
        stats_df = calc.get_statistics(df)
        
        def make_stats(row: dict) -> LatencyStats:
            return LatencyStats(
                mean=row.get("mean", 0) if row else 0,
                median=row.get("median", 0) if row else 0,
                std=row.get("std", 0) if row else 0,
                min=row.get("min", 0) if row else 0,
                max=row.get("max", 0) if row else 0,
                p95=row.get("p95", 0) if row else 0,
                p99=row.get("p99", 0) if row else 0
            )
        
        dist_df = calc.get_latency_distribution(df)
        
        return LatencyAnalysisResponse(
            success=True,
            tgw_process=make_stats(stats_df.row(0, named=True)) if len(stats_df) > 0 else None,
            counter_process=make_stats(stats_df.row(0, named=True)) if len(stats_df) > 0 else None,
            round_trip=make_stats(stats_df.row(0, named=True)) if len(stats_df) > 0 else None,
            distribution=dist_df.to_dicts() if len(dist_df) > 0 else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze/clustering")
async def analyze_clustering(request: LatencyAnalysisRequest):
    """聚类分析"""
    try:
        loader = ParquetLoader(str(current_data_dir))
        df = loader.load_date_range(request.start_date, request.end_date)
        
        analyzer = LatencyClusterAnalyzer()
        clusters = analyzer.identify_high_latency_clusters(df)
        similar = analyzer.calculate_link_similarity(df)
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


@router.post("/api/analyze/anomaly")
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
