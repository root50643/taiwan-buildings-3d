"""Export independent face-ray evidence and compact support/thickness tables."""
import csv, gzip, hashlib, io, json
from pathlib import Path
import numpy as np
import trimesh
from independent_qa import rays, plane_section

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'independent-qa-work'
STL=ROOT/'candidate-repo/淡江大學/淡水校本部/buildings/tku-maritime-museum/model.stl'
data=STL.read_bytes();mesh=trimesh.load_mesh(io.BytesIO(data),file_type='stl',process=False);mesh.merge_vertices(digits_vertex=7)
eps=max(float(max(mesh.extents))*1e-8,1e-7)
directions=-mesh.face_normals;distances,opposite=rays(mesh,mesh.triangles_center+directions*eps*5,directions);distances+=eps*5
with gzip.open(OUT/'full-face-rays-v2.csv.gz','wt',newline='',encoding='utf8') as f:
    w=csv.writer(f);w.writerow(['face','centroid_x_mm','centroid_y_mm','centroid_z_mm','inward_x','inward_y','inward_z','opposite_face','thickness_mm','area_mm2'])
    for i in range(len(mesh.faces)):
        w.writerow([i,*mesh.triangles_center[i],*directions[i],opposite[i],distances[i],mesh.area_faces[i]])
probes=json.loads((OUT/'geometry-probes-v2.json').read_text(encoding='utf8'))
with (OUT/'support-corridors-v2.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.writer(f);w.writerow(['probe','start_x','start_y','start_z','end_x','end_y','end_z','radius_mm','minimum_sampled_clearance_mm','continuous_clearance_lower_bound_mm','collision_free'])
    for name,p in probes['external_access_probes'].items():
        w.writerow([name,*p['start_mm'],*p['end_mm'],p['probe_radius_mm'],p['minimum_sampled_distance_to_mesh_mm'],p['continuous_clearance_lower_bound_mm'],p['collision_free_swept_probe']])
with (OUT/'targeted-thickness-v2.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.writer(f);w.writerow(['probe','solid_interval_index','entry_distance_mm','exit_distance_mm','solid_thickness_mm'])
    for name,p in probes['targeted_line_intersections'].items():
        for i,(a,b) in enumerate(p['solid_intervals_mm']):w.writerow([name,i,a,b,b-a])
# The first raw report flagged two rounded sloped coplanar pairs in v1.
# Retain their actual binary-STL coordinates, original normal discrepancy,
# point-to-plane distances, and the new classification; do not edit old flags.
v1path=ROOT/'candidate-repo/淡江大學/淡水校本部/buildings/tku-maritime-museum/qa/history/v1/model.stl'
v1data=v1path.read_bytes();v1=trimesh.load_mesh(io.BytesIO(v1data),file_type='stl',process=False);v1.merge_vertices(digits_vertex=7)
pairs=[]
for i,j in [(261,328),(471,796)]:
    a,b=v1.triangles[[i,j]];na,nb=v1.face_normals[[i,j]]
    da=(a-b[0])@nb;db=(b-a[0])@na
    shared=np.intersect1d(v1.faces[i],v1.faces[j])
    from independent_qa import pair_intersection
    pairs.append({'faces':[i,j],'triangles_mm':[a.tolist(),b.tolist()],'normal_cross_magnitude':float(np.linalg.norm(np.cross(na,nb))),'a_to_b_signed_plane_distances_mm':da.tolist(),'b_to_a_signed_plane_distances_mm':db.tolist(),'shared_coordinates_mm':v1.vertices[shared].tolist(),'original_v1_normal_parallel_threshold':1e-9,'v2_tolerance_mm':eps,'v2_intersection_result':pair_intersection(a,b,v1.vertices[shared],eps)})
diagnostic={'original_raw_report':'candidate-v1.json','original_flags_preserved':True,'original_v1_stl_sha256':hashlib.sha256(v1data).hexdigest(),'method_correction':'Use BOTH triangles point-to-plane distance within 1.48e-6 mm to classify coplanarity. Original 1e-9 normal-parallel threshold misclassified triangles rounded to float32. Coplanar polygon intersections contain only their actual shared vertex. A new positive control exercises these coordinates; overlapping-cubes negative control still fails intersections.','pairs':pairs,'v2_stl_sha256':hashlib.sha256(data).hexdigest(),'v2_full_face_ray_rows':len(mesh.faces)}
(OUT/'original-intersection-flags-diagnosis.json').write_text(json.dumps(diagnostic,indent=2),encoding='utf8')
print(json.dumps({'stl_sha256':hashlib.sha256(data).hexdigest(),'face_ray_rows':len(mesh.faces),'support_probes':len(probes['external_access_probes']),'original_flag_diagnosis':'original-intersection-flags-diagnosis.json'}))
