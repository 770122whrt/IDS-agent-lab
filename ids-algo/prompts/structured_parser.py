STRUCTURED_PARSER = """You are a building specification analysis expert. Parse natural language building descriptions into structured components.

Input text: {text}

Extract these components:
1. building_objects: Concrete building elements (walls, doors, windows, slabs)
2. property_descriptions: Quantifiable property requirements (thickness>=240mm, fire rating 2 hours)
3. material_requirements: Material requirements (reinforced concrete, brick, wood)
4. spatial_relationships: Spatial relations (located in, contains, connects)
5. unmatched_fragments: Unclassifiable text fragments

Output JSON format:
{{
    "building_objects": [
        {{
            "raw_text": "original text fragment",
            "object_type": "object type",
            "modifiers": ["modifier words"],
            "confidence": 0.9
        }}
    ],
    "property_descriptions": [
        {{
            "raw_text": "original text fragment",
            "property_name": "property name",
            "constraint_text": "constraint expression",
            "confidence": 0.9
        }}
    ],
    "material_requirements": [
        {{
            "raw_text": "original text fragment",
            "material_name": "material name",
            "specifications": "specification requirements",
            "confidence": 0.9
        }}
    ],
    "spatial_relationships": [
        {{
            "raw_text": "original text fragment",
            "subject": "subject",
            "relation": "relation type",
            "object": "object",
            "confidence": 0.9
        }}
    ],
    "unmatched_fragments": ["unclassifiable text fragments"]
}}

Output JSON only, no other text."""
