"""Actual STL triangle ray probes of retained posts. No proxy/repair.
Specific post-axis roots and local tangential widths; not global wall thickness.
"""
from pathlib import Path
import numpy as np,json,hashlib,trimesh,math
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles
S=2.;BASE=3.
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv;return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))
rows=[]
for i in range(32):
 t=math.radians(i*360/32);signed=(i*360/32+180)%360-180;enclosed=-157.5<=signed<=-22.5;ra=29.55 if enclosed else 28.6;rb=29.55 if enclosed else 30.;a=np.array([ra*math.cos(t)*S,ra*math.sin(t)*S,BASE+(8.55 if enclosed else 6.35)*S]);b=np.array([rb*math.cos(t)*S,rb*math.sin(t)*S,BASE+13.85*S]);o=(a+b)/2
 if enclosed:
  # Probe within the wall-facing part of each pier, not exactly on the
  # sector end boundary or a grazing exterior tangent.
  o-=np.array([math.cos(t),math.sin(t),0])*.4
  if abs(signed+157.5)<.01:o+=np.array([-math.sin(t),math.cos(t),0])*.2
  if abs(signed+22.5)<.01:o-=np.array([-math.sin(t),math.cos(t),0])*.2
 d=(b-a)/np.linalg.norm(b-a);down=ray(o,-d)[0];up=ray(o,d)[0];dz=(o-d*down)[2];uz=(o+d*up)[2]
 tangent=[-math.sin(t),math.cos(t),0];width_origin=(a+b)/2; width=ray(width_origin,tangent)[0]+ray(width_origin,-np.array(tangent))[0]
 assert dz<=BASE+6.61*S and uz>=BASE+13.54*S and width>=1.79,(i,dz,uz,width)
 rows.append({'post':i,'first_axis_down_exit_z_mm':dz,'first_axis_up_exit_z_mm':uz,'tangent_width_mm':width,'root_origin_mm':o.tolist(),'width_origin_mm':width_origin.tolist(),'axis_unit':d.tolist()})
entry=[]
for angle in [-29,-15,0,15,29]:
 t=math.radians(angle);o=np.array([34.6*math.cos(t)*S,34.6*math.sin(t)*S,BASE+8*S]);down=ray(o,[0,0,-1])[0];up=ray(o,[0,0,1])[0]
 assert o[2]-down<=BASE+.02 and o[2]+up>=BASE+11.44*S
 width=ray(o,[1,0,0])[0]+ray(o,[-1,0,0])[0];assert width>=1.89
 entry.append({'angle_degrees':angle,'down_exit_z_mm':o[2]-down,'up_exit_z_mm':o[2]+up,'x_width_mm':width})
report={'passed':True,'checks':{'all_32_main_posts_slanted_or_wall_piers_rooted_into_body_and_roof':True,'all_5_entry_posts_rooted_to_base_and_canopy':True,'main_sampled_tangent_width_at_least_1p79mm':True,'entry_sampled_width_at_least_1p89mm':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'main_posts':rows,'entry_posts':entry,'limits':'Specific retained-post probes using raw STL triangles. Not an exhaustive minimum-wall survey, unsupported-span test, slicer toolpath or physical print test.'}
(R/'root-ray-check.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['main_posts','entry_posts']},indent=2))
