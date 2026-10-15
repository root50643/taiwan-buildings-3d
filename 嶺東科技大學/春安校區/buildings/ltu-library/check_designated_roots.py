"""Specified four post roots and 28 stair tread original-face chords, no mesh repair."""
from pathlib import Path
import json,numpy as np,trimesh,hashlib
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);P=json.loads((R/'source-parameters.json').read_text());S=P['scale_mm_per_m'];A=np.array(P['rotation_xy']);C=np.array(P['rotated_center_m']);GL=P['ground_m']
def pt(p):return np.r_[(A@np.array(p[:2])-C)*S,(p[2]+GL)*S]
def direction(d):return np.r_[A@np.array(d[:2]),d[2]]
def through(p,d):
 x=pt(p);d=direction(d);d/=np.linalg.norm(d);h=ray.hits(x-d*250,d);iv=[(a,b)for a,b in zip(h[::2],h[1::2])if a[0]<250<b[0]];assert len(iv)==1,(p,d,h);a,b=iv[0];return dict(source_point_m=list(map(float,p)),direction=d.tolist(),width_mm=b[0]-a[0],entry_exit_original_faces=[a[1],b[1]],all_hits=h)
posts=[]
for p in P['posts']:
 x,y=p['center'];chords=[through([x,y,z],d)for z in [.5,p['top']/2,p['top']-.2]for d in [[1,0,0],[0,1,0]]];roots=[]
 for dx in [-.15,0,.15]:
  for dy in [-.15,0,.15]:
   q=pt([x+dx,y+dy,0]);h=ray.hits([q[0],q[1],-1],[0,0,1]);roots.append(dict(xy_mm=q[:2].tolist(),all_hits=h,first_entry_z_mm=h[0][0]-1,first_exit_z_mm=h[1][0]-1,required_top_mm=(p['top']+GL)*S))
 posts.append(dict(source=p,chords=chords,roots=roots))
steps=[]
for p in P['steps']:
 ds=[[*p['run_direction'],0],[*p['cross_direction'],0],[0,0,1]];steps.append(dict(source=p,chords=[through(p['center'],d)for d in ds]))
checks={'all_designated_post_normal_widths_ge_0p8':all(c['width_mm']>=.8 for p in posts for c in p['chords']),'all_36_post_rays_continuous_base_to_top':all(abs(r['first_entry_z_mm'])<1e-5 and r['first_exit_z_mm']>=r['required_top_mm']-1e-5 for p in posts for r in p['roots']),'all_28_tread_centre_three_direction_chords_ge_0p8':all(c['width_mm']>=.8 for p in steps for c in p['chords'])}
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,passed=all(checks.values()),posts=posts,steps=steps,limits='Specified original-face chord and support-root samples, not a global wall theorem. Stairs/canopies still need print supports.')
(R/'designated-roots.json').write_text(json.dumps(r,indent=2));print(checks);assert r['passed']
