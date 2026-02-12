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
        #得到result
        result = await ids_builder.build_ids_specifications(
            mapped_facets = mapped_facets,
            original_text = text,
            include_metadata = include_metadata,
        )

        return result
    
    except Exception as e:
        logging.error(f"Error in constraint extraction: {e}")
        return []
