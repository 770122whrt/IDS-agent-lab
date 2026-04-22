---
phase: 1
plan_id: document-output-format
title: Document Output Format for Phase 2
estimated_duration: 20min
dependencies: [validate-output-format]
---

# Plan: Document Output Format for Phase 2

## Objective

Create clear documentation of the output format so Phase 2 (fixing test scripts) knows exactly what format to expect and how to use it.

## Context

- Generated file: `ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt`
- Phase 2 will modify test scripts to use this file
- Need clear documentation of format structure

## Tasks

### 1. Create Format Documentation
**Action:** Write `ids-algo/experimental_results/large_scale_test/FORMAT.md` documenting:
- Overall structure (45 specifications)
- Specification delimiter format
- Section structure (IFC Version, Description, Applicability, Requirements)
- Entity format examples
- Requirements format examples (all types)
- Cardinality format examples
- How to parse the file

**Success:** Clear documentation exists

### 2. Add Usage Examples
**Action:** Include code examples in FORMAT.md:
```python
# Example: How to read and parse the file
with open('ids_input_text_full.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into specifications
specs = content.split('【Specification')
specs = [s for s in specs if s.strip()]

# Parse each specification
for spec in specs:
    # Extract IFC version
    if 'IFC Version:' in spec:
        version = spec.split('IFC Version:')[1].split('\n')[0].strip()
    
    # Extract applicability entities
    if 'Applicability:' in spec:
        applicability_section = spec.split('Applicability:')[1].split('Requirements:')[0]
        # Parse entities...
    
    # Extract requirements
    if 'Requirements:' in spec:
        requirements_section = spec.split('Requirements:')[1]
        # Parse requirements...
```

**Success:** Usage examples provided

### 3. Document Key Statistics
**Action:** Add statistics to FORMAT.md:
- Total specifications: 45
- Total requirements: 79 (across all specs)
- File size: ~30KB
- Encoding: UTF-8
- IFC versions used: IFC4X3_ADD2, IFC4, etc.

**Success:** Statistics documented

### 4. Create Quick Reference
**Action:** Add a quick reference section:
- File location
- How to regenerate (run convert_ids_to_text.py)
- What information is preserved
- What Phase 2 needs to do with it

**Success:** Quick reference available

## Acceptance Criteria

- [ ] FORMAT.md created in experimental_results/large_scale_test/
- [ ] Overall structure documented
- [ ] Section formats documented with examples
- [ ] Parsing code examples provided
- [ ] Key statistics included
- [ ] Quick reference section added
- [ ] Documentation is clear and actionable for Phase 2

## Notes

- This documentation is critical for Phase 2 success
- Make it practical - focus on "how to use" not just "what it is"
- Include enough examples that Phase 2 can copy-paste and adapt
- Keep it concise but complete
