# 第四章图片生成提示词

## 图4.1 IDS生成五阶段流水线流程图

**生成要求：** 横板（16:9），学术论文风格，白底，中英文标注

**Prompt：**

```
A clean, professional horizontal flowchart diagram for an academic paper, white background, landscape 16:9 aspect ratio.

The diagram shows a five-stage pipeline flowing left to right, connected by solid arrows:

Stage 1: "结构化解析 / Structured Parser" — a rounded rectangle box in light blue (#D6E4F0). Inside the box, show icons of a document and a brain symbol. Below the box, a small annotation: "输入: 自然语言文本 → 输出: StructuredParseResult (JSON)"

Stage 2: "Facet分类 / Facet Classifier" — a rounded rectangle box in light green (#D5E8D4). Inside, show a category/tag icon. Below: "输入: 结构化元素 → 输出: FacetClassification (JSON)"

Stage 3: "知识库映射 / Knowledge Base Mapping" — a rounded rectangle box in light orange (#FFE6CC). Inside, show a database and vector icon. Below: "输入: Facet候选 → 输出: IFC标准映射 (JSON)"

Stage 4: "约束提取 / Constraint Extraction" — a rounded rectangle box in light purple (#E1D5E7). Inside, show a regex/pattern icon. Below: "输入: 原始文本 → 输出: 约束条件 (JSON)"

Stage 5: "IDS构建 / IDS Builder" — a rounded rectangle box in light red (#F8CECC). Inside, show an XML document icon. Below: "输入: 前四阶段结果 → 输出: IDS XML文件"

Between stages, draw bidirectional data flow arrows with small JSON document icons on them.

At the bottom, a dashed rectangle spanning all five stages labeled "中间态数据格式: JSON", indicating the data passing mechanism between stages.

Style: minimalist academic diagram, no 3D effects, flat design, clear Chinese and English bilingual labels, sans-serif font, suitable for printing in a thesis.
```

---

## 图4.2 向量检索与知识图谱协同架构图

**生成要求：** 横板（16:9），学术论文风格，白底，双路并行架构

**Prompt：**

```
A clean, professional horizontal architecture diagram for an academic paper, white background, landscape 16:9 aspect ratio.

The diagram shows a dual-path retrieval architecture with two parallel processing paths:

TOP PATH — "向量检索路径 / Vector Retrieval Path" (blue theme):
Left side: A box labeled "自然语言输入 / NL Input" (e.g., "承重墙", "厚度") with a text icon.
Arrow → A box labeled "BGE-M3 编码器 / BGE-M3 Encoder" with a neural network icon, showing "1024维向量".
Arrow → A box labeled "FAISS 索引检索 / FAISS Index Search" with a database icon, showing "Top-5 候选, 阈值=0.7".
Arrow → Output box: "候选映射 / Candidate Mappings" (e.g., IfcWall, Pset_WallCommon.Thickness).

BOTTOM PATH — "知识图谱验证路径 / Knowledge Graph Verification Path" (green theme):
Left side: A box labeled "IFC实体知识图谱 / IFC Entity Knowledge Graph" with a graph/network icon.
Inside, show three connected layers: "实体层 (IfcWall, IfcBeam...)" → "属性集层 (Pset_WallCommon...)" → "属性层 (Thickness, LoadBearing...)" connected by arrows.
Arrow → A box labeled "合法性验证 / Legality Verification" with a checkmark icon.
Arrow → Output box: "验证通过的映射 / Verified Mappings".

RIGHT SIDE — Fusion point:
Both paths converge at a central box labeled "融合结果 / Fusion Result" with a merge icon.
Below the fusion box: "最终映射 / Final Mapping: IfcWall → Pset_WallCommon → Thickness".

Draw the two paths as parallel horizontal lanes, with the vector path on top and the knowledge graph path on bottom, converging on the right side.

Style: minimalist academic diagram, no 3D effects, flat design, clear Chinese and English bilingual labels, sans-serif font, blue (#2E75B6) for vector path, green (#548235) for knowledge graph path, suitable for printing in a thesis.
```

---

## 使用说明

1. 将Prompt复制到GPT-5.5（DALL-E 4）中生成
2. 生成后检查中文是否正确渲染（AI生图中文可能有误，需手动PS修正）
3. 建议生成PNG格式，分辨率至少300dpi
4. 插入Word时设置宽度为页面宽度（约15cm），居中对齐
