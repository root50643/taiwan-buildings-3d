"""Independent spatial Boolean checks against the retained pre-revision STL.
Run with numpy, trimesh, manifold3d. Uses actual delivered meshes, not renderer.
Coordinates are model axes, not geographic directions. No FFF validation.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from manifold3d import Manifold,Mesh64
A=Path(__file__).resolve().parents[1];P=A.parent
old_path=P/'model.stl';new_path=A/'model-v2.stl';assert hashlib.sha256(old_path.read_bytes()).hexdigest()=='e4f25a2d8c02e58a57a263ee7ac93289e8818c456be86c251a1a26f9e0337e8e'
def solid(path):
 m=trimesh.load(path,force='mesh',process=True);s=Manifold(Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)));assert str(s.status())=='Error.NoError';return m,s
def box(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def difference_volume(a,b):return abs((a-b).volume())+abs((b-a).volume())
om,old=solid(old_path);nm,new=solid(new_path);cube=box(-45,45,-45,45,2.8,98)
checks={};values={}
def test(name,a,b,tol=1e-5):
 v=difference_volume(a,b);values[name+'_symmetric_difference_mm3']=v;checks[name]=v<tol
old_stair_crop=box(43,60,-39,39,19,84)
new_stair_crop=box(-60,-43,-39,39,19,84)
test('whole_stair_and_doors_rotated_180_in_actual_mesh',(old^old_stair_crop).rotate((0,0,180)),new^new_stair_crop)
old_balcony_crop=box(-1,13,43,52,10,84);new_balcony_crop=box(43,52,-1,13,10,84)
test('both_balconies_and_doors_mapped_to_adjacent_x_positive_face',(old^old_balcony_crop).transform(np.array([[0,1,0,0],[1,0,0,0],[0,0,1,0]],dtype=float)),new^new_balcony_crop)
test('former_rear_balcony_and_door_sites_restored_to_plain_original_cube',new^old_balcony_crop,cube^old_balcony_crop)
for name,region in [('former_low_stair_door_closed',box(43,60,-39,-29,19,32)),('former_high_stair_door_closed',box(43,60,29,39,60,81))]:test(name,new^region,cube^region)
allowed=old_stair_crop+new_stair_crop+old_balcony_crop+new_balcony_crop
delta=(old-new)+(new-old);values['total_added_volume_mm3']=(new-old).volume();values['total_removed_volume_mm3']=(old-new).volume();values['difference_outside_declared_regions_mm3']=(delta-allowed).volume();checks['changes_bounded_to_stair_balcony_and_door_regions']=values['difference_outside_declared_regions_mm3']<1e-5
for name,region in [('front_projecting_box_unchanged',box(-40,40,-65,-45.0001,15,99)),('roof_unchanged',box(-46,46,-46,46,94.5,99)),('display_base_unchanged',box(-76,76,-72,72,-1,3))]:test(name,old^region,new^region)
checks['dimensions_unchanged']=bool(np.array_equal(nm.extents,om.extents));checks['base_contact_unchanged']=checks['display_base_unchanged'];checks['same_volume_within_1e_4_mm3']=abs(old.volume()-new.volume())<1e-4
rows={'model_axes_not_geographic':True,'front_projecting_box_wall':'y=-45 (unchanged)','left_stair_wall':'x=-45 (was x=+45)','stair_low_door_base_center_mm':[-45,34,20],'stair_high_door_base_center_mm':[-45,-34,61],'stair_ascent':'from rear y>0 to front y<0','right_two_balconies_wall':'x=+45 (was y=+45)','balcony_slab_base_centers_xyz_mm':[[47,6,12],[47,6,70]],'rear_y_positive_wall':'now plain neutral approximate surface; no new unseen detail','retained_estimates':'Nominal z heights, stair span/tread count/rail thickness and +6mm balcony along-wall offset retain legacy estimates; this is not a full resurvey.'}
report={'passed':all(checks.values()),'baseline_commit':'794cf7db91f422e88ac9eec6c5bb06f4e2a7c79c','baseline_STL_sha256':hashlib.sha256(old_path.read_bytes()).hexdigest(),'revised_STL_sha256':hashlib.sha256(new_path.read_bytes()).hexdigest(),'checks':checks,'measurements':values,'coordinate_registration':rows,'mesh_unit':'millimeter','geometry_comparison_tolerance_mm3':1e-5,'historical_QA_modified':False,'FFF_sliced':False,'physical_print':False}
(A/'qa/layout-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
