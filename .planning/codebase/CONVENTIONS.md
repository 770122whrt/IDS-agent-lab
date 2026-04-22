# Code Conventions

This document describes the coding conventions, style guidelines, and patterns used in the IDS Agent project.

## Project Structure

The project follows a modular pipeline architecture with stages labeled alphabetically:

- `a_structured_parser/` - Stage A: Natural language parsing
- `b_facet_classifier/` - Stage B: Facet classification
- `c_knowledge_base_mapping/` - Stage C: Knowledge base mapping
- `d_constrains/` - Stage D: Constraint extraction
- `e_ids_builder/` - Stage E: IDS specification building

## Naming Conventions

### Files and Directories

- **Module directories**: lowercase with underscores, prefixed with stage letter (e.g., `a_structured_parser`, `c_knowledge_base_mapping`)
- **Python files**: lowercase with underscores (e.g., `structured_parser.py`, `data_structures.py`, `entity_resolver.py`)
- **Entry point files**: Named `entry.py` in each module directory
- **Test files**: Located in `tests/` directory, named by stage letter (e.g., `a.py`, `b.py`, `c.py`)
- **Utility files**: Named `utils.py`
- **Configuration files**: `.env-pipeline` for environment variables

### Classes

- **PascalCase** for all class names
- Descriptive names indicating purpose:
  - Data structures: `BuildingObject`, `PropertyDescription`, `MappedFacet`, `ValueRestriction`
  - Processors: `EntityResolver`, `PropertyResolver`, `ConstraintExtractor`
  - Managers: `DatabaseManager`, `VectorCacheManager`, `VectorModelManager`
  - Clients: `LLMClient`, `OpenRouterClient`
  - Builders: `IdsBuilder`

### Functions and Methods

- **snake_case** for all function and method names
- Async functions prefixed with verb indicating action:
  - `async def runStructuredParser()` - Entry point functions
  - `async def structuredParser()` - Core implementation
  - `async def resolve()` - Resolver methods
  - `async def process_entry()` - Processing functions
- Helper functions prefixed with underscore:
  - `def _prepare_components()` - Private helper
  - `def _llm_select_best_match()` - Private async helper
  - `def _extract_bounds_constraints()` - Private extraction method

### Variables

- **snake_case** for all variables
- Descriptive names:
  - `query_text`, `original_text`, `mapped_name`
  - `ifc_version`, `ifc_item`, `property_set`
  - `confidence`, `similarity`, `threshold`
- Constants in **UPPER_SNAKE_CASE**:
  - `BASE_DIR`, `TEMP_DIR`, `DEFAULT_INPUT_FILE`

### Module-Level Entry Points

Each pipeline stage has a standardized entry function:
- `runStructuredParser()` - Stage A
- `runFacetClassifier()` - Stage B
- `runKnowledgeBaseMapping()` - Stage C
- `runConstraintExtraction()` - Stage D
- `runIDSBuilder()` - Stage E

Pattern: `run{StageName}()` in camelCase

## Code Style and Formatting

### Import Organization

Imports are organized in three groups with blank lines between:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import asyncio
import logging
from typing import Dict, Any, List

from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings

from openrouter import Settings
from prompts import select_prompt
from .data_structures import StructuredParseResult
```

### Line Length and Formatting

- No strict line length limit observed, but generally kept reasonable
- Multi-line function signatures use hanging indents
- Dictionary and list literals use trailing commas for multi-line definitions

### String Formatting

- **f-strings** preferred for string interpolation:
  ```python
  logger.info(f"Starting structured parsing for text: {text[:100]}...")
  print(f"▶️ Processing entry {entry_id}")
  ```
- **format()** method used for prompt templates:
  ```python
  formatted_prompt = prompt.format(text=text)
  ```

### Quotes

- Double quotes (`"`) used consistently throughout the codebase
- Single quotes (`'`) used only in special cases

## Documentation Standards

### Module Docstrings

Every module has a docstring at the top, often bilingual (English/Chinese):

```python
"""
Structured parser for building descriptions
Converts natural language into structured components using LLM
"""
```

```python
"""
Data structures for layered extraction pipeline

Defines clear interfaces between pipeline stages
分层提取管道的数据结构

定义管道阶段之间的清晰接口
"""
```

### Function Docstrings

Functions use Google-style docstrings with Args and Returns sections:

```python
async def resolve(
    self, query_text: str, context: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    解析Entity

    Args:
        query_text: 查询文本
        context: 上下文，包含pipeline_memory等

    Returns:
        解析结果
    """
```

### Class Docstrings

Classes have brief docstrings, often bilingual:

```python
@dataclass
class BuildingObject:
    """Parsed building object
    解析后的建筑对象
    """
```

### Inline Comments

- Chinese comments used frequently for implementation details
- English comments for high-level explanations
- Comments explain "why" not "what":
  ```python
  # 注意: runFacetClassifier 接受的是 Step A 的结果对象
  res_b = await runFacetClassifier(res_a)
  ```

## Type Hints Usage

### Comprehensive Type Annotations

Type hints are used extensively throughout the codebase:

```python
from typing import Dict, Any, List, Optional, Tuple

async def run_ids_pipeline(
    text_content: str, 
    return_timing: bool = False, 
    return_stage_outputs: bool = False
) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, Any]]:
```

### Common Type Patterns

- `Optional[T]` for nullable values
- `List[T]` for lists with specific types
- `Dict[str, Any]` for flexible dictionaries
- `Tuple[T1, T2]` for fixed-length tuples
- Custom types: `list[MappedFacet]`, `List[ValueRestriction]`

### Dataclasses

Extensive use of `@dataclass` decorator for data structures:

```python
from dataclasses import dataclass

@dataclass
class BuildingObject:
    raw_text: str
    object_type: str
    modifiers: List[str]
    confidence: float
```

### Enums

Type-safe enums using `str` and `Enum`:

```python
from enum import Enum

class IFCVersion(str, Enum):
    IFC2X3 = "IFC2X3"
    IFC4 = "IFC4"
    IFC4X3 = "IFC4X3"

class RestrictionType(Enum):
    BOUNDS = "bounds"
    ENUMERATION = "enumeration"
    PATTERN = "pattern"
    LENGTH = "length"
```

## Error Handling Patterns

### Try-Except with Logging

Standard pattern for error handling:

```python
try:
    result = await runStructuredParser(text)
    # ... processing ...
except Exception as e:
    logger.error(f"Structured parsing failed: {str(e)}")
    # Return fallback or re-raise
    return StructuredParseResult(
        building_objects=[],
        property_descriptions=[],
        # ... empty defaults ...
    )
```

### Graceful Degradation

Functions return empty/default values on failure rather than crashing:

```python
if not results:
    return None

if not components:
    logger.warning("No components to classify")
    return _empty_classification()
```

### Error Propagation

Errors are logged and re-raised in main entry points:

```python
except Exception as e:
    print(f"❌ Error: {e}")
    raise
```

### Traceback Printing

Detailed error information in pipeline code:

```python
except Exception as e:
    logger.error(f"[ERROR] Pipeline failed: {e}")
    import traceback
    traceback.print_exc()
```

## Logging Conventions

### Logger Setup

Module-level logger initialization:

```python
import logging

logger = logging.getLogger(__name__)
```

Pipeline-level logging configuration:

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ids_pipeline")
```

### Log Levels

- `logger.info()` - Progress updates, stage completion
- `logger.warning()` - Non-critical issues
- `logger.error()` - Failures and exceptions

### Log Message Format

Structured log messages with context:

```python
logger.info(f"Starting structured parsing for text: {text[:100]}...")
logger.info(f"[Step A] Running Structured Parser...")
logger.info(f"   Generated {len(facets)} facets.")
logger.error(f"Entity resolution failed: {str(e)}")
```

Console output uses emoji for visual clarity:

```python
print(f"▶️ Processing entry {entry_id}")
print(f"✅ Json temp file saved to: {output_path}")
print(f"❌ Error: {e}")
print(f"📄 File: {finalfilename}")
```

## Configuration Management

### Pydantic Settings

Configuration uses `pydantic-settings` for validation:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_provider: str = "openrouter"
    llm_api_key: Optional[str] = None
    parser_llm_model: str = "anthropic/claude-3.5-sonnet"
    
    model_config = SettingsConfigDict(
        env_file=".env-pipeline",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

### Field Validators

Custom validation using `@field_validator`:

```python
@field_validator("llm_api_key", mode="before")
def validate_api_key(cls, v, info: ValidationInfo):
    provider = info.data.get("llm_provider")
    if provider == "openrouter" and not v:
        v = os.getenv("OPENROUTER_API_KEY")
        if not v:
            raise ValueError("OpenRouter API key is required")
    return v
```

## Data Serialization Patterns

### JSON Conversion

Custom serialization for complex objects:

```python
def to_jsonable(obj):
    """Recursively convert result classes to JSON-serializable dicts."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    
    if isinstance(obj, list):
        return [to_jsonable(i) for i in obj]
    
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    
    if hasattr(obj, "__dict__"):
        return {k: to_jsonable(v) for k, v in vars(obj).items()}
    
    return str(obj)
```

### Dataclass Conversion

Standard pattern for dataclass serialization:

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "StructuredParseResult":
    """Create from dictionary"""
    return cls(
        building_objects=[
            BuildingObject(**obj) for obj in data.get("building_objects", [])
        ],
        # ...
    )

def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary representation"""
    return {
        "name": self.name,
        "definition": self.definition,
        # ...
    }
```

## Async/Await Patterns

### Async Entry Points

All pipeline stages use async functions:

```python
async def main() -> None:
    try:
        entries = load_input_entries("input.json")
        for entry in entries:
            result = await runStructuredParser(text)
            # ...
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

### Async Orchestration

Pipeline orchestrates async operations sequentially:

```python
async def run_ids_pipeline(text_content: str):
    res_a = await runStructuredParser(text_content)
    res_b = await runFacetClassifier(res_a)
    facets = await runKnowledgeBaseMapping(res_b)
    # ...
```

## File I/O Patterns

### Path Handling

Use `pathlib.Path` for file operations:

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "temp"
output_path = output_dir / finalfilename
```

### JSON File Operations

Standard pattern for reading/writing JSON:

```python
# Reading
with target.open("r", encoding="utf-8") as handle:
    data = json.load(handle)

# Writing
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(result_data, f, indent=2, ensure_ascii=False)
```

### File Creation with Timestamps

Utility functions create timestamped output files:

```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
finalfilename = f"{filename}-{timestamp}.md"
output_path = output_dir / finalfilename
output_path.write_text(content, encoding="utf-8")
```

## Bilingual Code

The codebase uses both English and Chinese:

- **English**: Function names, variable names, class names
- **Chinese**: Comments, docstrings, log messages
- **Bilingual**: Module docstrings, class docstrings

This reflects the project's context serving both international standards (IFC) and Chinese users.
