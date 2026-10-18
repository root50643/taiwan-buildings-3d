"""Read-only support-space audit; uses exported STL, no author QA imports.

This does not generate supports, slice, simulate removal, or certify printability.
Run: python independent_support_audit.py --candidate ../candidate --out results.json
"""
from pathlib import Path
import argparse, csv, hashlib, io, json
import numpy as np
import trimesh


def hits(tris, origin, direction):
    """Independent all-triangle Moller-Trumbore ray; distance dedup only at edges."""
    o = np.array(origin, dtype=float)
    d = np.array(direction, dtype=float)
    d /= np.linalg.norm(d)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    e1, e2 = b-a, c-a
    h = np.cross(np.broadcast_to(d, e2.shape), e2)
    det = np.einsum('ij,ij->i', e1, h)
    valid = np.abs(det) > 1e-10
    inv = np.zeros_like(det); inv[valid] = 1/det[valid]
    s = o-a
    u = inv*np.einsum('ij,ij->i', s, h)
    q = np.cross(s, e1)
    v = inv*np.einsum('j,ij->i', d, q)
    t = inv*np.einsum('ij,ij->i', e2, q)
    vals = np.sort(t[valid & (u >= -1e-9) & (v >= -1e-9) & (u+v <= 1+1e-9) & (t > 1e-7)])
    return [float(x) for i,x in enumerate(vals) if i == 0 or x-vals[i-1] > 1e-5]


def probe_line(tris, origin, direction):
    ts = hits(tris, origin, direction)
    return {'origin_mm':origin,'direction':direction,'hits_mm':ts,
            'solid_intervals_mm':[[ts[i],ts[i+1]] for i in range(0,len(ts)-1,2)]}


def swept_tool(mesh, start, end, radius=1.5):
    a,b=np.array(start,dtype=float),np.array(end,dtype=float)
    n=int(np.ceil(np.linalg.norm(b-a)/.2))+1
    pts=np.linspace(a,b,n)
    _,dist,_=trimesh.proximity.closest_point(mesh,pts)
    step=float(np.linalg.norm(b-a)/(n-1))
    lower=float(np.min(dist)-step/2)
    # Include an ideal print bed at z=0 in the clearance, not just the mesh.
    lower=min(lower,float(np.min(pts[:,2])))
    solid_start=(len(hits(mesh.triangles,a,[.991,.073,.11]))%2)==1
    return {'start_mm':start,'end_mm':end,'tool_radius_mm':radius,'samples':n,
            'maximum_step_mm':step,'minimum_mesh_distance_mm':float(np.min(dist)),
            'continuous_centerline_clearance_lower_bound_mm':lower,
            'tool_surface_clearance_lower_bound_mm':lower-radius,
            'start_in_solid':bool(solid_start),
            'nominal_swept_tool_clear':bool(not solid_start and lower>radius),
            'meaning':'An empty-space straight tool corridor only; does not model support shape, adhesion, breakage or withdrawal.'}


def stage_mesh(path):
    data=path.read_bytes()
    mesh=trimesh.load_mesh(io.BytesIO(data),file_type='stl',process=True)
    return mesh,hashlib.sha256(data).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    mesh,sha=stage_mesh(a.candidate/'model.stl');tris=mesh.triangles
    face_normals=mesh.face_normals;center=mesh.triangles_center
    ids=np.flatnonzero((face_normals[:,2] < -np.cos(np.pi/4)) & (center[:,2]>1e-5))
    rows=[]
    for i in ids:
        xyz=center[i]
        o=xyz+np.array([0,0,-1e-5])
        dists=[hits(tris,o,d) for d in [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0]]]
        z=xyz[2]
        if abs(z-16.8)<1e-4:zone='entry bridge underside'
        elif abs(z-64)<1e-4:zone='projecting wings underside'
        elif abs(z-79.8)<1e-4:zone='upper roof 1 mm perimeter lip'
        elif abs(z-109)<1e-4:zone='lower mast crossarm'
        elif abs(z-120)<1e-4:zone='upper mast crossarm'
        else:zone='shallow recess or local step'
        rows.append({'face_index_processed':int(i),'zone':zone,'centroid_mm':xyz.tolist(),
                     'normal':face_normals[i].tolist(),'area_mm2':float(mesh.area_faces[i]),
                     'projected_area_mm2':float(mesh.area_faces[i]*-face_normals[i,2]),
                     'open_cardinal_directions':[d for d,h in zip(['+X','-X','+Y','-Y'],dists) if not h],
                     'first_cardinal_hit_distances_mm':[h[0] if h else None for h in dists]})
    zones={}
    for r in rows:
        z=zones.setdefault(r['zone'],{'face_count':0,'projected_area_mm2':0.0,'closed_cardinal_centroid_count':0})
        z['face_count']+=1;z['projected_area_mm2']+=r['projected_area_mm2'];z['closed_cardinal_centroid_count']+=int(not r['open_cardinal_directions'])
    lines={
        'right_wing_over_deck':([48,44,-1],[0,0,1]),
        'right_wing_outside_body':([55,44,-1],[0,0,1]),
        'right_root_filled':([40,44,-1],[0,0,1]),
        'entry_bridge_main_bay':([-70,-4,-1],[0,0,1]),
        'bridge_piers_gap_at_z8_4':([-87.6,-20,8.4],[0,1,0]),
        'bridge_near_stairs':([-58,-4,-1],[0,0,1]),
        'lower_crossarm_and_roof':([24,41,-1],[0,0,1]),
        'both_crossarms_and_roof':([20,41,-1],[0,0,1]),
        'mast_free_tip':([-100,41,126],[1,0,0]),
        'roof_lip':([34.5,60,-1],[0,0,1]),
        'wing_end_wall':([45,44,69],[1,0,0]),
        'west_body_shallow_recess':([-100,-16,18],[1,0,0]),
    }
    paths={
        'right_wing_deck_space_outward':([50,44,54],[68,44,54]),
        'left_wing_deck_space_outward':([-50,44,54],[-68,44,54]),
        'right_outer_wing_bed_space':([55,44,32],[68,44,32]),
        'left_outer_wing_bed_space':([-55,44,32],[-68,44,32]),
        'bridge_main_bay_to_positive_y':([-70,-4,8.4],[-70,15,8.4]),
        'bridge_near_stairs_to_positive_y':([-58,-4,8.4],[-58,15,8.4]),
        'between_piers_to_inner_bay_positive_x':([-87.6,-2.6,8.4],[-78,-2.6,8.4]),
        'bridge_end_lip_3mm_tool_limitation':([-90,-4,8.4],[-97,-4,8.4]),
        'bridge_end_between_piers_alternative':([-90,-2.6,8.4],[-97,-2.6,8.4]),
        'lower_arm_left_towards_front':([0,41,105],[0,26,105]),
        'lower_arm_left_support_lower_section_towards_front':([0,41,95],[0,26,95]),
        'lower_arm_left_support_rearward_funnel_obstruction':([0,41,95],[0,55,95]),
        'lower_arm_right_towards_front':([24,41,105],[24,26,105]),
        'between_crossarms_towards_front':([20,41,115.9],[20,26,115.9]),
    }
    history={}
    for name in ['v1','v2']:
        m,h=stage_mesh(a.candidate/'qa/history'/name/'model.stl')
        history[name]={'sha256':h,'size_bytes':(a.candidate/'qa/history'/name/'model.stl').stat().st_size,
          'root_line':probe_line(m.triangles,[40,44,-1],[0,0,1]),
          'bridge_hidden_window_line':probe_line(m.triangles,[-100,-2,18],[1,0,0])}
    history['v3']={'sha256':sha,'root_line':probe_line(tris,[40,44,-1],[0,0,1]),
                   'bridge_hidden_window_line':probe_line(tris,[-100,-2,18],[1,0,0])}
    result={'method':'Independent actual-STL measurements: all-triangle ray casting, all downward face centroid survey, and finite-radius tool swept-distance bounds. No author QA code imported.',
      'candidate_commit':'c09925e44d758a46156241ddb7995d7f92ca6c9f','stl_sha256':sha,'bounds_mm':mesh.bounds.tolist(),'triangle_count':len(tris),
      'underside_threshold_degrees':45,'underside_count':len(rows),'underside_projected_area_mm2':sum(r['projected_area_mm2'] for r in rows),
      'underside_zones':zones,'underside_centroids':rows,
      'line_measurements':{k:probe_line(tris,*v) for k,v in lines.items()},
      'independent_tool_paths':{k:swept_tool(mesh,*v) for k,v in paths.items()},
      'revision_measurements':history,
      'limits':['Centroids are finite samples; open cardinal rays do not prove support removability.',
                'Tool probes establish air corridors for an ideal straight circular tool, not extractable bulk support.',
                'No support generation, slicing, material test, force simulation or test print was performed.',
                'Conditional print feasibility requires an appropriate support plan and actual slicer inspection.']}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with a.out.with_suffix('.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['face_index','zone','x','y','z','projected_area_mm2','open_cardinal_directions'])
        for r in rows:w.writerow([r['face_index_processed'],r['zone'],*r['centroid_mm'],r['projected_area_mm2'],' '.join(r['open_cardinal_directions'])])
    print(json.dumps({'sha256':sha,'underside_count':len(rows),'zones':zones,'tool_paths':{k:{'clear':v['nominal_swept_tool_clear'],'lower_bound_mm':v['continuous_centerline_clearance_lower_bound_mm']} for k,v in result['independent_tool_paths'].items()}},indent=2))


if __name__=='__main__':main()
