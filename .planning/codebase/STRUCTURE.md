# IDS Project Structure

## Root Directory Layout

```
E:\code for project\IDS_practise\backend\ids-agent/
├── .claude/                    # Claude Code configuration and memory
├── .git/                       # Git repository
├── .planning/                  # Planning and codebase documentation
│   └── codebase/              # Codebase mapping documents (this location)
├── app/                        # Next.js application directory
├── backend/                    # Backend services
├── cache/                      # Application cache
├── components/                 # React components
├── docs/                       # Documentation (auth.md, upload.md)
├── essay/                      # Thesis/essay content and outputs
├── i18n/                       # Internationalization
├── ids_converter/              # IDS conversion utilities
├── ids-algo/                   # CORE: IDS algorithm implementation
├── ifc_checker/                # IFC validation tools
├── lib/                        # Shared libraries
├── markdown/                   # Markdown processing
├── memory/                     # Memory/context storage
├── node_modules/               # Node.js dependencies
├── note/                       # Development notes
├── reference-for-essay/        # Essay reference materials
├── uploads/                    # File upload directory
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── next.config.mjs             # Next.js configuration
├── package.json                # Node.js package manifest
├── README.md                   # Project readme
├── tailwind.config.js          # Tailwind CSS configuration
├── test_anthropic_endpoint.py  # Anthropic API test
├── test_pipeline.py            # Pipeline integration test
└── tsconfig.json               # TypeScript configuration
```

## Core Algorithm Directory (ids-algo/)

This is the heart of the IDS generation system.

```
ids-algo/
├── a_structured_parser/        # Stage A: Natural language parsing
│   ├── __init__.py            # Package exports
│   ├── entry.py               # Entry point: runStructuredParser()
│   ├── structured_parser.py   # Main parsing logic
│   ├── data_structures.py     # StructuredParseResult, BuildingObject, etc.
│   └── result_formatter.py    # Markdown formatting
│
├── b_facet_classifier/         # Stage B: Facet classification
│   ├── __init__.py            # Package exports
│   ├── entry.py               # Entry point: runFacetClassifier()
│   ├── facet_classifier.py    # Classification logic
│   └── data_structures.py     # FacetClassification, FacetCandidate
│
├── c_knowledge_base_mapping/   # Stage C: IFC knowledge base mapping
│   ├── __init__.py            # Package exports
│   ├── entry.py               # Entry point: runKnowledgeBaseMapping()
│   ├── database_manager.py    # Singleton database manager
│   ├── knowledge_mapping_strategy.py  # Orchestrator
│   ├── data_structures.py     # MappedFacet, KnowledgeBaseMappingStrategy
│   │
│   ├── resolvers/             # Facet-specific resolvers
│   │   ├── resolver_factory.py      # Factory pattern
│   │   ├── entity_resolver.py       # Entity mapping
│   │   ├── property_resolver.py     # Property mapping
│   │   ├── material_resolver.py     # Material mapping
│   │   ├── classification_resolver.py  # Classification mapping
│   │   ├── attribute_resolver.py    # Attribute mapping
│   │   └── partof_resolver.py       # Spatial relationship mapping
│   │
│   ├── resources/             # Knowledge base data files
│   │   └── entity_db.json     # IFC entity database
│   │
│   └── vector_database/       # Vector database implementation
│       ├── __init__.py        # Package exports
│       ├── unified_db.py      # Unified database interface
│       └── core/              # Core vector database components
│           ├── base.py        # IFCVectorKnowledgeBase base class
│           ├── models.py      # IFCItem, IFCVersion, IFCItemType
│           ├── model_manager.py      # Embedding model management
│           └── vector_cache_manager.py  # Vector caching system
│
├── d_constrains/               # Stage D: Constraint extraction
│   ├── __init__.py            # Package exports
│   ├── entry.py               # Entry point: runConstraintExtraction()
│   ├── constraint_extractor.py  # Rule-based extraction
│   └── data_structures.py     # ValueRestriction, RestrictionType, etc.
│
├── e_ids_builder/              # Stage E: IDS specification builder
│   ├── __init__.py            # Package exports
│   ├── entry.py               # Entry point: runIDSBuilder()
│   ├── ids_builder.py         # IDS construction logic
│   └── data_structures.py     # SpecificationSlot, ApplicabilitySlot, etc.
│
├── openrouter/                 # LLM client infrastructure
│   ├── __init__.py            # Package exports
│   ├── client.py              # OpenRouterClient, LLMClient interface
│   ├── settings.py            # Settings class, configuration
│   ├── call_llm.py            # LLM call utilities
│   └── llm_response_handler.py  # Response processing
│
├── prompts/                    # LLM prompt templates
│   ├── __init__.py            # Package exports
│   ├── entity_resolver_prompts.py  # Entity resolution prompts
│   └── facet_classifier.py    # Classification prompts
│
├── cache/                      # Runtime cache
│   └── vectors/               # Cached embedding vectors
│       └── BAAI_bge-m3/       # Model-specific cache (hex-organized)
│           ├── 00/, 01/, ...  # Hex-prefixed cache buckets
│
├── experimental_results/       # Experiment outputs
│   ├── large_scale_test/      # Large-scale experiments
│   ├── real_world_test/       # Real-world test cases
│   ├── reference_verification/  # Reference verification
│   └── runs/                  # Experiment run logs
│
├── tests/                      # Test files
│   ├── a.py                   # Stage A tests
│   ├── b.py                   # Stage B tests
│   ├── c.py                   # Stage C tests
│   ├── d.py                   # Stage D tests
│   └── e.py                   # Stage E tests
│
├── archive_logs/               # Archived log files
├── note/                       # Development notes
├── output/                     # Generated outputs
├── temp/                       # Temporary files
├── venv/                       # Python virtual environment
│
├── pipeline.py                 # MAIN: Pipeline orchestration
├── pipeline_test.py            # Pipeline integration test
├── batch_experiment.py         # Batch experiment runner
├── compare_ids.py              # IDS comparison utility
├── extend_knowledge_base_bridge.py  # KB extension tool
├── generate_experiment_summary.py   # Experiment reporting
├── ids_to_requirements.py      # IDS to requirements converter
├── server.py                   # API server
├── .env-pipeline               # Pipeline-specific environment
├── experiment_config.json      # Experiment configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Algorithm documentation
└── Makefile                    # Build automation
```

## Key Files and Their Purposes

### Entry Points

1. **pipeline.py** - Main pipeline orchestrator
   - Function: `run_ids_pipeline(text_content: str) -> Dict[str, Any]`
   - Coordinates all five stages
   - Handles timing and stage output collection

2. **server.py** - API server
   - Exposes pipeline as HTTP endpoints
   - Handles file uploads and processing

3. **test_pipeline.py** - Integration testing
   - Tests complete pipeline flow
   - Validates output format

### Stage Entry Points

Each stage has an `entry.py` with a main function:

- `a_structured_parser/entry.py`: `runStructuredParser(text: str)`
- `b_facet_classifier/entry.py`: `runFacetClassifier(result: StructuredParseResult)`
- `c_knowledge_base_mapping/entry.py`: `runKnowledgeBaseMapping(classification: FacetClassification)`
- `d_constrains/entry.py`: `runConstraintExtraction(facets: List[MappedFacet])`
- `e_ids_builder/entry.py`: `runIDSBuilder(facets: List[MappedFacet], text: str)`

### Configuration Files

1. **.env** - Main environment variables
   - API keys
   - Model selection
   - Database paths

2. **.env-pipeline** - Pipeline-specific configuration
   - LLM model settings
   - Temperature and token limits

3. **openrouter/settings.py** - Settings class
   - Centralized configuration management
   - Parser/classifier/builder LLM configs
   - Vector dimension settings

4. **experiment_config.json** - Experiment parameters
   - Test case definitions
   - Evaluation criteria

### Data Structure Files

Each stage defines its data structures in `data_structures.py`:

- **a_structured_parser/data_structures.py**
  - `StructuredParseResult`, `BuildingObject`, `PropertyDescription`, `MaterialRequirement`, `SpatialRelationship`

- **b_facet_classifier/data_structures.py**
  - `FacetClassification`, `FacetCandidate`

- **c_knowledge_base_mapping/data_structures.py**
  - `MappedFacet`, `KnowledgeBaseMappingStrategy`

- **d_constrains/data_structures.py**
  - `ValueRestriction`, `RestrictionType`, `BoundsRestriction`, `EnumerationRestriction`, `PatternRestriction`, `LengthRestriction`

- **e_ids_builder/data_structures.py**
  - `SpecificationSlot`, `ApplicabilitySlot`, `RequirementsSlot`

### Knowledge Base Resources

- **c_knowledge_base_mapping/resources/entity_db.json**
  - IFC entity definitions
  - Used by vector database for semantic search

- **cache/vectors/BAAI_bge-m3/**
  - Cached embedding vectors (pickle files)
  - Organized by hex prefix (00-ff)
  - Avoids recomputing embeddings

### Test Structure

```
tests/
├── a.py    # Test Stage A: Structured parsing
├── b.py    # Test Stage B: Facet classification
├── c.py    # Test Stage C: Knowledge base mapping
├── d.py    # Test Stage D: Constraint extraction
└── e.py    # Test Stage E: IDS building
```

Each test file can be run independently to test a single stage.

### Experiment Structure

```
experimental_results/
├── large_scale_test/       # Batch processing results
├── real_world_test/        # Real-world requirement tests
├── reference_verification/ # Validation against reference IDS
└── runs/                   # Timestamped experiment runs
```

### Documentation Locations

- **README.md** (root) - Project overview
- **ids-algo/README.md** - Algorithm documentation
- **docs/** - Feature documentation
  - `auth.md` - Authentication
  - `upload.md` - File upload
- **essay/** - Thesis content
- **.claude/projects/.../memory/** - Claude Code memory files
- **EXPERIMENT_DATA_GUIDE.md** - Experiment data guide
- **STAGE_C_*.md** - Stage C diagnosis and fixes

## Module Organization Principles

### 1. Package Structure
Each pipeline stage is a Python package with:
- `__init__.py` - Exports public interface
- `entry.py` - Main entry point function
- `data_structures.py` - Data type definitions
- Implementation files - Core logic

### 2. Naming Conventions
- Stages: `a_`, `b_`, `c_`, `d_`, `e_` prefixes
- Entry functions: `run<StageName>()` pattern
- Data structures: Descriptive names ending in `Result`, `Classification`, `Facet`, `Restriction`, `Slot`

### 3. Dependency Direction
```
Stage A (no dependencies)
  ↓
Stage B (depends on A's data structures)
  ↓
Stage C (depends on B's data structures)
  ↓
Stage D (depends on C's data structures)
  ↓
Stage E (depends on C and D's data structures)
```

Shared infrastructure (openrouter, prompts) is used by multiple stages.

### 4. Configuration Hierarchy
```
.env (environment variables)
  ↓
openrouter/settings.py (Settings class)
  ↓
Stage-specific configuration
```

### 5. Cache Organization
- Vector cache organized by model name and hex prefix
- Enables efficient lookup and prevents directory bloat
- Pickle format for fast serialization

## Import Patterns

### Stage Entry Points
```python
from a_structured_parser import runStructuredParser
from b_facet_classifier import runFacetClassifier
from c_knowledge_base_mapping import runKnowledgeBaseMapping
from d_constrains import runConstraintExtraction
from e_ids_builder.entry import runIDSBuilder
```

### Data Structures
```python
from a_structured_parser import StructuredParseResult
from b_facet_classifier import FacetClassification, FacetCandidate
from c_knowledge_base_mapping.data_structures import MappedFacet
from d_constrains import ValueRestriction
```

### Infrastructure
```python
from openrouter import OpenRouterClient
from openrouter.settings import Settings
```

## Virtual Environment

- **venv/** - Python virtual environment
- **requirements.txt** - Python dependencies
  - FAISS for vector search
  - OpenAI SDK for LLM calls
  - Anthropic SDK for Claude API
  - NumPy for numerical operations

## Build and Run

### Setup
```bash
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### Run Pipeline
```bash
cd ids-algo
python pipeline.py
```

### Run Tests
```bash
python tests/a.py  # Test individual stage
python pipeline_test.py  # Test full pipeline
```

### Run Experiments
```bash
python batch_experiment.py
```

## Frontend Integration

The Next.js frontend (app/, components/, lib/) integrates with the Python backend via:
- API routes calling server.py
- File upload handling
- Result visualization

This is a hybrid TypeScript/Python project with clear separation between frontend and algorithm implementation.
