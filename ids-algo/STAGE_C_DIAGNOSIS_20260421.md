# Stage C 映射错误诊断报告
**日期**: 2026-04-21  
**问题**: IfcBridge、IfcBridgePart、IfcAlignment等IFC4X3实体无法被正确映射

---

## 问题现象

运行reference verification测试时，15个bridge相关需求的映射准确率为0%：
- IfcBridge → 错误映射为 IfcCivilElement
- IfcBridgePart → 错误映射为 IfcBuildingElementPart
- IfcAlignment → 错误映射为 IfcGridAxis

Stage E的LLM检测到了这些映射错误并拒绝生成IDS规范。

---

## 根本原因分析

### 原因1: 向量搜索默认IFC版本过滤器错误

**文件**: `c_knowledge_base_mapping/vector_database/core/base.py`  
**位置**: Line 208

**问题代码**:
```python
def search(
    self,
    query: str,
    top_k: Optional[int] = None,
    ifc_versions: Optional[List[str]] = ["IFC4"],  # ❌ 硬编码IFC4
    item_types: Optional[List[str]] = None,
) -> List[Tuple[IFCItem, float]]:
```

**影响**:
- 向量搜索默认只返回IFC4版本的实体
- IfcBridge (IFC4X3)、IfcBridgePart (IFC4X3)、IfcAlignment (IFC4X3) 被过滤掉
- 搜索"IfcBridge"返回的top 5全是IFC4实体，完全不包含IfcBridge

**修复**:
```python
ifc_versions: Optional[List[str]] = None,  # ✓ 默认搜索所有版本
```

---

### 原因2: Entity Resolver硬编码IFC4默认值

**文件**: `c_knowledge_base_mapping/resolvers/entity_resolver.py`  
**位置**: Line 39, 48

**问题代码**:
```python
ifc_version = context.get("ifc_version", "IFC4") if context else "IFC4"  # ❌ 默认IFC4
...
results = db.search(query_text, top_k=5, ifc_versions=[ifc_version])  # ❌ 强制过滤
```

**影响**:
- 即使修复了base.py，resolver仍然传递IFC4过滤器
- Pipeline没有设置ifc_version，所以总是使用"IFC4"默认值

**修复**:
```python
ifc_version = context.get("ifc_version") if context else None  # ✓ 默认None
...
ifc_versions_filter = [ifc_version] if ifc_version else None  # ✓ 只在明确指定时过滤
results = db.search(query_text, top_k=5, ifc_versions=ifc_versions_filter)
```

---

## 测试验证

### 修复前
```
搜索 "IfcBridge" (默认IFC4过滤):
1. IfcLightSourceAmbient (IFC2X3): 0.538
2. IfcLightSource (IFC2X3): 0.536
3. IfcLightSourceDirectional (IFC2X3): 0.534
4. IfcColourRgb (IFC4): 0.522
5. IfcLightSourcePositional (IFC2X3): 0.516

❌ IfcBridge不在结果中
```

### 修复后
```
搜索 "IfcBridge" (无版本过滤):
1. IfcGridPlacement (IFC4X3): 0.609
2. IfcEventType (IFC4X3): 0.586
3. IfcBridge (IFC4X3): 0.580  ✓
4. IfcFaceBound (IFC4X3): 0.568
5. IfcBridgePart (IFC4X3): 0.567  ✓

✓ IfcBridge正确出现在top 5中
```

---

## 已修复的文件

1. **c_knowledge_base_mapping/vector_database/core/base.py**
   - Line 208: `ifc_versions` 默认值从 `["IFC4"]` 改为 `None`

2. **c_knowledge_base_mapping/resolvers/entity_resolver.py**
   - Line 39: `ifc_version` 默认值从 `"IFC4"` 改为 `None`
   - Line 48: 添加条件判断，只在明确指定版本时才过滤

---

## 遗留问题

### 问题3: Pipeline保存Stage C结果的代码不正确

**文件**: `pipeline.py`  
**位置**: Lines 85-108

**问题**:
```python
# 当前代码检查 facet.entity.value (不存在的字段)
if hasattr(facet, 'entity') and facet.entity:
    mapping["entity"] = {
        "mapped_value": getattr(facet.entity, 'value', ''),  # ❌ 错误字段
        ...
    }
```

**正确的MappedFacet结构** (参考 `temp/c1.json`):
```python
{
    "facet_type": "entity",
    "original_text": "All walls",
    "mapped_name": "IfcWall",           # ✓ 映射后的名称
    "confidence": 0.669,                # ✓ 置信度
    "ifc_item": {                       # ✓ 完整的IFC项目信息
        "name": "IfcWall",
        "definition": "...",
        "ifc_version": "IFC4",
        "item_type": "entity"
    },
    "property_set": null,
    "entity_name": null,
    "constraints": [],
    "additional_data": null
}
```

**需要修复**:
- 直接提取 `facet.mapped_name`、`facet.confidence`、`facet.ifc_item`
- 删除错误的 `facet.entity.value` 检查

**建议**: 
1. 备份当前 `pipeline.py` 为 `pipeline_backup_20260421.py`
2. 参考 `pipeline_test.py` 中的正确实现 (lines 76-110)
3. 或者直接使用 `pipeline_test.py` 替换 `pipeline.py`

---

## 相关文件位置

### 测试文件
- `test_reference_verification_simple.py` - 简化的reference验证测试
- `direct_vector_test.py` - 直接测试向量搜索
- `debug_vector_search.py` - 调试向量搜索结果

### 日志文件
- `reference_verification.log` - Reference验证测试日志
- `rebuild_vectors.log` - 向量重建日志
- `experimental_results/reference_verification/full_test_log_20260421_003431.txt` - 完整测试日志

### Stage C输出示例
- `temp/c1.json` - 正确的Stage C输出格式示例
- `temp/c2.json` - 另一个输出示例
- `experimental_results/reference_verification/stage_c_mappings_*.json` - 实际测试输出

---

## 下一步行动

1. ✅ **已完成**: 修复向量搜索IFC版本过滤问题
2. ✅ **已完成**: 修复Entity Resolver默认版本问题
3. ⏳ **待完成**: 修复pipeline.py保存Stage C结果的代码
4. ⏳ **待完成**: 重新运行reference verification测试验证完整修复

---

## 技术细节

### 向量搜索工作原理
1. 使用 BAAI/bge-m3 模型生成1024维向量
2. 向量已归一化 (norm=1.0)
3. 使用FAISS IndexFlatIP (内积) 计算相似度
4. 相似度 = dot_product(query_vector, item_vector)
5. 结果按相似度降序排序

### Entity Database信息
- 总实体数: 2291
- 模型: BAAI/bge-m3 (1024维)
- IFC版本: IFC2X3, IFC4, IFC4X3
- IfcBridge位置: index 1484
- IfcBridgePart位置: index 1485

### 向量缓存
- 位置: `cache/vectors/`
- 已清理旧缓存 (使用错误模型生成的向量)
- 新缓存使用正确的bge-m3模型

---

## 总结

Stage C映射错误的根本原因是**IFC版本过滤器默认值设置错误**，导致IFC4X3版本的bridge相关实体被排除在搜索结果之外。修复后，向量搜索能够正确返回IfcBridge等实体。

但pipeline保存Stage C结果的代码仍需修复，才能让完整的映射信息传递到Stage E。
