"""TTCS Barclay main hall: raw mesh geometry probes and explicit limitations."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,struct
A=Path(__file__).parent
r=np.frombuffer((A/'model.stl').read_bytes(),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(v,inv.reshape(-1,3),process=False)
def occupied(p):return bool(m.contains([p])[0])
air=[[-85,-33,30],[-85,-36,30],[0,0,15],[43,0,30],[-43,28,15],[43,-28,15]]
solid=[[0,0,1.5],[0,27,10],[43,22,13],[120,0,30],[0,24,60],[0,0,57]]
assert all(not occupied(p) for p in air),[(p,occupied(p)) for p in air]
assert all(occupied(p) for p in solid),[(p,occupied(p)) for p in solid]
samples=[]
for label,p,d in [('miniature_glazing',[44.5,22,13],[0,1,0]),('wall_between_windows',[50,22,13],[0,1,0]),('SW_interface_jamb',[-89.7,-33.8,30],[1,0,0]),('spire_octagonal_body',[0,24,60],[1,0,0]),('east_short_side_window',[120,0,30],[1,0,0]),('center_roof_ridge',[0,0,57],[0,0,1]),('connecting_roof_shell',[43,15,46.2],[0,0,1])]:
 p=np.array(p);d=np.array(d);origin=p-d*400;loc,_,_=m.ray.intersects_location([origin],[d],multiple_hits=True);dist=sorted(float(np.dot(q-origin,d)) for q in loc if np.dot(q-origin,d)>0);cont=[b-a for a,b in zip(dist[::2],dist[1::2]) if a<=400<=b];assert cont,(label,dist);samples.append(dict(feature=label,probe_center=p.tolist(),direction=d.tolist(),ray_hit_distances_mm=dist,probe_containing_intervals_mm=cont))
sections=[]
for normal,origin,label in [([1,0,0],[0,0,0],'central_longitudinal_roof_and_two_storeys'),([0,1,0],[0,0,0],'five_roof_ridges_height_relationships'),([1,0,0],[-85,0,0],'southwest_open_interface'),([0,0,1],[0,0,48],'four_roof_junction_pairs')]:
 sec=m.section(plane_normal=normal,plane_origin=origin);assert sec is not None
 sections.append(dict(label=label,normal=normal,origin=origin,closed_paths=int(sum(bool(e.closed) for e in sec.entities)),entities=len(sec.entities),vertices=len(sec.vertices)))
# Upper envelope at every roof junction. Actual mesh ray hits, not merely design flags.
roof_samples=[]
for sign in [-1,1]:
 for x in [sign*82,sign*77,sign*70,sign*10,sign*15,sign*20]:
  for y in [-15,0,15]:
   loc,_,_=m.ray.intersects_location([[x,y,100]],[[0,0,-1]],multiple_hits=True)
   zs=sorted([float(p[2]) for p in loc],reverse=True);assert zs and zs[0]>43
   roof_samples.append(dict(x=x,y=y,highest_z=zs[0]))
down=m.face_normals[:,2]<-.707
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),name='南神本館（巴克禮紀念館）',empty_air_probes=air,solid_probes=solid,local_sections=sections,actual_mesh_ray_samples=samples,roof_junction_ray_samples=roof_samples,downward_faces_steeper_than_45deg_count=int(down.sum()),downward_face_area_mm2=float(m.area_faces[down].sum()),nominal_glazing_mm=1.05,not_global_minimum_thickness_certificate=True,roof_eaves_arches_interface_and_internal_floor_require_support_assessment=True,SW_boundary_not_real_closed_wall=True,physical_print_tested=False)
(A/'qa/feature-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
