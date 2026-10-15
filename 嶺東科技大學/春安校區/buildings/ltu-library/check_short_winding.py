"""Long-double all-triangle winding for every short-normal interval and chosen root.
Preserves raw two-face failures; no face deletion or alternative distant-wall jump.
"""
from pathlib import Path
import json,numpy as np,trimesh,tempfile,subprocess,hashlib
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);short=json.loads((R/'dense-short-chords.json').read_text())['short_chords'];roots=json.loads((R/'vertex-roots.json').read_text())['rows'];points=[];rows=[]
for q,r in zip(short,roots):
 assert q['original_triangle_index']==r['face'] and q['sample_index']==r['sample']
 p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);o=p+n*1e-6;h=q['all_ray_intersections_mm_face'];gap=h[2][0]-h[1][0]if len(h)>2 else 1
 probes=[o,o-n*(h[0][0]+min((h[1][0]-h[0][0])/4,1e-5)),o-n*((h[0][0]+h[1][0])/2),o-n*(h[1][0]+min(gap/4,1e-5))]
 d=np.array(r['chosen']['direction']);start=p+d*1e-5;rh=ray.hits(start,d);rgap=rh[1][0]-rh[0][0]if len(rh)>1 else 1
 probes += [start,start+d*(rh[0][0]/2),start+d*(rh[0][0]+min(1e-5,rgap/4))]
 ids=list(range(len(points),len(points)+len(probes)));points.extend(probes);rows.append(dict(face=r['face'],sample=r['sample'],point_indices=ids,expected=[0,1,1,0,1,1,0],original_normal_hits=h,chosen_root=r['chosen'],root_all_hits=rh))
with tempfile.TemporaryDirectory()as td:
 D=Path(td);np.asarray(m.triangles,dtype='<f8').tofile(D/'tri.bin');np.array(points,dtype='<f8').tofile(D/'pts.bin');subprocess.run(['g++','-O3','-std=c++17',str(R/'original_winding.cpp'),'-o',str(D/'wind')],check=True);subprocess.run([str(D/'wind'),str(D/'tri.bin'),str(D/'pts.bin'),str(D/'w.csv')],check=True);vals=np.loadtxt(D/'w.csv',delimiter=',')[:,1]
for row in rows:
 row['winding']=[float(vals[i])for i in row['point_indices']];row['points_mm']=[points[i].tolist()for i in row['point_indices']];row['valid']=all(abs(v-e)<1e-7 for v,e in zip(row['winding'],row['expected']))
checks={'every_short_original_first_interval_material_then_air':all(all(abs(v-e)<1e-7 for v,e in zip(q['winding'][:4],q['expected'][:4]))for q in rows),'every_chosen_root_starts_material_and_continues_to_first_air':all(all(abs(v-e)<1e-7 for v,e in zip(q['winding'][4:],q['expected'][4:]))for q in rows)}
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),count=len(rows),point_count=len(points),checks=checks,rows=rows,limits='High-precision finite probes; strict normal-short report remains false. Independent reviewer must assess the actual corner geometry and chosen incident directions.')
(R/'short-winding.json').write_text(json.dumps(r));print(checks, 'failed',[(q['face'],q['sample'],q['winding'])for q in rows if not q['valid']]);raise SystemExit(0 if all(checks.values())else 1)
