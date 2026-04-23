"""
单样本诊断测试脚本 - 保存ABCDE所有阶段的中间输出
用于深度分析pipeline各阶段的输入输出，特别是Stage C的映射质量
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


async def test_single_spec_with_debug(spec_id: str, spec_text: str, output_dir: str):
    """
    测试单个specification，保存所有阶段的中间输出

    Args:
        spec_id: Specification ID (e.g., "1")
        spec_text: Natural language specification text
        output_dir: Output directory for all intermediate files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"Testing Specification {spec_id}")
    print(f"{'='*80}\n")
    print(f"Input text length: {len(spec_text)} characters")
    print(f"Output directory: {output_path}")
    print(f"\n{'='*80}\n")

    try:
        # Run pipeline with full stage outputs
        result, timing, stage_outputs = await run_ids_pipeline(
            spec_text,
            return_timing=True,
            return_stage_outputs=True
        )

        # Make everything JSON-safe
        result_safe = make_json_safe(result)
        timing_safe = make_json_safe(timing)
        stage_outputs_safe = make_json_safe(stage_outputs)

        # ============================================================
        # Save Stage A outputs
        # ============================================================
        print("[Stage A] Structured Parser")
        with open(output_path / f"a1_input_spec_{spec_id}.txt", 'w', encoding='utf-8') as f:
            f.write(spec_text)

        stage_a_output = stage_outputs_safe.get('stage_a', {})
        with open(output_path / f"a2_output_parsed_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_a_output, f, indent=2, ensure_ascii=False)

        print(f"  - Objects: {len(stage_a_output.get('objects', []))}")
        print(f"  - Properties: {len(stage_a_output.get('properties', []))}")
        print(f"  - Materials: {len(stage_a_output.get('materials', []))}")
        print(f"  - Time: {timing_safe.get('stage_a', 0):.2f}s")

        # ============================================================
        # Save Stage B outputs
        # ============================================================
        print("\n[Stage B] Facet Classifier")
        stage_b_output = stage_outputs_safe.get('stage_b', {})
        with open(output_path / f"b1_input_parsed_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_a_output, f, indent=2, ensure_ascii=False)
        with open(output_path / f"b2_output_classified_facets_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_b_output, f, indent=2, ensure_ascii=False)

        print(f"  - Facets: {len(stage_b_output.get('facets', []))}")
        print(f"  - Time: {timing_safe.get('stage_b', 0):.2f}s")

        # ============================================================
        # Save Stage C outputs (MOST IMPORTANT FOR DIAGNOSIS)
        # ============================================================
        print("\n[Stage C] Knowledge Base Mapping")
        stage_c_mappings = stage_outputs_safe.get('stage_c_mappings', [])
        with open(output_path / f"c1_input_classified_facets_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_b_output, f, indent=2, ensure_ascii=False)
        with open(output_path / f"c2_output_mapped_facets_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_c_mappings, f, indent=2, ensure_ascii=False)

        print(f"  - Mapped facets: {len(stage_c_mappings)}")
        print(f"  - Time: {timing_safe.get('stage_c', 0):.2f}s")

        # Print detailed mapping info for diagnosis
        print("\n  [Stage C] Detailed Mappings:")
        for i, facet in enumerate(stage_c_mappings, 1):
            facet_type = facet.get('facet_type', 'unknown')
            original = facet.get('original_text', '')[:60]
            mapped = facet.get('mapped_name', '')
            confidence = facet.get('confidence', 0)
            print(f"    {i}. [{facet_type}] '{original}...' -> '{mapped}' (conf: {confidence:.3f})")

        # ============================================================
        # Save Stage D outputs
        # ============================================================
        print("\n[Stage D] Constraint Extraction")
        stage_d_output = stage_outputs_safe.get('stage_d', {})
        with open(output_path / f"d1_input_mapped_facets_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_c_mappings, f, indent=2, ensure_ascii=False)
        with open(output_path / f"d2_output_constrained_facets_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_d_output, f, indent=2, ensure_ascii=False)

        print(f"  - Constraints: {len(stage_d_output.get('constraints', []))}")
        print(f"  - Time: {timing_safe.get('stage_d', 0):.2f}s")

        # ============================================================
        # Save Stage E outputs
        # ============================================================
        print("\n[Stage E] IDS Builder")
        with open(output_path / f"e1_input_constrained_facets_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(stage_d_output, f, indent=2, ensure_ascii=False)
        with open(output_path / f"e2_output_ids_json_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(result_safe, f, indent=2, ensure_ascii=False)

        num_specs = len(result_safe.get('specifications', []))
        print(f"  - Generated specifications: {num_specs}")
        print(f"  - Merge time: {timing_safe.get('stage_e_merge', 0):.2f}s")
        print(f"  - Build time: {timing_safe.get('stage_e_build', 0):.2f}s")

        # ============================================================
        # Save Summary
        # ============================================================
        total_time = sum([
            timing_safe.get('stage_a', 0),
            timing_safe.get('stage_b', 0),
            timing_safe.get('stage_c', 0),
            timing_safe.get('stage_d', 0),
            timing_safe.get('stage_e_merge', 0),
            timing_safe.get('stage_e_build', 0)
        ])

        summary = {
            'spec_id': spec_id,
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'timing': timing_safe,
            'total_time': total_time,
            'num_specifications': num_specs,
            'stage_summary': {
                'stage_a': {
                    'objects': len(stage_a_output.get('objects', [])),
                    'properties': len(stage_a_output.get('properties', [])),
                    'materials': len(stage_a_output.get('materials', []))
                },
                'stage_b': {
                    'facets': len(stage_b_output.get('facets', []))
                },
                'stage_c': {
                    'mapped_facets': len(stage_c_mappings)
                },
                'stage_d': {
                    'constraints': len(stage_d_output.get('constraints', []))
                },
                'stage_e': {
                    'specifications': num_specs
                }
            }
        }

        with open(output_path / f"summary_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}\n")
        print(f"Total time: {total_time:.2f}s")
        print(f"Generated specifications: {num_specs}")
        print(f"\nAll intermediate files saved to: {output_path}")
        print(f"\n{'='*80}")
        print("KEY FILES TO CHECK:")
        print(f"{'='*80}")
        print(f"  c2_output_mapped_facets_spec_{spec_id}.json  <- Stage C mapping quality")
        print(f"  e2_output_ids_json_spec_{spec_id}.json       <- Final IDS output")
        print(f"  summary_spec_{spec_id}.json                  <- Overall summary")
        print(f"{'='*80}\n")

        return summary

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()

        error_info = {
            'spec_id': spec_id,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

        with open(output_path / f"error_spec_{spec_id}.json", 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2, ensure_ascii=False)

        return error_info


async def main():
    """Main function"""
    # Load natural language specs
    json_path = "experimental_results/large_scale_test/ids_input_natural_language.json"

    print(f"Loading specifications from: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        specs = json.load(f)

    print(f"Loaded {len(specs)} specifications\n")

    # Test the first specification (should be IfcBridge related)
    test_spec = specs[0]

    print(f"Testing Specification {test_spec['id']}")
    print(f"Text preview: {test_spec['text'][:200]}...\n")

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"experimental_results/large_scale_test/debug_spec_{test_spec['id']}_{timestamp}"

    # Run test
    result = await test_single_spec_with_debug(
        spec_id=test_spec['id'],
        spec_text=test_spec['text'],
        output_dir=output_dir
    )

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)
    print(f"\nCheck output directory for all intermediate files:")
    print(f"  {output_dir}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
