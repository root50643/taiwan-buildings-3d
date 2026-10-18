"""Trace original e45f8d6 normal-ray warnings without changing their locations.

Run with the repository as cwd and Python deps numpy, trimesh, scipy, shapely,
manifold3d. All original records and geometry come from Git e45f8d6, never HEAD.
"""
from pathlib import Path
import hashlib, json, subprocess, collections, math, sys, time
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, Point, box
from shapely import wkt
from manifold3d import Manifold, Mesh64

P = next(Path('.').glob('*/**/nthu-macronix-building'))
OUT = P/'qa/risk-followup-e45f8d6'
OUT.mkdir(exist_ok=True)
COMMIT='e45f8d65989cedca7fec439ce5b6a212323c4d2b'
def gitbytes(name):
    # These frozen inputs were first exported from COMMIT with git show. Prefer
    # them on replay so the review evidence also works without a Git checkout.
    frozen={'model.stl':'input-original.stl','qa/extended-checks-initial.json':'input-original-extended.json'}.get(name)
    if frozen and (OUT/frozen).exists():return (OUT/frozen).read_bytes()
    return subprocess.check_output(['git','show',COMMIT+':'+P.as_posix()+'/'+name])
raw=gitbytes('model.stl')
origjson=gitbytes('qa/extended-checks-initial.json')
(OUT/'input-original.stl').write_bytes(raw)
(OUT/'input-original-extended.json').write_bytes(origjson)
report=json.loads(origjson)
assert hashlib.sha256(raw).hexdigest()==report['stl_sha256']
assert report['stl_sha256']=='9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8'
rec=np.frombuffer(raw, offset=84, dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]))
tri=rec['v'].astype(float)
vertices,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True)
faces=inv.reshape(-1,3)
normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); normals/=np.linalg.norm(normals,axis=1)[:,None]
mesh=trimesh.Trimesh(vertices,faces,process=False)
solid=Manifold(Mesh64(vertices,faces.astype(np.uint64)))
assert str(solid.status()).endswith('NoError')
e1,e2=tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]

def ray(origin,direction):
    p=np.cross(np.broadcast_to(direction,e2.shape),e2); det=np.einsum('ij,ij->i',e1,p)
    valid=np.abs(det)>1e-12; inv=np.zeros_like(det); inv[valid]=1/det[valid]
    tv=origin-tri[:,0]; u=np.einsum('ij,ij->i',tv,p)*inv; q=np.cross(tv,e1)
    v=q@direction*inv; t=np.einsum('ij,ij->i',e2,q)*inv
    valid&=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-8)
    ids=np.flatnonzero(valid)
    if not len(ids):return None
    fi=int(ids[np.argmin(t[ids])]);return {'face':fi,'distance_mm':float(t[fi]),'point_mm':(origin+t[fi]*direction).tolist()}

section_cache={}
def section(axis,coord):
    key=(axis,float(coord))
    if key in section_cache:return section_cache[key]
    n=np.zeros(3);n[axis]=1;pt=n*coord
    keep=[i for i in range(3) if i!=axis]
    seg=trimesh.intersections.mesh_plane(mesh,n,pt)
    if not len(seg):return Polygon(),False,keep
    pts=seg[:,:,keep].reshape(-1,2);parent=list(range(len(pts)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b in cKDTree(pts).query_pairs(1e-4):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    edges=set();adj={}
    for i in range(0,len(pts),2):
        a,b=tuple(pts[find(i)]),tuple(pts[find(i+1)])
        if a!=b:edges.add(tuple(sorted([a,b])))
    for a,b in edges:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
    closed=bool(edges) and all(len(v)==2 for v in adj.values())
    region=Polygon()
    if closed:
        todo=set(edges)
        while todo:
            a,b=next(iter(todo));start=a;points=[a];prev=a;cur=b;todo.remove(tuple(sorted([a,b])))
            while cur!=start:
                points.append(cur);nxt=next(v for v in adj[cur] if v!=prev)
                todo.discard(tuple(sorted([cur,nxt])));prev,cur=cur,nxt
            poly=Polygon(points)
            if not poly.is_valid:closed=False;break
            region=region.symmetric_difference(poly)
    section_cache[key]=(region,closed,keep)
    return region,closed,keep

def polys(g):
    if g.is_empty:return []
    return [g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon']
def gsummary(g):
    return {'area_mm2':float(g.area),'bounds_2d_mm':list(g.bounds) if not g.is_empty else [],'components':len(polys(g))}
def point_segment_distance(p,a,b):
    ab=b-a; t=np.clip((p-a)@ab/(ab@ab),0,1);return float(np.linalg.norm(p-a-t*ab))

rows=[]
for idx,s in enumerate(report['normal_chord_thickness_screen']['flagged_samples']):
    f,g=s['face'],s['exit_face'];start=np.array(s['start_mm']);direction=np.array(s['inward_direction']);end=start+s['distance_mm']*direction;mid=(start+end)/2
    shared=[v for v in tri[f] if any(np.array_equal(v,w) for w in tri[g])]
    angle=math.degrees(math.acos(float(np.clip(normals[f]@normals[g],-1,1))))
    pair={'source_triangle_mm':tri[f].tolist(),'hit_triangle_mm':tri[g].tolist(),'shared_exact_vertices_mm':[v.tolist() for v in shared],'shared_vertex_count':len(shared),'share_edge':len(shared)==2,'outward_normal_angle_deg':angle,'source_normal':normals[f].tolist(),'hit_normal':normals[g].tolist()}
    if len(shared)==2:pair['source_centroid_distance_to_shared_edge_mm']=point_segment_distance(start,*shared)
    axes={}
    for axis,name in enumerate('XYZ'):
        v=np.zeros(3);v[axis]=1;plus=ray(mid,v);minus=ray(mid,-v)
        axes[name]={'minus':minus,'plus':plus,'connected_solid_chord_mm':plus['distance_mm']+minus['distance_mm'] if plus and minus else None}
    sections={}
    for axis,name in enumerate(['YZ','XZ','XY']):
        region,closed,keep=section(axis,start[axis]); localpoint=Point(start[keep]); components=polys(region)
        near=min(components,key=lambda c:c.distance(localpoint)) if components else Polygon()
        sec={'fixed_original_source_coordinate_mm':float(start[axis]),'plane_normal_axis':'XYZ'[axis],'closed':closed,'nearest_solid_component':gsummary(near),'source_to_component_distance_mm':float(near.distance(localpoint)) if components else None,'local_squares':[]}
        for side in [.8,1.6,3.2]:
            x,y=start[keep];clip=region.intersection(box(x-side/2,y-side/2,x+side/2,y+side/2))
            sec['local_squares'].append({'side_mm':side,**gsummary(clip),'solid_area_fraction':float(clip.area/side**2),'wkt_2d_mm':wkt.dumps(clip,rounding_precision=9,trim=True)})
        sections[name]=sec
    volumes=[]
    for side in [1.6,3.2]:
        cube=Manifold.cube((side,side,side)).translate(mid-side/2);local=solid^cube
        volumes.append({'cube_center_original_chord_midpoint_mm':mid.tolist(),'side_mm':side,'solid_volume_mm3':float(local.volume()),'solid_fraction':float(local.volume()/side**3),'solid_components':len(local.decompose())})
    x,y,z=start
    if 16<x<34 and -21<y<-18 and 7<z<38:
        group='connector_grid_relief_nominal_0.8mm'
        cls='real_0.8mm_backed_surface_relief_float32_threshold'
    elif z>52 and -9<y<-5:
        group='new_clerestory_and_cap_tapered_ends'
        cls='real_tapered_vertical_wall_or_cap_end_requires_manufacturing_revision'
    elif z>47 and y>-12:
        group='new_sloping_roof_perimeter_and_clerestory_junction'
        # Short ray meeting a sidewall does not imply entire plate has this
        # thickness: an independent local vertical chord records that fact.
        if axes['Z']['connected_solid_chord_mm'] and axes['Z']['connected_solid_chord_mm']>=1.29:
            cls='solid_roof_plate_boundary_chord_local_Z_material_at_least_1.29mm'
        else:
            cls='roof_strip_junction_taper_requires_local_review'
    else:
        group='existing_oval_window_slot_end_corners'
        cls='real_tapered_slot_corner_in_bulk_oval_body_backing_quantified'
    rows.append({'original_flag_index':idx,'original_sample_unchanged':s,'computed_original_ray_end_mm':end.tolist(),'original_ray_midpoint_mm':mid.tolist(),'region_group':group,'classification':cls,'face_pair_geometry':pair,'axis_chords_at_original_ray_midpoint':axes,'fixed_planes_through_original_source':sections,'local_original_solid_volumes':volumes})
    if idx%30==0: print('processed',idx,flush=True)

groups={}
for group in sorted(set(r['region_group'] for r in rows)):
    rr=[r for r in rows if r['region_group']==group]
    groups[group]={'count':len(rr),'source_faces':[r['original_sample_unchanged']['face'] for r in rr],'minimum_original_ray_distance_mm':min(r['original_sample_unchanged']['distance_mm'] for r in rr),'maximum_original_ray_distance_mm':max(r['original_sample_unchanged']['distance_mm'] for r in rr),'classification_counts':dict(collections.Counter(r['classification'] for r in rr)),'midpoint_Z_chord_min_mm':min(r['axis_chords_at_original_ray_midpoint']['Z']['connected_solid_chord_mm'] for r in rr),'midpoint_Z_chord_max_mm':max(r['axis_chords_at_original_ray_midpoint']['Z']['connected_solid_chord_mm'] for r in rr)}
result={'candidate_commit':COMMIT,'input_stl_sha256':hashlib.sha256(raw).hexdigest(),'input_original_report_sha256':hashlib.sha256(origjson).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'preserved_threshold_mm':.8,'original_warning_count':198,'reconciled_warning_count':len(rows),'original_warning_rows_exactly_preserved':all(r['original_sample_unchanged']==s for r,s in zip(rows,report['normal_chord_thickness_screen']['flagged_samples'])),'method':'All 198 original source coordinates, face IDs, directions, and ray lengths retained. The endpoint is source+original_direction*original_length. Shared exact raw STL vertices and recomputed outward face-normal angle quantify adjacency. For each original chord midpoint, +/- coordinate-axis first-boundary rays quantify connected local solid chords. Fixed XY/XZ/YZ sections go through the unaltered original source coordinate (no offset/resampling); contours use the original check_layers.py 1e-4 mm endpoint-clustering/degree-two/even-odd algorithm. Sections clipped to 0.8/1.6/3.2mm squares and exact-solid Boolean intersections with 1.6/3.2mm cubes give nearby material, with no warning suppressed.','limitations':['Axis chords are material intervals through the original normal-chord midpoint, not a global wall-thickness proof.','Fixed source planes can coincide with original planar faces: closed=false is retained as an unresolved sectional numerical degeneracy; independent local 3D cube intersections still quantify original nearby solid.','Local Boolean volume uses double-precision Manifold from original float32 STL, not exact rational CSG or a slicer.','Classification distinguishes manufacture-relevant protrusions from ray boundary artifacts but does not confer print approval. No slicing or print was performed.'],'group_summary':groups,'samples':rows}
(OUT/'thin_chord_trace.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'thin_chords_followup.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(groups,indent=2));print('wrote',len(rows),'warnings; section cache',len(section_cache))
