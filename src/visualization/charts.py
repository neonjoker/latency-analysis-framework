"""
可视化图表模块

使用 Plotly 生成图表
"""

import plotly.graph_objects as go
import plotly.express as px
import polars as pl
from typing import Optional, List, Dict, Any


def create_latency_histogram(
    df: pl.DataFrame,
    column: str = "roundTripTimeMs",
    title: str = "延时分布直方图",
    bins: int = 50
) -> go.Figure:
    """
    创建延时分布直方图
    
    Args:
        df: 包含延时数据的 DataFrame
        column: 延时列名
        title: 图表标题
        bins: 分箱数量
        
    Returns:
        Plotly Figure
    """
    fig = px.histogram(
        df,
        x=column,
        nbins=bins,
        title=title,
        labels={column: "延时 (ms)"},
        opacity=0.75
    )
    
    fig.update_layout(
        showlegend=False,
        hovermode="x unified"
    )
    
    return fig


def create_latency_timeseries(
    df: pl.DataFrame,
    timestamp_col: str = "tgwBackTime",
    latency_col: str = "roundTripTimeMs",
    group_col: Optional[str] = None,
    title: str = "延时时间序列"
) -> go.Figure:
    """
    创建延时时间序列图
    
    Args:
        df: 输入 DataFrame
        timestamp_col: 时间戳列
        latency_col: 延时列
        group_col: 分组列（如 counter）
        title: 图表标题
        
    Returns:
        Plotly Figure
    """
    # 转换时间戳为可读格式
    df_plot = df.with_columns(
        (pl.col(timestamp_col) // 1_000_000).alias("timestamp_ms")
    )
    
    if group_col and group_col in df.columns:
        fig = px.line(
            df_plot.to_pandas(),
            x="timestamp_ms",
            y=latency_col,
            color=group_col,
            title=title,
            labels={"timestamp_ms": "时间", latency_col: "延时 (ms)"}
        )
    else:
        fig = px.scatter(
            df_plot.to_pandas(),
            x="timestamp_ms",
            y=latency_col,
            title=title,
            labels={"timestamp_ms": "时间", latency_col: "延时 (ms)"},
            opacity=0.5
        )
    
    fig.update_layout(showlegend=True)
    return fig


def create_heatmap(
    df: pl.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    title: str = "热力图"
) -> go.Figure:
    """
    创建热力图
    
    Args:
        df: 输入 DataFrame
        x_col: X 轴列
        y_col: Y 轴列
        z_col: Z 轴（颜色）列
        title: 图表标题
        
    Returns:
        Plotly Figure
    """
    # 聚合数据
    pivot = df.group_by(x_col, y_col).agg(pl.col(z_col).mean())
    
    fig = px.density_heatmap(
        pivot.to_pandas(),
        x=x_col,
        y=y_col,
        z=z_col,
        title=title
    )
    
    return fig


def create_scatter_plot(
    df: pl.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: str = "散点图"
) -> go.Figure:
    """
    创建散点图
    
    Args:
        df: 输入 DataFrame
        x_col: X 轴列
        y_col: Y 轴列
        color_col: 颜色列
        title: 图表标题
        
    Returns:
        Plotly Figure
    """
    fig = px.scatter(
        df.to_pandas(),
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        opacity=0.6
    )
    
    # 添加 y=x 参考线
    fig.add_shape(
        type="line",
        x0=df[x_col].min(),
        y0=df[x_col].min(),
        x1=df[x_col].max(),
        y1=df[x_col].max(),
        line=dict(color="red", dash="dash"),
    )
    
    return fig


def create_box_plot(
    df: pl.DataFrame,
    value_col: str,
    group_col: str,
    title: str = "延时箱线图"
) -> go.Figure:
    """
    创建箱线图
    
    Args:
        df: 输入 DataFrame
        value_col: 值列
        group_col: 分组列
        title: 图表标题
        
    Returns:
        Plotly Figure
    """
    fig = px.box(
        df.to_pandas(),
        x=group_col,
        y=value_col,
        title=title,
        labels={group_col: "柜台", value_col: "延时 (ms)"}
    )
    
    fig.update_layout(showlegend=False)
    return fig


def create_latency_summary_chart(
    stats: Dict[str, float],
    title: str = "延时统计摘要"
) -> go.Figure:
    """
    创建延时统计摘要图
    
    Args:
        stats: 统计字典
        title: 图表标题
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    metrics = ["mean", "median", "p95", "p99"]
    values = [stats.get(m, 0) for m in metrics]
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=values,
        marker_color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="指标",
        yaxis_title="延时 (ms)",
        showlegend=False
    )
    
    return fig


# 图表模板
def get_chart_template() -> str:
    """获取图表模板名称"""
    return "plotly_white"


def apply_theme(fig: go.Figure) -> go.Figure:
    """
    应用主题到图表
    
    Args:
        fig: Plotly Figure
        
    Returns:
        应用主题后的 Figure
    """
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", size=12),
        hovermode="x unified"
    )
    return fig
