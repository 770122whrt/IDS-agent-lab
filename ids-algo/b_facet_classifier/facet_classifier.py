"""
Facet classifier for IDS specifications
Classifies structured components into 6 IDS facet types using LLM
"""

import json
import logging
from typing import Dict, Any, List

from openrouter import Settings
from .data_structures import (
    FacetClassification,
)
from a_structured_parser import StructuredParseResult
from openrouter import LLMClient
from openrouter import parse_llm_json_response
from openrouter import call_llm_and_response
from prompts import select_prompt
logger = logging.getLogger(__name__)


async def facetClassifier(
                        parse_result: StructuredParseResult,
                        settings: Settings, 
                        llm_client: LLMClient) -> FacetClassification:
        """
        Classify structured components into IDS facet types

        Args:
            parse_result: Result from structured parsing

        Returns:
            FacetClassification with categorized candidates
        """
        try:
            logger.info("Starting facet classification")

            # Prepare components for classification
            components = _prepare_components(parse_result)

            if not components:
                logger.warning("No components to classify")
                return _empty_classification()


            # Get classifier prompt
            prompt = select_prompt("facet_classifier")
            formatted_prompt = prompt.format(
                components=json.dumps(components, ensure_ascii=False)
            )

            response_content, llm_analysis = await call_llm_and_response("classifier",settings, llm_client,formatted_prompt)

            # Parse response using unified handler
            fallback_structure: Dict[str, List] = {
                "entity_candidates": [],
                "property_candidates": [],
                "material_candidates": [],
                "attribute_candidates": [],
                "classification_candidates": [],
                "partof_candidates": [],
            }
            # clean the response and parse the JSON
            classification_data = parse_llm_json_response(
                response_content, fallback_structure, "facet classification"
            )

            # Convert to classification result
            result = FacetClassification.from_dict(classification_data)

            # add LLM analysis to the result
            result.llm_analysis = llm_analysis

            total_candidates = (
                len(result.entity_candidates)
                + len(result.property_candidates)
                + len(result.attribute_candidates)
                + len(result.material_candidates)
                + len(result.classification_candidates)
                + len(result.partof_candidates)
            )

            logger.info(
                f"Facet classification completed: {total_candidates} candidates classified"
            )

            return result

        except Exception as e:
            logger.error(f"Facet classification failed: {str(e)}")
            return _empty_classification()

def _prepare_components(
    parse_result: StructuredParseResult
) -> List[Dict[str, Any]]:
    """
    Prepare components for classification

    Args:
        parse_result: Structured parse result

    Returns:
        List of components with metadata
    """
    components = []

    # Add building objects
    for obj in parse_result.building_objects:
        components.append(
            {
                "text": obj.raw_text,
                "type": "building_object",
                "details": {
                    "object_type": obj.object_type,
                    "modifiers": obj.modifiers,
                },
                "confidence": obj.confidence,
            }
        )

    # Add property descriptions
    for prop in parse_result.property_descriptions:
        components.append(
            {
                "text": prop.raw_text,
                "type": "property_description",
                "details": {
                    "property_name": prop.property_name,
                    "constraint_text": prop.constraint_text,
                },
                "confidence": prop.confidence,
            }
        )

    # Add material requirements
    for mat in parse_result.material_requirements:
        components.append(
            {
                "text": mat.raw_text,
                "type": "material_requirement",
                "details": {
                    "material_name": mat.material_name,
                    "specifications": mat.specifications,
                },
                "confidence": mat.confidence,
            }
        )

    # Add spatial relationships
    for rel in parse_result.spatial_relationships:
        components.append(
            {
                "text": rel.raw_text,
                "type": "spatial_relationship",
                "details": {
                    "subject": rel.subject,
                    "relation": rel.relation,
                    "object": rel.object,
                },
                "confidence": rel.confidence,
            }
        )

    return components

def _empty_classification() -> FacetClassification:
    """Return empty classification result"""
    return FacetClassification(
        entity_candidates=[],
        property_candidates=[],
        attribute_candidates=[],
        material_candidates=[],
        classification_candidates=[],
        partof_candidates=[],
    )
