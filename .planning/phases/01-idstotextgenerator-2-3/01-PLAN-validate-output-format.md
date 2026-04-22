---
phase: 1
plan_id: validate-output-format
title: Validate Output Format for Pipeline Compatibility
estimated_duration: 30min
dependencies: [llm-natural-language-generation]
---

# Plan: Validate Output Format for Pipeline Compatibility

## Objective

Ensure the generated structured text format is compatible with the IDS pipeline stages (A→B→C→D→E) and can be successfully parsed.

## Context

- Generated file: `ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json`
- Pipeline stages need to parse this natural language input
- Reference format: `ids-algo/temp/input.json` examples

## Tasks

### 1. Analyze Pipeline Input Requirements
**Action:** Check how Stage A (Structured Parser) expects input:
- Read `ids-algo/a_structured_parser/entry.py`
- Understand what text format it can parse
- Check if it expects specific delimiters or structure

**Success:** Understand Stage A input requirements

### 2. Compare with temp Directory Format
**Action:** Compare generated output with `ids-algo/temp/input.json`:
- Check JSON structure matches (array of objects with id, text, language)
- Verify natural language style matches
- Verify all information is preserved in natural language
- Identify any format mismatches

**Success:** Know if format is compatible

### 3. Validate JSON Structure
**Action:** Verify JSON format is correct:
- Check it's valid JSON (can be parsed)
- Verify array structure with 45 objects
- Verify each object has: id, text, language fields
- Verify IDs are sequential (1-45)

**Success:** JSON structure is valid

### 4. Validate Natural Language Quality
**Action:** Manually inspect 3-5 sample specifications:
- Pick simple, medium, complex examples
- Verify natural language is clear and readable
- Verify all information from structured text is preserved
- Verify style matches temp/input.json examples
- Check entities, requirements, cardinality are expressed naturally

**Success:** Sample specifications are high quality natural language

### 5. Test Parse-ability (Quick Check)
**Action:** Try to parse the output programmatically:
```python
import json

# Quick test to see if format is parseable
with open('ids_input_natural_language.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Validate structure
print(f"Total specifications: {len(data)}")
print(f"Expected: 45")

# Check each entry
for entry in data[:3]:  # Check first 3
    assert 'id' in entry
    assert 'text' in entry
    assert 'language' in entry
    assert entry['language'] == 'en'
    print(f"ID {entry['id']}: {entry['text'][:100]}...")

print("✓ Format validation passed")
```

**Success:** Format is parseable and matches expected structure

## Acceptance Criteria

- [ ] Stage A input requirements understood
- [ ] Output format compared with temp/input.json
- [ ] JSON structure validated (45 entries with id, text, language)
- [ ] Sample natural language manually validated (3-5 samples)
- [ ] Quick parse test passes
- [ ] Format confirmed compatible with pipeline
- [ ] Natural language quality verified

## Notes

- This validates the natural language output, not structured text
- If format issues found, may need to adjust LLM prompt in previous plan
- Focus on ensuring downstream stages can parse the natural language
- Don't need to run full pipeline yet - just validate format
- Natural language should match temp/input.json style
