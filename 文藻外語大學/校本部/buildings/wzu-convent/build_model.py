"""Photo-derived public exterior study. Millimetres; dimensions are visual estimates.
Run with Python 3.12 and requirements.txt. No survey or interior data used.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def arch(x,y,z,w,h,depth):
 r=w/2; spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts += [(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
 return profile(pts,y,depth)
def arch_cut(x,y,z,w,h,depth):cuts.append(arch(x,y,z,w,h,depth))
def arch_trim(x,y,z,w,h):
 # Backed relief ring, fused into the wall, not a separate floating shell.
 details.append(arch(x,y,z,w+1.7,h+.85,1.7)-arch(x,y-.1,z-.2,w,h+.2,2.3))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.72,.03)).translate((x,y,z)))
def column(x,y,z,r,h):parts.append(Manifold.cylinder(h,r,r,circular_segments=24).translate((x,y,z)))
def step(x,y,w,n=3):
 for i in range(n):add(x,y+i*1.4,2.8,w,1.7,.7*(i+1))
# Convent/faculty residence: four-storey brick grid, sail-like chapel face and open tower crown.
add(0,0,0,150,119,3)
add(-4,9,2.8,116,62,93)
# Three clear window ranks above chapel, concealed lower-right panes deliberately omitted.
for x in [-48,-24,0,24]:
 for z in [36,59,81]:
  bow=31+19.7*((x+42)/84)**2 if -42<x<42 else 0
  zz=max(z,bow+.8) if z==36 else z
  if zz<z+11:cut(x,-22,zz,12,3.2,z+11-zz)
for x in [-60,-36,-12,12,36]:add(x,-22.5,26,3,2,69)
for z in [51,74,94]:add(-8,-22.5,z,108,2,3)
# Main rectangular tower with genuinely open four-panel crown above roof.
add(54,-12,2.8,19,20,132.2)
for x in [49.5,58.5]:
 for z in [100,118]:cut(x,-12,z,6,23,14)
# Slightly rising curved upper edge of low chapel facade, interpreted from direct photograph.
xs=list(np.linspace(-43,40,35));curve=[(x,31+19.7*((x+43)/83)**2) for x in xs]
parts.append(profile([(-43,3),(40,3)]+curve[::-1],-27,22))
for x in [-34,-24,-14,-4,6,16,26]:
 top=31+19.7*((x+43)/83)**2
 cut(x,-38,10,3.8,3.2,top-15)
# Entrance on left of chapel sail remains a recessed porch, not sealed flush.
cut(-52,-22,3,14,8,19)
add(-51,-25,22,24,12,2.2)
for i in range(4):add(-51,-37+i*2,2.8,24,2.3,.8+i*.8)
# Rear and unobserved side fenestration intentionally simplified; neighboring spiritual centre omitted.

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
