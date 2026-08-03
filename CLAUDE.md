@AGENTS.md

# Fork-Specific Additions

This fork extends upstream LightRAG with a 3D knowledge graph viewer and interactive query activations.

## 3D Knowledge Graph Visualization

Standalone Three.js-based 3D viewer at `/graph3d/viewer` that renders the knowledge graph as a galaxy-like point cloud.

**Backend route** (`lightrag/api/routers/graph3d_routes.py`):
- `GET /graph3d/status` — layout computation status
- `GET /graph3d/layout.bin` — binary layout (positions + clusters + IDs)
- `GET /graph3d/layout_meta.json` — entity metadata + edges
- `GET /graph3d/viewer` — standalone HTML viewer page
- `GET /graph3d/insights` — research insights about the graph
- `GET /graph3d/clusters` — cluster analysis for all clusters

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

**Query activation system**:
- Query activations coexist (max 6 concurrent) with 60-second fade-out, color-differentiated through a 10-color palette
- Backend records activations in `lightrag/api/routers/query_routes.py` (60-second TTL); frontend polls `/query/activations` for external queries
- Manual submissions advance the polling watermark to avoid double-processing

See `docs/3d_visualization.md` for full documentation.

## Frontend Debugging

For WebUI bugs that only surface in rendered DOM (layout/overflow/scrollbar issues, transient flashes), drive the running dev server (`http://localhost:5173`) with Playwright. Seed state via `localStorage` (key: `settings-storage`, schema in `lightrag_webui/src/stores/settings.ts`) to skip live LLM calls. Use `wait_until="domcontentloaded"` plus selector wait—Vite dev's polling makes `networkidle` time out.

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
