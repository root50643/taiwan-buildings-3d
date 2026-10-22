"""Local raw-mesh sections, material-local thin features and overhang disclosure."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
def pt(p):return [-p[0],p[1],p[2]]
solid=[[0,0,1],[-80,0,50],[80,0,50],[0,0,110],[-50,0,108],[50,0,107],[-23,37,5],[-23,31.5,11.3]]
air=[[0,0,117],[-50,40,55],[50,40,55],[0,40,95],[0,-42,50],[125,0,50],[-23,31.8,18]]
solid=[pt(p) for p in solid];air=[pt(p) for p in air]
assert all(m.contains([p])[0] for p in solid);assert all(not m.contains([p])[0] for p in air)
samples=[]
for label,p,d in [('orange_fin',[13.3,33.4,52],[1,0,0]),('end_glazing_mullion',[121,-25,48],[0,1,0]),('roof_eave',[-60,34.6,102],[0,0,1]),('street_window_frame',[19,30.1,16.2],[1,0,0]),('entry_side_wall',[-33.3,38,8.15],[1,0,0])]:
 p=np.array(pt(p));d=np.array(pt(d));origin=p-d*400;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);cont=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=400<=b];assert cont,(label,dist);samples.append(dict(feature=label,point=p.tolist(),direction=d.tolist(),ray_intersections_mm=dist,containing_solid_width_mm=cont))
sections=[]
for n,o,label in [([0,0,1],[0,0,52],'five_floor_main_plan'),([0,1,0],[0,0,0],'longitudinal_three_roof_heights'),([1,0,0],[0,0,0],'central_high_cap'),([1,0,0],[-50,0,0],'left_long_gabled_roof'),([1,0,0],[50,0,0],'right_lower_gabled_roof')]:
 n=pt(n);o=pt(o);sec=m.section(plane_normal=n,plane_origin=o);assert sec is not None;sections.append(dict(label=label,normal=n,origin=o,entities=len(sec.entities),vertices=len(sec.vertices),closed_paths=sum(bool(e.closed) for e in sec.entities)))
down=m.face_normals[:,2]<-.707
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='綜合大樓（共同教室大樓）',solid_probes=solid,air_probes=air,local_sections=sections,actual_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),not_global_minimum_thickness_certificate=True,eaves_fins_steps_require_support_assessment=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
