"""
使用改进的v2自然语言测试，保存完整的ABCDE中间文件
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from pipeline import run_ids_pipeline


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


async def main():
    """主函数"""
    # 加载v2自然语言
    with open("experimental_results/large_scale_test/ids_input_natural_language_v2.json", "r", encoding="utf-8") as f:
        specs = json.load(f)

    # 测试第一个spec
    test_spec = specs[0]

    print(f"{'='*80}")
    print(f"Testing Specification {test_spec['id']} with V2 Natural Language")
    print(f"{'='*80}\n")
    print(f"Input text:\n{test_spec['text']}\n")
    print(f"{'='*80}\n")

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"experimental_results/large_scale_test/debug_spec_{test_spec['id']}_v2_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 运行pipeline
    result, timing, stage_outputs = await run_ids_pipeline(
        test_spec['text'],
        return_timing=True,
        return_stage_outputs=True
    )

    # 转换为JSON安全格式
    result_safe = make_json_safe(result)
    timing_safe = make_json_safe(timing)
    stage_outputs_safe = make_json_safe(stage_outputs)

    # 保存输入
    with open(output_dir / "a1_input_spec_1.txt", 'w', encoding='utf-8') as f:
        f.write(test_spec['text'])

    # 保存Stage A输出
    stage_a = stage_outputs_safe.get('stage_a', {})
    with open(output_dir / "a2_output_parsed_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_a, f, indent=2, ensure_ascii=False)

    print(f"[Stage A] Structured Parser")
    print(f"  Objects: {len(stage_a.get('objects', []))}")
    print(f"  Properties: {len(stage_a.get('properties', []))}")
    print(f"  Materials: {len(stage_a.get('materials', []))}")
    if stage_a.get('objects'):
        print(f"  Objects detail:")
        for obj in stage_a['objects']:
            print(f"    - {obj}")

    # 保存Stage B输出
    stage_b = stage_outputs_safe.get('stage_b', {})
    with open(output_dir / "b1_input_parsed_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_a, f, indent=2, ensure_ascii=False)
    with open(output_dir / "b2_output_classified_facets_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_b, f, indent=2, ensure_ascii=False)

    print(f"\n[Stage B] Facet Classifier")
    print(f"  Facets: {len(stage_b.get('facets', []))}")

    # 保存Stage C输出
    stage_c = stage_outputs_safe.get('stage_c_mappings', [])
    with open(output_dir / "c1_input_classified_facets_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_b, f, indent=2, ensure_ascii=False)
    with open(output_dir / "c2_output_mapped_facets_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_c, f, indent=2, ensure_ascii=False)

    print(f"\n[Stage C] Knowledge Base Mapping")
    print(f"  Mapped facets: {len(stage_c)}")
    print(f"\n  Detailed mappings:")
    for i, facet in enumerate(stage_c, 1):
        print(f"    {i}. [{facet.get('facet_type')}] '{facet.get('original_text', '')[:60]}...'")
        print(f"       -> {facet.get('mapped_name')} (confidence: {facet.get('confidence', 0):.3f})")
        if facet.get('ifc_item'):
            ifc_item = facet['ifc_item']
            print(f"       IFC Item: {ifc_item.get('name')} ({ifc_item.get('item_type')})")
            print(f"       Definition: {ifc_item.get('definition', '')[:80]}...")

    # 保存Stage D输出
    stage_d = stage_outputs_safe.get('stage_d', {})
    with open(output_dir / "d1_input_mapped_facets_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_c, f, indent=2, ensure_ascii=False)
    with open(output_dir / "d2_output_constrained_facets_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_d, f, indent=2, ensure_ascii=False)

    print(f"\n[Stage D] Constraint Extraction")
    print(f"  Constraints: {len(stage_d.get('constraints', []))}")

    # 保存Stage E输出
    with open(output_dir / "e1_input_constrained_facets_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(stage_d, f, indent=2, ensure_ascii=False)
    with open(output_dir / "e2_output_ids_json_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(result_safe, f, indent=2, ensure_ascii=False)

    num_specs = len(result_safe.get('specifications', []))
    print(f"\n[Stage E] IDS Builder")
    print(f"  Generated specifications: {num_specs}")

    # 保存摘要
    summary = {
        'spec_id': test_spec['id'],
        'timestamp': datetime.now().isoformat(),
        'input_text': test_spec['text'],
        'timing': timing_safe,
        'total_time': sum(timing_safe.values()),
        'stage_summary': {
            'stage_a': {
                'objects': len(stage_a.get('objects', [])),
                'properties': len(stage_a.get('properties', [])),
                'materials': len(stage_a.get('materials', []))
            },
            'stage_b': {
                'facets': len(stage_b.get('facets', []))
            },
            'stage_c': {
                'mapped_facets': len(stage_c)
            },
            'stage_d': {
                'constraints': len(stage_d.get('constraints', []))
            },
            'stage_e': {
                'specifications': num_specs
            }
        },
        'success': num_specs > 0
    }

    with open(output_dir / "summary_spec_1.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total time: {summary['total_time']:.2f}s")
    print(f"Success: {summary['success']}")
    print(f"\nAll files saved to: {output_dir}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
