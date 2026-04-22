# IDS Project Architecture

## Overview

The IDS (Information Delivery Specification) project is a pipeline-based system that transforms natural language building requirements into structured IFC-compliant IDS specifications. The architecture follows a five-stage sequential processing model with clear separation of concerns.

## System Architecture

### Pipeline Stages (A-E)

The system implements a linear pipeline with five distinct stages:

```
Text Input → [A] → [B] → [C] → [D] → [E] → IDS JSON Output
```

#### Stage A: Structured Parser
- **Purpose**: Parse natural language text into structured building components
- **Input**: Raw text string (natural language requirements)
- **Output**: `StructuredParseResult` containing:
  - Building objects (entities with types and modifiers)
  - Property descriptions (properties with constraints)
  - Material requirements
  - Spatial relationships
  - Unmatched text fragments
- **Key Components**:
  - `structuredParser`: Main parsing logic using LLM
  - `result_formatter`: Formats results as markdown
  - Uses OpenRouter/Anthropic LLM client for NLP

#### Stage B: Facet Classifier
- **Purpose**: Classify parsed elements into IFC facet types
- **Input**: `StructuredParseResult` from Stage A
- **Output**: `FacetClassification` containing categorized candidates:
  - Entity candidates (IFC entities like IfcWall, IfcDoor)
  - Property candidates (properties like Height, Width)
  - Attribute candidates (IFC attributes)
  - Material candidates (materials like Concrete, Steel)
  - Classification candidates (classification systems)
  - PartOf candidates (spatial relationships)
- **Key Components**:
  - `facetClassifier`: LLM-based classification logic
  - Each candidate includes confidence score and reasoning

#### Stage C: Knowledge Base Mapping
- **Purpose**: Map classified facets to standardized IFC terminology using vector databases
- **Input**: `FacetClassification` from Stage B
- **Output**: `List[MappedFacet]` with IFC-standardized names
- **Key Components**:
  - `KnowledgeBaseMappingOrchestrator`: Coordinates mapping process
  - `DatabaseManager`: Singleton managing all vector databases
  - `ResolverFactory`: Creates specialized resolvers for each facet type
  - Six resolver types: Entity, Property, Material, Classification, Attribute, PartOf
  - Vector database using FAISS for semantic search
  - Caching system for embedding vectors
- **Architecture Pattern**: Strategy + Factory + Singleton
  - Strategy: Different mapping strategies per facet type
  - Factory: ResolverFactory creates appropriate resolvers
  - Singleton: DatabaseManager ensures single instance

#### Stage D: Constraint Extraction
- **Purpose**: Extract value constraints from facet text
- **Input**: `List[MappedFacet]` from Stage C
- **Output**: `List[ValueRestriction]` containing:
  - Bounds restrictions (numeric ranges with units)
  - Enumeration restrictions (allowed values)
  - Pattern restrictions (regex patterns)
  - Length restrictions (string length constraints)
- **Key Components**:
  - `ConstraintExtractor`: Rule-based constraint extraction
  - Supports multiple restriction types via enum pattern

#### Stage E: IDS Builder
- **Purpose**: Construct final IDS JSON specification
- **Input**: 
  - `List[MappedFacet]` with merged constraints
  - Original text
- **Output**: IDS JSON specification with:
  - Applicability slots (what to check)
  - Requirements slots (what to validate)
  - Metadata and reasoning
- **Key Components**:
  - `IdsBuilder`: Orchestrates IDS construction
  - Merges constraints back into facets via text matching
  - Groups facets into logical specifications
  - Uses LLM for intelligent grouping decisions

### Pipeline Orchestration

The `pipeline.py` module orchestrates the entire flow:

```python
async def run_ids_pipeline(text_content: str) -> Dict[str, Any]:
    # Stage A: Parse
    res_a = await runStructuredParser(text_content)
    
    # Stage B: Classify
    res_b = await runFacetClassifier(res_a)
    
    # Stage C: Map to IFC
    facets = await runKnowledgeBaseMapping(res_b)
    
    # Stage D: Extract constraints
    constraints = runConstraintExtraction(facets)
    
    # Stage E: Merge and build IDS
    # E1: Merge constraints into facets
    # E2: Build final IDS JSON
    final_json = await runIDSBuilder(facets, text_content)
    
    return final_json
```

## Design Patterns

### 1. Pipeline Pattern
- Sequential stages with clear input/output contracts
- Each stage is independently testable
- Data flows through immutable data structures

### 2. Strategy Pattern
- `KnowledgeBaseMappingStrategy`: Configurable mapping strategies
- Different resolvers for different facet types
- Pluggable LLM clients (OpenRouter vs Anthropic)

### 3. Factory Pattern
- `ResolverFactory`: Creates appropriate resolver instances
- Centralizes resolver instantiation logic
- Manages resolver dependencies

### 4. Singleton Pattern
- `DatabaseManager`: Single instance manages all vector databases
- Thread-safe initialization with double-checked locking
- Lazy loading of database resources

### 5. Builder Pattern
- `IdsBuilder`: Constructs complex IDS specifications step-by-step
- Separates construction logic from representation

### 6. Adapter Pattern
- `OpenRouterClient`: Adapts both OpenRouter and Anthropic APIs
- Unified interface for different LLM providers

## Data Flow

### Primary Data Structures

```
Text → StructuredParseResult → FacetClassification → MappedFacet → ValueRestriction → IDS JSON
```

Each stage transforms data through well-defined structures:

1. **StructuredParseResult**: Raw parsed components
   - BuildingObject, PropertyDescription, MaterialRequirement, SpatialRelationship

2. **FacetClassification**: Categorized candidates
   - FacetCandidate with type, confidence, reasoning

3. **MappedFacet**: IFC-standardized facets
   - Includes IFC item, confidence, property set, entity context

4. **ValueRestriction**: Extracted constraints
   - RestrictionType enum with typed restrictions

5. **SpecificationSlot**: Final IDS structure
   - ApplicabilitySlot + RequirementsSlot

### Data Structure Hierarchy

```
StructuredParseResult
├── BuildingObject[]
├── PropertyDescription[]
├── MaterialRequirement[]
└── SpatialRelationship[]

FacetClassification
├── entity_candidates: FacetCandidate[]
├── property_candidates: FacetCandidate[]
├── material_candidates: FacetCandidate[]
├── classification_candidates: FacetCandidate[]
├── attribute_candidates: FacetCandidate[]
└── partof_candidates: FacetCandidate[]

MappedFacet
├── facet_type: str
├── original_text: str
├── mapped_name: str
├── confidence: float
├── ifc_item: IFCItem
├── property_set: str
├── entity_name: str
├── constraints: ValueRestriction[]
└── additional_data: Dict

ValueRestriction
├── restriction_type: RestrictionType
└── restriction: Union[Bounds, Enumeration, Pattern, Length]
```

## Key Abstractions

### 1. LLM Client Interface
```python
class LLMClient(ABC):
    async def generate(messages, **kwargs) -> Dict[str, Any]
```
- Abstracts LLM provider details
- Supports structured JSON output
- Handles both OpenRouter and Anthropic APIs

### 2. Knowledge Base Interface
```python
class KnowledgeBase(ABC):
    def search(query, top_k, **kwargs) -> List[Tuple[Any, float]]
    def add_item(item) -> None
    def save(path) -> None
    def load(path) -> None
```
- Abstracts vector database operations
- Supports semantic search
- Persistent storage

### 3. Resolver Interface
Each resolver implements:
```python
async def resolve(source_text: str, context: Dict) -> Dict[str, Any]
```
- Returns: mapped_name, confidence, ifc_item, source
- Context-aware resolution (e.g., properties need entity context)

### 4. Vector Database Abstraction
- `IFCVectorKnowledgeBase`: Base class for all vector databases
- `IFCItem`: Unified representation of IFC entities/properties/materials
- `VectorCacheManager`: Caches embeddings to avoid recomputation
- `ModelManager`: Manages embedding model lifecycle

## Module Dependencies

### Core Dependencies
```
pipeline.py
├── a_structured_parser
│   ├── openrouter (LLM client)
│   └── data_structures
├── b_facet_classifier
│   ├── a_structured_parser (input types)
│   ├── openrouter (LLM client)
│   └── data_structures
├── c_knowledge_base_mapping
│   ├── b_facet_classifier (input types)
│   ├── database_manager (singleton)
│   ├── knowledge_mapping_strategy (orchestrator)
│   ├── resolvers (factory + implementations)
│   └── vector_database (FAISS-based search)
├── d_constrains
│   ├── c_knowledge_base_mapping (MappedFacet)
│   └── constraint_extractor (rule-based)
└── e_ids_builder
    ├── c_knowledge_base_mapping (MappedFacet)
    ├── d_constrains (ConstraintExtractor)
    ├── openrouter (LLM client)
    └── ids_builder (construction logic)
```

### Shared Infrastructure
```
openrouter/
├── client.py (LLM abstraction)
├── settings.py (configuration)
└── llm_response_handler.py

prompts/
├── entity_resolver_prompts.py
└── facet_classifier.py
```

## Separation of Concerns

### 1. Stage Isolation
- Each stage (A-E) is a separate Python package
- Clear entry points: `runStructuredParser`, `runFacetClassifier`, etc.
- No cross-stage dependencies except through data structures

### 2. Data vs Logic
- Data structures defined in `data_structures.py` per stage
- Business logic in separate modules (parser, classifier, builder)
- Configuration in `settings.py`

### 3. Infrastructure vs Domain
- Infrastructure: `openrouter/`, `vector_database/`, `cache/`
- Domain: Stage-specific logic (A-E)
- Clear boundaries prevent coupling

### 4. Resolver Specialization
Each resolver handles one facet type:
- `EntityResolver`: IFC entities with abstract filtering
- `PropertyResolver`: Properties with entity context
- `MaterialResolver`: Material specifications
- `ClassificationResolver`: Classification systems
- `AttributeResolver`: IFC attributes
- `PartOfResolver`: Spatial relationships

### 5. Database Management
- `DatabaseManager`: Lifecycle management
- `VectorCacheManager`: Performance optimization
- `ModelManager`: Embedding model management
- Separation of concerns: management vs usage

## Asynchronous Architecture

The pipeline uses async/await for:
- LLM API calls (I/O bound)
- Database initialization
- Pipeline orchestration

Synchronous operations:
- Constraint extraction (rule-based, CPU bound)
- Vector search (FAISS operations)

## Error Handling

- Try-catch at stage entry points
- Graceful degradation (empty databases on failure)
- Logging at each stage
- Error propagation through return values

## Performance Optimizations

1. **Vector Caching**: Embeddings cached to disk (pickle format)
2. **Database Preloading**: Databases loaded once at startup
3. **Singleton Pattern**: Single database manager instance
4. **Batch Processing**: Support for batch experiments
5. **Lazy Initialization**: Resources loaded on demand

## Configuration Management

- `Settings` class in `openrouter/settings.py`
- Environment variables via `.env` files
- Model selection (OpenRouter vs Anthropic)
- Vector dimension configuration
- Temperature and token limits

## Testing Architecture

- Stage-specific test files: `tests/a.py` through `tests/e.py`
- Integration test: `pipeline_test.py`
- Batch experiments: `batch_experiment.py`
- Comparison utilities: `compare_ids.py`
