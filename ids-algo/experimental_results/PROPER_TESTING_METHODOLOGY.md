# 大规模鲁棒性测试方案

## 方案A：真实需求文档测试（推荐）

### 测试目标
验证系统处理大量真实工程需求的能力

### 测试数据来源
1. **建筑规范文档**
   - 提取30-50条具体的合规性要求
   - 例如：消防规范、结构规范、无障碍设计规范

2. **BIM执行计划（BEP）**
   - 提取模型交付要求
   - 例如：LOD要求、命名规范、属性要求

3. **项目特定需求**
   - 业主方的特殊要求
   - 例如：材料限制、性能指标、分类要求

### 示例需求集（30条）

```python
requirements = [
    # 结构要求 (10条)
    "All load-bearing walls must be made of concrete with compressive strength >= 30 MPa",
    "All structural columns must have a minimum cross-sectional area of 0.25 m²",
    "All beams with span > 6m must be made of steel or reinforced concrete",
    "All foundation elements must have property Pset_ConcreteElementGeneral.StrengthClass",
    "All structural slabs must have thickness >= 150mm",
    "All shear walls must be classified as load-bearing elements",
    "All structural frames must have seismic design category specified",
    "All post-tensioned elements must have property Pset_ConcreteElementGeneral.PostTensioned = true",
    "All structural connections must be classified by connection type",
    "All structural members must have material grade specified",
    
    # 消防要求 (5条)
    "All fire doors must have fire rating >= 60 minutes",
    "All fire-rated walls must have property Pset_WallCommon.FireRating",
    "All escape routes must have minimum width of 1.2m",
    "All fire compartments must be clearly identified",
    "All fire protection systems must be classified according to fire safety code",
    
    # MEP要求 (5条)
    "All HVAC ducts must have property Pset_DuctSegmentTypeCommon.NominalDiameter",
    "All electrical cables must be classified by voltage rating",
    "All plumbing pipes must have material specification",
    "All lighting fixtures must have property Pset_LightFixtureTypeCommon.LightEmitterType",
    "All mechanical equipment must have manufacturer and model number",
    
    # 无障碍要求 (5条)
    "All ramps must have slope <= 1:12",
    "All accessible doors must have clear width >= 850mm",
    "All accessible toilets must have grab bars installed",
    "All elevators must be wheelchair accessible",
    "All accessible parking spaces must be clearly marked",
    
    # 能效要求 (5条)
    "All external walls must have thermal transmittance U-value <= 0.3 W/m²K",
    "All windows must have property Pset_WindowCommon.ThermalTransmittance",
    "All roofs must have insulation with R-value >= 5.0 m²K/W",
    "All HVAC systems must have energy efficiency rating specified",
    "All lighting systems must use LED technology with efficacy >= 100 lm/W"
]
```

### 测试指标

1. **成功率**: 生成有效IDS的比例
2. **响应时间**: 处理30条需求的总耗时
3. **内存占用**: 峰值内存使用
4. **映射准确率**: Stage C映射的正确性（人工抽查）
5. **IDS质量**: 生成的IDS是否符合XSD schema

### 优势
- ✓ 输入是真实的自然语言，没有信息丢失
- ✓ 测试系统的实际使用场景
- ✓ 可以评估系统对不同领域的适应性

---

## 方案B：IDS作为参考答案（对比测试）

### 测试目标
使用IDS作为"标准答案"，评估系统生成的准确性

### 测试流程

```
1. 准备阶段
   - 收集真实的IDS文件（如你的45个specifications）
   - 人工编写对应的自然语言需求（不是自动转换！）

2. 测试阶段
   - 输入：人工编写的自然语言需求
   - 输出：系统生成的IDS

3. 对比阶段
   - 对比生成的IDS与原始IDS
   - 计算匹配率、覆盖率
   - 分析差异原因
```

### 关键：人工编写需求

**错误做法**（你之前的方法）:
```python
# 自动转换，丢失信息
ids_text = convert_ids_to_requirements(ids_file)
```

**正确做法**:
```python
# 人工编写，保留完整语义
requirements = {
    "spec_1": "All IfcBeam elements with predefined type GIRDER must be made of steel",
    "spec_2": "All IfcColumn elements in the substructure must have height >= 3.0m",
    "spec_3": "All IfcSlab elements with predefined type FLOOR must have LoadBearing property set to true",
    # ... 人工编写45条
}
```

### 示例对比

**原始IDS Specification**:
```xml
<specification name="Structural Beams">
  <applicability>
    <entity>
      <name><simpleValue>IfcBeam</simpleValue></name>
      <predefinedType><simpleValue>BEAM</simpleValue></predefinedType>
    </entity>
  </applicability>
  <requirements>
    <material>
      <value><simpleValue>Steel</simpleValue></value>
    </material>
    <property propertySet="Pset_BeamCommon" name="LoadBearing">
      <value><simpleValue>true</simpleValue></value>
    </property>
  </requirements>
</specification>
```

**人工编写的需求**:
```
"All structural beams (IfcBeam with predefined type BEAM) must be made of Steel 
and must have property Pset_BeamCommon.LoadBearing set to true"
```

**系统生成的IDS**:
```json
{
  "name": "Structural Beams Requirements",
  "applicability": {
    "entity": {"name": "IfcBeam", "predefinedType": "BEAM"}
  },
  "requirements": {
    "material": {"value": "Steel"},
    "property": {
      "propertySet": "Pset_BeamCommon",
      "name": "LoadBearing",
      "value": "true"
    }
  }
}
```

**对比结果**:
- ✓ Entity匹配: IfcBeam + BEAM
- ✓ Material匹配: Steel
- ✓ Property匹配: Pset_BeamCommon.LoadBearing = true
- **匹配率: 100%**

### 优势
- ✓ 有明确的"标准答案"可以对比
- ✓ 可以量化评估准确性
- ✓ 可以识别系统的系统性偏差

### 劣势
- ✗ 需要人工编写45条需求（工作量大）
- ✗ 人工编写可能引入主观性

---

## 方案C：混合测试（最全面）

### 测试设计

```python
test_suite = {
    "small_scale": {
        "count": 13,
        "source": "手工设计的简单需求",
        "purpose": "基本功能验证",
        "已完成": True
    },
    
    "medium_scale": {
        "count": 30,
        "source": "真实工程需求文档",
        "purpose": "实际场景测试",
        "待执行": True
    },
    
    "large_scale": {
        "count": 50+,
        "source": "多个项目的需求汇总",
        "purpose": "压力测试和性能评估",
        "待执行": True
    },
    
    "reference_comparison": {
        "count": 10-15,
        "source": "人工编写需求 + 原始IDS对比",
        "purpose": "准确性评估",
        "待执行": True
    }
}
```

---

## 推荐方案：方案A + 部分方案B

### 第一步：真实需求测试（30条）

使用我刚才提供的30条真实需求，测试：
- 系统能否处理多领域需求（结构、消防、MEP、无障碍、能效）
- 响应时间和内存占用
- 生成的IDS质量

### 第二步：参考对比测试（5-10条）

从你的45个specifications中选择5-10个**最典型的**：
- 人工编写对应的自然语言需求
- 运行系统生成IDS
- 与原始IDS对比，计算准确率

### 第三步：论文呈现

**5.3 性能测试**
- 小规模测试（13条）：功能验证 ✓
- 中规模测试（30条）：实际场景 ← 新增
- 大规模测试（50条）：压力测试 ← 新增

**5.4 准确性评估**
- 参考对比测试（5-10条）：与标准IDS对比 ← 新增
- 匹配率、覆盖率、差异分析

**5.5 系统局限性**
- 往返转换失败案例 ← 你刚才的实验
- 领域知识局限性
- 改进方向

---

## 总结

**你的问题**：
> 难道不能用大量的自然语言作为输入吗？

**答案**：
✓ **可以！** 但必须是**真实的自然语言需求**，而不是从IDS自动转换的

**你的问题**：
> 我只是想用大型的IDS文件来和我的系统从自然语言到IDS互相验证

**答案**：
✓ **可以！** 但需要**人工编写**对应的自然语言需求，而不是自动转换

**关键区别**：
```
❌ IDS → 自动转换 → 自然语言 → 系统 → IDS'  (信息丢失)
✓ IDS → 人工理解 → 自然语言 → 系统 → IDS'  (信息保留)
```

你想要的是第二种方法，这是完全合理的！
