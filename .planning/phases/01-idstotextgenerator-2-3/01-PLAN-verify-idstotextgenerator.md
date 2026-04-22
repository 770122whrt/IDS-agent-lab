---
phase: 1
plan_id: verify-idstotextgenerator
title: Verify IDSToTextGenerator Implementation
estimated_duration: 30min
dependencies: []
---

# Plan: Verify IDSToTextGenerator Implementation

## Objective

Verify that the existing `IDSToTextGenerator` in `ids_converter/ids_to_text.py` already preserves complete IDS information (entity, requirements, cardinality, IFC version). If it does, we can use it directly. If not, identify what needs to be enhanced.

## Context

- Existing tool: `ids_converter/ids_to_text.py` (940 lines)
- Source IDS: `ids_converter/20250317023029_IFCBridge-IDS-xml.ids`
- Expected output: Complete structured text with all facets preserved

## Tasks

### 1. Read IDSToTextGenerator Implementation
**Action:** Read `ids_converter/ids_to_text.py` focusing on:
- `generate()` method - main conversion logic
- How it handles applicability facets (entity types)
- How it handles requirements facets (partOf, attribute, property, material)
- How it handles cardinality (minOccurs/maxOccurs)
- How it handles IFC version information

**Success:** Understand what information is currently preserved vs. missing

### 2. Check for Existing Conversion Script
**Action:** Check if `convert_ids_to_text.py` already exists in the repo
- If exists: Read it to understand current usage
- If not exists: Note that we'll need to create it

**Success:** Know whether conversion script exists

### 3. Analyze temp Directory Format
**Action:** Read sample files from `ids-algo/temp/` to understand expected format:
- `a1.json` - Stage A input format
- `input.json` - Original input format
- Look for how entity, requirements, cardinality are structured

**Success:** Understand the target format for downstream stages

### 4. Create Verification Report
**Action:** Document findings:
- What information IDSToTextGenerator currently preserves
- What information is missing (if any)
- Whether enhancement is needed or just need to use it correctly
- Recommended approach for next plans

**Success:** Clear understanding of what needs to be done

## Acceptance Criteria

- [ ] IDSToTextGenerator implementation analyzed
- [ ] Current capabilities documented (what it preserves)
- [ ] Gaps identified (what's missing, if anything)
- [ ] temp directory format understood
- [ ] Recommendation made: enhance vs. use as-is

## Notes

- The summary mentioned IDSToTextGenerator is 940 lines and already exists
- Previous work may have already created `convert_ids_to_text.py`
- Focus on verification first before making changes
