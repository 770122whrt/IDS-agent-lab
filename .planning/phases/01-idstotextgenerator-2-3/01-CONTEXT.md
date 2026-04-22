# Phase 1: 增强IDSToTextGenerator - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning
**Source:** Manual context extraction from PROJECT.md, ROADMAP.md, and codebase analysis

<domain>
## Phase Boundary

This phase focuses on ensuring complete IDS information preservation during text conversion. The existing `IDSToTextGenerator` in `ids_converter/ids_to_text.py` already has the framework to convert IDS XML to structured text, but we need to verify it preserves ALL critical information:

1. **Entity information** (applicability facets) - IFC entity types like IFCBRIDGE, IFCWALL
2. **Requirements information** (partOf/attribute/property/material facets) - All constraint types
3. **Cardinality constraints** (minOccurs/maxOccurs) - Required, Optional, 0..unbounded, 1..unbounded
4. **IFC version information** - IFC4X3_ADD2, IFC4, etc.

**Current Problem:**
- Test scripts use simplified text extraction (only name + description)
- 85% of structured information is lost
- Match rate: 53.3% (should be 85%+)
- Requirements retention: 3.8% (should be 70%+)

**What This Phase Delivers:**
- Verified/enhanced `IDSToTextGenerator` that preserves complete IDS structure
- Generated full structured text file: `ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt`
- Conversion script: `convert_ids_to_text.py` (may already exist)
- Documentation of output format for downstream phases

</domain>

<decisions>
## Implementation Decisions

### Text Conversion Approach
- **LOCKED**: Use existing `IDSToTextGenerator` class from `ids_converter/ids_to_text.py` (940 lines)
- **LOCKED**: Enhance/verify rather than rewrite - existing framework is solid
- **LOCKED**: Output format must be structured text with clear section markers for parsing

### Information Preservation Requirements
- **LOCKED**: Must preserve ALL entity types from applicability facets
- **LOCKED**: Must preserve ALL requirements facets (partOf, attribute, property, material, classification)
- **LOCKED**: Must preserve cardinality constraints with exact values (minOccurs/maxOccurs)
- **LOCKED**: Must preserve IFC version information for each specification
- **LOCKED**: Must preserve description text for context

### Source and Output Files
- **LOCKED**: Source IDS file: `ids_converter/20250317023029_IFCBridge-IDS-xml.ids`
- **LOCKED**: Output file: `ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt`
- **LOCKED**: Expected: 45 specifications with complete information

### Output Format Structure
- **LOCKED**: Each specification must be clearly delimited (e.g., 【Specification N】)
- **LOCKED**: Must include sections: IFC Version, Description, Applicability, Requirements
- **LOCKED**: Cardinality must be explicit (not just "required" but "1..unbounded", "0..unbounded")
- **LOCKED**: Requirements must be numbered and typed (Part Of Requirement, Attribute Requirement, etc.)

### Claude's Discretion
- Exact text formatting details (spacing, indentation) as long as it's parseable
- Whether to use markdown, plain text, or structured format
- How to handle edge cases (missing fields, optional values)
- Error handling and validation logic

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### IDS Converter Implementation
- `ids_converter/ids_to_text.py` — Existing IDSToTextGenerator class (940 lines)
- `ids_converter/20250317023029_IFCBridge-IDS-xml.ids` — Source IDS file with 45 specifications

### Test Scripts (for understanding current usage)
- `ids-algo/test_large_scale_ids.py` — Current test script with simplified text extraction
- `ids-algo/convert_ids_to_text.py` — Conversion script (may exist from previous work)

### Reference Data
- `ids-algo/temp/` — Example input/output formats (a1.json, a2.json, etc.)
- `ids-algo/experimental_results/large_scale_robustness/` — Previous test results showing 53.3% match rate

### Project Documentation
- `.planning/PROJECT.md` — Project goals and constraints
- `.planning/CONFIG.yaml` — Target metrics (85%+ match rate, 70%+ requirements retention)

</canonical_refs>

<specifics>
## Specific Ideas

### Expected Output Format Example
```
【Specification 3】Bridge
IFC Version: IFC4X3_ADD2
Description: Each bridge structure is captured within a definition...

Applicability:
  Cardinality: 1..unbounded
  • Applies to all IFCBRIDGE type entities

Requirements:
  1. Part Of Requirement
     - Relation Type: IFCRELAGGREGATES
     - Related Entity: Must be one of: IFCBRIDGE, IFCPROJECT
     - Cardinality: Required
  2. Attribute Requirement
     - Attribute Name: Name
     - Cardinality: Required
```

### Key IFC4X3 Bridge Entities
- IFCBRIDGE
- IFCALIGNMENT
- IFCBRIDGEPART
- IFCRELAGGREGATES (relationship)

### Verification Criteria
- File size should be ~30KB+ (30,488 characters mentioned in summary)
- Should contain 45 specifications
- Each specification should have multiple sections
- Requirements count should be preserved (79 total across all specs)

</specifics>

<deferred>
## Deferred Ideas

- Performance optimization of text conversion (not critical for this phase)
- Support for other IDS file formats (only need to handle this one file)
- Validation of IDS XML structure (assume source file is valid)
- Internationalization/multi-language support (English output is sufficient)

</deferred>

---

*Phase: 01-idstotextgenerator-2-3*
*Context gathered: 2026-04-23*
