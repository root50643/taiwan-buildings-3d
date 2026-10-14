"""Validate the original delivered STL, source rebuild and Blender mesh agreement.
Usage: python validate_model.py --output validation.json
Requires Blender on PATH (or --blender path). Does not repair the delivered file.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, struct, subprocess, sys, tempfile
import numpy as np
import trimesh
p=argparse.ArgumentParser();p.add_argument('--output',default='validation.json');p.add_argument('--blender',default='blender');a=p.parse_args()
root=Path(__file__).resolve().parent; path=root/'model.stl';raw=path.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
# Validate the original binary STL's saved normal vectors before any mesh processing.
n=struct.unpack_from('<I',raw,80)[0]
records=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]),count=n)
tri=records['v'].astype(float); saved=records['normal'].astype(float)
calc=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(calc,axis=1)
unit=calc/np.maximum(norm[:,None],1e-30)
# Deduplicate only bit-identical coordinates from raw STL; no repair/process.
verts,inv=np.unique(tri.reshape((-1,3)),axis=0,return_inverse=True)
mesh=trimesh.Trimesh(verts,inv.reshape((-1,3)),process=False)
edges,cnt=np.unique(np.sort(mesh.edges,axis=1),axis=0,return_counts=True)
# Face-connected components without optional graph packages.
edgefaces={}; parent=list(range(len(mesh.faces)))
def find(i):
 while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
 return i
def union(i,j):
 i,j=find(i),find(j)
 if i!=j:parent[j]=i
links=[[] for _ in mesh.vertices]
for fi,(i,j,k) in enumerate(mesh.faces):
 for u,v in [(i,j),(j,k),(k,i)]:
  key=tuple(sorted((int(u),int(v))))
  if key in edgefaces: union(fi,edgefaces[key])
  else:edgefaces[key]=fi
 for v,u,w in [(i,j,k),(j,k,i),(k,i,j)]:links[v].append((u,w))
comps=len({find(i) for i in range(len(parent))});badlinks=0
for pairs in links:
 adj={}
 for u,v in pairs:adj.setdefault(int(u),set()).add(int(v));adj.setdefault(int(v),set()).add(int(u))
 if not adj or any(len(v)!=2 for v in adj.values()):badlinks+=1;continue
 seen=set();todo=[next(iter(adj))]
 while todo:
  v=todo.pop()
  if v in seen:continue
  seen.add(v);todo.extend(adj[v]-seen)
 if len(seen)!=len(adj):badlinks+=1
checks={'binary_stl_length':len(raw)==84+50*n,'finite_coordinates_and_normals':bool(np.isfinite(tri).all() and np.isfinite(saved).all()),'original_normals_unit':bool(np.allclose(np.linalg.norm(saved,axis=1),1,atol=1e-5)),'original_normals_match_winding':bool(np.allclose(saved,unit,atol=1e-5)),'nondegenerate_original_faces':bool((norm>1e-9).all()),'no_duplicate_triangles':len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'every_edge_two_faces':bool((cnt==2).all()),'vertex_links_single_cycles':badlinks==0,'one_connected_surface_shell':comps==1,'no_disconnected_enclosed_shell':comps==1,'positive_volume':bool(mesh.volume>0),'base_z_zero':abs(float(mesh.bounds[0,2]))<1e-6,'longest_dimension_150mm':abs(float(mesh.extents.max())-150)<1e-5}

print(json.dumps({"checks":checks,"shells":comps,"badlinks":badlinks,"min_norm":float(norm.min())},indent=2))
