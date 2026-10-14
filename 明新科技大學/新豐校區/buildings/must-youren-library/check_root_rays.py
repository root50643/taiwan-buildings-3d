"""Nominated original STL triangle-ray roots and local calipers; no proxy mesh.
These samples are not exhaustive global thickness, strength or support proofs.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=2.7;BASE=3.
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;inv=np.zeros(len(T));inv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*inv;r=np.cross(s,e1);v=r@d*inv;t=np.einsum('ij,ij->i',e2,r)*inv;hit=t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)];assert len(hit);return float(hit.min())
def point(x,y,z):return [x*S,y*S,BASE+z*S]
def backing(label,x,y,z):
 o=point(x,y,z);h=ray(o,[0,1,0]);assert h>40*S,(label,h);return {'feature':label,'origin_mm':o,'positive_y_solid_path_mm':h}
rows=[];widths=[]
for i,x in enumerate(np.linspace(-17.1,17.1,17)):
 for sign in [-1,1]:rows.append(backing('arch_%02d_border_%s'%(i,sign),x+sign*1.06,-22.07,8))
 if i%2==0:
  for z in [8,12,16]:
   o=point(x,-21.55,z);h=ray(o,[1,0,0])+ray(o,[-1,0,0]);assert h>=.8;rows.append(backing('glass_%02d_vertical_z%s'%(i,z),x,-21.55,z));widths.append({'origin_mm':o,'direction':'x','width_mm':h})
  for z in [5.3,9.9,14.5,18.0]:
   if abs(x)<8 and z<5.55:continue
   o=point(x+.50,-21.55,z+.175);h=ray(o,[0,0,1])+ray(o,[0,0,-1]);assert h>=.8;rows.append(backing('glass_%02d_horizontal_z%s'%(i,z),x+.5,-21.55,z+.175));widths.append({'origin_mm':o,'direction':'z','width_mm':h})
# Glass entrance mullions are behind the true entry recess.
for i,x in enumerate(np.linspace(-6.5,6.5,7)):
 rows.append(backing('entry_vertical_%s'%i,x,-20.8,2.5));o=point(x,-20.8,2.5);h=ray(o,[1,0,0])+ray(o,[-1,0,0]);assert h>=.8;widths.append({'origin_mm':o,'direction':'x','width_mm':h})
columns=[]
for x in [-8.1,8.1]:
 o=point(x,-24.35,3);down=ray(o,[0,0,-1]);up=ray(o,[0,0,1]);assert abs(o[2]-down)<.02;assert abs(o[2]+up-(BASE+6.35*S))<.02
 columns.append({'origin_mm':o,'down_to_base_mm':down,'up_through_canopy_mm':up})
roof=[]
for x,y,z in [(0,17.5,20.7),(-18.2,2.7,20.9),(17.7,16.5,21),(0,0,22)]:
 o=point(x,y,z);h=ray(o,[0,0,-1]);assert abs(o[2]-h)<.02;roof.append({'origin_mm':o,'down_to_base_mm':h})
j={'passed':True,'checks':{'all_34_arch_border_roots':True,'all_nominated_dark_glazing_and_entry_roots':True,'all_selected_local_widths_at_least_0p8mm':True,'both_canopy_columns_connected_base_to_canopy':True,'three_roof_volumes_and_skylight_root_to_body':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'backing_root_samples':rows,'local_width_samples':widths,'minimum_sampled_local_width_mm':min(x['width_mm'] for x in widths),'canopy_column_roots':columns,'roof_roots':roof,'limits':'Original triangle intersections in specified directions/locations only. Not all-direction/global minimum wall thickness, structural strength, full support analysis or print test.'}
(R/'root-ray-check.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k not in ['backing_root_samples','local_width_samples','canopy_column_roots','roof_roots']})
