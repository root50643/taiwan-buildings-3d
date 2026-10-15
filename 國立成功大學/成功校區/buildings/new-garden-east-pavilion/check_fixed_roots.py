"""Original short-chord evidence with fixed, source-feature-bounded material roots.
No search for a favorable direction. Original short values/air/hits are preserved.
The strict normal report stays false. This tests backed relief only, not universal
0.8 mm thickness. Every path and complete interval needs independent verification.
"""

import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,gzip,hashlib,collections
import numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).resolve().parent
mesh=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(mesh)
original=json.load(gzip.open(R/'dense-short-samples.json.gz','rt'))
EPS=1e-5
# Bind raw evidence to this actual mesh and to every original face/sample row.
import csv,io
strict=json.loads((R/'dense-short-chords.json').read_text())
if strict['stl_sha256']!=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest():raise RuntimeError('Strict report STL mismatch')
if strict['short_chords_sha256']!=hashlib.sha256((R/'dense-short-samples.json.gz').read_bytes()).hexdigest():raise RuntimeError('Raw short detail hash mismatch')
raw_csv=gzip.open(R/'dense-original.csv.gz','rb').read()
if hashlib.sha256(raw_csv).hexdigest()!=strict['uncompressed_csv_sha256']:raise RuntimeError('Original diagnostic CSV hash mismatch')
raw_rows=list(csv.DictReader(io.StringIO(raw_csv.decode())))
if len(raw_rows)!=len(mesh.faces)*10:raise RuntimeError('Original face/sample coverage count mismatch')
raw_map={(int(q['face']),int(q['sample'])):q for q in raw_rows}
if len(raw_map)!=len(mesh.faces)*10 or set(raw_map)!={(i,j) for i in range(len(mesh.faces)) for j in range(10)}:raise RuntimeError('Original face/sample identities incomplete')
short_keys={k for k,q in raw_map.items() if float(q['first_solid'])<.8}
keys=[(q['original_triangle_index'],q['sample_index']) for q in original]
if len(keys)!=len(set(keys)) or set(keys)!=short_keys or len(original)!=strict['under_0p8mm_count']:raise RuntimeError('Original short samples omitted, duplicated or changed')
W=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.01,.495,.495],[.495,.01,.495],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]])
for q in original:
 key=(q['original_triangle_index'],q['sample_index']);i,j=key
 p=W[j]@mesh.triangles[i];n=mesh.face_normals[i]
 if not np.allclose(p,q['surface_point_mm'],rtol=0,atol=1e-12) or not np.allclose(n,q['original_outward_normal'],rtol=0,atol=1e-12):raise RuntimeError('Short point/normal is not current original triangle sample')
 if q['original_cpp_row']!=raw_map[key]:raise RuntimeError('Original numeric row changed')
 h=ray.hits(p+n*1e-6,-n);old=q['all_ray_intersections_mm_face']
 if len(h)!=len(old) or any(abs(a[0]-b[0])>1e-9 or a[1]!=b[1] for a,b in zip(h,old)):raise RuntimeError('Original intersections differ from current triangles')


from root_rules import classify

def intervals(origin,direction):
 h=ray.hits(origin,direction)
 return {'origin_mm':origin.tolist(),'direction':direction.tolist(),'all_hits_mm_face':h,
         'first_material_length_mm':h[0][0] if h else None,
         'next_air_length_mm':h[1][0]-h[0][0] if len(h)>1 else None,
         'has_next_material_entry':len(h)>1}

rows=[];unclassified=[]
for q in original:
 p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);c=classify(p,n)
 if c is None:unclassified.append(q);continue
 family,d,target,axis=c;o=p-EPS*n;length=(target-o[axis])/d[axis];anchor=o+d*length
 root=intervals(o,d);plus=intervals(anchor,n);minus=intervals(anchor,-n)
 nh=q['all_ray_intersections_mm_face'];first=nh[1][0]-nh[0][0];gap=nh[2][0]-nh[1][0] if len(nh)>2 else None
 checks={'fixed_source_family':True,'root_direction_tangent_to_original_normal':abs(float(d@n))<1e-12,
         'anchor_distance_positive':bool(length>0),'complete_path_has_no_crossing_before_anchor':bool(root['all_hits_mm_face'] and root['all_hits_mm_face'][0][0]>length+.8),
         'root_first_hit_outward':bool(root['all_hits_mm_face'] and mesh.face_normals[root['all_hits_mm_face'][0][1]]@d>0),
         'anchor_both_directions_start_material_and_full_span_ge_0p8':bool(plus['all_hits_mm_face'] and minus['all_hits_mm_face'] and plus['first_material_length_mm']+minus['first_material_length_mm']>=.8),
         'original_first_value_preserved':abs(first-q['first_solid_chord_mm'])<1e-12}
 rows.append({'original':q,'family':family,'inward_offset_mm':EPS,'offset_point_mm':o.tolist(),
              'fixed_root_direction':d.tolist(),'fixed_anchor_coordinate_axis':axis,'fixed_anchor_coordinate_mm':target,
              'anchor_point_mm':anchor.tolist(),'offset_to_anchor_length_mm':float(length),
              'original_first_material_mm':first,'original_following_air_mm':gap,
              'continuous_root':root,'anchor_positive_normal':plus,'anchor_negative_normal':minus,
              'anchor_full_normal_material_span_mm':plus['first_material_length_mm']+minus['first_material_length_mm'] if plus['all_hits_mm_face'] and minus['all_hits_mm_face'] else None,
              'checks':checks,'passed':all(checks.values())})
with (R/'fixed-root-samples.json.gz').open('wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:g.write(json.dumps(rows,separators=(',',':')).encode())
checks={'every_original_short_sample_classified':len(rows)==len(original) and not unclassified,'all_local_path_and_interval_checks':all(r['passed'] for r in rows)}
out={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'original_strict_passed':False,
     'raw_short_detail_sha256':hashlib.sha256((R/'dense-short-samples.json.gz').read_bytes()).hexdigest(),'raw_csv_uncompressed_sha256':hashlib.sha256(raw_csv).hexdigest(),'original_sample_count':len(original),'family_counts':dict(collections.Counter(r['family'] for r in rows)),
     'minimum_original_first_material_mm':min(r['original_first_material_mm'] for r in rows),
     'minimum_continuous_root_material_mm':min(r['continuous_root']['first_material_length_mm'] for r in rows),
     'minimum_anchor_full_normal_material_span_mm':min(r['anchor_full_normal_material_span_mm'] for r in rows),
     'unclassified':unclassified,'failed':[{'face':r['original']['original_triangle_index'],'sample':r['original']['sample_index'],'checks':r['checks']} for r in rows if not r['passed']],
     'detail_file':'fixed-root-samples.json.gz','detail_sha256':hashlib.sha256((R/'fixed-root-samples.json.gz').read_bytes()).hexdigest(),
     'limits':'Moller-Trumbore interval evidence only. Complete original-triangle boundary and solid-angle controls are required separately. Original strict short-normal diagnostic stays false.'}
out['evidence_sources']={n:__import__('hashlib').sha256((R/n).read_bytes()).hexdigest() for n in ['check_fixed_roots.py', 'root_rules.py', 'original_rays.py']}
(R/'fixed-roots.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(0 if out['passed'] else 1)
