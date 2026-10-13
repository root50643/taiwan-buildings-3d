"""國立金門大學楊清廉圖資大樓銃樓段；照片近似，非全館；毫米。
兩個實拍可辨識立面保留，其餘留白。無第三方3D素材。
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64, CrossSection
OUT=Path(__file__).resolve().parent

def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
# Front y negative; photographed right elevation x positive.
s=box(0,0,0,70,70,3)+box(0,0,2.8,38,38,108.2)
# Stone plinth, slightly proud; balcony floor and solid parapet backed recess detail.
s+=box(0,0,3,39.6,39.6,20)
s+=box(0,0,110,53,53,2.6)
s+=box(0,0,112,53,53,6)
# Open balcony walkway, actual recessed deck rather than a solid block.
s-=box(0,0,112.8,48,48,5.3)-box(0,0,112.7,36,36,5.5)
# Top room, recessed inside balcony; actual known two elevations have dark window bands.
s+=box(0,0,117.5,36,36,15.5)
# Front single narrow windows on three rows; close top pair.
for z in [30,55,80]:s-=box(0,-19.05,z,3.3,2.7,10.5)
for x in [-3.1,3.1]:s-=box(x,-19.05,98,2.7,2.7,10)
for z in [30,55,80]:s-=box(19.05,0,z,2.7,3.3,10.5)
# Front and right window reveals with 1mm pale surrounding strips in relief.
for z in [30,55,80]:
 s+=box(0,-19.15,z-.9,5.1,1,1)
 s+=box(0,-19.15,z+10.4,5.1,1,1)
 for x in [-2.1,2.1]:s+=box(x,-19.15,z-.8,1,1,12)
 s+=box(19.15,0,z-.9,1,5.1,1)
 s+=box(19.15,0,z+10.4,1,5.1,1)
 for y in [-2.1,2.1]:s+=box(19.15,y,z-.8,1,1,12)
# Upper paired window edging.
for x in [-3.1,3.1]:
 for dx in [-1.8,1.8]:s+=box(x+dx,-19.15,97.3,1,1,11.4)
 s+=box(x,-19.15,97.2,4.6,1,1);s+=box(x,-19.15,108,4.6,1,1)
# Visible corner quoins, robust shallow relief, not brick texture.
for z in np.arange(23,109,3):
 s+=box(-18.7,-19.1,z,1.8,1,1.3);s+=box(18.7,-19.1,z,1.8,1,1.3)
 s+=box(19.1,18.7,z,1,1.8,1.3);s+=box(19.1,-18.7,z,1,1.8,1.3)
# Front two square balcony recesses, logo centre omitted; right three.
for x in [-15,15]:s-=box(x,-26.5,113.6,2.4,6,2.4)
for y in [-17,0,17]:s-=box(26.5,y,113.6,6,2.4,2.4)
# Head glazing on confirmed elevations, solid backing; unspecified elevations blank.
s-=box(0,-18,120,22,2.5,5)
s-=box(18,0,120,2.5,18,5)
# Photo-visible corner brackets below balcony, firmly intersect core.
for x in [-15,0,15]:s+=box(x,-21,107.5,3,7,4)
for y in [-14,0,14]:s+=box(21,y,107.5,7,3,4)
# Twin curved gables at x = +/-17, ridge runs along x; front y- is the tiled slope.
# Confirmed in architect cover photo and official recruitment p19, with 2019 reporter photo.
# Approximate curve controls, not inferred from the architect's maquette.
profile=[(-29,137.0),(-27,137.0),(-26,135.4),(-22,135.0),(-18,135.5),(-14,137),(-10,139.5),(-7,143),(-4,147),(-2.5,150),(0,150),(2.5,150),(4,147),(7,143),(10,139.5),(14,137),(18,135.5),(22,135.0),(26,135.4),(27,137.0),(29,137.0)]
# Piecewise dense interpolation keeps top surface curved while preserving explicit source silhouette.
ys=np.linspace(-29,29,117)
zs=np.interp(ys,[q[0] for q in profile],[q[1] for q in profile])
xs=np.linspace(-29,29,59)
v=[]
for x in xs:
 for y,z in zip(ys,zs):
  hip=min(1,max(0,(abs(x)-17)/10))
  end=133.5+3.2*min(1,(abs(y)/26)**8)
  top=(z-2.5)*(1-hip)+end*hip
  v.append([x,y,top])
f=[];ny=len(ys);nx=len(xs)
for i in range(nx-1):
 for j in range(ny-1):
  a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1;f.extend([[a,b,c],[a,c,d]])
# A finite underside eliminates zero-width curling tips.
edge=list(range(ny))+[i*ny+ny-1 for i in range(1,nx)]+[(nx-1)*ny+j for j in range(ny-2,-1,-1)]+[i*ny for i in range(nx-2,0,-1)]
bot=len(v);v.extend([[v[i][0],v[i][1],131.8] for i in edge])
for k,a in enumerate(edge):
 b=edge[(k+1)%len(edge)];c=bot+(k+1)%len(edge);d=bot+k;f.extend([[a,b,c],[a,c,d]])
center=len(v);v.append([0,0,131.8])
for k in range(len(edge)):f.append([center,bot+k,bot+(k+1)%len(edge)])
m=trimesh.Trimesh(v,f,process=True);m.fix_normals();s+=Manifold(Mesh64(np.array(m.vertices),np.array(m.faces,dtype=np.uint64)))
# Raised, broad, curved gable panels. Cross-section extruded 3.0mm in X and bonded to roof.
for x in [-17,17]:
 section=CrossSection([list(reversed([[float(y),float(z)] for y,z in zip(ys,zs)]+[[29,131.8],[-29,131.8]]))])
 gable=section.extrude(3.0).transform([[0,0,1,x-1.5],[1,0,0,0],[0,1,0,0]])
 s+=gable
assert len(s.decompose())==1
m=s.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
