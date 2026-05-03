"""
测试完整pipeline - 保存每个阶段的输入和输出JSON

每个阶段保存两个文件：
- stage_X_input.json: 该阶段的输入数据
- stage_X_output.json: 该阶段的输出数据
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from a_structured_parser import runStructuredParser
from b_facet_classifier import runFacetClassifier
from c_knowledge_base_mapping import runKnowledgeBaseMapping
from d_constrains import runConstraintExtraction
from e_ids_builder.entry import runIDSBuilder


def make_json_safe(obj):
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    if hasattr(obj, '__dict__'):
        return make_json_safe(obj.__dict__)
    return str(obj)


async def test_full_pipeline_with_io():
    """测试完整pipeline，保存每个阶段的输入输出"""

    # 测试用例选择
    test_cases = {
        "bridge": "所有桥梁结构必须使用IfcBridge实体表示，必须包含在项目或场地中，必须有Name属性",
        "girders": "所有IfcElementAssembly实体，且PredefinedType为GIRDER的构件，必须包含在IfcBridgePart（类型为SUPERSTRUCTURE）的上层结构中，必须有Name属性，必须定义材料。"
    }

    # 选择测试用例（修改这里来切换测试）
    test_name = "girders"  # 可选: "bridge" 或 "girders"
    text = test_cases[test_name]

    print(f"\n{'='*80}")
    print(f"Testing Full Pipeline with Input/Output Logging")
    print(f"Test Case: {test_name}")
    print(f"{'='*80}\n")
    print(f"Input: {text}\n")

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"experimental_results/large_scale_test/pipeline_{test_name}_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========== Stage A: Structured Parser ==========
    print(f"[Stage A] Structured Parser...")

    # 保存输入
    stage_a_input = {"text": text}
    with open(output_dir / "stage_a_input.json", 'w', encoding='utf-8') as f:
        json.dump(stage_a_input, f, indent=2, ensure_ascii=False)

    # 执行
    res_a = await runStructuredParser(text)

    # 保存输出
    stage_a_output = {
        "building_objects": [make_json_safe(obj) for obj in res_a.building_objects],
        "property_descriptions": [make_json_safe(prop) for prop in res_a.property_descriptions],
        "material_requirements": [make_json_safe(mat) for mat in res_a.material_requirements],
        "spatial_relationships": [make_json_safe(rel) for rel in res_a.spatial_relationships],
        "unmatched_fragments": res_a.unmatched_fragments
    }
    with open(output_dir / "stage_a_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_a_output, f, indent=2, ensure_ascii=False)

    print(f"  Objects: {len(res_a.building_objects)}")
    print(f"  Properties: {len(res_a.property_descriptions)}")
    print(f"  Materials: {len(res_a.material_requirements)}")

    # ========== Stage B: Facet Classifier ==========
    print(f"\n[Stage B] Facet Classifier...")

    # 保存输入（Stage A的输出）
    with open(output_dir / "stage_b_input.json", 'w', encoding='utf-8') as f:
        json.dump(stage_a_output, f, indent=2, ensure_ascii=False)

    # 执行
    res_b = await runFacetClassifier(res_a)

    # 保存输出
    stage_b_output = {
        "entity_candidates": [make_json_safe(f) for f in getattr(res_b, 'entity_candidates', [])],
        "property_candidates": [make_json_safe(f) for f in getattr(res_b, 'property_candidates', [])],
        "attribute_candidates": [make_json_safe(f) for f in getattr(res_b, 'attribute_candidates', [])],
        "material_candidates": [make_json_safe(f) for f in getattr(res_b, 'material_candidates', [])],
        "classification_candidates": [make_json_safe(f) for f in getattr(res_b, 'classification_candidates', [])],
        "partof_candidates": [make_json_safe(f) for f in getattr(res_b, 'partof_candidates', [])]
    }
    with open(output_dir / "stage_b_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_b_output, f, indent=2, ensure_ascii=False)

    total_facets = sum(len(v) for v in stage_b_output.values())
    print(f"  Total facets: {total_facets}")
    for key, value in stage_b_output.items():
        if value:
            print(f"    {key}: {len(value)}")

    # ========== Stage C: Knowledge Base Mapping ==========
    print(f"\n[Stage C] Knowledge Base Mapping...")

    # 保存输入（Stage B的输出）
    with open(output_dir / "stage_c_input.json", 'w', encoding='utf-8') as f:
        json.dump(stage_b_output, f, indent=2, ensure_ascii=False)

    # 执行
    facets = await runKnowledgeBaseMapping(res_b)

    # 保存输出
    stage_c_output = [make_json_safe(f) for f in facets]
    with open(output_dir / "stage_c_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_c_output, f, indent=2, ensure_ascii=False)

    print(f"  Mapped facets: {len(facets)}")
    for i, facet in enumerate(facets, 1):
        print(f"    {i}. [{facet.facet_type}] {facet.original_text[:40]}... -> {facet.mapped_name} (conf: {facet.confidence:.3f})")

    # ========== Stage D: Constraint Extraction ==========
    print(f"\n[Stage D] Constraint Extraction...")

    # 保存输入（Stage C的输出）
    with open(output_dir / "stage_d_input.json", 'w', encoding='utf-8') as f:
        json.dump(stage_c_output, f, indent=2, ensure_ascii=False)

    # 执行 - 返回约束列表
    constraints = runConstraintExtraction(facets)

    # 保存输出（约束列表）
    stage_d_output = [make_json_safe(c) for c in constraints]
    with open(output_dir / "stage_d_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_d_output, f, indent=2, ensure_ascii=False)

    print(f"  Extracted constraints: {len(constraints)}")

    # 合并约束到facets中（模拟tests/e.py的逻辑）
    merged_count = 0
    for facet in facets:
        if facet.constraints is None:
            facet.constraints = []

        facet_text = (facet.original_text or "").strip().lower()

        for constr in constraints:
            constr_text = (constr.original_text or "").strip().lower()
            # 包含匹配逻辑
            if constr_text and facet_text and (constr_text in facet_text or facet_text in constr_text):
                facet.constraints.append(constr)
                merged_count += 1

    print(f"  Merged {merged_count} constraints into facets")

    # ========== Stage E: IDS Builder ==========
    print(f"\n[Stage E] IDS Builder...")

    # 保存输入（合并后的facets）
    stage_e_input = [make_json_safe(f) for f in facets]
    with open(output_dir / "stage_e_input.json", 'w', encoding='utf-8') as f:
        json.dump(stage_e_input, f, indent=2, ensure_ascii=False)

    # 执行 - 传入原始文本
    result = await runIDSBuilder(facets, text=text)

    # 保存输出
    stage_e_output = make_json_safe(result)
    with open(output_dir / "stage_e_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_e_output, f, indent=2, ensure_ascii=False)

    num_specs = len(result.get('specifications', []))
    print(f"  Generated specifications: {num_specs}")
    for i, spec in enumerate(result.get('specifications', []), 1):
        print(f"    {i}. {spec.get('name', 'Unnamed')}")

    print(f"\n{'='*80}")
    print(f"Pipeline completed!")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")

    print(f"Files saved:")
    for stage in ['a', 'b', 'c', 'd', 'e']:
        print(f"  - stage_{stage}_input.json")
        print(f"  - stage_{stage}_output.json")

    return num_specs > 0


if __name__ == "__main__":
    success = asyncio.run(test_full_pipeline_with_io())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
