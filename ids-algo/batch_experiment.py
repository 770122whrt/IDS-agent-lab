"""
Batch Experiment Script for IDS Pipeline Performance Evaluation

This script runs multiple test samples through the IDS pipeline,
collects timing and performance data, and generates statistical reports
for thesis Chapter 5.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

# Import the pipeline
from pipeline import run_ids_pipeline


def load_experiment_config(config_path: str) -> Dict:
    """Load experiment configuration from JSON file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def run_single_experiment(sample_id: str, text: str, iteration: int, complexity: str) -> Dict:
    """
    Run a single experiment for one sample

    Args:
        sample_id: Unique identifier for the sample
        text: Input text requirement
        iteration: Iteration number (1, 2, 3, ...)
        complexity: Complexity level (simple, medium, complex)

    Returns:
        Dictionary containing experiment results
    """
    start_time = datetime.now()

    # Determine if this is a representative sample (record full stage outputs)
    representative_samples = ["simple_001", "medium_003", "complex_001"]
    return_stage_outputs = sample_id in representative_samples

    try:
        # Run pipeline with timing and optional stage outputs
        result, timing, stage_outputs = await run_ids_pipeline(
            text,
            return_timing=True,
            return_stage_outputs=return_stage_outputs
        )

        # Extract specifications count
        num_specs = len(result.get("specifications", [])) if result else 0

        experiment_result = {
            "sample_id": sample_id,
            "complexity": complexity,
            "iteration": iteration,
            "timestamp": start_time.isoformat(),
            "success": True,
            "timing": timing,
            "num_specifications": num_specs,
            "output": result,
            "error": None
        }

        # Always include Stage C mappings (for accuracy evaluation)
        if "stage_c_mappings" in stage_outputs:
            experiment_result["stage_c_mappings"] = stage_outputs["stage_c_mappings"]

        # Include full stage outputs for representative samples
        if return_stage_outputs:
            experiment_result["full_stage_outputs"] = {
                k: v for k, v in stage_outputs.items() if k != "stage_c_mappings"
            }

        return experiment_result

    except Exception as e:
        return {
            "sample_id": sample_id,
            "complexity": complexity,
            "iteration": iteration,
            "timestamp": start_time.isoformat(),
            "success": False,
            "timing": {},
            "num_specifications": 0,
            "output": None,
            "stage_c_mappings": [],
            "error": str(e)
        }


def save_run_result(result: Dict, output_dir: str):
    """Save individual run result to JSON file"""
    runs_dir = Path(output_dir) / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"run_{timestamp}_{result['sample_id']}_iter{result['iteration']}.json"
    filepath = runs_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


async def run_batch_experiment(config: Dict, num_iterations: int = 3, output_dir: str = "experimental_results") -> List[Dict]:
    """
    Run batch experiment for all test samples

    Args:
        config: Experiment configuration
        num_iterations: Number of iterations per sample
        output_dir: Output directory for results

    Returns:
        List of all experiment results
    """
    all_results = []
    test_samples = config["test_samples"]

    print(f"\n{'='*60}")
    print(f"Batch Experiment: {config['experiment_name']}")
    print(f"Total samples: {len(test_samples)}")
    print(f"Iterations per sample: {num_iterations}")
    print(f"Total runs: {len(test_samples) * num_iterations}")
    print(f"{'='*60}\n")

    for idx, sample in enumerate(test_samples, 1):
        sample_id = sample["id"]
        text = sample["text"]
        complexity = sample.get("complexity", "unknown")

        print(f"\n[{idx}/{len(test_samples)}] Sample: {sample_id} (complexity: {complexity})")
        print(f"[TEXT] {text[:80]}...")

        for i in range(1, num_iterations + 1):
            print(f"  [RUN {i}/{num_iterations}] ", end="", flush=True)

            result = await run_single_experiment(sample_id, text, i, complexity)
            all_results.append(result)

            if result["success"]:
                total_time = result["timing"].get("total", 0)
                print(f"OK - {total_time:.2f}s")
            else:
                print(f"FAILED - {result['error'][:50]}...")

            # Save individual run result
            save_run_result(result, output_dir)

            # Small delay between runs to avoid overwhelming the API
            await asyncio.sleep(0.5)

    return all_results


def calculate_statistics(results: List[Dict]) -> Dict:
    """
    Calculate summary statistics from experiment results

    Returns:
        Dictionary containing aggregated statistics
    """
    # Filter successful runs
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    if not successful:
        return {
            "metadata": {
                "total_samples": len(set(r["sample_id"] for r in results)),
                "total_runs": len(results),
                "successful_runs": 0,
                "failed_runs": len(failed),
                "timestamp": datetime.now().isoformat()
            },
            "success_rate": {"overall": 0.0},
            "error": "No successful runs to analyze"
        }

    # Calculate timing statistics for each stage
    stages = ["stage_a", "stage_b", "stage_c", "stage_d", "stage_e_merge", "stage_e_build", "total"]
    timing_stats = {}

    for stage in stages:
        times = [r["timing"][stage] for r in successful if stage in r["timing"]]
        if times:
            timing_stats[stage] = {
                "mean": float(np.mean(times)),
                "std": float(np.std(times)),
                "min": float(np.min(times)),
                "max": float(np.max(times))
            }

    # Calculate stage percentages
    stage_percentage = {}
    if "total" in timing_stats and timing_stats["total"]["mean"] > 0:
        total_mean = timing_stats["total"]["mean"]
        for stage in ["stage_a", "stage_b", "stage_c", "stage_d", "stage_e_merge", "stage_e_build"]:
            if stage in timing_stats:
                stage_percentage[stage] = (timing_stats[stage]["mean"] / total_mean) * 100

    # Calculate success rate by complexity
    success_by_complexity = {}
    for complexity in ["simple", "medium", "complex"]:
        complexity_results = [r for r in results if r.get("complexity") == complexity]
        if complexity_results:
            complexity_success = [r for r in complexity_results if r["success"]]
            success_by_complexity[complexity] = (len(complexity_success) / len(complexity_results)) * 100

    # Get failed sample IDs
    failed_samples = [f"{r['sample_id']}_run{r['iteration']}" for r in failed]

    # Analyze Stage C mapping results
    mapping_analysis = analyze_stage_c_mappings(successful)

    return {
        "metadata": {
            "experiment_name": "IDS Pipeline Performance Evaluation",
            "total_samples": len(set(r["sample_id"] for r in results)),
            "total_runs": len(results),
            "successful_runs": len(successful),
            "failed_runs": len(failed),
            "num_iterations": len(results) // len(set(r["sample_id"] for r in results)),
            "timestamp": datetime.now().isoformat()
        },
        "success_rate": {
            "overall": (len(successful) / len(results)) * 100,
            "by_complexity": success_by_complexity,
            "failed_samples": failed_samples
        },
        "timing_statistics": timing_stats,
        "stage_percentage": stage_percentage,
        "mapping_analysis": mapping_analysis
    }


def analyze_stage_c_mappings(successful_results: List[Dict]) -> Dict:
    """
    Analyze Stage C mapping results for accuracy evaluation

    Returns:
        Dictionary containing mapping statistics
    """
    all_mappings = []

    for result in successful_results:
        if "stage_c_mappings" not in result:
            continue

        sample_id = result["sample_id"]
        mappings = result["stage_c_mappings"]

        for mapping in mappings:
            mapping_record = {
                "sample_id": sample_id,
                "original_text": mapping.get("original_text", ""),
                "facet_type": mapping.get("facet_type", "")
            }

            # Entity mapping
            if "entity" in mapping:
                mapping_record["entity_mapped"] = mapping["entity"].get("mapped_value", "")
                mapping_record["entity_confidence"] = mapping["entity"].get("confidence", 0.0)
                mapping_record["entity_source"] = mapping["entity"].get("source", "")

            # Property mapping
            if "property" in mapping:
                mapping_record["property_mapped"] = mapping["property"].get("mapped_value", "")
                mapping_record["property_confidence"] = mapping["property"].get("confidence", 0.0)
                mapping_record["property_source"] = mapping["property"].get("source", "")

            # Material mapping
            if "material" in mapping:
                mapping_record["material_mapped"] = mapping["material"].get("mapped_value", "")
                mapping_record["material_confidence"] = mapping["material"].get("confidence", 0.0)
                mapping_record["material_source"] = mapping["material"].get("source", "")

            all_mappings.append(mapping_record)

    # Calculate average confidence scores
    entity_confidences = [m["entity_confidence"] for m in all_mappings if "entity_confidence" in m]
    property_confidences = [m["property_confidence"] for m in all_mappings if "property_confidence" in m]
    material_confidences = [m["material_confidence"] for m in all_mappings if "material_confidence" in m]

    return {
        "total_mappings": len(all_mappings),
        "entity_mappings": len(entity_confidences),
        "property_mappings": len(property_confidences),
        "material_mappings": len(material_confidences),
        "average_confidence": {
            "entity": float(np.mean(entity_confidences)) if entity_confidences else 0.0,
            "property": float(np.mean(property_confidences)) if property_confidences else 0.0,
            "material": float(np.mean(material_confidences)) if material_confidences else 0.0
        },
        "detailed_mappings": all_mappings
    }


def export_to_csv(statistics: Dict, output_path: str):
    """Export statistics to CSV format for Excel"""
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write timing statistics
        writer.writerow(["Stage", "Mean (s)", "Std (s)", "Min (s)", "Max (s)", "Percentage (%)"])

        stage_names = {
            "stage_a": "Stage A - Structured Parser",
            "stage_b": "Stage B - Facet Classifier",
            "stage_c": "Stage C - KB Mapping",
            "stage_d": "Stage D - Constraint Extraction",
            "stage_e_merge": "Stage E-1 - Merge Logic",
            "stage_e_build": "Stage E-2 - IDS Builder",
            "total": "Total"
        }

        timing_stats = statistics.get("timing_statistics", {})
        stage_percentage = statistics.get("stage_percentage", {})

        for stage_key, stage_name in stage_names.items():
            if stage_key in timing_stats:
                stats = timing_stats[stage_key]
                percentage = stage_percentage.get(stage_key, 100.0 if stage_key == "total" else 0.0)
                writer.writerow([
                    stage_name,
                    f"{stats['mean']:.2f}",
                    f"{stats['std']:.2f}",
                    f"{stats['min']:.2f}",
                    f"{stats['max']:.2f}",
                    f"{percentage:.1f}"
                ])

        # Write success rate
        writer.writerow([])
        writer.writerow(["Success Rate Statistics"])
        writer.writerow(["Category", "Success Rate (%)"])

        success_rate = statistics.get("success_rate", {})
        writer.writerow(["Overall", f"{success_rate.get('overall', 0):.2f}"])

        by_complexity = success_rate.get("by_complexity", {})
        for complexity, rate in by_complexity.items():
            writer.writerow([f"{complexity.capitalize()}", f"{rate:.2f}"])


async def main():
    """Main function to run batch experiment"""
    # Configuration
    config_path = "experiment_config.json"
    output_dir = "experimental_results"
    num_iterations = 3

    # Load configuration
    print("Loading experiment configuration...")
    config = load_experiment_config(config_path)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/runs", exist_ok=True)

    # Run batch experiment
    experiment_start = time.time()
    results = await run_batch_experiment(config, num_iterations, output_dir)
    experiment_duration = time.time() - experiment_start

    # Calculate statistics
    print("\n" + "="*60)
    print("Calculating statistics...")
    statistics = calculate_statistics(results)
    statistics["metadata"]["duration_minutes"] = experiment_duration / 60

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_json_path = f"{output_dir}/summary_{timestamp}.json"
    summary_csv_path = f"{output_dir}/summary_{timestamp}.csv"

    with open(summary_json_path, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)

    export_to_csv(statistics, summary_csv_path)

    # Print summary
    print("="*60)
    print("Batch Experiment Completed")
    print("="*60)
    print(f"Duration: {experiment_duration/60:.1f} minutes")
    print(f"Total runs: {statistics['metadata']['total_runs']}")
    print(f"Successful: {statistics['metadata']['successful_runs']}")
    print(f"Failed: {statistics['metadata']['failed_runs']}")
    print(f"Success rate: {statistics['success_rate']['overall']:.1f}%")

    if "timing_statistics" in statistics and "total" in statistics["timing_statistics"]:
        total_stats = statistics["timing_statistics"]["total"]
        print(f"\nAverage response time: {total_stats['mean']:.2f}s")
        print(f"Min response time: {total_stats['min']:.2f}s")
        print(f"Max response time: {total_stats['max']:.2f}s")
        print(f"Std deviation: {total_stats['std']:.2f}s")

    print(f"\nResults saved to:")
    print(f"  - JSON: {summary_json_path}")
    print(f"  - CSV:  {summary_csv_path}")
    print(f"  - Runs: {output_dir}/runs/ ({len(results)} files)")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
