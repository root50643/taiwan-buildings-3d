"""NTUNHS Erya: local checks on raw STL, not parametric claims alone."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
# Points in pre-reflection design axes, mapped into delivered coordinates.
def pt(p):return np.array([-p[0],p[1],p[2]])
solid=[[0,0,1.5],[-30,0,100],[48,-25,100],[-8,-18,182],[24,1,153],[4,27,169],[44,-44.5,4]]
air=[[24,30,100],[48,20,100],[4,27,174],[24,1,160],[0,65,20]]
assert all(m.contains([pt(p)])[0] for p in solid)
assert all(not m.contains([pt(p)])[0] for p in air)
samples=[]
for label,p,d in [('rear_window_closed_envelope',[-54,-41.15,41],[0,1,0]),('PV_panel',[-8,-17,188.5],[0,0,1]),('roof_screen_post',[59.7,-25,183],[1,0,0]),('roof_parapet',[-52.5,20,179],[1,0,0]),('rear_upper_white_frame',[32.7,-45.8,24],[1,0,0]),('rear_ground_entrance_mullion',[44,-45.4,8],[1,0,0]),('front_stair_rail_post',[-55.2,59,5],[1,0,0]),('front_window_parapet',[-55.7,43.1,36.6],[0,1,0])]:
 p=pt(p);d=pt(d);origin=p-d*400;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);cont=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=400<=b];assert cont,(label,dist);samples.append(dict(feature=label,point=p.tolist(),direction=d.tolist(),ray_intersections_mm=dist,containing_solid_width_mm=cont))
sections=[]
for n,o,label in [([0,0,1],[0,0,100],'stepped_midheight_footprint'),([0,0,1],[0,0,20],'diagonal_two_floor_skirt'),([0,1,0],[0,27,0],'roof_open_notch'),([1,0,0],[-24,0,0],'lower_middle_roof'),([0,0,1],[0,0,182],'raised_equipment_and_screen')]:
 sec=m.section(plane_normal=n,plane_origin=o);assert sec is not None;sections.append(dict(label=label,normal=n,origin=o,entities=len(sec.entities),vertices=len(sec.vertices),closed_paths=sum(bool(e.closed) for e in sec.entities)))
down=m.face_normals[:,2]<-.707
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='爾雅樓（第三學生宿舍）',solid_probes=[pt(p).tolist() for p in solid],air_probes=[pt(p).tolist() for p in air],local_sections=sections,actual_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),not_global_minimum_thickness_certificate=True,windows_stairs_roof_edges_require_support_assessment=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
