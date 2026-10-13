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
# NTUT Red House, exterior miniature after 2017 restoration.
# x is cross-gable, y is ridge direction; the restored east entry faces -Y.
# Public university photos + city cultural-tour photos establish all four elevations.
# Dimensions/proportions are visual estimates, not measurements.
add(0,0,0,108,150,3)
add(0,4,2.8,86,116,74.2)
# Dressed foundation, full-height brick buttress pilasters and paired corbel caps.
add(0,4,3,88,118,8.6)
for yy in [-54,62]:
 for x in [-42,-26,-8.7,8.7,26,42]:
  add(x,yy,10.8,3.3,3.1,65.4)
  add(x,yy,73.4,4.7,4.0,3.6)
for x in [-43,43]:
 for yy in [-53,-35,-15.5,4,23.5,43,61]:
  add(x,yy,10.8,3.0,3.3,65.4)
  add(x,yy,73.4,4.0,4.7,3.6)
# Cut actual openings rather than decorate an uninterrupted box. Fine muntins
# remain backed by the solid wall, and are thickened to 1.2 mm for this miniature.
def endwindow(x,y,z,w=9.7,h=21):
 cut(x,y,z,w,4.2,h)
 details.append(box(x,y+(.7 if y<0 else -.7),z,1.2,2.4,h))
 for zz in [z+6.6,z+13.2]:details.append(box(x,y+(.7 if y<0 else -.7),zz,w,2.4,1.2))
 add(x,y,z-1.8,w+2.0,3.8,1.8)
 add(x,y,z+h,w+1.6,2.9,2.1)
def sidewindow(x,y,z,w=10.7,h=21):
 cut(x,y,z,4.2,w,h)
 details.append(box(x+(.7 if x<0 else -.7),y,z,2.4,1.2,h))
 for zz in [z+6.6,z+13.2]:details.append(box(x+(.7 if x<0 else -.7),y,zz,2.4,w,1.2))
 add(x,y,z-1.8,3.8,w+2.0,1.8)
 add(x,y,z+h,2.9,w+1.6,2.1)
for x in [-17.3,0,17.3]:
 endwindow(x,-54,46)
 endwindow(x,62,46)
 endwindow(x,62,12.0,h=18.0)
for x in [-43,43]:
 for yy in [-25.25,-5.75,13.75,33.25]:
  sidewindow(x,yy,46)
  sidewindow(x,yy,12.0,h=18.0)
  cut(x,yy,35.8,3.4,2.5,4.8) # school-emblem vents simplified as recessed vents
  cut(x,yy,5.4,3.5,3.4,3.4)
for xx in [-17.3,0,17.3]:
 cut(xx,62,35.8,2.5,3.4,4.8)
 cut(xx,62,5.4,3.4,3.5,3.4)
# Continuous cornice and Lombard blind-arch frieze: recessed semicircle motifs
# preserve the rhythmic band without fragile free-standing ornament.
add(0,4,74.8,89,119,2.4)
for yy in [-55,63]:
 for xx in [-36,-31,-21,-16,-11,-4.5,0,4.5,11,16,21,31,36]:
  cuts.append(arch(xx,yy,72.2,3.4,3.2,2.3))
for x in [-44,44]:
 for yy in [-47,-42,-29,-24,-19,-9,-4,1,10,15,20,29,34,39,50,55]:
  c=arch(yy,0,72.2,3.4,3.2,2.3).rotate((0,0,90)).translate((x,0,0));cuts.append(c)
# Tile roof is a solid gable volume. Raised roof ridges stay fused to roof.
gable(0,4,76.6,89,116,23.4)
for xx in [-42,42]:add(xx,4,76.2,2.6,118,2.8)
# Main ridge and symmetrical rendered gable parapets, with small stepped apex.
add(0,4,99.1,2.8,118,2.0)
for yy in [-54.5,62.5]:
 parts.append(profile([(-44.8,76),(44.8,76),(44.8,79.5),(0,103),(-44.8,79.5)],yy,3.0))
 # Coping strip follows both raking edges, not a flat rectangular crown.
 for sign in [-1,1]:
  lo,hi=sorted([sign*44.8,0])
  def zz(x):return 103-abs(x)*23.5/44.8
  parts.append(profile([(lo,zz(lo)),(hi,zz(hi)),(hi,zz(hi)+1.5),(lo,zz(lo)+1.5)],yy,4.0))
 add(0,yy,102.6,3.6,4,3.2)
 # White double pointed-arch attic grille, recessed and solid-backed.
 for x in [-4.9,4.9]:
  pts=[(x-4.8,85.7),(x+4.8,85.7),(x+4.8,90.7),(x,94.2),(x-4.8,90.7)]
  details.append(profile(pts,yy,4.5))
  pts2=[(x-3.2,87),(x+3.2,87),(x+3.2,90),(x,92.2),(x-3.2,90)]
  # This recess is applied after all unions below.
  details[-1]=details[-1]-profile(pts2,yy+(-1.8 if yy<0 else 1.8),1.6)
  for zz2 in [88.2,89.8]:details.append(box(x,yy+(-1.25 if yy<0 else 1.25),zz2,7.4,1.4,1.0))
# Restored east door: one central door, blank lower flanks, portico canopy.
cut(0,-54,3.2,18,4.4,28)
details.append(box(0,-53.2,3.2,1.4,2.6,28))
for x in [-5,5]:
 for z in [10.5,17.5,24.5]:details.append(box(x,-53.2,z,8.5,2.6,1.4))
# Porch platform. Columns explicitly thickened and joined to platform and roof.
add(0,-60.8,2.9,45,20,1.2)
add(0,-61.7,32.6,44,19.5,2.5)
for x in [-18.3,18.3]:
 column(x,-68.5,3.6,1.8,29.6)
 column(x,-68.5,3.4,2.8,2.0)
 column(x,-68.5,28.8,2.8,4.3)
 for z in [5.5,7.0,29.4,31.0]:column(x,-68.5,z,2.15,1.0)
# Hipped porch roof and characteristic central curved eyebrow.
parts.append(CrossSection.square((44,19.5),center=True).extrude(7.3,scale_top=(.03,.03)).translate((0,-61.7,34.7)))
# Semi-circular upstand over the front fascia, rooted into fascia and roof.
parts.append(arch(0,-70.3,33.0,13.0,7.0,2.3))
cuts.append(arch(0,-71.0,32.8,8,4.5,2.5))
column(0,-61.7,41,1.5,3.1)
# Side wall tablet/plaque, without invented legible lettering.
add(12.9,-54.3,13.7,4.2,1.6,14.5)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print("components",[(x.volume(),x.bounding_box()) for x in solid.decompose()]); assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('mm',mesh.extents,'watertight',mesh.is_watertight)
