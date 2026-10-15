"""All original axis-aligned planar faces: reject positive-area coplanar overlap.
No repair or face deletion. Applicable to this all-box source, not arbitrary curved mesh.
"""
from pathlib import Path
import json,hashlib,collections,numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.strtree import STRtree
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.linalg.norm(N,axis=1)[:,None];groups=collections.defaultdict(list);bad=[];tested=0
for i,(t,n) in enumerate(zip(T,N)):
 axis=int(np.argmax(abs(n)));assert abs(n[axis])>1-1e-10 and np.max(t[:,axis])-np.min(t[:,axis])<1e-10
 groups[(axis,float(t[0,axis]))].append(i)
for (axis,pos),ids in groups.items():
 axes=[a for a in range(3) if a!=axis];polys=[Polygon(T[i][:,axes]) for i in ids];tree=STRtree(polys)
 for k,p in enumerate(polys):
  assert p.is_valid and p.area>0
  for l in tree.query(p):
   l=int(l)
   if l<=k:continue
   tested+=1;a=p.intersection(polys[l]).area
   if a>1e-9:bad.append({'faces':[ids[k],ids[l]],'area_mm2':a,'opposite_normals':bool(np.dot(N[ids[k]],N[ids[l]])<0),'axis':axis,'plane_mm':pos})
j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':not bad,'checks':{'all_original_faces_axis_aligned':True,'no_positive_area_coplanar_original_face_overlap':not bad},'triangles':len(T),'plane_groups':len(groups),'bbox_candidate_pairs':tested,'overlaps':bad,'limits':'Exact saved STL plane groups and positive-area 2D intersections. This explicitly excludes coincident opposite inner faces for the current axis-aligned source, but does not claim an arbitrary general self-intersection algorithm.'};(R/'coplanar-original-face-check.json').write_text(json.dumps(j,indent=2));print(j);assert j['passed']
