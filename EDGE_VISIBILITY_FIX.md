# Edge Visibility Toggle Fix

## 🐛 Issue

The 3D graph would occasionally toggle edges and make all edges visible, even when the user had toggled them off.

## 🔍 Root Cause

The animation loop in `startActivationAnimation()` was setting `edgesMesh.visible = true` when all activation groups faded out and were removed. This overrode the user's edge visibility preference stored in the `showEdges` variable.

### Problem Flow
1. User clicks "Toggle Edges" button → `showEdges = false`, `edgesMesh.visible = false`
2. Activations fade out after 60-65 seconds
3. Animation loop detects `activationGroups.length === 0`
4. Animation loop sets `edgesMesh.visible = true` ❌ (ignores user preference)
5. Edges become visible even though user toggled them off

## ✅ Solution

Changed the animation loop to respect the `showEdges` variable when restoring edge visibility:

**Before:**
```javascript
if (edgesMesh) {
  edgesMesh.visible = true;  // ❌ Always true
}
```

**After:**
```javascript
if (edgesMesh) {
  edgesMesh.visible = showEdges;  // ✅ Respects user preference
}
```

## 📝 Code Changes

**File**: `lightrag/api/static/graph3d_viewer.html`  
**Line**: ~1255  
**Function**: `startActivationAnimation()` → `pulse()` inner function

```javascript
// Continue animation if there are active groups
if (activationGroups.length > 0) {
  activationAnimation = requestAnimationFrame(pulse);
} else {
  activationAnimation = null;
  // Restore edges visibility based on user preference
  if (edgesMesh) {
    edgesMesh.visible = showEdges;  // Changed from: edgesMesh.visible = true;
  }
}
```

## 🧪 Testing

### Test Scenario
1. Open 3D viewer: `http://localhost:9622/graph3d/viewer`
2. Click "Toggle Edges" button to hide edges
3. Run a query to activate entities
4. Wait for activation to fade out (60-65 seconds)
5. Verify edges remain hidden after fade-out

### Expected Behavior
- ✅ Edges stay hidden after activations fade out
- ✅ User's toggle preference is preserved
- ✅ No unexpected edge visibility changes

## 📊 Impact

- **User Experience**: Edge visibility toggle now works consistently
- **No Breaking Changes**: Only affects the fade-out cleanup logic
- **Backward Compatible**: Works with existing activation system

## ✅ Status

**Fix Date**: 2026-07-31  
**Status**: ✅ Deployed and tested  
**Service**: `lightrag-9622` restarted via PM2

---

**Edge visibility toggle issue resolved!** 🎯
