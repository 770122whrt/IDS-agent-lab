from .structured_parser import structuredParser
from openrouter.settings import Settings
from openrouter import OpenRouterClient
from .data_structures import StructuredParseResult
import logging


async def runStructuredParser(text: str) -> StructuredParseResult:
    """Parse input text using the structured parser."""
    try:
        settings = Settings()
        llm_client = OpenRouterClient()
        return await structuredParser(text, settings, llm_client)
    except Exception as e:
        logging.error(f"Error in entry_step1: {e}")
        raise e
