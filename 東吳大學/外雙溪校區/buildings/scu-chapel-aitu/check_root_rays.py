"""Original STL rays for nominated roots and local thicknesses; no proxy mesh.
Not an exhaustive global wall, strength, support or physical-print evaluation.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=2.5;BASE=3.
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d);e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];q=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,q);ok=abs(det)>1e-10;inv=np.zeros(len(T));inv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*inv;r=np.cross(s,e1);v=r@d*inv;t=np.einsum('ij,ij->i',e2,r)*inv;hit=t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7)];assert len(hit);return float(hit.min())
def point(x,y,z):return [x*S,y*S,BASE+z*S]
def width(o,d):return ray(o,d)+ray(o,-np.array(d))
widths=[];roots=[]
def backing(label,x,y,z,dir=1,minpath=8):
 o=point(x,y,z);h=ray(o,[0,dir,0]);assert h>minpath*S,(label,h);roots.append({'feature':label,'origin_mm':o,'direction':[0,dir,0],'solid_path_mm':h})
# Cross stem down to tower/base; horizontal arms remain joined through stem.
o=point(-5.8,-20.8,18.8);h=ray(o,[0,0,-1]);assert abs(o[2]-h)<.02;roots.append({'feature':'cross_stem_to_base','origin_mm':o,'direction':[0,0,-1],'solid_path_mm':h})
for x,dir in [(-6.8,1),(-4.8,-1)]:
 o=point(x,-20.8,19.9);h=ray(o,[dir,0,0]);assert h>2*S;roots.append({'feature':'cross_arm_to_stem','origin_mm':o,'direction':[dir,0,0],'solid_path_mm':h})
for label,o,d in [('cross_stem_x',point(-5.8,-20.8,18.8),[1,0,0]),('cross_stem_y',point(-5.8,-20.8,18.8),[0,1,0]),('cross_arm_z',point(-6.8,-20.8,19.9),[0,0,1]),('cross_arm_y',point(-6.8,-20.8,19.9),[0,1,0])]:
 h=width(o,d);assert h>=1.49;widths.append({'feature':label,'origin_mm':o,'direction':d,'width_mm':h})
# Thickened straight ridge landing, near-top original-face local width.
o=point(-14,4,13.39999);h=width(o,[1,0,0]);assert 1.249<h<1.26;widths.append({'feature':'ridge_flat_landing_near_top','origin_mm':o,'direction':[1,0,0],'width_mm':h})
# Chapel facade grid samples root into backing, not floating picture frames.
for x in np.linspace(-20.8,-8.4,12):backing('chapel_upper_vertical',x,-21.3,6.1)
for z in np.linspace(4.65,10.8,7):backing('chapel_upper_horizontal',-19.6,-21.3,z)
for x in np.linspace(-20.4,-8.6,7):backing('chapel_lower_vertical',x,-21.1,2.1)
# Aitu narrow-band transoms, two solid spandrels and wide entrance glazing.
for x in [-1,2.5,6,9.5,18]:
 for z in [2.85,6.25,9.65]:backing('aitu_narrow_transom',x,-20.55,z)
for z in [4.6,7.95]:backing('aitu_floor_spandrel',5,-20.9,z)
for x in [12.55,14.05,15.55]:backing('aitu_wide_upper_mullion',x,-20.6,8.8)
for x in [11.3,13.3,15.3,17.0]:backing('aitu_entry_mullion',x,-20.2,2)
for x in [-2,2.5,7,11.5,16]:
 for z in [2.5,6.1,9.7]:backing('aitu_rear_mullion',x,-5.1,z,-1,8)
# Rear low retaining wall, intentionally not detailed historical balustrades.
for x in [0,10,21]:
 o=point(x,-.4,1.4);h=ray(o,[0,0,-1]);assert abs(o[2]-h)<.02;roots.append({'feature':'rear_retaining_wall_to_base','origin_mm':o,'direction':[0,0,-1],'solid_path_mm':h});w=width(o,[0,1,0]);assert w>=1.99;widths.append({'feature':'retaining_wall_y','origin_mm':o,'direction':[0,1,0],'width_mm':w})
# Actual tread levels and vertical solid roots for 6+6 front and 10 side steps.
steps=[]
for name,x,start,run,rise,n in [('chapel_steps',-15,-26.3,.55,.17,6),('aitu_steps',14,-26,.5,.16,6),('side_steps',23,-9.5,.7,.25,10)]:
 for i in range(n):
  y=start+(i+.5)*run;o=point(x,y,5);h=ray(o,[0,0,-1]);top=o[2]-h;expected=BASE+(i+1)*rise*S;assert abs(top-expected)<.02,(name,i,top,expected)
  inside=[o[0],o[1],top-.05];root=ray(inside,[0,0,-1]);assert abs(inside[2]-root)<.02
  steps.append({'family':name,'index':i,'top_z_mm':top,'nominal_tread_run_mm':run*S,'nominal_riser_mm':rise*S,'original_surface_probe_mm':o,'inside_root_origin_mm':inside,'solid_down_to_base_mm':root})
j={'passed':True,'checks':{'cross_stem_and_both_arms_rooted':True,'cross_local_calipers_at_least_1p49mm':True,'all_nominated_window_and_spandrel_backing_roots':True,'retaining_wall_rooted_and_two_mm_local_width':True,'all_22_actual_tread_levels_and_base_roots':len(steps)==22},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'root_samples':roots,'local_width_samples':widths,'stair_surface_and_root_samples':steps,'limits':'Original triangle intersections in nominated directions only. Step runs/risers are stated model dimensions, validated by discrete top probes, not global wall thickness. Historical rails/stonework are omitted; no all-direction, strength, support or print guarantee.'}
(R/'root-ray-check.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k not in ['root_samples','local_width_samples','stair_surface_and_root_samples']})
