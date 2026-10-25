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
report=[]
with tempfile.TemporaryDirectory(prefix='intersection-controls-')as tmp:
 for name,(m,expected)in items.items():
  d=Path(tmp)/name;(d/'qa').mkdir(parents=True);m.export(d/'nknu-yanchao-library-information.stl');run=subprocess.run([sys.executable,str(Path(__file__).with_name('validate_self_intersections.py')),'--out',str(d)],capture_output=True);data=json.loads((d/'qa/self-intersection-validation.json').read_text());assert data['all_pass']==expected,(name,data)
  assert (run.returncode==0)==expected,(name,run.returncode)
  report.append({'control':name,'expected_clear':expected,'reported_clear':data['all_pass'],'intersections_reported':len(data['forbidden_intersections']),'stl_sha256':hashlib.sha256((d/'nknu-yanchao-library-information.stl').read_bytes()).hexdigest(),'exit_code':run.returncode})
(a.out/'qa/self-intersection-controls.json').write_text(json.dumps({'all_expected_outcomes':True,'controls':report},indent=2)+'\n');print(json.dumps(report))
