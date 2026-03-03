# Speckit Commands for Claude Code

## 可用命令

### /speckit.constitution
查看项目宪法和开发原则。

**用法:**
```
/speckit.constitution
```

**操作:**
1. 读取 `.specify/memory/constitution.md`
2. 显示核心原则和约束
3. 提醒环境要求（pyenv + venv）

---

### /speckit.specify
创建或更新功能规格文档。

**用法:**
```
/speckit.specify [功能描述]
```

**示例:**
```
/speckit.specify 添加实时数据流支持
```

**操作:**
1. 创建新规格目录 `.specify/specs/XXX-feature-name/`
2. 生成 `spec.md` 使用模板
3. 定义用户故事和验收标准

---

### /speckit.plan
创建技术实现计划。

**用法:**
```
/speckit.plan [技术栈和架构要求]
```

**示例:**
```
/speckit.plan 使用 FastAPI 作为后端，Plotly.js 作为前端图表库
```

**操作:**
1. 读取对应的 `spec.md`
2. 创建 `plan.md` 使用模板
3. 定义架构设计和实现步骤

---

### /speckit.tasks
生成任务列表。

**用法:**
```
/speckit.tasks
```

**操作:**
1. 读取 `plan.md`
2. 生成 `tasks.md` 使用模板
3. 分解为可执行任务

---

### /speckit.implement
执行实现任务。

**用法:**
```
/speckit.implement
```

**操作:**
1. 验证前置条件（constitution, spec, plan, tasks）
2. 按顺序执行任务
3. 更新任务状态

**约束:**
- ⚠️ 必须在虚拟环境下执行 Python 命令
- ⚠️ 执行前检查 `source .venv/bin/activate`

---

### /speckit.check
检查项目状态。

**用法:**
```
/speckit.check
```

**操作:**
1. 检查虚拟环境状态
2. 检查依赖安装
3. 检查规格文档完整性

---

### /speckit.analyze
交叉分析规格一致性。

**用法:**
```
/speckit.analyze
```

**操作:**
1. 检查 spec/plan/tasks 一致性
2. 识别缺失的需求
3. 生成分析报告

---

### /speckit.clarify
澄清未明确的需求。

**用法:**
```
/speckit.clarify
```

**操作:**
1. 识别规格中的模糊点
2. 生成澄清问题列表
3. 记录用户回答

---

## 环境检查脚本

执行任何 Python 操作前，必须运行：

```bash
# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请运行：./specify/scripts/setup-env.sh"
    exit 1
fi

# 检查是否激活
if [ "$VIRTUAL_ENV" == "" ]; then
    echo "❌ 虚拟环境未激活，请运行：source .venv/bin/activate"
    exit 1
fi
```
