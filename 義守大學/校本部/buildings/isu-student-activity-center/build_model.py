"""Original bounded exterior draft: ISU student activity centre, 2022/2024 sources.
Physical dimensions are image estimates, not surveyed. Model output is millimetres.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,Mesh64,OpType
R=Path(__file__).parent;S=2.7;GL=4.7;parts=[];cuts=[];porch_roof=[]
def pt(x,y,z):return (x*S,y*S,GL+z*S)
def cube(x,y,z,w,d,h):return Manifold.cube((w*S,d*S,h*S)).translate(((x-w/2)*S,(y-d/2)*S,GL+z*S))
def polyprism(poly,bottom,top):
 n=len(poly);v=[pt(x,y,bottom(x,y))for x,y in poly]+[pt(x,y,top(x,y))for x,y in poly];f=[]
 for j in range(1,n-1):f.extend([[0,j+1,j],[n,n+j,n+j+1]])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,n+j],[i,n+j,n+i]])
 o=Manifold(Mesh64(np.array(v,float),np.array(f,np.uint64)));assert str(o.status()).endswith('NoError');return o
# Base longest150mm. Local GL is north entrance/pool platform reference.
parts.append(Manifold.cube((150,145,2)).translate((-75,-56.5,0)))
# North at +Y; south perimeter slopes down. This is terrain illustration only.
parts.append(polyprism([(-26,-19),(26,-19),(26,-8),(-26,-8)],lambda x,y:-1,lambda x,y:(y+8)/11))
parts.append(cube(0,12,-1,52,40,1))
# Main lower volume, upper two-window-band brick block. B1+5F is NOT six equal floors.
parts.append(cube(0,0,-1,39.2,26.8,10.4))
parts.append(cube(0,0,9.2,43.2,30.3,8.6))
# East pool-side platform only; pool and theatre are excluded.
parts.append(cube(22.0,-1,-1,4.8,31,1.1))
# Visible northeast low flat connector, approximate height4.5m (not surveyed).
parts.append(cube(16.7,21.5,-1,7.0,15.0,5.5))
parts.append(cube(16.7,21.5,4.4,7.4,15.4,.55))
# Hip roof: measured IMAGE eave envelope44.5x31.5m; ridge23m is photo-proportion trial.
eave=17.8;ridge=23.0
v=[pt(-22.25,-15.75,eave),pt(22.25,-15.75,eave),pt(22.25,15.75,eave),pt(-22.25,15.75,eave),pt(-11.5,0,ridge),pt(11.5,0,ridge)]
# Explicit1.1mm vertical eave edge: no zero-thickness perimeter or touching-only fascia.
v += [pt(x,y,eave-1.1/S)for x,y in [(-22.25,-15.75),(22.25,-15.75),(22.25,15.75),(-22.25,15.75)]]
f=[[0,1,5],[0,5,4],[1,2,5],[2,3,4],[2,4,5],[3,0,4],[6,9,8],[6,8,7]]
for i in range(4):
 j=(i+1)%4;f.extend([[i+6,j+6,j],[i+6,j,i]])
roof=Manifold(Mesh64(np.array(v),np.array(f,np.uint64)));assert str(roof.status()).endswith('NoError')
# South equipment recess cuts roof only; no evidence it continues through all walls.
roof=roof-cube(6,-14.5,17.3,14,10,12)
# Printing-only ridge truncation 0.25mm vertical, about1.52mm flat transverse cap.
roof=roof-cube(0,0,ridge-.25/S,60,50,10)
parts.append(roof)

# Eave and visible inter-storey belts, kept rooted to the main wall.
for z in [9.05,13.25,17.4]:parts.append(cube(0,0,z,43.7,30.8,.40))
# North three low raised sloping sheets follow the visible main slope.
# South narrow dark triangles have no proven boxed volume; omit uncertain fine detail.
roofz=lambda y:eave+(ridge-eave)*(1-abs(y)/15.75)
for x in [-9,0,9]:
 # Printing-only upper edge truncation0.4mm, local flat width1.21mm.
 ybreak=6+(.4/S)/((ridge-eave)/15.75);cap=roofz(6)+.55-.4/S
 for lo,hi in [(6,ybreak),(ybreak,10)]:
  p=[(x-3,lo),(x+3,lo),(x+3,hi),(x-3,hi)]
  parts.append(polyprism(p,lambda a,b:roofz(b)-.15,lambda a,b:min(roofz(b)+.55,cap)))
# Equipment within open roof notch: simplified low platform and two backed blocks.
parts.append(cube(6,-12.0,17.65,13.4,5.3,.6))
parts.append(cube(9,-12.8,18.1,3.5,2.7,2.6));parts.append(cube(3,-12.3,18.1,4.3,2.4,1.0))
# Recessed glazing, not through-holes. Window bays use photos, not equal guessed floors.
for z in [10.8,14.6]:
 for x in [-16.7,-10.0,-3.3,3.4,10.1,16.8]:
  cuts.append(cube(x,15.1,z,5.2,.7,1.55))
 for side in [-1,1]:
  for y,w in [(-11.8,1.7),(-5.3,5.2),(3.6,5.2),(11.7,1.7)]:
   cuts.append(cube(side*21.55,y,z,.7,w,1.55))
# Lower double-height colonnade across north and pilasters on visible east/west sides.
for x in np.linspace(-19.1,19.1,17):
 parts.append(Manifold.cylinder(9.35*S,.26*S,.26*S,32).translate(pt(x,14.15,0)))
for side in [-1,1]:
 for y in [-12,-7,-2,3,8,12]:parts.append(cube(side*19.475,y,.25,.90,.55,9.2))
for z in [1.0,6.1]:
 for x in np.linspace(-17.9,17.9,16):
  if abs(x+4)<4:continue
  cuts.append(cube(x,13.32,z,1.55,.55,1.75))
 for side in [-1,1]:
  for y,w in [(-11.8,1.8),(-5.3,4.8),(3.6,4.8),(11.7,1.8)]:
   cuts.append(cube(side*19.5,y,z,.6,w,1.75))
# Deep entrance has rear glazing and four front supports, not a solid gable block.
parts.append(cube(-4,13.30,.6,7.0,.45,8.4))
for x in [-7,-5.5,-4,-2.5,-1]:parts.append(cube(x,13.63,.6,.4,.35,8.4))
for z in [3.4,5.8,8.2]:parts.append(cube(-4,13.63,z,7.0,.35,.35))
for x,w in [(-9.7,.72),(-8.2,1.40),(.2,1.40),(1.7,.72)]:
 if w<1:parts.append(Manifold.cylinder(10.2*S,w/2*S,w/2*S,40).translate(pt(x,20.5,.6)))
 else:parts.append(cube(x,20.5,.6,w,w,10.2))
# Recessed side/back supports and heavy horizontal beam.
for x in [-8.2,.2]:parts.append(cube(x,14.1,.6,1.4,1.8,10.2))
porch_roof.append(cube(-4,17.4,10.35,13.2,8.4,.65))
# Two sloping 1.6mm roof boards, ridge height14.4m. Real empty space below.
for p in [[(-10.5,13.3),(-4,13.3),(-4,21.6),(-10.5,21.6)],[(-4,13.3),(2.5,13.3),(2.5,21.6),(-4,21.6)]]:
 zf=lambda x,y:14.4-abs(x+4)*3.4/6.5
 porch_roof.append(polyprism(p,lambda x,y:zf(x,y)-1.6/S,zf))
# Triangular glazed gable volume is internally solid to avoid a sealed hidden cavity.
# The tall entrance below remains open; front glazing uses rooted shallow mullions.
gable=[(-10.1,10.9), (2.1,10.9),(-4,14.1)]
vv=[pt(x,y,z)for y in [13.3,21.48]for x,z in gable];ff=[[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]]
glass=Manifold(Mesh64(np.array(vv),np.array(ff,np.uint64)[:,::-1]));assert str(glass.status()).endswith('NoError') and glass.volume()>0;porch_roof.append(glass)
# Gable glazing mullions: rooted shallow relief, not open wire.
for xx in [-8,-4,0]:
 a=np.array(pt(xx,21.4,10.9));b=np.array(pt(-4,21.4,14.1));v=b-a;length=np.linalg.norm(v);angle=np.degrees(np.arctan2(v[0],v[2]))
 parts.append(Manifold.cylinder(length,.22*S,.22*S,12).rotate((0,angle,0)).translate(a))
# Continuous entrance platform grounds all four front and rear supports.
parts.append(cube(-4,18.3,0,15.0,10.0,.6))
# North entry steps rise0.6m only; southern B1 exposure follows conservative terrain.
for i in range(3):parts.append(cube(-4,23-i*.65,0,15.0,3.3-i*.65,.2*(i+1)))
# Cut glazing BEFORE adding frames, retaining backed solids.
solid=Manifold.batch_boolean(parts,OpType.Add)
# Restrict window cuts to shallow front zones; frames reconstructed after cuts below.
for c in cuts:solid=solid-c
for board in porch_roof:solid=solid+board # Wall-window cuts must not sever the projecting roof root.
for x in [-8.2,.2]:solid=solid+cube(x,14.1,.6,1.4,1.8,10.2)
# Restore uninterrupted side pilasters after window recesses: cuts must not leave thin outer strips.
for side in [-1,1]:
 for y in [-12,-7,-2,3,8,12]:solid=solid+cube(side*19.475,y,.25,.90,.55,9.2)
# Thin pane bars are added after recesses; all overlap backing at least0.12m.
for z in [10.8,14.6]:
 for x in [-16.7,-10,-3.3,3.4,10.1,16.8]:
  for dx in [-1.73,-.87,0,.87,1.73]:solid=solid+cube(x+dx,14.73,z,.40,.6,1.55)
  solid=solid+cube(x,14.73,z+1.0,5.2,.57,.32)
for z in [1.0,6.1]:
 for x in np.linspace(-17.9,17.9,16):
  if abs(x+4)>=4:solid=solid+cube(x,13.1,z+.95,1.55,.55,.30)
for z in [10.8,14.6]:
 for side in [-1,1]:
  for y,w in [(-11.8,1.7),(-5.3,5.2),(3.6,5.2),(11.7,1.7)]:
   for dy in ([0] if w<2 else [-1.56,-.52,.52,1.56]):solid=solid+cube(side*21.36,y+dy,z,.65,.40,1.55)
   solid=solid+cube(side*21.36,y,z+1.0,.60,w,.32)
assert len(solid.decompose())==1,[(o.volume(),o.bounding_box())for o in solid.decompose()]
m=solid.to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=False);mesh.export(R/'model.stl');print(mesh.extents,mesh.volume,mesh.is_watertight)
