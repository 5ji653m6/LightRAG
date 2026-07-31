#!/bin/bash
# Deploy real-time activation fix

set -e

CONTAINER_NAME="hua-lightrag"
SOURCE_DIR="/data/workspace/lightrag_all/LightRAG"

echo "🚀 Deploying real-time activation fix..."

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    exit 1
fi

echo "✅ Container is running"

# Copy files
echo "📋 Copying files to container..."

echo "  - Copying query_routes.py (with dict access fix)..."
docker cp "$SOURCE_DIR/lightrag/api/routers/query_routes.py" "$CONTAINER_NAME:/app/lightrag/api/routers/"

echo "  - Copying graph3d_viewer.html (with polling)..."
docker cp "$SOURCE_DIR/lightrag/api/static/graph3d_viewer.html" "$CONTAINER_NAME:/app/lightrag/api/static/"

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
echo "🧪 Test it:"
echo "1. Open http://localhost:9621/graph3d/viewer in browser"
echo "2. Watch for: '🔄 Real-time activation monitoring enabled'"
echo "3. In another terminal:"
echo "   curl -X POST http://localhost:9621/query/data \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"testosterone\", \"mode\": \"hybrid\", \"top_k\": 20}'"
echo "4. Check activations are stored:"
echo "   curl http://localhost:9621/query/activations"
echo ""
