# Claude Code 配置

## 环境要求

### Python 环境
```bash
# 必须使用 pyenv 管理 Python 版本
pyenv install 3.11.8  # 如未安装
pyenv local 3.11.8

# 创建虚拟环境（仅在项目根目录）
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 约束条件
- ⚠️ **Claude Code 只能在虚拟环境下执行代码**
- ⚠️ **禁止在系统 Python 环境下安装包**
- ⚠️ **所有 Python 命令必须激活虚拟环境**

## 项目结构

```
latency_project/
├── .specify/                 # Spec-Driven 配置
│   ├── memory/
│   │   └── constitution.md   # 项目宪法
│   ├── scripts/              # 自动化脚本
│   ├── specs/                # 功能规格文档
│   └── templates/            # 文档模板
├── .venv/                    # Python 虚拟环境
├── src/                      # 源代码
│   ├── data/                 # 数据层
│   ├── analysis/             # 分析层
│   ├── visualization/        # 可视化层
│   └── web/                  # Web 层
├── tests/                    # 测试
├── notebooks/                # Jupyter 笔记本
├── data/                     # 数据文件
│   └── parquet/              # Parquet 数据
└── docs/                     # 文档
```

## 开发工作流

### Spec-Driven 流程
1. `/speckit.constitution` - 查看项目原则
2. `/speckit.specify` - 定义功能需求
3. `/speckit.plan` - 创建技术实现计划
4. `/speckit.tasks` - 生成任务列表
5. `/speckit.implement` - 执行实现

### 代码执行约束
```bash
# ✅ 正确：在虚拟环境下执行
source .venv/bin/activate && python script.py

# ❌ 错误：直接使用系统 Python
python script.py
```

## 数据源

### Parquet 文件位置
- `/mnt/f/latency_project/*.parquet` - 交易链路延时数据
- 文件格式：`YYYYMMDD_target_counters.parquet`
- 数据包含：委托时间、TGw 时间、柜台时间、延时指标

### 数据模式
主要字段：
- `clientInsertReqTimestamp` - 客户端请求时间
- `tgwOutTime` - TGW 发出时间
- `tgwBackTime` - TGW 返回时间
- `rspTransactTime` - 柜台处理时间
- `order_id` - 订单 ID
- `counter` - 柜台标识

## 技术栈

### 后端
- Python 3.11+
- Polars (数据处理)
- PyArrow (Parquet 读写)
- FastAPI (API 服务)

### 前端
- HTML/CSS/JavaScript (原生优先)
- Plotly.js (图表可视化)
- Tailwind CSS (样式)

### 开发工具
- pytest (测试)
- mypy (类型检查)
- black (代码格式化)
- ruff (代码检查)
