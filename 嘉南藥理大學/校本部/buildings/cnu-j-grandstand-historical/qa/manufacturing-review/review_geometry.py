"""Independent measurements of exported STLs, not source-parameter assertions."""
from pathlib import Path
import hashlib, json, math, itertools
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EPS = 1e-6
COLLISION_VOLUME_TOL = 1e-4

def read(name, mode='assembly'):
    return trimesh.load_mesh(ROOT/'parts'/f'{name}-{mode}.stl', process=True)

def solid(m):
    return Manifold(Mesh64(np.array(m.vertices,dtype=np.float64),np.array(m.faces,dtype=np.uint64)))

def first_hit(m, origin, direction):
    # Vectorized two-sided Moller-Trumbore, preserving original STL coordinates.
    o=np.array(origin,float); d=np.array(direction,float);d/=np.linalg.norm(d)
    t=m.triangles; a=t[:,0]; e1=t[:,1]-a; e2=t[:,2]-a
    h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h)
    good=np.abs(det)>1e-11; inv=np.zeros_like(det);inv[good]=1/det[good]
    s=o-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1)
    v=inv*np.einsum('j,ij->i',d,q);distance=inv*np.einsum('ij,ij->i',e2,q)
    valid=good&(u>=-EPS)&(v>=-EPS)&(u+v<=1+EPS)&(distance>EPS)
    if not np.any(valid): raise RuntimeError(f'no ray intersection at {origin} toward {direction}')
    return float(np.min(distance[valid]))

def caliper(m, origin, direction):
    return first_hit(m,origin,direction)+first_hit(m,origin,-np.array(direction))

def main():
    asm=json.loads((ROOT/'assembly.json').read_text(encoding='utf8'))
    names=[x['part'] for x in asm['inventory']]
    meshes={n:read(n) for n in names}; sol={n:solid(m) for n,m in meshes.items()}
    results={}
    for name in names:
        m=meshes[name]; p=read(name,'print');zmin=p.bounds[0,2]
        down=(p.face_normals[:,2]<-math.cos(math.radians(45)))&(p.triangles_center[:,2]>zmin+.01)
        fn=ROOT/'parts'/f'{name}-print.stl'
        results[name]={
            'print_stl_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),
            'bounds_assembly_mm':m.bounds.tolist(),'bounds_print_mm':p.bounds.tolist(),
            'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),
            'connected_components':len(m.split(only_watertight=False)),
            'signed_volume_mm3':float(m.volume),'manifold_status':str(sol[name].status()),
            'print_volume_mm3':float(p.volume),
            'downward_faces_above_bed_area_mm2':float(p.area_faces[down].sum()),
            'downward_surface_threshold':{'normal_z_less_than':-math.cos(math.radians(45)),'z_above_bed_mm':.01},
            'note':'Downward face area is a screening measurement, not a predicted support area. Vertical faces and bed-facing first layer are excluded.'}
    placements=[]
    for p in asm['placements']:
        placements.append((f"{p['part']}#{p['copy']}",sol[p['part']].translate(p['translation_mm'])))
    collisions=[];max_overlap=0
    for (an,a),(bn,b) in itertools.combinations(placements,2):
        volume=float((a^b).volume());max_overlap=max(max_overlap,volume)
        if volume>COLLISION_VOLUME_TOL:collisions.append({'a':an,'b':bn,'volume_mm3':volume})
    body=meshes['main_body'];roof=meshes['roof'];col=meshes['column'];frame=meshes['mast_brace_frame']
    probes={
        'column_x_full_thickness_mm':caliper(col,[0,15,28],[1,0,0]),
        'column_foot_y_width_mm':caliper(col,[0,15,24.5],[0,1,0]),
        'column_shoulder_y_width_mm':caliper(col,[0,15,28],[0,1,0]),
        'frame_side_thickness_mm':caliper(frame,[0,15,52],[1,0,0]),
        'mast_y_width_mm':caliper(frame,[0,15,52],[0,1,0]),
        'long_brace_perpendicular_width_mm':caliper(frame,[0,-4.5,44.5],[0,-11.8,39]),
        'short_brace_perpendicular_width_mm':caliper(frame,[0,21,44.5],[0,-11.8,-12]),
        'canopy_field_vertical_thickness_mm':caliper(roof,[0,0,36],[0,0,1]),
        'canopy_web_between_aligned_upper_lower_slots_mm':caliper(roof,[81,15,35.5],[0,0,1]),
        'body_slot_x_width_mm':caliper(body,[81,15,24.5],[1,0,0]),
        'body_slot_y_width_mm':caliper(body,[81,15,24.5],[0,1,0]),
        'roof_lower_slot_x_width_mm':caliper(roof,[81,15,34.1],[1,0,0]),
        'roof_lower_slot_y_width_mm':caliper(roof,[81,15,34.1],[0,1,0]),
        'roof_upper_slot_x_width_mm':caliper(roof,[81,15,37],[1,0,0]),
        'roof_upper_slot_y_width_mm':caliper(roof,[81,15,37],[0,1,0]),
        'body_socket_floor_z_mm':24.5-first_hit(body,[81,15,24.5],[0,0,-1]),
        'roof_lower_socket_ceiling_z_mm':34.1+first_hit(roof,[81,15,34.1],[0,0,1]),
        'roof_upper_socket_floor_z_mm':37-first_hit(roof,[81,15,37],[0,0,-1]),
        'front_balcony_underface_z_mm':11+first_hit(body,[0,-34,11],[0,0,1]),
        'front_wall_y_mm_at_z8':-50+first_hit(body,[20,-50,8],[0,1,0]),
        'front_balcony_front_y_mm_at_z13':-50+first_hit(body,[0,-50,13],[0,1,0])}
    # Measure every slot wall, including the full ten-station array and all
    # thirty frame-key sockets. No coordinate normalization or tolerance change.
    slots=[]
    for x in sorted({p['translation_mm'][0] for p in asm['placements'] if p['part']=='column'}):
        for name,m,y,z,xd,yd in [('body',body,15,24.5,2.8,4.4),('roof_lower',roof,15,34.1,2.8,4.4)]+[('roof_upper',roof,y,37,2.2,3.4) for y in [-24,15,27]]:
            wx=caliper(m,[x,y,z],[1,0,0]);wy=caliper(m,[x,y,z],[0,1,0])
            slots.append({'type':name,'x_mm':x,'y_mm':y,'z_probe_mm':z,'measured_slot_x_mm':wx,'measured_slot_y_mm':wy,'total_clearance_x_mm':wx-xd,'total_clearance_y_mm':wy-yd})
    report={'scope':'Independent manufacturing review of exported candidate STL files; no physical print or fit test.',
      'mesh_measurements':results,'pair_collision_check':{'assembled_pieces':len(placements),'pairs_tested':len(placements)*(len(placements)-1)//2,'volume_tolerance_mm3':COLLISION_VOLUME_TOL,'maximum_overlap_mm3':max_overlap,'collisions_over_tolerance':collisions},
      'ray_method':{'method':'Two-sided triangle Moller-Trumbore first surface intersections in unmodified assembly STL coordinates','barycentric_tolerance':EPS,'positive_distance_threshold_mm':EPS,'parallel_det_threshold_mm2':1e-11},
      'measured_features':probes,'all_socket_clearance_measurements':slots,
      'interpretation':{
        'main_body':'Upright. The front balcony projects 5 mm beyond the front wall, so a support-enabled main-body slice is used. Support is also generated in some shallow front/back window reliefs. All modeled reliefs open to the exterior; fine cutters may be needed for removal. There are no enclosed modeled rooms. The conservative automatic support profile has not been physically tested.',
        'roof':'Top face down. Thirty top-side blind sockets open toward the bed and close after 0.8 mm; their 2.6 by 3.8 mm openings require short bridges. The original lower sockets then face up, requiring no captive support. The assembled roof is not the print orientation.',
        'frame_and_column':'Side-flat members put their full planar side on the bed, giving 2.2 or 2.8 mm build thickness. No unsupported free-standing slender mast is printed vertically.',
        'assembly':'Body, ten posts, canopy, then ten upper frames. Sockets are glue-filled positioning joints; gaps are intentional, so there is no press-fit or direct-contact claim. Body key floor gap is 0.30 mm, roof key floor/ceiling gaps 0.15 mm, and shoulders clear by 0.05 mm. Use a suitable gap-filling adhesive and test fit before final bonding.',
        'limits':'Collision and sampled caliper checks do not replace the separate package-wide triangle self-intersection report. Minimum measurements are explicitly located rays; no claim of a complete arbitrary-direction wall-thickness proof.'}}
    (HERE/'geometry-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'features':probes,'collisions':report['pair_collision_check'],'parts':{n:{k:r[k] for k in ['watertight','connected_components','signed_volume_mm3','manifold_status']} for n,r in results.items()}},indent=2))

if __name__=='__main__':main()
