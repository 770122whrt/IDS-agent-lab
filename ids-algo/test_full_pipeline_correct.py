"""
测试完整pipeline - 使用正确的字段名访问Stage A输出

不修改源码，而是创建一个包装函数来正确处理Stage A的输出
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


async def test_full_pipeline_v2():
    """测试完整pipeline，使用v2自然语言输入"""

    # 加载v2输入
    with open("experimental_results/large_scale_test/ids_input_natural_language_v2.json", 'r', encoding='utf-8') as f:
        specs = json.load(f)

    test_spec = specs[0]
    text = test_spec['text']

    print(f"\n{'='*80}")
    print(f"Testing Full Pipeline with V2 Input")
    print(f"{'='*80}\n")
    print(f"Input: {text[:100]}...\n")

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"experimental_results/large_scale_test/full_pipeline_test_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stage A
    print(f"[Stage A] Structured Parser...")
    res_a = await runStructuredParser(text)

    # 正确访问Stage A的字段
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

    # Stage B
    print(f"\n[Stage B] Facet Classifier...")
    res_b = await runFacetClassifier(res_a)

    stage_b_output = {
        "facets": [make_json_safe(f) for f in getattr(res_b, 'facets', [])]
    }

    with open(output_dir / "stage_b_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_b_output, f, indent=2, ensure_ascii=False)

    print(f"  Facets: {len(getattr(res_b, 'facets', []))}")

    # Stage C
    print(f"\n[Stage C] Knowledge Base Mapping...")
    facets = await runKnowledgeBaseMapping(res_b)

    stage_c_output = [make_json_safe(f) for f in facets]

    with open(output_dir / "stage_c_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_c_output, f, indent=2, ensure_ascii=False)

    print(f"  Mapped facets: {len(facets)}")
    for i, facet in enumerate(facets, 1):
        print(f"    {i}. [{facet.facet_type}] {facet.original_text[:40]}... -> {facet.mapped_name} ({facet.confidence:.3f})")

    # Stage D
    print(f"\n[Stage D] Constraint Extraction...")
    constrained_facets = await runConstraintExtraction(facets)

    stage_d_output = [make_json_safe(f) for f in constrained_facets]

    with open(output_dir / "stage_d_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_d_output, f, indent=2, ensure_ascii=False)

    print(f"  Constrained facets: {len(constrained_facets)}")

    # Stage E
    print(f"\n[Stage E] IDS Builder...")
    result = await runIDSBuilder(constrained_facets)

    stage_e_output = make_json_safe(result)

    with open(output_dir / "stage_e_output.json", 'w', encoding='utf-8') as f:
        json.dump(stage_e_output, f, indent=2, ensure_ascii=False)

    num_specs = len(result.get('specifications', []))
    print(f"  Generated specifications: {num_specs}")

    print(f"\n{'='*80}")
    print(f"Pipeline completed!")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")

    return num_specs > 0


if __name__ == "__main__":
    success = asyncio.run(test_full_pipeline_v2())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
