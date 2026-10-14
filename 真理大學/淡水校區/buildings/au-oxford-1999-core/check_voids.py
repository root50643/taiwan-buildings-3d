"""Inspect the delivered STL with directed rays. No mesh repairs or material overrides."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=True)
def first(origin,direction):
 points,_,_=m.ray.intersects_location([origin],[direction],multiple_hits=True)
 distances=np.dot(points-np.asarray(origin),np.asarray(direction))
 valid=distances>1e-7
 assert valid.any(),f'No hit for {origin}/{direction}'
 return points[valid][distances[valid].argmin()].tolist()
rows=[];checks={}
for x in [-18.1,0,18.1]:
 for z in [12.,23.]:
  hit=first([x,-66,z],[0,1,0]);ok=hit[1]>-46
  rows.append({'purpose':'front open column bay reaches recessed hall wall','origin':[x,-66,z],'hit':hit,'passed':ok});checks[f'portico_bay_{x}_{z}_clear']=ok
for x in [-14,0,14]:
 for y in [10,28,50]:
  hit=first([x,y,80],[0,0,-1]);ok=abs(hit[2]-3)<1e-5
  rows.append({'purpose':'courtyard open to print-base floor','origin':[x,y,80],'hit':hit,'passed':ok});checks[f'courtyard_{x}_{y}_open']=ok
for x in [-18,0,18]:
 hit=first([x,66,15],[0,-1,0]);ok=hit[1]<2
 rows.append({'purpose':'no fourth rear wing or courtyard addition','origin':[x,66,15],'hit':hit,'passed':ok});checks[f'rear_open_gap_{x}']=ok
# Positive controls: columns and both full-length wings must still exist.
for x in [-27.,-9.1,9.1,27.]:
 hit=first([x,-66,15],[0,1,0]);checks[f'front_column_{x}_present']=hit[1]<-55
for x in [-49.5,49.5]:
 hit=first([x,66,15],[0,-1,0]);checks[f'full_length_wing_{x}_present']=hit[1]>57
out={'passed':all(checks.values()),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'checks':checks,'rays':rows,'limitations':['Rays test selected large voids, not every surface or support condition.','The base is a presentation/printing support; courtyard openness begins above its z=3 mm top.']}
(R/'void-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
