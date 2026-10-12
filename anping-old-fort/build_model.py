"""安平古堡現存白色瞭望塔與磚臺：公開外觀照片判讀縮景。
不是17世紀熱蘭遮城復原。150 mm 長邊，毫米，正面 -Y。
小型展示館及遮蔽平面為推定縮化；無室內、地下或安全設施。
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
def frustum(x,y,z0,z1,w0,d0,w1,d1):
 return m.Manifold.hull_points([(x+sx*w/2,y+sy*d/2,z) for z,w,d in [(z0,w0,d0),(z1,w1,d1)] for sx in [-1,1] for sy in [-1,1]])
def rail(x,y,z,w,d):
 parts.append(block(x,y,z-.2,z+2.25,w,d))
 if w>d:
  for xx in np.linspace(x-w/2+.8,x+w/2-.8,max(2,int(w/6))):parts.append(block(float(xx),y,z-.2,z+3.4,1.8,d+.3))
 else:
  for yy in np.linspace(y-d/2+.8,y+d/2-.8,max(2,int(d/6))):parts.append(block(x,float(yy),z-.2,z+3.4,w+.3,1.8))
def arch_cut(x,y,z,w,h,depth):
 # Blind external arch, no through-space or interior.
 r=w/2
 return block(x,y,z,z+h-r,w,depth)+m.Manifold.cylinder(depth,r,r,32).rotate((90,0,0)).translate((x,y+depth/2,z+h-r))
# Deliberately cropped fragment of the present stepped raised plinth.
parts += [block(0,0,0,2.6,150,106),frustum(0,10,2.4,9.3,140,83,136,79),frustum(0,12,9.1,16.7,132,75,129,71),frustum(0,13,16.5,24,125,69,123,67)]
parts.append(block(0,13,23.7,24.8,124.5,68.5))
# Brick courses, shallow exterior grooves. Long courses follow terrace bands.
for z,y,w in [(4,-31.7,133),(6.5,-31.0,133),(11,-25.35,126),(13.7,-24.6,126),(18.2,-21.0,119),(20.6,-20.45,119),(22.6,-19.9,119)]:
 cuts.append(box(0,y,z,w,4.0,.35))
# Side courses are sparse, approximate surface rhythm rather than surveyed bond.
for x,s in [(-68,-1),(68,1)]:
 for z in [4.5,7]:cuts.append(box(x+(1.2*s),10,z,3.6,75,.32))
# Wide exposed staircase rises into the front terrace, count thickened for FDM.
for k in range(20):
 y0=-48+k*1.45
 parts.append(block(-29,(y0-17.6)/2,2.45,2.6+(k+1)*22.2/20,16,-17.6-y0+.25))
for x in [-37.4,-20.6]:
 parts.append(m.Manifold.hull_points([(x+dx,y,z) for dx in [-.75,.75] for y,z in [(-48.5,2.5),(-48.5,5.0),(-17.4,27.6),(-17.4,2.5)]]))
# Tower shaft: compact square white tower, two engaged bands and shallow slit.
tx=-31;ty=-3
parts += [block(tx,ty,24.4,26.5,18,18),block(tx,ty,26,69,14.5,14.5),block(tx,ty,65.5,67,16,16)]
cuts += [block(tx,ty-7.15,26.4,37.2,5.3,1.1),block(tx+3.3,ty-7.15,52,58,1.8,.9),block(tx-7.15,ty+1.3,42,47,.9,1.7)]
# Most distinctive volume: inverted truncated pyramid lookout cabin.
parts += [frustum(tx,ty,66.7,82.5,16,16,24,24),block(tx,ty,81.8,84,25,25)]
# Cabin glazing on four faces is recessed into the sloping skin. Cuts extend
# outward so each recess is open; a cross mullion is left intact.
for side in [-1,1]:
 for off in [-4.6,4.6]:
  cut=frustum(tx+off,ty+side*11.2,72.2,80.8,7.5,3.4,7.5,5.2)
  cuts.append(cut)
  cut=frustum(tx+side*11.2,ty+off,72.2,80.8,3.4,7.5,5.2,7.5)
  cuts.append(cut)
# The visible red pyramidal roof; apex thickened to 0.9 mm rather than needle.
parts += [frustum(tx,ty,83.4,84.5,26.5,26.5,28,28),frustum(tx,ty,84.3,103.2,28,28,.9,.9)]
# Present display hall behind/right of tower. Compact colonial hip roof,
# engaged colonnade/arch relief, facade consistent with the official photos.
hx=21;hy=22
parts += [block(hx,hy,24.5,26.2,66,36),block(hx,hy,26,39.5,61,31),block(hx,hy,38.6,40.5,66,36),frustum(hx,hy,40.2,49.4,70,40,48,1.5)]
# Museum front arches and backing stay solid. At this scale they are relief.
for x in np.linspace(hx-24,hx+24,5):cuts.append(arch_cut(float(x),hy-15.45,26.4,8.1,10.9,1.2))
for x in np.linspace(hx-30,hx+30,6):
 parts += [block(float(x),hy-15.55,26.05,38.8,1.75,1.3),block(float(x),hy-15.7,26,27,2.7,1.6),block(float(x),hy-15.7,37.7,39,2.8,1.65)]
# Side blind openings, restrained banding. Unseen rear left intentionally plain.
for yy in [14,23,32]:cuts.append(block(hx+30.35,yy,28,36,1.0,4.8))
parts.append(block(hx,hy+15.3,27.8,28.5,60,.7))
# Partial terrace parapets (front gaps reserved for stairs).
rail(-49,-20.1,24.6,25,1.5);rail(19.5,-20.1,24.6,82,1.5)
rail(61.2,13,24.6,1.5,66);rail(-61.2,13,24.6,1.5,66)
rail(0,46.2,24.6,123,1.5)
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert str(body.status()).endswith('NoError'),body.status()
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');a=ap.parse_args();tm.export(a.output)
print(json.dumps({'dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},indent=2))
