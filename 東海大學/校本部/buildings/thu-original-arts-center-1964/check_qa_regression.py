#!/usr/bin/env python3
"""Synthetic regression cases for false/nonzero strict QA gates."""
from pathlib import Path
import tempfile,json,subprocess,sys
import numpy as np,trimesh,manifold3d as md
from build import deterministic_stl
HERE=Path(__file__).resolve().parent

def run():
 rows=[]
 with tempfile.TemporaryDirectory(prefix='qa-regression-',dir=HERE) as td:
  root=Path(td)
  base=trimesh.creation.box(extents=[10,10,2]);base.apply_translation([5,5,1])
  cases=[('valid_box',base,None,True,False),('oversized',trimesh.creation.box(extents=[151,10,2]),None,False,True),('negative_volume',trimesh.Trimesh(base.vertices,base.faces[:,::-1],process=False),None,False,True),('stored_normal_nonunit',base,'nonunit',False,True),('stored_normal_reversed',base,'reversed',False,True)]
  thin=trimesh.creation.box(extents=[.6,10,2]);thin.apply_translation([.3,5,1]);cases.append(('vanished_polygon',thin,None,False,False))
  solid=md.Manifold.cube([5,5,2])+md.Manifold.cube([5,5,2]).translate([6,0,0])+md.Manifold.cube([1.1,.6,2]).translate([4.95,2.2,0])
  raw=solid.to_mesh64();split=trimesh.Trimesh(np.asarray(raw.vert_properties)[:,:3],raw.tri_verts,process=False);cases.append(('split_polygon',split,None,False,False))
  for name,m,mutate,expected,top_only in cases:
   out=root/name;out.mkdir();deterministic_stl(m,out/'model.stl')
   if mutate:
    b=bytearray((out/'model.stl').read_bytes());n=np.frombuffer(b,dtype='<f4',offset=84,count=3);n*=2 if mutate=='nonunit' else -1;(out/'model.stl').write_bytes(b)
   args=[sys.executable,str(HERE/'qa.py'),'--out',str(out)]+(['--topology-only'] if top_only else [])
   proc=subprocess.run(args,capture_output=True,text=True)
   top=json.loads((out/'qa-topology.json').read_text());sec=json.loads((out/'qa-sections.json').read_text()) if (out/'qa-sections.json').exists() else None
   actual=proc.returncode==0
   row={'case':name,'expected_pass':expected,'exit_code':proc.returncode,'actual_pass':actual,'topology_pass':top['passed'],'sections_pass':sec['passed'] if sec else None,'regression_passed':actual==expected}
   if name=='oversized':row['regression_passed'] &= not top['gates']['max_dimension_150mm']
   if name=='negative_volume':row['regression_passed'] &= not top['gates']['positive_volume']
   if name=='stored_normal_nonunit':row['regression_passed'] &= not top['gates']['stored_unit_normals']
   if name=='stored_normal_reversed':row['regression_passed'] &= not top['gates']['stored_normals_nonpositive_dot']
   if name in ['split_polygon','vanished_polygon']:row['regression_passed'] &= bool(sec and sec['split_or_vanished']>0)
   rows.append(row)
 result={'passed':all(r['regression_passed'] for r in rows),'cases':rows}
 (HERE/'output'/'qa-regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result['passed']
if __name__=='__main__':raise SystemExit(0 if run() else 1)
