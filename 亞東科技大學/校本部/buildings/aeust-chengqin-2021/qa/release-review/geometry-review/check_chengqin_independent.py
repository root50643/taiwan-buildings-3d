"""Independent review of the exact binary32 STL; never changes the input.

Topology and every triangle-pair contact use this file's own standard-library
implementation. Coordinates are converted to a common integer lattice so pair
intersections are rational/exact for the stored binary32 vertices. Section work
uses independently assembled segments and Shapely, without trimesh or the
candidate's QA code. This is geometry review, not a slicer or a test print.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import struct
import sys
import time


def sub(a, b): return tuple(x-y for x,y in zip(a,b))
def add(a, b): return tuple(x+y for x,y in zip(a,b))
def mul(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum(x*y for x,y in zip(a,b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a,a))
def det2(a,b): return a[0]*b[1]-a[1]*b[0]
def orient2(a,b,c): return det2(sub(b,a),sub(c,a))
def on_segment(p,a,b):
    v, w = sub(b,a), sub(p,a)
    return cross(v,w)==(0,0,0) and 0<=dot(w,v)<=dot(v,v)


def read_binary_stl(path):
    data=path.read_bytes()
    n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n: raise ValueError('Unexpected binary STL size')
    verts=[]; faces=[]; index={}; normals=[]; attributes=[]
    for i in range(n):
        fields=struct.unpack_from('<12fH',data,84+50*i)
        normals.append(tuple(fields[:3])); attributes.append(fields[-1]); f=[]
        for k in range(3):
            p=tuple(fields[3+3*k:6+3*k])
            if not all(math.isfinite(x) for x in p): raise ValueError('Nonfinite vertex')
            if p not in index: index[p]=len(verts); verts.append(p)
            f.append(index[p])
        faces.append(tuple(f))
    scale=max(x.as_integer_ratio()[1] for p in verts for x in p)
    iv=[tuple(int(Q(x)*scale) for x in p) for p in verts]
    return data,verts,faces,iv,scale,normals,attributes


def topology(v,f,iv,scale,stored_normals):
    edges=defaultdict(list); adj=[set() for _ in f]
    normals=[]; zero=[]; normal_disagreement=[]
    volume6=0; areas=[]
    for i,face in enumerate(f):
        a,b,c=(iv[j] for j in face); n=cross(sub(b,a),sub(c,a)); normals.append(n)
        if n==(0,0,0): zero.append(i)
        volume6+=dot(a,cross(b,c))
        areas.append(norm(n)/(2*scale**2))
        sn=stored_normals[i]
        if norm(sn)>0 and dot(sn,n)<=0: normal_disagreement.append(i)
        for a,b in zip(face,face[1:]+face[:1]): edges[tuple(sorted((a,b)))].append((i,a,b))
    for uses in edges.values():
        for x in uses:
            adj[x[0]].update(y[0] for y in uses if y[0]!=x[0])
    remaining=set(range(len(f))); comps=[]
    while remaining:
        stack=[min(remaining)]; comp=[]
        while stack:
            i=stack.pop()
            if i not in remaining: continue
            remaining.remove(i); comp.append(i); stack.extend(adj[i])
        comps.append(comp)
    bad_links=[]
    for vi in range(len(v)):
        link=defaultdict(list)
        for face in f:
            if vi not in face: continue
            other=[k for k in face if k!=vi]
            if len(other)!=2: continue
            a,b=other; link[a].append(b); link[b].append(a)
        seen=set(); stack=[next(iter(link))] if link else []
        while stack:
            q=stack.pop()
            if q in seen: continue
            seen.add(q); stack.extend(link[q])
        if not link or len(seen)!=len(link) or any(len(x)!=2 for x in link.values()): bad_links.append(vi)
    bounds=[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
    result=dict(vertices=len(v),triangles=len(f),edges=len(edges),bounds_mm=bounds,
        extents_mm=[bounds[1][k]-bounds[0][k] for k in range(3)],
        exact_signed_volume_mm3_fraction=str(Q(volume6,6*scale**3)),
        signed_volume_mm3=float(Q(volume6,6*scale**3)),surface_area_mm2=sum(areas),
        min_triangle_area_mm2=min(areas),
        edge_incidence_histogram=dict(Counter(len(x) for x in edges.values())),
        winding_conflict_edges=[list(e) for e,u in edges.items() if len(u)==2 and u[0][1:]==u[1][1:]],
        boundary_edges=[list(e) for e,u in edges.items() if len(u)==1],
        nonmanifold_edges=[list(e) for e,u in edges.items() if len(u)>2],
        degenerate_triangles=zero,duplicate_triangles=len(f)-len({tuple(sorted(x)) for x in f}),
        nonmanifold_vertex_links=bad_links,face_connected_components=len(comps),
        component_face_counts=[len(c) for c in comps],euler=len(v)-len(edges)+len(f),
        stored_normals_opposed_to_geometry=normal_disagreement,
        merge_policy='Exact equality of binary32 coordinate triples; no rounding, repair, or trimesh processing')
    result['passes']=not any((result['winding_conflict_edges'],result['boundary_edges'],result['nonmanifold_edges'],zero,result['duplicate_triangles'],bad_links)) and len(comps)==1 and volume6>0
    return result,normals


def point_in_triangle(p,t,n):
    return all(dot(cross(sub(t[(k+1)%3],t[k]),sub(p,t[k])),n)>=0 for k in range(3))


def segment_hits_triangle(a,b,t,n):
    da=dot(sub(a,t[0]),n); db=dot(sub(b,t[0]),n)
    if da==0 and db==0:
        # The edge lies in the triangle's plane. Project onto its dominant plane.
        drop=max(range(3),key=lambda k:abs(n[k])); axes=[k for k in range(3) if k!=drop]
        proj=lambda p: tuple(p[k] for k in axes)
        pa,pb=proj(a),proj(b); r=sub(pb,pa); hits=[]
        for p in (a,b):
            if point_in_triangle(p,t,n): hits.append(p)
        for c,d in zip(t,t[1:]+t[:1]):
            pc,pd=proj(c),proj(d); s=sub(pd,pc); den=det2(r,s); off=sub(pc,pa)
            if den:
                u=Q(det2(off,s),den); w=Q(det2(off,r),den)
                if 0<=u<=1 and 0<=w<=1: hits.append(add(a,mul(sub(b,a),u)))
            elif det2(off,r)==0:
                for p in (c,d):
                    if on_segment(p,a,b): hits.append(p)
        return hits
    if da>0 and db>0 or da<0 and db<0: return []
    u=Q(da,da-db); p=add(a,mul(sub(b,a),u))
    return [p] if point_in_triangle(p,t,n) else []


def triangle_contacts(t,u,n,m):
    hits=[]
    for a,b in zip(t,t[1:]+t[:1]): hits.extend(segment_hits_triangle(a,b,u,m))
    for a,b in zip(u,u[1:]+u[:1]): hits.extend(segment_hits_triangle(a,b,t,n))
    return set(hits)


def pair_check(iv,f,normals):
    triangles=[tuple(iv[j] for j in face) for face in f]
    bnds=[(tuple(min(p[k] for p in t) for k in range(3)),tuple(max(p[k] for p in t) for k in range(3))) for t in triangles]
    counts=Counter(); unexpected=[]; contact_rows=[]
    for i,j in itertools.combinations(range(len(f)),2):
        counts['total_pairs']+=1
        if any(bnds[i][1][k]<bnds[j][0][k] or bnds[j][1][k]<bnds[i][0][k] for k in range(3)):
            counts['exact_aabb_disjoint']+=1; continue
        counts['exact_aabb_candidates']+=1
        t,u=triangles[i],triangles[j]
        hits=triangle_contacts(t,u,normals[i],normals[j])
        shared=sorted(set(f[i]) & set(f[j])); expected=[iv[x] for x in shared]
        if not hits: counts['candidate_disjoint']+=1; continue
        allowed=(len(expected)==1 and all(p==expected[0] for p in hits)) or (len(expected)==2 and all(on_segment(p,*expected) for p in hits))
        coplanar=cross(normals[i],normals[j])==(0,0,0) and dot(sub(u[0],t[0]),normals[i])==0
        counts['coplanar_contact' if coplanar else 'noncoplanar_contact']+=1
        counts['expected_edge_contacts' if len(expected)==2 else 'expected_vertex_contacts' if len(expected)==1 else 'nonindexed_contacts']+=1
        if not allowed:
            unexpected.append(dict(faces=[i,j],shared_vertices=shared,coplanar=coplanar,
                intersection_points_lattice=[[str(x) for x in p] for p in sorted(hits)]))
    return dict(method='Every unordered pair: exact integer AABB exclusion, then all six edge/closed-triangle intersection tests using rational segment-plane and 2-D segment tests. Any contact beyond the exact indexed shared edge or vertex is rejected.',
        coordinate_arithmetic='Python integers and fractions, exact for binary32 STL coordinates; no floating tolerance in pair tests',
        counts=dict(counts),unexpected_contacts=unexpected,passes=not unexpected,
        limitation='A reproducible exact-coordinate algorithmic check, not an independently machine-verified formal proof or a physical-print guarantee.')


def pair_controls():
    def test(t,u):
        n=cross(sub(t[1],t[0]),sub(t[2],t[0])); m=cross(sub(u[1],u[0]),sub(u[2],u[0]))
        return triangle_contacts(t,u,n,m)
    a=((0,0,0),(4,0,0),(0,4,0))
    cases={
        'crossing_noncoplanar':(((1,1,-1),(1,1,1),(3,1,0)),True),
        'coplanar_area_overlap':(((1,0,0),(5,0,0),(1,4,0)),True),
        'coplanar_containment':(((1,1,0),(2,1,0),(1,2,0)),True),
        'coplanar_disjoint':(((5,5,0),(7,5,0),(5,7,0)),False),
        'parallel_disjoint':(((0,0,1),(4,0,1),(0,4,1)),False),
        'edge_on_triangle_plane':(((1,1,0),(2,1,0),(1,1,2)),True),
        'vertex_contact':(((4,0,0),(5,0,1),(5,1,1)),True),
        'shared_edge_only':(((4,0,0),(0,0,0),(0,-4,0)),True),
    }
    rows={}
    for name,(b,expected) in cases.items():
        points=test(a,b); rows[name]=dict(expected_contact=expected,contact=bool(points),points=[[str(x) for x in p] for p in sorted(points)],passes=bool(points)==expected)
    return rows


def solid_controls():
    # Hand-written unit cube; test both contact classification and topology.
    cv=[(0.,0.,0.),(2.,0.,0.),(2.,2.,0.),(0.,2.,0.),
        (0.,0.,2.),(2.,0.,2.),(2.,2.,2.),(0.,2.,2.)]
    cf=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
        (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    def check(v,f):
        scale=max(x.as_integer_ratio()[1] for p in v for x in p)
        iv=[tuple(int(Q(x)*scale) for x in p) for p in v]
        tp,ns=topology(v,f,iv,scale,[(0,0,0)]*len(f))
        return tp,pair_check(iv,f,ns)
    clean_t,clean_p=check(cv,cf)
    missing,_=check(cv,cf[1:])
    inverted,_=check(cv,[x[::-1] for x in cf])
    overlap_v=cv+[tuple(x+.5 for x in p) for p in cv]
    detached_v=cv+[tuple(x+4 for x in p) for p in cv]
    double_f=cf+[tuple(x+8 for x in face) for face in cf]
    detached_t,_=check(detached_v,double_f)
    overlap_t,overlap_p=check(overlap_v,double_f)
    # A cube sharing only a coordinate vertex with another cube is not a
    # manifold at that vertex; deduplicate exact coordinates explicitly.
    touched_v=cv+[tuple(x+2 for x in p) for p in cv]
    index={}; merged=[]; mapping=[]
    for p in touched_v:
        if p not in index: index[p]=len(merged); merged.append(p)
        mapping.append(index[p])
    touched_t,touched_p=check(merged,[tuple(mapping[x] for x in face) for face in double_f])
    rows=dict(
        clean_cube=dict(passes=clean_t['passes'] and clean_p['passes'],topology_pass=clean_t['passes'],pair_pass=clean_p['passes']),
        missing_face=dict(passes=not missing['passes'],boundary_edge_count=len(missing['boundary_edges'])),
        reversed_winding=dict(passes=not inverted['passes'],volume_mm3=inverted['signed_volume_mm3']),
        detached_cube=dict(passes=not detached_t['passes'],components=detached_t['face_connected_components']),
        overlapping_cubes=dict(passes=not overlap_p['passes'],unexpected_contact_pairs=len(overlap_p['unexpected_contacts']),topology_alone_passes=overlap_t['passes']),
        vertex_touching_cubes=dict(passes=bool(touched_t['nonmanifold_vertex_links']),bad_vertex_links=touched_t['nonmanifold_vertex_links'],pair_check_alone_passes=touched_p['passes']))
    return rows


def sections(v,f,zs):
    from shapely.geometry import LineString, Point
    from shapely.ops import polygonize_full, unary_union
    import shapely
    triangles=[tuple(v[j] for j in face) for face in f]
    rows=[]; previous=None; previous_z=None
    for z in zs:
        segments=[]
        for t in triangles:
            hits=[]
            for a,b in zip(t,t[1:]+t[:1]):
                if (a[2]<z<b[2]) or (b[2]<z<a[2]):
                    u=(z-a[2])/(b[2]-a[2]); hits.append(tuple(round(a[k]+u*(b[k]-a[k]),8) for k in (0,1)))
            if len(hits)==2 and hits[0]!=hits[1]: segments.append(hits)
        polygons,cuts,dangles,invalid=polygonize_full(unary_union([LineString(s) for s in segments]))
        material=[]
        for p in polygons.geoms:
            x,y=p.representative_point().coords[0]; crossings=0
            for a,b in segments:
                if (a[1]>y)!=(b[1]>y):
                    ix=a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1])
                    if ix>x: crossings+=1
            if crossings%2: material.append(p)
        geom=unary_union(material); core=geom.buffer(-0.4,join_style=2)
        component_count=lambda q: 0 if q.is_empty else 1 if q.geom_type=='Polygon' else len(q.geoms)
        row=dict(z_mm=z,area_mm2=geom.area,components=component_count(geom),
            valid=geom.is_valid,cut_count=len(cuts.geoms),dangle_count=len(dangles.geoms),invalid_ring_count=len(invalid.geoms),
            core_0_8mm_area_mm2=core.area,core_components=component_count(core),
            core_vanished=not geom.is_empty and core.is_empty)
        if previous is not None:
            reach=z-previous_z
            row['dz_mm']=reach
            row['outside_45deg_support_envelope_mm2']=geom.difference(previous.buffer(reach,join_style=2)).area
        parts=[] if geom.is_empty else [geom] if geom.geom_type=='Polygon' else list(geom.geoms)
        row['component_cores']=[dict(area_mm2=p.area,core_area_mm2=p.buffer(-0.4,join_style=2).area,core_components=component_count(p.buffer(-0.4,join_style=2))) for p in parts]
        rows.append(row); previous=geom; previous_z=z
    return dict(method='Own triangle/plane segments (XY rounded to 1e-8 mm), polygonize and odd crossing material parity; no candidate QA or trimesh functions used.',
        section_count=len(rows),sampling='0.1 mm midpoint grid plus every vertex-event interval midpoint and points 1e-6 mm above/below events, excluding exactly coplanar event levels.',
        first_section_build_plate_supported=True,feature_core_width_mm=0.8,
        component_core_failures=[dict(z_mm=r['z_mm'],components=r['component_cores']) for r in rows if any(c['core_components']!=1 for c in r['component_cores'])],
        max_components=max(r['components'] for r in rows),
        invalid_or_open_sections=[r for r in rows if not r['valid'] or any(r[k] for k in ('cut_count','dangle_count','invalid_ring_count'))],
        vanished_core_z_mm=[r['z_mm'] for r in rows if r['core_vanished']],
        split_core_z_mm=[r['z_mm'] for r in rows if r['core_components']>r['components']],
        maximum_outside_support_envelope_mm2=max(r.get('outside_45deg_support_envelope_mm2',0) for r in rows),
        support_violations_over_1e_5_mm2=[r for r in rows if r.get('outside_45deg_support_envelope_mm2',0)>1e-5],
        shapely_version=shapely.__version__,rows=rows,
        limitations=['Still finite section sampling; event-augmented grid examines all mesh vertex-height intervals but does not certify arbitrary 3-D minimum thickness.',
        'The 45 degree envelope is a geometric support rule, not extrusion paths, bridges, cooling, shrinkage, adhesion, strength, or a test print.',
        'A section core may survive while an attached taper is thinner than the test width. This is not an every-point minimum wall-thickness certificate.'])



def analytic_risks(v,f,normals,scale):
    down=[]; base=[]
    for i,(face,n) in enumerate(zip(f,normals)):
        if n[2]>=0: continue
        pts=[v[j] for j in face]
        if all(p[2]==0 for p in pts): base.append(i); continue
        xy=math.hypot(n[0],n[1]); ratio=-n[2]/xy if xy else math.inf
        down.append(dict(face=i,angle_from_vertical_deg=math.degrees(math.atan(ratio)),horizontal_expansion_per_unit_height=ratio,
            exact_within_45_degrees=n[2]**2<=n[0]**2+n[1]**2,area_mm2=norm(n)/(2*scale**2),vertices_mm=pts))
    return dict(nonbase_downward_faces=down,base_face_count=len(base),
        maximum_downward_face_angle_from_vertical_deg=max(r['angle_from_vertical_deg'] for r in down),
        exact_over_45_degree_faces=[r['face'] for r in down if not r['exact_within_45_degrees']],
        over_45_01_degree_faces=[r['face'] for r in down if r['angle_from_vertical_deg']>45.01],
        print_limits=['No physical trial print and no printer-specific slice/G-code inspected.',
          '3 mm base, 159 mm total height, and 184.3 x 63.08 mm footprint require allowance for bed exclusions/brim/skirt. Tall body stability, adhesion/warping and supports remain slicer/material dependent.',
          'Filled exterior STL; slicer shell/infill settings determine actual internal material.',
          '0.65 mm front recesses / 0.6 mm connector band depth and chamfers are shallow relief, subject to nozzle, layer quantization, and rescaling.',
          'Component erosion examines core survival/splitting, not pointwise minimum thickness. Attached corner tips and tapered portions may disappear without a failed core.',
          'Roof boxes may give two section components above the main roof: this is expected and is not a disconnected STL shell. Each section component is checked individually.'])


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('stl',type=Path); ap.add_argument('--libs',type=Path); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.libs: sys.path.insert(0,str(a.libs))
    start=time.time(); data,v,f,iv,scale,sn,attrs=read_binary_stl(a.stl)
    top,normals=topology(v,f,iv,scale,sn)
    pair=pair_check(iv,f,normals)
    controls=pair_controls(); solid_ctrl=solid_controls()
    print(json.dumps({'phase':'exact_pairs_complete','topology_pass':top['passes'],'pairs':pair['counts'],'pair_pass':pair['passes'],'elapsed_seconds':time.time()-start}),flush=True)
    events=sorted(set(p[2] for p in v)); zmax=events[-1]
    zs={round(.05+.1*k,8) for k in range(math.ceil((zmax-.05)/.1)) if .05+.1*k<zmax}
    zs.update((x+y)/2 for x,y in zip(events,events[1:]))
    for z in events:
        for dz in (-1e-6,1e-6):
            if 0<z+dz<zmax: zs.add(z+dz)
    zs=sorted(z for z in zs if z not in set(events))
    sec=sections(v,f,zs)
    result=dict(input_name=a.stl.name,sha256=hashlib.sha256(data).hexdigest(),binary_stl_bytes=len(data),binary32_exact_integer_scale=scale,
        python=platform.python_version(),input_untouched=True,attributes_nonzero=sum(x!=0 for x in attrs),
        topology=top,triangle_pairs=pair,triangle_pair_controls=controls,solid_negative_controls=solid_ctrl,vertex_z_events_mm=events,
        sections=sec,analytic_print_review=analytic_risks(v,f,normals,scale),elapsed_seconds=time.time()-start)
    result['digital_geometry_go']=top['passes'] and pair['passes'] and all(x['passes'] for x in controls.values()) and all(x['passes'] for x in solid_ctrl.values()) and not sec['invalid_or_open_sections'] and not sec['component_core_failures'] and not sec['support_violations_over_1e_5_mm2'] and not result['analytic_print_review']['over_45_01_degree_faces']
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    summary={k:val for k,val in result.items() if k not in ('sections','analytic_print_review')}
    summary['sections']={k:val for k,val in sec.items() if k!='rows'}
    summary['analytic_print_review']={k:val for k,val in result['analytic_print_review'].items() if k!='nonbase_downward_faces'}
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if not result['digital_geometry_go']: raise SystemExit(1)


if __name__=='__main__': main()
