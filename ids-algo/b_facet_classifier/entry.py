from openrouter.settings import Settings
from openrouter import OpenRouterClient
from .data_structures import FacetClassification
from a_structured_parser import StructuredParseResult
from .facet_classifier import facetClassifier
import logging

async def runFacetClassifier(structured_parser_result: StructuredParseResult) -> FacetClassification:
    try:
        settings = Settings()
        llm_client = OpenRouterClient()
        # Step 2: Facet 分类
        return await facetClassifier(structured_parser_result,settings, llm_client)
    except Exception as e:
        logging.error(f"Error in entry_step2: {e}")
        raise e
