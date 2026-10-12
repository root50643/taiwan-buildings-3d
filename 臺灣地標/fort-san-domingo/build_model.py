"""Fort San Domingo main fort, Tamsui: 150 mm original printable exterior.
Reference: Tamsui Historical Museum official brochure front/back, main-fort photo
and aerial. Includes the square flat-roofed fort, two diagonal projecting turrets,
brick south terrace and small lean-to porch. Excludes the separate consulate.
Run: python build_model.py [--output model.stl]. All units mm.
"""
from pathlib import Path
import argparse,math
import numpy as np
import manifold3d as m
import trimesh
OUT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=OUT/'model.stl');a=p.parse_args()
parts=[];cuts=[]
def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def hull(pts):return m.Manifold.hull_points(pts)
def arch(w,h,depth):
 r=w/2;pts=[[-r,0],[r,0]]+[[r*math.cos(t),h-r+r*math.sin(t)] for t in np.linspace(0,math.pi,21)]
 return m.CrossSection([pts]).extrude(depth).rotate((90,0,0)).translate((0,depth,0))
def recess(x,y,z,w,h,d=2,angle=0):cuts.append(arch(w,h,d).rotate((0,0,angle)).translate((x,y,z)))
# Flat independent display plinth; the public main fort is a compact square.
add(0,0,1.5,150,140,3)
add(0,10,33.5,92,92,61.2)
# A shallow roof terrace, open to the sky; all building material below is solid.
cuts.append(box(0,10,67,83.6,83.6,9.6))
# Slightly raised coping blocks, unlike fantasy deep battlements.
for t in [-37,-22,-7,8,23,38]:
 for side in [-1,1]:
  add(t,10+side*45,64.55,9.5,3.9,1.15)
  add(side*45,10+t,64.55,3.9,9.5,1.15)
# Broad apron at the south facade, connected by a full area overlap to the fort.
add(0,-47.5,18,92,25,30.2)
add(0,-47.5,33.15,93,26,1.1)
# Solid, low brick terrace parapet with stepped posts and pale coping in reality.
add(0,-59.6,36.5,93,3.0,6.8)
for side in [-1,1]:add(side*45,-47.5,36.5,3.2,25,6.8)
for x in [-42,-28,-14,0,14,28,42]:
 add(x,-59.6,38.3,4.6,4.1,7.0)
 add(x,-59.6,41.85,7.1,5.2,1.0)
for side in [-1,1]:
 for y in [-51,-39]:
  add(side*45,y,38.2,4.2,7.0 if y>-45 else 4.6,6.8);add(side*45,y,41.6,5.3,6.8,1.0)
# Shallow front door/window niches, no room or prison reconstruction.
for x in [-32,-16,0,16,32]:recess(x,-61.5,7,7.5,20,2.6)
# The public brick terrace has simple courses, represented by shallow bands only.
for z in np.arange(6.1,31.8,2.6):
 cuts.append(box(0,-60.02,float(z),89,.48,.36))
 for side in [-1,1]:cuts.append(box(side*46.05,-48,float(z),.50,22,.36))
# Lower courses taper slightly out at base, making a robust grounded silhouette.
add(0,10,4.1,94,94,2.0)
# Main painted plaster walls intentionally remain largely plain, like the photos.
# Visible public west wall has sparse rectangular openings; no generic window grid.
for side in [-1,1]:
 for y,z,w,h in [(-10,24,8,11),(26,23,7,10),(5,43,6,8)]:
  cuts.append(box(side*46.15,y,z,2.5,w,h))
# Conservative rear openings, simplified due limited full rear photographic coverage.
for x,z,w,h in [(-21,27,7.5,10),(20,39,7.5,11)]:cuts.append(box(x,56.15,z,w,2.5,h))
# Small front lean-to porch, with closed supports and a shallow sloping roof.
# Large mass is filled; this is not an enclosed void or an interior room.
porch=hull([[x,y,z] for x in [-19,19] for y,top in [(-35.4,49.8),(-47.5,46.6)] for z in [33.1,top]])
parts.append(porch)
roof=hull([[x,y,z] for x in [-22,22] for y,top in [(-34.6,51.0),(-50.0,47.0)] for z in [top-1.4,top]])
parts.append(roof)
for x in [-16.5,16.5]:add(x,-47.5,40.1,2.2,1.8,13.4)
# Three shallow apertures through the visible facade surface only.
for x in [-11,0,11]:cuts.append(box(x,-48.2,40.8,6.8,2.8,9.5))
# Two characteristic projecting corner turrets: southwest and northeast only.
for sx,sy in [(-1,-1),(1,1)]:
 x=sx*46;y=10+sy*46
 # Thickened corbel tapers back into the wall for printability.
 pts=[]
 for zz,cx,cy,w in [(45.0,x-sx*6,y-sy*6,6.0),(54.0,x,y,16.7)]:
  pts.extend([[cx+dx*w/2,cy+dy*w/2,zz] for dx in [-1,1] for dy in [-1,1]])
 parts.append(hull(pts))
 add(x,y,63.5,16,16,19.2)
 add(x,y,73.5,18,18,1.3)
 parts.append(hull([[x+dx*9.2,y+dy*9.2,74.0] for dx in [-1,1] for dy in [-1,1]]+[[x,y,76.0]]))
 # Short shallow masonry lines; not individual thin loose brick objects.
 for z in np.arange(55.4,73,2.0):
  cuts.extend([box(x,y+sy*8.0,float(z),17.0,.38,.30),box(x+sx*8.0,y,float(z),.38,17.0,.30)])
 # A small outside slit is indicated without creating a tunnel.
 cuts.append(box(x+sx*8,y,68,1.5,2.4,4.5))
 cuts.append(box(x,y+sy*8,68,2.4,1.5,4.5))
# No flags, cannons, furniture, interior partitions or consulate residence included.
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert body.status()==m.Error.NoError,body.status()
body=body.as_original().set_tolerance(.005).simplify(.005)
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
a.output.parent.mkdir(parents=True,exist_ok=True);tm.export(a.output)
print(a.output,'triangles',len(tm.faces),'dimensions',tm.extents.tolist(),'watertight',tm.is_watertight)
