"""Original CTU bounded source-based exterior draft, metres then 1.75mm/m."""
from pathlib import Path
import numpy as np,trimesh,json
from manifold3d import Manifold,CrossSection
R=Path(__file__).parent;P=[];C=[];GL=1.4
# local front=southeast=-y; positive y towards teaching block; not a surveyed north basis.
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z+GL))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,48).translate((x,y,z+GL))
def beam(a,b,w):
 a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v);v/=L;xx=np.cross([0,1,0],v)
 if np.linalg.norm(xx)<.1:xx=np.cross([1,0,0],v)
 xx/=np.linalg.norm(xx);yy=np.cross(v,xx)
 return Manifold.cube((w,w,L)).translate((-w/2,-w/2,0)).transform(np.column_stack([xx,yy,v,a+[0,0,GL]]))
def gable(x,y,z,w,d,h):
 # triangular prism along y
 q=CrossSection([np.array([[-w/2,0],[w/2,0],[0,h]])]).extrude(d).rotate((90,0,0)).translate((x,y+d/2,z+GL));return q
P.append(box(0,0,-GL,60,51,GL))
P.append(box(0,0,0,48,38,22))
# Tall rear-set body with narrower crown footprint; side setbacks visible on back photo.
P += [box(0,2.5,21.6,35,33,34.4),box(-19,6,21.5,4,26,18),box(19,6,21.5,4,26,18)]
for x in [-19,19]:P.append(box(x,12,39,4,14,5))
# Rim of podium terrace, no full added storey.
for x in [-23.5,23.5]:P.append(box(x,0,22,1,38,1.2))
P += [box(0,-18.5,22,48,1,1.2),box(0,18.5,22,48,1,1.2)]
# Source front lower multilevel glass with distinct side narrow bays.
for z,h in [(3,8),(12,3.4),(16.5,3.2),(20,1.2)]:
 for x,w in [(-20,2.2),(-14,6),(-7,5),(0,5),(7,5),(14,6),(20,2.2)]:
  if not(abs(x)<10 and z<19):C.append(box(x,-19.02,z,w,.65,h))
# Tall front three central broad glazed bands; flanking punched piers.
for z in [25,29,33,37,41,45,49]:
 for x in [-8,8]:C.append(box(x,-14.04,z,6.0,.65,2.8))
 C.append(box(0,-14.04,z+.4,7.2,.7,1.65))
 for x in [-14.4,14.4]:C.append(box(x,-14.04,z,2.0,.55,2.4))
for x in [-14.4,14.4]:C.append(box(x,-14.04,52.5,2.2,.55,2.5))
for x in [-8,8]:C.append(box(x,-14.04,52.4,5.7,.55,2.7))
P.append(box(0,-14.2,51.8,7.8,.9,4.5))
# Back: pronounced continuous central vertical glazing and narrow vertical strips.
C.append(box(0,19.04,8,8,.8,42.5))
C.append(Manifold.cylinder(.9,4,4,64).rotate((90,0,0)).translate((0,19.55,50.5+GL)))
for x in [-6.4,6.4,-11.6,11.6]:C.append(box(x,19.04,4,1.25,.65,48))
for z in [25,29,33,37,41,45,49,53]:
 for x in [-15,15]:C.append(box(x,19.04,z,2.1,.55,2.5))
# Source continuous back glazing: divide shallow glass with rooted solid mullions after subtraction.
for z in [4,8,12,16,20]:
 for x,w in [(-15,4.5),(-8,2),(0,5.2),(8,2),(15,4.5)]:C.append(box(x,19.04,z,w,.65,2.6))
for x in [-19,19]:
 for z in [25,29,33,37]:C.append(box(x,19.04,z,3,.55,2.7))
# Front top round medallion, rather than an extra identical central window.
C.append(Manifold.cylinder(.7,1.1,1.1,48).rotate((90,0,0)).translate((0,-14.0,53.7+GL)))
# Side-visible windows below setbacks, limited to seen bands, not copied decorative front.
for side in [-1,1]:
 for z in [6,10,14,18,25,29,33,37]:
  for y in [-10,-4,2,8,14]:C.append(box(side*(24.02 if z<22 else 21.02),y,z,.6,3.5,2.6))
# Top cornice, four corner lanterns with low pyramidal roofs.
P.append(box(0,2.5,55.6,36,34,.9))
for x in [-14,14]:
 for y in [-10.5,12.5]:
  P.append(box(x,y,56,5.3,5.3,3.3));P.append(box(x,y,58.75,5.8,5.8,.65));C.append(box(x,y-2.67,56.7,3.2,.65,1.8));C.append(box(x,y+2.67,56.7,3.2,.65,1.8))
  
  for z0,z1,r0,r1 in [(0,.35,4.1,2.9),(.35,1.25,2.9,1.55),(1.25,2.2,1.55,.6)]:
   P.append(Manifold.cylinder(z1-z0,r0,r1,4).rotate((0,0,45)).translate((x,y,59.2+z0+GL)))
# Central square crown plinth and genuinely 3D open pyramidal steel crown.
P.append(box(0,1,59.15,10.8,10.8,1.1))
P.append(Manifold.cylinder(3.4,6.3,6.3,8).rotate((0,0,22.5)).translate((0,1,56+GL)))
# Bounded solid-backed undulating crown parapet, confirmed in front and reverse high angles.
for y,phase in [(-4.6,0),(6.6,3.14159)]:
 pts=[[-5.6,0],[5.6,0]]+[[float(x),3.2-1.15*np.sin((float(x)/11.2)*np.pi+phase)] for x in np.linspace(5.6,-5.6,25)]
 P.append(CrossSection([np.array(pts)]).extrude(.85).rotate((90,0,0)).translate((0,y+.4,56+GL)))
# Crown side glass is represented by solid-backed undulating surface; no cut that severs its root.
for x in [-4.7,4.7]:
 for y in [-3.7,5.7]:P.append(beam((x,y,60),(0,1,71.5),.9))
for z,r in [(60,4.7),(64,3.1)]:
 for a,b in [((-r,1-r,z),(r,1-r,z)),((r,1-r,z),(r,1+r,z)),((r,1+r,z),(-r,1+r,z)),((-r,1+r,z),(-r,1-r,z))]:P.append(beam(a,b,.8))
P.append(cyl(0,1,69.2,.9,3.1))
P.append(Manifold.batch_boolean([Manifold.sphere(1.3,32).translate((0,1,72+GL)),box(0,1,70,4,4,2.95)],2))
# Two rounded rear rooftop service heads seen in both aerial epochs.
for x in [-8,8]:P.append(cyl(x,13.5,56,3.1,2.2))
P.append(box(0,14,56,17,4,2.2))
# Two source-visible lower flanking arched glass openings with stout rooted edge columns.
for x in [-14.5,14.5]:
 C.append(box(x,-19.4,1.3,6.6,2.7,6.9))
 C.append(Manifold.cylinder(2.7,3.3,3.3,48).rotate((90,0,0)).translate((x,-18.05,8.2+GL)))
 for dx in [-3.7,3.7]:P.append(cyl(x+dx,-19.6,1.3,.65,9.6))
# Formal entrance porch: deep central arch between paired giant columns.
P.append(box(0,-20.8,1.3,20,6,12.7))
C.append(box(0,-22.4,1.3,8.2,10,7.5))
arch=Manifold.cylinder(10,4.1,4.1,64).rotate((90,0,0)).translate((0,-17.4,8.7+GL));C.append(arch)
P.append(box(0,-20.8,12.5,22.4,6.5,1.8))
P.append(Manifold.batch_boolean([gable(0,-20.8,14.2,22,6,3.0),box(0,-20.8,14.1,23,7,2.8)],2))
for x in [-8,-5.8,5.8,8]:
 P += [cyl(x,-24.0,1.3,.75,7.1),box(x,-24,1.3,2,2,.8),box(x,-24,8.1,2,2,.8)]
for x in [-6.9,6.9]:
 P.append(box(x,-21.4,8.5,5.5,6.8,1.0))
 C.append(box(x,-23.8,10.0,1.65,1,1.8))
 C.append(Manifold.cylinder(1,.825,.825,32).rotate((90,0,0)).translate((x,-23.3,11.8+GL)))
for i in range(6):P.append(box(0,-23.3-i*.55,0,24+i*.08,1+i*1.1,1.3-i*.18))
solid=Manifold.batch_boolean(P,0)-Manifold.batch_boolean(C,0)
F=[]
# Source-linked flanking columns require genuine broad solid back roots after shallow glazing cuts.
for x in [-18.2,-10.8,10.8,18.2]:F.append(box(x,-19.05,1.3,1.0,1.6,9.6))
for z in np.arange(8,51,3.2):F.append(box(0,18.8,float(z),8.05,.65,.6))
for x in [-2.6,0,2.6]:F.append(box(x,18.8,8,.6,.65,42.5))
for x in [-6.4,6.4,-11.6,11.6]:
 for z in np.arange(23,52,3.6):F.append(box(x,18.9,float(z),1.7,.6,.55))
# Tall front paired narrow mullions and three major central groups.
for z in [25,29,33,37,41,45,49,52.4]:
 for x in [-8,8]:
  for dx in [-1.7,1.7]:F.append(box(x+dx,-13.9,z,.6,.65,2.8))
# Raised source-backed border around the tall rear glass and its arched head.
for x in [-4.35,4.35]:F.append(box(x,19.1,8,.95,.8,42.7))
ro=Manifold.cylinder(.65,4.7,4.7,64).rotate((90,0,0)).translate((0,19.45,50.5+GL))
ri=Manifold.cylinder(.85,4,4,64).rotate((90,0,0)).translate((0,19.55,50.5+GL))
F.append((ro-ri)-box(0,19.1,44,11,2,6.5))
solid=solid+Manifold.batch_boolean(F,0)
m=solid.to_mesh();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:,:3]*1.75,faces=np.asarray(m.tri_verts),process=False);mesh.export(R/'model.stl')
(R/'draft-parameters.json').write_text(json.dumps({'status':'bounded draft not freeze','mm_per_m':1.75,'podium':[48,38,22],'upper':[35,33,56],'crown_top':73,'height_sources':'55.95/75.35 third-party only; prototype differs, not measured','extents_mm':mesh.extents.tolist()},indent=2))
print(mesh.extents,mesh.is_watertight,len(mesh.split()))
