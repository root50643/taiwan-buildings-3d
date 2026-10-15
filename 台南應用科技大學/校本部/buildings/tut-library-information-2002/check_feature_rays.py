"""Original STL first-chord and root checks. Finite samples, not global min wall."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
O=Path(__file__).parent;m=trimesh.load(O/'model.stl',process=False);T=m.triangles;p=json.loads((O/'draft-parameters.json').read_text());s=p['scale_mm_per_m'];B=1.2*s
xy=lambda q:np.array([(q[0]-359.5)*p['aerial_m_per_px'],(331.5-q[1])*p['aerial_m_per_px']]);pts=[xy(q) for q in p['roof_pixel_trace']];ctr=np.mean(pts,axis=0)
def frame(i):
 a=pts[i];b=pts[(i+1)%6];u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
 if n@(ctr-(a+b)/2)<0:n=-n
 return a,u,n,np.linalg.norm(b-a)
def hits(o,d):
 o=np.array(o);d=np.array(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;iv=np.zeros(len(T));iv[ok]=1/det[ok];ss=o-T[:,0];u=np.einsum('ij,ij->i',ss,q)*iv;r=np.cross(ss,e1);v=r@d*iv;t=np.einsum('ij,ij->i',e2,r)*iv
 return sorted(set(round(float(x),7) for x in t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-6)]))
def mm(q):return np.array(q)*s+[0,0,B]
checks={};samples=[]
def root(name,q,d,min_mm):
 h=hits(mm(q),d);got=h[0] if h else 0;checks[name]=got>=min_mm;samples.append({'name':name,'source_point_m':list(q),'direction':list(d),'first_exit_mm':got,'required_min_mm':min_mm,'all_hits_mm':h[:5]})
a,u,n,L=frame(3)
# Four/ five actual main portico posts, plus separate two awning posts.
for k,x in enumerate([3,L*.29,L*.5,L*.71,L-3]):
 q=a+u*x+n*1.1
 root('portico_down_'+str(k),[*q,3],[0,0,-1],(3+1.2)*s-1e-3)
 root('portico_up_'+str(k),[*q,3],[0,0,1],6.3*s)
for k,x in enumerate([L*.31+.65,L*.69-.65]):
 q=a+u*x-n*4.8
 root('awning_post_down_'+str(k),[*q,3],[0,0,-1],(3+1.2)*s-1e-3)
 root('awning_post_up_'+str(k),[*q,3],[0,0,1],3*s)
 for j,d in enumerate([[u[0],u[1],0],[-u[0],-u[1],0],[n[0],n[1],0],[-n[0],-n[1],0]]):root(f'awning_post_halfwidth_{k}_{j}',[*q,3],d,.55*s*.7)
# Actual original STL world-X/Y total widths at both detached post shafts.
post_widths=[]
for k,x in enumerate([L*.31+.65,L*.69-.65]):
 q=a+u*x-n*4.8;o=mm([*q,3]);width=[]
 for axis in [0,1]:
  d=np.eye(3)[axis];width.append(hits(o,d)[0]+hits(o,-d)[0])
 checks['awning_post_XY_width_'+str(k)]=min(width)>=1.1*s-1e-4
 post_widths.append({'post':k,'X_width_mm':width[0],'Y_width_mm':width[1]})
for k,t in enumerate([.1,.3,.5,.7,.9]):
 x=L*.31+L*.38*t;z=6.6+1.7*np.sin(np.pi*t)-.5;q=a+u*x+n*3.5
 root('awning_rear_solid_root_'+str(k),[*q,z],[n[0],n[1],0],2*s)
# North roof low round cap shares horizontal solid deck and body to base.
q=xy((287,287));root('round_cap_down_to_base',[*q,47],[0,0,-1],48.2*s-1e-3)
dense=json.loads((O/'dense-first-chords.json').read_text());sha=hashlib.sha256((O/'model.stl').read_bytes()).hexdigest();assert dense['stl_sha256']==sha
source=T.mean(axis=1)/s-[0,0,1.2];dep=(source[:,:2]-a)@n;along=(source[:,:2]-a)@u
wa,wu,wn,wL=frame(5);wd=(source[:,:2]-wa)@wn
masks={'barrel_roof_posts_and_shoulders':(dep>-5.6)&(dep<4.1)&(along>L*.30)&(along<L*.70)&(source[:,2]>5.25)&(source[:,2]<8.4),'roof_round_cap':(np.linalg.norm(source[:,:2]-xy((287,287)),axis=1)<5)&(source[:,2]>45.9),'west_projecting_frames_and_groove_edges':(wd>-.7)&(wd<1)&(source[:,2]>.5)&(source[:,2]<45),'front_upper_frames_and_grooves':(dep>-.6)&(dep<1)&(source[:,2]>30)&(source[:,2]<44)}
regions={}
for name,mask in masks.items():
 ids=set(np.where(mask)[0].tolist());rows=[r for r in dense['samples'] if r['face'] in ids];regions[name]={'faces':len(ids),'probes':len(rows),'minimum_original_normal_first_chord_mm':min(r['first_solid_mm'] for r in rows),'below_0p8_count':sum(r['first_solid_mm']<.8 for r in rows),'short_samples':[r for r in rows if r['first_solid_mm']<.8]}
r={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha,'root_samples':samples,'two_post_XY_widths':post_widths,'dense_regions':regions,'limitations':'First chord retained including short real corners. Directional roots separately recorded and never substituted as global normal minimum. Decorative backed relief is not an isolated thin wall; short corners require independent case review. No print/slicer test.'};(O/'feature-ray-check.json').write_text(json.dumps(r,indent=2));print('root checks',r['passed']);print({k:{a:b for a,b in v.items() if a!='short_samples'} for k,v in regions.items()});assert r['passed']
