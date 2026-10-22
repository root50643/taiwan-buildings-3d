"""Source-bounded geometric checks: 國立東華大學壽豐校區景觀橋."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
A=Path(__file__).parent;m=trimesh.load(A/'model.stl',process=True);raw=md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def occupied(p):return bool(m.contains([p])[0])
# Air checks are interior sample probes, not a proof of every opening.
air=[[0,29,20],[0,-29,20],[0,0,15],[73,29,45],[-73,29,45],[73,-29,45],[-73,-29,45]]
assert all(not occupied(p) for p in air)
assert occupied([0,0,24]) and not occupied([0,0,31])
assert occupied([0,29,32]) and occupied([0,-29,32])
assert occupied([50,29,27]) and not occupied([50,29,32])
# Thickness measured on actual raw mesh by opposite ray intersections at known features.
samples=[]
for label,p,d in [('rail_baluster',[1,-35.6,35],[0,1,0]),('column_frame',[63.35,-38.65,40],[1,0,0]),('base',[0,0,1],[0,0,1]),('road_slab',[0,5,23.8],[0,0,1])]:
 p=np.array(p);d=np.array(d);origin=p-d*200;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);samples.append(dict(feature=label,probe_center=p.tolist(),direction=d.tolist(),ray_hit_distances_mm=dist,local_intervals_mm=[b-a for a,b in zip(dist[::2],dist[1::2])],probe_containing_intervals_mm=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=200<=b]))
# Vertical local cross-sections in two bridge-width planes and long-side plane.
sections=[]
for normal,origin,label in [([1,0,0],[0,0,0],'midspan_width'),([1,0,0],[73,0,0],'four_post_end_plane'),([0,1,0],[0,-31,0],'outer_arch_long_side')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None
 sections.append(dict(label=label,normal=normal,origin=origin,closed_paths=int(sum(bool(e.closed) for e in sec.entities)),entities=len(sec.entities),vertices=len(sec.vertices)))
down=m.face_normals[:,2]<-.707
r=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='國立東華大學壽豐校區景觀橋',air_probes_empty=air,central_flat_and_two_arched_deck_probes_pass=True,local_sections=sections,actual_mesh_ray_samples=samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),nominal_minimum_members_mm=.85,roof_lattice_mm=.9,not_global_minimum_thickness_certificate=True,supports_likely_for_bridge_slabs_rails_roof_and_curls=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
