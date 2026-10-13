"""學生活動中心（含表演廳）外觀縮模，毫米。
官方 a9 各層平面、2014 湖側、2017 道路入口照片、2021 空拍及 2024 湖側照片自建。
主要凹空、弧形端牆、中央柱廊與天井保留；樹後側窗高、坡屋頂斜度為近似。
"""
from pathlib import Path
import math,numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent;parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,48).translate((x,y,z))
def gable(x0,x1,y0,y1,z,h):
 pts=[[x,y,z] for x in [x0,x1] for y in [y0,y1]]+[[x,(y0+y1)/2,z+h] for x in [x0,x1]]
 return Manifold.hull_points(np.array(pts))
add(0,0,0,150,65,2.8)
# Overall 145 m by 52 m plan reduced independently; asymmetric end wings retained.
# Office west wing with stepped west edge and curved inner court corner.
p=[(-69,-21),(-65,-21),(-65,-25),(-33,-25),(-28,-22),(-27,-16),(-27,9)]
p += [(-34+7*math.cos(a),9+7*math.sin(a)) for a in np.linspace(0,math.pi/2,10)]
p += [(-58,16),(-58,22),(-66,22),(-66,10),(-69,10)]
parts.append(poly(p,2.6,12.5))
# Eastern performance wing's large low hall, with a distinct narrower tall club-room block.
add(59,0,2.6,21,44,12.5)
p=[(27,-22),(48,-22),(48,16),(37,16)]
p += [(37-10*math.sin(a),6+10*math.cos(a)) for a in np.linspace(0,math.pi/2,10)]
p += [(27,-22)]
parts.append(poly(p,2.6,12.5))
# Tall rounded rear lobes frame the north entrance court, with visible upper blank walls.
for sign in [-1,1]:
 b=box(sign*43,12,2.6,30,19,15.5)+cyl(sign*33,12,2.6,10,15.5)
 # Keep inner court boundary beyond x +/-23 rather than letting lobes fill the centre.
 b=b^box(sign*47,13,2.5,48,25,16)
 parts.append(b)
 # Central roof-light supporting block, set behind the lakeside upper office wall.
 add(sign*38,0,14.8,29,17.2,3.5)
# Central open concourse, roofed by long glazed gallery; both sides remain open.
add(0,0,2.6,54,22,1.5)
add(0,0,9.6,54,22,1.3)
# Punch the large double-height central court through lower floors, not blind dark rectangles.
court_void=box(0,0,4.0,42,16.0,8.8)
for xx in [-20,-12,0,12,20]:court_void=court_void-cyl(xx,-7,3.8,.9,9.2)
cuts.append(court_void)
# Centre stair/round drum on lakeside terrace; basement entry behind the drum is recessed.
add(0,-16.3,2.6,47,6.0,1.5)
add(0,-15.4,7.5,47,6.0,1.4)
parts.append(cyl(0,-18.0,2.6,3.5,6.3))
cut(0,-21.55,3.4,2.7,2.0,3.0)
for sign in [-1,1]:
 for i in range(7):add(sign*21,-23.2+i*.95,2.6+i*.65,7,2.4,.9)
# North high entry bridge, columns and broad stairs visible in 2017 frontal photographs.
add(0,15.0,13.4,52,6.4,2.2)
for x in [-20,-12,0,12,20]:parts.append(cyl(x,14.3,2.6,.9,11.2))
for x in [-20,-12,0,12,20]:parts.append(cyl(x,-7,3.8,.9,14.6))
for i in range(6):add(0,26-i*1.1,2.6+i*.45,29,2.6,.7)
# Upper gallery is a solid backed model of the glazing wall; large void below is preserved.
add(0,0,14.8,107,16.8,3.5)
# Long east-west pitched roof and the higher north-south cross-gable.
parts.append(gable(-54,54,-9.4,9.4,18.1,3.2))
pts=[[x,y,18.15] for x in [-8.2,8.2] for y in [-10,10]]+[[0,y,23.0] for y in [-10,10]]
parts.append(Manifold.hull_points(np.array(pts)))
# Fine glazing divisions are not structural columns. Major 0.9 mm relief strips only.
# Individual roof glazing strips are omitted rather than made into protruding posts.
# Lakeside outer wings: 3 visible rows (basement + first + second), not 3 complete tall blocks.
# Upper office row uses four wider bays and neighbouring grouped window openings.
for sign in [-1,1]:
 for j in range(7):
  x=sign*(29.8+j*4.6)
  for z,h in [(3.3,2.2),(7.0,2.9),(11.2,2.8)]:cut(x,-24.65 if sign<0 else -21.8,z,3.3,2.9,h)
 # Low open veranda between piers, backed at 4 mm from face.
 # Interior glazing/door-leaf divisions are omitted; the aligned major bays remain.
 # Upper outer roof-beams are broad and connected to the block, seven visible ribs.
 for j in range(7 if sign<0 else 5):
  x=sign*(30+j*4.7);add(x,-14.0,14.8,1.2,14.8,1.0)
# Recessed continuous glazing bands on curved north lobes. Cylinder intersection supplies curved recess.
for sign in [-1,1]:
 for z,h in [(4.2,2.3),(8.4,2.3)]:
  outer=(box(sign*43,12,z,30,19,h)+cyl(sign*33,12,z,10.05,h))^box(sign*47,13,z,48,25,h)
  inner=(box(sign*43,11,z-.1,27.0,17.0,h+.2)+cyl(sign*33,11,z-.1,8.6,h+.2))
  cuts.append((outer-inner)^box(sign*43,20,z-.05,45,16,h+.1))
 # Heavy shared vertical supports between window bands, fully backed.
 for x in np.arange(29,65,4.8):add(sign*float(x),20.7,3.6,1.0,2.1,7.7)
 # Single square upper opening in each inner stair block is visible from road court.
 add(sign*26.8,12.5,2.6,5.0,8.0,15.5)
 cut(sign*26.8,22,12.6,2.6,13,2.8)
# Rear upper office windows beyond the curved blank corner walls.
for sign in [-1,1]:
 for xx in [42,47,52,57]:cut(sign*xx,21.5,13.0,3.2,2.5,2.6)
# Gallery glazing bands front/back above the central bridge, with generously backed mullions.
for y in [-8.5,8.5]:
 for x in np.linspace(-48,48,17):
  if y<0 or abs(x)<23:cut(float(x),y,15.7,4.2,1.7,1.6)
# Outer ends: stepped office end vs broad performance hall end. Less-seen small openings estimated.
for z in [4.5,8.7,12.0]:
 for y in [-14,-6,2,10]:cut(-69.1,y,z,2.4,3.3,2.0)
for y in [-15,-5,5,15]:cut(69.55,y,5.2,2.5,3.5,4.0)
# Flat end roofs have shallow open parapets, with no detailed plant copied from photographs.
cut(59,0,14.2,16.5,39,1.5)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
assert len(solid.decompose())==1,'Disconnected or enclosed shell'
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
