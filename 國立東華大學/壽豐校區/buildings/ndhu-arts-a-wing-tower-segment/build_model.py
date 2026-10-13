"""東華藝術學院A棟折翼與高塔段 — 2021外觀參考，非全院。
Hand-authored miniature-mm CSG; no imported mesh. Frame follows official A-wing plan,
not geographic north. +Y is garden-facing exterior, -Y is courtyard-facing.
B/C wings, oval entry hall, concert hall, bridges and site landscaping are omitted.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P={'base_mm':[150,88,2.5],'floor_pitch':8,'body_top':36.5,'tower_top':60,'bend_degrees':27,'minimum_support':1.6}
parts=[];cuts=[];postparts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def poly(pts,z,h):return CrossSection([pts]).extrude(h).translate((0,0,z))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,64).translate((x,y,z))
def at(m,x,y,a):return m.rotate((0,0,a)).translate((x,y,0))
def rounded_roof(x,y,z,w,d,angle,skylights=True):
 # Barrel-like folded metal roofs with rolled eaves, retained as solid printable roof.
 ys=np.linspace(-d/2,d/2,35)
 zz=1.1+3.0*np.cos(ys/(d/2)*math.pi/2)
 pts=[(-d/2,0),(d/2,0)]+list(zip(ys[::-1],zz[::-1]))
 roof=CrossSection([pts]).extrude(w).rotate((90,0,90)).translate((-w/2,0,z))
 parts.append(at(roof,x,y,angle))
 # long elevated roof spine, visible in 2021 completion aerial; rounded roof not a gable.
 parts.append(at(box(0,1.9,z+3.2,w,1.6,2.1),x,y,angle))
 # Only two skylight wells per bank, not an invented repetitive roof window array.
 for xx in ([-5.0,1.7] if skylights else []):cuts.append(at(box(xx,-1,z+1.8,4.8,5.7,3.2),x,y,angle))
add(0,-8,0,*P['base_mm'])
# Bent A wing: short high-tower limb plus long garden-facing limb.
wings=[(-29,-14.4,63,20,27),(32,0,64,20,0)]
for x,y,w,d,a in wings:
 parts.append(at(box(0,0,2.4,w,d,25.4),x,y,a))
 parts.append(at(box(0,2.5,27.6,w,15,8.9),x,y,a))
 # Upper floor retreats from the court, leaving a substantial open roof terrace.
 ar=math.radians(a)
 rounded_roof(x-2.5*math.sin(ar),y+2.5*math.cos(ar),36.2,w+1.8,16.6,a)
 # Lower projection on the tower-side portion, visible in the court close-up.
 parts.append(at(box(-w/4,-12.7,2.4,w/2,5.8,17.4),x,y,a))
 # Garden facade: lower narrow window row, two tall rows and upper balcony/window bays.
 for z,h in [(4.1,5.9),(12.1,6.2),(20.1,6.2),(28.1,6.7)]:
  for xx in np.arange(-w/2+4,w/2-2,5.6):
   if (x>0 and xx < -w/2+10) or (x<0 and xx>w/2-10):continue
   cuts.append(at(box(xx,10.05,z,3.3,2.6,h),x,y,a))
   # robust integral lintel, no tiny sill corner chips
   parts.append(at(box(xx,10.2,z+h,3.9,1.8,1.0),x,y,a))
 # Court facade has staggered open terraces, not repeated deep arcades.
 for z in [4.1,12.1,20.1,28.1]:
  for xx in np.arange(-w/2+4,w/2-2,6.2):
   if (x>0 and xx < -w/2+10) or (x<0 and xx>w/2-10):continue
   yy=-15.6 if z<19 and xx<0 else (-5.05 if z>27 else -10.05)
   cuts.append(at(box(xx,yy,z,3.6,2.1,5.8),x,y,a))
   postparts.append(at(box(xx,yy-.15,z+5.8,4.0,1.8,1.0),x,y,a))
 # Parapets stand on actual terrace decks and are deliberately thicker than rails.
 for xx0,yy,z,ww in [(0,-9.9,27.6,w-2),(-w/4,-15.2,19.6,w/2-1)]:
  postparts.append(at(box(xx0,yy,z,ww,1.6,1.8),x,y,a))
  for xx in np.arange(xx0-ww/2+1.1,xx0+ww/2,8):
   postparts.append(at(box(xx,yy,z,2.2,2.0,2.7),x,y,a))
# Corner/circulation bay at the kink projects toward garden. Angular face matches plan.
core=[(-9,-10),(7,-10),(9,13),(1,16),(-10,12)]
parts.append(poly(core,2.4,37.5));parts.append(poly([(-10,-11),(8,-11),(10.2,13.7),(1,17.3),(-11.2,12.6)],39.4,1.4))
# Three open-looking recessed gallery mouths, with solid backing wall.
for z in [12,20,28]:cuts.append(box(-.8,13.4,z,11.2,7.4,6.2))
for xx in [-8.2]:
 for z in [5,13,21,29]:cuts.append(box(xx,13.3,z,1.6,5.4,4.8))
# Garden-side stair glazing at the cut terminal of A wing, omit adjoining B wing.
add(64,0,2.4,5,20,33.6)
for z in [4.2,12.2,20.2,28.2]:cuts.append(box(64,10.2,z,3.0,1.8,6.0))
# High observation stair tower at the opposite end, oval/polygonal with broad vertical glazing.
tx,ty=-61,-30
pts=[(-5.5,-3.5),(-3.3,-6),(3.3,-6),(5.5,-3.5),(5.5,3.5),(3.3,6),(-3.3,6),(-5.5,3.5)]
parts.append(poly([(tx+x,ty+y) for x,y in pts],2.4,53.0))
# Broad glass side bands become two supported shallow recesses, with visible robust transoms.
for side in [-1,1]:
 for z in np.arange(5,51,5.8):
  if side>0 and z<38:continue
  cuts.append(box(tx+side*5.4,ty,z,1.7,5.7,4.3))
# Three small triangular apertures in the solid tower wall, retained as shallow recesses.
for i,z in enumerate([18,30,42]):
 pts=[(-1.3,0),(1.3,0),(0,2.2)] if i!=1 else [(-1.3,1.1),(1.3,0),(1.3,2.2)]
 recess=CrossSection([pts]).extrude(1.9).rotate((90,0,0)).translate((tx,ty+6.4,z))
 cuts.append(recess)
# Thick flared crown, open to top; no needle antennae or fragile glass roof framework.
crown=Manifold.cylinder(4.4,6.3,8.0,8).translate((tx,ty,54.4))
parts.append(crown)
cuts.append(Manifold.cylinder(4.5,4.4,6.1,8).translate((tx,ty,55.5)))
# Shallow notches distinguish the flared canopy fins; every fin remains rooted in the ring.
for xx in [-2.3,2.3]:
 for yy in [-7.0,7.0]:cuts.append(box(tx+xx,ty+yy,57.2,1.1,3.0,2.0))
# Two robust cross beams near top communicate the real canopy braces.
postparts.append(box(tx,ty,56.0,13.8,1.6,1.6));postparts.append(box(tx,ty,56.0,1.6,13.8,1.6))
# Low tower-side room under a rounded roof, attached to the short A-wing tip.
parts.append(at(box(0,0,2.4,21,12,11.3),-56,-37,27))
rounded_roof(-56,-37,13.4,22.4,13.2,27,False)
# Three porthole-like windows retained as stout circular recesses, not separate discs.
for xx in [-6.4,0,6.4]:
 c=Manifold.cylinder(2.2,1.4,1.4,32).rotate((90,0,0)).translate((xx,-5.3,10.8))
 cuts.append(at(c,-56,-37,27))
# All negative volumes applied after union; reject detached enclosed shells rather than repair.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in postparts:solid=solid+p
assert len(solid.decompose())==1, [(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(0.001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
