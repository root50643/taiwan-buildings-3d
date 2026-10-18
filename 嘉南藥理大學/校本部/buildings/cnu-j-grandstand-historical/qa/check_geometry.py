"""Independent, read-only STL review. Run from any directory with requirements.txt.

Writes geometry-review.json next to this script. Never rebuilds or overwrites STL.
Triangle contact tests use the STL's original millimetre coordinates: AABB broad
phase followed by plane/edge triangle intersections and 2D convex clipping for
coplanar pairs. A shared vertex/edge alone is allowed. This is an actual surface
intersection test, independent of watertightness and manifold3d's validity test.
"""
from pathlib import Path
import datetime, hashlib, importlib.metadata, importlib.util, json, platform
import sys, time
sys.dont_write_bytecode = True
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name('geometry-review.json')
EPS = 1e-6                 # absolute surface/contact tolerance, mm
REBUILD_EPS = 1e-5         # binary STL float32 coordinate error allowance, mm
COLLISION_VOLUME_EPS = 1e-7  # mm^3
MIN_FACE_AREA = 1e-12      # mm^2

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cross2(a, b):
    return float(a[0]*b[1]-a[1]*b[0])

def dedupe(points):
    result=[]
    for p in points:
        if not any(np.linalg.norm(p-q)<=EPS for q in result):
            result.append(np.asarray(p,dtype=float))
    return result

def inside_triangle(p, tri):
    a,b,c=tri
    v0=b-a;v1=c-a;v2=p-a
    d00=np.dot(v0,v0);d01=np.dot(v0,v1);d11=np.dot(v1,v1)
    den=d00*d11-d01*d01
    if den<=MIN_FACE_AREA*MIN_FACE_AREA:
        return False
    u=(d11*np.dot(v2,v0)-d01*np.dot(v2,v1))/den
    v=(d00*np.dot(v2,v1)-d01*np.dot(v2,v0))/den
    # Convert absolute mm tolerance to a conservative barycentric tolerance.
    tol=EPS/max(min(np.linalg.norm(v0),np.linalg.norm(v1)),EPS)
    return u>=-tol and v>=-tol and u+v<=1+tol

def clipped_coplanar_points(a,b,normal):
    drop=int(np.argmax(np.abs(normal)))
    axes=[i for i in range(3) if i!=drop]
    a2=a[:,axes]; b2=b[:,axes]
    sign=1 if cross2(b2[1]-b2[0],b2[2]-b2[0])>=0 else -1
    poly=[p.copy() for p in a]
    # Clip in 2D while preserving original 3D coordinates in interpolation.
    for i in range(3):
        c=b2[i];d=b2[(i+1)%3]; edge=d-c
        tol=EPS*max(np.linalg.norm(edge),EPS)
        def dist(p):return sign*cross2(edge,p[axes]-c)
        old=poly;poly=[]
        if not old:break
        prev=old[-1];dp=dist(prev);pin=dp>=-tol
        for cur in old:
            dc=dist(cur);cin=dc>=-tol
            if cin!=pin:
                # The true line, not the tolerance-expanded line, defines contact.
                den=dp-dc
                if abs(den)>1e-20:
                    poly.append(prev+(cur-prev)*(dp/den))
            if cin:poly.append(cur)
            prev=cur;dp=dc;pin=cin
    return dedupe(poly)

def triangle_contact_points(a,b):
    na=np.cross(a[1]-a[0],a[2]-a[0]); nb=np.cross(b[1]-b[0],b[2]-b[0])
    la=np.linalg.norm(na);lb=np.linalg.norm(nb)
    if la<=2*MIN_FACE_AREA or lb<=2*MIN_FACE_AREA:return []
    na/=la;nb/=lb
    da=(a-b[0])@nb; db=(b-a[0])@na
    if (np.all(da>EPS) or np.all(da<-EPS) or
        np.all(db>EPS) or np.all(db<-EPS)):return []
    if np.linalg.norm(np.cross(na,nb))<=1e-9:
        if np.max(np.abs(da))>EPS:return []
        return clipped_coplanar_points(a,b,na)
    points=[]
    for tri,other,n in [(a,b,nb),(b,a,na)]:
        ds=(tri-other[0])@n
        for i in range(3):
            j=(i+1)%3;p=tri[i];q=tri[j];dp=ds[i];dq=ds[j]
            if abs(dp)<=EPS and inside_triangle(p,other):points.append(p)
            if (dp>EPS and dq<-EPS) or (dp<-EPS and dq>EPS):
                hit=p+(q-p)*(dp/(dp-dq))
                if inside_triangle(hit,other):points.append(hit)
    return dedupe(points)

def outside_shared_feature(points, shared):
    if not points:return False
    if not len(shared):return True
    if len(shared)==1:return any(np.linalg.norm(p-shared[0])>EPS*4 for p in points)
    if len(shared)>=3:return True  # duplicated/coincident triangle
    a,b=shared;v=b-a;vv=np.dot(v,v)
    for p in points:
        u=np.clip(np.dot(p-a,v)/vv,0,1) if vv else 0
        if np.linalg.norm(p-(a+u*v))>EPS*4:return True
    return False

def self_intersections(mesh):
    tri=mesh.triangles;lo=tri.min(axis=1);hi=tri.max(axis=1)
    pairs=0;contacts=0;fail=[]
    for i in range(len(tri)):
        js=np.flatnonzero(np.all(lo[i]<=hi[i+1:]+EPS,axis=1)&
                          np.all(hi[i]>=lo[i+1:]-EPS,axis=1))+i+1
        for j in js:
            pairs+=1
            shared_indices=np.intersect1d(mesh.faces[i],mesh.faces[j])
            points=triangle_contact_points(tri[i],tri[j])
            if points:contacts+=1
            shared=mesh.vertices[shared_indices]
            if outside_shared_feature(points,shared):
                fail.append({'faces':[i,int(j)],'shared_vertex_indices':shared_indices.tolist(),
                    'triangles_original_mm':[tri[i].tolist(),tri[j].tolist()],
                    'intersection_points_original_mm':[p.tolist() for p in points]})
    return {'method':'AABB broad phase, plane/edge triangle narrow phase, coplanar convex clipping; shared vertex/edge contact allowed',
            'aabb_candidate_pairs':pairs,'contact_pairs_including_adjacency':contacts,
            'unexpected_surface_intersection_count':len(fail),'unexpected_surface_intersections':fail}

def detector_smoke_test():
    a=np.array([[0,0,0],[2,0,0],[0,2,0]],float)
    crossing=np.array([[.5,.5,-1],[.5,.5,1],[1.5,.5,0]],float)
    overlap=np.array([[.2,.2,0],[1.2,.2,0],[.2,1.2,0]],float)
    edge=np.array([[2,0,0],[0,0,0],[0,-2,0]],float)
    separated=a+np.array([0,0,.01])
    checks={'detects_noncoplanar_crossing':bool(triangle_contact_points(a,crossing)),
            'detects_coplanar_area_overlap':bool(triangle_contact_points(a,overlap)),
            'rejects_separated_parallel_triangles':not bool(triangle_contact_points(a,separated)),
            'allows_shared_edge':not outside_shared_feature(triangle_contact_points(a,edge),a[:2])}
    if not all(checks.values()):raise RuntimeError(f'Triangle detector smoke test failed: {checks}')
    return checks

def load(path,process=True):
    return trimesh.load_mesh(path,process=process,maintain_order=True)

def as_manifold(mesh):
    return Manifold(Mesh64(np.array(mesh.vertices,dtype=np.float64),
                           np.array(mesh.faces,dtype=np.uint64)))

def geometry_record(path):
    mesh=load(path)
    counts=np.bincount(mesh.edges_unique_inverse)
    sm=self_intersections(mesh)
    solid=as_manifold(mesh)
    record={'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
            'vertices':len(mesh.vertices),'triangles':len(mesh.faces),
            'bounds_mm':mesh.bounds.tolist(),'volume_mm3':float(mesh.volume),
            'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
            'connected_components':len(mesh.split(only_watertight=False)),
            'non_two_incident_edge_count':int(np.count_nonzero(counts!=2)),
            'degenerate_face_count':int(np.count_nonzero(mesh.area_faces<=MIN_FACE_AREA)),
            'manifold3d_status':str(solid.status()),'self_intersection':sm}
    record['pass']=bool(record['watertight'] and record['winding_consistent'] and
        record['volume_mm3']>0 and record['connected_components']==1 and
        record['non_two_incident_edge_count']==0 and record['degenerate_face_count']==0 and
        str(solid.status())=='Error.NoError' and sm['unexpected_surface_intersection_count']==0)
    return record,mesh,solid

def canonical_triangles(mesh):
    # Round only for lexicographic ordering; compare unrounded float64 coordinates.
    triangles=np.asarray(mesh.triangles)
    ordered=[]
    for t in triangles:
        idx=np.lexsort(np.round(t,5).T[::-1]);ordered.append(t[idx])
    a=np.array(ordered).reshape((-1,9));idx=np.lexsort(np.round(a,5).T[::-1])
    return a[idx]

def compare_meshes(a,b):
    aa=canonical_triangles(a);bb=canonical_triangles(b)
    if aa.shape!=bb.shape:
        return {'same_triangle_count':False,'pass':False,'shapes':[list(aa.shape),list(bb.shape)]}
    err=float(np.max(np.abs(aa-bb)))
    return {'same_triangle_count':True,'maximum_coordinate_error_mm':err,'pass':err<=REBUILD_EPS}

def run():
    start=time.time()
    report={'review_kind':'Independent read-only geometry QA; no STL or generator mutation',
        'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'units':'mm','coordinate_policy':'All face indices and coordinates retain the loaded STL design/print frame; no normalization before testing',
        'thresholds':{'surface_tolerance_mm':EPS,'shared_feature_tolerance_mm':EPS*4,
            'rebuild_coordinate_tolerance_mm':REBUILD_EPS,'collision_volume_threshold_mm3':COLLISION_VOLUME_EPS,
            'degenerate_area_threshold_mm2':MIN_FACE_AREA},
        'versions':{'python':platform.python_version(),**{n:importlib.metadata.version(n) for n in ['numpy','trimesh','manifold3d']}},
        'inputs':{n:sha(ROOT/n) for n in ['build_model.py','parameters.json','assembly.json','model.stl']},
        'detector_smoke_tests':detector_smoke_test(),'parts':[]}
    meshes={};solids={}
    for path in sorted((ROOT/'parts').glob('*.stl')):
        rec,m,s=geometry_record(path);report['parts'].append(rec)
        meshes[path.stem]=m;solids[path.stem]=s
        print(f'{path.name}: manifold={rec["watertight"]}, components={rec["connected_components"]}, volume={m.volume:.6f}, unexpected intersections={rec["self_intersection"]["unexpected_surface_intersection_count"]}',flush=True)
    spec=importlib.util.spec_from_file_location('candidate_generator',ROOT/'build_model.py')
    gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
    built=gen.build();rebuild={}
    data=json.loads((ROOT/'assembly.json').read_text(encoding='utf-8'))
    for item in data['inventory']:
        name=item['part'];m=gen.as_mesh(built[name])
        rebuild[name+'-assembly']=compare_meshes(m,load(ROOT/'parts'/f'{name}-assembly.stl',False))
        rebuild[name+'-print']=compare_meshes(gen.orient(m,item['print_orientation']),load(ROOT/'parts'/f'{name}-print.stl',False))
    report['rebuild_in_memory_without_writing']=rebuild
    instances=[];posed_meshes=[]
    for item in data['placements']:
        name=item['part'];v=item['translation_mm'];s=solids[name+'-assembly'].translate(v)
        m=meshes[name+'-assembly'].copy();m.apply_translation(v);posed_meshes.append(m)
        instances.append((f'{name}:{item["copy"]}',s,m.bounds))
    collisions=[];checked=0;overlap_bounds=0
    for i,(name,s,bounds) in enumerate(instances):
        for other,t,bb in instances[i+1:]:
            checked+=1
            if np.any(np.minimum(bounds[1],bb[1])-np.maximum(bounds[0],bb[0])<=0):continue
            overlap_bounds+=1;intersection=s^t;volume=float(intersection.volume())
            if volume>COLLISION_VOLUME_EPS:
                collisions.append({'parts':[name,other],'intersection_volume_mm3':volume,
                    'intersection_bounds_original_mm':list(intersection.bounding_box())})
    report['assembled_piece_collisions']={'physical_piece_count':len(instances),'all_pairs':checked,
        'positive_aabb_overlap_pairs_tested_by_manifold_boolean':overlap_bounds,
        'method':'Manifold3d solid intersection of independently loaded STL parts in declared assembly placements',
        'collision_count':len(collisions),'collisions':collisions,'pass':len(collisions)==0}
    overview=load(ROOT/'model.stl',False)
    assembled=trimesh.util.concatenate(posed_meshes)
    report['assembly_overview_matches_placements']=compare_meshes(assembled,overview)
    overview_processed=load(ROOT/'model.stl')
    report['overview']={'file':'model.stl','sha256':sha(ROOT/'model.stl'),
        'watertight':bool(overview_processed.is_watertight),
        'winding_consistent':bool(overview_processed.is_winding_consistent),
        'connected_components':len(overview_processed.split(only_watertight=False)),
        'expected_components':len(instances),'volume_mm3':float(overview_processed.volume),
        'bounds_mm':overview_processed.bounds.tolist(),
        'self_intersection_basis':'Each component surface checked above; all cross-component solid intersections checked in assembly. Separate parts are intentional.'}
    report['input_sha256_unchanged_after_review']=all(sha(ROOT/n)==v for n,v in report['inputs'].items())
    report['limitations']=['Floating-point triangle predicate with stated millimetre tolerances, not arbitrary-precision proof.',
        'Positive-volume collision test does not certify adhesive strength, material tolerance, printer calibration, or support removal.',
        'No physical print or fit test performed; manufacturing review is separate.']
    report['pass']=bool(len(report['parts'])==8 and all(p['pass'] for p in report['parts']) and
        all(x['pass'] for x in rebuild.values()) and report['assembled_piece_collisions']['pass'] and
        report['assembly_overview_matches_placements']['pass'] and
        report['overview']['watertight'] and report['overview']['winding_consistent'] and
        report['overview']['connected_components']==len(instances) and report['input_sha256_unchanged_after_review'])
    report['elapsed_seconds']=round(time.time()-start,3)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Review pass={report["pass"]}; {OUT.name}; elapsed={report["elapsed_seconds"]} s',flush=True)
    return 0 if report['pass'] else 1

if __name__=='__main__':
    raise SystemExit(run())
