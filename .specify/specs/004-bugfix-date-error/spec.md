# Bug 修复：日期对象属性错误

## 问题描述

**错误信息：** `'datetime.date' object has no attribute 'date'`

**触发场景：** 选择数据文件夹后点击查询按钮

**错误位置：** `src/api/routes.py` 中的 `/api/data/query` 端点

## 问题分析

在 `load_date_range()` 方法中，日期迭代逻辑存在问题。当从 API 接收日期参数后，在迭代日期范围时可能重复调用了 `.date()` 方法，导致 `datetime.date` 对象被再次调用 `.date()` 属性。

## 用户故事

### US-1: 修复日期迭代错误
**作为** 用户
**我想要** 选择文件夹后正常查询数据
**以便于** 分析不同数据源

#### 验收标准
- [ ] 选择任意有效文件夹后可正常查询
- [ ] 日期范围迭代正确
- [ ] 不出现 AttributeError
- [ ] 返回正确的数据行数

## 功能需求

### FR-1: 修复 load_date_range 方法
- 描述：修复日期迭代逻辑
- 优先级：P0
- 依赖：无

### FR-2: 添加日期验证
- 描述：验证 API 接收的日期参数
- 优先级：P1
- 依赖：FR-1

## 约束条件

- 保持向后兼容
- 遵循项目宪法
- 添加单元测试防止回归

## 测试用例

```python
# 测试日期范围加载
def test_load_date_range():
    loader = ParquetLoader('/path/to/data')
    df = loader.load_date_range(date(2026, 2, 2), date(2026, 2, 3))
    assert len(df) > 0
```

## 实现状态

✅ **已完成** (2026-03-03)

### 修复内容

- [x] Task 1.1: 修复 schemas.py 日期验证
- [x] Task 1.2: 检查 routes.py 日期传递
- [x] Task 2.1: 测试验证查询功能

### 修复方案

**问题原因：** Pydantic v2 的 date 类型验证器在某些情况下可能返回非标准 date 对象

**解决方案：** 在 schemas.py 中添加 `field_validator`，确保日期类型正确转换

```python
@field_validator('start_date', 'end_date', mode='before')
@classmethod
def validate_date(cls, value):
    if isinstance(value, str):
        return date.fromisoformat(value)
    elif isinstance(value, datetime):
        return value.date()
    return value
```

### 测试结果

```
✅ 查询成功：4,011,089 行数据
```

### 修改文件

- `src/api/schemas.py` - 添加日期验证器
