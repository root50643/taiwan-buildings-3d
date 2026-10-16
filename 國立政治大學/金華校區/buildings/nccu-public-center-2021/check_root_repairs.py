"""Check the exact same 20 trial05 sample lines against the revised raw trial06 STL.

This is extra root diagnostics only, never a substitute for trial06 dense QA.
The old sample points are now within the thickened material, so report the full
new material interval containing each old point, in both line directions.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip
import hashlib
import json
import sys
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
from qa_common import load_stl,require,write_json

W=[(F(1,3),)*3,tuple(map(F,('.98','.01','.01'))),tuple(map(F,('.01','.98','.01'))),
   tuple(map(F,('.01','.01','.98'))),tuple(map(F,('.495','.495','.01'))),tuple(map(F,('.01','.495','.495'))),
   tuple(map(F,('.495','.01','.495'))),tuple(map(F,('.49','.49','.02'))),tuple(map(F,('.49','.02','.49'))),tuple(map(F,('.02','.49','.49')))]
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def vec(p):return tuple(F.from_float(float(v))for v in p)
def exact(x):return f'{x.numerator}/{x.denominator}'

def main():
 fixture=json.loads((ROOT/'root-repair-fixtures.json').read_text())
 newraw,newtri,newnorm,_=load_stl(ROOT/'model.stl')
 oldsha,newsha=fixture['old_stl_sha256'],hashlib.sha256(newraw).hexdigest()
 require(oldsha=='40fdcf9c861f6e0a1aa29c278144713e2c5de3b9f8bfdef4058730e466774611','Wrong old input')
 require(newsha=='8ad969e0135c2dfcd505cc85a1a79b78c9982cac3f8b9fe6f0525de9a34a367e','Wrong new input')
 samples=fixture['samples']
 require(len(samples)==20,'Expected exactly the 20 old short samples')
 cached={};triangles=[];bounds=[]
 for tri in newtri:
  points=[]
  for p in tri:
   key=tuple(p)
   if key not in cached:cached[key]=vec(p)
   points.append(cached[key])
  triangles.append(tuple(points))
  bounds.append((min(p[0]for p in points),max(p[0]for p in points),min(p[2]for p in points),max(p[2]for p in points)))
 direction=(F(0),F(-1),F(0));rows=[]
 for sample in samples:
  require(sample['original_geometric_outward_normal']==[0.,1.,0.],'Unexpected old normal')
  index,si=sample['original_face_index'],sample['sample_index']
  old=tuple(vec(p)for p in sample['original_triangle']);weight=W[si]
  point=tuple(sum(old[j][a]*weight[j]for j in range(3))for a in range(3))
  hits=[];coplanar=[];rejected=0;candidates=0
  for face,(triangle,box)in enumerate(zip(triangles,bounds)):
   # Exact rational bounds rejection is a proof for this unchanged axis ray,
   # not a float epsilon or an unenumerated spatial index.
   if point[0]<box[0]or point[0]>box[1]or point[2]<box[2]or point[2]>box[3]:
    rejected+=1;continue
   candidates+=1
   a,b,c=triangle;e1,e2=sub(b,a),sub(c,a);n=cross(e1,e2);h=cross(direction,e2);det=dot(e1,h);relative=sub(point,a)
   if det==0:
    if dot(n,relative)==0:coplanar.append(face)
    continue
   u=dot(relative,h)/det;q=cross(relative,e1);v=dot(direction,q)/det;t=dot(e2,q)/det
   if u>=0 and v>=0 and u+v<=1:hits.append((t,face,1 if dot(n,direction)>0 else -1))
  hits.sort();events={}
  for t,face,sign in hits:events.setdefault(t,[]).append((face,sign))
  ordered=sorted(events);lower=max((t for t in ordered if t<0),default=None);upper=min((t for t in ordered if t>0),default=None)
  signs_before={sign for _,sign in events.get(lower,[])};signs_after={sign for _,sign in events.get(upper,[])}
  valid=lower is not None and upper is not None and signs_before=={-1}and signs_after=={1}and F(0)not in events
  length=upper-lower if valid else None
  row={'old_face_index':index,'old_sample_index':si,'old_first_chord_mm':sample['first_solid_chord_mm'],
       'unchanged_old_surface_point_mm':[float(v)for v in point],'exact_unchanged_old_surface_point_rationals':[exact(v)for v in point],
       'unchanged_inward_line_direction':[0,-1,0],
       'all_new_faces_enumerated':rejected+candidates,'exact_axis_bounds_rejected_faces':rejected,'exact_triangle_tests':candidates,
       'new_forward_and_backward_transverse_hits':[{'signed_distance_from_old_point_mm':float(t),'exact_distance_rational':exact(t),'new_face_index':face,'enter_minus_exit_plus':sign}for t,face,sign in hits],
       'exact_coplanar_candidate_face_indices':coplanar,
       'old_point_is_in_new_material_interval':valid,
       'new_material_interval_containing_old_point_mm':[float(lower),float(upper)]if valid else None,
       'new_root_length_mm':float(length)if valid else None,
       'new_root_length_ge_0p8mm':valid and length>=F(4,5),
       'new_interval_boundary_faces':[{'new_face_index':face,'vertices_mm':newtri[face].tolist(),'saved_outward_normal':newnorm[face].tolist()}
          for face,_ in events.get(lower,[])+events.get(upper,[])]}
  rows.append(row)
 report={'old_stl_sha256':oldsha,'new_stl_sha256':newsha,'diagnostic_only':True,'production_strict_unchanged':True,
         'all_20_previous_lines_checked':len(rows)==20,'all_previous_roots_now_ge_0p8mm':all(row['new_root_length_ge_0p8mm']for row in rows),
         'minimum_new_root_length_mm':min((row['new_root_length_mm']for row in rows if row['new_root_length_mm']is not None),default=None),
         'samples':rows,'method':'Keep each old original barycentric point and its original -Y inward line exactly. Enumerate every new original triangle, reject impossible intersections only by exact rational X/Z bounds, and recompute all remaining signed forward/backward transverse hits with exact rational predicates. Find the oriented new material interval containing the old point. No old ray line is translated, no new dense sample is substituted, and no production acceptance is changed.'}
 report['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 report['fixtures_sha256']=hashlib.sha256((ROOT/'root-repair-fixtures.json').read_bytes()).hexdigest()
 write_json(ROOT/'qa/boundaries/previous-short-root-evidence.json',report)
 require(report['all_previous_roots_now_ge_0p8mm'] and report['all_20_previous_lines_checked'],'Root repair check failed')
 print(json.dumps({k:v for k,v in report.items()if k not in ['samples','method']},indent=2))

if __name__=='__main__':main()
