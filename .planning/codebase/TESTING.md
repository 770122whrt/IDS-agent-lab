# Testing Practices

This document describes the testing approach, patterns, and infrastructure used in the IDS Agent project.

## Test Framework

### No Formal Test Framework

The project **does not use a formal testing framework** like pytest or unittest. Instead, it uses:

- **Manual test scripts** in the `tests/` directory
- **Pipeline integration tests** at the root level
- **Experimental batch testing** for performance evaluation

### Test Execution

Tests are run directly as Python scripts:

```bash
# Run individual stage tests
python -m tests.a
python -m tests.b
python -m tests.c

# Run pipeline test
python test_pipeline.py

# Run batch experiments
python batch_experiment.py
```

## Test Directory Structure

```
ids-algo/
├── tests/                          # Stage-by-stage test scripts
│   ├── a.py                       # Test structured parser (Stage A)
│   ├── b.py                       # Test facet classifier (Stage B)
│   ├── c.py                       # Test knowledge mapping (Stage C)
│   ├── d.py                       # Test constraint extraction (Stage D)
│   ├── e.py                       # Test IDS builder (Stage E)
│   └── utils.py                   # Test utilities
├── test_pipeline.py               # End-to-end pipeline test
├── pipeline_test.py               # Pipeline test with timing
├── batch_experiment.py            # Batch experiment runner
└── temp/                          # Test data directory
    └── input.json                 # Test input data
```

## Test Patterns

### Stage-by-Stage Testing

Each pipeline stage has a dedicated test script that:
1. Loads input from previous stage
2. Processes the data
3. Saves output for next stage

**Pattern Example (tests/a.py):**

```python
import asyncio
from a_structured_parser import runStructuredParser
from .utils import load_input_entries, createJsonTempFile

async def main() -> None:
    try:
        entries = load_input_entries("input.json")
        for entry in entries:
            text = str(entry.get("text", "")).strip()
            entry_id = str(entry.get("id", "")).strip()
            print(f"▶️ Processing entry {entry_id}")
            result = await runStructuredParser(text)
            createJsonTempFile(result, f"a{entry_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

### File-Based Test Data Flow

Tests use a file-based approach for data passing:

1. **Input**: `temp/input.json` - Contains test requirements
2. **Stage A Output**: `temp/a{id}.json` - Structured parse results
3. **Stage B Output**: `temp/b{id}.json` - Facet classification results
4. **Stage C Output**: `temp/c{id}.json` - Knowledge mapping results
5. **Stage D Output**: `temp/d{id}.json` - Constraint extraction results
6. **Stage E Output**: `temp/e{id}.json` - Final IDS specifications

### Test Data Format

**Input Format (temp/input.json):**

```json
[
  {
    "id": "1",
    "text": "All IfcWall elements must have a FireRating property..."
  },
  {
    "id": "2",
    "text": "The Height property of IfcDoor should be between 2000mm..."
  }
]
```

### Integration Testing

**End-to-End Pipeline Test (test_pipeline.py):**

```python
import asyncio
from pipeline import run_ids_pipeline

TEST_REQUIREMENT = """
All IfcWall elements must have a FireRating property with a value 
greater than 120 minutes.
"""

async def main():
    print("=" * 60)
    print("IDS Pipeline Test with Anthropic Endpoint")
    print("=" * 60)
    
    try:
        result = await run_ids_pipeline(TEST_REQUIREMENT)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n[PASS] Pipeline test completed successfully!")
        return True
    except Exception as e:
        print(f"\n[FAIL] Pipeline test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
```

## Test Utilities

### Test Helper Functions (tests/utils.py)

**File I/O Utilities:**

```python
def createJsonTempFile(obj: object, filename: str):
    """Save test results to temp directory"""
    content = to_json(obj, indent=2)
    output_dir = Path(__file__).parent.parent / "temp"
    output_dir.mkdir(exist_ok=True)
    finalfilename = f"{filename}.json"
    output_path = output_dir / finalfilename
    output_path.write_text(content, encoding="utf-8")
    print(f"✅ Json temp file saved to: {output_path}")

def load_input_entries(filename: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load test inputs from temp directory"""
    target = BASE_DIR / "temp" / filename if filename else DEFAULT_INPUT_FILE
    raw_content = target.read_text(encoding="utf-8")
    data = json.loads(raw_content)
    if not isinstance(data, list):
        raise RuntimeError(f"Expected a list of entries in {target}.")
    return data
```

**JSON Serialization:**

```python
def to_jsonable(obj):
    """Recursively convert result classes to JSON-serializable dicts."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, list):
        return [to_jsonable(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        return {k: to_jsonable(v) for k, v in vars(obj).items()}
    return str(obj)

def to_json(obj, **kwargs):
    """Return a JSON string."""
    return json.dumps(to_jsonable(obj), ensure_ascii=False, **kwargs)
```

**Data Normalization:**

```python
def normalize_ifc_version(version_str: str) -> str:
    """Normalize IFC version string"""
    if not version_str:
        return ""
    return "".join(c for c in version_str if c.isalnum()).upper()
```

## Batch Experiment Testing

### Experimental Testing Framework

The project includes a sophisticated batch experiment system for performance evaluation:

**batch_experiment.py** provides:
- Multiple iterations per test sample
- Timing measurements for each stage
- Success/failure tracking
- Statistical analysis
- CSV export for results

### Experiment Configuration

**experiment_config.json:**

```json
{
  "samples": [
    {
      "id": "simple_wall",
      "text": "All walls must have FireRating property",
      "complexity": "simple"
    },
    {
      "id": "complex_multi",
      "text": "Complex requirement with multiple constraints...",
      "complexity": "complex"
    }
  ]
}
```

### Experiment Execution

```python
async def run_single_experiment(
    sample_id: str, 
    text: str, 
    iteration: int, 
    complexity: str
) -> Dict:
    """Run a single experiment iteration"""
    start_time = time.perf_counter()
    
    try:
        result, timing, stage_outputs = await run_ids_pipeline(
            text, 
            return_timing=True, 
            return_stage_outputs=True
        )
        
        return {
            "sample_id": sample_id,
            "iteration": iteration,
            "complexity": complexity,
            "success": True,
            "total_time": timing["total"],
            "stage_timings": timing,
            "stage_outputs": stage_outputs,
            # ...
        }
    except Exception as e:
        return {
            "sample_id": sample_id,
            "iteration": iteration,
            "success": False,
            "error": str(e),
            # ...
        }
```

### Statistical Analysis

The batch experiment system calculates:
- Success rates
- Average execution times per stage
- Standard deviations
- Min/max times
- Stage C mapping accuracy

```python
def calculate_statistics(results: List[Dict]) -> Dict:
    """Calculate comprehensive statistics from experiment results"""
    successful_results = [r for r in results if r.get("success")]
    
    stats = {
        "total_runs": len(results),
        "successful_runs": len(successful_results),
        "success_rate": len(successful_results) / len(results),
        "stage_timings": {
            "stage_a": {"mean": ..., "std": ..., "min": ..., "max": ...},
            # ...
        },
        "stage_c_accuracy": analyze_stage_c_mappings(successful_results),
    }
    return stats
```

## Test Data Management

### Input Data Location

- **Primary**: `ids-algo/temp/input.json`
- **Format**: JSON array of test cases with `id` and `text` fields
- **Persistence**: Test data persists between runs for reproducibility

### Intermediate Results

Each stage saves its output to `temp/` directory:
- Enables debugging of individual stages
- Allows re-running downstream stages without re-executing upstream
- Facilitates manual inspection of intermediate results

### Output Data

- **Stage outputs**: `temp/{stage}{id}.json`
- **Final IDS**: `temp/e{id}.json`
- **Experiment results**: `experimental_results/` directory
- **Markdown reports**: `output/` directory (when enabled)

## Test Coverage

### What is Tested

**Unit-Level (Stage Tests):**
- Stage A: Natural language parsing to structured components
- Stage B: Facet classification (entity, property, material, etc.)
- Stage C: Knowledge base mapping to IFC terminology
- Stage D: Constraint extraction from text
- Stage E: IDS specification building

**Integration-Level:**
- Full pipeline execution (test_pipeline.py)
- Data flow between stages (tests/e.py)
- Error handling and recovery

**Performance-Level:**
- Batch experiments with timing
- Multiple iterations for statistical significance
- Complexity-based analysis (simple vs complex requirements)

### What is NOT Tested

- **No unit tests** for individual functions/methods
- **No mocking** of external dependencies (LLM, vector DB)
- **No automated test discovery**
- **No test fixtures** in the traditional sense
- **No code coverage measurement**
- **No continuous integration tests**

## Debugging and Inspection

### Console Output

Tests use emoji-rich console output for visual feedback:

```python
print(f"▶️ Processing entry {entry_id}")
print(f"✅ Json temp file saved to: {output_path}")
print(f"❌ Error: {e}")
print(f"📌 [{facet.facet_type.upper()}] '{facet.original_text}'")
print(f"   🔁 Mapped To: {facet.mapped_name}")
print(f"   📊 Confidence: {facet.confidence}")
```

### Logging

Pipeline uses structured logging:

```python
logger.info("[Step A] Running Structured Parser...")
logger.info(f"   Generated {len(facets)} facets.")
logger.error(f"[ERROR] Pipeline failed: {e}")
```

### Traceback Printing

Full tracebacks printed on errors:

```python
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
```

## Test Execution Workflow

### Manual Stage-by-Stage Testing

1. Prepare test data in `temp/input.json`
2. Run Stage A: `python -m tests.a`
3. Inspect `temp/a*.json` output
4. Run Stage B: `python -m tests.b`
5. Continue through stages C, D, E
6. Inspect final output in `temp/e*.json`

### End-to-End Testing

1. Modify `TEST_REQUIREMENT` in `test_pipeline.py`
2. Run: `python test_pipeline.py`
3. Check exit code (0 = success, 1 = failure)
4. Review JSON output

### Batch Experiment Testing

1. Configure experiments in `experiment_config.json`
2. Run: `python batch_experiment.py`
3. Review results in `experimental_results/`
4. Analyze CSV statistics

## Test Data Reconstruction

### Constraint Reconstruction (tests/e.py)

Complex pattern for reconstructing typed objects from JSON:

```python
def reconstruct_constraint(d_dict: dict) -> ValueRestriction:
    """Reconstruct constraint object from JSON dict"""
    type_str = d_dict.get("restriction_type", "").upper()
    r_type = RestrictionType[type_str]
    r_data = d_dict.get("restriction", {})
    
    if r_type == RestrictionType.BOUNDS:
        restriction_obj = BoundsRestriction(
            min_value=r_data.get("min_value"),
            max_value=r_data.get("max_value"),
            # ...
        )
    # ... handle other types
    
    return ValueRestriction(
        restriction_type=r_type,
        restriction=restriction_obj,
        confidence=d_dict.get("confidence", 0.0),
        original_text=d_dict.get("original_text", "")
    )
```

### Data Merging Logic

Tests implement the core data merging logic:

```python
# Merge constraints into facets based on text matching
merged_count = 0
for facet in facets:
    if facet.constraints is None:
        facet.constraints = []
    
    facet_text = (facet.original_text or "").strip().lower()
    
    for constr in constraints:
        constr_text = (constr.original_text or "").strip().lower()
        if constr_text and facet_text and \
           (constr_text in facet_text or facet_text in constr_text):
            facet.constraints.append(constr)
            merged_count += 1
```

## Performance Testing

### Timing Measurements

Pipeline supports detailed timing:

```python
timing = {}
start_total = time.perf_counter()

start_a = time.perf_counter()
res_a = await runStructuredParser(text_content)
timing["stage_a"] = time.perf_counter() - start_a

# ... repeat for each stage

timing["total"] = time.perf_counter() - start_total
```

### Performance Metrics

Batch experiments track:
- Per-stage execution time
- Total pipeline time
- Success/failure rates
- Memory usage (via psutil)
- Mapping accuracy

## CI/CD Testing

### No Automated CI/CD

The project **does not have**:
- GitHub Actions workflows
- Automated test runs on commit/PR
- Pre-commit hooks for testing
- Automated deployment testing

### Manual Testing Process

Testing is performed manually:
1. Developer runs test scripts locally
2. Results inspected manually
3. Experiments run for performance validation
4. Changes committed after manual verification

## Test Maintenance

### Test Data Updates

- Test data in `temp/input.json` updated manually
- No test data versioning
- No test data generation tools

### Test Script Updates

- Test scripts updated alongside code changes
- No automated test generation
- Tests serve as usage examples and documentation

## Recommendations for Future Testing

While not currently implemented, the following would improve testing:

1. **Add pytest framework** for structured unit testing
2. **Implement test fixtures** for common test data
3. **Add mocking** for LLM and external services
4. **Create test coverage reports**
5. **Set up CI/CD pipeline** with automated tests
6. **Add integration test suite** with assertions
7. **Implement property-based testing** for data structures
8. **Add performance regression tests**
9. **Create test data generators** for edge cases
10. **Add validation tests** for IDS output correctness
