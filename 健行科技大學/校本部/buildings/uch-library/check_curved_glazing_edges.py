"""Investigate all short near-edge first chords without hiding the original interval.
Distance to true original dihedral edges, first interval material/air, and actual adjacent-face corner-bisector backing rays.
This evidence is not automatic approval of a short-chord exception.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).parent;m0=trimesh.load(R/'model.stl',process=False);v,ix=np.unique(m0.triangles.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,ix.reshape(-1,3),process=False);d=json.loads((R/'surface-chords.json').read_text());mask=m.face_adjacency_angles>np.radians(12);edges=m.vertices[m.face_adjacency_edges[mask]];edge_faces=m.face_adjacency[mask];a=edges[:,0];e=edges[:,1]-a;ee=np.einsum('ij,ij->i',e,e);rows=[]
def hits(o,d):
 p,_,f=m0.ray.intersects_location([o],[d],multiple_hits=True);r=sorted((float(np.dot(q-o,d)),int(fi))for q,fi in zip(p,f)if np.dot(q-o,d)>1e-7);u=[]
 for x in r:
  if not u or abs(x[0]-u[-1][0])>1e-6:u.append(x)
 return u
for q in d['short_chords']:
 p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);h=q['all_ray_intersections_mm_face'];o=p+n*1e-6
 first=(h[0][0]+h[1][0])/2;gap=(h[2][0]-h[1][0])if len(h)>2 else None;after=h[1][0]+min(.001,gap/4 if gap else .001)
 material=bool(m0.contains([o-n*first])[0]);air=not bool(m0.contains([o-n*after])[0]);t=np.clip(np.einsum('ij,ij->i',p-a,e)/ee,0,1);dist=np.linalg.norm(p-(a+e*t[:,None]),axis=1);k=int(np.argmin(dist))
 nn=m.face_normals[edge_faces[k]];rad=-nn.sum(axis=0);rad/=np.linalg.norm(rad);inside=p+rad*.02;rootinside=bool(m0.contains([inside])[0]);rh=hits(inside,rad);assert material and air and rootinside and rh,(q,material,air,rootinside,rh)

 rows.append(dict(original_triangle_index=q['original_triangle_index'],sample_index=q['sample_index'],surface_point_mm=p.tolist(),original_outward_normal=n.tolist(),original_first_solid_chord_mm=q['first_solid_chord_mm'],first_interval_midpoint_is_material=material,immediately_after_first_exit_is_air=air,air_gap_after_first_exit_mm=gap,nearest_true_dihedral_edge_distance_mm=float(dist[k]),nearest_true_edge_mm=edges[k].tolist(),true_edge_adjacent_face_indices=edge_faces[k].tolist(),true_edge_adjacent_normals=nn.tolist(),inward_true_corner_bisector=rad.tolist(),bisector_inward_0p02mm_is_material=rootinside,bisector_first_exit_after_backing_mm=rh[0][0],all_bisector_hits=rh))
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),samples=rows,count=len(rows),maximum_distance_to_true_edge_mm=max(x['nearest_true_dihedral_edge_distance_mm']for x in rows),minimum_bisector_backing_first_exit_mm=min(x['bisector_first_exit_after_backing_mm']for x in rows),checks={'all_short_chord_midpoints_material_and_after_exit_air':True,'all_short_chords_have_true_corner_bisector_solid_backing':True},status='Evidence only; strict original-normal0.8mm check still fails and requires independent review, not reclassified as globally thick.')
(R/'curved-glazing-edge-evidence.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k!='samples'})
