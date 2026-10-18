"""Independent exact triangle contact check via edge/plane & edge/edge tests.

This does not import or call either candidate triangle intersection predicate.
It uses a Y sweep rather than the candidate's X sweep. No tolerances/repairs.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from itertools import permutations
import hashlib,json,struct,time

HERE=Path(__file__).resolve().parent
SOURCE=Path(r'<HISTORICAL_OTHER_MODEL_ROOT>')
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def det(a,b): return a[0]*b[1]-a[1]*b[0]
def edges(t): return zip(t,t[1:]+t[:1])
def projected(t,axis): return [tuple(p[k] for k in range(3) if k!=axis) for p in t]
def inside2(p,t):
    turns=[det(sub(v,u),sub(p,u)) for u,v in edges(t)]
    return all(x>=0 for x in turns) or all(x<=0 for x in turns)
def inside3(p,t,n):
    axis=max(range(3),key=lambda k:abs(n[k]))
    return inside2(projected([p],axis)[0],projected(t,axis))
def allowed(p,shared):
    if len(shared)==1:return p==shared[0]
    if len(shared)!=2:return False
    a,b=shared; ap=sub(p,a); ab=sub(b,a)
    collinear=cross(ap,ab)==(0,0,0) if len(p)==3 else det(ap,ab)==0
    return collinear and all(min(a[k],b[k])<=p[k]<=max(a[k],b[k]) for k in range(len(p)))
def segments2(a,b,c,d):
    r,s=sub(b,a),sub(d,c); delta=sub(c,a); denominator=det(r,s)
    if denominator:
        t,u=F(det(delta,s),denominator),F(det(delta,r),denominator)
        if 0<=t<=1 and 0<=u<=1:return [tuple(a[k]+t*r[k] for k in range(2))]
        return []
    if det(delta,r):return []
    return [p for p in (a,b,c,d) if all(min(a[k],b[k])<=p[k]<=max(a[k],b[k]) and min(c[k],d[k])<=p[k]<=max(c[k],d[k]) for k in range(2))]
def edge_plane_points(t,d,other,normal):
    points=[]
    for i,j in [(0,1),(1,2),(2,0)]:
        if d[i]==0 and inside3(t[i],other,normal):points.append(t[i])
        if d[j]==0 and inside3(t[j],other,normal):points.append(t[j])
        if d[i]*d[j]<0:
            ratio=F(d[i],d[i]-d[j])
            p=tuple(t[i][k]+ratio*(t[j][k]-t[i][k]) for k in range(3))
            if inside3(p,other,normal):points.append(p)
    return points
def check(a,b):
    na,nb=cross(sub(a[1],a[0]),sub(a[2],a[0])),cross(sub(b[1],b[0]),sub(b[2],b[0]))
    if na==(0,0,0) or nb==(0,0,0):return 'invalid_degenerate'
    da=[dot(sub(p,b[0]),nb) for p in a]; db=[dot(sub(p,a[0]),na) for p in b]
    if any(all(v>0 for v in d) or all(v<0 for v in d) for d in (da,db)):return 'disjoint'
    shared=[p for p in a if p in b]
    if cross(na,nb)==(0,0,0):
        if any(da) or any(db):return 'disjoint'
        axis=max(range(3),key=lambda k:abs(na[k])); ap,bp=projected(a,axis),projected(b,axis)
        points=[p for p in ap if inside2(p,bp)]+[p for p in bp if inside2(p,ap)]
        for x,y in edges(ap):
            for u,v in edges(bp):points+=segments2(x,y,u,v)
        if not points:return 'disjoint'
        return 'allowed_shared_simplex_contact' if all(allowed(p,projected(shared,axis)) for p in points) else 'invalid_coplanar_contact'
    points=edge_plane_points(a,da,b,nb)+edge_plane_points(b,db,a,na)
    if not points:return 'disjoint'
    return 'allowed_shared_simplex_contact' if all(allowed(p,shared) for p in points) else 'invalid_noncoplanar_contact'
def load(path):
    data=path.read_bytes(); n=struct.unpack_from('<I',data,80)[0]; assert len(data)==84+50*n
    tri=[tuple(tuple(struct.unpack_from('<3f',data,84+i*50+12+j*12)) for j in range(3)) for i in range(n)]
    scale=max(float(v).as_integer_ratio()[1] for t in tri for p in t for v in p)
    return data,[tuple(tuple(int(F(v)*scale) for v in p) for p in t) for t in tri],scale
def controls():
    a=((0,0,0),(2,0,0),(0,2,0)); q=F(1,2); tiny=F(1,2**40)
    cases=[
       ('crossing',((q,q,-1),(q,q,1),(F(3,2),q,0)),True),
       ('coplanar_overlap',((q,q,0),(F(3,2),q,0),(q,F(3,2),0)),True),
       ('duplicate',a,True),
       ('unshared_point_touch',((1,1,0),(1,1,1),(2,2,1)),True),
       ('shared_vertex_extra_crossing',((0,0,0),(1,1,-1),(1,1,1)),True),
       ('shared_edge_coplanar_overlap',((0,0,0),(2,0,0),(1,q,0)),True),
       ('separated',((3,3,1),(4,3,1),(3,4,1)),False),
       ('parallel_distinct',((0,0,q),(2,0,q),(0,2,q)),False),
       ('shared_edge_coplanar',((0,0,0),(2,0,0),(1,-1,0)),False),
       ('shared_edge_folded',((0,0,0),(2,0,0),(1,0,1)),False),
       ('shared_vertex',((0,0,0),(-1,0,1),(0,-1,1)),False),
       ('overlapping_boxes_disjoint',((2,2,0),(2,q,0),(q,2,0)),False),
       ('tiny_exact_separation',((0,0,tiny),(2,0,tiny),(0,2,tiny)),False),
       ('tiny_exact_crossing',((q,q,-tiny),(q,q,tiny),(F(3,2),q,0)),True),
       ('unshared_collinear_edge_contact',((q,0,0),(F(3,2),0,0),(1,-1,0)),True),
       ('degenerate',((0,0,0),(1,0,0),(2,0,0)),True),
    ]
    results=[]
    for name,b,expect in cases:
        count=0; good=True
        for ap in permutations(a):
            for bp in permutations(b):
                for x,y in [(ap,bp),(bp,ap)]:
                    actual=check(x,y).startswith('invalid');count+=1;good=good and actual==expect
        results.append({'name':name,'expected_invalid':expect,'all_permutations_and_pair_swaps_match':good,'evaluations':count})
    assert all(r['all_permutations_and_pair_swaps_match'] for r in results)
    return results
def full_y_sweep(tri):
    bounds=[(tuple(min(p[k] for p in t) for k in range(3)),tuple(max(p[k] for p in t) for k in range(3))) for t in tri]
    order=sorted(range(len(tri)),key=lambda i:(bounds[i][0][1],i)); counts=Counter(); findings=[]; pairs=[]
    for pos,i in enumerate(order):
        lo,hi=bounds[i]
        for j in order[pos+1:]:
            lj,hj=bounds[j]
            if lj[1]>hi[1]:break
            if any(lj[k]>hi[k] or lo[k]>hj[k] for k in (0,2)):continue
            pair=tuple(sorted((i,j)));pairs.append(pair);kind=check(tri[i],tri[j]);counts[kind]+=1
            if kind.startswith('invalid'):findings.append({'faces':pair,'kind':kind})
    return {'aabb_candidate_pairs':len(pairs),'sorted_pairs_sha256':hashlib.sha256(json.dumps(sorted(pairs),separators=(',',':')).encode()).hexdigest(),'counts':dict(counts),'invalid_contact_count':len(findings),'findings':findings}
def flags(path,tri,data):
    initial=json.loads(path.read_text(encoding='utf-8'));assert initial['stl_sha256']==hashlib.sha256(data).hexdigest()
    rows=[]
    for row in initial['self_intersection_screen']['findings']:
        i,j=row['faces'];kind=check(tri[i],tri[j]);rows.append({'faces':[i,j],'preserved_initial_kind':row['kind'],'independent_exact_class':kind,'confirmed_invalid':kind.startswith('invalid')})
    return {'initial_report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'preserved_hard_geometry_checks_passed':initial['hard_geometry_checks_passed'],'flag_count':len(rows),'confirmed_invalid':sum(r['confirmed_invalid'] for r in rows),'classes':dict(Counter(r['independent_exact_class'] for r in rows)),'rows':rows}
if __name__=='__main__':
    start=time.monotonic(); cs=controls();data,tri,scale=load(SOURCE/'model.stl')
    result={'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'method':'Independent exact rational edge/plane intersection with 2D point-in-triangle; coplanar triangle intersection candidates from contained vertices and 9 edge/edge tests; Y ordered AABB sweep. Does not import candidate predicates. Every intersection vertex must lie in exact shared vertex/edge. All vertex permutations and pair swaps exercised for controls.',
      'stl_sha256':hashlib.sha256(data).hexdigest(),'integer_units_per_mm':scale,'controls':cs,'controls_evaluations':sum(r['evaluations'] for r in cs),
      'full_final_stl':full_y_sweep(tri),'final_35_flags':flags(SOURCE/'qa/risk-followup-e45f8d6/r2-extended-checks.json',tri,data)}
    old_data,old_tri,_=load(SOURCE/'qa/risk-followup-e45f8d6/input-original.stl')
    result['e45_37_flags']=flags(SOURCE/'qa/extended-checks-initial.json',old_tri,old_data)
    result['elapsed_seconds']=time.monotonic()-start
    result['limitations']=['Implementation review and synthetic controls are not formal verification.','This contact property does not address thickness, support removal, slicing or print outcome.']
    (HERE/'independent-edge-plane-contact.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k in ['stl_sha256','controls_evaluations','full_final_stl','elapsed_seconds']},indent=2))
