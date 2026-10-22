"""HCU Hsuan Fo Hall: bounded actual raw mesh probes, not thickness certification."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,struct
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
def occupied(p):return bool(m.contains([p])[0])
air=[[0,0,25],[29,-40,22],[29,40,22],[0,52,25],[0,-49,28],[94,0,25],[-95,0,25]]
solid=[[60,-39,25],[-84,0,25],[0,0,56],[0,35,49.8],[0,40.3,23],[85,3,22]]
assert all(not occupied(p) for p in air),[(p,occupied(p)) for p in air]
assert all(occupied(p) for p in solid),[(p,occupied(p)) for p in solid]
samples=[]
for label,p,d in [('glass_sheet',[85,6,22],[1,0,0]),('gray_wall',[60,-39,25],[0,1,0]),('north_cabinet',[-50,40.3,23],[0,1,0]),('canopy_outer_grid',[100,-44,40],[0,0,1]),('roof_slope',[0,25,51.5],[0,0,1]),('ramp_rail_post',[-65,-52.5,11],[1,0,0])]:
 p=np.array(p);d=np.array(d);origin=p-d*300;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);cont=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=300<=b];assert cont,(label,dist);samples.append(dict(feature=label,probe_center=p.tolist(),direction=d.tolist(),ray_hit_distances_mm=dist,probe_containing_intervals_mm=cont))
sections=[]
for normal,origin,label in [([1,0,0],[0,0,0],'transverse_two_slope_roof_and_canopies'),([0,1,0],[0,0,0],'longitudinal_hollow_hall'),([1,0,0],[29,0,0],'aligned_part_open_north_south_entries'),([0,1,0],[0,40.3,0],'north_flat_cabinet_interface')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None
 sections.append(dict(label=label,normal=normal,origin=origin,closed_paths=int(sum(bool(e.closed) for e in sec.entities)),entities=len(sec.entities),vertices=len(sec.vertices)))
down=m.face_normals[:,2]<-.707
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='玄奘大學慈恩精舍選佛場',empty_air_probes=air,solid_probes=solid,local_sections=sections,actual_mesh_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),nominal_minimum_glass_sheet_mm=.9,not_global_minimum_thickness_certificate=True,canopies_and_main_roof_require_support_assessment=True,shared_north_corridor_cut_boundary_not_real_free_cantilever=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
