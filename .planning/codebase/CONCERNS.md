# Technical Concerns & Known Issues

## Critical Performance Bottlenecks

### Stage C Knowledge Base Mapping (59.6% of total time)
- **Impact**: 171 seconds out of 287 total seconds
- **Root causes**:
  - LLM calls per entity: 44 entities × 3s/call ≈ 132s
  - Vector search inefficiency: Brute-force IndexFlatIP over 2,291 entities
  - Memory leak: 358MB → 2,838MB (7.9× growth)
- **Optimization potential**: 171s → 50s (70% improvement) with batching + IVF indexing

### Requirements Generation Failure (3.8% retention rate)
- **Current state**: Only 3 out of 79 requirements preserved
- **Root cause breakdown**:
  - 85%: Input layer information loss (text conversion drops requirements)
  - 10%: Stage D capability limitations (only extracts numeric/enum constraints)
  - 5%: Stage E slot allocation errors (requirements → applicability)
- **Expected improvement**: 3.8% → 70%+ with proper IDSToTextGenerator usage

## Data Quality Issues

### IDS-to-Text Conversion Information Loss
- **Problem**: `test_large_scale_ids.py` uses simplified conversion (name + description only)
- **Lost information** (85% of critical data):
  - Applicability facets (entity names, predefinedType)
  - Requirements facets (partOf, attribute, property, material)
  - Cardinality (minOccurs, maxOccurs)
  - IFC version information
  - Structured constraints (value restrictions, enumerations, patterns)
- **Impact**: 21 specifications completely lost, 53.3% match rate
- **Solution exists**: `ids_converter/ids_to_text.py` has proper `IDSToTextGenerator` class

### Entity Database Incompleteness
- **File**: `c_knowledge_base_mapping/resources/entity_db.json`
- **Current coverage**: 2,291 entities (IFC2X3/IFC4 only)
- **Missing**: IFC4X3 bridge-specific entities
  - IfcBridge, IfcBridgePart
  - IfcAlignment, IfcAlignmentHorizontal, IfcAlignmentVertical
  - IfcBorehole, IfcGeomodel
  - IfcKerb, IfcPavement
- **Impact**: 60% of mapping errors due to missing entities
  - Example: "Piers" → IfcPerson (wrong) instead of IfcColumn/IfcMember (correct)

## Architecture & Code Quality

### Inefficient LLM Usage Pattern
- **Location**: `c_knowledge_base_mapping/resolvers/entity_resolver.py`
- **Problem**: Sequential LLM calls for each entity
- **Missing optimizations**:
  - No batch processing
  - No response caching
  - No concurrent execution
  - No streaming support

### Vector Search Inefficiency
- **Location**: `c_knowledge_base_mapping/vector_database/core/base.py`
- **Current**: IndexFlatIP (brute-force search)
- **Problem**: O(n) search over 2,291 entities, ~0.5s per query
- **Solution**: IndexIVFFlat with clustering (O(log n) search)

### Property Mapping Low Accuracy (25% error rate)
- **Example failures**:
  - "footing depth" → Pset_DoorCommon.Width (expected: Pset_FootingCommon.Depth)
  - Generic properties mapped to wrong domains
- **Root cause**: Insufficient context in property resolution

### Material Facets Missing Constraints (10% error rate)
- **Problem**: Material facets not generating proper constraints
- **Impact**: Material-based specifications fail validation

### PartOf Relationship Extraction Incomplete (5% error rate)
- **Problem**: Hierarchical relationships not fully captured
- **Impact**: Decomposition specifications fail

## Testing & Quality Assurance

### No Automated Testing
- **Current state**: Manual test scripts only
- **Missing**:
  - Unit tests
  - Integration tests
  - CI/CD pipeline
  - Regression testing
- **Risk**: Changes may break existing functionality without detection

### Experimental Results Not Version-Controlled
- **Location**: `ids-algo/experimental_results/`
- **Problem**: Large result files tracked in git
- **Impact**: Repository bloat, merge conflicts
- **Solution needed**: Move to external storage or .gitignore

### No Performance Monitoring
- **Missing**:
  - Real-time performance metrics
  - Memory profiling
  - LLM cost tracking
  - Error rate monitoring

## Configuration & Deployment

### Hardcoded Configuration
- **Problem**: Configuration scattered across multiple files
- **Examples**:
  - LLM endpoints in multiple locations
  - API keys in .env files
  - Model names hardcoded in code
- **Risk**: Difficult to switch between environments

### No Deployment Documentation
- **Missing**:
  - Deployment guide
  - Environment setup instructions
  - Dependency management
  - Production configuration

### API Key Management
- **Current**: .env files with plaintext keys
- **Risk**: Accidental exposure in version control
- **Solution needed**: Secrets management system

## Documentation Gaps

### Bilingual Documentation Inconsistency
- **Problem**: Chinese and English docs out of sync
- **Examples**:
  - README.md vs README_CN.md
  - Code comments mixed languages
- **Impact**: Confusion for international contributors

### Missing API Documentation
- **No documentation for**:
  - REST API endpoints
  - Request/response schemas
  - Error codes
  - Rate limits

### Algorithm Documentation Incomplete
- **Missing details on**:
  - Stage C mapping algorithm specifics
  - Vector similarity thresholds
  - LLM prompt engineering strategies
  - Fallback mechanisms

## Immediate Action Items (Priority Order)

1. **[5 min]** Fix text conversion in `test_large_scale_ids.py`
   - Use `IDSToTextGenerator` instead of simplified extraction
   - Expected: 53.3% → 85%+ match rate

2. **[2 days]** Expand `entity_db.json` with IFC4X3 entities
   - Source: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/
   - Expected: 60% mapping errors eliminated

3. **[1 week]** Implement batch LLM calls + response caching
   - Target: 171s → 100s Stage C time

4. **[1 week]** Optimize vector search with IVF indexing
   - Target: 100s → 50s Stage C time

5. **[2 weeks]** Add unit tests for critical components
   - Focus: Stage C resolvers, text conversion, validation

## Long-term Improvements

### Phase 1: Performance (1-2 months)
- Batch LLM processing
- Response caching
- IVF vector indexing
- Concurrent execution
- Streaming support
- Target: 287s → 100s total time

### Phase 2: Accuracy (2-3 months)
- Complete IFC4X3 entity coverage
- Improved property mapping
- Material facets constraints
- PartOf relationship extraction
- Target: 53.3% → 90%+ match rate

### Phase 3: Production Readiness (3-4 months)
- Automated testing suite
- CI/CD pipeline
- Performance monitoring
- Secrets management
- Deployment documentation
- API documentation

## Risk Assessment

### High Risk
- **Stage C performance**: Blocks production use at scale
- **Requirements loss**: Core functionality failure
- **No testing**: High regression risk

### Medium Risk
- **Entity database gaps**: Limits domain coverage
- **Configuration management**: Deployment complexity
- **Documentation gaps**: Onboarding friction

### Low Risk
- **Code style inconsistencies**: Maintainability impact
- **Bilingual docs sync**: Communication overhead
