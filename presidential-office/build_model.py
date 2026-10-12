"""Presidential Office, Taipei. Original photo-interpreted 150 mm exterior.
Run: python build_model.py [--output model.stl]. Units: millimeters.
The two exterior courts are open at their tops; no rooms or sealed voids.
Public source: https://www.president.gov.tw/Page/91 and /qrcode/06c.
"""
from pathlib import Path
import argparse, math
import numpy as np
import manifold3d as m
import trimesh
OUT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=OUT/'model.stl');a=p.parse_args()
parts=[];cuts=[]
def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def add(x,y,z,sx,sy,sz):parts.append(box(x,y,z,sx,sy,sz))
def hull(pts):return m.Manifold.hull_points(pts)
def hip(x,y,z,w,d,h,ridge=.65):
 return hull([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x+sx*(w-d*ridge)/2,y,z+h] for sx in [-1,1]])
def cap(x,y,z,w,d,h,topw,topd):
 return hull([[x+sx*ww/2,y+sy*dd/2,zz] for ww,dd,zz in [(w,d,z),(topw,topd,z+h)] for sx in [-1,1] for sy in [-1,1]])
def cyl(x,y,z,r,h,n=32):return m.Manifold.cylinder(h,r,r,n).translate((x,y,z))
def arch(w,h,depth):
 # A solid vertical cutter, front-facing (-Y), with semicircular top.
 r=w/2;pts=[[-r,0], [r,0]]+[[r*math.cos(t),h-r+r*math.sin(t)] for t in np.linspace(0,math.pi,17)]
 return m.CrossSection([pts]).extrude(depth).rotate((90,0,0)).translate((0,depth,0))
def recess(x,y,z,w,h,depth=1.0,angle=0):
 cuts.append(arch(w,h,depth).rotate((0,0,angle)).translate((x,y,z)))
# 150 mm flat plinth. Exterior building width 140, depth 85, central tower ~60.
add(0,0,1.5,150,106,3)
# Four solid perimeter wings plus center spine, interpreted '日' silhouette.
for x,y,w,d in [(0,-34.5,140,16),(0,34.5,140,16),(-62,0,16,69),(62,0,16,69),(0,0,17,70)]:
 add(x,y,15.8,w,d,26)
 add(x,y,28.75,w+.6,d+.6,1.1)
 if w>d:parts.append(hip(x,y,29.15,w+.7,d+.7,3.2))
 else:parts.append(hip(y,x,29.15,d+.7,w+.7,3.2).rotate((0,0,90)))
# Facade bands (red/white bands are rendered as printable monochrome relief).
for z in [6.5,8,17,24,27.8]:
 add(0,-42.6,z,140,.9,.65);add(0,42.6,z,140,.9,.65)
 add(-70.1,0,z,.9,85,.65);add(70.1,0,z,.9,85,.65)
# Front and back bays. Lower/upper arcs are shallow, never openings into rooms.
for side in [-1,1]:
 for x in [-51,-44.5,-38,-31.5,-25,-18.5,18.5,25,31.5,38,44.5,51]:
  angle=0 if side==-1 else 180;y=side*43.25
  for z,h in [(8.2,6.8),(18.15,5.6)]:recess(x,y,z,4.2,h,1.8,angle)
  add(x,side*42.65,26,3.2,.9,1.5)
  # Engaged pilasters retain the generous ground-to-third-floor rhythm.
  for dx in [-2.75,2.75]:add(x+dx,side*42.9,15.8,.75,1.05,17)
  for z in [7.75,17.65,24.05]:add(x,side*43.05,z,5.5,1.15,.65)
# Public-visible side elevations use simplified repeated bays.
for side in [-1,1]:
 for y in [-24,-16,-8,0,8,16,24]:
  angle=90 if side==1 else -90
  for z,h in [(8.2,6.8),(18.15,5.6)]:recess(side*70.75,y,z,4.4,h,1.7,angle)
  add(side*70.15,y,26,.9,3.3,1.5)
# Four stepped corner towers; front pediments capture the published corners.
for x in [-62,62]:
 for y in [-34.5,34.5]:
  add(x,y,18,17,18,30)
  for z in [6.4,8.1,10,22.4,24.2,29.1,31.8]:add(x,y,z,17.7,18.7,.75)
  add(x,y,33,12,13,2.6)
  parts.append(cap(x,y,34.15,13,14,2.6,2,2))
  sy=-1 if y<0 else 1
  # Triangular front pediment with broad sculpted tympanum, no tiny sculpture.
  ped=hull([[-6,-1,0],[6,-1,0],[0,-1,3.8],[-6,1,0],[6,1,0],[0,1,3.8]]).translate((x,sy*44,27.7));parts.append(ped)
  for z,h in [(9,6.5),(19,5.5)]:recess(x,sy*44.55,z,4.7,h,1.5,0 if sy==-1 else 180)
  for dx in [-6.8,6.8]:add(x+dx,sy*43.9,17,.9,1.3,22)
# Central entrance group with two high flat-topped escort towers.
add(0,-35.5,17.5,26,16,29)
for x in [-10.2,10.2]:
 add(x,-35.9,19.5,7.2,17.2,33)
 for z in [7.4,9,23.1,25,31.1,35.1]:add(x,-35.9,z,7.9,18,.75)
 add(x,-35.9,35.5,7.6,17.8,1.4)
 for z in [11,20,28]:recess(x,-45.1,z,2.8,4.6,1.6)
# The iconic square tall shaft, flared cornice, octagonal lantern/crown.
add(0,-34.5,37.4,10.5,12,34.8)
for x in [-4.4,4.4]:add(x,-40.7,40,.9,1.0,27)
for z in [32.7,39.1,45.3,51.5]:recess(0,-41.1,z,2.7,4.4,1.05)
parts.append(cap(0,-34.5,53.4,10.8,12.3,1.7,13,14.5))
add(0,-34.5,55,13,14.5,1.1)
# Octagonal plan fits the documented square-to-eight-sided transition.
lantern=m.Manifold.cylinder(7.2,7.0,7.0,8).rotate((0,0,22.5)).scale((1,1.07,1)).translate((0,-34.5,55.35));parts.append(lantern)
for z in [56.2,57.8,59.4,61.0,62.4]:
 parts.append(m.Manifold.cylinder(.55,7.3,7.3,8).rotate((0,0,22.5)).scale((1,1.07,1)).translate((0,-34.5,z)))
for angle in [0,90,180,270]:
 rad=math.radians(angle);xx=7.8*math.sin(rad);yy=-34.5-7.8*math.cos(rad)
 recess(xx,yy,56.7,2.8,5.0,2.5,angle)
parts.append(m.Manifold.cylinder(1.65,7.0,4.1,8).rotate((0,0,22.5)).scale((1,1.07,1)).translate((0,-34.5,62.9)))
# Flag and extremely fine pole omitted intentionally; roof has solid blunt top.
add(0,-34.5,64.5,3,3,1.2)
# Central pediment and solid small entrance porch, with readable arch relief.
parts.append(hull([[-5,-1,0],[5,-1,0],[0,-1,3.4],[-5,1,0],[5,1,0],[0,1,3.4]]).translate((0,-44,30)))
add(0,-46.0,9,17,7,12)
add(0,-46,15.2,18,8,1)
for x in [-6.7,-4.5,4.5,6.7]:add(x,-49.7,9.5,1.0,1.3,10.4)
recess(0,-50.2,3.7,6,10,2.0)
for n in range(3):add(0,-49.4-n*.45,3.1+n*.32,22-n*1.3,3.2-n*.3,.5)
# Rear entrance: low Ionic porch, unlike the tall central east/front tower.
parts.append(cyl(0,42.4,3,9,11).scale((1,1,1)))
parts.append(cyl(0,42.4,13.8,9.5,1.2))
for x in [-7,-3.5,3.5,7]:add(x,42.4+math.sqrt(81-x*x),8.5,1.0,1.25,10.8)
recess(0,52,3.5,4.8,8.5,2.0,180)
# Roof lanterns seen along both wings, thickened into integral roof furniture.
for y in [-34.5,34.5]:
 for x in [-43,-25,25,43]:
  add(x,y,32.9,2.7,2.7,2.8);parts.append(cap(x,y,34.1,3.4,3.4,1.4,.9,.9))
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert body.status()==m.Error.NoError,body.status()
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
a.output.parent.mkdir(parents=True,exist_ok=True);tm.export(a.output)
print(a.output, 'triangles',len(tm.faces),'dimensions',tm.extents.tolist(),'watertight',tm.is_watertight)
