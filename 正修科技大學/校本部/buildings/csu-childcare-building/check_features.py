"""Local raw-mesh sections, feature probes, sampled thickness and overhang disclosure."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
def pt(p):return [-p[0],p[1],p[2]]
solid=[[0,0,1],[-80,0,50],[80,0,50],[-10,0,130],[-50,0,128],[110,0,118],[-115,-16,4.5],[72,-38,24],[-121,-15,65]]
air=[[0,36,50],[0,-35,50],[-50,0,135],[-10,0,145],[-115,-10,30],[72,-32,15],[38,0,120],[-43,0,135],[72,-22,12],[86,24,110]]
solid=[pt(p) for p in solid];air=[pt(p) for p in air]
for p in solid:assert m.contains([p])[0],('solid',p)
for p in air:assert not m.contains([p])[0],('air',p)
samples=[]
for label,p,d in [('pv_support',[25,-17,120],[1,0,0]),('pergola_post',[57,-38,13],[1,0,0]),('rear_lattice',[0,-30.1,98],[0,1,0]),('front_rib',[-33,26.5,50],[0,1,0]),('pv_high_edge',[-21,-19,143.5],[0,1,0]),('curved_roof_edge',[-50,-18.6,126],[0,1,0])]:
 p=np.array(pt(p));d=np.array(pt(d));origin=p-d*400;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);cont=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=400<=b];assert cont,(label,dist);samples.append(dict(feature=label,point=p.tolist(),direction=d.tolist(),ray_intersections_mm=dist,containing_solid_width_mm=cont))
sections=[]
for n,o,label in [([0,0,1],[0,0,51],'lower_storey_plan'),([0,0,1],[0,0,109],'added_sixth_setback_plan'),([0,1,0],[0,0,0],'different_roof_levels_longitudinal'),([1,0,0],[-115,0,0],'open_stair_short_end'),([1,0,0],[-50,0,0],'shallow_curved_roof'),([1,0,0],[72,0,0],'open_rear_pergola')]:
 n=pt(n);o=pt(o);sec=m.section(plane_normal=n,plane_origin=o);assert sec is not None;sections.append(dict(label=label,normal=n,origin=o,entities=len(sec.entities),vertices=len(sec.vertices),closed_paths=sum(bool(e.closed) for e in sec.entities)))
down=(m.face_normals[:,2]<-.707)&(m.triangles_center[:,2]>.1)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='正修科技大學幼兒保育館',solid_probes=solid,air_probes=air,local_sections=sections,actual_ray_samples=samples,downward_faces_steeper_than_45deg_above_base_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),not_global_minimum_thickness_certificate=True,pv_grid_relief_nominal_width_mm=.35,pv_grid_is_attached_surface_detail_not_free_standing_member=True,supports_and_color_detail_require_slicer_review=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
