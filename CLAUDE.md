# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LightRAG is a graph-based Retrieval-Augmented Generation (RAG) framework that extracts entities and relationships from documents, builds a knowledge graph, and uses multiple retrieval modes (local, global, hybrid, mix, naive) for queries. It serves as an efficient alternative to Microsoft GraphRAG with dual-layer architecture managing both knowledge graphs and vector embeddings.

## Development Commands

### Setup and Installation

```bash
# Bootstrap development environment (recommended)
make dev

# Or manual setup with uv
uv sync --extra test --extra offline
source .venv/bin/activate

# Configure environment
make env-base           # LLM, embedding, reranker (required first step)
make env-storage        # Storage backends (optional)
make env-server         # Server port, auth, SSL (optional)

# Build frontend
cd lightrag_webui && bun install --frozen-lockfile && bun run build && cd ..
```

### Running the Server

```bash
# Production server
lightrag-server

# Development with hot reload
uvicorn lightrag.api.lightrag_server:app --reload

# Multi-worker production
lightrag-gunicorn
```

### Testing

```bash
# Run full test suite (preferred)
./scripts/test.sh tests

# Run specific test file
./scripts/test.sh tests/kg/test_graph_storage.py

# Run with custom workers
./scripts/test.sh tests --test-workers 4

# Direct pytest (if needed)
pytest tests/
pytest tests/kg/test_graph_storage.py -v
```

**Test organization**: Tests mirror the source structure under `tests/`. Backend tests use `tests/kg/<backend>_impl/` with `_impl` suffix to avoid import shadowing. Markers: `offline`, `integration`, `requires_db`, `requires_api`. Integration tests skipped by default.

### Linting

```bash
ruff check .
```

### WebUI Development

```bash
cd lightrag_webui
bun install --frozen-lockfile
bun run dev          # Dev server
bun run build        # Production build
bun test             # Frontend tests (Bun runner, NOT Vitest/Jest)
bun run lint         # ESLint
```

## Architecture

### Core Class Composition

`LightRAG` is assembled from focused mixins:

```
LightRAG → _RoleLLMMixin → _StorageMigrationMixin → _PipelineMixin → object
```

The `@final` decorator is preserved—mixin layering is internal, not for subclassing. Public API (`ainsert`, `aquery`, `initialize_storages`, etc.) is unchanged.

**Critical initialization pattern**:

```python
rag = LightRAG(working_dir="./storage", ...)
await rag.initialize_storages()  # REQUIRED - omitting causes AttributeError/KeyError
# ... use rag ...
await rag.finalize_storages()
```

### Storage Layer

Four storage types with pluggable backends:

- **KV_STORAGE**: LLM cache, text chunks, document info
- **VECTOR_STORAGE**: Entity/relation/chunk embeddings
- **GRAPH_STORAGE**: Entity-relation graph
- **DOC_STATUS_STORAGE**: Document processing status

Backend implementations in `lightrag/kg/`. Registry in `kg/__init__.py`; factory in `kg/factory.py`.

**Workspace isolation**: Each instance can use a `workspace` parameter for data separation. Implementation varies:
- File-based: subdirectories under `working_dir`
- Collection-based: collection name prefixes
- Relational DB: workspace column filtering
- Qdrant: payload-based partitioning

### Document Ingestion Pipeline

The pipeline coordinates concurrent writers through `pipeline_status` (shared dict in `lightrag.kg.shared_storage`). Key fields:

- **busy**: Pipeline-busy state (set by processing loop AND destructive jobs)
- **destructive_busy**: True during `/documents/clear` or delete operations (blocks enqueue)
- **scanning**: `/documents/scan` running (whole lifecycle)
- **scanning_exclusive**: True during scan's classification phase (blocks enqueue)
- **pending_enqueues**: Count of reserved upload slots

**Concurrency contract**: Mutual exclusion checked atomically via `get_namespace_lock("pipeline_status", workspace=...)`. The contract permits concurrent enqueue + processing—freshly uploaded docs land in `doc_status` while the loop is mid-batch.

**FAILED retry semantics**: Automatic runs resume only PENDING + PROCESSING/PARSING/ANALYZING orphans. FAILED docs re-enter exclusively through sticky manual retry requests (one attempt per request). All scheduling queries use `get_docs_by_statuses(..., strict=True)`.

### Query Modes

- **local**: Context-dependent retrieval focused on specific entities
- **global**: Community/summary-based broad knowledge retrieval
- **hybrid**: Combines local and global
- **naive**: Direct vector search without graph
- **mix**: Integrates KG and vector retrieval (recommended with reranker)

### Role-Specific LLM Configuration

Four LLM roles with independent configuration:

- **EXTRACT**: Entity-relation extraction (fast, non-thinking model recommended)
- **QUERY**: Final answer generation from retrieved context (stronger model)
- **KEYWORD**: Query keyword extraction (lightweight, non-thinking model)
- **VLM**: Multimodal image analysis

Configuration via `ROLES` registry in `llm_roles.py`.

### Module Structure

- **lightrag.py**: Main orchestrator class with `ainsert`, `aquery`, `ainsert_custom_kg`
- **pipeline.py**: Document ingestion (`apipeline_enqueue_documents`, `apipeline_process_enqueue_documents`)
- **operate.py**: Core extraction and query operations
- **base.py**: Abstract base classes for storage backends
- **llm_roles.py**: Role-specific LLM configuration and management
- **kg/**: Storage implementations (JSON, NetworkX, Neo4j, PostgreSQL, MongoDB, Redis, Milvus, Qdrant, Faiss, Memgraph, OpenSearch)
- **llm/**: LLM provider bindings (OpenAI, Ollama, Azure, Gemini, Bedrock, Anthropic, etc.)
- **parser/**: Unified parsing layer with routing for legacy/native/mineru/docling engines
- **chunker/**: Chunking strategies (token-size, recursive, semantic, paragraph)
- **api/**: FastAPI service with REST endpoints and Ollama-compatible API

### WebUI Architecture (`lightrag_webui/`)

React 19 + TypeScript frontend with Vite bundler and Bun runtime.

**Tech Stack**:
- **Framework**: React 19 with functional components and hooks
- **Build tool**: Vite 8 with Bun (fallback to Node.js/npm supported)
- **Styling**: Tailwind CSS 4 with utility-first approach
- **State management**: Zustand 5 (stores in `src/stores/`)
- **Graph visualization**: Sigma.js 3 + react-sigma 5 for knowledge graph rendering
- **UI components**: Radix UI primitives + shadcn/ui patterns
- **Routing**: React Router 7
- **i18n**: react-i18next with multi-language support
- **Tables**: TanStack React Table 8
- **Markdown**: react-markdown with KaTeX math rendering

**Directory Structure** (`lightrag_webui/src/`):
- **features/**: Major feature components (DocumentManager, GraphViewer, RetrievalView, ApiSite, SiteHeader, LoginPage)
- **components/**: Reusable UI components organized by domain
  - `ui/`: Base UI primitives (Button, Card, Dialog, Table, Tabs, etc.)
  - `documents/`: Document upload, delete, clear, pipeline status dialogs
  - `graph/`: Graph visualization controls (search, layout, zoom, properties, legend, merge)
  - `retrieval/`: Query settings, chat message components
  - `status/`: Backend health status indicators
- **stores/**: Zustand state stores (settings, state, graph)
- **api/**: API client layer (`lightrag.ts` - backend REST API calls)
- **services/**: Business logic services (navigation, etc.)
- **hooks/**: Custom React hooks (useDebounce, useIsDarkMode, etc.)
- **lib/**: Utilities, constants, helper functions
- **locales/**: i18n translation files
- **types/**: TypeScript type definitions
- **contexts/**: React contexts (TabVisibilityProvider)

**Main Application Views** (tab-based navigation):
1. **Documents**: Document management (upload, delete, clear, status tracking, pipeline monitoring)
2. **Knowledge Graph**: Interactive graph visualization with Sigma.js (search, layout algorithms, node/edge properties, zoom, fullscreen)
3. **Retrieval**: Query interface with chat-like message display, streaming responses, LaTeX rendering, chain-of-thought support
4. **API**: Swagger/OpenAPI documentation embedded

**State Management Pattern**:
```typescript
// Zustand store with selector pattern
import { useSettingsStore } from '@/stores/settings'
const currentTab = useSettingsStore.use.currentTab()
const setCurrentTab = useSettingsStore.use.setCurrentTab()
```

**Key UI Components**:
- **SiteHeader**: Tab navigation, version display, logout, theme/language toggles
- **DocumentManager**: Table-based document list with status filtering, pagination, bulk operations
- **GraphViewer**: Sigma container with controls (layout, zoom, search, properties panel, legend)
- **RetrievalView**: Chat interface with streaming, query settings panel, message history

**Graph Visualization**:
- Sigma.js settings configured in `createSigmaSettings()` (theme-aware, performance-tuned)
- Node types: `border` (default with white ring), `circle`, `point`
- Edge types: `rect` (default), `line`, `arrow`, `curvedArrow`
- Performance: `hideEdgesOnMove: true`, `EDGE_PERF_LIMIT` threshold for large graphs
- Layout algorithms: force, forceatlas2, circular, circlepack, random, noverlap

**Build Output**: Production build outputs to `lightrag/api/webui/` for FastAPI serving.

### 3D Knowledge Graph Visualization

Standalone Three.js-based 3D viewer at `/graph3d/viewer` that renders the knowledge graph as a galaxy-like point cloud.

**Backend route** (`lightrag/api/routers/graph3d_routes.py`):
- `GET /graph3d/status` — layout computation status
- `GET /graph3d/layout.bin` — binary layout (positions + clusters + IDs)
- `GET /graph3d/layout_meta.json` — entity metadata + edges
- `GET /graph3d/viewer` — standalone HTML viewer page

**Layout computation** (`lightrag/tools/compute_3d_layout.py`):
```bash
# Requires umap-learn (install in a separate venv)
uv venv .venv-graph3d --python 3.12
uv pip install umap-learn numpy networkx --python .venv-graph3d/bin/python
source .venv-graph3d/bin/activate

# Compute layout (30-60 min for ~200k entities)
lightrag-compute-3d-layout --working-dir data/rag_storage
```

Vector decoding: LightRAG stores entity embeddings as zlib-compressed, base64-encoded float16 arrays (3840-dim, unit-normalized).

**Frontend** (`lightrag/api/static/graph3d_viewer.html`): Three.js 0.160 via CDN, WebGL points with UnrealBloomPass, OrbitControls, cluster-based coloring, hover tooltips, click-for-details panel.

See `docs/3d_visualization.md` for full documentation.

### Research Reproduction

The `reproduce/` directory contains scripts for reproducing the evaluation results from the LightRAG paper:

- **Step_0.py**: Extract unique contexts from datasets
- **Step_1.py** / **Step_1_openai_compatible.py**: Generate high-level queries from dataset descriptions
- **Step_2.py**: Run RAG systems and collect answers
- **Step_3.py** / **Step_3_openai_compatible.py**: Pairwise evaluation of answers
- **batch_eval.py**: Batch evaluation comparing LightRAG against baselines (NaiveRAG, RQ-RAG, HyDE, GraphRAG)

Dataset: [TommyChien/UltraDomain](https://huggingface.co/datasets/TommyChien/UltraDomain) on HuggingFace. Evaluation metrics: Comprehensiveness, Diversity, Empowerment. See `docs/Reproduce.md` for full methodology.

The `realdeepresearch.github.io/` directory contains the static website for the "Real Deep Research" project showcase (HTML + assets).

## Key Implementation Patterns

### Custom Embedding Functions

Use `@wrap_embedding_func_with_attrs` decorator. When wrapping already-decorated functions, access the underlying via `.func`:

```python
from lightrag.utils import wrap_embedding_func_with_attrs

@wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8192)
async def custom_embed(texts: list[str]) -> np.ndarray:
    return await openai_embed.func(texts, model="text-embedding-3-large")
```

**Pitfall**: Switching embedding models requires clearing the data directory (except `kv_store_llm_response_cache.json`). Existing vectors won't match the new model's space.

### Storage Configuration

```python
rag = LightRAG(
    working_dir="./storage",
    workspace="project_name",
    kv_storage="PGKVStorage",
    vector_storage="PGVectorStorage",
    graph_storage="Neo4JStorage",
    doc_status_storage="PGDocStatusStorage",
    vector_db_storage_cls_kwargs={"cosine_better_than_threshold": 0.2}
)
```

### Document Operations

```python
# Insert
await rag.ainsert("Text content")
await rag.ainsert(["Text 1", "Text 2"], file_paths=["doc1.pdf", "doc2.pdf"])

# Query
result = await rag.aquery(
    "Your question",
    param=QueryParam(
        mode="mix",
        top_k=60,
        chunk_top_k=20,
        enable_rerank=True
    )
)
```

## Configuration

### Environment Variables

Primary configuration via `.env` file. Generate with `make env-base` or copy `env.example`. Key sections:

- Server settings (HOST, PORT, CORS)
- Storage backends (connection strings)
- Query parameters (TOP_K, MAX_TOTAL_TOKENS)
- Reranking (RERANK_BINDING, RERANK_MODEL)
- Authentication (AUTH_ACCOUNTS, LIGHTRAG_API_KEY)

**Setup wizard outputs**:
- `.env` should remain host-usable (no container-only hostnames)
- `docker-compose.final.yml` is generated from `scripts/setup/templates/*.yml`
- Prefer `make env-*` targets over direct `scripts/setup/setup.sh` calls

### Concurrency Tuning

For large-scale document processing:

- **MAX_ASYNC_LLM**: Max LLM concurrency
- **MAX_PARALLEL_INSERT**: Max files processed in parallel (~1/3 of MAX_ASYNC_LLM)
- **EMBEDDING_FUNC_MAX_ASYNC**: Max embedding concurrency
- **EMBEDDING_BATCH_NUM**: Texts per embedding request

## Code Style

### Python

- PEP 8 with 4-space indentation
- Type annotations on all function signatures
- Use dataclasses for state management
- Use `lightrag.utils.logger` instead of print
- Async/await patterns throughout
- Comments, log messages, and Git commits in English

### TypeScript / React (WebUI)

- Functional components with hooks
- PascalCase for components
- 2-space indentation, single quotes
- Tailwind utility-first styling
- ESLint: TypeScript-ESLint + React Hooks plugin + Prettier
- `@typescript-eslint/no-explicit-any` is disabled (allowed)

## Testing Guidelines

- Use mock-based tests for external services (Redis, httpx, etc.)—no live service dependencies in unit tests
- Add regression tests for every bug fix
- Run full test suite and report pass counts before declaring done
- Backend tests: pytest; Frontend tests: Bun's built-in runner (NOT Vitest/Jest)
- Integration tests skipped by default (`-m "not integration"`)
- Integration env vars: `LIGHTRAG_RUN_INTEGRATION=true`, `LIGHTRAG_KEEP_ARTIFACTS=true`, `LIGHTRAG_TEST_WORKERS=4`

## Frontend Debugging

For WebUI bugs that only surface in rendered DOM (layout/overflow/scrollbar issues, transient flashes), drive the running dev server (`http://localhost:5173`) with Playwright. Seed state via `localStorage` (key: `settings-storage`, schema in `lightrag_webui/src/stores/settings.ts`) to skip live LLM calls. Use `wait_until="domcontentloaded"` plus selector wait—Vite dev's polling makes `networkidle` time out.

## Git Workflow

- Commit messages in English (repository artifacts, not conversational replies)
- PR descriptions: summary, motivation, linked issues, what's changed, what's broken
- If this is a fork of `HKUDS/LightRAG`, target PRs to `HKUDS/LightRAG`, not the fork's repo

## PM2 Services

| Port | Name | Type |
|------|------|------|
| 9622 | lightrag-9622 | Python/FastAPI |

**Terminal Commands:**
```bash
pm2 start ecosystem.config.cjs   # First time
pm2 start all                    # After first time
pm2 stop all / pm2 restart all
pm2 start lightrag-9622 / pm2 stop lightrag-9622
pm2 logs / pm2 status / pm2 monit
pm2 save                         # Save process list
pm2 resurrect                    # Restore saved list
```
