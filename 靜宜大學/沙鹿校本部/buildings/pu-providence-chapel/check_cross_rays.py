"""Selected raw-STL normal rays. Self-contained; no repair or global-wall claim."""
from pathlib import Path
import numpy as np,json,hashlib,trimesh
R=Path(__file__).resolve().parent
W=R;T=trimesh.load(W/'model.stl',process=False).triangles
assert hashlib.sha256((W/'model.stl').read_bytes()).hexdigest()=='df84e1b7a4290b799082c7d2a2d23427fd6bb5cb3719ee2c82f73c152c84847b'
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))
S=3.5;FLOOR=12.9;y=(.31*514+790-1047)*(35/514)*S
rows=[]
for z in [65,68,70,72,74,75.1]:
 o=[0,y,z];a=ray(o,[1,0,0]);b=ray(o,[-1,0,0]);c=ray(o,[0,1,0]);d=ray(o,[0,-1,0]);assert a and b and c and d;rows.append({'z':z,'x_normal_thickness_mm':a[0]+b[0],'y_normal_thickness_mm':c[0]+d[0]})
roots=[]
for x in [-.5,0,.5]:
 o=[x,y,70];hit=ray(o,[0,0,-1]);assert hit;exit_z=70-hit[0];assert exit_z<63.99;roots.append({'x':x,'first_down_exit_z':exit_z})
r={'stl_sha256':hashlib.sha256((W/'model.stl').read_bytes()).hexdigest(),'passed':True,'cross_normal_ray_samples':rows,'root_continuity_rays':roots,'limits':'Selected actual triangle calipers at cross and root only; not global minimum wall thickness or print guarantee.'};(R/'cross-rays-check.json').write_text(json.dumps(r,indent=2));print(r)
