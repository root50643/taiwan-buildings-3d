"""Visible sharp edges projected from delivered STL onto its north-up top render.
Visibility tested against original triangles; no model edits or invented roof edges.
"""
from pathlib import Path
import trimesh,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).parent;m0=trimesh.load(R/'model.stl',process=False);v,idx=np.unique(m0.triangles.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,idx.reshape(-1,3),process=False)
a=m.face_adjacency;mask=(m.face_adjacency_angles>.3)&(np.max(m.face_normals[a][:,:,2],axis=1)>.4);edges=m.face_adjacency_edges[mask]
im=Image.open(R/'previews/top.png').convert('RGB');d=ImageDraw.Draw(im);scale=max(m.extents[0],m.extents[1]*4/3)*1.12
project=lambda p:(600+1200*p[0]/scale,450-1200*p[1]/scale)
for e in edges:
 p,q=m.vertices[e];ts=np.linspace(0,1,max(2,int(np.linalg.norm(q-p)/.7)+1));pts=p[None,:]+ts[:,None]*(q-p);orig=pts.copy();orig[:,2]=200;dirs=np.tile([0,0,-1],(len(pts),1));loc,ri,_=m0.ray.intersects_location(orig,dirs,multiple_hits=True);top=np.full(len(pts),-1e9)
 for h,r in zip(loc,ri):top[r]=max(top[r],h[2])
 visible=abs(top-pts[:,2])<.025
 for i in range(len(pts)-1):
  if visible[i] and visible[i+1]:d.line([project(pts[i]),project(pts[i+1])],fill=(75,77,79),width=2)
im.save(R/'previews/top-lines.png')
