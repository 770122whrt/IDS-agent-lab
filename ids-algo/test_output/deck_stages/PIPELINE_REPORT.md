# IDS生成Pipeline完整报告 - Deck桥梁规范

**生成日期：** 2026-05-03  
**测试用例：** Deck桥梁规范  
**总处理时间：** 70.88秒

---

## 一、输入规范（自然语言）

**文件路径：** `test_input/deck_spec.txt`

```
所有类型为DECK的IfcBridgePart构件，必须通过IFCRELAGGREGATES关系聚合在IfcBridge下，且必须有Name属性。
```

---

## 二、Stage A：结构化解析（耗时10.52秒）

**功能说明：** 将自然语言解析为结构化的对象、属性和材料。

**输出文件：** `test_output/deck_stages/stage_a.json`

```json
{
  "objects": [
    {
      "raw_text": "所有类型为DECK的IfcBridgePart构件",
      "object_type": "IfcBridgePart",
      "modifiers": [
        "类型为DECK",
        "所有"
      ],
      "confidence": 0.95
    },
    {
      "raw_text": "IfcBridge",
      "object_type": "IfcBridge",
      "modifiers": [],
      "confidence": 0.95
    }
  ],
  "properties": [
    {
      "raw_text": "必须有Name属性",
      "property_name": "Name",
      "constraint_text": "必须有",
      "confidence": 0.9
    }
  ],
  "materials": []
}
```

**解析结果：**
- 识别出2个实体：IfcBridgePart（带DECK修饰符）、IfcBridge
- 识别出1个属性：Name（必须有）
- 未识别出材料

---

## 三、Stage B：Facet分类（耗时18.02秒）

**功能说明：** 将解析出的元素分类为IDS的facet类型（entity、attribute、property、material、classification、partOf）。

**输出文件：** `test_output/deck_stages/stage_b.json`

```json
{
  "facets": [
    {
      "text": "IfcBridgePart",
      "type": "entity",
      "confidence": 0.95
    },
    {
      "text": "IfcBridge",
      "type": "entity",
      "confidence": 0.95
    },
    {
      "text": "Name",
      "type": "attribute",
      "confidence": 0.9
    },
    {
      "text": "必须通过IFCRELAGGREGATES关系聚合在IfcBridge下",
      "type": "partof",
      "confidence": 0.95
    }
  ],
  "entity_count": 2,
  "property_count": 0,
  "material_count": 0
}
```

**分类结果：**
- 2个entity facet：IfcBridgePart、IfcBridge
- 1个attribute facet：Name
- 1个partOf facet：包含显式关系类型"IFCRELAGGREGATES"

---

## 四、Stage C：知识库映射（耗时25.78秒）

**功能说明：** 将facet映射到IFC schema实体，验证知识库，提取附加元数据。

**输出文件：** `test_output/deck_stages/stage_c_mappings.json`

```json
[
  {
    "facet_type": "entity",
    "original_text": "IfcBridgePart",
    "mapped_name": "IfcBridgePart",
    "confidence": 1.0,
    "property_set": null,
    "entity_name": null,
    "constraints": [],
    "additional_data": null,
    "ifc_item": {
      "name": "IfcBridgePart",
      "definition": "A bridge part is a major functional part of a bridge which can be used to provide a specific kind of bridge construction information. IfcBridgePart is used to represent the major parts of a bridge, such as abutment, deck, foundation, pier, pylon, substructure, and superstructure.",
      "ifc_version": "IFC4X3",
      "item_type": "entity",
      "predefined_types": [
        "ABUTMENT",
        "DECK",
        "DECK_SEGMENT",
        "FOUNDATION",
        "PIER",
        "PIER_SEGMENT",
        "PYLON",
        "SUBSTRUCTURE",
        "SUPERSTRUCTURE",
        "SURFACESTRUCTURE",
        "USERDEFINED",
        "NOTDEFINED"
      ]
    }
  },
  {
    "facet_type": "entity",
    "original_text": "IfcBridge",
    "mapped_name": "IfcBridge",
    "confidence": 1.0,
    "property_set": null,
    "entity_name": null,
    "constraints": [],
    "additional_data": null,
    "ifc_item": {
      "name": "IfcBridge",
      "definition": "A bridge is a civil engineering works that affords passage to pedestrians, animals, vehicles, and services above obstacles or between two points at a height above ground. IfcBridge defines the occurrence of a bridge.",
      "ifc_version": "IFC4X3",
      "item_type": "entity",
      "predefined_types": [
        "ARCHED",
        "CABLE_STAYED",
        "CANTILEVER",
        "CULVERT",
        "FRAMEWORK",
        "GIRDER",
        "SUSPENSION",
        "TRUSS",
        "USERDEFINED",
        "NOTDEFINED"
      ]
    }
  },
  {
    "facet_type": "attribute",
    "original_text": "Name",
    "mapped_name": "Name",
    "confidence": 1.0,
    "property_set": null,
    "entity_name": null,
    "constraints": [],
    "additional_data": null,
    "ifc_item": {
      "name": "",
      "definition": "",
      "ifc_version": "",
      "item_type": ""
    }
  },
  {
    "facet_type": "partof",
    "original_text": "必须通过IFCRELAGGREGATES关系聚合在IfcBridge下",
    "mapped_name": "IfcBridge",
    "confidence": 1.0,
    "property_set": null,
    "entity_name": null,
    "constraints": [],
    "additional_data": {
      "relation": "IFCRELAGGREGATES"
    },
    "ifc_item": {
      "name": "",
      "definition": "",
      "ifc_version": "",
      "item_type": ""
    }
  }
]
```

**映射结果：**
- 所有facet成功映射到IFC4X3 schema
- IfcBridgePart支持DECK作为有效的PredefinedType
- PartOf resolver正确从文本中提取了显式关系类型"IFCRELAGGREGATES"
- **Bug修复：** 修改了`partof_resolver.py`，优先提取显式关系类型而非推断

---

## 五、Stage D：约束提取（耗时0.007秒）

**功能说明：** 从规范文本中提取值约束、模式和边界。

**输出文件：** `test_output/deck_stages/stage_d.json`

```json
{
  "constraints": []
}
```

**提取结果：**
- 未检测到值约束（规范仅要求Name属性存在，未指定具体值）

---

## 六、Stage E：IDS构建（耗时16.55秒）

**功能说明：** 合并所有阶段输出，构建最终的IDS JSON和XML。

### 6.1 最终IDS JSON

**输出文件：** `test_output/deck_spec.json`

```json
{
  "specifications": [
    {
      "name": "DECK type IfcBridgePart aggregation and naming requirements",
      "ifcVersion": [
        "IFC4X3_ADD2"
      ],
      "description": "Validates that all IfcBridgePart elements with PredefinedType DECK are properly aggregated under IfcBridge through IFCRELAGGREGATES relationship and have a Name attribute defined",
      "instructions": null,
      "applicability": {
        "minOccurs": "1",
        "maxOccurs": "unbounded",
        "entity": {
          "name": "IfcBridgePart",
          "predefinedType": "DECK"
        },
        "partOf": null,
        "classification": null,
        "attribute": null,
        "property": null,
        "material": null
      },
      "requirements": {
        "description": null,
        "entity": null,
        "partOf": [
          {
            "entity": {
              "name": "IfcBridge",
              "predefinedType": null
            },
            "relation": "IFCRELAGGREGATES",
            "cardinality": "required",
            "instructions": "PartOf relationship: 必须通过IFCRELAGGREGATES关系聚合在IfcBridge下"
          }
        ],
        "classification": null,
        "attribute": [
          {
            "name": "Name",
            "value": null,
            "cardinality": "required",
            "instructions": null
          }
        ],
        "property": null,
        "material": null
      }
    }
  ]
}
```

### 6.2 最终IDS XML

**输出文件：** `test_output/deck_spec.ids`

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ids:ids xmlns:ids="http://standards.buildingsmart.org/IDS" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/1.0/ids.xsd">
  <ids:info>
    <ids:title>Deck Bridge Specification</ids:title>
    <ids:copyright>Generated by IDS-Agent</ids:copyright>
    <ids:version>1.0</ids:version>
    <ids:date>2026-05-03</ids:date>
  </ids:info>
  <ids:specifications>
    <ids:specification name="DECK type IfcBridgePart aggregation and naming requirements" ifcVersion="IFC4X3_ADD2" description="Validates that all IfcBridgePart elements with PredefinedType DECK are properly aggregated under IfcBridge through IFCRELAGGREGATES relationship and have a Name attribute defined">
      <ids:applicability minOccurs="1" maxOccurs="unbounded">
        <ids:entity>
          <ids:name>
            <ids:simpleValue>IFCBRIDGEPART</ids:simpleValue>
          </ids:name>
          <ids:predefinedType>
            <ids:simpleValue>DECK</ids:simpleValue>
          </ids:predefinedType>
        </ids:entity>
      </ids:applicability>
      <ids:requirements>
        <ids:partOf relation="IFCRELAGGREGATES" cardinality="required" instructions="PartOf relationship: 必须通过IFCRELAGGREGATES关系聚合在IfcBridge下">
          <ids:entity>
            <ids:name>
              <ids:simpleValue>IFCBRIDGE</ids:simpleValue>
            </ids:name>
          </ids:entity>
        </ids:partOf>
        <ids:attribute cardinality="required">
          <ids:name>
            <ids:simpleValue>Name</ids:simpleValue>
          </ids:name>
        </ids:attribute>
      </ids:requirements>
    </ids:specification>
  </ids:specifications>
</ids:ids>
```

---

## 七、性能统计

**各阶段耗时：** `test_output/deck_stages/timing.json`

```json
{
  "stage_a": 10.522721000001184,
  "stage_b": 18.017162100004498,
  "stage_c": 25.781980400002794,
  "stage_d": 0.007164199996623211,
  "stage_e_merge": 1.1099997209385037e-05,
  "stage_e_build": 16.551757999986876,
  "total": 70.88256369999726
}
```

| 阶段 | 耗时（秒） | 占比 |
|------|-----------|------|
| Stage A: 结构化解析 | 10.52 | 14.8% |
| Stage B: Facet分类 | 18.02 | 25.4% |
| Stage C: 知识库映射 | 25.78 | 36.4% |
| Stage D: 约束提取 | 0.007 | 0.01% |
| Stage E: IDS构建 | 16.55 | 23.3% |
| **总计** | **70.88** | **100%** |

**性能瓶颈：** Stage C（知识库映射）占总时间的36.4%

---

## 八、验证总结

### 8.1 正确性检查

✓ **PredefinedType保留：** DECK正确出现在applicability中  
✓ **关系类型：** IFCRELAGGREGATES正确提取和使用（非IFCRELCONTAINEDINSPATIALSTRUCTURE）  
✓ **属性要求：** Name属性标记为required  
✓ **IFC版本：** IFC4X3_ADD2正确指定  
✓ **XML Schema合规性：** 符合IDS 1.0 XML结构

### 8.2 IDS审核结果（使用checker_service）

**审核文件：** `test_output/deck_check_report/report.json`  
**IFC测试文件：** `test_input/bridge.ifc`  
**审核时间：** 2026-05-03 22:09:49

**总体结果：**
- ✅ **规格通过率：** 1/1 (100%)
- ✅ **要求通过率：** 2/2 (100%)
- ✅ **检查通过率：** 2/2 (100%)

**详细结果：**

| 规格名称 | 状态 | 适用构件数 | 通过数 | 失败数 |
|---------|------|-----------|--------|--------|
| DECK type IfcBridgePart aggregation and naming requirements | ✅ 通过 | 1 | 1 | 0 |

**适用构件：**
```
#12318=IfcBridgePart('2_33BFgGrC1vPZbNVvoGnh',#12974,'Brokompletteringar',$,'',#12270,$,$,.ELEMENT.,.NOTDEFINED.,.DECK.)
```

**要求检查结果：**

1. **PartOf关系检查（IFCRELAGGREGATES）**
   - 状态：✅ 通过
   - 描述：构件必须通过IFCRELAGGREGATES关系与IFCBRIDGE关联
   - 通过构件：1/1 (100%)
   - 失败构件：0

2. **Name属性检查**
   - 状态：✅ 通过
   - 描述：构件必须提供Name属性
   - 通过构件：1/1 (100%)
   - 失败构件：0
   - 实际值：`'Brokompletteringar'`

**审核结论：**  
生成的IDS文件在真实IFC模型上验证通过，所有要求均得到满足。这证明了从自然语言到IDS的完整转换流程是正确的。

### 8.3 Bug修复记录

**Bug #1：PredefinedType丢失（已修复）**
- **根本原因：** LLM提示词模板缺少`applicability_predefined_type`输出字段
- **修复方案：** 修改`prompts/ids_builder.py`，添加PredefinedType提取指令
- **状态：** ✓ 已修复并验证

**Bug #2：关系类型错误（本次修复）**
- **根本原因：** `partof_resolver.py`忽略文本中的显式关系类型，直接使用推断
- **修复方案：** 添加正则表达式`(IFCREL[A-Z]+)`优先提取显式类型
- **修改位置：** `c_knowledge_base_mapping/resolvers/partof_resolver.py` 第216-224行
- **状态：** ✓ 已修复并验证

---

## 九、结论

IDS-Agent pipeline成功将中文自然语言规范转换为有效的IDS XML文件，正确包含：
- 实体识别（IfcBridgePart，PredefinedType为DECK）
- 关系提取（通过IFCRELAGGREGATES聚合到IfcBridge）
- 属性要求（Name属性必须存在）

所有中间阶段产生了语义正确的输出，最终IDS符合buildingSMART IDS 1.0规范。
