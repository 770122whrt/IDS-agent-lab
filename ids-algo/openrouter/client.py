"""
OpenRouter LLM client implementation
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI

from .settings import settings


#from the LLM client interfaces
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """LLM client interface"""

    @abstractmethod
    async def generate(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """
        generate LLM response

        Args:
            messages: messages to send to LLM
            **kwargs: additional parameters

        Returns:
            generated response
        """
        pass


class KnowledgeBase(ABC):
    """knowledge base interface"""
    @abstractmethod
    def search(self, query: str, top_k: int = 5, **kwargs) -> List[tuple[Any, float]]:
        """
        search the knowledge base

        Args:
            query: query text
            top_k: number of results to return
            **kwargs: additional parameters

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    def add_item(self, item: Any) -> None:
        """Add item to knowledge base"""
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Save knowledge base"""
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """Load knowledge base"""
        pass








class OpenRouterClient(LLMClient):
    """OpenRouter LLM client implementation"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenRouter client

        Args:
            config: input configuration dictionary or None to use default settings
        """
        # Use parser-specific LLM config from settings
        self.config = config or settings.get_parser_llm_config()

        # Create OpenAI client
        self.client = OpenAI(
            api_key=self.config["api_key"], base_url=self.config["base_url"]
        )

        self.model = self.config["model"]
        self.temperature = self.config["temperature"]
        self.max_tokens = self.config["max_tokens"]

        logger.info(f"initialize OpenRouter client, model: {self.model}")

    async def generate(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """
        generate response from LLM

        Args:
            messages: messages to send to the LLM
            **kwargs: additional parameters

        Returns:
            generated response
                such as: max_tokens, temperature, schema
        """
        try:
            # construct parameters
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }

            # If there is a JSON schema, add response_format
            if "schema" in kwargs:
                params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": kwargs.get("schema_type", "response"),
                        "strict": True,
                        "schema": kwargs["schema"],
                    },
                }

            # Call API
            response = self.client.chat.completions.create(**params)

            # Get response content: the first choice + first message + content
            content = response.choices[0].message.content

            # if response has usage info, record it 
            if hasattr(response, "usage") and response.usage:
                token_usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            # it has JSON format, parse the response
            if "schema" in kwargs:
                try:
                    # clean possible markdown code block markers
                    cleaned_content = content.strip()
                    if cleaned_content.startswith("```"):
                        # remove the ```json or ``` at the start and ``` at the end
                        lines = cleaned_content.split("\n")
                        if len(lines) > 2:
                            cleaned_content = "\n".join(lines[1:-1])

                    return json.loads(cleaned_content)
                except json.JSONDecodeError:
                    logger.error(f"cannot parse JSON response: {content}")
                    return {"error": "JSON parse failed", "raw_content": content}

            return {"content": content}

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
