"""法鼓文理學院金山校本部大願橋: finite-volume air/solid, local cuts and thickness."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md,math
A=Path(__file__).parent;m=trimesh.load(A/'model.stl',process=False);v,inv=np.unique(m.vertices,axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv[m.faces],process=False);raw=md.Manifold(md.Mesh(np.array(m.vertices,dtype=np.float32),np.array(m.faces,dtype=np.uint32)))
def y(x):return -7+9.5*math.sin(math.pi*(x+135)/270)+1.6*math.sin(2*math.pi*(x+135)/270)
def z(x):return 14+2.1*math.sin(math.pi*(x+135)/270)
probes=[]
for label,c,s,air in [('end_bore_west',[-128.5,y(-128.5)-1,z(-128.5)+3.65],[2,8,2],True),('end_bore_east',[128.5,y(128.5)-1,z(128.5)+3.65],[2,8,2],True),('no_central_pier',[0,3,8],[20,15,8],True),('open_walking_surface',[0,10,20],[10,6,3],True),('solid_high_box',[0,.5,22],[1,.5,1],False),('solid_deck',[0,10,15.5],[1,1,.3],False)]:
 q=md.Manifold.cube(s,True).translate(c);vol=(raw^q).volume();full=q.volume();assert vol<1e-6 if air else vol>full*.99,(label,vol,full);probes.append(dict(feature=label,center=c,size=s,intersection_mm3=vol,box_mm3=full,expected='air' if air else 'solid'))
sections=[]
for normal,origin,label in [([1,0,0],[0,0,0],'midspan_width'),([1,0,0],[-128.5,0,0],'west_bore_plane'),([1,0,0],[105,0,0],'east_bank_support'),([0,0,1],[0,0,16],'deck_and_bores_horizontal')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None;sections.append(dict(label=label,normal=normal,origin=origin,closed_paths=int(sum(bool(e.closed) for e in sec.entities)),entities=len(sec.entities),vertices=len(sec.vertices)))
samples=[]
xx=134/90; yy=y(xx)+8.4+6.6*math.sin(math.pi*(xx+135)/270)**.8+.12+(.58-.12)*(2.4-1.15)/(3.6-1.15)
for label,p,d in [('high_box_normal',[0,.5,22],[0,1,.17]),('fine_rail_normal',[xx,yy,z(xx)+2.4],[1,0,0]),('deck',[0,10,15.5],[0,0,1]),('display_base',[0,3,.8],[0,0,1])]:
 p=np.array(p);d=np.array(d,dtype=float);d/=np.linalg.norm(d);origin=p-d*200;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);samples.append(dict(feature=label,probe_center=p.tolist(),direction=d.tolist(),ray_hit_distances_mm=dist,probe_containing_intervals_mm=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=200<=b]))
down=m.face_normals[:,2]<-.707
r=dict(name='法鼓文理學院金山校本部大願橋',stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),finite_volume_probes=probes,local_sections=sections,actual_mesh_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),nominal_fine_rail_diameter_mm=.34,nominal_soffit_diagonal_diameter_mm=.4,not_global_minimum_thickness_certificate=True,thin_members_below_0_8mm=True,supports_likely_for_long_span_rails_tubes_and_leaning_wall=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
