# External Integrations

## Overview
The IDS Agent integrates with multiple external services for LLM processing, vector embeddings, database storage, authentication, file uploads, and email delivery.

---

## AI/LLM Services

### Anthropic Claude API
**Purpose**: Primary LLM provider for IDS document processing

**Configuration**:
- Provider: `anthropic`
- Base URL: `https://cc-vibe.com` (custom endpoint)
- Auth Token: `ANTHROPIC_AUTH_TOKEN` (environment variable)
- Models Used:
  - `claude-3-5-sonnet-20241022` - Parser, Classifier, PropertySet selector
  
**Settings** (`.env-pipeline`):
```
LLM_PROVIDER=anthropic
ANTHROPIC_AUTH_TOKEN=sk-d2c34707eb1a890aa86061cd84ccd8574ee13da991963d01459a3e4095744c17
ANTHROPIC_BASE_URL=https://cc-vibe.com
LLM_API_KEY=sk-d2c34707eb1a890aa86061cd84ccd8574ee13da991963d01459a3e4095744c17
LLM_BASE_URL=https://cc-vibe.com
LLM_TIMEOUT=60
```

**Stage-Specific Configuration**:
- **Stage 1 (Parser)**: Temperature 0.1, Max tokens 2048
- **Stage 2 (Classifier)**: Temperature 0.05, Max tokens 1024
- **Stage 4 (PropertySet)**: Temperature 0.0, Max tokens 512

**Implementation**:
- Client: `ids-algo/openrouter/client.py` - `OpenRouterClient` class
- Uses Anthropic SDK with fallback to OpenAI SDK compatibility layer
- Supports both streaming and non-streaming responses

---

### OpenRouter (Backup Provider)
**Purpose**: Alternative LLM provider

**Configuration**:
```
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

**Status**: Currently configured as backup, not actively used

---

## Vector Embedding Services

### Hugging Face Model Hub
**Purpose**: Download and cache transformer models for embeddings

**Models Used**:
- **BAAI/bge-m3** - Primary embedding model
  - Vector dimension: 1024
  - Used for both Entity and Property knowledge bases
  
**Configuration**:
```
ENTITY_EMBEDDING_MODEL=BAAI/bge-m3
PROPERTY_EMBEDDING_MODEL=BAAI/bge-m3
VECTOR_DIM=1024
SEMANTIC_MATCHING_THRESHOLD=0.7
```

**Implementation**:
- Model Manager: `ids-algo/c_knowledge_base_mapping/vector_database/core/model_manager.py`
- Cache Location: `ids-algo/cache/vectors/BAAI_bge-m3/`
- Uses `sentence-transformers` library
- Local caching with disk persistence

**Cache Configuration**:
```
ENABLE_CACHE=true
CACHE_TTL=3600
CACHE_MAX_MEMORY_SIZE=10000
CACHE_DIR=./cache/vectors
CACHE_ENABLE_PERSISTENCE=true
```

---

## Database Services

### MongoDB Atlas
**Purpose**: Primary database for user data, resources, and file metadata

**Connection**:
```
MONGODB_URI=mongodb+srv://haoyuwang:770122@cluster0.maypzsy.mongodb.net/IDS-agent?appName=Cluster0
```

**Collections**:
- `resources` - Task/resource metadata
- `uploads.files` - GridFS file metadata
- `uploads.chunks` - GridFS file chunks
- User authentication data (via better-auth)

**Features Used**:
- GridFS for file storage (IDS files, IFC files, results)
- Document storage for JSON data
- Aggregation pipelines for queries

**Drivers**:
- Python: `pymongo` >= 4.6.0
- Node.js: `mongodb` ^7.0.0, `mongoose` ^8.19.2

---

### FAISS Vector Database
**Purpose**: Local vector similarity search for IFC entities and properties

**Type**: In-memory/disk-persisted vector index

**Implementation**:
- Library: `faiss-cpu` >= 1.7.3
- Base class: `ids-algo/c_knowledge_base_mapping/vector_database/core/base.py`
- Unified DB: `ids-algo/c_knowledge_base_mapping/vector_database/unified_db.py`

**Knowledge Bases**:
- Entity knowledge base (`entity_db.json`)
- Property knowledge base
- Material knowledge base
- Classification knowledge base

**Features**:
- Cosine similarity search
- Top-K retrieval
- IFC version filtering
- Metadata filtering

---

## External APIs

### IFC Entity PropertySet API
**Purpose**: Fetch IFC entity property sets dynamically

**Endpoint**:
```
IFC_ENTITY_PSET_API_URL=http://36.103.199.7:5000/api/property/entity-psets
```

**Request Format**:
```json
{
  "entityName": "IfcWall",
  "schemaVersions": ["IFC4"]
}
```

**Response**: Property sets and properties for the specified entity

**Implementation**:
- Resolver: `ids-algo/c_knowledge_base_mapping/resolvers/property_resolver.py`
- Method: `_fetch_property_sets_from_api()`
- Timeout: 5 seconds
- Fallback: Static knowledge base if API unavailable

**Error Handling**:
- Connection errors logged as warnings
- Graceful degradation to local knowledge base

---

### buildingSMART Data Dictionary (bSDD) - DISABLED
**Purpose**: External classification dictionary (currently disabled)

**Configuration** (commented out):
```
# BSDD_API_URL=https://api.bsdd.buildingsmart.org
# BSDD_LANGUAGE=zh-CN
# BSDD_MAX_RESULTS=5
# ENABLE_BSDD_CLASSIFICATION=true
```

**Status**: Not currently integrated

---

## Authentication Services

### Better Auth
**Purpose**: User authentication and session management

**Configuration** (.env):
```
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Features**:
- Session management
- OAuth integration support
- Password reset functionality

---

### OAuth Providers

#### GitHub OAuth
```
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

#### Google OAuth
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

## File Upload & Storage

### UploadThing
**Purpose**: File upload service for frontend

**Configuration**:
```
UPLOADTHING_TOKEN=your-uploadthing-token-here
```

**Integration**:
- React components: `@uploadthing/react`
- Server SDK: `uploadthing`

**File Types Handled**:
- IFC files (.ifc)
- IDS files (.ids)
- Text documents
- Images (via Sharp processing)

---

### GridFS (MongoDB)
**Purpose**: Backend file storage system

**Collections**:
- `uploads.files` - File metadata
- `uploads.chunks` - File data chunks

**Features**:
- Large file support (>16MB)
- Streaming support
- Metadata storage

**Implementation**:
- Python: `gridfs` module via `pymongo`
- Server: `ids-algo/server.py`

---

## Email Services

### Resend
**Purpose**: Transactional email delivery (password reset, notifications)

**Configuration**:
```
RESEND_API_KEY=re_your-api-key-here
```

**Use Cases**:
- Password reset emails
- Account verification
- System notifications

---

## Rate Limiting

### Upstash Redis
**Purpose**: API rate limiting and request throttling

**Configuration**:
```
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-redis-token-here
```

**Implementation**:
- Library: `@upstash/ratelimit`
- REST API based (no persistent connection)

---

## Image Processing

### Sharp
**Purpose**: Server-side image optimization and transformation

**Version**: 0.32.6 (pinned for stability)

**Features**:
- Image resizing
- Format conversion
- Optimization for web delivery

**Build Configuration**:
- Listed in `onlyBuiltDependencies` for pnpm
- Native binary compilation required

---

## File System Dependencies

### Temporary File Storage
**Purpose**: Temporary storage for IFC validation

**Implementation**:
- Python `tempfile` module
- Created during IFC checking process
- Automatically cleaned up after validation

**Directories**:
- System temp directory (OS-dependent)
- Cleaned up in `finally` blocks

---

### Cache Directories

#### Vector Cache
```
CACHE_DIR=./cache/vectors
```
- Stores embedding vectors
- Organized by model name (BAAI_bge-m3)
- Pickle format (.pkl files)

#### Output Directories
```
OUTPUT_DIR=output
ERROR_LOG_DIR=output/extraction_errors
```

---

## Network Protocols

### HTTP/HTTPS
- FastAPI server: `http://0.0.0.0:8000`
- Next.js dev server: `http://localhost:3000`
- All external APIs use HTTPS

### WebSocket
- Supported via Uvicorn[standard]
- Not currently utilized

---

## Configuration Management

### Environment Files

#### Python Backend (`.env-pipeline`)
- LLM configuration
- Database URIs
- API endpoints
- Feature flags
- Performance settings

#### Node.js Frontend (`.env`)
- MongoDB URI
- Authentication secrets
- OAuth credentials
- Third-party API keys
- Public environment variables (NEXT_PUBLIC_*)

### Settings Management

#### Python
- **pydantic-settings**: Type-safe configuration
- **python-dotenv**: Environment loading
- Settings class: `ids-algo/openrouter/settings.py`

#### Node.js
- **dotenv**: Environment loading
- **cross-env**: Cross-platform env vars
- Next.js built-in env support

---

## CORS Configuration

**Backend CORS** (`.env-pipeline`):
```
CORS_ORIGINS=["*"]
```

**Note**: Should be restricted in production

---

## Security Headers

**Next.js Configuration** (`next.config.mjs`):
- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()

---

## Monitoring & Logging

### Performance Monitoring
```
ENABLE_PERFORMANCE_LOGGING=true
ENABLE_INTERMEDIATE_RESULTS_LOGGING=false
ENABLE_MONITORING=true
MONITORING_REFRESH_INTERVAL=5
STATS_RETENTION_DAYS=30
```

### Health Checks
- Endpoint: `/health`
- Checks: MongoDB, memory, disk, dependencies
- Status codes: 200 (healthy), 503 (degraded)

---

## API Endpoints

### Python Backend (FastAPI)
- **Base**: `http://0.0.0.0:8000`
- **Prefix**: `/api`
- **Endpoints**:
  - `POST /analyze` - File analysis
  - `POST /analyze-text` - Text analysis
  - `POST /check-ifc` - IFC validation
  - `GET /health` - Health check

### Next.js Frontend
- **Base**: `http://localhost:3000` (dev)
- **API Routes**: `/api/*`
- **Server Actions**: App Router based

---

## Deployment Considerations

### Environment Detection
- Vercel deployment detection via `VERCEL_PROJECT_PRODUCTION_URL`
- Fallback to `NEXT_PUBLIC_SERVER_URL`
- Default: `http://localhost:3000`

### Image Optimization
- Remote patterns configured for:
  - Server URL (dynamic)
  - Unsplash images
  - TODO: Add bucket address

---

## Dependencies Summary

### Critical External Services
1. **Anthropic API** - Core LLM functionality
2. **MongoDB Atlas** - Data persistence
3. **Hugging Face** - Model downloads

### Optional Services
1. **OpenRouter** - LLM backup
2. **IFC PropertySet API** - Enhanced property resolution
3. **UploadThing** - File uploads
4. **Resend** - Email delivery
5. **Upstash Redis** - Rate limiting

### Offline Capabilities
- Vector search (FAISS) - Fully offline
- IFC processing (ifcopenshell) - Fully offline
- Static knowledge bases - Fully offline
- Cached embeddings - Offline after first download
