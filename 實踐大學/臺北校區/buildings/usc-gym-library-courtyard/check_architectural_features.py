"""Finite occupancy probes on the original STL, without repairs or rounding.
This confirms selected voids/masses. It does not prove appearance or global thickness.
"""
from pathlib import Path
import hashlib,json,os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
p=json.loads((R/'parameters.json').read_text());s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm']
rows=[
 ('N lower south half of double-height aperture',113.5,43,12,False),
 ('N upper north half of double-height aperture',113.5,56,17.5,False),
 ('N upper south open bay',113.5,44,18,False),
 ('N north-third internal support',114,52.8,15,True),
 ('N continuous north-end concrete strip',113.1,65,16,True),
 ('N ground colonnade opening',116,33,2,False),
 ('N ground north glass/core mass',115,66,2,True),
 ('M undercroft between columns',30,15,4,False),
 ('M recessed backing wall',26,15,4,True),
 ('M V-column central open space',39.4,50.1,4,False),
 ('M north platform underside open zone',38,52,4,False),
 ('Courtyard raised lawn mass',70,35,.3,True),
 ('West court shallow descending entry void',40,12.5,-.5,False),
 ('N narrow roof slot lies below parapet',126.2,40,28.3,False),
 ('M south lower annex',20,-8,4,True),
 ('M southwest stair projection',10,-16,4,True),
]
for i,(px,py) in enumerate(p['skylight_centres_orthophoto_px']):
 x=(px-50)*p['orthophoto_resolution_m_per_px'];y=(520-py)*p['orthophoto_resolution_m_per_px'];rows.append((f'Lawn skylight {i+1} body',x,y,.85,True))
mesh=trimesh.load_mesh(R/'model.stl',process=False)
points=np.array([[x*s,y*s,base+z*s] for _,x,y,z,_ in rows]);found=mesh.contains(points)
reports=[{'name':r[0],'point_mm':point.tolist(),'expected_solid':r[4],'observed_solid':bool(f),'passed':bool(f)==r[4]} for r,point,f in zip(rows,points,found)]
report={'passed':all(x['passed'] for x in reports),'checker_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'checks':reports,'method':'Trimesh occupancy parity at fixed points; process=False, no STL modification','limits':'Finite source-informed probes. Not all facade openings, measured geometry, global manifold validity or global thickness proof.'}
(R/'architectural-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
