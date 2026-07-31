# Queue System for Sequential Activation Processing

## Overview

The 3D Knowledge Graph now uses a **queue-based system** to process query activations sequentially, ensuring that every query gets proper visual activation time, even when multiple queries arrive rapidly.

## Problem Solved

### Before (Without Queue)
```
Time 0: Query A arrives → starts activation (4s)
Time 1: Query B arrives → immediately clears A, starts B
Time 2: Query C arrives → immediately clears B, starts C
Result: User only sees C, A and B were skipped visually
```

### After (With Queue)
```
Time 0: Query A arrives → queued
Time 0: Queue processor → activates A (4s display)
Time 1: Query B arrives → queued (waits)
Time 2: Query C arrives → queued (waits)
Time 4: A finished → B starts (4s display)
Time 8: B finished → C starts (4s display)
Result: User sees ALL activations in sequence
```

## Implementation Details

### Queue Configuration

```javascript
// In graph3d_viewer.html
const ACTIVATION_DISPLAY_DURATION = 4000; // 4 seconds per activation
const QUEUE_PROCESSING_DELAY = 500;       // 0.5s between activations
const POLL_INTERVAL_MS = 2000;            // Poll every 2 seconds
```

### Data Structures

```javascript
let activationQueue = [];           // FIFO queue of pending activations
let isProcessingQueue = false;      // Lock to prevent concurrent processing

// Queue item structure
{
  query: "query text",
  entities: ["entity1", "entity2", ...],
  entityCount: 15,
  timestamp: 1785418916.373209,
  isManual: true/false  // Distinguishes manual vs external queries
}
```

### Queue Processing Flow

```
1. Query arrives (manual or external)
   ↓
2. Add to activationQueue[]
   ↓
3. If not processing, start processActivationQueue()
   ↓
4. Loop while queue has items:
   a. Shift first item from queue
   b. Log query details
   c. Activate entities (4s visible)
   d. Show queue status if more items
   e. Wait 4.5s (4s display + 0.5s delay)
   f. Continue to next item
   ↓
5. Set isProcessingQueue = false
```

## Features

### 1. Sequential Processing
- Queries processed in FIFO order
- Each gets full 4-second display time
- No activations skipped

### 2. Queue Status Feedback
When multiple queries are queued:
```
🌐 External query: "testosterone"
✅ Found 15 entities
⚡ Activated 15 neurons
⏳ 2 more queries queued...
```

### 3. Manual vs External Queries
Both use the same queue, but logged differently:
- **Manual**: `🔍 Manual query: "text"`
- **External**: `🌐 External query: "text"`

### 4. Concurrent Query Handling

**Scenario: 3 queries arrive in rapid succession**

```bash
# Terminal 1
curl -X POST http://localhost:9622/query/data \
  -H "Content-Type: application/json" \
  -d '{"query": "testosterone", "mode": "hybrid", "top_k": 20}'

# Terminal 2 (immediately after)
curl -X POST http://localhost:9622/query/data \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes", "mode": "hybrid", "top_k": 20}'

# Terminal 3 (immediately after)
curl -X POST http://localhost:9622/query/data \
  -H "Content-Type: application/json" \
  -d '{"query": "protein", "mode": "hybrid", "top_k": 20}'
```

**Viewer Log**:
```
[Time 0] 🌐 External query: "testosterone"
[Time 0] ✅ Found 15 entities
[Time 0] ⚡ Activated 15 neurons
[Time 0] ⏳ 2 more queries queued...

[Time 4.5] 🌐 External query: "diabetes"
[Time 4.5] ✅ Found 12 entities
[Time 4.5] ⚡ Activated 12 neurons
[Time 4.5] ⏳ 1 more query queued...

[Time 9] 🌐 External query: "protein"
[Time 9] ✅ Found 18 entities
[Time 9] ⚡ Activated 18 neurons
```

**Result**: All 3 queries are visualized in sequence!

## Configuration Options

### Adjust Display Duration

```javascript
// Show each activation longer (e.g., 6 seconds)
const ACTIVATION_DISPLAY_DURATION = 6000;
```

### Adjust Processing Delay

```javascript
// Faster transitions (e.g., 0.2s)
const QUEUE_PROCESSING_DELAY = 200;
```

### Adjust Polling Frequency

```javascript
// Poll more frequently (e.g., every 1 second)
const POLL_INTERVAL_MS = 1000;
```

## Testing

### Test 1: Single Query
```bash
curl -X POST http://localhost:9622/query/data \
  -H "Content-Type: application/json" \
  -d '{"query": "testosterone", "mode": "hybrid", "top_k": 20}'
```
**Expected**: Activation appears immediately, stays for 4 seconds

### Test 2: Rapid Sequential Queries
```bash
# Run these in quick succession
for query in "testosterone" "diabetes" "protein" "glucose"; do
  curl -X POST http://localhost:9622/query/data \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\", \"mode\": \"hybrid\", \"top_k\": 20}" &
done
wait
```
**Expected**: All 4 queries activate sequentially, each visible for 4 seconds

### Test 3: Manual + External Mixed
1. Enter query in viewer: "manual test"
2. Immediately run: `curl ... "external test"`
3. **Expected**: Both activate in order received

### Test 4: Queue Status
```bash
# Send 5 queries rapidly
for i in {1..5}; do
  curl -X POST http://localhost:9622/query/data \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"query$i\", \"mode\": \"hybrid\", \"top_k\": 10}" &
done
wait
```
**Expected**: 
- First query activates
- Log shows: "⏳ 4 more queries queued..."
- Each subsequent query processes in order

## Visual Timeline

### Example: 3 Queries Arriving at t=0, t=1, t=2

```
Time (s) | Viewer State
---------|------------------------------------------------
0.0      | Query 1 arrives, starts processing
0.0      | 🔍 Query 1 activates (bright white)
0.0-4.0  | Query 1 visible, neurons glowing
1.0      | Query 2 arrives, waits in queue
2.0      | Query 3 arrives, waits in queue
4.0      | Query 1 fades
4.5      | Query 2 starts processing
4.5-8.5  | Query 2 visible, neurons glowing
8.5      | Query 2 fades
9.0      | Query 3 starts processing
9.0-13.0 | Query 3 visible, neurons glowing
13.0     | Queue empty, system idle
```

## Benefits

1. **No Skipped Activations**: Every query gets visual time
2. **Predictable Behavior**: FIFO ordering
3. **User Feedback**: Queue status shown in log
4. **Smooth Experience**: Delay between activations
5. **Scalable**: Handles burst of queries gracefully
6. **Unified System**: Manual and external queries use same queue

## Limitations

1. **Queue Buildup**: If queries arrive faster than processing, queue grows
2. **Memory**: Queue stored in memory (not persistent)
3. **Single Viewer**: Queue is per-viewer, not shared across viewers
4. **Max Queue Size**: No limit (could add one if needed)

## Future Enhancements

Potential improvements:

- [ ] **Queue Size Limit**: Drop oldest if queue > N items
- [ ] **Priority System**: Some queries skip queue
- [ ] **Batch Mode**: Combine similar queries
- [ ] **Persistent Queue**: Survive page reload
- [ ] **Multi-Viewer Sync**: Share queue across viewers
- [ ] **Configurable Duration**: User-adjustable display time
- [ ] **Pause/Resume**: Temporarily halt queue processing

## Troubleshooting

### Queue Not Processing?
- Check browser console for errors
- Verify `isProcessingQueue` flag
- Check if `activationQueue` has items

### Activations Too Fast?
- Increase `ACTIVATION_DISPLAY_DURATION`
- Increase `QUEUE_PROCESSING_DELAY`

### Activations Too Slow?
- Decrease `ACTIVATION_DISPLAY_DURATION`
- Decrease `QUEUE_PROCESSING_DELAY`

### Queue Building Up?
- Reduce query frequency
- Increase processing speed
- Add queue size limit

## Code Location

All queue logic in `lightrag/api/static/graph3d_viewer.html`:

```javascript
// Line ~520: Queue variables
let activationQueue = [];
let isProcessingQueue = false;

// Line ~1127: pollForActivations() adds to queue
// Line ~1183: startPolling() starts polling
// Line ~1193: processActivationQueue() processes queue
// Line ~860: queryAndActivate() adds manual queries to queue
```

## Summary

The queue system ensures that **every query gets its moment to shine**, providing a smooth, sequential visualization experience even when multiple queries arrive rapidly. No more skipped activations!

---

**Status**: ✅ Implemented and deployed  
**Version**: 1.0  
**Last Updated**: 2026-07-30
