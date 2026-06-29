from typing import Dict, Literal
from .facet_classfier import FACET_CLASSIFIER
from .structured_parser import STRUCTURED_PARSER
from .ids_builder import IDS_BUILDER_PROMPT
from .entity_resolver_prompts import ENTITY_RESOLVER_PROMPT

PromptType = Literal[
    "facet_classifier",
    "structured_parser",
    "ids_builder",
    "entity_resolver"
]

PROMPT_BUILDERS: Dict[PromptType, str] = {
    "facet_classifier": FACET_CLASSIFIER,
    "structured_parser": STRUCTURED_PARSER,
    "ids_builder": IDS_BUILDER_PROMPT,
    "entity_resolver": ENTITY_RESOLVER_PROMPT,
}

def select_prompt(prompt_type: PromptType) -> str:
    builder = PROMPT_BUILDERS.get(prompt_type)
    if not builder:
        valid = ", ".join(sorted(PROMPT_BUILDERS))
        raise ValueError(f"Unknown prompt type '{prompt_type}'. Expected one of: {valid}.")
    return builder
