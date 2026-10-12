"""松園別館主棟，原創公開照片判讀模型。mm；正面 -Y。
二層連續拱廊與日式長坡屋頂。後側為簡化重建，非測量資料。
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import trimesh
import manifold3d as m
P=Path(__file__).resolve().parent
parts=[];cuts=[];after=[];last=[]
def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def block(x,y,z0,z1,w,d):return box(x,y,(z0+z1)/2,w,d,z1-z0)
def arch(x,y,bottom,spring,r,depth):return block(x,y,bottom,spring,2*r,depth)+m.Manifold.cylinder(depth,r,r,48).rotate((90,0,0)).translate((x,y+depth/2,spring))
def gable(x,y,z,w,d,h):return m.Manifold.hull_points([(x+xx,y+yy,z+zz) for xx in [-w/2,w/2] for yy,zz in [(-d/2,0),(d/2,0),(0,h)]])
# Clean, thin landscape display base. Trees are omitted to expose the architecture.
parts += [block(0,0,0,2.8,150,72),block(0,1,2.6,4.4,137,53),block(0,-24.5,2.7,3.5,137,9)]
# Long rectangular solid body, two storeys and continuous floor stringcourse.
parts += [block(0,1,4.1,44.8,130,44),block(0,1,23.3,24.7,131.6,45.4),block(0,1,4.0,5.4,132,45.7)]
# Gable ends and a long Japanese-tile roof, rather than a generic hipped roof.
parts += [gable(0,1,44.4,130,44,11.5),gable(0,1,44.0,138,49.5,12.9),block(0,1,43.8,45.0,138,49.5),block(0,1,56.45,57.4,138.5,1.6)]
# Very shallow broad tile courses run along the roof slope. All are attached.
for sign in [-1,1]:
 for yy in np.linspace(3,23,9):
  y=1+sign*float(yy);z=44.0+12.9*(1-float(yy)/24.75)
  parts.append(block(0,y,z-.26,z+.18,137.9,.62))
# Ten repeated bays express the photographed long facade rhythm; approximate.
xs=np.linspace(-57.5,57.5,10)
for x in xs:
 x=float(x)
 cuts += [arch(x,-21.0,5.3,16.7,4.8,7.4),arch(x,-21.0,25.0,36.7,4.8,7.4)]
 # Engaged balcony parapet supports a thick top rail. Rib pattern replaces gaps.
 after += [block(x,-20.1,24.3,28.8,9.8,5.3),block(x,-22.9,28.6,29.65,10.15,1.6)]
 for dx in [-3.6,-1.8,0,1.8,3.6]:last.append(box(x+dx,-23.0,26.75,.8,1.1,2.8))
 # Doors and transoms set back in the blind arcade, still exterior details.
 for z in [12.1,32.2]:
  last += [box(x,-17.43,z,4.5,.85,10.0),box(x,-17.58,z+5.85,4.5,.65,1.35)]
# Side gable walls, observed as plain planes with a few vertical windows.
for sign in [-1,1]:
 for z in [13.5,33.5]:
  for y in [0,12]:cuts.append(box(sign*65.0,y,z,1.5,4.5,8.5))
 # A small gable vent is an explicit simplified reconstruction.
 cuts.append(box(sign*69.0,1,49.0,1.3,4.1,3.5))
# Unseen rear is intentionally restrained; no invented rear arcade.
for x in np.linspace(-54,54,8):
 for z in [13.5,33.5]:
  cuts += [box(float(x),23.0,z,5.8,1.35,9.1),box(float(x),23.0,z+5.8,5.8,1.35,1.35)]
# Slender engaged corner/downpipe strips are thickened, nonfunctional relief.
for x in [-64.4,64.4]:parts.append(block(x,-21.1,5.0,44.8,1.15,1.0))
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
body=body+m.Manifold.batch_boolean(after,m.OpType.Add)
body=body-m.Manifold.batch_boolean(last,m.OpType.Add)
assert str(body.status()).endswith('NoError'),body.status()
t=body.to_mesh();tm=trimesh.Trimesh(vertices=t.vert_properties[:,:3],faces=t.tri_verts,process=True)
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');a=ap.parse_args();tm.export(a.output)
print(json.dumps({'dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},indent=2))
