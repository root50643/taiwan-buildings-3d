"""Fixed original rays into the r2 STL, plus all 19 new roof warnings.
Run from candidate-repo after thin_chords_followup.py. No original sample moves.
"""
from pathlib import Path
import json, hashlib, math, collections
import numpy as np
import trimesh
from shapely.geometry import Point, box
from shapely import wkt
from manifold3d import Manifold, Mesh64

P=next(Path('.').glob('*/**/nthu-macronix-building'))
OUT=P/'qa/risk-followup-e45f8d6'
helper=OUT/'thin_chords_followup.py'
ns={'__file__':str(helper)}
# Load precisely the helper functions/setup; the 198-row generation loop is not
# re-executed and the original output report is never rewritten by this script.
exec(compile(helper.read_text(encoding='utf-8').split('\nrows=[]')[0],str(helper),'exec'),ns)
old=json.loads((OUT/'thin_chord_trace.json').read_text())
newraw=(P/'model.stl').read_bytes()
SHA='00f6bbdd09196fba873d843bb9d50a1c3aad4e19e760978333dce6f49740627c'
assert hashlib.sha256(newraw).hexdigest()==SHA
(OUT/'input-r2.stl').write_bytes(newraw)
newreport=json.loads((OUT/'r2-extended-checks.json').read_text())
assert newreport['stl_sha256']==SHA
rec=np.frombuffer(newraw,offset=84,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]))
tri=rec['v'].astype(float);vertices,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3)
normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
mesh=trimesh.Trimesh(vertices,faces,process=False);solid=Manifold(Mesh64(vertices,faces.astype(np.uint64)))
ns.update(tri=tri,vertices=vertices,faces=faces,normals=normals,mesh=mesh,solid=solid,e1=tri[:,1]-tri[:,0],e2=tri[:,2]-tri[:,0],section_cache={})
ray,section=ns['ray'],ns['section']
def status(point):
    nearest,dist,face=trimesh.proximity.closest_point_naive(mesh,np.array([point]))
    if dist[0]<1e-6:return {'state':'on_r2_boundary_within_1e-6mm','nearest_boundary_distance_mm':float(dist[0]),'nearest_face':int(face[0])}
    d=np.array([.235,.517,.823]);d/=np.linalg.norm(d);e1,e2=ns['e1'],ns['e2']
    p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p);valid=np.abs(det)>1e-12
    iv=np.zeros_like(det);iv[valid]=1/det[valid];tv=point-tri[:,0];u=np.einsum('ij,ij->i',tv,p)*iv;q=np.cross(tv,e1);v=q@d*iv;t=np.einsum('ij,ij->i',e2,q)*iv
    valid&=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-8)
    ts=sorted(t[valid]);unique=[]
    for x in ts:
        if not unique or x-unique[-1]>1e-7:unique.append(float(x))
    return {'state':'inside_r2_solid' if len(unique)%2 else 'outside_r2_solid','nearest_boundary_distance_mm':float(dist[0]),'nearest_face':int(face[0]),'parity_positive_ray_unique_crossings':len(unique)}
def axes_at(mid):
    axes={}
    for axis,name in enumerate('XYZ'):
        d=np.zeros(3);d[axis]=1;plus=ray(mid,d);minus=ray(mid,-d)
        axes[name]={'minus':minus,'plus':plus,'connected_solid_chord_mm':plus['distance_mm']+minus['distance_mm'] if plus and minus else None}
    return axes
def volumes_at(mid):
    rows=[]
    for side in [1.6,3.2]:
        local=solid^Manifold.cube((side,side,side)).translate(mid-side/2)
        rows.append({'cube_center_original_ray_midpoint_mm':mid.tolist(),'side_mm':side,'solid_volume_mm3':float(local.volume()),'solid_fraction':float(local.volume()/side**3),'solid_components':len(local.decompose())})
    return rows

reprojections=[]
for row in old['samples']:
    if not row['region_group'].startswith('new_'):continue
    s=row['original_sample_unchanged'];start=np.array(s['start_mm']);direction=np.array(s['inward_direction']);mid=np.array(row['original_ray_midpoint_mm'])
    first=ray(start+direction*1e-5,direction)
    if first:
        first['distance_from_unmoved_original_start_mm']=first['distance_mm']+1e-5
        first['exit_faces_outward']=bool(normals[first['face']]@direction>0)
        first['distance_difference_from_original_warning_mm']=first['distance_from_unmoved_original_start_mm']-s['distance_mm']
    reprojections.append({'original_flag_index':row['original_flag_index'],'original_sample_unchanged':s,'old_group':row['region_group'],'r2_state_at_exact_original_source':status(start),'r2_state_at_original_chord_midpoint':status(mid),'r2_first_hit_from_original_direction_and_original_1e_5mm_offset':first,'r2_axis_chords_at_original_chord_midpoint':axes_at(mid),'r2_solid_volumes_at_original_chord_midpoint':volumes_at(mid)})

newroof=[]
for s in newreport['normal_chord_thickness_screen']['flagged_samples']:
    x,y,z=s['start_mm']
    if not(z>40 and x<15):continue
    f,g=s['face'],s['exit_face'];start=np.array(s['start_mm']);direction=np.array(s['inward_direction']);end=start+s['distance_mm']*direction;mid=(start+end)/2
    shared=[v for v in tri[f] if any(np.array_equal(v,w) for w in tri[g])]
    axes=axes_at(mid);secs={}
    for axis,name in enumerate(['YZ','XZ','XY']):
        region,closed,keep=section(axis,start[axis]);a,b=start[keep];local=region.intersection(box(a-1.6,b-1.6,a+1.6,b+1.6))
        secs[name]={'plane_normal_axis':'XYZ'[axis],'fixed_source_coordinate_mm':float(start[axis]),'closed':closed,'local_square_side_mm':3.2,'local_solid_area_mm2':float(local.area),'local_solid_fraction':float(local.area/3.2**2),'wkt_2d_mm':wkt.dumps(local,rounding_precision=9,trim=True)}
    newroof.append({'new_r2_warning_unchanged':s,'ray_endpoint_mm':end.tolist(),'shared_exact_vertices_mm':[v.tolist() for v in shared],'shared_vertex_count':len(shared),'outward_normal_angle_deg':math.degrees(math.acos(float(np.clip(normals[f]@normals[g],-1,1)))),'source_triangle_mm':tri[f].tolist(),'hit_triangle_mm':tri[g].tolist(),'axis_chords_at_new_ray_midpoint':axes,'fixed_source_plane_sections':secs,'local_r2_solid_volumes':volumes_at(mid),'classification':'solid_1.3mm_roof_plate_boundary_ray' if axes['Z']['connected_solid_chord_mm']>=1.29 else 'unresolved_new_roof_thinness'})

result={'original_stl_sha256':old['input_stl_sha256'],'r2_stl_sha256':SHA,'r2_extended_report_sha256':hashlib.sha256((OUT/'r2-extended-checks.json').read_bytes()).hexdigest(),'original_roof_warning_count':37,'original_roof_rays_reprojected_without_moving_source_or_direction':len(reprojections),'original_ray_threshold_mm':.8,'new_total_centroid_warning_count':180,'new_roof_warning_count':len(newroof),'new_roof_classification_counts':dict(collections.Counter(r['classification'] for r in newroof)),'method':'Original 37 roof/clerestory sample coordinates and directions are copied exactly. Reprojection uses the same 1e-5 mm inward origin offset, first-hit ray, and 0.8 mm threshold as the original screen, without moving the location. Exact original points and original chord midpoints are independently classified against r2 using nearest boundary and generic-direction parity; a longer new distance from an interior point is not called a new wall-thickness minimum. New roof warnings retain their new centroid coordinates and are supplemented by fixed source-coordinate planes, shared vertices, angle, coordinate-axis material chords, and local original-chord-midpoint cube volumes.','limitations':['Boundary status is numerical (1e-6 mm); parity is a floating-point point-in-solid screen.','Every original warning remains in thin_chord_trace.json; old and new centroid minima are not directly comparable because triangulation changed.','A 1.3 mm vertical material chord describes nearby roof plate material, not an edge radius or a print guarantee.','No slicer or physical print was performed.'],'original_roof_ray_reprojections':reprojections,'new_roof_warnings_with_local_evidence':newroof}
(OUT/'thin_r2_same_rays_and_roof.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
(OUT/'thin_revision_followup.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'reprojected':len(reprojections),'source_states':dict(collections.Counter(r['r2_state_at_exact_original_source']['state'] for r in reprojections)),'new_roof':len(newroof),'new_classes':result['new_roof_classification_counts'],'min_Z_material':min(r['axis_chords_at_new_ray_midpoint']['Z']['connected_solid_chord_mm'] for r in newroof)},indent=2))
for r in reprojections:
    if r['original_sample_unchanged']['face'] in [1215,1290,1291,1395,1397,1434,1437,1784]: print(r['original_sample_unchanged']['face'],r['r2_state_at_exact_original_source'],r['r2_first_hit_from_original_direction_and_original_1e_5mm_offset'])
