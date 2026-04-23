# Phase 2 Planning Summary

**Phase:** 02-fix-test-scripts-1-2  
**Status:** Planning Complete, Ready to Execute  
**Created:** 2026-04-23  
**Estimated Time:** 1-2 hours

---

## Overview

Phase 2 focuses on modifying test scripts to use the natural language JSON generated in Phase 1, replacing the simplified text extraction that caused 85% information loss.

---

## Deliverables

### Primary Deliverables
1. **test_large_scale_natural_language.py** - New test script for 45 specifications
2. **Modified batch_experiment.py** - Support for JSON input
3. **Test Results** - Saved to `natural_language_test_results/`
4. **Metrics Report** - Match rate and requirements retention

### Documentation
1. **02-CONTEXT.md** - Implementation context and decisions
2. **02-PLAN.md** - Detailed 6-step execution plan
3. **02-PROGRESS.md** - Execution progress (to be created during execution)
4. **02-SUMMARY.md** - This file

---

## Expected Outcomes

### Baseline (Before Phase 2)
- Match Rate: 53.3% (24/45 specifications)
- Requirements Retention: 3.8% (3/79 requirements)
- Information Loss: 85% (only name+description preserved)

### Target (After Phase 2)
- Match Rate: **85%+** (38+/45 specifications)
- Requirements Retention: **70%+** (55+/79 requirements)
- Information Loss: **0%** (complete IDS information preserved)

### Improvement
- Match Rate: **+31.7%** absolute improvement
- Requirements Retention: **+66.2%** absolute improvement

---

## Implementation Steps

1. **Create test_large_scale_natural_language.py** (30 min)
   - Load `ids_input_natural_language.json`
   - Run all 45 specifications through pipeline
   - Calculate metrics and save results

2. **Modify batch_experiment.py** (20 min)
   - Add JSON loading function
   - Support both JSON and on-the-fly generation
   - Maintain backward compatibility

3. **Run Initial Test** (10 min)
   - Test first 3 specifications
   - Verify pipeline accepts input
   - Check for errors

4. **Run Full Test** (20 min)
   - Process all 45 specifications
   - Collect complete results
   - Calculate final metrics

5. **Verify Results** (10 min)
   - Validate output files
   - Compare against baseline
   - Spot-check generated IDS

6. **Update Documentation** (10 min)
   - Create PROGRESS.md
   - Update STATE.md
   - Document metrics

---

## Key Files

### Input (from Phase 1)
- `ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json`

### Scripts to Modify
- `ids-algo/batch_experiment.py`
- `ids-algo/test_large_scale_natural_language.py` (new)

### Output
- `experimental_results/large_scale_test/natural_language_test_results/run_*.json`
- `experimental_results/large_scale_test/natural_language_test_results/summary_*.json`

---

## Success Criteria

- [x] Planning documents created (CONTEXT, PLAN, SUMMARY)
- [ ] test_large_scale_natural_language.py created and functional
- [ ] batch_experiment.py modified with JSON support
- [ ] All 45 specifications processed successfully
- [ ] Match rate ≥ 85%
- [ ] Requirements retention ≥ 70%
- [ ] Results saved and documented

---

## Next Steps

1. Execute Phase 2 plan using `/gsd-execute-phase 2`
2. Monitor execution and handle any issues
3. Verify metrics meet targets
4. If successful, proceed to Phase 7 (comparison report)
5. If unsuccessful, analyze failures and adjust approach

---

## Dependencies

**Completed:**
- ✅ Phase 1: Natural language JSON generated

**Required:**
- Pipeline.py functional
- Anthropic API access
- Python environment configured

**Blocked By:**
- None

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Pipeline rejects input | Low | High | Test with 3 specs first |
| Match rate < 85% | Medium | Medium | Analyze failures, adjust prompts |
| Long execution time | Low | Low | Run in background |
| Format incompatibility | Low | Medium | Verify output structure |

---

*Planning completed: 2026-04-23*  
*Ready for execution*
