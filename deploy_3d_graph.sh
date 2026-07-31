#!/bin/bash
# Deploy 3D Graph Visualization to Production (Port 9621)

set -e

CONTAINER_NAME="hua-lightrag"
SOURCE_DIR="/data/workspace/lightrag_all/LightRAG"

echo "🚀 Deploying 3D Graph Visualization to $CONTAINER_NAME..."

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    exit 1
fi

echo "✅ Container is running"

# Copy files
echo "📋 Copying files to container..."

echo "  - Copying graph3d_routes.py..."
docker cp "$SOURCE_DIR/lightrag/api/routers/graph3d_routes.py" "$CONTAINER_NAME:/app/lightrag/api/routers/"

echo "  - Copying graph3d_viewer.html..."
docker cp "$SOURCE_DIR/lightrag/api/static/graph3d_viewer.html" "$CONTAINER_NAME:/app/lightrag/api/static/"

echo "  - Copying compute_3d_layout.py..."
docker cp "$SOURCE_DIR/lightrag/tools/compute_3d_layout.py" "$CONTAINER_NAME:/app/lightrag/tools/"

echo "✅ Files copied successfully"

# Restart container
echo "🔄 Restarting container..."
docker restart "$CONTAINER_NAME"

echo "✅ Container restarted"

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 10

# Check if server is responding
if curl -s http://localhost:9621/health > /dev/null 2>&1; then
    echo "✅ Server is responding"
else
    echo "⚠️  Server may still be starting. Check logs: docker logs $CONTAINER_NAME"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Compute 3D layout (if not already done):"
echo "   docker exec $CONTAINER_NAME python -m lightrag.tools.compute_3d_layout --working-dir /app/data/rag_storage"
echo ""
echo "2. Access the viewer:"
echo "   http://localhost:9621/graph3d/viewer"
echo ""
echo "3. Test the activation:"
echo "   - Enter a query like 'testosterone' or 'diabetes'"
echo "   - Watch the neurons activate!"
echo ""
