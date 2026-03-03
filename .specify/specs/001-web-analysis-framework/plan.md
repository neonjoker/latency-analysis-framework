# 实现计划：网页版交易链路延时数据分析框架

## 技术栈

### 后端
- Python 3.11+ (pyenv 管理)
- Polars (数据处理)
- PyArrow (Parquet 读写)
- FastAPI (API 服务)
- Pydantic (数据验证)

### 前端
- HTML5/CSS3/JavaScript (原生)
- Plotly.js (图表)
- Tailwind CSS (样式，CDN)

### 开发工具
- pytest (测试)
- mypy (类型检查)
- black (格式化)
- ruff (lint)

## 架构设计

### 组件图
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  FastAPI    │────▶│   Data      │
│  (HTML/JS)  │◀────│    API      │◀────│   Layer     │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Analysis   │     │  Parquet    │
                    │   Engine    │     │   Files     │
                    └─────────────┘     └─────────────┘
```

### 目录结构
```
src/
├── __init__.py
├── data/
│   ├── __init__.py
│   ├── loader.py          # 数据加载
│   └── validator.py       # 数据验证
├── analysis/
│   ├── __init__.py
│   ├── latency.py         # 延时计算
│   ├── clustering.py      # 聚类分析
│   └── anomaly.py         # 异常检测
├── visualization/
│   ├── __init__.py
│   ├── charts.py          # 图表生成
│   └── templates.py       # 图表模板
├── api/
│   ├── __init__.py
│   ├── routes.py          # API 路由
│   └── schemas.py         # 数据模型
└── web/
    ├── index.html         # 主页面
    ├── app.js             # 前端逻辑
    └── styles.css         # 样式
```

## 实现步骤

### Phase 1: 数据层 (2 天)
- [ ] 创建项目结构和虚拟环境
- [ ] 实现 Parquet 数据加载器
- [ ] 实现数据验证和清洗
- [ ] 编写单元测试

### Phase 2: 分析层 (3 天)
- [ ] 实现延时计算模块
- [ ] 实现聚类算法（高延时聚集区检测）
- [ ] 实现异常检测算法
- [ ] 编写单元测试和集成测试

### Phase 3: API 层 (2 天)
- [ ] 创建 FastAPI 应用
- [ ] 实现数据查询 API
- [ ] 实现分析结果 API
- [ ] API 文档和测试

### Phase 4: 可视化层 (2 天)
- [ ] 实现图表生成函数
- [ ] 创建图表模板
- [ ] 编写可视化测试

### Phase 5: 前端层 (3 天)
- [ ] 创建 HTML 主页面
- [ ] 实现前端交互逻辑
- [ ] 集成图表展示
- [ ] 响应式设计适配

### Phase 6: 集成与优化 (2 天)
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善
- [ ] 代码审查和重构

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 大数据量性能问题 | 中 | 高 | 使用 Polars，增量加载，缓存 |
| 前端图表渲染慢 | 中 | 中 | 数据采样，Web Worker |
| 内存溢出 | 低 | 高 | 流式处理，分块加载 |

## 测试计划

### 单元测试
- 数据加载器测试
- 延时计算测试
- 聚类算法测试
- API 端点测试

### 集成测试
- 数据加载→分析→API 全流程
- 前端→API→后端全流程

### 性能测试
- 100 万行数据处理性能
- 并发 API 请求测试

## 环境设置

```bash
# 1. 设置 Python 版本
pyenv install 3.11.8
pyenv local 3.11.8

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
pytest
mypy src/
```
