"""Source bounded mesh probes: 建國科技大學綠崗亭, not an all-feature certificate."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
A=Path(__file__).parent
# Exact welding only, no process repair.
import struct
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
def occupied(p):return bool(m.contains([p])[0])
air=[[0,-43,25.7],[0,43,25.7],[-35,-3,79],[35,-3,79],[0,0,30],[0,0,85],[-35,27,62],[-47,28,58]]
solid=[[-35,-27,80],[35,27,65],[0,0,55],[35,35,80],[-35,-35,30]]
assert all(not occupied(p) for p in air),[(p,occupied(p)) for p in air]
assert all(occupied(p) for p in solid),[(p,occupied(p)) for p in solid]
samples=[]
for label,p,d in [('upper_curved_baluster',[0,-35,64],[0,1,0]),('continuous_column',[35,35,80],[1,0,0]),('upper_floor',[0,0,55],[0,0,1]),('upper_moon_panel',[-35,-26,80],[1,0,0]),('lower_gray_cap',[48,0,17],[1,0,0]),('external_stair_tread',[-43,-35,8],[1,0,0])]:
 p=np.array(p);d=np.array(d);origin=p-d*200;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);samples.append(dict(feature=label,probe_center=p.tolist(),direction=d.tolist(),ray_hit_distances_mm=dist,local_intervals_mm=[b-a for a,b in zip(dist[::2],dist[1::2])],probe_containing_intervals_mm=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=200<=b]))
sections=[]
for normal,origin,label in [([1,0,0],[-35,0,0],'upper_moon_face'),([0,1,0],[0,-43,0],'lower_moon_face_90_degrees'),([1,0,0],[-43,0,0],'external_stair_plane'),([0,1,0],[0,27,0],'landing_side_opening')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None
 sections.append(dict(label=label,normal=normal,origin=origin,closed_paths=int(sum(bool(e.closed) for e in sec.entities)),entities=len(sec.entities),vertices=len(sec.vertices)))
colors=np.array(json.loads((A/'mesh.json').read_text())['face_materials']);centers=m.triangles_center
notch_red=(colors==4)&(centers[:,2]<60)&(centers[:,0]<-31.50001)&(centers[:,1]>16.00001)
assert not notch_red.any(), 'Red roof/tile faces must not float inside stair notch'
down=m.face_normals[:,2]<-.707
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='建國科技大學綠崗亭',red_roof_or_tile_faces_inside_stair_notch=0,empty_air_probes=air,solid_probes=solid,local_sections=sections,actual_mesh_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),nominal_minimum_members_mm=.9,not_global_minimum_thickness_certificate=True,supports_likely_for_floor_eaves_roof_moon_openings_and_stair=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
