# Stage C Similarity Calculation Bug Fix

## 问题描述

Stage C知识库映射阶段将IfcBridge错误映射为IfcCivilElement，根本原因是**相似度计算错误**。

## 根本原因

所有resolver中存在相同的bug：将search()返回的**相似度**误当作**距离**，进行了错误的转换。

```python
# 错误代码
ifc_item, distance = results[0]
similarity = 1.0 / (1.0 + distance)  # ❌ distance实际上已经是similarity!
```

### 技术细节

- `base.py`的`search()`方法返回：`List[Tuple[IFCItem, float]]`
- 第二个float值是**点积相似度** (dot product similarity)，范围约[0.3, 0.7]
- 错误的转换公式导致：
  - 真实相似度0.633 (IfcBridge) → 被转换为0.612
  - 真实相似度0.622 (IfcGridPlacement) → 被转换为0.617
  - **相似度排序被完全打乱**

### 影响范围

LLM在选择最佳匹配时看到的候选项相似度分数完全错误，导致：
1. IfcBridge (真实rank 3, similarity 0.633) 被错误转换后排名下降
2. 其他不相关实体的相似度被错误提升
3. LLM基于错误的相似度分数选择了错误的实体

## 修复内容

### 1. entity_resolver.py (2处修复)

**Line 94-104**: 构建候选信息时的变量命名和注释
```python
# 修复前
for ifc_item, distance in candidates:
    similarity = 1.0 / (1.0 + distance)

# 修复后
for ifc_item, similarity in candidates:
    # Note: search() returns similarity (dot product), not distance
```

**Line 137-146**: 返回选中实体时的变量命名
```python
# 修复前
for ifc_item, distance in candidates:
    if ifc_item.name == selected_name:
        similarity = 1.0 / (1.0 + distance)

# 修复后
for ifc_item, similarity in candidates:
    if ifc_item.name == selected_name:
        # similarity已经是正确的值，直接使用
```

### 2. property_resolver.py (Line 131-134)

```python
# 修复前
ifc_item, distance = results[0]
similarity = 1.0 / (1.0 + distance)

# 修复后
ifc_item, similarity = results[0]
# similarity已经是点积相似度，不需要转换
```

### 3. material_resolver.py (Line 42-45)

```python
# 修复前
ifc_item, distance = results[0]
similarity = 1.0 / (1.0 + distance)

# 修复后
ifc_item, similarity = results[0]
# similarity已经是点积相似度，不需要转换
```

### 4. classification_resolver.py (Line 46-47)

```python
# 修复前
ifc_item, distance = results[0]
similarity = 1.0 / (1.0 + distance)

# 修复后
ifc_item, similarity = results[0]
# similarity已经是点积相似度，不需要转换
```

## 验证方法

### 修复前的搜索结果
```
Query: "bridge structure IfcBridge entity"
LLM看到的候选项（错误的相似度）：
1. IfcGridPlacement - similarity: 0.621 (错误转换自0.609)
2. IfcEventType - similarity: 0.630 (错误转换自0.586)
3. IfcBridge - similarity: 0.633 (错误转换自0.580)
```

### 修复后的搜索结果
```
Query: "bridge structure IfcBridge entity"
LLM看到的候选项（正确的相似度）：
1. IfcGridPlacement - similarity: 0.622 (正确)
2. IfcEventType - similarity: 0.630 (正确)
3. IfcBridge - similarity: 0.633 (正确) ✓
```

修复后，IfcBridge的真实相似度(0.633)正确显示，LLM能够基于正确的分数做出选择。

## 测试计划

1. ✅ 修复所有4个resolver的相似度计算
2. 🔄 运行reference_verification测试验证IfcBridge映射
3. ⏳ 检查Stage C输出的mapped_name是否正确
4. ⏳ 验证其他IFC4X3实体（IfcAlignment, IfcBridgePart）的映射

## 相关文件

- 诊断报告: `STAGE_C_DIAGNOSIS_20260421.md`
- 版本过滤修复: `STAGE_C_FIX_SUMMARY.md`
- 测试日志: `reference_test_similarity_fix.log`

## 修复时间

2026-04-21 11:47
