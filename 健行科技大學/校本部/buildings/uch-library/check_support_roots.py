"""All12 main/canopy supports: original axis chords at5 heights and9 footprint roots.
No tolerance merge or repair; widths are solid intervals containing designated support centres.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False);S=150/52;ZH=.75;GL=2;rows=[]
def hit(o,d):
 o=np.array(o,float);d=np.array(d,float);p,_,f=m.ray.intersects_location([o],[d],multiple_hits=True);h=sorted((float(np.dot(q-o,d)),int(fi))for q,fi in zip(p,f)if np.dot(q-o,d)>0);u=[]
 for a in h:
  if not u or abs(a[0]-u[-1][0])>1e-6:u.append(a)
 return u
supports=[('south-wing',x,-19.45,1.2,1.1,0,11.5)for x in [-9.65,9.65]]+[('main-corner',x,-9.45,1.1,1.1,0,12.05)for x in [-19.45,19.45]]+[('canopy',x,y,.48,.48,1.1,3.1)for x in [-23.5,-20,-16,-11.5]for y in [-10.6,-1.6]]
for family,x,y,w,d,z,h in supports:
 widths=[];roots=[]
 for level in np.linspace(z+.1,z+h-.1,5):
  p=np.array([x*S,y*S,GL+level*S*ZH])
  for axis,nom in [(0,w*S),(1,d*S)]:
   direction=np.eye(3)[axis];hs=hit(p-direction*200,direction);assert len(hs)%2==0;iv=[(a,b)for a,b in zip(hs[::2],hs[1::2])if a[0]<=200<=b[0]];assert len(iv)==1;actual=iv[0][1][0]-iv[0][0][0];assert actual>=nom-1e-5
   widths.append(dict(z_mm=p[2],axis=axis,nominal_width_mm=nom,original_solid_width_at_center_mm=actual,entry_exit_faces=[iv[0][0][1],iv[0][1][1]],all_original_hits=hs))
 for dx in [-w*S/2+.05,0,w*S/2-.05]:
  for dy in [-d*S/2+.05,0,d*S/2-.05]:
   o=[x*S+dx,y*S+dy,-1];hs=hit(o,[0,0,1]);required=GL+(z+h-.05)*S*ZH;assert len(hs)>=2 and abs(hs[0][0]-1)<1e-5 and hs[1][0]-1>=required,(family,x,y,dx,dy,hs,required)
   roots.append(dict(xy_mm=o[:2],first_solid_exit_z_mm=hs[1][0]-1,required_root_z_mm=required,all_original_hits=hs))
 rows.append(dict(family=family,center_xy_m=[x,y],nominal_section_mm=[w*S,d*S],width_samples=widths,footprint_root_samples=roots))
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),passed=True,checks={'twelve_supports_five_height_two_axis_chords':len(rows)==12,'all_nine_footprint_points_rooted_from_base':True,'all_original_support_widths_at_least_nominal':True},minimum_nominal_canopy_width_mm=.48*S,minimum_nominal_main_width_mm=1.1*S,supports=rows,limits='Only designated posts; attached posts may merge with walls and have larger measured intervals. Other glazing/roof faces require separate checks; no global wall guarantee.')
(R/'support-roots.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k!='supports'})
