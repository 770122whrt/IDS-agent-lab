# 第四章 IDS生成流水线与知识库构建

## 4.1 五阶段处理流程概述

合规审查是建筑行业的基本要求[8]，本系统的主要功能是将自然语言表达的规范描述转化为标准化的IDS规则文件。基于第三章确定的系统架构，本研究设计了一套结构化的五阶段处理流水线，如图4.1所示。该流水线将自然语言理解与规则生成任务分解为五个顺序执行的子阶段，各阶段通过中间态JSON结构实现数据传递，每个阶段的输出即为下一阶段的输入。

---

> **【图表需求 - 待创建】**
>
> **图4.1 IDS生成五阶段流水线流程图**
> - **位置**：此处（4.1节，"如图4.1所示"后）
> - **类型**：横向流程图/流水线图
> - **内容要点**：五个阶段的顺序流转（结构化解析 → Facet分类 → 知识库映射 → 约束提取 → IDS构建），标注各阶段输入输出

---

流水线采用分阶段设计而非端到端生成。端到端方式要求大语言模型在单次调用中同时完成语义理解、术语映射与规则构建，任务复杂度超出模型的可靠处理范围，容易产生"幻觉"——即生成与输入不符的IFC实体名称或虚构的属性约束[41]。分阶段设计通过知识库检索与规则验证机制约束了每一步的生成空间[24]。另一方面，中间态JSON结构使每个阶段的输出均可独立检查，当最终生成的IDS规则存在错误时，开发者可以定位到具体是哪个阶段引入了问题，而非面对端到端模型的黑箱输出。

五个阶段的输入输出关系如表4.1所示。以"所有承重墙的厚度必须不小于200mm"为例，各阶段的处理结果如下：

表4.1以"所有承重墙的厚度必须不小于200mm"为贯穿示例，展示了各阶段的数据流转过程。

**表4.1 五阶段输入输出对照表**

| 阶段 | 输入 | 输出 | 任务 | 技术 |
|------|------|------|----------|----------|
| 阶段一：结构化解析 | 原始自然语言文本 | `{building_objects: [{raw_text:"承重墙", object_type:"墙", modifiers:["承重"]}], property_descriptions: [{property_name:"厚度", constraint_text:"不小于200mm"}], ...}` | 提取四类结构化元素 | Claude-3.5-Sonnet, Few-shot |
| 阶段二：Facet分类 | 阶段一的结构化元素 | `{entity_candidates: [{source_text:"承重墙", facet_type:"EntityFacet"}], property_candidates: [{source_text:"厚度", facet_type:"PropertyFacet"}], ...}` | 映射至七种Facet类型 | Claude-3.5-Sonnet |
| 阶段三：知识库映射 | 阶段二的Facet候选 | `{..., ifc_mapping: {entity:"IfcWall", property_set:"Pset_WallCommon", property:"Thickness"}}` | 自然语言→IFC标准化命名 | BGE-M3 + FAISS |
| 阶段四：约束提取 | Facet元素的原始文本 | `{constraint_detail: {type:"Measure", minValue:200, unit:"mm", dataType:"IfcLengthMeasure"}}` | 提取数值/枚举/格式/长度约束 | 正则表达式 |
| 阶段五：IDS构建 | 前四阶段的整合结果 | 符合IDS XSD规范的XML规则文件 | 规则分组 + JSON→XML转换 | LLM分组 + lxml |

五阶段流水线的技术实现依赖于第三章选定的技术栈：阶段一、二与阶段五通过OpenRouter平台调用Claude-3.5-Sonnet模型执行语义理解与规则生成任务；阶段三通过BGE-M3嵌入模型与FAISS索引实现术语映射；阶段四通过正则表达式引擎提取约束条件。下文将依次介绍各阶段的处理逻辑，并在4.2节首先阐述作为阶段三支撑的向量知识库构建方法。

## 4.2 向量知识库构建

向量知识库是知识库映射阶段（阶段三）的支撑环节，其构建质量直接影响自然语言到IFC标准命名的映射准确性。本节阐述知识库的数据来源、嵌入方法、索引构建与缓存设计。

### 4.2.1 数据来源与术语库结构

向量知识库的数据来源为IFC官方文档（IFC4与IFC4.3版本），系统构建了七类结构化的JSON术语库文件：

**实体类型术语库（entity_db.json）**：收录IFC标准定义的各类实体类型，包括建筑构件（如IfcWall、IfcBeam、IfcColumn）、空间结构（如IfcBuilding、IfcSite）等，共800余个条目。每个条目包含英文名称与定义描述，为EntityFacet约束的映射提供候选实体。

**属性集术语库（propertySet_db.json）**：收录IFC标准定义的约200个标准属性集（Property Set），如Pset_WallCommon（墙体通用属性集）、Pset_BeamCommon（梁通用属性集）等。每个属性集记录其所属实体类型与包含的属性列表，是连接实体与属性的中间层。

**属性术语库（property_db.json）**：属性集术语库的细化层级，收录IFC标准定义的约1,000个属性，如Thickness（厚度）、LoadBearing（是否承重）、FireRating（防火等级）等。每个属性附带数据类型与所属属性集信息，为PropertyFacet约束的映射提供候选属性。

**材料术语库（material_db.json）**：收录IFC标准定义的材料类型术语，如Concrete（混凝土）、Steel（钢材）等，用于MaterialFacet约束的材料名称映射。

**分类术语库（classification_db.json）**：存储IFC标准支持的分类系统术语，如UniClass、OmniClass等分类体系中的编码与名称，用于ClassificationFacet约束的分类编码映射。

**组合关系术语库（partof_db.json）**：定义IFC实体之间的组合关系，如IfcWall与IfcBuilding之间的包含关系，用于PartOfFacet约束的映射。

**特征术语库（attribute_db.json）**：收录IFC实体的直接属性（如Name、Description），区别于通过属性集间接关联的属性，用于AttributeFacet约束的映射。

上述七类术语库覆盖了IDS规范生成所需的所有术语类型。系统在初始化时加载这些文件，为每个术语条目生成向量表示，构建统一的向量索引。

### 4.2.2 嵌入模型与向量编码

本研究采用BAAI/bge-m3作为嵌入模型，通过sentence-transformers框架在本地加载推理。选择该模型基于以下实际需求：知识库中的IFC术语定义为英文技术文本，而用户输入通常为中文，BGE-M3的多语言嵌入能力能够处理这种跨语言语义匹配；模型输出1024维向量，在语义表达能力与计算存储开销之间取得了平衡[46]。

向量编码时，每个术语条目的文本格式为"{名称}: {定义}"，即拼接术语名称与定义描述后整体编码。生成的向量经L2归一化处理，使得后续FAISS内积检索的结果与余弦相似度排序数学等价。向量在首次计算后以二进制格式持久化至本地磁盘缓存，后续检索直接读取缓存向量，避免重复调用嵌入模型的推理开销。

### 4.2.3 FAISS索引构建

向量索引采用FAISS库的IndexFlatIP（内积精确检索）类型构建[47]。选择精确检索而非近似检索的依据是当前知识库规模——约2,291个IFC实体条目，精确检索的单次计算延迟在毫秒级别，不存在性能瓶颈。对于归一化向量，IndexFlatIP的内积计算等价于余弦相似度，保证了语义匹配的准确性。

检索时，系统支持按IFC版本（IFC2x3、IFC4、IFC4.3）筛选候选范围，确保映射结果与目标模型的数据结构一致。相似度阈值设定为0.7，低于该阈值的候选结果将被过滤，系统默认使用IFC4版本。检索接口返回Top-5相似结果，供后续知识图谱验证阶段筛选。

### 4.2.4 缓存机制

系统设计了双层缓存以优化检索性能。内存缓存层采用LRU（最近最少使用）淘汰策略，最大容量为10,000条，缓存高频查询的向量与术语元数据。磁盘持久化层将向量索引与术语数据库存储至本地文件系统，知识库更新时仅需重建索引文件，无需重启服务。知识库按IFC版本分区存储，支持用户按版本筛选检索范围。

## 4.3 结构化解析模块（阶段一）

结构化解析是流水线的第一阶段，任务是将用户输入的自然语言规范描述转化为结构化的中间表示。该阶段调用大语言模型完成语义提取，是流水线中计算开销最大的环节。

### 4.3.1 解析任务定义

自然语言规范描述的特点是语义表达模糊、句式结构多变。例如"所有承重墙的厚度必须不小于200mm"中，"承重墙"同时包含实体类型（墙）与修饰条件（承重），"不小于200mm"是隐含的数值约束。传统关键词匹配方法难以处理这类语义嵌套，因此本阶段借助大语言模型的语义理解能力完成提取。

系统将解析结果组织为五类结构化元素：

**建筑构件（BuildingObject）**：描述规范适用的目标构件类型，如"墙"、"梁"、"柱"，附带修饰词（如"承重"）与置信度。

**属性描述（PropertyDescription）**：描述需要检验的属性及其约束文本，如属性名"厚度"、约束文本"不小于200mm"。

**材料要求（MaterialRequirement）**：描述材料相关约束，如"混凝土"、"C30及以上强度等级"。

**空间关系（SpatialRelationship）**：描述构件之间的空间关联，如"属于某建筑"、"位于某楼层"。

**未匹配片段（UnmatchedFragment）**：无法归类的文本片段，作为兜底保留。

### 4.3.2 LLM调用策略

本阶段通过OpenRouter平台调用Claude-3.5-Sonnet模型，温度参数设为0.1。LLM在规范语义理解中的应用已有初步探索[11]。温度参数的选择需要在输出稳定性与语义理解能力之间取得平衡：过低的温度（如0.0）会使模型倾向于复制训练数据中的固定模式，面对多样化规范表述时灵活性不足；过高的温度则会引入随机性，导致相同输入产生不一致的解析结果。0.1的设定保证了大多数情况下输出的确定性，同时保留了对复杂句式的理解弹性。

提示词设计采用Few-shot范式[39]，在提示中提供两组规范描述与对应解析结果的示例。示例的选择遵循两个原则：一是覆盖性，示例需包含数值约束（如"不小于200mm"）与枚举约束（如"混凝土或钢材"）两种典型模式，使模型理解不同约束类型的提取方式；二是边界性，示例中的实体描述包含修饰词（如"承重墙"），使模型学会区分实体类型与修饰条件。提示词以系统角色设定开头（"你是一名BIM规范解析专家"），随后嵌入示例对，最后放置待解析的用户输入。

输出格式约束是提示词设计的重要环节。提示词要求模型返回符合预定义JSON Schema的结构化结果，而非自由文本。这种约束将模型的生成空间限制在合法的字段组合内，降低了输出解析的失败率。系统通过后处理解析器校验返回结果的字段完整性，当LLM返回非JSON格式（如自然语言解释）时，触发降级处理——尝试从返回文本中正则提取JSON片段，若仍失败则返回空结果并记录错误。

### 4.3.3 输出结构

结构化解析的输出为内部数据结构StructuredParseResult对象，包含五类元素列表。每个元素附带原始文本（raw_text）与置信度评分（confidence），便于后续阶段追溯与筛选。以"所有承重墙的厚度必须不小于200mm"为例，解析结果如下：

```json
{
  "building_objects": [
    {"raw_text": "承重墙", "object_type": "墙", "modifiers": ["承重"], "confidence": 0.95}
  ],
  "property_descriptions": [
    {"raw_text": "厚度", "property_name": "厚度", "constraint_text": "不小于200mm", "confidence": 0.92}
  ],
  "material_requirements": [],
  "spatial_relationships": [],
  "unmatched_fragments": []
}
```

该结果表明LLM成功将"承重墙"拆解为实体类型"墙"与修饰词"承重"，将"厚度"识别为属性名并将其约束文本"不小于200mm"独立提取。空的material_requirements与spatial_relationships列表说明输入文本不涉及材料与空间关系约束，unmatched_fragments为空说明所有文本片段均被正确归类。

## 4.4 Facet分类模块（阶段二）

Facet分类是流水线的第二阶段，任务是将结构化解析提取的元素映射至IDS标准定义的七种Facet类型[37][49]。

### 4.4.1 IDS Facet类型

IDS标准通过七种Facet类型表达不同粒度的约束条件：

**实体方面（EntityFacet）**：约束目标构件的IFC实体类型，如"必须是IfcWall"。

**直接属性方面（AttributeFacet）**：约束IFC实体的直接属性值，如"Name属性不能为空"。

**属性集方面（PropertySetFacet）**：约束构件必须包含特定属性集，如"必须包含Pset_WallCommon"。

**属性值方面（PropertyFacet）**：约束通过属性集关联的属性值，如"Thickness必须≥200mm"。需要注意区分PropertyFacet与AttributeFacet：前者约束的是通过属性集（PropertySet）间接关联的属性，如Thickness通过Pset_WallCommon关联到IfcWall，映射时需经过"实体→属性集→属性"三层路径；后者约束的是IFC实体的直接属性，如IfcWall自带的Name、Description等，映射时仅需定位到实体层级即可。两者在本系统的知识库映射阶段（阶段三）遵循不同的检索与验证路径。

**分类方面（ClassificationFacet）**：约束构件的分类编码，如"UniClass编码为特定值"。

**材料方面（MaterialFacet）**：约束构件的材料类型，如"必须使用混凝土"。

**组合方面（PartOfFacet）**：约束构件的组合关系，如"必须属于某个IfcBuilding实体"。

### 4.4.2 分类策略

Facet分类采用单次LLM调用完成。系统将阶段一输出的四类元素列表（建筑构件、属性描述、材料要求、空间关系）序列化为JSON格式，作为上下文输入LLM。LLM根据每个元素的语义特征，将其归入对应的Facet候选列表。

分类结果为FacetClassification对象，包含六个候选列表（entity_candidates、property_candidates、attribute_candidates、material_candidates、classification_candidates、partof_candidates），每个候选元素附带来源文本、Facet类型、置信度与分类理由。本阶段LLM的温度参数设为0.05，低于结构化解析阶段，以保证分类结果的一致性。

### 4.4.3 输出结构

Facet分类的输出在解析结果基础上增加了Facet类型标注。每个候选元素携带facet_type字段，明确该元素对应的IDS约束类型。以"所有承重墙的厚度必须不小于200mm"为例，分类结果如表4.3所示。

**表4.3 Facet分类输出示例**

| 候选列表 | 来源文本 | Facet类型 | 置信度 | 分类理由 |
|----------|----------|-----------|--------|----------|
| entity_candidates | 承重墙 | EntityFacet | 0.95 | 指定构件类型 |
| property_candidates | 厚度 | PropertyFacet | 0.90 | 属性名+约束值 |
| material_candidates | — | — | — | 无材料相关描述 |
| attribute_candidates | — | — | — | 无直接属性约束 |

该结果表明"承重墙"被识别为实体约束，"厚度"被识别为属性约束，两者将分别进入后续的知识库映射与约束提取流程。完整的JSON数据结构见附录A.1。

## 4.5 知识库映射模块（阶段三）

知识库映射是流水线的第三阶段，任务是将自然语言描述中的实体名称与属性名称映射至IFC标准的标准化命名。该阶段不调用LLM，完全依赖4.2节构建的向量知识库完成语义匹配。

### 4.5.1 语义鸿沟问题

自然语言与IFC标准之间存在表述差异。用户可能使用"墙"、"墙体"、"墙面"等不同表述，而IFC标准的实体名称统一为IfcWall。属性名称的表达更为多样——"厚度"、"厚度尺寸"、"墙体厚度"均需映射至Pset_WallCommon.Thickness。错误的映射会导致生成的IDS规则无法匹配IFC模型中的实际实体，直接影响审查的准确性。

### 4.5.2 向量-图协同检索架构

为解决语义鸿沟问题，本研究设计了向量-图协同检索架构[33]（图指知识图谱），如图4.2所示。知识图谱以实体-关系-属性三元组组织领域知识，将IFC标准中实体类型、属性集与属性之间的关联关系结构化存储。该架构包含两条检索路径：

**向量检索路径**：将用户输入的自然语言名称通过BGE-M3模型编码为1024维向量，与4.2节构建的FAISS索引计算内积相似度，返回Top-5候选映射。相似度低于0.7阈值的候选被过滤。例如，输入"厚度"检索到Thickness属性（相似度0.88），输入"承重墙"检索到IfcWall（相似度0.87）。

**知识图谱验证路径**：向量检索返回候选后，通过IFC实体知识图谱验证实体与属性的关联是否合法。知识图谱记录了IFC实体类型、属性集与属性的三层关系——例如IfcWall关联Pset_WallCommon属性集，Pset_WallCommon包含Thickness属性。若候选属性不属于目标实体的合法属性集，则该映射被拒绝。

---

> **【图表需求 - 待创建】**
>
> **图4.2 向量检索与知识图谱协同架构图**
> - **位置**：此处（4.5.2节，"如图4.2所示"后）
> - **类型**：双路协同架构图（左右并行）
> - **内容要点**：向量检索路径（模糊匹配）+ 知识图谱验证路径（精确验证），标注两条路径的融合点

---

### 4.5.3 映射流程

映射算法的执行流程如下：接收自然语言名称，调用BGE-M3模型生成向量表示；通过FAISS索引检索Top-5相似向量，过滤相似度低于0.7的候选；根据实体类型在知识图谱中查询合法属性集列表；验证候选映射是否属于合法属性集。若验证通过，输出标准化映射；若验证失败，返回候选列表供用户确认。

映射结果附加到每个Facet元素的ifc_mapping字段中。以"承重墙"和"厚度"为例：实体Facet"承重墙"映射至IfcWall，属性Facet"厚度"映射至IfcWall实体下的Pset_WallCommon属性集中的Thickness属性。属性映射结果同时包含了实体关联信息（IfcWall），这是因为PropertyFacet的约束必须锚定到具体的实体-属性集-属性三层路径上，才能在IDS规则中正确定位检验目标。完整的映射结果JSON结构见附录A.2。

对于向量检索未能返回高于阈值候选的情况（即Top-5结果均低于0.7），系统将原始自然语言名称保留为未映射状态，并在后续的IDS构建阶段（阶段五）提示用户手动确认或修正映射结果。这一设计避免了低置信度映射被静默采纳而引入错误。

## 4.6 约束提取模块（阶段四）

约束提取是流水线的第四阶段，任务是从自然语言描述中提取结构化的约束条件。该阶段不涉及LLM调用，完全基于正则表达式模式匹配实现，保证了提取结果的确定性与可复现性。

### 4.6.1 约束类型分类

系统将约束条件分为四类，每类对应一组正则表达式模式：

**数值约束（BOUNDS）**：描述数值的边界条件。系统通过六种正则模式匹配：比较算符（≥、≤、>、<）、区间表述（between X and Y）、程度副词（at least、no more than）、范围表示（X-Y）。例如，"不小于200mm"解析为大于等于（gte）关系，边界值200，单位mm。

**枚举约束（ENUMERATION）**：描述属性的枚举值范围。系统通过四种模式匹配：引号包围的列表、逗号分隔的关键词、选择表述（one of、choose from）、互斥表述（either X or Y）。例如，"混凝土或钢材"解析为枚举值列表，包含"混凝土"与"钢材"两个选项。

**格式约束（PATTERN）**：描述属性值的格式要求。系统匹配"matching the pattern"、"format:"等关键词，提取正则表达式约束。

**长度约束（LENGTH）**：描述字符串的长度限制。系统匹配"max N characters"、"at least N characters"等表述，提取minLength/maxLength值。

### 4.6.2 提取与去重

约束提取模块对每个Facet元素的原始文本执行上述四类模式匹配，输出约束条件列表。提取完成后执行两步去重：对格式约束保留文本最长的条目；对枚举约束按值集合去重。每条约束附带置信度评分（数值约束0.9、枚举约束0.8、格式约束0.85、长度约束0.8）。

提取结果转换为IDS标准的约束JSON格式，供阶段五直接使用。表4.2展示了四类约束的提取示例。

**表4.2 约束提取示例**

| 输入文本 | 约束类型 | 提取结果 | 置信度 |
|----------|----------|----------|--------|
| "不小于200mm" | BOUNDS | 大于等于关系，边界值200，单位mm | 0.9 |
| "混凝土或钢材" | ENUMERATION | 枚举值：["混凝土", "钢材"] | 0.8 |
| "编码格式ABC-001" | PATTERN | 正则模式：[A-Z]{3}-[0-9]{3} | 0.85 |
| "名称不超过50字符" | LENGTH | 最大长度：50 | 0.8 |

## 4.7 IDS构建与验证模块（阶段五）

IDS构建是流水线的最终阶段，任务是将前四个阶段的输出整合为符合IDS XSD规范的规则文件。该阶段包含两个子步骤：先由LLM完成规则分组（Slot Assignment），再通过机械转换生成最终的IDS XML文件。

### 4.7.1 数据缝合与规则分组

前四个阶段分别产出了Facet元素列表（阶段二）与约束条件列表（阶段四），但两者尚未关联——系统需要将约束条件"缝合"到对应的Facet元素上。这一步骤通过双向子串匹配实现：对每个Facet元素的原始文本与每个约束条件的原始文本执行大小写不敏感的包含检测，若约束文本是Facet文本的子串，或反之，则将该约束附加到该Facet的constraints列表中。例如，Facet原始文本"厚度"与约束原始文本"不小于200mm"虽不完全相同，但通过子串匹配可建立关联。该策略不涉及LLM调用，保证了缝合结果的确定性。不过，双向子串匹配依赖文本层面的包含关系，对于语义相近但表述不同的场景（如Facet文本"墙体厚度"与约束文本"≥200mm"）可能无法建立关联，此时需要LLM在规则分组阶段辅助匹配。

缝合完成后，各Facet元素携带了完整的约束信息，但尚未组织为IDS规范要求的"适用范围（Applicability）+ 约束要求（Requirements）"结构。规则分组任务即确定哪些元素应作为适用范围（筛选目标实体），哪些应作为约束要求（检验属性条件）。

系统通过单次LLM调用完成分组。LLM接收原始规范文本与所有Facet元素的序列化描述，输出若干SpecificationSlot，每个Slot包含一个ApplicabilitySlot（实体Facet）与一个RequirementsSlot（属性/材料/分类等Facet）。LLM返回的分组结果经验证器检查——确保引用的Facet ID均存在且无重复使用——后进入下一步转换。

若LLM不可用，系统执行降级策略：为每个实体Facet创建一个独立的Specification，将所有非实体Facet归入其Requirements。

### 4.7.2 JSON到XML转换

IDS标准采用XML格式，遵循buildingSMART定义的XSD规范[37]。流水线内部使用JSON作为中间态数据格式，最终阶段通过转换器将JSON转换为符合XSD规范的XML文件。

转换器使用lxml库构建XML文档对象模型（DOM）树，流程分为三步。

第一步构建XML树骨架。根节点声明IDS标准的命名空间与XSD Schema位置，根节点下包含两个子节点：文件元信息（标题、版本、日期）与规则列表。每条规则节点通过"适用范围"与"约束要求"两个子节点表达其逻辑结构。

第二步映射Facet节点。转换器为每类Facet实现专门的构建方法，各类节点的字段组合不同：实体节点需要实体名称与可选的预定义类型；属性节点需要属性集名称、基础名称与可选的约束值，并支持指定IFC数据类型；直接属性节点约束实体的固有属性；分类节点约束分类系统与编码；材料节点约束材料名称；组合节点通过嵌套实体与关系属性表达包含关系。

第三步处理约束值的转换。IDS标准将约束值分为两种表示方式：简单值用于固定字符串，如实体名称IfcWall在输出时需统一转换为大写形式；复杂约束用于范围、枚举、格式等条件，每种约束类型映射为对应的XSD限制元素。系统支持四类约束的转换：数值约束映射为上下界限制，枚举约束映射为枚举值列表，格式约束映射为正则表达式，长度约束映射为最小与最大长度限制。各步骤的JSON输入与XSD输出对照见附录B。

### 4.7.3 XSD Schema验证

转换完成后，系统通过lxml库的XMLSchema类验证生成的XML是否符合IDS标准规范。Schema对象在首次加载后缓存，避免重复解析。验证过程自动检查XML树结构是否符合XSD规范，失败时返回包含行号与错误描述的详细信息。

常见验证错误包括四类：结构错误（如`<ids:requirements>`节点出现在`<ids:applicability>`之前，违反Schema规定的节点顺序）、类型错误（如`<ids:date>`内容不符合YYYY-MM-DD格式）、必填节点缺失（如specification节点缺少name属性）、命名空间错误（根节点未声明ids、xs、xsi三个命名空间前缀）。

验证失败时，系统根据错误类型采取不同的处理策略。对于实体名称错误（如输入了不存在的"IfcWalll"），系统回溯至阶段三的知识库映射环节，重新执行向量检索以获取正确的IFC实体名称。对于属性名称错误（如"Thicknesss"拼写错误），系统验证该属性是否属于目标实体的合法属性集，若不属于则返回该属性集下的合法属性列表供用户选择。对于结构错误与命名空间错误，系统将详细的错误信息（包含行号与描述）返回给用户，用户可选择手动修正或重新生成。这种分级处理策略在保证生成文件严格符合标准规范的同时，对可自动纠正的错误提供了修正路径。

### 4.7.4 输出与持久化

**IDS文件结构**

转换前的中间态JSON与最终的IDS XML文件具有对应的结构关系。中间态JSON包含两部分：info字段存储文件元信息（标题、版本、IFC版本），specifications字段存储规则定义列表。每条规则通过applicability字段约束目标实体类型（如IfcWall），通过requirements字段定义属性约束条件（如Thickness≥200mm）。转换器将此JSON转换为对应的IDS XML格式，其中实体名称统一转换为大写形式，数值约束转换为XSD限制元素。完整的JSON与XML对照示例见附录A.3。

**XML格式化与命名规范**

验证通过的XML文件序列化为格式化字符串，启用缩进排版与XML声明头，指定UTF-8字符编码。生成的文件以.ids为扩展名，遵循buildingSMART推荐的命名约定[37]。文件名采用"规则名称_版本号_日期.ids"的格式，例如"承重墙厚度约束_v1.0_2024-01-15.ids"，便于版本管理与历史追溯。

**与IFC审查工具的集成**

生成的IDS文件可直接用于IFC模型的合规性审查。系统集成ifctester与ifcopenshell两个开源工具：ifctester负责加载IDS文件并执行规则匹配，ifcopenshell负责解析IFC模型并提取实体属性[16]。审查流程为：ifcopenshell打开IFC模型文件，ifctester加载IDS规则并调用validate方法逐条执行匹配，最终输出JSON、HTML与BCF三种格式的审查报告（详见第五章）。

**多文件合并**

系统还实现了多文件合并功能，支持将多个IDS文件合并为单一规则集。合并流程包括解析输入文件、检查IFC版本一致性、合并规则列表、执行XSD验证。版本冲突处理支持三种策略：ask模式返回冲突信息供用户确认，use_first模式强制使用第一个文件的IFC版本，error模式抛出异常终止合并。

## 4.8 端到端处理示例

为完整展示五阶段流水线的数据流转，本节以一条涉及多种Facet类型的复合规范为例，追踪从自然语言到IDS XML文件的全过程。输入文本为："所有承重构件的混凝土强度等级不应低于C30，且必须包含Pset_WallCommon属性集。"

**阶段一（结构化解析）**：LLM将输入文本解析为三组元素——建筑构件"承重构件"（修饰词："承重"）、属性描述"强度等级"（约束文本："不应低于C30"）、以及属性集描述"Pset_WallCommon"。输出StructuredParseResult对象，包含building_objects、property_descriptions与unmatched_fragments三类列表。

**阶段二（Facet分类）**：LLM将"承重构件"归入entity_candidates（EntityFacet），将"强度等级"归入property_candidates（PropertyFacet），将"Pset_WallCommon"归入property_candidates中的PropertySetFacet子类。该示例展示了单条规范同时触发多种Facet类型的情况。

**阶段三（知识库映射）**：BGE-M3将"承重构件"编码为向量，FAISS检索到IfcWall（相似度0.85）与IfcBeam（相似度0.82）两个候选实体；将"强度等级"编码为向量，检索到Pset_MaterialProperties.Grade属性（相似度0.81）；将"Pset_WallCommon"直接与术语库精确匹配。知识图谱验证IfcWall确实关联Pset_WallCommon属性集，映射通过。

**阶段四（约束提取）**：正则表达式从"不应低于C30"中匹配到枚举约束：枚举值为["C30"]，语义上隐含"不低于"关系，系统将其转换为IDS格式的枚举约束。

**数据缝合**：约束"不应低于C30"通过子串匹配关联到PropertyFacet元素"强度等级"上；属性集描述"Pset_WallCommon"独立作为PropertySetFacet约束。

**阶段五（IDS构建）**：LLM将EntityFacet"承重构件"设为applicability，PropertyFacet"强度等级"与PropertySetFacet"Pset_WallCommon"共同设为requirements。转换器将JSON转换为XML，XSD验证通过，输出最终的IDS文件。该文件包含两个约束条件：一个要求构件必须包含Pset_WallCommon属性集，另一个要求Grade属性值为C30。

上述流程涉及三次LLM调用（阶段一、二、五各一次）、一次向量检索（阶段三）与一次正则提取（阶段四），完整耗时约25-30秒，其中LLM调用占总耗时的80%以上。

## 4.9 本章小结

本章阐述了IDS生成流水线的设计与实现。流水线采用五阶段结构化处理流程：阶段一通过Claude-3.5-Sonnet模型提取自然语言中的建筑构件、属性描述、材料要求与空间关系四类元素；阶段二将元素映射至IDS标准的七种Facet类型；阶段三通过向量-图协同检索实现IFC标准化命名映射；阶段四通过正则表达式提取数值、枚举、格式与长度四类约束；阶段五先通过双向子串匹配将约束缝合至对应Facet，再由LLM完成规则分组，最终通过转换器转换为符合XSD规范的IDS XML文件。

向量知识库作为阶段三的支撑，基于七类IFC术语库文件构建，采用BGE-M3嵌入模型生成1024维归一化向量，通过FAISS IndexFlatIP索引实现精确内积检索，相似度阈值设定为0.7。知识库支持按IFC版本筛选，采用LRU内存缓存（10,000条容量）与磁盘持久化双层机制保障检索性能。生成的IDS文件经XSD Schema验证后持久化存储，可直接被ifctester等标准审查工具加载执行，也可通过多文件合并功能整合为统一规则集。本章确立的流水线架构与知识库设计为第五章的系统实现与性能测试提供了算法基础。

---

## 第四章引用参考文献

| 编号 | 引用信息 |
|------|----------|
| [8] | Wu L, et al. Automated compliance checking in the architecture, engineering, and construction industry: A systematic review[J]. Automation in Construction, 2023. |
| [11] | Chen Z, et al. Large language model-based automated compliance checking for building designs[J]. 2024. |
| [16] | Nithya V, et al. IfcOpenShell: An open source IFC parsing library[J]. |
| [24] | Lewis P, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks[C]. NeurIPS, 2020. |
| [33] | Li Z, Wang N. BuildingGPT: A framework for BIM semantic query with LLM[J]. |
| [37] | buildingSMART International. Information Delivery Specification (IDS) Standard[EB/OL]. https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/, 2023. |
| [39] | Brown T, et al. Language models are few-shot learners[C]. NeurIPS, 2020. |
| [41] | Ji Z, et al. Survey of hallucination in natural language generation[J]. ACM Computing Surveys, 2023. |
| [46] | Xiao S, et al. C-Pack: Packaged resources to advance general Chinese embedding[J]. 2024. |
| [47] | Johnson J, Douze M, Jégou H. Billion-scale similarity search with GPUs[J]. IEEE Transactions on Big Data, 2021, 7(3): 535-547. |
| [49] | buildingSMART International. IDS 1.0 Official Documentation[EB/OL]. https://buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/. |

---

## 附录A：中间态数据结构

### A.1 Facet分类输出JSON结构

对应4.4.3节表4.3的完整JSON格式：

```json
{
  "entity_candidates": [
    {"source_text": "承重墙", "facet_type": "EntityFacet", "confidence": 0.95, "reasoning": "指定构件类型"}
  ],
  "property_candidates": [
    {"source_text": "厚度", "facet_type": "PropertyFacet", "confidence": 0.90, "reasoning": "属性名+约束值"}
  ],
  "material_candidates": [],
  "classification_candidates": [],
  "attribute_candidates": [],
  "partof_candidates": []
}
```

### A.2 知识库映射输出JSON结构

对应4.5.3节的映射结果：

```json
{
  "entity_candidates": [
    {
      "source_text": "承重墙",
      "facet_type": "EntityFacet",
      "ifc_mapping": {"entity": "IfcWall"}
    }
  ],
  "property_candidates": [
    {
      "source_text": "厚度",
      "facet_type": "PropertyFacet",
      "ifc_mapping": {"entity": "IfcWall", "property_set": "Pset_WallCommon", "property": "Thickness"}
    }
  ]
}
```

### A.3 IDS中间态JSON与XML对照

对应4.7.4节的IDS文件结构。以"承重墙厚度约束"为例：

**中间态JSON：**

```json
{
  "info": {
    "title": "承重墙厚度约束",
    "version": "1.0",
    "ifcVersion": ["IFC4"]
  },
  "specifications": [{
    "name": "承重墙厚度检查",
    "applicability": {
      "entity": {"name": "IfcWall"}
    },
    "requirements": [{
      "name": "厚度约束",
      "propertySet": "Pset_WallCommon",
      "property": "Thickness",
      "value": {"minValue": 200, "unit": "mm"}
    }]
  }]
}
```

**转换后的IDS XML：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ids:ids xmlns:ids="http://standards.buildingsmart.org/IDS"
         xmlns:xs="http://www.w3.org/2001/XMLSchema"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://standards.buildingsmart.org/IDS
         http://standards.buildingsmart.org/IDS/ids.xsd">
  <ids:info>
    <ids:title>承重墙厚度约束</ids:title>
    <ids:version>1.0</ids:version>
    <ids:date>2024-01-15</ids:date>
  </ids:info>
  <ids:specifications>
    <ids:specification name="承重墙厚度检查" ifcVersion="IFC4">
      <ids:applicability>
        <ids:entity>
          <ids:name>
            <ids:simpleValue>IFCWALL</ids:simpleValue>
          </ids:name>
        </ids:entity>
      </ids:applicability>
      <ids:requirements>
        <ids:property>
          <ids:propertySet>
            <ids:simpleValue>Pset_WallCommon</ids:simpleValue>
          </ids:propertySet>
          <ids:baseName>
            <ids:simpleValue>Thickness</ids:simpleValue>
          </ids:baseName>
          <ids:value>
            <xs:restriction base="xs:double">
              <xs:minInclusive value="200"/>
            </xs:restriction>
          </ids:value>
          <ids:datatype>IfcLengthMeasure</ids:datatype>
        </ids:property>
      </ids:requirements>
    </ids:specification>
  </ids:specifications>
</ids:ids>
```

## 附录B：JSON到XSD转换详细映射

对应4.7.2节三步转换流程的具体XSD元素映射。

### B.1 第一步：XML树骨架

**JSON输入（info字段）：**

```json
{
  "info": {
    "title": "承重墙厚度约束",
    "version": "1.0",
    "ifcVersion": ["IFC4"]
  }
}
```

**XSD输出：**

| JSON字段 | XSD父元素 | XSD子元素 | 说明 |
|----------|-----------|-----------|------|
| info.title | ids:info | ids:title | 文件标题 |
| info.version | ids:info | ids:version | 版本号 |
| info.ifcVersion | ids:specification | ifcVersion属性 | IFC版本声明 |
| specifications[] | ids:specifications | ids:specification | 规则列表，每条规则含name属性 |
| applicability | ids:specification | ids:applicability | 适用范围节点 |
| requirements[] | ids:specification | ids:requirements | 约束要求节点 |

### B.2 第二步：Facet节点映射

| Facet类型 | XSD子元素 | 必填/可选 | 说明 |
|----------|-----------|-----------|------|
| EntityFacet | ids:name | 必填 | 实体名称，simpleValue自动大写 |
| EntityFacet | ids:predefinedType | 可选 | 预定义类型（如Wall的Partitioning） |
| PropertyFacet | ids:propertySet | 必填 | 属性集名称（如Pset_WallCommon） |
| PropertyFacet | ids:baseName | 必填 | 属性名称（如Thickness） |
| PropertyFacet | ids:value | 可选 | 约束值，复杂约束时使用restriction |
| PropertyFacet | ids:datatype | 可选 | IFC数据类型（如IfcLengthMeasure） |
| AttributeFacet | ids:name | 必填 | 直接属性名称（如Name、Description） |
| AttributeFacet | ids:value | 可选 | 属性值约束 |
| ClassificationFacet | ids:system | 必填 | 分类系统名称 |
| ClassificationFacet | ids:value | 可选 | 分类编码约束 |
| MaterialFacet | ids:value | 必填 | 材料名称约束 |
| PartOfFacet | ids:entity | 必填 | 嵌套实体节点，含relation属性 |

### B.3 第三步：约束值类型映射

**简单值示例（实体名称）：**

| JSON输入 | XSD输出 |
|----------|---------|
| `"name": "IfcWall"` | `<ids:simpleValue>IFCWALL</ids:simpleValue>` |

简单值自动执行大写转换，直接嵌入simpleValue节点。

**复杂约束示例（四类约束）：**

| 约束类型 | JSON输入示例 | XSD base | XSD子元素 |
|----------|-------------|----------|-----------|
| 数值约束 | `{"minValue": 200, "maxValue": 500}` | xs:double | xs:minInclusive, xs:maxInclusive |
| 枚举约束 | `{"enum": ["C30", "C40", "C50"]}` | xs:string | xs:enumeration（多个） |
| 格式约束 | `{"pattern": "[A-Z]{3}-[0-9]{3}"}` | xs:string | xs:pattern |
| 长度约束 | `{"minLength": 1, "maxLength": 50}` | xs:string | xs:minLength, xs:maxLength |

**数值约束XSD示例（Thickness≥200mm）：**

```xml
<ids:value>
  <xs:restriction base="xs:double">
    <xs:minInclusive value="200"/>
  </xs:restriction>
</ids:value>
<ids:datatype>IfcLengthMeasure</ids:datatype>
```

**枚举约束XSD示例（强度等级为C30或C40）：**

```xml
<ids:value>
  <xs:restriction base="xs:string">
    <xs:enumeration value="C30"/>
    <xs:enumeration value="C40"/>
  </xs:restriction>
</ids:value>
```
