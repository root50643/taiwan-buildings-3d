"""NUK humanities A/B: raw mesh spatial, local thickness and support probes."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
def p(x,y,z):return [x-111,y-10,z]
air=[p(65,40,z) for z in [5,15,30,40]]+[p(170,-55,z) for z in [5,15,25,40]]+[p(70,-10,7),p(138,-55,7),p(70,-5,12),p(142,-55,11),p(33,120,2.5),p(33,120,8)]
solid=[p(10,50,10),p(130,50,18),p(70,100,26),p(210,-55,10),p(180,-10,12),p(180,-100,12),p(143,-8,8),p(70,-5,21.8),p(142,-55,13.8),p(33,120,1.3),p(127,130,16)]
assert all(not m.contains([q])[0] for q in air)
assert all(m.contains([q])[0] for q in solid)
samples=[]
for label,q,d in [('A_front_column',p(0,-10,15),[1,0,0]),('A_rear_fin',p(50.5,117,20),[1,0,0]),('A_high_roof_fascia',p(0,50,33.8),[1,0,0]),('A_inner_gallery_parapet',p(29,40,12.8),[1,0,0]),('B_court_column',p(194,-70,10),[1,0,0])]:
 q=np.array(q);d=np.array(d);o=q-d*400;loc,_,_=m.ray.intersects_location([o],[d],multiple_hits=True);dist=sorted(float(np.dot(t-o,d)) for t in loc);pairs=[(a,b) for a,b in zip(dist[::2],dist[1::2]) if a<=400<=b];assert pairs,label
 samples.append(dict(feature=label,center=q.tolist(),direction=d.tolist(),containing_thickness_mm=[b-a for a,b in pairs],ray_hits_mm=dist))
platforms=[]
for label,x,y,z in [('A_left',6,45,28.2),('A_right',134,45,28.2),('A_back',48,104,28.2),('B_top',166,-5,20.2),('B_back',219,-46,20.2),('B_bottom',166,-104,20.2)]:
 q=p(x,y,50);loc,_,_=m.ray.intersects_location([q],[[0,0,-1]],multiple_hits=True);zs=sorted([float(t[2]) for t in loc],reverse=True);assert abs(zs[0]-(z+.05))<.01,(label,zs);platforms.append(dict(label=label,highest_surface_z=zs[0],expected_platform_z=z+.05))
# Actual revised sloped lecture roof must rise outwards, not merely be declared.
lecture_roof=[]
for yy in [112,122,134]:
 loc,_,_=m.ray.intersects_location([p(127,yy,50)],[[0,0,-1]],multiple_hits=True);lecture_roof.append(max(float(q[2]) for q in loc))
assert lecture_roof[0]<lecture_roof[1]<lecture_roof[2]
sections=[]
for normal,origin,label in [([1,0,0],p(65,0,0),'A_court_open_section'),([0,1,0],p(0,-55,0),'B_court_open_section'),([0,0,1],[0,0,15],'two_courtyards_and_corner_connection')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None;sections.append(dict(label=label,vertices=len(sec.vertices),entities=len(sec.entities)))
down=m.face_normals[:,2]<-.707
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='國立高雄大學人文社會科學院 A/B 主樓',air_probes=air,solid_probes=solid,local_sections=sections,actual_mesh_ray_samples=samples,six_roof_platform_probes=platforms,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_area_mm2=float(m.area_faces[down].sum()),revised_lecture_roof_z_samples=lecture_roof,parking_ramp_not_stairs=True,single_high_A_and_low_B_canopies=True,supports_required=True,not_global_minimum_thickness_certificate=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
