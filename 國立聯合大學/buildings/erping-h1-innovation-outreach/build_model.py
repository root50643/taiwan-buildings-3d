"""H1 產研創新暨推廣大樓，依官方外觀照片估計比例的實體列印模型。
All geometry is millimetres. The front is -Y. No source photos are bundled.
Run: python build_model.py
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, OpType

OUT = Path(__file__).resolve().parent
parts, cuts, details = [], [], []

def box(x, y, z, w, d, h):
    return Manifold.cube((w, d, h)).translate((x-w/2, y-d/2, z))

def add(x, y, z, w, d, h):
    parts.append(box(x, y, z, w, d, h))

def detail(x, y, z, w, d, h):
    details.append(box(x, y, z, w, d, h))

def cut(x, y, z, w, d, h):
    cuts.append(box(x, y, z, w, d, h))

def cylinder(x, y, z, radius, h, segments=64):
    return Manifold.cylinder(h, radius, radius, segments).translate((x, y, z))

def ellipse(z, rx, ry, h):
    return Manifold.cylinder(h, 1, 1, 112).scale((rx, ry, 1)).translate((0,-10.5,z))

# A single flat, connected plinth, with a shallow forecourt terrace.
add(0, 2, 0, 150, 80, 2.4)
add(0, 6, 2.3, 140, 66, 2.1)
# Main solid core: the photographs support ten front window rows, not a measured floor plan.
# Main silhouette is wider than tall. Depth is deliberately an estimate.
add(0, 9, 4.3, 132, 38, 100)
# Solid edge cores. Their outside window strips are visible from opposite front obliques.
add(-61, -2, 4.3, 10, 18, 110)
add(61, -2, 4.3, 10, 18, 116)
add(-60, 17, 104.2, 17, 18, 17.2)
add(60, 17, 104.2, 12, 15, 16)
# The glazed outside strips are represented by shallow recesses, not detached glass.
for side in [-1, 1]:
    add(side*67.0, 9, 4.3, 5, 30, 101.3)
    for z in [7.4+9.6*i for i in range(10)]:
        cut(side*69.0, 9, z, 2.0, 23.5, 6.0)
        detail(side*68.8, 9, z-.1, 2.0, .9, 6.2)
        for y in [-.0, 18.0]:
            detail(side*68.8, y, z-.1, 2.0, .9, 6.2)
# Narrow top-storey windows: distinct from the grouped horizontal windows below.
for x in np.linspace(-51.5, 51.5, 24):
    cut(float(x), -10, 92.2, 2.6, 1.5, 6.5)
# Ground to ninth floor, with the sixth visual row using narrow individual windows.
# Recesses leave substantial solid backing and do not create interior rooms.
for row in range(9):
    z = 5.8 + row*9.6
    if row == 4:
        for x in list(np.arange(-51.5,-17,4.8)) + list(np.arange(20.8,54,4.8)):
            cut(float(x), -10, z+1.5, 2.7, 1.5, 5.8)
    else:
        for x in [-45.3,-36.2,-27.1,27.1,36.2,45.3]:
            cut(x, -10, z+1.2, 7.5, 1.5, 5.2)
            # Robust mullions and transoms are real STL geometry.
            detail(x, -9.95, z+1.1, .8, 1.6, 5.4)
            detail(x, -9.95, z+5.15, 7.7, 1.6, .8)
        for x in [-52.0,-18.7,18.7,52.0]:
            if row == 2 and abs(x) < 20: continue  # hidden behind the solid entrance drum
            cut(x, -10, z+1.0, 2.7, 1.5, 5.6)
# Photographed vertical shallow slots around the four narrow window stacks.
for x in [-52.0,-18.7,18.7,52.0]:
    for row in [5,6,7,8]:
        cut(x, -10.25, 5.8+row*9.6-1.1, 2.7, .75, 1.8)
# Central protruding window stack, with five thick parapet/sill bands.
add(0, -10.6, 38.0, 18.6, 2.2, 54.3)
for z in [39.4,49.0,58.6,68.2,77.8,87.4]:
    cut(0, -11.8, z, 16.8, 1.6, 5.0)
    for x in [-6.5,-3.25,0,3.25,6.5]:
        detail(x, -11.60, z-.1, .8, 1.6, 5.2)
for z in [38.0,47.6,57.2,66.8,76.4]:
    add(0, -12.2, z, 19.2, 3.4, 3.1)
# The most recognisable entrance: curved elevated drum, two bands, and tall columns.
# The inner core stays solid. Only its open exterior porch remains under the drum.
parts.append(ellipse(21.6, 21.0, 11.2, 14.8))
parts.append(ellipse(21.3, 21.8, 11.8, 3.1))
parts.append(ellipse(33.6, 21.8, 11.8, 3.1))
# Recessed curved-window bays. Each local planar cutter is oriented tangent to the ellipse.
for deg in [-165,-145,-125,-105,-85,-65,-45,-25,-5]:
    t=np.deg2rad(deg)
    x=21.0*np.cos(t); y=-10.5+11.2*np.sin(t)
    normal=np.array([np.cos(t)/21.0,np.sin(t)/11.2]); normal/=np.linalg.norm(normal)
    angle=np.degrees(np.arctan2(normal[1],normal[0]))-90
    cutter=box(0,0,25.2,3.6,1.6,6.7).rotate((0,0,float(angle))).translate((float(x),float(y),0))
    cuts.append(cutter)
# Heavy cylindrical entrance columns, with connected feet, reproduce the visible porch.
for x,y in [(-18.0,-15.8),(-11.4,-20.0),(11.4,-20.0),(18.0,-15.8)]:
    parts.append(cylinder(x,y,4.2,1.75,17.6))
    parts.append(cylinder(x,y,4.1,2.05,1.4))
# Glazed double-height entrance behind the columns.
cut(0,-10.2,4.8,18.0,2.0,16.3)
for x in [-8.2,-4.1,0,4.1,8.2]:detail(x,-9.7,4.7,.9,1.6,16.5)
for z in [7.4,11.8,16.2,20.3]:detail(0,-9.7,z,18.2,1.6,.9)
# Forecourt stairs, in descending nested treads, join the terrace to the base.
for i in range(5):
    add(0,-31.8+i*1.35,2.3+i*.42,31.8,2.0,.65)
# Flat parapet rim, then the central low solar roof canopy.
add(0,9,104.1,118.5,38.8,1.25)
for x in [-48,-32,-16,0,16,32,48]:
    for y in [-3,23]:add(x,y,105.2,1.4,1.4,4.0+(y+3)*.04)
for y in [-3,23]:add(0,y,108.2+(y+3)*.04,100,1.6,1.4)
# Sloped solid panel (extruded vertical cross-section), with shallow panel grid.
# Rotation is around world origin, so use local shape for a correct slope about its centre.
roof=box(0,0,0,102,31,1.35).rotate((2.4,0,0)).translate((0,10,109.2))
parts.append(roof)
for x in range(-48,49,8):
    cuts.append(box(x,0,.94,.65,31.5,.8).rotate((2.4,0,0)).translate((0,10,109.2)))
for y in [-10,0,10]:
    cuts.append(box(0,y,.94,101,.65,.8).rotate((2.4,0,0)).translate((0,10,109.2)))
# Left rooftop equipment screen: planar shallow slots, no guessed machinery or antennae.
for x in [-66,-62,-58,-54]:cut(x,7.9,114.8,.65,1.3,5.3)
for z in [115,117.1,119.2]:cut(-60,7.9,z,14.8,1.3,.65)
# Unobserved rear stays plain; it is not a mirrored invented elevation.
result = Manifold.batch_boolean(parts, OpType.Add) - Manifold.batch_boolean(cuts, OpType.Add)
result = result + Manifold.batch_boolean(details, OpType.Add)
if result.status().name != 'NoError':raise RuntimeError(result.status())
m=result.to_mesh()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
if not mesh.is_watertight or len(mesh.split(only_watertight=False)) != 1:
    print([(q.volume,q.bounds.tolist()) for q in mesh.split(only_watertight=False)])
    raise RuntimeError('Model must remain one watertight boundary')
mesh.export(OUT/'model.stl')
print('Exported model.stl:',mesh.extents.tolist(),'mm;',len(mesh.faces),'triangles')
