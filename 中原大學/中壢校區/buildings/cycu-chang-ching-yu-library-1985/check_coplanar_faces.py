"""Positive-area coplanar triangle overlap screening on original STL; no repairs."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from collections import defaultdict
from shapely.geometry import Polygon
from shapely.strtree import STRtree
O=Path(__file__).parent;m=trimesh.load(O/'model.stl',process=False);T=m.triangles;groups=defaultdict(list)
for i,t in enumerate(T):
 n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)
 if n[np.argmax(abs(n))]<0:n=-n
 d=np.dot(n,t[0]);groups[tuple(np.round(n,5))+(round(d,4),)].append(i)
checked=0;bad=[]
for key,ids in groups.items():
 if len(ids)<2:continue
 axis=int(np.argmax(np.abs(key[:3])));polys=[Polygon(np.delete(T[i],axis,axis=1)) for i in ids];tree=STRtree(polys)
 for a,p in enumerate(polys):
  for b in tree.query(p):
   if b<=a:continue
   checked+=1;area=p.intersection(polys[b]).area
   if area>1e-7:bad.append({'faces':[ids[a],ids[int(b)]],'projected_overlap_area_mm2':area})
r={'passed':not bad,'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'candidate_pairs':checked,'positive_area_overlaps':bad,'method':'Original triangles grouped by canonical plane normal rounded5 decimals and distance rounded4 decimals; projected STRtree positive-area test threshold1e-7mm2. Shared edges are allowed. No geometric repair. Not exhaustive self-intersection proof.'}
(O/'coplanar-face-check.json').write_text(json.dumps(r,indent=2));print(r);assert not bad
