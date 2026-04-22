---
phase: 1
plan_id: enhance-idstotextgenerator
title: Enhance IDSToTextGenerator (If Needed)
estimated_duration: 1-2h
dependencies: [verify-idstotextgenerator, create-conversion-script]
---

# Plan: Enhance IDSToTextGenerator (If Needed)

## Objective

Based on verification results, enhance `IDSToTextGenerator` to preserve any missing information. This plan may be skipped if verification shows it already preserves everything.

## Context

- File: `ids_converter/ids_to_text.py`
- Required information: entity types, requirements (all facet types), cardinality, IFC version
- Current status: TBD from verification plan

## Tasks

### 1. Review Verification Results
**Action:** Check findings from verify-idstotextgenerator plan:
- What information is currently preserved?
- What information is missing?
- Is enhancement needed?

**Decision Point:** If everything is preserved, SKIP this plan and mark as complete

### 2. Enhance Entity Information (If Needed)
**Action:** If entity types are not fully preserved:
- Locate applicability facet handling in `generate()` method
- Ensure all entity types are included in output
- Add cardinality for applicability (e.g., "1..unbounded")

**Success:** Entity types fully preserved with cardinality

### 3. Enhance Requirements Information (If Needed)
**Action:** If requirements are not fully preserved:
- Ensure partOf requirements are included (relation type, related entity)
- Ensure attribute requirements are included (attribute name, value constraints)
- Ensure property requirements are included (property set, property name, value)
- Ensure material requirements are included (material name)
- Ensure classification requirements are included (system, value)

**Success:** All requirement types preserved with complete details

### 4. Enhance Cardinality Information (If Needed)
**Action:** If cardinality is not explicit:
- Change from "Required/Optional" to "1..unbounded", "0..unbounded", etc.
- Preserve exact minOccurs and maxOccurs values
- Apply to both applicability and requirements

**Success:** Cardinality is explicit and precise

### 5. Enhance IFC Version Information (If Needed)
**Action:** If IFC version is missing:
- Extract IFC version from IDS XML
- Include in each specification output
- Format: "IFC Version: IFC4X3_ADD2"

**Success:** IFC version present for each specification

### 6. Test Enhanced Version
**Action:** Re-run conversion script with enhanced generator:
```bash
python convert_ids_to_text.py
```
- Compare output before/after
- Verify all information is now preserved

**Success:** Output contains complete information

## Acceptance Criteria

- [ ] Verification results reviewed
- [ ] Enhancement decision made (enhance vs. skip)
- [ ] If enhancing: All missing information now preserved
- [ ] If enhancing: Conversion re-run successfully
- [ ] If enhancing: Output verified to be complete
- [ ] If skipping: Documented that no enhancement needed

## Notes

- This plan is conditional - may be skipped if verification shows no enhancement needed
- Focus on minimal changes - don't refactor unnecessarily
- Preserve existing functionality - only add missing information
- Test after each enhancement to catch issues early
