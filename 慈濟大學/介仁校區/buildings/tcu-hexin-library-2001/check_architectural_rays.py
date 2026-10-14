"""Unrepaired actual STL normal and root probes. Local checks, not global minimum-wall certificate."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=False);tri=m.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
def ray(o,d):
 o=np.array(o,float);d=np.array(d,float);p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p);good=np.abs(det)>1e-10;inv=np.zeros(len(tri));inv[good]=1/det[good];s=o-tri[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv;sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(v),6) for v in dist[sel]))
def span(o,axis):
 d=np.eye(3)[axis];a=ray(o,d);b=ray(o,-d);assert a and b;return a[0]+b[0]
def roots(o):return o[2]-ray(o,[0,0,-1])[0],o[2]+ray(o,[0,0,1])[0]
S=150/96
mm=lambda x,y,z:[x*S,-y*S,z*S+2]
checks={};columns=[];air=[];backs=[]
for x,y in [(7,-22.1),(13,-23.1),(20,-23.6),(27,-23.5),(34,-22.8),(40.3,-21.7),(40.3,-13.5),(40.3,-5.4)]:
 o=mm(x,y,2);sx=span(o,0);sy=span(o,1);lo,hi=roots(o);assert min(sx,sy)>2.1093 and abs(lo)<1e-5 and hi>26.9
 columns.append({'origin_mm':o,'normal_x_mm':sx,'normal_y_mm':sy,'down_root_z_mm':lo,'up_root_z_mm':hi})
checks['eight_undercroft_piers_normal_and_base_roof_roots']=True
for label,o in [('north_undercroft',mm(23,-21,2)),('east_road_underpass',mm(39,-10,2))]:
 up=ray(o,[0,0,1]);down=ray(o,[0,0,-1]);assert abs(up[0]-3.125)<1e-4 and abs(down[0]-3.125)<1e-4
 air.append({'feature':label,'point_mm':o,'up_to_cantilever_mm':up[0],'down_to_base_mm':down[0]})
# Actual east road longitudinal clear path passes between piers and core.
o=mm(38.3,-16,2);north=ray(o,[0,1,0]);south=ray(o,[0,-1,0]);assert not north and south[0]>15
checks['north_and_east_undercrofts_are_true_air']=True
for z in [2,7]:
 o=mm(5,34,z);a=ray(o,[-1,0,0]);assert abs(a[0]-7.5*S)<1e-4
 air.append({'feature':'E_portal_depth_to_recessed_back','origin_mm':o,'inward_hits_mm':a})
o=mm(0,34,7);up=ray(o,[0,0,1]);assert abs(up[0]-1.9*S)<1e-4
checks['E_portal_two_storey_clear_recess_preserved']=True
for x,y,z in [(-8,9,6),(-20,37,5),(-20,37,11),(-20,20,12),(-20,53,12)]:
 o=mm(x,y,z);lo,hi=roots(o);assert abs(lo)<1e-5 and hi>20
 backs.append({'feature':'D_link_or_FG_low_roof_solid_root','origin_mm':o,'bottom_z_mm':lo,'top_z_mm':hi})
checks['D_and_FG_lower_roof_are_continuous_to_base']=True
# All selected original exposed face normals, from actual geometry rather than parameters.
norm=np.cross(e1,e2);norm/=np.linalg.norm(norm,axis=1)[:,None];centres=tri.mean(axis=1);skin=[];cap=[]
for i,(c,n) in enumerate(zip(centres,norm)):
 x,y,z=c[0]/S,-c[1]/S,(c[2]-2)/S
 kind=None
 if 4.01<z<15.8 and y< -22 and n[1]>.8:kind='north_glass_backed_front'
 if 4.01<z<15.8 and x>41.7 and n[0]>.8:kind='east_glass_backed_front'
 if 0.6<z<12.6 and 2.7<x<3.2 and 14.5<y<60.5 and n[0]>.99:kind='E_backed_window_frames_and_recesses'
 if 8<z<12.6 and 4.4<y<5.2 and -3<x<42 and n[1]<-.99:kind='B_backed_ribbon_frames_and_recesses'
 if kind:
  a=ray(c-n*1e-4,-n);assert a and a[0]+1e-4>.8,(kind,i,c,a)
  skin.append({'feature':kind,'face':i,'centroid_mm':c.tolist(),'inward_normal':(-n).tolist(),'solid_normal_mm':a[0]+1e-4})
 if n[2]<-.99 and abs(z-4)<1e-4:
  a=ray(c-n*1e-4,-n);assert a and a[0]>.8
  cap.append({'face':i,'centroid_mm':c.tolist(),'upward_thickness_mm':a[0]+1e-4})
assert len(skin)>100 and cap
checks['all_selected_actual_front_skin_normals_have_solid_backing']=True
checks['actual_undercroft_ceiling_faces_have_solid_roof_above']=True
loss=json.loads((R/'feature-loss-locations.json').read_text());warn=[]
for r in loss['high_loss_components']:
 x1,y1,x2,y2=r['bounds'];o=[(x1+x2)/2,(y1+y2)/2,r['z_mm']];sx=span(o,0);sy=span(o,1);lo,hi=roots(o)
 assert min(sx,sy)>2.1093 and abs(lo)<1e-5 and hi>26.9 and abs(r['bbox_area_mm2']-r['original_area_mm2'])<1e-8 and r['loss_outside_bbox_corners_0p41_mm2']<1e-10
 warn.append({'origin_mm':o,'actual_x_width_mm':sx,'actual_y_width_mm':sy,'down_root_z_mm':lo,'up_root_z_mm':hi,'loss_fraction':r['opening_loss_fraction'],'outside_true_rectangle_corners_0p41_mm2':r['loss_outside_bbox_corners_0p41_mm2']})
checks['248_samples_are_eight_rectangular_rooted_piers_corner_only']=len(warn)==248
report={'passed':all(checks.values()),'checks':checks,'columns':columns,'air':air,'D_FG_roots':backs,'original_face_skins':skin,'original_ceiling_faces':cap,'high_loss_samples':warn,'minimum_selected_original_skin_normal_mm':min(x['solid_normal_mm'] for x in skin),'minimum_original_ceiling_thickness_mm':min(x['upward_thickness_mm'] for x in cap),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'limitations':'Selected original face-normal and root checks only; not exhaustive minimum wall, not slicer or physical print test. Decorative shallow frame edge width may be below nozzle width; frames are fused to full backing.'}
(R/'architectural-ray-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['columns','air','D_FG_roots','original_face_skins','original_ceiling_faces','high_loss_samples']})
