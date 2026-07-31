# Auto-Rotate Feature for 3D Knowledge Graph

## Overview

The 3D Knowledge Graph now features **gentle auto-rotation** by default, inspired by the realdeepresearch.github.io implementation. This provides a more dynamic and engaging visualization experience.

## Implementation

### Configuration (from realdeepresearch.github.io)

```javascript
// In OrbitControls setup:
controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.rotateSpeed = 0.5;
controls.zoomSpeed = 1.2;
controls.autoRotate = true;           // Enabled by default
controls.autoRotateSpeed = 0.45;      // Slow, gentle rotation
```

### UI Toggle Button

Added "Auto Rotate" button to the bottom control bar:

```html
<button class="control-btn" id="btn-auto-rotate">
  <span>🔄</span> Auto Rotate
</button>
```

### Event Handler

```javascript
document.getElementById('btn-auto-rotate').addEventListener('click', () => {
  controls.autoRotate = !controls.autoRotate;
  const btn = document.getElementById('btn-auto-rotate');
  btn.style.opacity = controls.autoRotate ? '1' : '0.5';
  addLog(
    controls.autoRotate ? '🔄 Auto-rotate enabled' : '⏸️ Auto-rotate disabled',
    'info'
  );
});
```

## Features

### Default Behavior
- **Auto-rotate starts automatically** when viewer loads
- **Speed**: 0.45 (gentle, not distracting)
- **Visual feedback**: Button appears fully opaque when active

### Toggle Control
- Click "🔄 Auto Rotate" button to enable/disable
- Button dims to 50% opacity when disabled
- Query Log shows status change:
  - `🔄 Auto-rotate enabled`
  - `⏸️ Auto-rotate disabled`

### User Interaction
- **Manual rotation**: User can still rotate manually by dragging
- **Resumes after interaction**: Auto-rotate continues after user stops interacting
- **Smooth transitions**: Damping ensures smooth motion

## Technical Details

### OrbitControls Settings

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `autoRotate` | `true` | Enable automatic rotation |
| `autoRotateSpeed` | `0.45` | Slow, gentle rotation speed |
| `enableDamping` | `true` | Smooth deceleration |
| `dampingFactor` | `0.05` | Damping intensity |

### Performance
- **Minimal overhead**: Uses Three.js built-in auto-rotate
- **60 FPS**: No performance impact
- **GPU accelerated**: Leverages WebGL rendering

## Comparison with Reference Implementation

### realdeepresearch.github.io
```javascript
this.controls.autoRotate = true;
this.controls.autoRotateSpeed = 0.45;
```

### Our Implementation (Identical)
```javascript
controls.autoRotate = true;
controls.autoRotateSpeed = 0.45;
```

Both use the same settings for consistent user experience!

## Usage Examples

### Default Experience
1. Open viewer: `http://localhost:9621/graph3d/viewer`
2. Galaxy slowly rotates automatically
3. User can drag to rotate manually
4. Galaxy continues rotating after release

### Disable Auto-Rotate
1. Click "🔄 Auto Rotate" button
2. Button dims to 50% opacity
3. Query Log shows: "⏸️ Auto-rotate disabled"
4. Galaxy stops rotating

### Re-enable Auto-Rotate
1. Click "🔄 Auto Rotate" button again
2. Button returns to full opacity
3. Query Log shows: "🔄 Auto-rotate enabled"
4. Galaxy resumes rotation

## Benefits

1. **Engaging Visualization**: Gentle motion draws attention
2. **Professional Look**: Similar to research visualizations
3. **Spatial Awareness**: Helps users understand 3D structure
4. **Low Distraction**: Slow speed doesn't interfere with interaction
5. **User Control**: Easy to toggle on/off

## Customization

### Adjust Rotation Speed

Edit `graph3d_viewer.html`:

```javascript
controls.autoRotateSpeed = 0.45;  // Current (gentle)
// controls.autoRotateSpeed = 0.2;  // Even slower
// controls.autoRotateSpeed = 1.0;  // Faster rotation
```

### Disable by Default

```javascript
controls.autoRotate = false;  // Start disabled
```

### Remove Toggle Button

Remove from HTML:
```html
<button class="control-btn" id="btn-auto-rotate">
  <span>🔄</span> Auto Rotate
</button>
```

And remove event listener from JavaScript.

## Integration with Other Features

### Works With:
- ✅ Neuron activation
- ✅ Edge highlighting
- ✅ Query panel
- ✅ Entity selection
- ✅ Camera controls

### Does Not Interfere With:
- ✅ Manual rotation
- ✅ Zoom in/out
- ✅ Panning
- ✅ Entity hover/click

## Deployment

The auto-rotate feature is included in the latest deployment. To update:

```bash
# Copy updated viewer
docker cp /data/workspace/lightrag_all/LightRAG/lightrag/api/static/graph3d_viewer.html \
  hua-lightrag:/app/lightrag/api/static/

# Restart container
docker restart hua-lightrag
```

## Future Enhancements

Potential improvements:

- [ ] **Variable speed control**: Slider to adjust rotation speed
- [ ] **Pause on hover**: Stop rotation when user hovers over entity
- [ ] **Direction toggle**: Switch between clockwise/counterclockwise
- [ ] **Axis selection**: Rotate around X, Y, or Z axis
- [ ] **Animation presets**: Different rotation patterns

## References

- **Three.js OrbitControls**: https://threejs.org/docs/#examples/en/controls/OrbitControls
- **Inspired by**: realdeepresearch.github.io implementation
- **Auto-rotate documentation**: https://threejs.org/docs/#examples/en/controls/OrbitControls.autoRotate

---

**Status**: ✅ Implemented and deployed  
**Version**: 1.0  
**Last Updated**: 2026-07-30
