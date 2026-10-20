"""Finite local solid/air/root and slice opening tests, not universal thickness proof."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
A=Path(__file__).resolve().parent;t=trimesh.load_mesh(A/'model.stl',process=True);reg=json.loads((A/'qa/design-registration.json').read_text());rows=[]
def probe(name,p,want):
 got=bool(t.contains([p])[0]);rows.append({'name':name,'point':p,'expected_solid':want,'solid':got,'pass':got==want})
probe('path-side open volume',[64,-15,25],False)
probe('red wall core',[64,-4,25],True)
probe('track-side long wall',[64,21,20],True)
probe('cropped stairwell air above lowest tread',[57,-13,8.7],False)
probe('basement cropped floor',[60,-13,2],True)
for x in np.arange(30.5,78,4):
 for z in [9.8,12,17.8,18.5]:probe('rail rooted and continuous',[float(x),-24.7,z],True)
 probe('open rail spacing',[float(x)+2,-24.7,14],False)
for i,q in enumerate(reg['skylight_triangles']):
 c=np.mean(q,axis=0)
 for dz,solid in [(-.3,False),(-1.2,True),(-2.8,False)]:probe('skylight%d recess/backing/underside'%i,[float(c[0]),float(c[1]),float(c[2]+dz)],solid)
raw=md.Manifold(md.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32)))
local=[]
for z,roi,name in [(12,box(29,-26,79,-23),'rail upright strip'),(18.5,box(29,-26,79,-23),'rail top'),(24.8,box(125,-20,132,-14),'far roof tip'),(42.999,box(90,15,100,25),'roof apex')]:
 g=GeometryCollection()
 for c in raw.slice(z).to_polygons():g=g.symmetric_difference(Polygon(c))
 p=g.intersection(roi);opened=g.buffer(-.4,quad_segs=16).buffer(.4,quad_segs=16).intersection(roi)
 local.append({'name':name,'z_mm':z,'original_area_mm2':p.area,'opened_area_mm2':opened.area,'lost_area_mm2':p.difference(opened).area,'survives':not opened.is_empty,'warning':'Opening loses convex corners even on thick members; not equivalent to all-direction thickness.'})
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'probe_count':len(rows),'all_probes_pass':all(p['pass'] for p in rows),'probes':rows,'local_0_8mm_opening':local,'global_minimum_thickness_certified':False,'physical_print_tested':False}
(A/'qa/features.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='probes'},indent=2));print('Failed probes:',[p for p in rows if not p['pass']]);assert r['all_probes_pass']
