#!/usr/bin/env python3
"""Synthetic closed-shell and vertex-link fixtures for the exported topology checker."""
import pathlib,argparse,json
import numpy as np,trimesh
from mesh_topology import check_topology
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
cube=trimesh.creation.box([2,2,2]);cases=[]
cases.append(('single_oriented_cube',cube.vertices,cube.faces,True))
cases.append(('missing_triangle',cube.vertices,cube.faces[:-1],False))
faces=cube.faces.copy();faces[0]=faces[0][::-1];cases.append(('one_inverted_triangle',cube.vertices,faces,False))
cases.append(('duplicated_triangle',cube.vertices,np.concatenate([cube.faces,cube.faces[:1]]),False))
cases.append(('unreferenced_vertex',np.concatenate([cube.vertices,[[8,8,8]]]),cube.faces,False))
other=cube.copy();other.apply_translation([2,2,2]);touch=trimesh.util.concatenate([cube,other]);touch.merge_vertices()
cases.append(('two_shells_touching_only_at_vertex',touch.vertices,touch.faces,False))
other=cube.copy();other.apply_translation([4,0,0]);apart=trimesh.util.concatenate([cube,other]);cases.append(('two_disjoint_shells',apart.vertices,apart.faces,False))
rows=[]
for name,v,f,expected in cases:
 r=check_topology(v,f,name);assert r['all_pass']==expected,(name,r)
 rows.append({'control':name,'expected_pass':expected,'actual_pass':r['all_pass'],
  'closed_shells':r['closed_shells'],'nonmanifold_vertex_links':r['nonmanifold_vertex_links'],
  'nonmanifold_edges':r['nonmanifold_edges'],'inconsistently_oriented_edges':r['inconsistently_oriented_edges']})
(a.out/'qa').mkdir(parents=True,exist_ok=True)
(a.out/'qa/topology-controls.json').write_text(json.dumps({'all_expected_outcomes':True,'controls':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
