"""Exact rational narrow-phase diagnosis of only previously flagged STL pairs.

This supplements, and does not change or waive, a generic floating-point QA
failure. It is exact on the finite stored STL coordinates, not the intended CAD
surface, and is not a whole-mesh exact intersection certificate.
"""
import argparse
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np
import trimesh


def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unique(items): return list(dict.fromkeys(items))
def cut(tri, origin, normal):
    d=[dot(sub(p,origin),normal) for p in tri]
    out=[]
    for i in range(3):
        j=(i+1)%3
        if d[i]==0: out.append(tri[i])
        if d[i]*d[j]<0: out.append(add(tri[i],mul(sub(tri[j],tri[i]),d[i]/(d[i]-d[j]))))
    return unique(out),d
def on_segment(p,a,b):
    return not any(cross(sub(p,a),sub(b,a))) and all(min(a[i],b[i])<=p[i]<=max(a[i],b[i]) for i in range(3))
def coplanar_clip(a,b,normal):
    keep=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(normal[i]))]
    def orient(p,q,r):
        return (q[keep[0]]-p[keep[0]])*(r[keep[1]]-p[keep[1]])-(q[keep[1]]-p[keep[1]])*(r[keep[0]]-p[keep[0]])
    sign=1 if orient(*b)>0 else -1
    polygon=list(a)
    for i in range(3):
        p,q=b[i],b[(i+1)%3]
        incoming=polygon; polygon=[]
        if not incoming:break
        for j in range(len(incoming)):
            u,v=incoming[j-1],incoming[j]
            du,dv=sign*orient(p,q,u),sign*orient(p,q,v)
            if (du>=0)!=(dv>=0):
                polygon.append(add(u,mul(sub(v,u),du/(du-dv))))
            if dv>=0: polygon.append(v)
    return unique(polygon)
def exact_pair(a,b,shared):
    na,nb=cross(sub(a[1],a[0]),sub(a[2],a[0])),cross(sub(b[1],b[0]),sub(b[2],b[0]))
    if not any(na) or not any(nb):
        raise ValueError('Exact pair diagnosis rejects degenerate triangles')
    direction=cross(na,nb)
    ca,da=cut(a,b[0],nb); cb,db=cut(b,a[0],na)
    out={'signed_a_to_b_plane_exact':[str(x) for x in da], 'signed_b_to_a_plane_exact':[str(x) for x in db],
         'exactly_parallel':not any(direction),'exactly_coplanar':not any(direction) and not any(db),
         'plane_cut_a_points':[[float(x) for x in p] for p in ca],
         'plane_cut_b_points':[[float(x) for x in p] for p in cb]}
    if not any(direction):
        points=coplanar_clip(a,b,na) if not any(db) else []
    elif not ca or not cb:
        points=[]
    else:
        axis=max(range(3),key=lambda i:abs(direction[i]))
        lo=max(min(p[axis] for p in ca),min(p[axis] for p in cb))
        hi=min(max(p[axis] for p in ca),max(p[axis] for p in cb))
        out['exact_interval_axis']=axis
        out['exact_interval_low']=str(lo);out['exact_interval_high']=str(hi)
        points=[] if hi<lo else unique([add(ca[0],mul(direction,(t-ca[0][axis])/direction[axis])) for t in (lo,hi)])
    allowed=not points or (len(shared)==1 and all(p==shared[0] for p in points)) or (len(shared)==2 and all(on_segment(p,*shared) for p in points))
    out['exact_intersection_points']=[[float(x) for x in p] for p in points]
    out['intersection_confined_to_shared_topology']=bool(allowed)
    out['classification']='shared_edge_only' if points and len(shared)==2 and allowed else 'shared_vertex_only' if points and len(shared)==1 and allowed else 'disjoint' if not points else 'unexpected_intersection'
    return out


def rational_triangle(tri):
    return tuple(tuple(F(float(x)) for x in p) for p in tri)


def exact_controls():
    """Small independent cases for exact intersections and legitimate contact."""
    a=[(0,0,0),(2,0,0),(0,2,0)]
    cases={
        'disjoint_parallel':(a,[(0,0,1),(2,0,1),(0,2,1)],[], 'disjoint'),
        'shared_edge_noncoplanar':(a,[(0,0,0),(2,0,0),(0,0,2)],[(0,0,0),(2,0,0)], 'shared_edge_only'),
        'shared_vertex_noncoplanar':(a,[(0,0,0),(-1,0,1),(0,-1,1)],[(0,0,0)], 'shared_vertex_only'),
        'true_noncoplanar_crossing':(a,[(0.5,0.5,-1),(0.5,0.5,1),(1.5,0.5,0)],[], 'unexpected_intersection'),
        'coplanar_area_overlap':(a,[(0.5,0.5,0),(2,0.5,0),(0.5,2,0)],[], 'unexpected_intersection'),
        'coplanar_shared_edge':(a,[(0,0,0),(2,0,0),(1,-1,0)],[(0,0,0),(2,0,0)], 'shared_edge_only'),
        'near_coplanar_shared_edge':(a,[(0,0,0),(2,0,0),(0,-2,2**-22)],[(0,0,0),(2,0,0)], 'shared_edge_only'),
    }
    rows={}
    for name,(ta,tb,shared,expected) in cases.items():
        result=exact_pair(rational_triangle(ta),rational_triangle(tb),rational_triangle(shared))
        rows[name]={'expected_classification':expected, 'actual_classification':result['classification'],
                    'expectation_passed':result['classification']==expected,
                    'triangles_mm':[ta,tb], 'shared_coordinates_mm':shared, 'exact':result}
    try:
        exact_pair(rational_triangle(a),rational_triangle([(0,0,0),(1,0,0),(2,0,0)]),[])
        rejected=False
    except ValueError:
        rejected=True
    rows['degenerate_triangle_guard']={'expectation_passed':rejected,'degenerate_input_rejected':rejected}
    return {'method':'Independent small cases for shared edge/vertex, disjoint, proper crossing, coplanar overlap and near-coplanar contact; no model mesh required.',
            'controls':rows,'all_control_expectations_passed':all(r['expectation_passed'] for r in rows.values())}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mesh',type=Path)
    parser.add_argument('report',type=Path)
    parser.add_argument('--json',type=Path,required=True)
    args=parser.parse_args()
    model,report,output=args.mesh,args.report,args.json
    if output.resolve() in (model.resolve(),report.resolve()):
        parser.error('Output must differ from the STL and original generic report')
    output.parent.mkdir(parents=True,exist_ok=True)
    mesh=trimesh.load_mesh(model,process=True)
    source=json.loads(report.read_text(encoding='utf-8'))
    raw=trimesh.load_mesh(model,process=False)
    input_hash=hashlib.sha256(model.read_bytes()).hexdigest()
    flags=source.get('self_intersections',{}).get('unexpected_contacts_or_intersections',[])
    guard_errors=[]
    if source.get('sha256')!=input_hash:
        guard_errors.append('report_input_sha256_does_not_match_STL')
    if not isinstance(mesh,trimesh.Trimesh) or not isinstance(raw,trimesh.Trimesh):
        guard_errors.append('input_must_load_as_single_Trimesh')
    if not flags or not isinstance(flags,list):
        guard_errors.append('nonempty_flag_list_required')
        flags=[]
    if not len(mesh.faces) or not np.isfinite(mesh.vertices).all():
        guard_errors.append('mesh_empty_or_nonfinite')
    raw_order_equal=bool(np.array_equal(raw.triangles,mesh.triangles))
    float32_exact=bool(np.array_equal(mesh.vertices,mesh.vertices.astype(np.float32).astype(float)))
    if not raw_order_equal:guard_errors.append('processed_triangle_order_or_coordinates_differ_from_raw_STL')
    if not float32_exact:guard_errors.append('coordinates_are_not_exactly_float32_representable')
    seen=set()
    for flag in flags:
        pair=flag.get('faces') if isinstance(flag,dict) else None
        if (not isinstance(pair,list) or len(pair)!=2
                or any(type(i) is not int or not 0<=i<len(mesh.faces) for i in pair)
                or pair[0]==pair[1]):
            guard_errors.append('invalid_flag_face_pair')
            continue
        key=tuple(sorted(pair))
        if key in seen:guard_errors.append('duplicate_flag_pair')
        seen.add(key)
    # This exact degeneracy guard scans the input triangles only; it performs
    # no extra pairwise intersections beyond the supplied flags.
    degenerate=[]
    if np.isfinite(mesh.vertices).all():
        for face_id,tri in enumerate(mesh.triangles):
            t=rational_triangle(tri)
            if not any(cross(sub(t[1],t[0]),sub(t[2],t[0]))):degenerate.append(face_id)
    if degenerate:guard_errors.append('exact_degenerate_triangles_present')
    result={'scope':'Only pairs listed by the existing floating-point report are evaluated for intersection. No whole-mesh pair QA or render is performed; an exact degeneracy input guard scans all triangles.',
            'method':'Exact rational arithmetic on finite float32 STL coordinates promoted to Python float. Unnormalized plane normals and exact plane cuts. Noncoplanar line interval overlap is compared with shared topology. Coplanar polygons are clipped using exact 2D orientation and rational crossings.',
            'input_sha256':input_hash,
            'diagnostic_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'versions':{'python':sys.version,'numpy':np.__version__,'trimesh':trimesh.__version__},
            'report_declared_input_sha256':source.get('sha256'),
            'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
            'loaded_face_count':len(mesh.faces),
            'triangle_order_equal_to_raw_stl':raw_order_equal,
            'coordinates_exactly_float32_representable':float32_exact,
            'exact_degenerate_triangle_indices':degenerate,
            'source_flag_count':len(flags),
            'unique_source_pair_count':len(seen),
            'guard_errors':guard_errors,
            'exact_controls':exact_controls(),
            'pairs':[]}
    for flag in ([] if guard_errors else flags):
        i,j=flag['faces']; a,b=mesh.triangles[[i,j]]
        shared_indices=np.intersect1d(mesh.faces[i],mesh.faces[j])
        shared=mesh.vertices[shared_indices]
        ar,br=map(rational_triangle,(a,b))
        sr=rational_triangle(shared)
        e=exact_pair(ar,br,sr)
        normals=mesh.face_normals[[i,j]]
        r={'original_flag':flag,'shared_vertex_indices':shared_indices.tolist(),'shared_coordinates_mm':shared.tolist(),
           'triangles_mm':[a.tolist(),b.tolist()],
           'unit_normal_cross_norm':float(np.linalg.norm(np.cross(*normals))),
           'float_signed_a_to_b_plane_mm':((a-b[0])@normals[1]).tolist(),
           'float_signed_b_to_a_plane_mm':((b-a[0])@normals[0]).tolist(),
           'exact':e}
        result['pairs'].append(r)
    result['classification_counts']={k:sum(p['exact']['classification']==k for p in result['pairs']) for k in sorted(set(p['exact']['classification'] for p in result['pairs']))}
    result['diagnosed_pair_count']=len(result['pairs'])
    result['all_flags_covered_once']=bool(flags and len(result['pairs'])==len(flags)==len(seen) and not guard_errors)
    result['all_flagged_pairs_have_only_expected_contact']=bool(result['all_flags_covered_once'] and all(p['exact']['intersection_confined_to_shared_topology'] for p in result['pairs']))
    result['passes_flag_diagnosis']=bool(not guard_errors and result['all_flagged_pairs_have_only_expected_contact'] and result['exact_controls']['all_control_expectations_passed'])
    result['generic_report_unchanged']=hashlib.sha256(report.read_bytes()).hexdigest()==result['report_sha256']
    result['passes_flag_diagnosis']=bool(result['passes_flag_diagnosis'] and result['generic_report_unchanged'])
    result['does_not_override_generic_report_exit_status']=True
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('pairs','exact_controls')},indent=2))
    raise SystemExit(0 if result['passes_flag_diagnosis'] else 1)


if __name__=='__main__':main()
