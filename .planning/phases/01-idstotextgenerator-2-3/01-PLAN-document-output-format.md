---
phase: 1
plan_id: document-output-format
title: Document Output Format for Phase 2
estimated_duration: 20min
dependencies: [validate-output-format]
---

# Plan: Document Output Format for Phase 2

## Objective

Create clear documentation of the natural language output format so Phase 2 (fixing test scripts) knows exactly what format to expect and how to use it.

## Context

- Generated file: `ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json`
- Phase 2 will modify test scripts to use this file
- Need clear documentation of format structure and usage

## Tasks

### 1. Create Format Documentation
**Action:** Write `ids-algo/experimental_results/large_scale_test/FORMAT.md` documenting:
- Overall structure (JSON array with 45 specifications)
- JSON schema (id, text, language fields)
- Natural language style and conventions
- Example specifications (simple, medium, complex)
- How entities are expressed in natural language
- How requirements are expressed in natural language
- How cardinality is expressed in natural language
- How to use the file in test scripts

**Success:** Clear documentation exists

### 2. Add Usage Examples
**Action:** Include code examples in FORMAT.md:
```python
# Example: How to read and use the natural language file
import json

with open('ids_input_natural_language.json', 'r', encoding='utf-8') as f:
    specifications = json.load(f)

# Use in test scripts
for spec in specifications:
    spec_id = spec['id']
    natural_text = spec['text']
    language = spec['language']
    
    # Pass to pipeline
    result = await run_ids_pipeline(natural_text)
    
    # Process result...
```

**Success:** Usage examples provided

### 3. Document Key Statistics
**Action:** Add statistics to FORMAT.md:
- Total specifications: 45
- Total requirements: 79 (preserved in natural language)
- File format: JSON
- Encoding: UTF-8
- Language: English (en)
- Average text length per specification
- IFC versions covered: IFC4X3_ADD2, IFC4, etc.

**Success:** Statistics documented

### 4. Create Quick Reference
**Action:** Add a quick reference section:
- File location: `ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json`
- How to regenerate: 
  1. Run `python convert_ids_to_text.py` (structured text)
  2. Run `python generate_natural_language.py` (natural language)
- What information is preserved: All entities, requirements, cardinality, IFC versions
- What Phase 2 needs to do: Modify test scripts to load this JSON file instead of simplified text

**Success:** Quick reference available

## Acceptance Criteria

- [ ] FORMAT.md created in experimental_results/large_scale_test/
- [ ] JSON structure and schema documented
- [ ] Natural language style and conventions documented
- [ ] Example specifications provided (simple, medium, complex)
- [ ] Parsing/usage code examples provided
- [ ] Key statistics included
- [ ] Quick reference section added
- [ ] Documentation is clear and actionable for Phase 2

## Notes

- This documentation is critical for Phase 2 success
- Make it practical - focus on "how to use" not just "what it is"
- Include enough examples that Phase 2 can copy-paste and adapt
- Keep it concise but complete
- Emphasize that this is natural language, not structured text
