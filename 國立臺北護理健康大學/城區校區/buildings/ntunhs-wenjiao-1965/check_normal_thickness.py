"""Sample actual STL fin/stair normal thickness and top-root continuity. No mesh repair."""
from pathlib import Path
import numpy as np,json,hashlib,trimesh,math
O=Path(__file__).resolve().parent;P=O/'model.stl';T=trimesh.load(P,process=False).triangles

def hits(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);good=abs(det)>1e-10;iv=np.zeros_like(det);iv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,h)*iv;q=np.cross(s,e1);v=q@d*iv;t=np.einsum('ij,ij->i',e2,q)*iv;ok=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7);return sorted(set(round(float(x),6) for x in t[ok]))
fin=[];theta=math.radians(-25);n=np.array([math.cos(theta),math.sin(theta),0]);depth=np.array([-math.sin(theta),math.cos(theta),0])
for x in np.linspace(-44.8,44.8,35):
 for z in [13,22,31]:
  c=np.array([x,-20,z])+depth*(-.9);h=hits(c,n);h2=hits(c,-n);assert h and h2;th=h[0]+h2[0];assert 1.09<th<1.11,(x,z,th,h,h2)
  root=np.array([x,-20,z])+depth*.9;hroot=hits(root,depth);assert hroot and hroot[0]>1
  fin.append({'x':float(x),'z':z,'normal_thickness_mm':th,'root_to_next_boundary_mm':hroot[0]})
stairs=[]
for start,end,width,z0,z1 in [((-40.5,5.5),(-40.5,13.5),4,2.7,7),((-35.8,14.5),(-35.8,7),4,7,10.3),((42.6,31),(39.8,23.2),6,2.7,7.8),((32.4,19.8),(32.4,11.2),4.8,7.8,10.8)]:
 a=np.array(start);b=np.array(end);L=np.linalg.norm(b-a);direction=(b-a)/L;k=(z1-z0)/L;n=np.array([-k*direction[0],-k*direction[1],1]);n/=np.linalg.norm(n);measures=[]
 for f in np.linspace(.08,.92,29):
  pos=a+(b-a)*f;z=z0+(z1-z0)*f-.65;c=np.array([*pos,z]);up=hits(c,n);down=hits(c,-n);assert up and down;th=up[0]+down[0];measures.append({'fraction':float(f),'normal_thickness_mm':th});assert th>.99
 root0=np.array([*(a+(b-a)*.98),z0+(z1-z0)*.98-.2]);root1=np.array([*(b+direction*.1),z1-.2]);vv=root1-root0;length=np.linalg.norm(vv);hh=hits(root0,vv);assert not [t for t in hh if t<length-1e-5],(start,end,hh,length)
 stairs.append({'top_root_internal_segment_start':root0.tolist(),'top_root_internal_segment_end':root1.tolist(),'top_root_no_boundary_crossing':True,'start':list(start),'end':list(end),'designed_substrate_normal_mm':1.3/math.sqrt(1+k*k),'min_sampled_actual_normal_mm':min(x['normal_thickness_mm'] for x in measures),'samples':measures})
d={'stl_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'method':'Original unprocessed triangle ray intersections; sampled actual normal thickness, not exhaustive wall thickness. Fins root begins 0.9 mm along local depth, remains inside solid until backing boundary.','fins':fin,'stairs':stairs,'passed':True};(O/'normal-thickness-check.json').write_text(json.dumps(d,indent=2));print('fins',min(x['normal_thickness_mm'] for x in fin),'stairs',[x['min_sampled_actual_normal_mm'] for x in stairs])
