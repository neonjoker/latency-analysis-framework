# Spec-Driven 工作流配置指南

## 📦 已创建的文件结构

```
latency_project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # 项目宪法
│   ├── specs/
│   │   └── 001-web-analysis-framework/
│   │       ├── spec.md              # 功能规格
│   │       ├── plan.md              # 实现计划
│   │       └── tasks.md             # 任务列表
│   ├── scripts/
│   │   └── setup-env.sh             # 环境设置
│   └── templates/                   # 文档模板
├── .claude/
│   └── commands/
│       └── speckit.md               # Slash commands
├── requirements.txt                  # Python 依赖
├── README.md                         # 项目说明
└── SPEC_SETUP_GUIDE.md               # 本文件
```

## 🚀 使用流程

### 1. 环境设置

```bash
cd /mnt/f/latency_project

# 运行环境设置脚本
./specify/scripts/setup-env.sh

# 激活虚拟环境
source .venv/bin/activate
```

### 2. 启动 Claude Code

```bash
# 确保在虚拟环境下
claude
```

### 3. 使用 Speckit 命令

在 Claude Code 中，使用以下命令：

```
/speckit.constitution    # 查看项目原则
/speckit.specify         # 定义功能需求
/speckit.plan            # 创建实现计划
/speckit.tasks           # 生成任务列表
/speckit.implement       # 执行实现
```

### 4. 开发新功能的完整流程

```
1. /speckit.specify [功能描述]
   → 创建 spec.md，定义用户故事和验收标准

2. /speckit.plan [技术栈要求]
   → 创建 plan.md，定义架构和实现步骤

3. /speckit.tasks
   → 创建 tasks.md，分解为具体任务

4. /speckit.implement
   → 按任务顺序执行实现

5. 测试和验证
   → 运行 pytest，检查功能
```

## 📋 现有规格

### 001-web-analysis-framework

已创建的规格文档：

| 文档 | 内容 |
|------|------|
| `spec.md` | 5 个用户故事，6 个功能需求 |
| `plan.md` | 6 个 Phase，详细实现步骤 |
| `tasks.md` | 18 个具体任务，带验收标准 |

**功能范围：**
- 数据浏览与探索
- 高延时聚集区检测
- 链路归因分析
- 异常检测与告警
- 报告生成

## ⚠️ 重要约束

### 环境约束
- ✅ 必须使用 pyenv 管理 Python 版本
- ✅ 必须使用 venv 创建虚拟环境
- ⚠️ **Claude Code 只能在虚拟环境下执行代码**

### 代码约束
- ✅ 模块化设计，减少重复
- ✅ 类型注解必需
- ✅ 单元测试覆盖核心功能
- ✅ 遵循 constitution.md 原则

## 🔧 常用命令

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行测试
pytest tests/ -v

# 类型检查
mypy src/

# 代码格式化
black src/

# 启动 API 服务
uvicorn src.api.main:app --reload

# 检查项目状态
/speckit.check
```

## 📖 参考文档

- [Spec-Driven 方法论](https://github.com/github/spec-kit)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Polars 文档](https://pola.rs/)
- [Plotly.js 文档](https://plotly.com/javascript/)
