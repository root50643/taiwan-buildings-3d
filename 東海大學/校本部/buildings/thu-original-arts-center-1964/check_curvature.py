#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, numpy as np, trimesh
R=Path(__file__).resolve().parent; P=json.loads((R/'parameters.json').read_text());K=P['fabrication']['mm_per_plan_pixel'];M=K*P['source_era']['nominal_pixels_per_metre'];margin=P['fabrication']['roof_flat_rim_width_mm']
mesh=trimesh.load(R/'output/model.stl',process=False)
checks=[]
for name,cx,cy,xedge,yedge,rise in [('classroom quadrant',149,142,184,177,.6*M),('hall quadrant',394,123,422.5,174.5,.8*M)]:
    samples=[];z=[]
    for u,v in [(0.2,0.2),(.8,.2),(.2,.8),(.8,.8)]:
        x=(cx-104)*K+u*((xedge-cx)*K-margin);y=(390-cy)*K-v*((yedge-cy)*K-margin)
        loc,_,_=mesh.ray.intersects_location(np.array([[x,y,100.]]),np.array([[0.,0.,-1.]]),multiple_hits=True)
        height=float(max(loc[:,2]));z.append(height);samples.append({'u':u,'v':v,'x_mm':x,'y_mm':y,'raw_STL_roof_z_mm':height})
    delta=z[3]-z[1]-z[2]+z[0]
    checks.append({'part':name,'samples':samples,'measured_mixed_height_difference_mm':delta,'expected_bilinear_difference_mm':-.36*rise,'nonplanar_four_sample_test_pass':abs(delta)>.5})
manifest=json.loads((R/'output/build-manifest.json').read_text()); error_bound=0.0
for roof in manifest['roofs']:
    x0,x1,y0,y1=roof['bounds_px'];cx,cy=roof['head_px']
    du=max((cx-x0)*K/(((cx-x0)*K-margin)*14),(x1-cx)*K/(((x1-cx)*K-margin)*14))
    dv=max((cy-y0)*K/(((cy-y0)*K-margin)*14),(y1-cy)*K/(((y1-cy)*K-margin)*14))
    error_bound=max(error_bound,(roof['rim_mm']-roof['valley_mm'])*du*dv/4)
report={'stl_sha256':hashlib.sha256((R/'output/model.stl').read_bytes()).hexdigest(),'scope':'Two exposed example quadrants only; curvature illustration, never normal-thickness or root certification','passed':all(c['nonplanar_four_sample_test_pass'] for c in checks),'method':'Vertical ray intersections with final raw STL. A planar quadrant has zero mixed height difference at the four sample corners; each tested quadrant is demonstrably nonplanar.','formula':'z = valley + rise*(u + v - u*v), with a separately recorded 1.1mm high-rim band','subdivisions_per_quadrant':14,'pre_simplification_triangulation_vertical_error_bound_mm':error_bound,'additional_simplification_tolerance_mm':.0002,'checks':checks}
(R/'output/qa-curvature.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

raise SystemExit(0 if report['passed'] else 1)
