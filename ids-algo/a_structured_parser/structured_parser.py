"""
Structured parser for building descriptions
Converts natural language into structured components using LLM
"""

import logging
from openrouter import Settings
from prompts import select_prompt
from .data_structures import StructuredParseResult
from openrouter import parse_llm_json_response
from openrouter import LLMClient
from openrouter import call_llm_and_response

logger = logging.getLogger(__name__)


async def structuredParser(text: str,
                        settings: Settings,
                        llm_client: LLMClient) -> StructuredParseResult:
    try:
        logger.info(f"Starting structured parsing for text: {text[:100]}...")

        # Get parser prompt and format with input text from propmpt manager v1
        prompt = select_prompt("structured_parser")
        # use text to embedding in the prompt
        formatted_prompt = prompt.format(text=text)
        response_content, llm_analysis = await call_llm_and_response("parser",settings, llm_client,formatted_prompt)

        # Parse the response using unified handler
        fallback_structure = {
            "building_objects": [],
            "property_descriptions": [],
            "material_requirements": [],
            "spatial_relationships": [],
            "unmatched_fragments": [text],
        }
        parsed_data = parse_llm_json_response(
            response_content, fallback_structure, "structured parsing"
        )

        # Convert to structured result
        result = StructuredParseResult.from_dict(parsed_data)

        # Attach LLM analysis to result
        result.llm_analysis = llm_analysis

        logger.info(
            f"Structured parsing completed: "
            f"{len(result.building_objects)} objects, "
            f"{len(result.property_descriptions)} properties, "
            f"{len(result.material_requirements)} materials, "
            f"{len(result.spatial_relationships)} relationships"
        )

        return result

    except Exception as e:
        logger.error(f"Structured parsing failed: {str(e)}")
        # Return empty result on failure
        return StructuredParseResult(
            building_objects=[],
            property_descriptions=[],
            material_requirements=[],
            spatial_relationships=[],
            unmatched_fragments=[text],  # Put original text as unmatched
    )
