"""鵝鑾鼻燈塔。原創照片判讀外觀模型，單位 mm，正面 -Y。
Public exterior only. Unseen dimensions and rear are reconstructed, not surveyed.
Run: python build_model.py [--output model.stl]
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import trimesh
import manifold3d as m
P=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def block(x,y,z0,z1,w,d):return box(x,y,(z0+z1)/2,w,d,z1-z0)
def cyl(x,y,z,h,r,rt=None,n=96):return m.Manifold.cylinder(h,r,r if rt is None else rt,n).translate((x,y,z))
def arch(x,y,bottom,spring,r,depth):
 return block(x,y,bottom,spring,2*r,depth)+m.Manifold.cylinder(depth,r,r,48).rotate((90,0,0)).translate((x,y+depth/2,spring))
def tangent_box(cx,cy,r,a,z,w,d,h):return box(0,-r,z,w,d,h).rotate((0,0,a)).translate((cx,cy,0))
# Compact display base and broad open paved apron.
parts += [block(0,0,0,2.8,150,104),block(0,4,2.5,3.8,139,91),block(15,-31,3.65,4.15,25,26)]
# Main low rectangular keeper's building, flat roof and small parapet piers.
parts += [block(-30,15,3.5,24,74,42),block(-30,15,23.3,25.3,77,45),block(-30,15,24.9,25.7,74,42)]
for x in [-66.4,6.4]:parts.append(block(x,15,24.9,28.0,1.65,42.5))
for y in [-5.4,35.4]:parts.append(block(-30,y,24.9,28.0,74,1.65))
for x in [-64,-43,-22,3]:
 for y in [-5.4,35.4]:parts.append(block(x,y,25.6,29.1,1.85,1.85))
# Five broad blind arched recesses express the photographed arcade.
for x in [-58,-46,-34,-22,-10]:cuts.append(arch(x,-6.1,4.15,16.3,4.2,5.0))
# The perpendicular arcade is visible in the official ground-level photo.
for y in [3,14,25]:
 a=arch(0,0,4.15,16.3,3.7,4.4).rotate((0,0,90)).translate((6.7,y,0));cuts.append(a)
# Deliberately simplified unseen rear, shallow marks only.
for x in [-58,-42,-26,-10]:cuts.append(box(x,36.0,14.0,5.2,1.2,8.0))
# Small lower connecting annex beside the round tower.
parts += [block(13,14,3.5,15.0,28,23),block(13,14,14.6,16.5,30,25)]
# White circular tower with slight taper and base plinth.
cx,cy=16,-5
parts += [cyl(cx,cy,3.6,2.2,12.0),cyl(cx,cy,5.5,56,10.4,9.35)]
# Horizontal cast-iron joint bands intentionally enlarged for FDM.
for z,r in [(22,10.23),(40,9.90),(57.7,9.53)]:parts.append(cyl(cx,cy,z,.55,r+.13))
# Cornice: flared corbel zone, gallery floor and solid outer parapet.
parts += [cyl(cx,cy,61,6.1,9.38,14.6),cyl(cx,cy,66.7,1.7,16.3),cyl(cx,cy,68.1,5.7,15.85)]
for a in np.arange(0,360,30):
 pts=[(x,y,z) for x in [-.6,.6] for y,z in [(-9.2,59.5),(-9.2,67.2),(-15.9,67.2),(-13.5,64.7)]]
 parts.append(m.Manifold.hull_points(pts).rotate((0,0,float(a))).translate((cx,cy,0)))
# Keep upper platform open to air. No interior chamber or enclosed cavity.
parts += [cyl(cx,cy,73.4,4.2,10.1),cyl(cx,cy,77.3,1.3,10.8),cyl(cx,cy,78.1,11.6,6.65,n=48)]
# Lower lantern-gallery handrail becomes a sturdy low ring with short piers.
ring=cyl(cx,cy,78.3,1.25,10.4)-cyl(cx,cy,78.0,2.0,8.9)
parts.append(ring)
for a in np.arange(0,360,30):parts.append(tangent_box(cx,cy,9.7,float(a),78.25,1.3,1.3,2.1))
# Lantern window panels are blind relief, held in a solid printable core.
for a in np.arange(0,360,30):
 cuts.append(tangent_box(cx,cy,6.55,float(a),85.1,2.2,1.0,6.0))
parts += [cyl(cx,cy,89.4,1.3,7.0),cyl(cx,cy,90.3,5.0,8.4,.9),cyl(cx,cy,95.0,2.9,1.0,.75),cyl(cx,cy,97.6,1.5,.8,.55)]
# Public visible tower openings as shallow exterior marks, not access models.
for z,a in [(17,0),(36,0),(54,0),(36,90),(54,-90)]:
 cuts.append(tangent_box(cx,cy,10.3-(z-5.5)*.01875,a,z,2.1,1.65,3.1))
# Low rear boundary fragments frame the displayed building; no military detail.
parts += [block(-6,43.5,3.5,9.0,124,1.6),block(-67.0,17,3.5,9.0,1.6,54)]
# Union solids before engraving, with no internal negative-volume shell.
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert str(body.status()).endswith('NoError'),body.status()
t=body.to_mesh();tm=trimesh.Trimesh(vertices=t.vert_properties[:,:3],faces=t.tri_verts,process=True)
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');a=ap.parse_args();tm.export(a.output)
print(json.dumps({'dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},indent=2))
