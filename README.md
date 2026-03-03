# 交易链路延时数据分析框架

基于网页的交互式分析框架，用于分析交易链路延时数据。

**🌍 跨平台支持：** Windows / macOS / Linux

**📦 GitHub:** https://github.com/neonjoker/latency-analysis-framework

---

## 🚀 快速开始

### Linux / macOS

```bash
# 1. 克隆项目
git clone https://github.com/neonjoker/latency-analysis-framework.git
cd latency-analysis-framework

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动 API 服务
uvicorn src.api.main:app --host 0.0.0.0 --port 10737

# 5. 启动前端（新终端）
cd src/web
python3 -m http.server 10738

# 6. 访问
# http://localhost:10738
```

### Windows (PowerShell)

```powershell
# 1. 克隆项目
git clone https://github.com/neonjoker/latency-analysis-framework.git
cd latency-analysis-framework

# 2. 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动 API 服务
uvicorn src.api.main:app --host 0.0.0.0 --port 10737

# 5. 启动前端（新终端）
cd src\web
python -m http.server 10738

# 6. 访问
# http://localhost:10738
```

---

## 📁 项目结构

```
latency-analysis-framework/
├── .specify/                     # Spec-Driven 配置
│   ├── memory/
│   │   └── constitution.md       # 项目宪法
│   ├── specs/
│   │   ├── 001-web-analysis-framework/
│   │   │   ├── spec.md           # 功能规格
│   │   │   ├── plan.md           # 实现计划
│   │   │   └── tasks.md          # 任务列表
│   │   └── 002-data-folder-selection/
│   │   │   ├── spec.md           # 文件夹选择规格
│   │   │   ├── plan.md           # 实现计划
│   │   │   └── tasks.md          # 任务列表
│   │   └── 003-cross-platform-folders/
│   │       ├── spec.md           # 跨平台支持规格
│   │       ├── plan.md           # 实现计划
│   │       └── tasks.md          # 任务列表
│   └── scripts/
│       └── setup-env.sh          # 环境设置脚本
├── src/                          # 源代码
│   ├── data/                     # 数据层
│   ├── analysis/                 # 分析层
│   ├── visualization/            # 可视化层
│   ├── api/                      # API 层
│   │   ├── routes.py             # API 路由
│   │   ├── config.py             # 配置管理（跨平台）
│   │   └── schemas.py            # 数据模型
│   └── web/                      # 前端
│       ├── index.html            # 主页面
│       ├── app.js                # 前端逻辑
│       └── styles.css            # 样式
├── tests/                        # 测试
├── config.json                   # 配置文件（跨平台）
├── requirements.txt              # Python 依赖
├── README.md                     # 本文件
├── USAGE_GUIDE.md                # 使用指南
└── DEVELOPMENT_REPORT.md         # 开发报告
```

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端** | Python 3.11+, FastAPI, Polars, PyArrow |
| **前端** | HTML/CSS/JavaScript, Plotly.js, Tailwind CSS |
| **数据** | Parquet 文件格式 |
| **测试** | pytest, mypy, black, ruff |
| **部署** | Uvicorn, 跨平台支持 |

---

## 📋 功能特性

### 核心功能
- ✅ 交互式数据浏览和筛选
- ✅ 高延时聚集区自动检测
- ✅ 链路聚类分析
- ✅ 异常模式识别（糖葫芦现象、microburst、链路阻塞）
- ✅ 延时归因分析
- ✅ 可视化图表展示
- ✅ 分析报告生成

### 跨平台功能（新增）
- ✅ **Windows/macOS/Linux 支持** - 任意有效路径
- ✅ **数据文件夹选择** - 网页界面选择数据源
- ✅ **路径安全验证** - 防止路径遍历攻击
- ✅ **配置文件支持** - 自定义允许/禁止目录

---

## 🔧 配置

### config.json

```json
{
  "data_folders": {
    "allowed_roots": [],
    "forbidden_dirs": [
      "C:\\Windows",
      "C:\\Program Files",
      "/System",
      "/etc",
      "/usr"
    ],
    "default_path": ""
  },
  "api": {
    "host": "0.0.0.0",
    "port": 10737
  }
}
```

**配置说明：**
- `allowed_roots`: 允许的根目录列表（空表示允许所有绝对路径）
- `forbidden_dirs`: 禁止访问的目录黑名单
- `default_path`: 默认数据路径

---

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

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [USAGE_GUIDE.md](USAGE_GUIDE.md) | 完整使用指南 |
| [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md) | 开发报告 |
| [.specify/specs/001-web-analysis-framework/](.specify/specs/001-web-analysis-framework/) | 主功能规格 |
| [.specify/specs/002-data-folder-selection/](.specify/specs/002-data-folder-selection/) | 文件夹选择规格 |
| [.specify/specs/003-cross-platform-folders/](.specify/specs/003-cross-platform-folders/) | 跨平台支持规格 |
| [.specify/memory/constitution.md](.specify/memory/constitution.md) | 项目宪法 |

---

## 🌐 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/dates` | GET | 获取可用日期 |
| `/api/counters` | GET | 获取柜台列表 |
| `/api/data/query` | POST | 数据查询 |
| `/api/analyze/latency` | POST | 延时分析 |
| `/api/analyze/clustering` | POST | 聚类分析 |
| `/api/analyze/anomaly` | POST | 异常检测 |
| `/api/folders` | GET | 获取文件夹列表 |
| `/api/folders/validate` | POST | 验证文件夹路径 |
| `/api/folders/set` | POST | 设置当前文件夹 |

**API 文档：** http://localhost:10737/docs

---

## ⚠️ 环境约束

- **必须使用虚拟环境** (`.venv/`)
- **Python 3.11+**
- **数据文件**：需要 parquet 格式的交易链路延时数据

---

## 📝 License

MIT License

---

## 🙏 致谢

基于 Spec-Driven Development 流程开发，遵循 [GitHub spec-kit](https://github.com/github/spec-kit) 规范。
