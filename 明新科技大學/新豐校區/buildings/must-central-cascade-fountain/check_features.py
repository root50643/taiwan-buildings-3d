"""Actual raw mesh radial, air and local ray probes; not physical print certification."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
air=[[50,0,5],[70,0,8],[82,0,8],[37,0,8],[33,0,11],[29,0,15],[0,0,18],[95,0,3]]
solid=[[0,0,1],[50,0,2],[87,0,8],[95,0,1],[38,0,5],[34,0,8],[30,0,11],[26,0,15]]
assert not m.contains(air).any();assert m.contains(solid).all()
samples=[]
for label,p,d in [('display_closure_not_pool_floor',[50,0,2],[0,0,1]),('narrow_paving',[95,0,1],[0,0,1]),('outer_rim',[87,0,8],[1,0,0]),('top_tier',[0,0,15],[1,0,0])]:
 p=np.array(p);d=np.array(d);origin=p-d*300;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);cont=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=300<=b];assert cont;samples.append(dict(feature=label,probe_center=p.tolist(),direction=d.tolist(),ray_hit_distances_mm=dist,probe_containing_intervals_mm=cont))
sections=[]
for normal,origin,label in [([1,0,0],[0,0,0],'diametral_four_steps_and_hollow_annular_basin'),([0,1,0],[0,0,0],'orthogonal_four_steps'),([0,0,1],[0,0,8],'tier_and_separate_outer_ring'),([0,0,1],[0,0,15],'upper_tall_tier')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None;sections.append(dict(label=label,normal=normal,origin=origin,closed_paths=int(sum(bool(e.closed) for e in sec.entities)),entities=len(sec.entities),vertices=len(sec.vertices)))
down=m.face_normals[:,2]<-.707;above=down & (m.triangles_center[:,2]>.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='明新科技大學中正堂、鴻超樓前噴水池',empty_air_probes=air,solid_probes=solid,local_sections=sections,actual_mesh_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),downward_faces_above_base_count=int(above.sum()),downward_faces_above_base_area_mm2=float(m.area_faces[above].sum()),nominal_narrow_paving_thickness_mm=1.6,nominal_display_closure_thickness_mm=3.5,nominal_rim_radial_width_mm=7,not_global_minimum_thickness_certificate=True,no_overhang_above_base_detected_by_45deg_face_test=not above.any(),physical_print_tested=False,support_free_certified=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
