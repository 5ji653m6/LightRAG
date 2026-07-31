# Real-Time Query Activation Feature

## Overview

The 3D Knowledge Graph now supports **real-time neuron activation** whenever the `/query/data` endpoint is called from **any source** - not just from the viewer itself.

## How It Works

### Backend Changes

1. **Query Tracking** (`lightrag/api/routers/query_routes.py`):
   - Every call to `/query/data` now stores the query results in a global list
   - Stores: timestamp, query text, entity names, and relationship pairs
   - Keeps the last 100 activations in memory

2. **Activation Polling Endpoint** (`GET /query/activations`):
   - Returns recent query activations
   - Supports filtering by timestamp (`?since=<timestamp>`)
   - Supports limiting results (`?limit=10`)
   - Example response:
   ```json
   {
     "activations": [
       {
         "timestamp": 1722345678.123,
         "query": "testosterone",
         "entities": ["TESTOSTERONE", "ANDROGEN", "HORMONE"],
         "relationships": [
           {"src": "TESTOSTERONE", "tgt": "ANDROGEN"},
           {"src": "TESTOSTERONE", "tgt": "HORMONE"}
         ]
       }
     ],
     "count": 1,
     "latest_timestamp": 1722345678.123
   }
   ```

### Frontend Changes

1. **Polling Mechanism** (`lightrag/api/static/graph3d_viewer.html`):
   - Viewer polls `/query/activations` every 2 seconds
   - Tracks `lastActivationTimestamp` to only process new activations
   - Automatically activates neurons when new queries are detected

2. **User Experience**:
   - Log panel shows: "🌐 External query: **"query text"**"
   - Entities activate with the same visual effect as manual queries
   - Activation persists until next query (from any source)

## Usage Examples

### Example 1: External API Call Triggers Activation

```bash
# Make a query from anywhere (terminal, script, another app)
curl -X POST http://localhost:9621/query/data \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes treatment",
    "mode": "hybrid",
    "top_k": 20
  }'

# The 3D viewer (if open) will automatically activate the neurons!
```

### Example 2: Python Script Integration

```python
import requests

# Query from your Python application
response = requests.post(
    "http://localhost:9621/query/data",
    json={
        "query": "protein synthesis",
        "mode": "hybrid",
        "top_k": 15
    }
)

# 3D viewer automatically shows the activation
```

### Example 3: Multiple Concurrent Viewers

```
┌─────────────────┐
│  API Client 1   │ ──┐
└─────────────────┘   │
                      ▼
┌─────────────────┐   ┌──────────────┐   ┌─────────────────┐
│  API Client 2   │ ──▶│ /query/data  │   │  3D Viewer 1    │
└─────────────────┘   │              │──▶│  (auto-activate) │
                      │  Stores in   │   └─────────────────┘
┌─────────────────┐   │  memory      │   ┌─────────────────┐
│  3D Viewer 2    │◀──│              │──▶│  (auto-activate) │
│  (auto-activate)│   │ /query/      │   └─────────────────┘
└─────────────────┘   │ activations  │   ┌─────────────────┐
                      │              │──▶│  3D Viewer 3    │
┌─────────────────┐   └──────────────┘   │  (auto-activate) │
│  API Client 3   │ ────────────────────▶└─────────────────┘
└─────────────────┘
```

All viewers see the activation in real-time!

## Technical Details

### Polling Configuration

In `graph3d_viewer.html`:

```javascript
const POLL_INTERVAL_MS = 2000; // Poll every 2 seconds
```

Adjust this value to change polling frequency:
- **1000ms (1s)**: More responsive, more server load
- **2000ms (2s)**: Balanced (default)
- **5000ms (5s)**: Less responsive, less server load

### Activation Storage

In `query_routes.py`:

```python
_MAX_ACTIVATIONS_TO_KEEP = 100
```

This keeps the last 100 queries in memory. Adjust based on your needs.

### Timestamp Filtering

The viewer only processes activations newer than `lastActivationTimestamp`:

```javascript
const url = lastActivationTimestamp
  ? `${ACTIVATIONS_URL}?since=${lastActivationTimestamp}&limit=5`
  : `${ACTIVATIONS_URL}?limit=5`;
```

This prevents duplicate activations and reduces processing overhead.

## Benefits

1. **Real-Time Visualization**: See query results visualized immediately
2. **Multi-Client Support**: All viewers see the same activation
3. **No WebSocket Required**: Uses simple HTTP polling
4. **Backward Compatible**: Existing queries work unchanged
5. **Low Overhead**: Polling every 2s is negligible load

## Testing

### Manual Test

1. Open viewer: `http://localhost:9621/graph3d/viewer`
2. Watch the log panel - should show: "🔄 Real-time activation monitoring enabled"
3. In another terminal:
   ```bash
   curl -X POST http://localhost:9621/query/data \
     -H "Content-Type: application/json" \
     -d '{"query": "testosterone", "mode": "hybrid", "top_k": 20}'
   ```
4. Within 2 seconds, neurons should activate in the viewer

### Automated Test

```python
import time
import requests

# Start viewer first, then run this script
queries = ["testosterone", "diabetes", "protein synthesis"]

for query in queries:
    print(f"Querying: {query}")
    requests.post(
        "http://localhost:9621/query/data",
        json={"query": query, "mode": "hybrid", "top_k": 20}
    )
    time.sleep(5)  # Wait to see each activation
```

## Limitations

1. **Polling Delay**: Up to 2-second delay (configurable)
2. **Memory Usage**: Stores last 100 queries (~1-2 MB)
3. **No Persistence**: Activations lost on server restart
4. **Single Server**: Doesn't work across multiple server instances

## Future Enhancements

Potential improvements:

- [ ] **WebSocket support**: True real-time (no polling delay)
- [ ] **Persistent storage**: Save activations to database
- [ ] **Multi-server support**: Redis pub/sub for distributed systems
- [ ] **Activation history**: View past activations
- [ ] **Replay mode**: Replay query sequence
- [ ] **Filter by query mode**: Only activate for specific modes
- [ ] **Configurable polling**: Let users adjust polling interval

## Troubleshooting

### Viewer not activating?

1. Check if polling is enabled:
   - Open browser console (F12)
   - Look for: "🔄 Real-time activation monitoring enabled"

2. Check if activations endpoint works:
   ```bash
   curl http://localhost:9621/query/activations
   ```

3. Check server logs:
   ```bash
   docker logs hua-lightrag | grep activations
   ```

### Polling too slow?

Reduce `POLL_INTERVAL_MS` in `graph3d_viewer.html`:

```javascript
const POLL_INTERVAL_MS = 1000; // 1 second
```

### Too much server load?

Increase polling interval or disable polling:

```javascript
// Disable polling
// startPolling(); // Comment this out in init()
```

## Deployment

Run the deployment script:

```bash
./deploy_realtime_activation.sh
```

Or manually:

```bash
# Copy files
docker cp lightrag/api/routers/query_routes.py hua-lightrag:/app/lightrag/api/routers/
docker cp lightrag/api/static/graph3d_viewer.html hua-lightrag:/app/lightrag/api/static/

# Restart
docker restart hua-lightrag
```

---

**Status**: ✅ Implemented and deployed  
**Version**: 1.0  
**Last Updated**: 2026-07-30
