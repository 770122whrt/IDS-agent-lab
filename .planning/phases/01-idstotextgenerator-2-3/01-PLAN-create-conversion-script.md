---
phase: 1
plan_id: create-conversion-script
title: Create/Verify IDS to Text Conversion Script
estimated_duration: 30min
dependencies: [verify-idstotextgenerator]
---

# Plan: Create/Verify IDS to Text Conversion Script

## Objective

Create or verify the `convert_ids_to_text.py` script that uses `IDSToTextGenerator` to convert the source IDS file to complete structured text.

## Context

- Source IDS: `ids_converter/20250317023029_IFCBridge-IDS-xml.ids`
- Output: `ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt`
- Tool: `IDSToTextGenerator` from `ids_converter/ids_to_text.py`
- Expected: 45 specifications, ~30KB output

## Tasks

### 1. Check if Script Exists
**Action:** Check if `convert_ids_to_text.py` exists
- Location: Project root or `ids-algo/` directory
- If exists: Read and verify it's correct
- If not: Create it

**Success:** Know the current state

### 2. Create/Update Conversion Script
**Action:** Write `convert_ids_to_text.py` with:
```python
from ids_converter.ids_to_text import IDSToTextGenerator

def convert_ids_to_text(ids_file_path, output_file_path, language="en"):
    generator = IDSToTextGenerator()
    text = generator.generate_from_file(ids_file_path, language=language)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Converted {ids_file_path}")
    print(f"Output: {output_file_path}")
    print(f"Size: {len(text)} characters")
    print(f"Specifications: {text.count('Specification:')}")

if __name__ == "__main__":
    ids_file = "ids_converter/20250317023029_IFCBridge-IDS-xml.ids"
    output_file = "ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt"
    convert_ids_to_text(ids_file, output_file, language="en")
```

**Success:** Script created with proper encoding (UTF-8) and error handling

### 3. Run Conversion
**Action:** Execute the conversion script:
```bash
cd "E:\code for project\IDS_practise\backend\ids-agent"
python convert_ids_to_text.py
```

**Success:** 
- Script runs without errors
- Output file created
- ~30KB size, 45 specifications

### 4. Verify Output Quality
**Action:** Read first 100 lines of output to verify:
- Specifications are clearly delimited
- IFC version is present
- Entity types are preserved
- Requirements are preserved with types
- Cardinality is explicit

**Success:** Output contains all required information

## Acceptance Criteria

- [ ] Conversion script exists and is correct
- [ ] Script uses UTF-8 encoding (Windows compatibility)
- [ ] Output file generated: `ids_input_text_full.txt`
- [ ] File size ~30KB with 45 specifications
- [ ] Sample output verified to contain complete information
- [ ] No encoding errors or crashes

## Notes

- Windows encoding issues: Always use `encoding='utf-8'`
- The summary mentioned this was done before but file doesn't exist now
- May need to re-run if previous output was lost
