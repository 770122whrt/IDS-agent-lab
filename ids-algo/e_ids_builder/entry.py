from d_constrains import ConstraintExtractor
import logging
from .ids_builder import IdsBuilder
from openrouter import OpenRouterClient
from typing import Dict, Any, List
from c_knowledge_base_mapping.data_structures import MappedFacet

async def runIDSBuilder(mapped_facets: List[MappedFacet], text: str = "",include_metadata: bool = True) -> Dict[str, Any]:
    try:
        llm_client = OpenRouterClient()
        constraint_extractor = ConstraintExtractor()
        #初始化
        ids_builder = IdsBuilder(constraint_extractor, llm_client)

        # Infer IFC version from mapped facets (use highest version found)
        ifc_version = _infer_ifc_version(mapped_facets)
        logging.info(f"Inferred IFC version: {ifc_version}")

        #得到result
        result = await ids_builder.build_ids_specifications(
            mapped_facets = mapped_facets,
            ifc_version = ifc_version,
            original_text = text,
            include_metadata = include_metadata,
        )

        return result

    except Exception as e:
        logging.error(f"Error in constraint extraction: {e}")
        return []


def _map_to_ids_version(ifc_version: str) -> str:
    """
    Map ifcopenshell schema version names to IDS XSD-compliant version names.

    IDS XSD only accepts: IFC2X3, IFC4, IFC4X3_ADD2
    ifcopenshell uses: IFC2X3, IFC4, IFC4X3

    Args:
        ifc_version: Version string from ifcopenshell (e.g., "IFC4X3")

    Returns:
        IDS-compliant version string (e.g., "IFC4X3_ADD2")
    """
    version_mapping = {
        "IFC2X3": "IFC2X3",
        "IFC4": "IFC4",
        "IFC4X3": "IFC4X3_ADD2",  # Map IFC4X3 to IFC4X3_ADD2 for IDS XSD compliance
        "IFC4X3_ADD2": "IFC4X3_ADD2",  # Already compliant
    }

    mapped = version_mapping.get(ifc_version, "IFC4")  # Default to IFC4 if unknown
    if mapped != ifc_version:
        logging.info(f"Mapped IFC version: {ifc_version} -> {mapped} (for IDS XSD compliance)")

    return mapped


def _infer_ifc_version(mapped_facets: List[MappedFacet]) -> str:
    """
    Infer the required IFC version from mapped facets.
    Uses the highest version found to ensure all entities are supported.

    Version hierarchy: IFC4X3 > IFC4 > IFC2X3
    Returns IDS XSD-compliant version names (e.g., IFC4X3_ADD2)
    """
    version_priority = {
        "IFC4X3": 3,
        "IFC4": 2,
        "IFC2X3": 1,
    }

    max_version = "IFC4"  # Default fallback
    max_priority = version_priority.get(max_version, 0)

    for facet in mapped_facets:
        # Check if facet has ifc_item with version information
        if facet.ifc_item and hasattr(facet.ifc_item, 'ifc_version'):
            facet_version = facet.ifc_item.ifc_version
            if facet_version:
                priority = version_priority.get(facet_version, 0)
                if priority > max_priority:
                    max_version = facet_version
                    max_priority = priority
                    logging.debug(f"Updated max version to {max_version} from facet: {facet.original_text}")

    # Map to IDS XSD-compliant version name
    return _map_to_ids_version(max_version)
