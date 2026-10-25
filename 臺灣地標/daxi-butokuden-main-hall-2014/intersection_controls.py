#!/usr/bin/env python3
"""Positive and negative fixtures for the delivered triangle-intersection checker."""
from pathlib import Path
import argparse,subprocess,json,hashlib,tempfile,sys
import numpy as np,trimesh
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();(a.out/'qa').mkdir(parents=True,exist_ok=True);items={}
items['single_manifold_cube']=(trimesh.creation.box([2,2,2]),True)
u=trimesh.creation.box([2,2,2]);v=trimesh.creation.box([2,2,2]);v.apply_translation([.8,.6,.5]);items['overlapping_cubes']=(trimesh.util.concatenate([u,v]),False)
items['crossing_triangles']=(trimesh.Trimesh(vertices=[[-2,-2,0],[2,-2,0],[0,2,0],[0,-1,-2],[0,-1,2],[0,2,0]],faces=[[0,1,2],[3,4,5]],process=False),False)
items['coplanar_triangles']=(trimesh.Trimesh(vertices=[[-2,-2,0],[2,-2,0],[0,2,0],[-1,-1,0],[3,-1,0],[1,3,0]],faces=[[0,1,2],[3,4,5]],process=False),False)
v=np.array([[-2,-2,0],[2,-2,0],[0,2,0],[-1,-1,0],[3,-1,0],[1,3,0]],float);v[3:,2]=v[3:,0]*2e-7;items['near_coplanar_overlap']=(trimesh.Trimesh(vertices=v,faces=[[0,1,2],[3,4,5]],process=False),False)
items['shared_edge_triangles']=(trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0],[1,1,0]],faces=[[0,1,2],[1,3,2]],process=False),True)
u=trimesh.creation.box([2,2,2]);v=trimesh.creation.box([2,2,2]);v.apply_translation([4,0,0]);items['disjoint_cubes']=(trimesh.util.concatenate([u,v]),True)
items['shared_vertex_only']=(trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0],[-1,0,1],[0,-1,1]],faces=[[0,1,2],[0,3,4]],process=False),True)
items['coplanar_t_junction']=(trimesh.Trimesh(vertices=[[0,0,0],[4,0,0],[0,4,0],[1,0,0],[2,-2,0],[3,0,0]],faces=[[0,1,2],[3,4,5]],process=False),False)
items['coplanar_vertex_on_edge']=(trimesh.Trimesh(vertices=[[0,0,0],[4,0,0],[0,4,0],[2,0,0],[1,-2,0],[3,-2,0]],faces=[[0,1,2],[3,4,5]],process=False),False)
items['noncoplanar_vertex_on_face']=(trimesh.Trimesh(vertices=[[-2,-2,0],[2,-2,0],[0,2,0],[0,0,0],[1,0,2],[0,1,2]],faces=[[0,1,2],[3,4,5]],process=False),False)
# Reusable numerical regression fixtures from prior authored test geometry, not source imagery or this building.
# Their only true contact is a shared vertex. Ill-conditioned determinant evaluation
# formerly reported points metres outside the other triangle's projected footprint.
regressions = {
 'near_parallel_shared_vertex_fan_972_14889': [[[-86.0,-40.0,24.399999618530273],[-50.439998626708984,-42.70000076293945,16.71139907836914],[-50.439998626708984,-44.79999923706055,16.71139907836914]],[[-86.0,-40.0,24.399999618530273],[-50.3661003112793,38.97249984741211,16.69540023803711],[-50.439998626708984,37.099998474121094,16.71139907836914]]],
 'near_parallel_shared_vertex_fan_973_14887': [[[-86.0,-40.0,24.399999618530273],[-50.35599899291992,-42.44139862060547,16.693199157714844],[-50.439998626708984,-42.70000076293945,16.71139907836914]],[[-86.0,-40.0,24.399999618530273],[-50.439998626708984,35.0,16.71139907836914],[-50.439998626708984,32.900001525878906,16.71139907836914]]],
 'near_parallel_shared_vertex_fan_1469_14887': [[[-86.0,-40.0,24.399999618530273],[-50.35599899291992,-27.74139976501465,16.693199157714844],[-50.439998626708984,-28.0,16.71139907836914]],[[-86.0,-40.0,24.399999618530273],[-50.439998626708984,35.0,16.71139907836914],[-50.439998626708984,32.900001525878906,16.71139907836914]]]
}
for name,triangles in regressions.items():
 items[name]=(trimesh.Trimesh(vertices=np.asarray(triangles).reshape(-1,3),faces=[[0,1,2],[3,4,5]],process=False),True)
items['near_parallel_true_crossing']=(trimesh.Trimesh(vertices=[[-100,-100,0],[100,-100,0],[0,100,0],[-80,-80,-.00008],[80,-80,.00008],[0,80,0]],faces=[[0,1,2],[3,4,5]],process=False),False)
report=[]
with tempfile.TemporaryDirectory(prefix='intersection-controls-')as tmp:
 for name,(m,expected)in items.items():
  d=Path(tmp)/name;(d/'qa').mkdir(parents=True);m.export(d/'daxi-butokuden-main-hall-2014.stl');run=subprocess.run([sys.executable,str(Path(__file__).with_name('validate_self_intersections.py')),'--out',str(d)],capture_output=True);data=json.loads((d/'qa/self-intersection-validation.json').read_text());assert data['all_pass']==expected,(name,data)
  assert (run.returncode==0)==expected,(name,run.returncode)
  report.append({'control':name,'expected_clear':expected,'reported_clear':data['all_pass'],'intersections_reported':len(data['forbidden_intersections']),'stl_sha256':hashlib.sha256((d/'daxi-butokuden-main-hall-2014.stl').read_bytes()).hexdigest(),'exit_code':run.returncode,'rejected_unconfirmed_hit_points':data.get('rejected_unconfirmed_hit_points',0)})
(a.out/'qa/self-intersection-controls.json').write_text(json.dumps({'all_expected_outcomes':True,'controls':report},indent=2)+'\n');print(json.dumps(report))
