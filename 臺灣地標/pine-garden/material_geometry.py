"""Exact original STL geometry and a bijective oriented-triangle identity mapping."""
from pathlib import Path
import hashlib,struct,json
import numpy as np
STL_SHA256='7fc0fcf4aadbf8a0c774d0cc6f659092bb6553e6071334953f17ac5c2f478d1d'
def load_stl(path):
 raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==STL_SHA256
 n=struct.unpack_from('<I',raw,80)[0];assert n==5874 and len(raw)==84+n*50
 rec=np.frombuffer(raw,offset=84,count=n,dtype=np.dtype([('normal','<f4',3),('triangle','<f4',(3,3)),('attribute','<u2')]))
 tri=rec['triangle'].copy();vertices=[];lookup={};faces=[]
 for t in tri:
  f=[]
  for v in t:
   key=tuple(float(x)for x in v)
   if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
   f.append(lookup[key])
  faces.append(f)
 v=np.asarray(vertices,np.float32);f=np.asarray(faces,np.int32)
 assert np.array_equal(v[f],tri)
 return v,f,tri,rec['normal'].copy()
def normals(tri):
 t=np.asarray(tri,np.float64);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return cross/np.linalg.norm(cross,axis=1)[:,None]
def triangle_key(t):
 # Cyclic rotations preserve orientation; reversed winding must not match.
 q=[tuple(float(x)for x in v)for v in t];return min(tuple(q[i:]+q[:i])for i in range(3))
def bijection(original,actual):
 lookup={triangle_key(t):i for i,t in enumerate(original)};assert len(lookup)==len(original),'Duplicate original triangles'
 ids=np.asarray([lookup[triangle_key(t)]for t in actual],np.int32)
 assert len(ids)==len(original) and len(set(ids.tolist()))==len(original),'Not a complete bijection'
 assert np.allclose(normals(actual),normals(original)[ids],rtol=0,atol=1e-12),'Winding / normal mismatch'
 return ids
def load_materials(root):
 root=Path(root);a=json.loads((root/'face-material-map.json').read_text());assert a['source_stl_sha256']==STL_SHA256
 n=a['source_triangles'];assert n==5874
 roof=set(a['roof']);masonry=set(a['front_masonry']);assert len(roof)==122 and len(masonry)==4295 and not roof&masonry
 hold=set(a['white_hold_door_back'])|set(a['white_hold_transom_back'])|set(a['excluded_side_gable_vent'])
 assert len(a['white_hold_door_back'])==len(a['white_hold_transom_back'])==40
 assert not (roof|masonry)&hold
 assert min(roof|masonry)>=0 and max(roof|masonry)<n
 materials=np.zeros(n,np.int32);materials[list(roof)]=1;materials[list(masonry)]=2
 assert np.bincount(materials,minlength=3).tolist()==[1457,122,4295]
 return materials
