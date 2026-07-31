# Quick Start: Deploy 3D Graph to Production (Port 9621)

## The Fast Way (Recommended)

```bash
cd /data/workspace/lightrag_all/LightRAG
./deploy_3d_graph.sh
```

That's it! The script will:
1. Copy all 3D graph files to the container
2. Restart the container
3. Show you next steps

## Manual Deployment

If you prefer manual control:

```bash
# 1. Copy files
docker cp lightrag/api/routers/graph3d_routes.py hua-lightrag:/app/lightrag/api/routers/
docker cp lightrag/api/static/graph3d_viewer.html hua-lightrag:/app/lightrag/api/static/
docker cp lightrag/tools/compute_3d_layout.py hua-lightrag:/app/lightrag/tools/

# 2. Restart
docker restart hua-lightrag

# 3. Wait 10 seconds, then test
curl http://localhost:9621/graph3d/viewer
```

## Compute 3D Layout (Required)

After deployment, compute the layout:

```bash
# Using the deployment script's suggestion
docker exec hua-lightrag python -m lightrag.tools.compute_3d_layout --working-dir /app/data/rag_storage
```

**Or** use the existing layout files if already computed:

```bash
# Copy existing layout files into container
docker cp data/rag_storage/graph3d_layout.bin hua-lightrag:/app/data/rag_storage/
docker cp data/rag_storage/graph3d_layout_meta.json hua-lightrag:/app/data/rag_storage/
```

## Access the Viewer

Open in browser:
```
http://your-server:9621/graph3d/viewer
```

## Test It

1. Wait for graph to load (197k entities, ~2-3 seconds)
2. Enter query: `testosterone`
3. Press Enter
4. Watch the neurons activate!

## Verify Deployment

Check if files are in the container:
```bash
docker exec hua-lightrag ls -la /app/lightrag/api/routers/graph3d_routes.py
docker exec hua-lightrag ls -la /app/lightrag/api/static/graph3d_viewer.html
```

Check server logs:
```bash
docker logs hua-lightrag | grep graph3d
```

## Troubleshooting

**Viewer not accessible?**
- Check container is running: `docker ps | grep hua-lightrag`
- Check port mapping: `docker port hua-lightrag`
- Check logs: `docker logs hua-lightrag`

**Layout files not found?**
- Compute layout (see above)
- Or copy existing layout files into container

**Query returns no results?**
- Check LLM is configured in `.env`
- Verify data exists in container
- Check server logs for errors

## What's Deployed

- **Backend**: `/app/lightrag/api/routers/graph3d_routes.py`
- **Frontend**: `/app/lightrag/api/static/graph3d_viewer.html`
- **Tool**: `/app/lightrag/tools/compute_3d_layout.py`
- **Routes**: Automatically registered at `/graph3d/*`

## Features

- ✅ 3D galaxy visualization (197k entities)
- ✅ Neuron activation on query
- ✅ Query log panel
- ✅ Demo activation button
- ✅ Edges between activated entities
- ✅ Persistent activation (until next query)
- ✅ Cluster-based coloring
- ✅ Interactive camera controls

## Next Steps

1. Deploy to production ✅
2. Compute layout (if needed)
3. Test the viewer
4. Customize colors/sizes in `graph3d_viewer.html`
5. Share with your team!

---

**Need help?** See `DEPLOY_3D_GRAPH.md` for detailed documentation.
