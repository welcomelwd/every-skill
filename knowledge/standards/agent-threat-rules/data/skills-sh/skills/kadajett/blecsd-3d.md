---
name: blecsd-3d
description: Render 3D graphics in the terminal with @blecsd/3d. Covers software rasterizer, 3D math (vec3/mat4), multiple backends (braille/sixel/kitty), OBJ loading, scene graphs, and camera systems.
license: MIT
metadata:
  author: blecsd
  version: "2.0.0"
---

# @blecsd/3d Package Skill

The `@blecsd/3d` package provides a complete 3D rendering pipeline for blECSd terminal applications. It includes a software rasterizer, 3D math library, multiple terminal rendering backends, OBJ model loading, scene graph system, and camera management. All blECSd functional programming rules apply.

**Install:** `pnpm add @blecsd/3d`
**Peer dependency:** `blecsd >= 0.7.0`

## Subpath Imports

```typescript
import { vec3, vec3Add, mat4Identity, mat4Multiply, perspectiveMatrix, lookAt } from '@blecsd/3d/math';
import { createBrailleBackend, detectBestBackend } from '@blecsd/3d/backends';
import { Transform3D, Camera3D, Mesh, Material3D } from '@blecsd/3d/components';
import { parseObj, loadObjAsMesh } from '@blecsd/3d/loaders';
import { createPixelFramebuffer, fillTriangleFlat, drawLine } from '@blecsd/3d/rasterizer';
import { sceneGraphSystem, projectionSystem, rasterSystem, viewportOutputSystem } from '@blecsd/3d/systems';
import { createCubeMesh, createSphereMesh } from '@blecsd/3d/stores';
```

Or use namespace API:

```typescript
import { vec3 as v3, mat4 as m4, projection, clipping, pixelBuffer, raster, transform3d, camera3d, mesh, backends } from '@blecsd/3d';
```

## 3D Math

### Vec3

```typescript
import {
  vec3, vec3Add, vec3Sub, vec3Scale, vec3Dot, vec3Cross,
  vec3Normalize, vec3Length, vec3Distance, vec3Lerp, vec3Zero, vec3Negate,
} from '@blecsd/3d/math';

const a = vec3(1, 2, 3);
const b = vec3(4, 5, 6);
const sum = vec3Add(a, b);           // [5, 7, 9]
const diff = vec3Sub(a, b);          // [-3, -3, -3]
const scaled = vec3Scale(a, 2);      // [2, 4, 6]
const dot = vec3Dot(a, b);           // 32
const cross = vec3Cross(a, b);       // [-3, 6, -3]
const norm = vec3Normalize(a);       // unit vector
const len = vec3Length(a);           // 3.741...
const dist = vec3Distance(a, b);     // 5.196...
const lerped = vec3Lerp(a, b, 0.5); // [2.5, 3.5, 4.5]
const zero = vec3Zero();             // [0, 0, 0]
const neg = vec3Negate(a);           // [-1, -2, -3]
```

### Mat4

```typescript
import {
  mat4Identity, mat4Multiply, mat4Transpose, mat4Invert, mat4Determinant,
  mat4Translate, mat4RotateX, mat4RotateY, mat4RotateZ, mat4Scale,
  mat4FromTRS, mat4TransformVec3,
} from '@blecsd/3d/math';

const identity = mat4Identity();
const translated = mat4Translate(identity, vec3(10, 0, 0));
const rotated = mat4RotateY(identity, Math.PI / 4);
const scaled = mat4Scale(identity, vec3(2, 2, 2));
const combined = mat4Multiply(translated, rotated);

// Transform a point
const worldPos = mat4TransformVec3(combined, vec3(0, 0, 0));

// Build from Translation, Rotation, Scale
const trs = mat4FromTRS(
  vec3(10, 5, 0),      // translation
  vec3(0, Math.PI, 0), // rotation (euler angles)
  vec3(1, 1, 1),       // scale
);

// Inverse and transpose
const inv = mat4Invert(combined);
const trans = mat4Transpose(combined);
```

### Projection

```typescript
import {
  perspectiveMatrix, orthographicMatrix, lookAt, buildMVP,
  projectVertex, unprojectVertex, viewportTransform,
} from '@blecsd/3d/math';

// Perspective projection
const proj = perspectiveMatrix(
  Math.PI / 4,  // FOV (radians)
  80 / 24,      // Aspect ratio
  0.1,          // Near plane
  100,          // Far plane
);

// Orthographic projection
const ortho = orthographicMatrix(-10, 10, 10, -10, 0.1, 100);

// View matrix (camera)
const view = lookAt(
  vec3(0, 5, 10),  // Eye position
  vec3(0, 0, 0),   // Look at target
  vec3(0, 1, 0),   // Up vector
);

// Combined MVP matrix
const model = mat4Identity();
const mvp = buildMVP(model, view, proj);

// Project 3D point to screen
const screenPos = projectVertex(vec3(1, 2, 3), mvp, { width: 80, height: 24 });

// Unproject screen point back to 3D
const worldPos = unprojectVertex({ x: 40, y: 12, z: 0.5 }, mvp, { width: 80, height: 24 });
```

### Frustum Culling

```typescript
import { extractFrustumPlanes, isPointInFrustum, isSphereInFrustum, clipLine } from '@blecsd/3d/math';

const planes = extractFrustumPlanes(mvp);
const visible = isPointInFrustum(vec3(0, 0, -5), planes);
const sphereVisible = isSphereInFrustum(vec3(0, 0, -5), 2.0, planes);
const clipped = clipLine(p1, p2, planes);
```

## Rendering Backends

Multiple backends with different quality/compatibility trade-offs:

```typescript
import {
  createBrailleBackend, createHalfBlockBackend, createSextantBackend,
  createSixelBackend, createKittyBackend, detectBestBackend, createBackendByType,
} from '@blecsd/3d/backends';

// Auto-detect best backend for current terminal
const backend = detectBestBackend();

// Or create specific backend
const braille = createBrailleBackend();    // 2x4 dots per cell (widest support)
const halfblock = createHalfBlockBackend(); // 2 pixels per cell vertically
const sextant = createSextantBackend();     // 2x3 pixels per cell
const sixel = createSixelBackend();         // True pixel (requires Sixel support)
const kitty = createKittyBackend();         // True pixel (requires Kitty protocol)

// Create by name
const byName = createBackendByType('braille');
```

**Backend comparison:**

| Backend | Resolution | Compatibility | Notes |
|---------|-----------|---------------|-------|
| `braille` | 2x4 per cell | Most terminals | Best default choice |
| `halfblock` | 1x2 per cell | All terminals | Simple, fast |
| `sextant` | 2x3 per cell | Unicode terminals | Good balance |
| `sixel` | Pixel-level | xterm, mlterm, foot | True graphics |
| `kitty` | Pixel-level | Kitty terminal | True graphics |

## ECS Components

### Transform3D

Position, rotation, scale with world matrix caching:

```typescript
import { Transform3D, setTranslation, setRotation, setScale, getWorldMatrix, markDirty } from '@blecsd/3d/components';

setTranslation(world, eid, vec3(10, 5, 0));
setRotation(world, eid, vec3(0, Math.PI / 4, 0));
setScale(world, eid, vec3(2, 2, 2));

const worldMatrix = getWorldMatrix(eid); // Computed from parent chain
markDirty(eid); // Force recalculation
```

### Camera3D

Camera with projection and view matrices:

```typescript
import { Camera3D, setCamera3D, getCamera3D, getProjMatrix, getViewMatrix } from '@blecsd/3d/components';

setCamera3D(world, eid, {
  fov: Math.PI / 4,
  near: 0.1,
  far: 100,
  eye: vec3(0, 5, 10),
  target: vec3(0, 0, 0),
  up: vec3(0, 1, 0),
});

const proj = getProjMatrix(eid);
const view = getViewMatrix(eid);
```

### Mesh

Vertex and index buffers:

```typescript
import { Mesh, createMeshFromArrays, registerMesh, setMesh, getMesh } from '@blecsd/3d/components';

// Create mesh from raw arrays
const mesh = createMeshFromArrays(
  [0,0,0, 1,0,0, 0,1,0], // vertices (x,y,z triplets)
  [0, 1, 2],               // indices (triangle)
);

// Register for reuse
registerMesh('triangle', mesh);

// Assign to entity
setMesh(world, eid, 'triangle');

// Retrieve
const data = getMeshData('triangle');
```

### Material3D

Surface appearance:

```typescript
import { Material3D, setMaterial3D } from '@blecsd/3d/components';

setMaterial3D(world, eid, {
  color: [255, 128, 0],  // RGB
  shadingMode: 'flat',   // 'flat' | 'wireframe' | 'points'
});
```

### Primitive Meshes

Pre-built geometry:

```typescript
import { createCubeMesh, createSphereMesh, createPlaneMesh, createCylinderMesh } from '@blecsd/3d/stores';

const cube = createCubeMesh();
const sphere = createSphereMesh(1.0, 16); // radius, segments
const plane = createPlaneMesh(5, 5);      // width, height
const cylinder = createCylinderMesh(0.5, 2.0, 12); // radius, height, segments
```

## Rasterizer

Software rasterization pipeline:

### Pixel Framebuffer

```typescript
import {
  createPixelFramebuffer, setPixel, getPixel, clearFramebuffer,
  fillRect, testAndSetDepth, isInBounds,
} from '@blecsd/3d/rasterizer';

const fb = createPixelFramebuffer(160, 96); // width x height in pixels
clearFramebuffer(fb, [0, 0, 0]); // Clear to black

setPixel(fb, 10, 20, [255, 0, 0]); // Red pixel
const color = getPixel(fb, 10, 20);

// Depth testing
if (testAndSetDepth(fb, x, y, z)) {
  setPixel(fb, x, y, color); // Closer than existing
}
```

### Line Drawing

```typescript
import { drawLine, drawLineColor, drawLineDepth, drawLineAA, blendPixel } from '@blecsd/3d/rasterizer';

drawLine(fb, 0, 0, 80, 48, [255, 255, 255]);             // White line
drawLineColor(fb, 0, 0, 80, 48, [255,0,0], [0,0,255]);   // Gradient red to blue
drawLineDepth(fb, 0, 0, 80, 48, 0.1, 0.9, [255,255,255]); // With depth
drawLineAA(fb, 0, 0, 80, 48, [255, 255, 255]);            // Anti-aliased
blendPixel(fb, 40, 24, [255, 0, 0, 128]);                  // Alpha blend
```

### Triangle Rasterization

```typescript
import {
  fillTriangleFlat, fillTriangle, triangleArea2, triangleBoundingBox,
  computeFaceNormal, computeFlatShading,
} from '@blecsd/3d/rasterizer';

// Flat color triangle
fillTriangleFlat(fb, v1, v2, v3, [255, 128, 0]);

// Custom shader triangle
fillTriangle(fb, v1, v2, v3, (x, y, bary) => {
  // bary = barycentric coordinates [u, v, w]
  // Return color based on barycentric interpolation
  return interpolateColor(c1, c2, c3, bary);
});

// Shading
const normal = computeFaceNormal(v1, v2, v3);
const lightDir = vec3Normalize(vec3(1, 1, 1));
const color = computeFlatShading(normal, lightDir, [200, 100, 50]);
```

## ECS Systems (Rendering Pipeline)

The 3D systems form a rendering pipeline:

```typescript
import {
  sceneGraphSystem,     // 1. Compute world matrices from hierarchy
  projectionSystem,     // 2. Project 3D to 2D screen coords
  rasterSystem,         // 3. Rasterize triangles to framebuffer
  viewportOutputSystem, // 4. Encode framebuffer via backend
  animation3DSystem,    // Update 3D animations
  mouseInteraction3DSystem, // Handle mouse input for 3D
} from '@blecsd/3d/systems';

// Run pipeline each frame
function render3D(world: World): void {
  sceneGraphSystem(world);
  projectionSystem(world);
  rasterSystem(world);
  viewportOutputSystem(world);
}
```

**Stores** (shared state between systems):

```typescript
import {
  projectionStore, clearProjectionStore,
  framebufferStore, clearFramebufferStore,
  backendStore, clearBackendStore,
  outputStore, clearOutputStore,
} from '@blecsd/3d/systems';
```

## OBJ Loader

Load 3D models from OBJ files:

```typescript
import { parseObj, loadObjAsMesh, computeBoundingBox } from '@blecsd/3d/loaders';

// Parse OBJ file
const objData = parseObj(objFileContent);
// { vertices, normals, texcoords, faces, groups }

// Load directly as mesh
const mesh = loadObjAsMesh('/models/teapot.obj');
registerMesh('teapot', mesh);

// Compute bounding box
const bbox = computeBoundingBox(objData.vertices);
// { min: Vec3, max: Vec3, center: Vec3, size: Vec3 }
```

## Complete Example: Spinning Cube

```typescript
import { createWorld, addEntity, addComponent } from 'blecsd';
import { vec3, mat4RotateY, perspectiveMatrix, lookAt } from '@blecsd/3d/math';
import { setTranslation, setRotation } from '@blecsd/3d/components';
import { setCamera3D } from '@blecsd/3d/components';
import { setMesh, registerMesh } from '@blecsd/3d/components';
import { setMaterial3D } from '@blecsd/3d/components';
import { createCubeMesh } from '@blecsd/3d/stores';
import { detectBestBackend } from '@blecsd/3d/backends';
import {
  sceneGraphSystem, projectionSystem, rasterSystem, viewportOutputSystem,
} from '@blecsd/3d/systems';

const world = createWorld();

// Register cube mesh
registerMesh('cube', createCubeMesh());

// Create cube entity
const cube = addEntity(world);
setMesh(world, cube, 'cube');
setMaterial3D(world, cube, { color: [0, 200, 100], shadingMode: 'flat' });
setTranslation(world, cube, vec3(0, 0, 0));

// Create camera
const cam = addEntity(world);
setCamera3D(world, cam, {
  fov: Math.PI / 4,
  near: 0.1,
  far: 100,
  eye: vec3(3, 3, 5),
  target: vec3(0, 0, 0),
  up: vec3(0, 1, 0),
});

// Detect best rendering backend
const backend = detectBestBackend();

// Render loop
let angle = 0;
setInterval(() => {
  angle += 0.05;
  setRotation(world, cube, vec3(0, angle, 0));

  sceneGraphSystem(world);
  projectionSystem(world);
  rasterSystem(world);
  viewportOutputSystem(world);
}, 1000 / 30);
```

## Viewport3D Widget

High-level widget that wraps the 3D rendering pipeline into a composable ECS entity:

```typescript
import { createViewport3D, addMeshToViewport, removeMeshFromViewport } from '@blecsd/3d';

const viewport = createViewport3D(world, {
  position: { x: 0, y: 0 },
  dimensions: { width: 80, height: 24 },
  backend: 'braille',  // 'braille' | 'halfblock' | 'sextant' | 'sixel' | 'kitty'
  camera: {
    fov: Math.PI / 4,
    near: 0.1,
    far: 100,
    eye: [3, 3, 5],
    target: [0, 0, 0],
  },
});

// Add meshes to the viewport
addMeshToViewport(world, viewport, meshEntity);

// Remove meshes
removeMeshFromViewport(world, viewport, meshEntity);
```

The viewport manages camera, framebuffer, backend selection, and mesh rendering as a single widget entity.

## Best Practices

1. **Use `detectBestBackend()`** to automatically select the best rendering backend for the user's terminal.
2. **Cache mesh registrations.** Call `registerMesh` once, then reuse the ID with `setMesh` for multiple entities.
3. **Run systems in pipeline order:** sceneGraph -> projection -> raster -> viewportOutput.
4. **Use frustum culling** for scenes with many objects. Check `isSphereInFrustum` before projecting.
5. **Clear stores in tests.** Use `clearProjectionStore()`, `clearFramebufferStore()`, etc.
6. **Braille backend is the safest default.** It works in almost all terminals and gives 2x4 pixel resolution per character cell.
7. **Use primitive factories** (`createCubeMesh`, `createSphereMesh`) for quick prototyping.
8. **All blECSd rules apply.** No classes, pure functions, early returns, Zod at boundaries.
