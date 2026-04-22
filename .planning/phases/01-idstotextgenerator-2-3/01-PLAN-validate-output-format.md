---
phase: 1
plan_id: validate-output-format
title: Validate Output Format for Pipeline Compatibility
estimated_duration: 30min
dependencies: [create-conversion-script, enhance-idstotextgenerator]
---

# Plan: Validate Output Format for Pipeline Compatibility

## Objective

Ensure the generated structured text format is compatible with the IDS pipeline stages (A→B→C→D→E) and can be successfully parsed.

## Context

- Generated file: `ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt`
- Pipeline stages need to parse this text
- Reference format: `ids-algo/temp/` directory examples

## Tasks

### 1. Analyze Pipeline Input Requirements
**Action:** Check how Stage A (Structured Parser) expects input:
- Read `ids-algo/a_structured_parser/entry.py`
- Understand what text format it can parse
- Check if it expects specific delimiters or structure

**Success:** Understand Stage A input requirements

### 2. Compare with temp Directory Format
**Action:** Compare generated output with `ids-algo/temp/input.json`:
- Check if structure matches
- Verify entity format matches
- Verify requirements format matches
- Identify any format mismatches

**Success:** Know if format is compatible

### 3. Validate Specification Delimiters
**Action:** Verify specifications are clearly separated:
- Check delimiter format (e.g., 【Specification N】)
- Ensure each specification is self-contained
- Verify numbering is consistent (1-45)

**Success:** Specifications are properly delimited

### 4. Validate Information Completeness
**Action:** Manually inspect 3-5 sample specifications:
- Pick simple, medium, complex examples
- Verify each has: IFC version, description, applicability, requirements
- Verify cardinality is explicit
- Verify all requirement types are present

**Success:** Sample specifications contain complete information

### 5. Test Parse-ability (Quick Check)
**Action:** Try to parse the output programmatically:
```python
# Quick test to see if format is parseable
with open('ids_input_text_full.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Count specifications
spec_count = content.count('【Specification')
print(f"Found {spec_count} specifications")

# Check for required sections
has_ifc_version = 'IFC Version:' in content
has_applicability = 'Applicability:' in content
has_requirements = 'Requirements:' in content
print(f"Has IFC Version: {has_ifc_version}")
print(f"Has Applicability: {has_applicability}")
print(f"Has Requirements: {has_requirements}")
```

**Success:** Format is parseable and contains expected sections

## Acceptance Criteria

- [ ] Stage A input requirements understood
- [ ] Output format compared with temp directory examples
- [ ] Specifications properly delimited (45 total)
- [ ] Sample specifications manually validated (3-5 samples)
- [ ] Quick parse test passes
- [ ] Format confirmed compatible with pipeline

## Notes

- This is a validation step, not implementation
- If format issues found, may need to adjust IDSToTextGenerator output
- Focus on ensuring downstream stages can parse the text
- Don't need to run full pipeline yet - just validate format
