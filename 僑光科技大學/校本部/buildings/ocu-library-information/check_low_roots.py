"""Original shaded-window blade sections, continuous backing roots and designated post roots."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);S=1.6552519477888414;a=np.radians(-2.5);A=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1.]])
def pt(p):return A@(np.array(p)+[0,0,1.3])*S
def interval(p,d):
 d=A@np.array(d,float);h=ray.hits(pt(p)-250*d,d);assert len(h)%2==0
 iv=[(x,y)for x,y in zip(h[::2],h[1::2])if x[0]<250<y[0]];assert len(iv)==1,(p,h)
 return dict(original_normal=d.tolist(),local_point_m=p,first_solid_width_mm=iv[0][1][0]-iv[0][0][0],containing_faces=[iv[0][0][1],iv[0][1][1]],all_original_hits=h)
features=[]
for z in [7,12.1]:
 for x in [5.5,13.5,21.5,29.5]:
  if not(z==7 and x in[13.5,21.5]):features.append(('south',x,-28.3,z+1.65,6))
 for x in [-16,-8,0]:features.append(('south',x,-28.3,z+1.65,6))
for z in [6.8,11.8]:features.append(('southwest',-27,-24.8,z+1.65,8.3))
for x in [-5,6,17,28]:features.append(('terrace',x,-27.9,20.35,8.5))
for x in [-24,-13,-2,9,20,30]:features.append(('north',x,25.4,6.1,8.2))
rows=[]
for family,x,y,z,w in features:
 samples=[]
 for dx in [-.30*w,0,.30*w]:
  v=interval([x+dx,y,z+.275],[0,0,1]);assert v['first_solid_width_mm']>=.55*S-1e-5
  b=interval([x+dx,y,z+.275],[0,1,0]);assert b['first_solid_width_mm']>=1.0*S
  samples.append(dict(vertical_blade=v,continuous_wall_backing=b))
 rows.append(dict(family=family,center_m=[x,y,z+.275],samples=samples))
posts=[]
for family,x,y,w,d,z,top,backquarter in [('entry',x,-27.4,1.5,1.5,0,5.85,False)for x in[6,18,30]]+[('terrace',x,-27.3,1.3,2.3,17.3,top,True)for x,top in[(-19.3,22.4),(-7.4,27.4),(1.4,27.4)]]:
 roots=[]
 for dx in [-.4,0,.4]:
  for dy in [-.2,0,.2]:
   q=pt([x+dx,y+dy,0]);h=ray.hits([q[0],q[1],-1],[0,0,1]);assert abs(h[0][0]-1)<1e-5 and h[1][0]-1>=pt([x,y,top])[2]-1e-5,(family,x,y,dx,dy,h[:4],pt([x,y,top])[2])
   roots.append(dict(local_xy_m=[x+dx,y+dy],first_exit_z_mm=h[1][0]-1,required_continuous_z_mm=pt([x,y,top])[2],all_original_hits=h))
 posts.append(dict(family=family,root_region='rear supporting footprint only'if backquarter else 'central footprint',roots=roots))
checks=dict(all_source_visible_shades_vertical_and_backing_pass=True,all_six_designated_post_roots_continuous=True)
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),passed=True,checks=checks,shades=rows,posts=posts,limits='Three stations per designated shade; nine roots per specified post support region. Terrace fronts are cantilevered; root test is the stated rear footprint, not every overhanging point. No global wall guarantee.')
(R/'low-roots.json').write_text(json.dumps(r,indent=2));print(checks)
