# Technology Stack

## Overview
The IDS Agent project is a full-stack application combining a Next.js frontend with a Python-based AI pipeline backend for IFC/IDS document processing.

---

## Backend (Python)

### Core Language
- **Python 3.12.4**

### Web Framework
- **FastAPI** >= 0.109.0 - Modern async web framework for building APIs
- **Uvicorn[standard]** >= 0.27.0 - ASGI server with WebSocket support

### AI/ML Libraries

#### LLM Integration
- **OpenAI SDK** >= 2.8.1 - Used for both OpenRouter and Anthropic API compatibility
- **Anthropic SDK** - Direct integration with Claude models (imported dynamically)

#### Vector Embeddings & Search
- **sentence-transformers** >= 4.41.0 - Transformer-based sentence embeddings
- **FAISS-CPU** >= 1.7.3 - Facebook AI Similarity Search for vector database
- **PyTorch** <= 2.8.0 - Deep learning framework (dependency for transformers)

### Data Processing & Validation
- **Pydantic** >= 2.12.4 - Data validation and settings management
- **pydantic-settings** >= 2.12.0 - Configuration management
- **python-dotenv** - Environment variable management
- **lxml** >= 0.3.0 - XML processing library

### Database
- **PyMongo** >= 4.6.0 - MongoDB driver for Python
- **GridFS** - MongoDB file storage system (via pymongo)

### IFC/BIM Processing
- **ifcopenshell** - IFC file parsing and manipulation
- **ifctester** - IDS validation against IFC models

### Utilities
- **requests** >= 2.31.0 - HTTP client library
- **python-multipart** - Multipart form data parsing
- **psutil** >= 5.9.0 - System and process monitoring

---

## Frontend (Node.js/TypeScript)

### Core Language & Runtime
- **Node.js** ^18.20.2 || >=20.9.0
- **TypeScript** 5.7.3
- **pnpm** ^9 || ^10 - Package manager

### Framework
- **Next.js** 15.3.2 - React framework with App Router
- **React** 19.1.0
- **React DOM** 19.1.0

### UI Libraries

#### Component Libraries
- **@radix-ui/react-checkbox** ^1.3.3
- **@radix-ui/react-label** ^2.1.8
- **@radix-ui/react-slot** ^1.2.4

#### Styling
- **Tailwind CSS** ^3.4.0 - Utility-first CSS framework
- **tailwindcss-animate** ^1.0.7 - Animation utilities
- **tailwind-merge** ^3.3.1 - Merge Tailwind classes
- **class-variance-authority** ^0.7.1 - Component variants
- **clsx** ^2.1.1 - Conditional class names
- **@tailwindcss/typography** ^0.5.16 - Typography plugin
- **PostCSS** ^8.5.6 - CSS processing
- **Autoprefixer** ^10.4.0 - CSS vendor prefixing

#### Icons & Fonts
- **lucide-react** ^0.553.0 - Icon library
- **react-icons** ^5.5.0 - Additional icons
- **geist** ^1.4.2 - Vercel's font family

#### Animation
- **framer-motion** ^12.23.24 - Animation library

### Database & Backend Integration
- **MongoDB** ^7.0.0 - MongoDB Node.js driver
- **Mongoose** ^8.19.2 - MongoDB ODM

### Authentication & Security
- **better-auth** ^1.3.34 - Authentication library
- **zod** ^3.23.8 - Schema validation

### File Upload & Storage
- **uploadthing** ^7.7.4 - File upload service
- **@uploadthing/react** ^7.3.3 - React components for UploadThing
- **sharp** 0.32.6 - Image processing

### Rate Limiting
- **@upstash/ratelimit** ^2.0.8 - Redis-based rate limiting

### Email
- **resend** ^6.9.4 - Email API service

### UI/UX
- **sonner** ^2.0.7 - Toast notifications

### Utilities
- **dotenv** 16.4.7 - Environment variables
- **cross-env** ^7.0.3 - Cross-platform environment variables

---

## Development Tools

### Python Development
- **Virtual Environment** - Located at `ids-algo/venv/`
- **Environment Configuration** - `.env-pipeline` for Python backend

### Node.js Development

#### Linting & Formatting
- **ESLint** ^8 - JavaScript/TypeScript linter
- **eslint-config-next** ^15.0.3 - Next.js ESLint config
- **eslint-config-prettier** ^9.1.0 - Prettier integration
- **@next/eslint-plugin-next** ^15.0.3 - Next.js specific rules
- **eslint-plugin-import** - Import/export validation
- **eslint-plugin-jsx-a11y** - Accessibility linting
- **eslint-plugin-react** - React specific rules
- **Prettier** ^3.4.1 - Code formatter
- **prettier-plugin-tailwindcss** ^0.6.9 - Tailwind class sorting
- **@trivago/prettier-plugin-sort-imports** ^4.3.0 - Import sorting

#### TypeScript
- **@types/node** ^22.5.4
- **@types/react** 19.1.0
- **@types/react-dom** 19.1.2
- **tsx** ^4.19.2 - TypeScript execution

#### Style Guide
- **@vercel/style-guide** ^6.0.0 - Vercel's style guide

---

## Build Tools

### Python
- **pip** - Package installer (standard)
- **setuptools** - Build system (via venv)

### Node.js
- **Next.js Compiler** - Built-in SWC-based compiler
- **@swc/helpers** ^0.5.15 - SWC runtime helpers
- **esbuild** - Fast JavaScript bundler (via Next.js)

---

## Configuration Files

### Python
- `requirements.txt` - Python dependencies
- `.env-pipeline` - Backend environment configuration
- `.envrc` - Directory environment setup

### Node.js/TypeScript
- `package.json` - Node.js dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `next.config.mjs` - Next.js configuration
- `.eslintrc.cjs` - ESLint configuration
- `.prettierrc` - Prettier configuration
- `components.json` - UI components configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration

### Environment
- `.env` - Frontend environment variables
- `.env.example` - Environment template
- `.npmrc` - npm configuration
- `.gitignore` - Git ignore rules

---

## Runtime Requirements

### Python Backend
- Python 3.12.4
- CUDA support optional (for GPU acceleration with PyTorch)
- Minimum 8GB RAM recommended for vector operations

### Node.js Frontend
- Node.js 18.20.2+ or 20.9.0+
- pnpm 9+ or 10+
- 8GB RAM recommended for Next.js build

---

## Package Managers

### Python
- **pip** - Standard Python package installer
- **venv** - Virtual environment management

### Node.js
- **pnpm** - Primary package manager (workspace support)
- Configured with `onlyBuiltDependencies`: sharp, esbuild, unrs-resolver
