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

def ell(x,y,z,rx,ry,h):return Manifold.cylinder(h,1,1,circular_segments=128).scale((rx,ry,1)).translate((x,y,z))
def circle_cut(x,y,z,r,d):cuts.append(Manifold.cylinder(d,r,r,circular_segments=24).rotate((90,0,0)).translate((x,y+d/2,z)))
def ramp_x(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x+w/2,z+h)],y,d))
# N5: exterior massing based on official front/field-side photographs.
add(0,0,0,150,132,3)
parts.append(ell(0,0,2.8,64,50,39))
# Broad low stadium dome; whole interior remains solid, not nested shells.
dome=Manifold.sphere(1,128).scale((68,54,13)).translate((0,0,43))
parts.append(dome ^ box(0,0,42,140,120,20))
parts.append(ell(0,0,41,68,54,2.5))
# Glazed clerestory band beneath roof rim, shallow exterior relief.
for deg in range(0,360,12):
 t=math.radians(deg); x=63.7*math.cos(t); y=49.7*math.sin(t)
 if y<0 and abs(x)>37:continue
 cuts.append(box(0,0,36,2.3,1.6,4).rotate((0,0,deg-90)).translate((x,y,0)))
# Front portal towers with horizontal sunshade strips.
for x in [-48,48]:
 add(x,-32,2.8,15,19,45)
 cut(x,-41.5,13,10.5,2,32)
 for z in np.arange(14,45,3):add(x,-42,z,11.6,2.4,1)
# Two rows of circular portholes on the curved entrance facade.
for deg in range(245,296,10):
 t=math.radians(deg);x=63.7*math.cos(t);y=49.7*math.sin(t)
 # Cylinder local z points normal to the ellipse at the observed front.
 a=math.degrees(math.atan2(y/(50**2),x/(64**2)))
 for z in [22,30]:
  c=Manifold.cylinder(3.2,1.6,1.6,circular_segments=24).rotate((0,90,0)).rotate((0,0,a)).translate((x-1.6*math.cos(math.radians(a)),y-1.6*math.sin(math.radians(a)),z))
  cuts.append(c)
# Entrance window band, a backed shallow arc relief.
for deg in range(239,302,7):
 t=math.radians(deg);x=64*math.cos(t);y=50*math.sin(t)
 cuts.append(box(0,0,4,4.3,2,13).rotate((0,0,deg-90)).translate((x,y,0)))
parts.append(ell(0,0,17,69,55,1.5) ^ box(0,-32,16,145,50,4))
# Field-side recessed sheltered zone and clear strong columns shown by rear photo.
cut(0,46,17,83,16,15)
for x in [-24,24]:details.append(Manifold.cylinder(18,3,3,circular_segments=24).translate((x,43,15)))
for x in [-55,-43,-31,-19,-7,7,19,31,43,55]:
 cut(x,48,5,6,7,7)
# Two outside stair approaches simplified into robust joined steps.
for x in [-60,60]:
 for i in range(9):add(x,-52+i*2.9,2.9,12,3.2,1.5*(i+1))
step(0,-59,44,4)

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
