"""
Large-Scale Test Script Using Natural Language JSON Input

This script tests all 45 specifications from the natural language JSON
generated in Phase 1, replacing the simplified text extraction that
caused 85% information loss.

Target Metrics:
- Match Rate: 85%+ (from baseline 53.3%)
- Requirements Retention: 70%+ (from baseline 3.8%)
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

from pipeline import run_ids_pipeline


def make_json_safe(obj):
    """Convert objects to JSON-safe format"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Convert objects with __dict__ to dictionaries
        return make_json_safe(obj.__dict__)
    else:
        # Fallback: convert to string
        return str(obj)


def load_natural_language_specs(json_path: str) -> List[Dict]:
    """Load specifications from natural language JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def test_single_specification(spec: Dict, spec_index: int, total: int) -> Dict:
    """
    Test a single specification through the pipeline

    Args:
        spec: Specification dict with id, text, language
        spec_index: Current index (1-based)
        total: Total number of specs

    Returns:
        Dictionary containing test results
    """
    spec_id = spec['id']
    text = spec['text']

    print(f"[{spec_index}/{total}] Testing Spec {spec_id}...", end=" ", flush=True)

    start_time = time.perf_counter()

    try:
        # Run pipeline with timing and stage outputs
        result, timing, stage_outputs = await run_ids_pipeline(
            text,
            return_timing=True,
            return_stage_outputs=True
        )

        elapsed = time.perf_counter() - start_time

        # Extract key metrics
        num_specs = len(result.get("specifications", [])) if result else 0
        stage_c_mappings = stage_outputs.get("stage_c_mappings", [])

        # Count requirements in Stage C mappings
        num_requirements = sum(1 for m in stage_c_mappings if m.get("facet_type") in ["property", "attribute", "material", "classification"])

        print(f"OK ({elapsed:.2f}s, {num_specs} specs, {num_requirements} reqs)")

        return {
            "spec_id": spec_id,
            "spec_index": spec_index,
            "success": True,
            "elapsed_time": elapsed,
            "timing": timing,
            "num_specifications": num_specs,
            "num_requirements": num_requirements,
            "stage_c_mappings": make_json_safe(stage_c_mappings),
            "output": make_json_safe(result),
            "error": None
        }

    except Exception as e:
        elapsed = time.perf_counter() - start_time
        print(f"FAILED ({elapsed:.2f}s) - {str(e)[:50]}")

        return {
            "spec_id": spec_id,
            "spec_index": spec_index,
            "success": False,
            "elapsed_time": elapsed,
            "timing": {},
            "num_specifications": 0,
            "num_requirements": 0,
            "stage_c_mappings": [],
            "output": None,
            "error": str(e)
        }


def calculate_metrics(results: List[Dict]) -> Dict:
    """
    Calculate match rate and requirements retention metrics

    Args:
        results: List of test results

    Returns:
        Dictionary with calculated metrics
    """
    total_specs = len(results)
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    # Match rate: percentage of specs that generated output
    match_rate = (len(successful) / total_specs * 100) if total_specs > 0 else 0

    # Requirements retention: total requirements preserved
    total_requirements = sum(r["num_requirements"] for r in successful)

    # Average processing time
    avg_time = sum(r["elapsed_time"] for r in results) / len(results) if results else 0

    # Timing breakdown
    timing_stats = {}
    if successful:
        stages = ["stage_a", "stage_b", "stage_c", "stage_d", "stage_e_merge", "stage_e_build", "total"]
        for stage in stages:
            times = [r["timing"].get(stage, 0) for r in successful if stage in r["timing"]]
            if times:
                timing_stats[stage] = {
                    "mean": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times)
                }

    return {
        "total_specifications": total_specs,
        "successful": len(successful),
        "failed": len(failed),
        "match_rate": match_rate,
        "total_requirements": total_requirements,
        "avg_processing_time": avg_time,
        "timing_stats": timing_stats,
        "failed_spec_ids": [r["spec_id"] for r in failed]
    }


async def run_large_scale_test(json_path: str, limit: int = None, output_dir: str = None) -> Dict:
    """
    Run large-scale test on all specifications

    Args:
        json_path: Path to natural language JSON
        limit: Optional limit on number of specs to test
        output_dir: Optional output directory for results

    Returns:
        Dictionary with complete test results and metrics
    """
    print(f"\n{'='*70}")
    print("Large-Scale Test: Natural Language JSON Input")
    print(f"{'='*70}\n")

    # Load specifications
    print(f"Loading specifications from: {json_path}")
    specs = load_natural_language_specs(json_path)

    if limit:
        specs = specs[:limit]
        print(f"Testing first {limit} specifications (limited mode)")
    else:
        print(f"Testing all {len(specs)} specifications")

    print(f"\nStarting test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run tests
    start_time = time.perf_counter()
    results = []

    for i, spec in enumerate(specs, 1):
        result = await test_single_specification(spec, i, len(specs))
        results.append(result)

        # Small delay to avoid overwhelming the API
        await asyncio.sleep(0.5)

    total_time = time.perf_counter() - start_time

    # Calculate metrics
    print(f"\n{'='*70}")
    print("Calculating metrics...")
    metrics = calculate_metrics(results)

    # Print summary
    print(f"\n{'='*70}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*70}\n")
    print(f"Total Specifications: {metrics['total_specifications']}")
    print(f"Successful: {metrics['successful']}")
    print(f"Failed: {metrics['failed']}")
    print(f"\nMatch Rate: {metrics['match_rate']:.1f}% ({metrics['successful']}/{metrics['total_specifications']})")
    print(f"Total Requirements: {metrics['total_requirements']}")
    print(f"Avg Processing Time: {metrics['avg_processing_time']:.2f}s")
    print(f"Total Test Time: {total_time:.2f}s ({total_time/60:.1f} min)")

    if metrics['failed'] > 0:
        print(f"\nFailed Spec IDs: {', '.join(metrics['failed_spec_ids'])}")

    # Target comparison
    print(f"\n{'='*70}")
    print("TARGET COMPARISON")
    print(f"{'='*70}\n")
    print(f"Match Rate Target: 85%+")
    print(f"Match Rate Actual: {metrics['match_rate']:.1f}%")
    match_status = "[OK]" if metrics['match_rate'] >= 85 else "[BELOW TARGET]"
    print(f"Status: {match_status}")

    # Save results if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        run_file = output_path / f"run_{timestamp}.json"
        with open(run_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "input_file": json_path,
                "total_time": total_time,
                "results": results
            }, f, indent=2, ensure_ascii=False)

        # Save summary
        summary_file = output_path / f"summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "input_file": json_path,
                "total_time": total_time,
                "metrics": metrics
            }, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_dir}")
        print(f"- {run_file.name}")
        print(f"- {summary_file.name}")

    print(f"\n{'='*70}\n")

    return {
        "metrics": metrics,
        "results": results,
        "total_time": total_time
    }


async def main():
    parser = argparse.ArgumentParser(description="Large-scale test using natural language JSON")
    parser.add_argument(
        "--json",
        default="experimental_results/large_scale_test/ids_input_natural_language.json",
        help="Path to natural language JSON file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of specifications to test (for quick validation)"
    )
    parser.add_argument(
        "--output",
        default="experimental_results/large_scale_test/natural_language_test_results",
        help="Output directory for results"
    )

    args = parser.parse_args()

    await run_large_scale_test(args.json, args.limit, args.output)


if __name__ == "__main__":
    asyncio.run(main())
