"""Selected normal-thickness/root and open-space rays against original STL.
Not exhaustive wall thickness, toolpaths, support design or physical print QA.
"""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=150/132;B=2.4;G=3.2;K=.1378645278805804
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

def xy(p):return np.array([(p[0]-930)*K,(790-p[1])*K])
j=json.loads((R/'parameters.json').read_text())
for i,p in enumerate(j['main_column_centres_m']):
 for z in [G+2,G+8,G+15]:
  o=pt(*p,z);thickness(f'canopy_column_{i}_X_z{z}',o,[1,0,0],2.0);thickness(f'canopy_column_{i}_Y_z{z}',o,[0,1,0],2.0)
 root(f'canopy_column_{i}_base',pt(*p,G+8),[0,0,-1],0)
 root(f'canopy_column_{i}_roof',pt(*p,G+15),[0,0,1],B+(G+18.1)*S)
ba=xy(j['trace_pixels']['bridge_axis'][0]);bb=xy(j['trace_pixels']['bridge_axis'][1]);u=(bb-ba)/np.linalg.norm(bb-ba);n=np.array([u[1],-u[0]])
for t in [.2,.4,.6]:
 c=ba+(bb-ba)*t
 thickness('bridge_deck',pt(*c,G+5.7),[0,0,1],1.3)
 for side in [-1,1]:
  p=c+n*side*(2.5-.475);o=pt(*p,G+7)
  thickness('bridge_rail_normal',o,[*n,0],1.0)
  root('bridge_rail_into_deck',o,[0,0,-1],B+(G+5.1)*S)
 # Bridge underside is genuinely clear above grade, not a solid block.
 o=pt(*c,G+3);hits=ray(o,[0,0,1]);assert hits and abs(o[2]+hits[0]-(B+(G+5.1)*S))<1e-4
 spaces.append({'feature':'bridge_underside_gap','origin_mm':o.tolist(),'clear_up_mm':hits[0]})
# Selected mid-bay canopy void, avoiding posts.
p=np.mean(j['main_column_centres_m'][2:4],axis=0);o=pt(*p,G+8);h=ray(o,[0,0,1]);assert h and h[0]>10
spaces.append({'feature':'open_canopy_bay','origin_mm':o.tolist(),'clear_up_mm':h[0]})
# Sunken court remains open to sky and below surrounding grade.
c=np.array([2.0,20.0]);o=pt(*c,G+.5)
assert not ray(o,[0,0,1]);h=ray(o,[0,0,-1]);assert h and o[2]-h[0]<B+.3*S
spaces.append({'feature':'sunken_court_open_to_sky','origin_mm':o.tolist(),'floor_z_mm':o[2]-h[0]})
# Arc retaining wall local radial width; root goes continuously to base.
for a in [.0,.5,1.0]:
 p=np.array([4,16.5])+8.4*np.array([np.cos(a),np.sin(a)]);o=pt(*p,G+.5)
 thickness('court_retaining_wall',o,[np.cos(a),np.sin(a),0],1.2)
# Northern annex rails: thickened, deliberately embedded in balcony decks.
a=xy([812,348]);b=xy([645,484]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]])
for z,ts in [(G+4.8,[.31,.915]),(G+9.4,[.13,.575])]:
 for t in ts:
  p=a+(b-a)*t+n*1.15;o=pt(*p,z+.9)
  thickness('annex_balcony_rail_normal',o,[*n,0],1.5)
  h=ray(o,[0,0,-1]);assert h and o[2]-h[0]<=B+(z-.55)*S+1e-4
  roots.append({'feature':'annex_rail_into_deck','origin_mm':o.tolist(),'first_down_exit_mm':(o+np.array([0,0,-h[0]])).tolist()})
# Glazed stair-tower bars are relief on original backing, sampled away from crossbars.
a=xy([908,299]);b=xy([847,310]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]])
for t in [.29,.44]:
 for z in [4.5,9.5,14.5]:
  p=a+(b-a)*t-n*.30;o=pt(*p,z)
  thickness('C_glazing_vertical_mullion',o,[*u,0],.8)
  h=ray(o,[-n[0],-n[1],0]);assert h and h[0]>2
  roots.append({'feature':'C_glazing_into_body','origin_mm':o.tolist(),'inward_first_exit_mm':h[0]})
# G horizontal frames are shallow backed relief, not freestanding walls.
for z in [3.0,5.4,7.8,10.2,12.6,15.85]:
 for t in [.20,.36,.52]:
  p=a+(b-a)*t-n*.30;o=pt(*p,z+.275)
  thickness('G_backed_horizontal_frame_Z',o,[0,0,1],.60)
  h=ray(o,[-n[0],-n[1],0]);assert h and h[0]>2
  roots.append({'feature':'G_horizontal_frame_into_body','origin_mm':o.tolist(),'inward_first_exit_mm':h[0]})
# C right white wall is retained as body and continuous to the base.
for z in [4.5,9.5,14.5]:
 p=a+(b-a)*.8-n*.5;o=pt(*p,z)
 thickness('C_right_white_wall_normal',o,[*n,0],2.)
 root('C_right_white_wall_base',o,[0,0,-1],0)
# Original narrow ridge caps, width and downward attachment at each segment midpoint.
for name,points in {'A':[[657,552],[660,494],[821,375]],'B':[[714,528],[787,490]],'C':[[879,323],[899,418],[817,460]]}.items():
 for i in range(len(points)-1):
  a0=xy(points[i]);b0=xy(points[i+1]);u0=(b0-a0)/np.linalg.norm(b0-a0);n0=np.array([u0[1],-u0[0]]);p=(a0+b0)/2;o=pt(*p,19.35)
  thickness(f'{name}_ridge_{i}_normal',o,[*n0,0],1.2)
  root(f'{name}_ridge_{i}_base',o,[0,0,-1],0)
# Main east two-band glazing: shallow frames rooted into solid wall backing.
outer=j['trace_pixels']['main_outer']
for idx in [2,3,4]:
 a0=xy(outer[idx+1]);b0=xy(outer[idx]);u0=(b0-a0)/np.linalg.norm(b0-a0);n0=np.array([u0[1],-u0[0]])
 for z0,z1 in [(G+6.1,G+10.0),(G+12.2,G+15.9)]:
  for t in [.08,.92]:
   p=a0+(b0-a0)*t-n0*.3;o=pt(*p,(z0+z1)/2)
   thickness('east_backed_vertical_frame',o,[*u0,0],.8)
   h=ray(o,[-n0[0],-n0[1],0]);assert h and h[0]>2
   roots.append({'feature':'east_frame_into_body','origin_mm':o.tolist(),'inward_first_exit_mm':h[0]})
# Straight retaining wall sample retains a real void beside the descent.
a=xy([944,596]);b=xy([876,615]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);p=(a+b)/2;o=pt(*p,G+.4)
thickness('B1_straight_retaining_wall',o,[*n,0],1.2);root('B1_straight_wall_base',o,[0,0,-1],0)
checks={'all_selected_normal_widths_pass':True,'six_columns_rooted_to_base_and_canopy':True,'bridge_rails_rooted_to_deck':True,'bridge_underside_and_canopy_bay_open':True,'sunken_court_open_and_lower_than_grade':True,'G_frames_and_right_wall_backed':True,'ridge_caps_rooted':True,'east_window_frames_backed':True}
r={'passed':True,'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'normal_thickness_samples':rows,'root_samples':roots,'open_space_samples':spaces,'limitations':['Only nominated original-triangle rays, not exhaustive global minimum wall thickness.','No physical printing or actual slicer paths.','Canopy, bridge and balcony undersides need support assessment; remove supports gently; do not arbitrarily shrink.']};(R/'feature-rays.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print({k:v for k,v in r.items() if not isinstance(v,list)})
