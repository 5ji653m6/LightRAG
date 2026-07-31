# 3D Knowledge Graph Visualization - Deployment Guide

## Overview

The 3D Knowledge Graph visualization is a standalone Three.js-based viewer that renders the knowledge graph as a galaxy-like point cloud with interactive neuron activation effects.

## Files to Incorporate

The following files implement the 3D graph feature:

### 1. Backend Routes
**File**: `lightrag/api/routers/graph3d_routes.py`
- Provides REST API endpoints for 3D layout data
- Endpoints:
  - `GET /graph3d/status` - Layout computation status
  - `GET /graph3d/layout.bin` - Binary layout data (positions, clusters, IDs)
  - `GET /graph3d/layout_meta.json` - Entity metadata and edges
  - `GET /graph3d/viewer` - Standalone HTML viewer page

### 2. Frontend Viewer
**File**: `lightrag/api/static/graph3d_viewer.html`
- Standalone HTML/JS/CSS 3D viewer using Three.js 0.160
- Features:
  - WebGL point cloud rendering with UnrealBloomPass
  - OrbitControls for camera navigation
  - Cluster-based coloring (10 colors)
  - Hover tooltips and click-for-details
  - Query panel for neuron activation
  - Activation log panel showing query results
  - Demo activation button

### 3. Layout Computation Tool
**File**: `lightrag/tools/compute_3d_layout.py`
- Command-line tool to compute 3D layout from entity embeddings
- Uses UMAP for dimensionality reduction (3840-dim → 3D)
- Uses KMeans for clustering (50 clusters)
- Outputs binary layout file and metadata JSON

### 4. Server Integration
**File**: `lightrag/api/lightrag_server.py` (already integrated)
- Lines 69, 2306: Imports and registers graph3d routes
- Automatically serves 3D viewer at `/graph3d/viewer`

## Deployment Steps for Production (Port 9621)

### Option A: Rebuild Docker Image (Recommended)

1. **Ensure all files are committed to the repository**:
   ```bash
   cd /data/workspace/lightrag_all/LightRAG
   git add lightrag/api/routers/graph3d_routes.py
   git add lightrag/api/static/graph3d_viewer.html
   git add lightrag/tools/compute_3d_layout.py
   git add lightrag/api/lightrag_server.py
   git commit -m "feat: add 3D knowledge graph visualization with neuron activation"
   git push
   ```

2. **Rebuild the Docker image**:
   ```bash
   cd /data/workspace/lightrag_all/LightRAG
   docker-compose -f docker-compose-full.yml build --no-cache
   ```

3. **Restart the container**:
   ```bash
   docker-compose -f docker-compose-full.yml down
   docker-compose -f docker-compose-full.yml up -d
   ```

4. **Compute 3D layout** (inside container or on host):
   ```bash
   # Option 1: Using the script directly
   docker exec hua-lightrag python -m lightrag.tools.compute_3d_layout --working-dir /path/to/rag_storage
   
   # Option 2: From host with proper Python environment
   source .venv-graph3d/bin/activate
   lightrag-compute-3d-layout --working-dir data/rag_storage
   ```

5. **Verify the deployment**:
   - Access viewer: http://your-server:9621/graph3d/viewer
   - Test query: Enter "test" in query panel
   - Check activation: Entities should pulse bright white

### Option B: Manual File Copy (Quick Update)

If you want to update without rebuilding:

1. **Copy files into running container**:
   ```bash
   # Copy router
   docker cp lightrag/api/routers/graph3d_routes.py hua-lightrag:/app/lightrag/api/routers/
   
   # Copy viewer
   docker cp lightrag/api/static/graph3d_viewer.html hua-lightrag:/app/lightrag/api/static/
   
   # Copy tool (if needed)
   docker cp lightrag/tools/compute_3d_layout.py hua-lightrag:/app/lightrag/tools/
   ```

2. **Restart the container**:
   ```bash
   docker restart hua-lightrag
   ```

3. **Compute layout** (see Option A step 4)

## Layout Computation Requirements

### Dependencies
The layout computation requires additional packages:
```bash
# Create separate venv to avoid conflicts
uv venv .venv-graph3d --python 3.12
uv pip install umap-learn numpy networkx --python .venv-graph3d/bin/python
source .venv-graph3d/bin/activate
```

### Computation Time
- **~200k entities**: 30-60 minutes
- **~50k entities**: 10-15 minutes
- **~10k entities**: 2-5 minutes

### Output Files
- `graph3d_layout.bin` - Binary layout (11 MB for 197k entities)
- `graph3d_layout_meta.json` - Metadata (110 MB for 197k entities)

### Memory Requirements
- **~200k entities**: ~8GB RAM during computation
- **~50k entities**: ~2GB RAM
- **~10k entities**: ~500MB RAM

## Usage

### Viewing the 3D Graph
1. Navigate to `http://your-server:9621/graph3d/viewer`
2. Wait for graph to load (2-3 seconds)
3. Use mouse to navigate:
   - **Left click + drag**: Rotate
   - **Right click + drag**: Pan
   - **Scroll**: Zoom in/out

### Querying and Activation
1. Enter query in the input field (bottom-left)
2. Press Enter or click "Query"
3. Watch the log panel (bottom-right) for results
4. Activated entities pulse bright white for 2 seconds, then stay bright
5. Edges between activated entities glow white
6. Next query clears previous activation

### Demo Mode
- Click "⚡ Demo Activation" button
- Activates 10 random entities
- Good for testing the visual effect

## Configuration

### Adjusting Visual Parameters

Edit `lightrag/api/static/graph3d_viewer.html`:

```javascript
// Point size (default: 0.012)
const POINT_SIZE = 0.012;

// Bloom effect (default: strength=0.6, radius=0.4, threshold=0.3)
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(width, height),
  0.6,  // strength
  0.4,  // radius
  0.3   // threshold
);

// Cluster colors (10 colors, can be customized)
const CLUSTER_COLORS = [
  0x2a5a9f, 0x6835a7, 0x0a7951, 0x956e0b, 0x8f2424,
  0x047684, 0x5b3c96, 0x547c0e, 0x99550e, 0x942c5f
];
```

### Adjusting Query Parameters

In `queryAndActivate()` function:

```javascript
body: JSON.stringify({
  query: queryText,
  mode: 'hybrid',      // Options: local, global, hybrid, mix, naive
  top_k: 20,           // Number of entities to retrieve
  chunk_top_k: 10      // Number of chunks to retrieve
})
```

## Troubleshooting

### Viewer Shows Empty Galaxy
- **Cause**: Layout files not found
- **Solution**: Ensure `graph3d_layout.bin` and `graph3d_layout_meta.json` exist in the working directory

### Query Returns No Results
- **Cause**: LLM not configured or data not loaded
- **Solution**: 
  1. Check `.env` file has LLM configuration
  2. Verify data exists in `rag_storage/`
  3. Check server logs for errors

### Activation Not Visible
- **Cause**: Entities not found in point cloud
- **Solution**: 
  1. Check browser console for "Entities not found" message
  2. Entity names from query may not match exact names in visualization
  3. Try different query terms

### Layout Computation Fails
- **Cause**: Insufficient memory or missing dependencies
- **Solution**:
  1. Ensure umap-learn is installed: `pip install umap-learn`
  2. Check available RAM (need ~8GB for 200k entities)
  3. Reduce dataset size or use subset

## Performance Optimization

### For Large Graphs (>100k entities)

1. **Reduce point size**:
   ```javascript
   const POINT_SIZE = 0.008;
   ```

2. **Disable edges by default**:
   ```javascript
   let showEdges = false;
   ```

3. **Increase bloom threshold**:
   ```javascript
   const bloomPass = new UnrealBloomPass(..., 0.5);
   ```

4. **Use edge performance limit**:
   ```javascript
   const EDGE_PERF_LIMIT = 100000; // Only show edges if < 100k
   ```

### Browser Recommendations
- **Chrome/Edge**: Best performance with WebGL
- **Firefox**: Good, but slightly slower
- **Safari**: May have issues with large graphs

## Future Enhancements

Potential improvements:
- [ ] Label rendering with CSS2DRenderer
- [ ] Entity type filtering
- [ ] Time-based animation
- [ ] Export activated subgraph
- [ ] Share query results
- [ ] Multi-query comparison
- [ ] Virtual scrolling for very large graphs

## Support

For issues or questions:
1. Check server logs: `docker logs hua-lightrag`
2. Check browser console (F12) for JavaScript errors
3. Verify layout files exist and are not corrupted
4. Test with demo activation first

## References

- Three.js Documentation: https://threejs.org/docs/
- UMAP Paper: https://arxiv.org/abs/1802.03426
- LightRAG Documentation: `/data/workspace/lightrag_all/LightRAG/docs/`
