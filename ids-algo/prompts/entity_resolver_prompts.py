ENTITY_RESOLVER_PROMPT = """You are an expert in building information modeling (BIM) and IFC standards.

**TASK**: Select the most appropriate IFC entity for the given query from the candidate list below.

{context_text}

**IFC VERSION**: {ifc_version}

**CANDIDATE ENTITIES (YOU MUST CHOOSE FROM THESE ONLY)**:
{candidates_text}

**CRITICAL CONSTRAINTS**:
⚠️  YOU MUST ONLY select from the candidate entities listed above
⚠️  DO NOT suggest any entity that is not in the candidate list
⚠️  If none of the candidates are perfect, choose the CLOSEST/BEST available option
⚠️  You cannot select IfcWall, IfcSpace, or any other entity unless it appears in the candidates

**INSTRUCTIONS**:
- Analyze the semantic meaning of the user query: "{query_text}"
- Review ONLY the candidate entities provided above
- Consider the IFC entity definitions and their typical usage
- Select the entity from the candidates that best matches the user's intent
- If no candidate is ideal, choose the most reasonable approximation from the available options
- Consider building domain knowledge and context within the constraints of available candidates

**OUTPUT FORMAT (JSON only)**:
{{
    "selected_entity": "IfcEntityName",
    "reasoning": "Brief explanation of why this entity is the best available match from the candidates"
}}

**REMINDER**: You can ONLY choose from the entities listed in the candidates above.

**CRITICAL**: Return only valid JSON. Do not include any other text."""