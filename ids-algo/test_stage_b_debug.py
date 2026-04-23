"""
测试Stage B - Facet Classifier

单独测试Stage B，看看为什么返回空facets
"""

import asyncio
import json
from pathlib import Path
from a_structured_parser import StructuredParseResult
from b_facet_classifier import runFacetClassifier


async def test_stage_b():
    """测试Stage B对Stage A输出的处理"""

    # 加载Stage A的输出
    stage_a_file = "experimental_results/large_scale_test/debug_spec_1_v2_20260423_125545/a2_output_parsed_spec_1.json"

    print(f"\n{'='*80}")
    print(f"Testing Stage B - Facet Classifier")
    print(f"{'='*80}\n")

    with open(stage_a_file, 'r', encoding='utf-8') as f:
        stage_a_data = json.load(f)

    print(f"Stage A output:")
    print(f"  Objects: {len(stage_a_data['objects'])}")
    print(f"  Properties: {len(stage_a_data['properties'])}")
    print(f"  Materials: {len(stage_a_data['materials'])}")

    # 转换为StructuredParseResult对象
    # 注意：需要添加缺失的字段
    stage_a_data_complete = {
        "building_objects": stage_a_data['objects'],
        "property_descriptions": stage_a_data['properties'],
        "material_requirements": stage_a_data['materials'],
        "spatial_relationships": [],
        "unmatched_fragments": []
    }

    parse_result = StructuredParseResult.from_dict(stage_a_data_complete)

    print(f"\nStructuredParseResult created:")
    print(f"  building_objects: {len(parse_result.building_objects)}")
    print(f"  property_descriptions: {len(parse_result.property_descriptions)}")
    print(f"  material_requirements: {len(parse_result.material_requirements)}")

    # 调用Stage B
    print(f"\n{'-'*80}")
    print(f"Calling Stage B...")
    print(f"{'-'*80}\n")

    facet_result = await runFacetClassifier(parse_result)

    # 检查结果
    print(f"\nStage B output:")
    print(f"  Type: {type(facet_result)}")
    print(f"  Attributes: {dir(facet_result)}")

    if hasattr(facet_result, 'entity_candidates'):
        print(f"\n  entity_candidates: {len(facet_result.entity_candidates)}")
        for i, candidate in enumerate(facet_result.entity_candidates, 1):
            print(f"    {i}. {candidate}")

    if hasattr(facet_result, 'property_candidates'):
        print(f"\n  property_candidates: {len(facet_result.property_candidates)}")
        for i, candidate in enumerate(facet_result.property_candidates, 1):
            print(f"    {i}. {candidate}")

    if hasattr(facet_result, 'material_candidates'):
        print(f"\n  material_candidates: {len(facet_result.material_candidates)}")

    if hasattr(facet_result, 'attribute_candidates'):
        print(f"\n  attribute_candidates: {len(facet_result.attribute_candidates)}")

    if hasattr(facet_result, 'classification_candidates'):
        print(f"\n  classification_candidates: {len(facet_result.classification_candidates)}")

    if hasattr(facet_result, 'partof_candidates'):
        print(f"\n  partof_candidates: {len(facet_result.partof_candidates)}")

    # 保存结果
    output_file = "experimental_results/large_scale_test/stage_b_test_output.json"

    if hasattr(facet_result, '__dict__'):
        result_dict = vars(facet_result)

        def make_serializable(obj):
            if hasattr(obj, '__dict__'):
                return {k: make_serializable(v) for k, v in vars(obj).items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            else:
                return obj

        serializable_result = make_serializable(facet_result)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_result, f, indent=2, ensure_ascii=False)

        print(f"\n{'-'*80}")
        print(f"Result saved to: {output_file}")
        print(f"{'-'*80}\n")

    total_facets = 0
    if hasattr(facet_result, 'entity_candidates'):
        total_facets += len(facet_result.entity_candidates)
    if hasattr(facet_result, 'property_candidates'):
        total_facets += len(facet_result.property_candidates)
    if hasattr(facet_result, 'material_candidates'):
        total_facets += len(facet_result.material_candidates)

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total facets generated: {total_facets}")
    print(f"Expected: 5 (1 entity + 4 properties)")
    print(f"Status: {'✅ PASS' if total_facets >= 5 else '❌ FAIL'}")
    print(f"{'='*80}\n")

    return facet_result


if __name__ == "__main__":
    asyncio.run(test_stage_b())
