# Phase 2: 修复测试脚本 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning
**Source:** Phase 1 completion analysis and codebase review

<domain>
## Phase Boundary

Phase 2 focuses on modifying test scripts to use the natural language JSON generated in Phase 1 instead of the simplified text extraction that caused 85% information loss.

**What Phase 1 Delivered:**
- `ids_input_text_full.txt` - Structured text (31KB, 45 specs)
- `ids_input_natural_language.json` - Natural language JSON (36KB, 45 specs)
- Both files preserve complete IDS information (entity, requirements, cardinality, IFC version)

**What Phase 2 Must Do:**
1. Modify `batch_experiment.py` to load from JSON instead of generating text on-the-fly
2. Create a new large-scale test script that uses the natural language JSON
3. Ensure all test scripts use consistent input format
4. Verify the pipeline can process the natural language input correctly

**Current Problem:**
- Previous tests extracted only name+description from IDS XML
- Lost 85% of structural information
- Match rate: 53.3%, Requirements retention: 3.8%

**Expected Improvement:**
- Match rate: 85%+ (from 53.3%)
- Requirements retention: 70%+ (from 3.8%)

</domain>

<decisions>
## Implementation Decisions

### Test Script Architecture
- **LOCKED**: Use `ids_input_natural_language.json` as the single source of truth for all tests
- **LOCKED**: Do not regenerate text from IDS XML in test scripts
- **LOCKED**: Load JSON once at startup, iterate through specifications
- **LOCKED**: Maintain existing test structure (batch_experiment.py framework)

### Input Format
- **LOCKED**: JSON format with array of objects: `[{"id": "1", "text": "...", "language": "en"}]`
- **LOCKED**: Each specification is a separate entry in the array
- **LOCKED**: Text field contains complete natural language description
- **LOCKED**: Language field is always "en" for this project

### Test Scripts to Modify
- **LOCKED**: `batch_experiment.py` - Main batch testing framework
- **LOCKED**: Create new `test_large_scale_natural_language.py` - Dedicated large-scale test
- **LOCKED**: Keep `compare_ids.py` unchanged - it compares outputs, not inputs

### Backward Compatibility
- **LOCKED**: Keep old test scripts as backup (rename with _old suffix)
- **LOCKED**: Do not delete existing experimental results
- **LOCKED**: New results go to separate directory to avoid confusion

### Claude's Discretion
- Exact variable names and function signatures
- Error handling details
- Progress reporting format
- Whether to add additional validation checks

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Input Files (Phase 1 Output)
- `ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json` — Natural language JSON (45 specs)
- `ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt` — Structured text (reference only)

### Test Scripts to Modify
- `ids-algo/batch_experiment.py` — Current batch testing framework
- `ids-algo/pipeline.py` — Pipeline entry point (verify it accepts text input)

### Reference Data
- `ids-algo/temp/input.json` — Example input format
- `ids-algo/experimental_results/LARGE_SCALE_TEST_DETAILED_REPORT.md` — Baseline metrics (53.3% match rate)

### Phase 1 Documentation
- `.planning/phases/01-idstotextgenerator-2-3/PROGRESS.md` — Phase 1 summary
- `.planning/phases/01-idstotextgenerator-2-3/01-CONTEXT.md` — Phase 1 context

</canonical_refs>

<specifics>
## Specific Ideas

### Modified batch_experiment.py Structure
```python
def load_natural_language_specs(json_path: str) -> List[Dict]:
    """Load specifications from natural language JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def run_batch_experiment_from_json(json_path: str, num_iterations: int = 3):
    """Run batch experiment using pre-generated natural language JSON"""
    specs = load_natural_language_specs(json_path)
    
    for spec in specs:
        spec_id = spec['id']
        text = spec['text']
        
        for i in range(1, num_iterations + 1):
            result = await run_single_experiment(spec_id, text, i, "bridge")
            # ... save results
```

### New test_large_scale_natural_language.py
```python
async def test_large_scale_with_natural_language():
    """Test all 45 specifications using natural language JSON"""
    json_path = "experimental_results/large_scale_test/ids_input_natural_language.json"
    specs = load_specs(json_path)
    
    results = []
    for spec in specs:
        result = await run_ids_pipeline(spec['text'])
        results.append({
            'spec_id': spec['id'],
            'success': result is not None,
            'output': result
        })
    
    # Calculate match rate and requirements retention
    match_rate = calculate_match_rate(results)
    req_retention = calculate_requirements_retention(results)
    
    print(f"Match Rate: {match_rate:.1f}%")
    print(f"Requirements Retention: {req_retention:.1f}%")
```

### Expected Output Structure
```
experimental_results/
├── large_scale_test/
│   ├── ids_input_natural_language.json  (input)
│   ├── natural_language_test_results/   (new)
│   │   ├── run_20260423_*.json
│   │   └── summary_20260423.json
```

</specifics>

<deferred>
## Deferred Ideas

- Running tests with different LLM models (use current model only)
- Parallel test execution (run sequentially for now)
- Automated comparison with baseline (manual comparison in Phase 7)
- Test result visualization (focus on data collection first)
- Integration with CI/CD (out of scope for this project)

</deferred>

---

*Phase: 02-fix-test-scripts-1-2*
*Context gathered: 2026-04-23*
