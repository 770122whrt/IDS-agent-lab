# Phase 2: 修复测试脚本使用自然语言输入

**Phase:** 02-fix-test-scripts-1-2  
**Estimated Time:** 1-2 hours  
**Status:** Ready to execute

---

## Goal

Modify test scripts to use the natural language JSON generated in Phase 1, replacing the simplified text extraction that caused 85% information loss. Verify that the pipeline can process complete IDS information and achieve target metrics (85%+ match rate, 70%+ requirements retention).

---

## Success Criteria

1. ✅ `batch_experiment.py` loads from `ids_input_natural_language.json`
2. ✅ New `test_large_scale_natural_language.py` script created and functional
3. ✅ Test runs successfully on all 45 specifications without errors
4. ✅ Results saved to new directory `natural_language_test_results/`
5. ✅ Match rate and requirements retention calculated and reported
6. ✅ No regression in existing test scripts (old scripts still work)

---

## Context

**Input:** Phase 1 delivered `ids_input_natural_language.json` (36KB, 45 specs) with complete IDS information in natural language format.

**Problem:** Current test scripts extract only name+description from IDS XML, losing 85% of structural information (entity types, requirements, cardinality, IFC version).

**Expected Impact:** Match rate 53.3% → 85%+, Requirements retention 3.8% → 70%+

---

## Implementation Plan

### Step 1: Create New Large-Scale Test Script (30 min)

**File:** `ids-algo/test_large_scale_natural_language.py`

**Actions:**
1. Create new test script that loads `ids_input_natural_language.json`
2. Iterate through all 45 specifications
3. Run each through the IDS pipeline
4. Collect results (success/failure, generated IDS)
5. Calculate match rate and requirements retention
6. Save results to `experimental_results/large_scale_test/natural_language_test_results/`

**Key Functions:**
```python
def load_natural_language_specs(json_path: str) -> List[Dict]
async def test_single_specification(spec: Dict) -> Dict
async def run_large_scale_test() -> Dict
def calculate_metrics(results: List[Dict]) -> Dict
```

**Output:**
- `natural_language_test_results/run_{timestamp}.json` - Detailed results
- `natural_language_test_results/summary_{timestamp}.json` - Metrics summary
- Console output with match rate and requirements retention

---

### Step 2: Modify batch_experiment.py (20 min)

**File:** `ids-algo/batch_experiment.py`

**Actions:**
1. Backup original: `cp batch_experiment.py batch_experiment_old.py`
2. Add function to load from JSON: `load_specs_from_json()`
3. Modify `run_batch_experiment()` to accept JSON path parameter
4. Update main() to use JSON input when provided
5. Keep backward compatibility (can still generate text on-the-fly if needed)

**Changes:**
```python
# Add new function
def load_specs_from_json(json_path: str) -> List[Dict]:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Modify main
async def main():
    # Option 1: Use natural language JSON (new)
    if args.use_json:
        specs = load_specs_from_json(args.json_path)
        for spec in specs:
            await run_single_experiment(spec['id'], spec['text'], ...)
    
    # Option 2: Generate text from IDS (old, keep for compatibility)
    else:
        # ... existing code
```

---

### Step 3: Run Initial Test (10 min)

**Actions:**
1. Run new test script on first 3 specifications (quick validation)
2. Verify pipeline accepts natural language input
3. Check output format is correct
4. Verify no errors in pipeline stages

**Command:**
```bash
cd ids-algo
python test_large_scale_natural_language.py --limit 3
```

**Expected Output:**
```
Testing 3 specifications...
[1/3] Spec 1: Project - SUCCESS
[2/3] Spec 2: Spatial Structure - SUCCESS
[3/3] Spec 3: Bridge Parts - SUCCESS

Quick Test Results:
- Success Rate: 100% (3/3)
- Average Processing Time: 2.5s
```

---

### Step 4: Run Full Large-Scale Test (20 min)

**Actions:**
1. Run test on all 45 specifications
2. Monitor for errors or failures
3. Collect complete results
4. Calculate final metrics

**Command:**
```bash
cd ids-algo
python test_large_scale_natural_language.py
```

**Expected Output:**
```
Testing 45 specifications...
[Progress bar or counter]

Final Results:
- Match Rate: 87.2% (39/45) ✅ Target: 85%+
- Requirements Retention: 72.5% (57/79) ✅ Target: 70%+
- Average Processing Time: 3.2s
- Total Time: 2m 24s

Results saved to: experimental_results/large_scale_test/natural_language_test_results/
```

---

### Step 5: Verify Results (10 min)

**Actions:**
1. Check output files exist and are valid JSON
2. Verify all 45 specifications were processed
3. Compare metrics against baseline (53.3% → 85%+, 3.8% → 70%+)
4. Spot-check 3-5 generated IDS files for correctness

**Validation:**
```bash
# Check output files
ls -lh experimental_results/large_scale_test/natural_language_test_results/

# Verify JSON format
python -m json.tool natural_language_test_results/summary_*.json

# Count specifications processed
jq '.results | length' natural_language_test_results/run_*.json
```

---

### Step 6: Update Documentation (10 min)

**Actions:**
1. Create `02-PROGRESS.md` documenting completion
2. Update `.planning/STATE.md` marking Phase 2 complete
3. Create `02-SUMMARY.md` with metrics comparison

**Key Metrics to Document:**
- Baseline: 53.3% match rate, 3.8% requirements retention
- Phase 2: X% match rate, Y% requirements retention
- Improvement: +ΔX% match rate, +ΔY% requirements retention
- Processing time per specification
- Total test execution time

---

## Dependencies

**Required Files:**
- `ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json` (from Phase 1)
- `ids-algo/pipeline.py` (existing)
- `ids-algo/batch_experiment.py` (existing)

**Required Packages:**
- All existing dependencies (no new packages needed)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pipeline rejects natural language input | High | Test with 3 specs first, adjust format if needed |
| Match rate doesn't reach 85% | Medium | Analyze failures, may need Phase 2.5 to improve LLM prompts |
| Test takes too long (>10 min) | Low | Run in background, add progress reporting |
| Results format incompatible with compare_ids.py | Medium | Verify output format matches expected structure |

---

## Rollback Plan

If Phase 2 fails or results are worse than baseline:
1. Keep `batch_experiment_old.py` as backup
2. Document failure reasons in `02-PROGRESS.md`
3. Revert to Phase 1 and adjust LLM prompts
4. Re-run natural language generation with improved prompts

---

## Next Phase

**Phase 3:** Analyze results and identify failure patterns (if match rate < 85%)  
**Phase 7:** Generate comprehensive comparison report (if match rate ≥ 85%)

---

*Created: 2026-04-23*  
*Estimated: 1-2 hours*  
*Dependencies: Phase 1 complete*
