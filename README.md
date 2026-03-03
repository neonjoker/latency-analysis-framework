# 交易链路延时数据分析框架

基于网页的交互式分析框架，用于分析交易链路延时数据。

## 🚀 快速开始

### 环境设置

```bash
# 1. 设置 Python 环境
./specify/scripts/setup-env.sh

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 启动 API 服务
python -m src.api.main

# 4. 打开浏览器访问
open src/web/index.html
```

## 📁 项目结构

```
latency_project/
├── .specify/                 # Spec-Driven 配置
│   ├── memory/
│   │   └── constitution.md   # 项目宪法
│   ├── specs/
│   │   └── 001-web-analysis-framework/
│   │       ├── spec.md       # 功能规格
│   │       ├── plan.md       # 实现计划
│   │       └── tasks.md      # 任务列表
│   ├── scripts/
│   │   └── setup-env.sh      # 环境设置脚本
│   └── templates/            # 文档模板
├── src/                      # 源代码
│   ├── data/                 # 数据层
│   ├── analysis/             # 分析层
│   ├── visualization/        # 可视化层
│   ├── api/                  # API 层
│   └── web/                  # 前端
├── tests/                    # 测试
├── notebooks/                # Jupyter 笔记本
├── data/                     # 数据文件
└── docs/                     # 文档
```

## 🛠️ 技术栈

- **后端**: Python 3.11, FastAPI, Polars
- **前端**: HTML/CSS/JavaScript, Plotly.js
- **数据**: Parquet, PyArrow
- **测试**: pytest, mypy

## 📋 功能特性

- ✅ 交互式数据浏览和筛选
- ✅ 高延时聚集区自动检测
- ✅ 链路聚类分析
- ✅ 异常模式识别（糖葫芦现象、microburst）
- ✅ 延时归因分析
- ✅ 可视化图表展示
- ✅ 分析报告生成

## 🔧 开发命令

```bash
# 运行测试
pytest

# 类型检查
mypy src/

# 代码格式化
black src/

# 代码检查
ruff check src/

# 启动开发服务器
uvicorn src.api.main:app --reload
```

## 📖 文档

- [功能规格](.specify/specs/001-web-analysis-framework/spec.md)
- [实现计划](.specify/specs/001-web-analysis-framework/plan.md)
- [任务列表](.specify/specs/001-web-analysis-framework/tasks.md)
- [项目宪法](.specify/memory/constitution.md)

## ⚠️ 环境约束

- **必须使用 pyenv 管理 Python 版本**
- **必须在虚拟环境下运行**
- **Claude Code 只能在激活的虚拟环境中执行代码**

## 📝 License

MIT
