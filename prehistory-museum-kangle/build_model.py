"""國立臺灣史前文化博物館康樂本館：2023 改造後入口外觀。
Original photo-interpreted 150 mm miniature, millimeters, front -Y.
No old sundial plaza, speculative renovation concept, interior, or service systems.
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
def hip(x,y,z,w,d,h,tw,td):return m.Manifold.hull_points([(x+xx,y+yy,z+zz) for ww,dd,zz in [(w,d,0),(tw,td,h)] for xx in [-ww/2,ww/2] for yy in [-dd/2,dd/2]])
def arch(x,y,bottom,spring,r,depth):return block(x,y,bottom,spring,2*r,depth)+m.Manifold.cylinder(depth,r,r,48).rotate((90,0,0)).translate((x,y+depth/2,spring))
def terrain():
 # Smooth front grassy bank, replacement of the old monumental stair/plaza.
 xs=np.linspace(-44,29,31);ys=np.linspace(-65,-25,25);v=[];f=[]
 for y in ys:
  t=(y+65)/40;t=t*t*(3-2*t)
  for x in xs:
   ex=max(0,1-((x+7.5)/37.0)**4);v.append((x,y,2.65+3.75*t*ex))
 nx=len(xs);ny=len(ys);n=len(v)
 v += [(x,y,2.35) for y in ys for x in xs]
 for j in range(ny-1):
  for i in range(nx-1):
   a=j*nx+i;b=a+1;c=a+nx+1;d=a+nx;f.extend([(a,b,c),(a,c,d),(a+n,c+n,b+n),(a+n,d+n,c+n)])
 boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range((ny-1)*nx+nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):f.extend([(a,b+n,b),(a,a+n,b+n)])
 t=trimesh.Trimesh(vertices=v,faces=f,process=True);t.fix_normals();return m.Manifold(m.Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
# Overall site base and the post-2023 front grassy slope.
parts += [block(0,0,0,2.8,150,142),terrain()]
# Museum's front entry is an indented middle between two taller brick boxes.
# The five-bay, two-level projecting frame is backed solid for reliable printing.
parts += [block(-8,-13.8,2.6,24.0,53,20.4),block(-26,-13.8,2.6,29.2,17,20.4),block(10,-13.8,2.6,29.2,17,20.4)]
parts += [block(-8,-25.6,2.6,27.7,36.8,5.8),block(-8,-28.2,5.5,6.5,38,3.0)]
for x in np.linspace(-22.55,6.55,5):
 cuts += [box(float(x),-27.9,9.95,5.35,3.4,6.3),box(float(x),-27.9,20.7,5.35,3.4,11.5)]
 # Fine front window/door panels in the rear of each deep frame recess.
 cuts.append(box(float(x),-26.15,20.4,3.8,.7,8.1))
 cuts.append(box(float(x),-26.15,9.7,3.8,.7,5.7))
# Large-scale running-bond pattern in the brick flanking walls; no lettering.
for cx in [-30.5,14.5]:
 for k,z in enumerate(np.arange(8.0,28.9,4.2)):
  cuts.append(box(cx,-24.02,float(z),7.5,.7,.65))
  start=cx-3.0+(3.8 if k%2 else 0)
  for x in np.arange(start,cx+3.7,7.6):cuts.append(box(float(x),-24.02,float(z)+2.1,.6,.7,3.6))
# Left long three-level administrative wing, a restrained plain modern block.
parts += [block(-47,10,2.6,30.0,22,70),block(-47,10,29.6,30.7,23,71)]
# Photographed tall brick projecting bay on its front, without interior plans.
parts += [block(-47,-25.0,2.6,28.0,11.3,8.0),block(-47,-25.0,27.6,28.5,12.0,8.7)]
for z in [9.8,17.4,25.0]:
 for x in [-55.0,-39.0]:cuts.append(box(x,-25.05,z,1.8,1.0,2.6))
 for y in np.linspace(-19,41,13):cuts.append(box(-58.02,float(y),z,1.0,1.8,2.6))
for x in [-50.7,-47,-43.3]:cuts.append(box(x,-29.0,17.8,2.3,1.2,17.0))
# Right exhibition block: low broad podium and raised roof monitor with clerestory.
parts += [block(46,10,2.6,20.4,53,71),block(46,10,20.0,21.2,54,72),block(44,17,20.9,28.0,37,30)]
parts += [hip(44,17,27.7,40,33,2.0,37.5,30.5),block(44,17,29.3,29.95,38,31)]
# The front low wing steps farther toward the visitor.
parts += [block(45,-26,2.6,18.2,46,13),block(45,-26,17.9,19.0,47,14)]
# Secondary square-framed frontage, shown at the right of the official photo.
parts.append(block(58,-33.0,4.0,17.9,12,2.3))
for z in [7.6,13.5]:
 for x in [54.2,58,61.8]:cuts.append(box(x,-34.13,z,2.7,1.2,4.2))
for k,z in enumerate(np.arange(6.8,18.2,3.0)):
 cuts.append(box(39,-32.55,float(z),32,.8,.55))
 for x in np.arange(23+(3.2 if k%2 else 0),54,6.4):cuts.append(box(float(x),-32.55,float(z)+1.5,.55,.8,2.4))
# Upper rectangular clerestory bands, solid-backed blind openings.
for x in np.linspace(28,60,9):
 for y in [1.97,32.03]:cuts.append(box(float(x),y,24.8,2.6,.8,4.5))
for y in np.linspace(4.5,29.5,7):
 for x in [25.47,62.53]:cuts.append(box(x,float(y),24.8,.8,2.5,4.5))
# Outdoor central courtyard: perimeter gallery volume and robust vertical rhythm.
# All external recesses are blind; no enclosed voids or walkthrough tunnels.
parts += [block(-31.8,15,2.6,18.5,5.2,42),block(17.0,16,2.6,19.5,5.5,42),block(-7.4,39.5,2.6,19.0,51.5,5.5)]
for y in np.linspace(-2,34,10):
 cuts.append(box(-29.16,float(y),12.8,1.0,2.5,8.0));cuts.append(box(14.22,float(y),12.8,1.0,2.5,8.0))
for x in np.linspace(-29,14,12):cuts.append(box(float(x),36.7,12.8,2.3,1.0,8.0))
# Central rear arched garden frame stays as a blind public-facing outline.
parts.append(block(-7.5,39.4,2.6,22.0,12.0,6.0));cuts.append(arch(-7.5,42.43,3.1,10.9,3.8,1.2))
# A small mound represents the renewed public courtyard landscape.
parts.append(m.Manifold.sphere(1,48).scale((9.8,8.2,4.0)).translate((-8,17,2.35)) ^ block(-8,17,2.55,7.0,21,18))
# Broad courtyard terraces indicate the visible outdoor seating, not exact count.
for k in range(5):parts.append(block(-8,29.5+k*.95,2.6,3.2+k*.72,28,5.8-k*.95))
# Rear external elevations intentionally simplified; no service or roof equipment.
for z in [8.0,14.0]:
 for x in np.linspace(22,66,10):cuts.append(box(float(x),45.53,z,2.1,1.0,3.2))
body=m.Manifold.batch_boolean(parts,m.OpType.Add)-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert str(body.status()).endswith('NoError'),body.status()
t=body.to_mesh();tm=trimesh.Trimesh(vertices=t.vert_properties[:,:3],faces=t.tri_verts,process=True)
# Flat display base must remain the global lower boundary.
if tm.bounds[0,2]<0: raise ValueError('Geometry protrudes below base')
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');a=ap.parse_args();tm.export(a.output)
print(json.dumps({'dimensions_mm':tm.extents.tolist(),'triangles':len(tm.faces),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},indent=2))
