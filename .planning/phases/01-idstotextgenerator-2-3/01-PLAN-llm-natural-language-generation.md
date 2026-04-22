---
phase: 1
plan_id: llm-natural-language-generation
title: LLM Natural Language Generation from Structured Text
estimated_duration: 1-2h
dependencies: [create-conversion-script, enhance-idstotextgenerator]
---

# Plan: LLM Natural Language Generation from Structured Text

## Objective

Convert the structured text (ids_input_text_full.txt) into natural language descriptions using LLM, matching the format expected by the pipeline (like temp/input.json examples).

## Context

**Current situation:**
- We have structured text: `【Specification 3】Bridge\nIFC Version: IFC4X3_ADD2\n...`
- Pipeline expects natural language: "All walls should have the property FireRating..."
- Need LLM to convert structured → natural language

**Reference format (temp/input.json):**
```json
[
  {
    "id": "1",
    "text": "All walls should have the property FireRating in the set Pset_WallCommon with a value being one of REI30, REI60, REI90.",
    "language": "en"
  }
]
```

## Tasks

### 1. Analyze Natural Language Requirements
**Action:** Study temp/input.json examples to understand:
- How entities are expressed ("All walls", "entities that have IFC class IFCBUILDINGSTOREY")
- How requirements are expressed ("MUST HAVE attribute", "should have the property")
- How cardinality is expressed ("MUST contain", "all", "each")
- Tone and style (formal, imperative)

**Success:** Clear understanding of target natural language style

### 2. Design LLM Prompt Template
**Action:** Create prompt template for converting structured text to natural language:

```
You are converting IDS specifications from structured format to natural language.

Input (structured):
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

Convert to natural language following these rules:
1. Start with IFC version declaration
2. Describe which entities this applies to (applicability)
3. List all requirements in natural language
4. Use "MUST" for required, "SHOULD" for optional
5. Be clear and precise

Output format:
IFC versions: IFC4X3_ADD2

The model MUST contain entities that have IFC class IFCBRIDGE with cardinality 1..unbounded

that MEET the following requirements:
- MUST be part of (via IFCRELAGGREGATES) one of: IFCBRIDGE, IFCPROJECT
- MUST HAVE attribute Name
```

**Success:** Prompt template designed and tested with 1-2 examples

### 3. Create Natural Language Generation Script
**Action:** Write `generate_natural_language.py`:

```python
import json
import asyncio
from openrouter import OpenRouterClient
from openrouter.settings import Settings

async def convert_to_natural_language(structured_text: str, spec_id: str) -> str:
    """Convert one structured specification to natural language"""
    
    prompt = f"""Convert this IDS specification from structured format to natural language.

{structured_text}

Follow these rules:
1. Start with IFC version declaration
2. Describe applicability (which entities, cardinality)
3. List all requirements clearly
4. Use "MUST" for required, "SHOULD" for optional
5. Be precise and complete

Output natural language description:"""

    settings = Settings()
    client = OpenRouterClient()
    
    response = await client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=settings.model_name,
        temperature=0.3  # Low temperature for consistency
    )
    
    return response.choices[0].message.content

async def process_all_specifications(input_file: str, output_file: str):
    """Process all specifications from structured text to natural language"""
    
    # Read structured text
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into specifications
    specs = content.split('【Specification')
    specs = [s.strip() for s in specs if s.strip()]
    
    results = []
    
    for i, spec in enumerate(specs, 1):
        print(f"Processing specification {i}/{len(specs)}...")
        
        # Convert to natural language
        natural_text = await convert_to_natural_language(
            f"【Specification{spec}",
            str(i)
        )
        
        results.append({
            "id": str(i),
            "text": natural_text,
            "language": "en"
        })
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Generated {len(results)} natural language specifications")
    print(f"[OK] Output: {output_file}")

if __name__ == "__main__":
    input_file = "ids-algo/experimental_results/large_scale_test/ids_input_text_full.txt"
    output_file = "ids-algo/experimental_results/large_scale_test/ids_input_natural_language.json"
    
    asyncio.run(process_all_specifications(input_file, output_file))
```

**Success:** Script created and ready to run

### 4. Run Natural Language Generation
**Action:** Execute the generation:
```bash
cd "E:\code for project\IDS_practise\backend\ids-agent"
python generate_natural_language.py
```

**Expected:**
- Process 45 specifications
- ~45 LLM calls (one per specification)
- Time: ~5-10 minutes depending on API speed
- Output: `ids_input_natural_language.json`

**Success:** All 45 specifications converted without errors

### 5. Validate Natural Language Output
**Action:** Verify output quality:
- Read 3-5 sample specifications
- Check they match temp/input.json style
- Verify all information is preserved (entities, requirements, cardinality)
- Ensure natural language is clear and readable
- Compare with original structured text to confirm completeness

**Success:** Natural language output is high quality and complete

### 6. Create Comparison Report
**Action:** Document the conversion:
- Show 2-3 before/after examples
- Structured text → Natural language
- Highlight how information is preserved
- Note any edge cases or issues

**Success:** Comparison documented for reference

## Acceptance Criteria

- [ ] Natural language style requirements analyzed
- [ ] LLM prompt template designed and tested
- [ ] Generation script created (generate_natural_language.py)
- [ ] All 45 specifications converted successfully
- [ ] Output file created: ids_input_natural_language.json
- [ ] Sample outputs validated for quality and completeness
- [ ] Comparison report created
- [ ] Natural language matches pipeline input format

## Notes

- Use low temperature (0.3) for consistency
- May need to iterate on prompt template based on initial results
- Consider batch processing if API has rate limits
- This is the critical step that makes the output usable by the pipeline
- Phase 2 will use this natural language file, not the structured text

## Cost Estimate

- 45 specifications × ~2000 tokens input × ~500 tokens output
- Total: ~112,500 tokens
- Cost: ~$0.50-1.00 (depending on model)
