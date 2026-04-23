"""
测试改进版自然语言输入 - 单样本快速验证

使用ids_input_natural_language_v2.json测试第一个specification
验证Stage A是否能够正确解析简洁的自然语言格式

作者: IDS-Agent
日期: 2026-04-23
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from pipeline import run_ids_pipeline


async def test_improved_natural_language():
    """测试改进版自然语言输入"""

    # 等待v2文件生成
    v2_file = "experimental_results/large_scale_test/ids_input_natural_language_v2.json"

    print("Waiting for v2 natural language file...")
    while not Path(v2_file).exists():
        await asyncio.sleep(2)

    print(f"Loading improved natural language specs from: {v2_file}")
    with open(v2_file, 'r', encoding='utf-8') as f:
        specs = json.load(f)

    print(f"Loaded {len(specs)} specifications\n")

    # Test first spec
    test_spec = specs[0]

    print(f"{'='*80}")
    print(f"Testing Specification {test_spec['id']}")
    print(f"{'='*80}\n")
    print(f"Natural language input:")
    print(f"{test_spec['text']}\n")
    print(f"{'='*80}\n")

    # Run pipeline
    print("Running pipeline...")
    result, timing, stage_outputs = await run_ids_pipeline(
        test_spec['text'],
        return_timing=True,
        return_stage_outputs=True
    )

    # Check Stage A output
    stage_a = stage_outputs.get('stage_a', {})
    print(f"\n{'='*80}")
    print("STAGE A RESULTS")
    print(f"{'='*80}")
    print(f"Objects: {len(stage_a.get('objects', []))}")
    print(f"Properties: {len(stage_a.get('properties', []))}")
    print(f"Materials: {len(stage_a.get('materials', []))}")

    if stage_a.get('objects'):
        print("\nObjects found:")
        for obj in stage_a['objects']:
            print(f"  - {obj}")

    if stage_a.get('properties'):
        print("\nProperties found:")
        for prop in stage_a['properties']:
            print(f"  - {prop}")

    # Check Stage C mappings
    stage_c = stage_outputs.get('stage_c_mappings', [])
    print(f"\n{'='*80}")
    print("STAGE C RESULTS")
    print(f"{'='*80}")
    print(f"Mapped facets: {len(stage_c)}")

    if stage_c:
        print("\nMappings:")
        for i, facet in enumerate(stage_c[:5], 1):  # Show first 5
            print(f"  {i}. [{facet.get('facet_type')}] '{facet.get('original_text', '')[:50]}...'")
            print(f"     -> {facet.get('mapped_name')} (confidence: {facet.get('confidence', 0):.3f})")

    # Check final output
    num_specs = len(result.get('specifications', []))
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Generated specifications: {num_specs}")
    print(f"Total time: {sum(timing.values()):.2f}s")

    if num_specs > 0:
        print("\n[SUCCESS] Pipeline generated IDS specifications!")
    else:
        print("\n[FAILED] Pipeline did not generate any specifications")

    print(f"{'='*80}\n")

    return {
        'stage_a_objects': len(stage_a.get('objects', [])),
        'stage_a_properties': len(stage_a.get('properties', [])),
        'stage_c_mappings': len(stage_c),
        'final_specs': num_specs,
        'success': num_specs > 0
    }


async def main():
    """主函数"""
    try:
        result = await test_improved_natural_language()

        if result['success']:
            print("\n[OK] Test PASSED - Improved natural language format works!")
        else:
            print("\n[FAILED] Test FAILED - Still need to improve the format")

    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
