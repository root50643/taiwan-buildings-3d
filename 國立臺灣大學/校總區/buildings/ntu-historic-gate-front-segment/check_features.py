"""Finite local geometry and air tests; not universal printability certification."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
A=Path(__file__).resolve().parent;t=trimesh.load_mesh(A/'model.stl',process=True);rows=[]
def probe(name,p,want):
 got=bool(t.contains([p])[0]);rows.append(dict(name=name,point=p,expected_solid=want,solid=got,passed=got==want))
for side in [-1,1]:
 for y in [-1,3,6,10,13]:probe('pedestrian portal is genuinely through', [side*47,y,15],False)
 probe('portal lintel',[side*47,6,28],True)
 probe('wing rooting',[side*35,6,3.2],True)
 for z in [4,15,30,35,39]:probe('lamp rooted continuous',[side*68,6,z],True)
for x in [-15,0,15]:
 R=(27**2+6.5**2)/13;y=R-(R*R-x*x)**.5
 probe('window recess air',[x,y+.5,25],False)
 probe('window solid backing',[x,y+2.2,25],True)
probe('neutral rear closure',[0,10.5,25],True)
probe('omitted rear guardhouse',[0,14,25],False)
probe('top neutral closure air',[20,9,46],False)
probe('top neutral closure support',[20,9,44.9],True)
for z in [48,51,53]:probe('stepped pedestal continuous',[0,5,z],True)
raw=md.Manifold(md.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32)))
local=[]
for z,roi,name in [(35,box(63,1,73,3),'lantern panel and raised frames'),(41.6,box(62,0,74,12),'lantern cap tip near top'),(41.799,box(62,0,74,12),'lantern cap at top minus 0.001'),(27,box(40,1,54,11),'portal lintel'),(38.1,box(-13,-1,13,3),'plaque front'),(10,box(-25,-1,25,1.5),'bowed masonry relief')]:
 g=GeometryCollection()
 for c in raw.slice(z).to_polygons():g=g.symmetric_difference(Polygon(c))
 p=g.intersection(roi);opened=g.buffer(-.4,quad_segs=16).buffer(.4,quad_segs=16).intersection(roi)
 local.append(dict(name=name,z_mm=z,original_area_mm2=p.area,opened_area_mm2=opened.area,lost_area_mm2=p.difference(opened).area,survives=not opened.is_empty,warning='Opening removes convex corners too; shallow mortar and lantern tips are not certified 0.8 mm details.'))
r=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),probe_count=len(rows),all_probes_pass=all(p['passed'] for p in rows),probes=rows,local_0_8mm_opening=local,global_minimum_thickness_certified=False,physical_print_tested=False)
(A/'qa/features.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));assert r['all_probes_pass']
