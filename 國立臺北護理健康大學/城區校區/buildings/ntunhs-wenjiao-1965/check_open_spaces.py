"""Explicit bounded segment/ray tests of actual STL air spaces; no repair.
The selected probes do not claim a complete interior reconstruction.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',force='mesh',process=True);T=m.triangles

def hits(a,b):
 a=np.array(a,float);b=np.array(b,float);v=b-a;length=np.linalg.norm(v);d=v/length
 e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0];h=np.cross(np.tile(d,(len(T),1)),e2);det=np.einsum('ij,ij->i',e1,h)
 usable=np.abs(det)>1e-10;f=np.zeros_like(det);f[usable]=1/det[usable];s=a-T[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);w=f*np.einsum('j,ij->i',d,q);t=f*np.einsum('ij,ij->i',e2,q)
 good=usable&(u>=-1e-9)&(w>=-1e-9)&(u+w<=1+1e-9)&(t>1e-6)&(t<length-1e-6)
 return sorted(set(round(float(i),6) for i in t[good]))
tests=[]
def check(name,a,b,open):
 out=hits(a,b);ok=(len(out)==0)==open;tests.append({'name':name,'a_mm':a,'b_mm':b,'expected_clear':open,'intersection_distances_mm':out,'passed':ok});assert ok,(name,out)
for x in [-55,-30,-10,0,10,20,55]:check('1965 ground colonnade '+str(x),[x,-30,5.5],[x,30,5.5],True)
for z in [16,24.7,33.4]:
 check('north corridor long open strip '+str(z),[-44,17.3,z],[44,17.3,z],True)
 check('north corridor opening '+str(z),[0,30,z],[0,15.4,z],True)
 check('wall behind north corridor '+str(z),[0,30,z],[0,10,z],False)
check('air below exterior folding-stair landing',[35.3,21,4.2],[42,21,4.2],True)
check('air below north-projecting flight',[37,27,3.0],[47,27,3.0],True)
check('actual step mass of north-projecting flight',[41.1,27,15],[41.1,27,2.5],False)
check('roof remains solid, no invented inner courtyard',[0,0,50],[0,0,30],False)
check('original ground service core retained',[39.5,-28,6],[39.5,-12,6],False)
measurements=[]
for floor,zc in [(2,16),(3,24.7),(4,33.4)]:
 d=hits([3.9,30,zc],[3.9,0,zc]);back=30-d[0]
 up=hits([0,17.3,zc],[0,17.3,50]);down=hits([0,17.3,zc],[0,17.3,0])
 rail=hits([0,20.1,zc],[0,20.1,0]);ceiling=zc+up[0];floor_z=zc-down[0];rail_z=zc-rail[0]
 row={'storey':floor,'front_plane_y_mm':21.0,'back_wall_y_mm':back,'front_to_back_wall_mm':21-back,'inner_rail_y_mm':19.4,'rail_to_back_wall_clear_depth_mm':19.4-back,'floor_z_mm':floor_z,'soffit_z_mm':ceiling,'floor_to_soffit_clear_height_mm':ceiling-floor_z,'rail_top_z_mm':rail_z,'above_rail_clear_height_mm':ceiling-rail_z}
 assert row['front_to_back_wall_mm']>6.5 and row['rail_to_back_wall_clear_depth_mm']>4.9 and row['above_rail_clear_height_mm']>4.5
 measurements.append(row)
u=hits([0,0,6],[0,0,50]);d=hits([0,0,6],[0,0,0]);ground={'base_top_z_mm':6-d[0],'soffit_z_mm':6+u[0],'clear_height_mm':u[0]+d[0]};assert ground['clear_height_mm']>7.4
report={'passed':True,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore finite-segment intersections against original delivered STL triangles; no mesh repair.','checks':{'ground_colonnade_preserved':True,'three_upper_north_corridor_air_strips_preserved':True,'exterior_stair_under_space_preserved':True,'stair_and_original_service_core_are_present':True,'main_flat_roof_without_invented_courtyard':True},'tests':tests,'north_corridor_measured_clearances':measurements,'ground_colonnade_measured_clearance':ground}
(R/'open-space-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print({'passed':True,'tests':len(tests)})
