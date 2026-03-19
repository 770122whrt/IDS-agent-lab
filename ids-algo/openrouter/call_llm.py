from .settings import Settings 
from .client import LLMClient 


async def call_llm_and_response(
    typename: str,
    settings: Settings, 
    llm_client: LLMClient, 
    format_prompt: str
):
    """Call LLM and parse response."""
    # Get LLM configuration
    if typename == "parser":
        llm_config = settings.get_parser_llm_config()
    if typename == "classifier":
        llm_config = settings.get_classifier_llm_config()
        
    # Call LLM
    messages = [{"role": "user", "content": format_prompt}]
    response = await llm_client.generate(
        messages=messages,
        model=llm_config["model"],
        temperature=llm_config["temperature"],
        max_tokens=llm_config["max_tokens"],
    )

    # record LLM analysis
    llm_analysis = f"Prompt: {format_prompt}...\nResponse: {str(response)}..."

    # Parse response
    response_content = response.get("content", "")
    # Parse the response using unified handler
    return response_content, llm_analysis