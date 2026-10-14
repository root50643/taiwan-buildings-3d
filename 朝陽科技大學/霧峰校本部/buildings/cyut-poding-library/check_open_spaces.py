"""Ray checks on original STL, no repair: courtyard and actual recessed portal."""
from pathlib import Path
import json
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False)
def ray(o,d):
 o=np.array(o,dtype=float);d=np.array(d,dtype=float); t=m.triangles
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(np.tile(d,(len(t),1)),e2);det=np.einsum('ij,ij->i',e1,p)
 good=np.abs(det)>1e-10;inv=np.zeros(len(t));inv[good]=1/det[good];s=o-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(v),5) for v in dist[sel]))
tests={};data={}
S=150/166; Z=S*1.12
# Probe the narrow, backed decorative elements against the raw triangles.
for label,x,z in [('main_window_mullion',-33,30),('main_transom',-32.2,32.9),('tower_glazing_mullion',4,26),('arch_left_foot',-48,4),('door_jamb',-39,5),('front_band_pier',19,45)]:
 o=(x*S,(-25 if label in ['arch_left_foot','door_jamb'] else -60)*S,z*Z); hits=ray(o,(0,1,0)); positions=[o[1]+t for t in hits]
 tests[label+'_root_contiguous_to_main_mass']=len(positions)==2 and positions[1]-positions[0]>8*S
 data[label]={'origin_mm':o,'intersection_y_mm':positions,'solid_interval_count':len(positions)//2}
# Deep portico must be empty before the recessed arched entrance wall.
o=(-36.5*S,-60*S,15*Z);hits=ray(o,(0,1,0)); y=o[1]+hits[0]
tests['entry_portico_is_recessed']=y>-23*S
data['entry_portico']={'first_y_mm':y,'expected_wall_y_about_mm':-22*S}
# The south upper-floor notch stays genuinely recessed.
o=(-54*S,-60*S,40*Z);hits=ray(o,(0,1,0));y=o[1]+hits[0]
tests['south_upper_notch_recessed']=y>-9*S
data['south_notch']={'first_y_mm':y}
# The glazed roof footprint remains solid capped, never an invented open well.
for label,x,y in [('south_glass',-24,0),('north_glass',7,0)]:
 o=(x*S,y*S,90);hits=ray(o,(0,0,-1));height=o[2]-hits[0]
 tests[label+'_solid_roof_cover']=height>47*Z
 data[label]={'first_hit_z_mm':height}
# Measure actual band gaps and front-to-back rooting, not parameter-only checks.
for label,zlo,zhi,clo,chi in [('upper',44.7,46.2,43.8,47),('middle',25.45,27.15,24.6,28)]:
 x=17.75*S
 origin=(x,-21.85*S,0);inner=ray(origin,(0,0,1))
 origin2=(x,-23.0*S,0);cornice=ray(origin2,(0,0,1))
 def near(vals,target):
  q=min(vals,key=lambda q:abs(q-target));assert abs(q-target)<1e-4;return q
 lo=near(inner,zlo*Z);hi=near(inner,zhi*Z)
 lower_top=near(cornice,clo*Z);upper_bottom=near(cornice,chi*Z)
 gaps=[lo-lower_top,upper_bottom-hi]
 tests[label+'_actual_STL_vertical_lands_at_least_0_8mm']=min(gaps)>=.8
 data[label+'_lands']={'window_bottom_top_mm':[lo,hi],'cornice_edge_mm':[lower_top,upper_bottom],'solid_lands_mm':gaps}
# First mullion starts at x16.0 before the second at x18.5; thin relief is wall-backed.
o=(15.2*S,-21.90*S,45*Z);hits=ray(o,(1,0,0));xs=[o[0]+v for v in hits]
width=xs[1]-xs[0]
tests['actual_glazing_mullion_width_at_least_0_8mm']=width>=.8
data['glazing_mullion_width']={'intersection_x_mm':xs,'first_width_mm':width}
report={'passed':all(tests.values()),'checks':tests,'rays':data,'method':'Original binary STL triangles with no repair; Moller-Trumbore rays test backed fine-detail roots, deep portico, setback and closed glass roof. Not exhaustive wall thickness.'}
(R/'open-space-check.json').write_text(json.dumps(report,indent=2));print(report);assert report['passed']
