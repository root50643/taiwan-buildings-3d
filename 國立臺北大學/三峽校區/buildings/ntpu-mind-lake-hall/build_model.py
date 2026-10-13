"""NTPU Mind Lake Hall: handmade exterior approximation from completed photos.
All dimensions are miniature millimetres. Does not import any external mesh.
Front = land/parking side; rear = lake side. Hidden service details are omitted.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def beam(p,q,w,h,z):
 dx,dy=q[0]-p[0],q[1]-p[1];l=math.hypot(dx,dy)
 return box(0,0,z,l+w,w,h).rotate((0,0,math.degrees(math.atan2(dy,dx)))).translate(((p[0]+q[0])/2,(p[1]+q[1])/2,0))
def roof(x,y,z,w,d,rise,ang=0,off=0):
 # Four folded triangular slopes, deliberately non-level eaves, and an offset ridge.
 # Folded roofs visually estimated from completed photos, not measured roof drawings.
 v=np.array([[-w/2,-d/2,0],[w/2,-d/2,0],[w/2,d/2,0],[-w/2,d/2,0],[-w/2,-d/2,1.4],[w/2,-d/2,1.4],[w/2,d/2,1.4],[-w/2,d/2,1.4],[-w*.19,off,rise],[w*.19,off,rise]],float)
 v[1,2]+=1.2;v[5,2]+=1.2;v[2,2]+=2.3;v[6,2]+=2.3;v[3,2]+=.6;v[7,2]+=.6
 f=[[0,2,1],[0,3,2],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7],[4,5,9],[4,9,8],[5,6,9],[6,7,8],[6,8,9],[7,4,8]]
 from manifold3d import Mesh
 r=Manifold(Mesh(v.astype('float32'),np.array(f,dtype='uint32')))
 parts.append(r.rotate((0,0,ang)).translate((x,y,z)))
# Zig-zag slab traced approximately from official completion aerial. Three pavilion zones.
outline=[(-67,-21),(-54,-33),(-24,-26),(-4,-13),(14,-17),(35,-9),(62,6),(68,28),(24,28),(0,18),(-15,26),(-47,17),(-68,9)]
add(0,0,0,150,100,2.5)
# Main enclosed dining floor is recessed from the continuous overhanging terrace edge.
body=[(-63,-18),(-54,-29),(-25,-22),(-5,-9),(14,-13),(33,-5),(55,8),(59,23),(23,23),(0,14),(-15,21),(-46,13),(-63,6)]
parts.append(poly(body,2.4,10.3));parts.append(poly(outline,12,2.4))
# Light but printable parapets follow the irregular terrace outline, interrupted by stairs.
for i,p in enumerate(outline):
 q=outline[(i+1)%len(outline)]
 if i not in [5,6]:parts.append(beam(p,q,1.15,2.1,14.1))
# Long landside colonnade reflects completed red-brick bays, not an invented rear clone.
front=[(-63,-18),(-54,-29),(-25,-22),(-5,-9),(14,-13),(33,-5)]
for a,b in zip(front,front[1:]):
 dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);n=max(2,round(l/5.7))
 for t in np.linspace(0,1,n+1):
  x=a[0]+dx*t;y=a[1]+dy*t
  parts.append(box(x,y-1,2.4,1.8,2.1,10))
 # recessed glazing band, set behind posts
 nx,ny=dy/l,-dx/l
 cuts.append(beam((a[0]-nx*.6,a[1]-ny*.6),(b[0]-nx*.6,b[1]-ny*.6),1.7,7.2,4.1))
# Low glazing on the lake-facing zig-zag wing; no copied front colonnade.
for a,b in zip([(-63,6),(-46,13),(-15,21),(0,14),(23,23)], [(-46,13),(-15,21),(0,14),(23,23),(59,23)]):
 dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);n=max(2,int(l/6))
 for t in np.linspace(.1,.9,n):
  x=a[0]+dx*t;y=a[1]+dy*t
  cuts.append(box(x,y,4.4,4,2.2,6))
# Upper left shop pavilion with offset paired roof planes.
left=box(0,0,14.2,22,17,12).rotate((0,0,12)).translate((-48,-7,0));parts.append(left)
for x in [-7,0,7]:cuts.append(box(x,-8.5,16,4.5,3,7.7).rotate((0,0,12)).translate((-48,-7,0)))
for x in [-7,0,7]:cuts.append(box(x,8.5,16,5.4,3,7.7).rotate((0,0,12)).translate((-48,-7,0)))
roof(-48,-7,26,26,21,5.3,12,2.5)
# Central open pavilion: four robust columns carry the hipped roof.
for x in [-21,-7]:
 for y in [-4,8]:add(x,y,14.2,1.8,1.8,11.8)
roof(-14,2,25,20,17,5.1,-8)
# Right shop is a larger irregular two-roof cluster, as seen in completion aerial.
parts.append(box(0,0,14.2,25,19,12).rotate((0,0,27)).translate((15,2,0)))
parts.append(box(0,0,14.2,14,18,11).rotate((0,0,27)).translate((28,9,0)))
roof(14,2,26,29,23,5.5,27,-2.2);roof(29,10,25,16,22,5,27,1.5)
for x in [-8,0,8]:cuts.append(box(x,-9.5,16,5.6,3,7).rotate((0,0,27)).translate((15,2,0)))
for x in [-8,0,8]:cuts.append(box(x,9.5,16,5.6,3,7).rotate((0,0,27)).translate((15,2,0)))
# Wide exterior stairs at the eastern tip; 12 supported steps rise to the terrace.
for i in range(12):add(61.3,42.3-i*1.15,2.4,15,1.5,(i+1))
# A raised dividing strip and five rectangular planting recesses in the stair slope.
parts.append(beam((61.3,42.2),(61.3,28.9),1.3,1.1,10.6) ^ box(61.3,36,2.4,2,18,15))
# Two battered support walls under tip, visible in completed photos.
for x in [47,55]:parts.append(poly([(x-1.4,10),(x+1.4,10),(x+4,17),(x+1.2,17)],2.4,9.8))
# Two small deck planters remain solid raised relief rather than fragile individual plants.
for x,y,w,d in [(-31,4,12,3.2),(40,17,12,3.2)]:add(x,y,14.3,w,d,1.1)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(0.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
