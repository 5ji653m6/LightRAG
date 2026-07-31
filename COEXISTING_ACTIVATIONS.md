# Coexisting Activations with Fade-Out - Implementation Summary

## ✨ Feature Overview

Query activations now **coexist** instead of replacing each other, with automatic fade-out after 60 seconds.

### Key Features
1. **Coexisting Activations**: Multiple query activations can be visible simultaneously
2. **Maximum 6 Concurrent**: System limits to 6 active activation groups (oldest removed when exceeded)
3. **60-Second Fade**: Activations start fading after 60 seconds, fully disappearing after 65 seconds
4. **Color Differentiation**: Each query still uses a different color from the 10-color palette

## 🎯 Implementation Details

### Backend (query_routes.py)
- **No changes required** - Backend already supports multiple activations with 60-second TTL
- Activations are stored in `_recent_query_activations` list
- Each activation has: query, entities, relations, timestamp

### Frontend (graph3d_viewer.html)

#### New Data Structures
```javascript
const MAX_CONCURRENT_ACTIVATIONS = 6;
const ACTIVATION_FADE_DURATION = 60000; // 60 seconds before fade starts
const ACTIVATION_FADE_OUT_TIME = 5000; // 5 seconds to fade out completely

let activationGroups = []; // Array of activation group objects
```

#### Activation Group Structure
Each activation group contains:
```javascript
{
  id: unique identifier,
  color: THREE.Color,
  timestamp: creation time (Date.now()),
  indices: Set of entity indices,
  spheres: array of sphere meshes,
  edgesMesh: LineSegments mesh,
  particles: Points mesh for traffic lines,
  trafficData: traffic line animation data
}
```

#### Key Functions

**`activateEntities(entityNames)`**
- Creates new activation group instead of clearing previous ones
- Adds group to `activationGroups` array
- Removes oldest groups if exceeding `MAX_CONCURRENT_ACTIVATIONS` (6)
- Starts global animation loop if not already running

**`startActivationAnimation()`**
- Global animation loop handling all activation groups
- Resets all points to original colors each frame
- Applies activation colors for each group with fade factor
- Calculates fade based on age:
  - Age < 60s: fadeFactor = 1.0 (full brightness)
  - Age 60-65s: fadeFactor = 1.0 - (age - 60000) / 5000 (gradual fade)
  - Age > 65s: fadeFactor = 0 (fully faded, marked for removal)
- Animates spheres, edges, and traffic lines for each group
- Removes fully faded groups and cleans up visual elements

**`removeActivationGroup(group)`**
- Helper function to clean up visual elements
- Removes spheres, edges mesh, and traffic particles
- Disposes of geometries and materials
- Logs removal with age information

## 🎨 Visual Behavior

### Multiple Queries Example
1. **Query 1** (Cyan): 20 entities activated
2. **Query 2** (Magenta): 15 entities activated
3. **Query 3** (Yellow): 25 entities activated

All three activations remain visible simultaneously with their respective colors.

### Fade-Out Timeline
- **0-60 seconds**: Full brightness, pulsing animation
- **60-65 seconds**: Gradual fade (opacity decreases from 1.0 to 0.0)
- **After 65 seconds**: Activation removed, visual elements cleaned up

### Max Concurrent Limit
When 7th query is submitted:
- Oldest activation (Query 1) is removed
- New activation (Query 7) is added
- System maintains max 6 concurrent activations

## 🔧 Technical Implementation

### Animation Loop Logic
```javascript
function pulse() {
  // 1. Reset all points to original colors
  for (let idx = 0; idx < entityData.length; idx++) {
    const baseColor = CLUSTER_COLORS[entityData[idx].cluster % CLUSTER_COLORS.length];
    colors[idx * 3] = baseColor.r;
    colors[idx * 3 + 1] = baseColor.g;
    colors[idx * 3 + 2] = baseColor.b;
    sizes[idx] = POINT_SIZE;
  }

  // 2. Process each activation group
  for (const group of activationGroups) {
    const age = now - group.timestamp;
    let fadeFactor = 1.0;

    // Calculate fade based on age
    if (age > ACTIVATION_FADE_DURATION) {
      const fadeProgress = (age - ACTIVATION_FADE_DURATION) / ACTIVATION_FADE_OUT_TIME;
      fadeFactor = Math.max(0, 1.0 - fadeProgress);
      
      if (fadeFactor <= 0) {
        groupsToRemove.push(group);
        continue;
      }
    }

    // Apply activation color with fade
    for (const idx of group.indices) {
      const brightColor = baseColor.clone()
        .lerp(group.color, 0.3 * fadeFactor)
        .lerp(white, pulseIntensity * 0.5 * fadeFactor);
      colors[idx * 3] = brightColor.r;
      colors[idx * 3 + 1] = brightColor.g;
      colors[idx * 3 + 2] = brightColor.b;
      sizes[idx] = POINT_SIZE * (1 + pulseIntensity * 1.5 * fadeFactor);
    }

    // Animate visual elements with fade
    if (group.spheres) {
      group.spheres.forEach(sphere => {
        sphere.material.opacity = baseOpacity * pulse * fadeFactor;
      });
    }
  }

  // 3. Remove fully faded groups
  for (const group of groupsToRemove) {
    activationGroups.splice(activationGroups.indexOf(group), 1);
    removeActivationGroup(group);
  }

  // 4. Continue animation if groups exist
  if (activationGroups.length > 0) {
    activationAnimation = requestAnimationFrame(pulse);
  } else {
    activationAnimation = null;
  }
}
```

## 📊 Benefits

### User Experience
- **Temporal context**: See multiple recent queries simultaneously
- **Color coding**: Easy to distinguish which entities belong to which query
- **Natural fade**: Activations gradually disappear instead of abruptly vanishing
- **Performance**: Max 6 concurrent activations prevents visual clutter

### Visual Clarity
- **No overlap confusion**: Different colors prevent confusion between queries
- **Smooth transitions**: 5-second fade-out is smooth and non-distracting
- **Automatic cleanup**: Old activations automatically removed after fading

## 🚀 Testing

### Test Scenario
```python
# Run 3 queries in quick succession
queries = ['糖尿病是什么', '高血压治疗', '心脏病症状']

# Expected behavior:
# - All 3 activations visible simultaneously
# - Each uses different color (cyan, magenta, yellow)
# - After 60 seconds, oldest starts fading
# - After 65 seconds, oldest is removed
```

### Verification Steps
1. Open 3D viewer: `http://localhost:9622/graph3d/viewer`
2. Run first query → observe cyan activation
3. Run second query → observe magenta activation (cyan still visible)
4. Run third query → observe yellow activation (cyan and magenta still visible)
5. Wait 60 seconds → observe first query (cyan) start fading
6. Wait 65 seconds → observe first query completely removed
7. Run 7 queries → observe oldest automatically removed when exceeding max 6

## ✅ Status

**Implementation Date**: 2026-07-31  
**Status**: ✅ Complete and deployed  
**Service**: Running on port 9622 via PM2  
**Features**:
- ✅ Coexisting activations (max 6 concurrent)
- ✅ 60-second fade-out (5-second fade duration)
- ✅ Color differentiation (10-color rotating palette)
- ✅ Automatic cleanup of faded activations
- ✅ Global animation loop for all groups

---

**Coexisting activations with fade-out successfully implemented!** 🎨✨
