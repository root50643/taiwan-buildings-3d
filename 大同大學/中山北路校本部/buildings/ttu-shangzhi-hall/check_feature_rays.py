"""Selected normal-thickness/root and open-space rays against original STL.
Not exhaustive wall thickness, toolpaths, support design or physical print QA.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=150/68;B=2.4
E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0]
def ray(o,d):
 o=np.asarray(o,float);d=np.asarray(d,float);p=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,p);good=abs(det)>1e-10;inv=np.zeros(len(T));inv[good]=1/det[good];s=o-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,E1);v=q@d*inv;t=np.einsum('ij,ij->i',E2,q)*inv
 return sorted(set(round(float(x),7) for x in t[good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)]))
def pt(x,y,z):return np.array([x*S,y*S,B+z*S])
rows=[];roots=[];spaces=[]
def thickness(label,o,d,min_width=.8):
 a=ray(o,d);b=ray(o,-np.asarray(d));assert a and b,(label,'no exit');w=a[0]+b[0];assert w>=min_width,(label,w);rows.append({'feature':label,'origin_mm':o.tolist(),'normal':list(d),'thickness_mm':w,'reference_minimum_mm':min_width})
def root(label,o,d,target):
 hits=ray(o,d);assert hits,(label,'no root exit');exit=o+np.asarray(d)*hits[0];assert abs(exit[2]-target)<1e-4,(label,exit,target);roots.append({'feature':label,'origin_mm':o.tolist(),'direction':list(d),'first_exit_mm':exit.tolist(),'expected_exit_z_mm':target})
for side in [-1,1]:
 for i,y in enumerate(np.linspace(-6.55,6.55,6)):
  for z in [5.8,10.0,15.45]:
   o=pt(side*17.65,y,z)
   thickness(f'portico_{side}_column_{i}_z{z}_X',o,[1,0,0],2.0);thickness(f'portico_{side}_column_{i}_z{z}_Y',o,[0,1,0],2.0)
  root(f'portico_{side}_column_{i}_base',pt(side*17.65,y,10),[0,0,-1],0)
 # Court-end colonnade piers are rooted into base, and openings remain clear.
 for i,x in enumerate([-7.5,-4.5,-1.5,1.5,4.5,7.5]):
  o=pt(x,side*26.15,2.0);thickness(f'court_{side}_pier_{i}',o,[1,0,0],2.0);root(f'court_{side}_pier_{i}_base',o,[0,0,-1],0)
 for x in [-6,-3,0,3,6]:
  o=pt(x,side*25.8,2);h=ray(o,[0,side,0]);assert h and h[0]>3.5*S,(x,side,h[:1]);spaces.append({'feature':'end_gallery_open_bay','origin_mm':o.tolist(),'clear_depth_mm':h[0]})
 for x in [-6,0,6]:
  for y in [14,18,24]:
   o=pt(x,side*y,6.5);up=ray(o,[0,0,1]);assert not up,(x,side*y,up);down=ray(o,[0,0,-1]);assert down;z=o[2]-down[0];assert z<=B+.6*S+1e-5;spaces.append({'feature':'open_to_sky_courtyard','origin_mm':o.tolist(),'up_hits':0,'first_ground_or_pond_z_mm':z})
 # Outer parapet at a source-backed baluster recess: remaining web measured.
 for y in [-27.9,12.1]:thickness(f'outer_rail_{side}_{y}',pt(side*18.8,y,5.6),[1,0,0],1.0)
# Top collar, axis samples of same annular miniature (not a global minimum).
for a in [0,np.pi/2,np.pi,3*np.pi/2]:
 o=pt(1.20*np.cos(a),1.20*np.sin(a),25.8);d=[np.cos(a),np.sin(a),0];thickness('top_collar_radial',o,d,1.3);root('top_collar_root',o,[0,0,-1],0)
# Bell roots upward in the porch ceiling; it is intentionally suspended.
o=pt(-16.3,0,15.5);thickness('west_bell_stem_X',o,[1,0,0],2.0);thickness('west_bell_stem_Y',o,[0,1,0],2.0)
h=ray(o,[0,0,1]);assert h and o[2]+h[0]>B+18*S;roots.append({'feature':'west_bell_ceiling_connection','origin_mm':o.tolist(),'first_up_exit_z_mm':o[2]+h[0],'support_warning':'Suspended bell requires slicer support assessment; remove supports gently.'})
# Major portico glazing bars are thin relief rooted in backing, not floating.
for side in [-1,1]:
 for y in [-4.1,4.1]:
  for z,h in [(5.65,3.1),(11.1,3.6)]:
   o=pt(side*14.10,y,z+.6);thickness('backed_vertical_glazing_bar',o,[0,1,0],.8)
   inward=ray(o,[-side,0,0]);assert inward and inward[0]>S
   roots.append({'feature':'glazing_bar_into_backing','origin_mm':o.tolist(),'inward_first_exit_distance_mm':inward[0]})
   o=pt(side*14.10,y-.5,z+h*.47);thickness('backed_horizontal_glazing_bar',o,[0,0,1],.8)
# Middle-row pediments are backed relief on the cylinder, not separate triangles.
for side in [-1,1]:
 o=pt(0,side*11.55,10.0);h=ray(o,[0,-side,0]);assert h and h[0]>11.5*S
 roots.append({'feature':'cylinder_window_pediment_into_body','origin_mm':o.tolist(),'inward_first_exit_distance_mm':h[0]})
checks={'all_selected_normal_widths_pass':True,'selected_roots_continuous_to_base_or_ceiling':True,'both_courtyards_open_to_sky':True,'end_gallery_bays_open':True}
r={'passed':True,'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'normal_thickness_samples':rows,'root_samples':roots,'open_space_samples':spaces,'limitations':['Only nominated original-triangle rays, not exhaustive global minimum wall thickness.','No physical printing or actual slicer paths.','Portico/colonnade roofs and bell may need support; no unsupported-print claim.']};(R/'feature-rays.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print({k:v for k,v in r.items() if not isinstance(v,list)})
