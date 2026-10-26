"""Exact original STL geometry and a bijective oriented-triangle identity mapping."""
from pathlib import Path
import hashlib,struct,json
import numpy as np
STL_SHA256='19dd8d6d17606fe0674245fca57230e7d9cae6b5b800dac93746b6ff2d11b524'
def load_stl(path):
 raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==STL_SHA256
 n=struct.unpack_from('<I',raw,80)[0];assert n==3618 and len(raw)==84+n*50
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
GROUP_INDEX_SHA256={'tower_front_outer_plaster': '482259c96d7ca1b3b6157a90854c77df3ab87bab7f13aa4ef680a7492406f6b4', 'tower_front_lower_cabin_skirt': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945', 'tower_front_eave_fascia': 'b54e482944209a5232bf0c87097b53891c6e8fa30683ee61a892d78b30a5562e', 'tower_front_roof_slope': '71998b52935587f9ca4184e476bb4ab829b6092d54a2b7e31f8754f659d9b8d8', 'front_brick_tier_outer_planes': 'ebd994864b0eeaad156e94b6819fafd7270642f95bc966f8dd1f2b38d885fa24', 'front_stair_risers_and_treads': 'b1d3d5b211ee52b0f7a07b0e39024e2599c742e51a431e9dc4ac98f8f2007f53'}
def load_materials(root):
 root=Path(root);a=json.loads((root/'face-material-map.json').read_text());assert a['source_stl_sha256']==STL_SHA256 and a['source_triangles']==3618
 assert set(a['groups'])==set(GROUP_INDEX_SHA256)
 tri=load_stl(root/'model.stl')[2];keys=[]
 for t in tri:
  vertices=sorted([[round(float(x),5)for x in v]for v in t]);keys.append(hashlib.sha256(json.dumps(vertices,separators=(',',':')).encode()).hexdigest())
 assert len(set(keys))==3618
 materials=np.zeros(3618,np.int32);selected=set();palette={'plaster':1,'roof':2,'brick':3}
 for name,g in a['groups'].items():
  indices=[r['stl_face_index_0based'] for r in g['faces']]
  assert hashlib.sha256(json.dumps(indices,separators=(',',':')).encode()).hexdigest()==GROUP_INDEX_SHA256[name]
  assert len(indices)==g['count'] and not selected.intersection(indices);selected.update(indices)
  for r in g['faces']:
   i=r['stl_face_index_0based'];assert keys[i]==r['coordinate_key_sha256'];assert sorted([[round(float(x),5)for x in v]for v in tri[i]])==r['triangle_vertices_mm_sorted_5dp']
  expected_key='plaster' if name in ('tower_front_outer_plaster','tower_front_lower_cabin_skirt','tower_front_eave_fascia') else 'roof' if name=='tower_front_roof_slope' else 'brick'
  assert g['palette_key']==expected_key;materials[indices]=palette[expected_key]
 assert len(selected)==158 and hashlib.sha256(json.dumps(sorted(selected),separators=(',',':')).encode()).hexdigest()=='9250d0fdd52a7fa4a9248d9c83e3d4e5bfd62940614022aabc4e03232f4b9fbd'
 assert a['unknown_neutral_indices_0based']==sorted(set(range(3618))-selected)
 for indices in a['named_hold_sets'].values():assert not selected.intersection(indices)
 assert np.bincount(materials,minlength=4).tolist()==[3460,14,2,142]
 return materials
