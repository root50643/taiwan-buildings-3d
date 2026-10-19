"""Reproducible raw-STL geometry QA. No repair, voxel remesh, or model edits.

Run with Python 3 and numpy, shapely, Pillow. Full triangle AABB candidates are
enumerated and independently refined by floating planes / GEOS and by integer /
Fraction arithmetic on original dyadic STL coordinates. Custom geometry checks
are not a formal verification or a proof of printability. See geometry-report.json.
"""
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction
import argparse, csv, hashlib, json, math, struct, time
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point, GeometryCollection, box
from shapely.ops import unary_union
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'
EPS = 1e-6  # mm; STL has float32 coordinates
AREA_EPS = 1e-10
PLANE_EPS = 1e-10  # arithmetic zero, distinct from final contact tolerance


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jwrite(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf8')


def raw_stl(path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError('Binary STL is too short')
    count = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + 50 * count:
        raise ValueError('Expected exact binary STL record length; not repairing/parsing ASCII')
    dtype = np.dtype([('normal', '<f4', (3,)), ('v', '<f4', (3, 3)), ('attr', '<u2')])
    rec = np.frombuffer(data, dtype=dtype, offset=84, count=count)
    triangles = rec['v'].astype(np.float64)
    vertices, inv = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
    return triangles, vertices, inv.reshape(-1, 3), rec['normal'].astype(np.float64)


def topology(tri, v, faces, stored_normals):
    cross = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
    twice_area = np.linalg.norm(cross, axis=1)
    degenerate = np.flatnonzero(twice_area <= 2*AREA_EPS).tolist()
    edges = defaultdict(list)
    links = defaultdict(list)
    for fi, f in enumerate(faces):
        for a, b in zip(f, np.roll(f, -1)):
            edges[tuple(sorted((int(a), int(b))))].append((fi, int(a), int(b)))
        for k in range(3):
            links[int(f[k])].append((int(f[(k+1)%3]), int(f[(k+2)%3])))
    bad_edges = []
    face_adj = [[] for _ in faces]
    for edge, uses in edges.items():
        if len(uses) != 2 or uses[0][1:] != uses[1][1:][::-1]:
            bad_edges.append({'edge': edge, 'uses': uses})
        if len(uses) == 2:
            a, b = uses[0][0], uses[1][0]
            face_adj[a].append(b); face_adj[b].append(a)
    bad_links = []
    for vi, le in links.items():
        adj = defaultdict(list)
        for a, b in le:
            adj[a].append(b); adj[b].append(a)
        seen = set(); stack = [next(iter(adj))]
        while stack:
            u = stack.pop()
            if u not in seen:
                seen.add(u); stack.extend(adj[u])
        if len(seen) != len(adj) or any(len(n) != 2 for n in adj.values()):
            bad_links.append({'vertex': vi, 'link_vertices': len(adj), 'connected': len(seen) == len(adj), 'degrees': dict(Counter(map(len, adj.values())))})
    seen = set(); comp = []
    for first in range(len(faces)):
        if first in seen: continue
        stack = [first]; n = 0
        while stack:
            fi = stack.pop()
            if fi not in seen:
                seen.add(fi); n += 1; stack.extend(face_adj[fi])
        comp.append(n)
    dup = Counter(tuple(sorted(map(int, f))) for f in faces)
    volume = float(np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum()/6)
    unit = cross / np.maximum(twice_area[:, None], 1e-300)
    stored_len = np.linalg.norm(stored_normals, axis=1)
    dots = np.einsum('ij,ij->i', unit, stored_normals/np.maximum(stored_len[:, None], 1e-300))
    result = {
        'raw_triangle_count': len(tri), 'exact_coordinate_welded_vertices': len(v),
        'raw_coordinate_records': int(tri.size//3), 'finite_coordinates': bool(np.isfinite(tri).all()),
        'duplicate_triangles_ignoring_winding': sum(n-1 for n in dup.values()),
        'degenerate_triangles': degenerate, 'minimum_triangle_area_mm2': float(twice_area.min()/2),
        'edge_count': len(edges), 'edge_incidence_histogram': dict(Counter(len(u) for u in edges.values())),
        'bad_edge_count': len(bad_edges), 'bad_edge_examples': bad_edges[:50],
        'bad_vertex_link_count': len(bad_links), 'bad_vertex_link_examples': bad_links[:50],
        'face_connected_components': len(comp), 'component_triangle_counts': comp,
        'euler_characteristic': int(len(v)-len(edges)+len(faces)),
        'signed_volume_mm3': volume, 'surface_area_mm2': float(twice_area.sum()/2),
        'bounds_mm': [v.min(axis=0).tolist(), v.max(axis=0).tolist()],
        'stored_normal_opposed_face_count': int((dots < -0.99).sum()),
        'stored_normal_zero_count': int((stored_len <= EPS).sum()),
        'passed': bool(np.isfinite(tri).all() and not degenerate and not bad_edges and not bad_links and all(n == 1 for n in dup.values()) and volume > 0),
        'method': 'Read raw binary records; exact float-coordinate deduplication only, no tolerance welding or repair. Each edge must have two oppositely directed uses, and each vertex link must be one cycle.'
    }
    return result, unit


def plane_clip(tri, distances):
    pts = []
    for k in range(3):
        a, b = tri[k], tri[(k+1)%3]
        da, db = distances[k], distances[(k+1)%3]
        if abs(da) <= PLANE_EPS: pts.append(a)
        if (da < -PLANE_EPS and db > PLANE_EPS) or (da > PLANE_EPS and db < -PLANE_EPS):
            pts.append(a + (b-a)*(da/(da-db)))
    return np.asarray(pts)


def tri_intersection(a, b, normal_a, normal_b, shared_points):
    """Return numerical intersection classification, permitting true simplex contacts."""
    db = (b-a[0]) @ normal_a
    da = (a-b[0]) @ normal_b
    if (db.min() > PLANE_EPS or db.max() < -PLANE_EPS or da.min() > PLANE_EPS or da.max() < -PLANE_EPS):
        return 'none', None
    direction = np.cross(normal_a, normal_b)
    length = np.linalg.norm(direction)
    if length <= 1e-12:
        if np.max(np.abs(db)) > PLANE_EPS or np.max(np.abs(da)) > PLANE_EPS:
            return 'none', None
        drop = int(np.argmax(np.abs(normal_a)))
        a2 = np.delete(a, drop, axis=1); b2 = np.delete(b, drop, axis=1)
        inter = Polygon(a2).intersection(Polygon(b2))
        if inter.is_empty: return 'none', None
        if len(shared_points) >= 2:
            permitted = LineString(np.delete(shared_points[:2], drop, axis=1))
        elif len(shared_points) == 1:
            permitted = Point(np.delete(shared_points[0], drop))
        else:
            permitted = GeometryCollection()
        unexpected = inter if permitted.is_empty else inter.difference(permitted.buffer(EPS))
        # Area intersection, even on adjacent triangles, cannot be shared-edge contact.
        if inter.area > AREA_EPS or not unexpected.is_empty:
            return 'unexpected_coplanar', {'type': inter.geom_type, 'area_mm2_projected': float(inter.area), 'length_mm_projected': float(inter.length)}
        return 'permitted_shared_simplex', None
    direction /= length
    sa = plane_clip(a, da); sb = plane_clip(b, db)
    if not len(sa) or not len(sb): return 'none', None
    ta, tb = sa @ direction, sb @ direction
    lo, hi = max(ta.min(), tb.min()), min(ta.max(), tb.max())
    if hi < lo-EPS: return 'none', None
    if len(shared_points):
        ts = shared_points @ direction
        if lo >= ts.min()-EPS and hi <= ts.max()+EPS:
            return 'permitted_shared_simplex', None
    return 'unexpected_noncoplanar', {'intersection_length_mm': float(max(0, hi-lo)), 'line_coordinate_interval': [float(lo), float(hi)]}


def collision_controls():
    a = np.array([[0., 0, 0], [2, 0, 0], [0, 2, 0]])
    cases = [
        ('separate', np.array([[10.,0,0],[12,0,0],[10,2,0]]), [], 'none'),
        ('noncoplanar_crossing', np.array([[.5,.5,-1],[.5,.5,1],[1.5,.5,0]]), [], 'unexpected_noncoplanar'),
        ('coplanar_overlap', np.array([[.5,.5,0],[1.5,.5,0],[.5,1.5,0]]), [], 'unexpected_coplanar'),
        ('legal_shared_edge', np.array([[0.,0,0],[2,0,0],[1,-1,0]]), [[0.,0,0],[2,0,0]], 'permitted_shared_simplex'),
        ('legal_shared_vertex', np.array([[0.,0,0],[-1,0,1],[0,-1,1]]), [[0.,0,0]], 'permitted_shared_simplex'),
        ('shared_vertex_but_crossing', np.array([[0.,0,0],[1,1,-1],[1,1,1]]), [[0.,0,0]], 'unexpected_noncoplanar'),
        ('almost_coplanar_separate_faces', np.array([[1.1,1.1,1e-7],[2,1.1,2e-7],[1.1,2,1e-7]]), [], 'none'),
        ('warped_shared_vertex_only', np.array([[0.,0,0],[-2,0,1e-7],[0,-2,2e-7]]), [[0.,0,0]], 'permitted_shared_simplex'),
    ]
    rows = []
    for name, b, shared, expected in cases:
        na = np.cross(a[1]-a[0], a[2]-a[0]); na /= np.linalg.norm(na)
        nb = np.cross(b[1]-b[0], b[2]-b[0]); nb /= np.linalg.norm(nb)
        got, detail = tri_intersection(a, b, na, nb, np.asarray(shared))
        rows.append({'name': name, 'expected': expected, 'actual': got, 'passed': got == expected})
    return rows


def isub(a,b): return tuple(a[k]-b[k] for k in range(3))
def icross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def idot(a,b): return sum(a[k]*b[k] for k in range(3))
def orient2(a,b,p): return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def exact_integer_vertices(vertices):
    ratios = [[float(c).as_integer_ratio() for c in v] for v in vertices]
    denominator = max(d for row in ratios for n,d in row)
    # IEEE floats are dyadic, therefore the largest denominator is a common one.
    return [tuple(n*(denominator//d) for n,d in row) for row in ratios], denominator


def exact_triangle_intersection(a,b,na,nb,shared):
    """Exact predicates and Fraction constructions on dyadic STL coordinates."""
    da=[idot(isub(p,b[0]),nb) for p in a]
    db=[idot(isub(p,a[0]),na) for p in b]
    if min(da)>0 or max(da)<0 or min(db)>0 or max(db)<0: return 'none'
    direction=icross(na,nb)
    if direction == (0,0,0):
        if any(da) or any(db): return 'none'
        drop=max(range(3),key=lambda k:abs(na[k])); axes=[k for k in range(3) if k!=drop]
        a2=[tuple(p[k] for k in axes) for p in a]; b2=[tuple(p[k] for k in axes) for p in b]
        sign=1 if orient2(b2[0],b2[1],b2[2])>0 else -1
        poly=[tuple(Fraction(c) for c in p) for p in a2]
        for k in range(3):
            if not poly: return 'none'
            e0,e1=b2[k],b2[(k+1)%3]
            clipped=[]; prev=poly[-1]; dp=orient2(e0,e1,prev)*sign
            for cur in poly:
                dc=orient2(e0,e1,cur)*sign
                if (dp>=0) != (dc>=0):
                    t=dp/(dp-dc)
                    clipped.append(tuple(prev[q]+t*(cur[q]-prev[q]) for q in range(2)))
                if dc>=0: clipped.append(cur)
                prev,dp=cur,dc
            poly=list(dict.fromkeys(clipped))
        if not poly: return 'none'
        s2=[tuple(p[k] for k in axes) for p in shared]
        if len(s2)==1 and all(p==s2[0] for p in poly): return 'permitted_shared_simplex'
        if len(s2)==2 and all(orient2(s2[0],s2[1],p)==0 and all(min(s2[0][q],s2[1][q])<=p[q]<=max(s2[0][q],s2[1][q]) for q in range(2)) for p in poly):
            return 'permitted_shared_simplex'
        return 'unexpected_coplanar'
    axis=max(range(3),key=lambda k:abs(direction[k]))
    def interval(t,ds):
        result=[]
        for k in range(3):
            aa,bb=t[k][axis],t[(k+1)%3][axis]; x,y=ds[k],ds[(k+1)%3]
            if x==0: result.append(Fraction(aa))
            if x*y<0: result.append(Fraction(aa*y-bb*x,y-x))
        return (min(result),max(result)) if result else None
    ia,ib=interval(a,da),interval(b,db)
    if ia is None or ib is None: return 'none'
    lo,hi=max(ia[0],ib[0]),min(ia[1],ib[1])
    if lo>hi: return 'none'
    if shared and lo>=min(p[axis] for p in shared) and hi<=max(p[axis] for p in shared): return 'permitted_shared_simplex'
    return 'unexpected_noncoplanar'


def exact_collisions(tri,vertices,faces):
    integer_vertices,denominator=exact_integer_vertices(vertices)
    itri=[[integer_vertices[int(k)] for k in f] for f in faces]
    normals=[icross(isub(t[1],t[0]),isub(t[2],t[0])) for t in itri]
    sets=[set(map(int,f)) for f in faces]
    lo,hi=tri.min(axis=1),tri.max(axis=1)
    count=0;counts=Counter();unexpected=[];started=time.time()
    for i in range(len(tri)-1):
        js=np.flatnonzero(np.all(hi[i]+EPS>=lo[i+1:],axis=1)&np.all(hi[i+1:]+EPS>=lo[i],axis=1))+i+1
        for j in js:
            shared=sorted(sets[i]&sets[j]); count+=1
            kind=exact_triangle_intersection(itri[i],itri[j],normals[i],normals[j],[integer_vertices[k] for k in shared])
            counts[kind]+=1
            if kind.startswith('unexpected'):
                unexpected.append({'faces':[i,int(j)],'shared_vertex_count':len(shared),'classification':kind})
    controls=exact_collision_controls()
    return {
        'all_unordered_triangle_pairs':len(tri)*(len(tri)-1)//2,'aabb_candidate_pairs_refined':count,
        'coordinate_integer_common_denominator':str(denominator),'classifications':dict(counts),
        'unexpected_pair_count':len(unexpected),'unexpected_pairs':unexpected,
        'elapsed_seconds':round(time.time()-started,3),'controls':controls,'passed':not unexpected and all(r['passed'] for r in controls),
        'method':'Original float32 STL coordinates converted exactly to dyadic integer coordinates with one common power-of-two denominator. Every inclusive-AABB candidate tested again with unbounded Python integer signed-plane predicates. Noncoplanar triangle/plane intervals constructed and compared with exact fractions; coplanar triangles intersected by exact-fraction Sutherland-Hodgman clipping in dominant 2D projection. Only an intersection confined exactly to the actual shared STL vertex/edge is allowed. No epsilon is used in exact refinement; the inclusive floating AABB broad phase is conservative for the same finite input coordinates.',
        'limits':'Exact arithmetic applies only to triangle self-intersections of the quantized binary STL. It is custom code with numerical controls and a separately implemented floating cross-check, not a formally verified geometry library. It does not validate architecture, slicer paths, feature strength, supports or physical printing.'
    }


def exact_collision_controls():
    a=np.array([[0.,0,0],[2,0,0],[0,2,0]])
    cases=[
        ('separate',[[10.,0,0],[12,0,0],[10,2,0]],'none'),
        ('noncoplanar_crossing',[[.5,.5,-1],[.5,.5,1],[1.5,.5,0]],'unexpected_noncoplanar'),
        ('coplanar_containment',[[.5,.5,0],[1.5,.5,0],[.5,1.5,0]],'unexpected_coplanar'),
        ('legal_shared_edge',[[0.,0,0],[2,0,0],[1,-1,0]],'permitted_shared_simplex'),
        ('legal_shared_vertex',[[0.,0,0],[-1,0,1],[0,-1,1]],'permitted_shared_simplex'),
        ('legal_coplanar_vertex',[[0.,0,0],[-1,0,0],[0,-1,0]],'permitted_shared_simplex'),
        ('shared_vertex_but_crossing',[[0.,0,0],[1,1,-1],[1,1,1]],'unexpected_noncoplanar'),
        ('shared_edge_but_area_overlap',[[0.,0,0],[2,0,0],[.5,.5,0]],'unexpected_coplanar'),
        ('almost_coplanar_separate_faces',[[1.1,1.1,1e-7],[2,1.1,2e-7],[1.1,2,1e-7]],'none'),
        ('warped_shared_vertex_only',[[0.,0,0],[-2,0,1e-7],[0,-2,2e-7]],'permitted_shared_simplex'),
        ('interior_point_touch',[[.5,.5,0],[.5,.5,-1],[1,.5,-1]],'unexpected_noncoplanar'),
        ('interior_segment_touch',[[.5,.5,0],[1,.5,0],[.5,.5,-1]],'unexpected_noncoplanar'),
    ]
    rows=[]
    for name,b,expected in cases:
        both=np.vstack([a,np.asarray(b,dtype=float)]); vs,inv=np.unique(both,axis=0,return_inverse=True)
        iv,den=exact_integer_vertices(vs); aa=[iv[int(k)] for k in inv[:3]];bb=[iv[int(k)] for k in inv[3:]]
        na=icross(isub(aa[1],aa[0]),isub(aa[2],aa[0]));nb=icross(isub(bb[1],bb[0]),isub(bb[2],bb[0]))
        shared=[iv[k] for k in sorted(set(map(int,inv[:3]))&set(map(int,inv[3:])))]
        got=exact_triangle_intersection(aa,bb,na,nb,shared)
        rows.append({'name':name,'expected':expected,'actual':got,'passed':got==expected})
    return rows


def collisions(tri, vertices, faces, normals):
    lo, hi = tri.min(axis=1), tri.max(axis=1)
    candidates = 0; counts = Counter(); unexpected = []
    sets = [set(map(int, f)) for f in faces]
    started = time.time()
    for i in range(len(tri)-1):
        js = np.flatnonzero(np.all(hi[i]+EPS >= lo[i+1:], axis=1) & np.all(hi[i+1:]+EPS >= lo[i], axis=1)) + i+1
        candidates += len(js)
        for j in js:
            shared = sorted(sets[i] & sets[j])
            kind, detail = tri_intersection(tri[i], tri[j], normals[i], normals[j], vertices[shared])
            counts[kind] += 1
            if kind.startswith('unexpected'):
                unexpected.append({'faces': [i, int(j)], 'shared_vertex_count': len(shared), 'classification': kind, 'detail': detail})
    controls = collision_controls()
    return {
        'all_unordered_triangle_pairs': len(tri)*(len(tri)-1)//2,
        'all_aabb_candidate_pairs_refined': candidates,
        'aabb_excluded_pairs': len(tri)*(len(tri)-1)//2-candidates,
        'classifications': dict(counts), 'unexpected_pair_count': len(unexpected),
        'unexpected_pairs': unexpected, 'elapsed_seconds': round(time.time()-started, 3),
        'controls': controls, 'passed': not unexpected and all(r['passed'] for r in controls),
        'method': 'Every unordered pair tested against inclusive AABBs. All AABB candidates refined: signed triangle planes, line/triangle interval overlap; parallel coplanar faces projected to dominant plane and GEOS intersected. Only the geometric intersection lying on the actual shared STL vertex/edge is permitted. No candidate cap, early exit, or broad exemption for adjacent faces.',
        'limitation': 'Exhaustive floating-point refinement at 1e-6mm final contact / 1e-10mm arithmetic plane-zero / 1e-10mm2 projected-area tolerance. Plane clipping uses arithmetic-zero tolerance, not contact tolerance, so nearly coplanar triangles are not broadened to their whole planes. Not an exact-arithmetic robust-predicate proof; features below tolerance and pathological near-parallel cases are not certified.'
    }


def section(tri, z):
    d = tri[:, :, 2]-z
    active = np.flatnonzero((d.min(axis=1) < 0) & (d.max(axis=1) > 0))
    edges = []; points = {}
    for fi in active:
        verts = tri[fi]; ds = d[fi]; cross = []
        for k in range(3):
            a, b = verts[k], verts[(k+1)%3]
            da, db = ds[k], ds[(k+1)%3]
            if da*db < 0:
                xy = (a+(b-a)*(da/(da-db)))[:2]
                key = tuple(np.round(xy, 6))
                points[key] = xy
                cross.append(key)
        if len(cross) != 2:
            return None, {'error': 'non_two_endpoint_triangle_intersection', 'face': int(fi), 'endpoint_count': len(cross)}
        if cross[0] != cross[1]: edges.append(tuple(cross))
    if not edges: return GeometryCollection(), {'raw_segments': 0, 'valid': True, 'components': 0, 'holes': 0, 'area_mm2': 0., 'loops': 0}
    ec = Counter(tuple(sorted(e)) for e in edges)
    adjacency = defaultdict(list)
    for a, b in edges:
        adjacency[a].append(b); adjacency[b].append(a)
    bad_degrees = {str(p): len(adj) for p, adj in adjacency.items() if len(adj) != 2}
    if bad_degrees or any(n != 1 for n in ec.values()):
        return None, {'valid': False, 'error': 'raw_contour_graph_not_disjoint_cycles', 'bad_degree_count': len(bad_degrees), 'examples': dict(list(bad_degrees.items())[:10]), 'duplicate_segment_count': sum(n-1 for n in ec.values())}
    remaining = set(adjacency); loops = []
    while remaining:
        start = next(iter(remaining)); prev = None; cur = start; ring = []
        while True:
            ring.append(cur); remaining.discard(cur)
            opts = adjacency[cur]
            nxt = opts[0] if opts[0] != prev else opts[1]
            prev, cur = cur, nxt
            if cur == start: break
            if len(ring) > len(adjacency):
                return None, {'valid': False, 'error': 'cycle_traversal_failed'}
        poly = Polygon(ring)
        if not poly.is_valid or poly.area <= AREA_EPS:
            return None, {'valid': False, 'error': 'invalid_raw_ring', 'reason': shapely.is_valid_reason(poly)}
        loops.append(poly)
    # Disjoint or nested loops only. Crossing/touching loops are not silently repaired.
    for i, a in enumerate(loops):
        for b in loops[i+1:]:
            if a.boundary.intersects(b.boundary):
                return None, {'valid': False, 'error': 'raw_ring_boundaries_intersect'}
    geom = GeometryCollection()
    for poly in loops: geom = geom.symmetric_difference(poly)
    polys = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else ([geom] if geom.geom_type == 'Polygon' else [])
    return geom, {'raw_segments': len(edges), 'valid': bool(geom.is_valid), 'loops': len(loops), 'components': len(polys), 'holes': sum(len(p.interiors) for p in polys), 'area_mm2': float(geom.area)}


def morph(geom, diameter):
    r = diameter/2
    # Mitre joins avoid reporting ordinary square corners as round-buffer losses.
    opened = geom.buffer(-r, join_style='mitre').buffer(r, join_style='mitre').intersection(geom)
    closed = geom.buffer(r, join_style='mitre').buffer(-r, join_style='mitre').union(geom)
    return opened, closed


def morphology_controls():
    body = box(0, 0, 20, 20)
    skinny = body.union(box(20, 9.8, 24, 10.2))
    broad = body.union(box(20, 9, 24, 11))
    slot = body.difference(box(8, 9.8, 12, 10.2))
    so, sc = morph(skinny, .8); bo, bc = morph(broad, .8); vo, vc = morph(slot, .8)
    loss = skinny.difference(so).area; broad_loss = broad.difference(bo).area; filled = vc.difference(slot).area
    return {
        'diameter_mm': .8,
        'negative_thin_finger_width_mm': .4, 'negative_thin_finger_length_mm': 4,
        'negative_thin_finger_opening_loss_mm2': float(loss),
        'positive_broad_finger_width_mm': 2, 'positive_broad_finger_opening_loss_mm2': float(broad_loss),
        'negative_slot_width_mm': .4, 'negative_slot_closing_fill_mm2': float(filled),
        'passed': bool(loss > 1.5 and broad_loss < 1e-6 and filled > 1.5)
    }


def draw_sections(rows, geoms):
    width, height = 1500, 1470
    im = Image.new('RGB', (width, height), '#f0f3f5'); draw = ImageDraw.Draw(im)
    try: font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    except OSError: font = ImageFont.load_default()
    selected = [0.1, 2.5, 8.1, 15.1, 25.1, 33.1, 39.1, 45.1, 54.3]
    for panel, target in enumerate(selected):
        idx = min(range(len(rows)), key=lambda i: abs(rows[i]['requested_z_mm']-target))
        row = rows[idx]; geom = geoms[idx]; ox = (panel%3)*500; oy=(panel//3)*490
        draw.rectangle((ox+10,oy+10,ox+490,oy+480), fill='white', outline='#bbc7ce')
        draw.text((ox+24,oy+24), f"z={row['actual_z_mm']:.5f} mm | area={row.get('area_mm2', 0):.2f}", fill='#172b3a', font=font)
        draw.text((ox+24,oy+52), f"components={row.get('components')} holes={row.get('holes')}", fill='#172b3a', font=font)
        if geom is None: continue
        scale = 2.65
        def pixel(xy): return [(ox+250+x*scale, oy+265-y*scale) for x,y in xy]
        def paint(g, color):
            polys = list(g.geoms) if hasattr(g,'geoms') else [g]
            for p in polys:
                if p.geom_type != 'Polygon' or p.is_empty or len(p.exterior.coords) < 3: continue
                draw.polygon(pixel(p.exterior.coords), fill=color)
                for ring in p.interiors: draw.polygon(pixel(ring.coords), fill='white')
        paint(geom, '#236d93')
        opened, closed = morph(geom,.8)
        paint(geom.difference(opened), '#e06a25')
        draw.text((ox+24,oy+436), 'Blue: section; orange: 0.8 mm opening loss', fill='#455a64', font=font)
    im.save(QA/'geometry-layer-sections.png')


def sections(tri):
    zmin, zmax = float(tri[:,:,2].min()), float(tri[:,:,2].max())
    levels = np.arange(zmin+.1, zmax, .2)
    vertices_z = np.unique(tri[:,:,2])
    rows = []; geoms = []
    for requested_z in levels:
        actual_z = float(requested_z)
        nudged = bool(np.min(np.abs(vertices_z-actual_z)) < EPS)
        if nudged: actual_z += 1e-5
        geom, info = section(tri, actual_z)
        row = {'requested_z_mm': round(float(requested_z), 6), 'actual_z_mm': actual_z, 'nudged_off_vertex_plane': nudged, **info}
        if geom is not None and not geom.is_empty:
            for diameter in [.6, .8, 1., 1.2]:
                opened, closed = morph(geom, diameter)
                loss = geom.difference(opened).area
                fill = closed.difference(geom).area
                key = f'{diameter:.1f}'
                row[f'opening_{key}_loss_mm2'] = float(loss)
                row[f'closing_{key}_fill_mm2'] = float(fill)
                row[f'opening_{key}_loss_percent'] = float(100*loss/geom.area)
                row[f'opening_{key}_empty'] = bool(opened.is_empty)
        rows.append(row); geoms.append(geom)
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (QA/'geometry-layer-sections.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)
    draw_sections(rows, geoms)
    controls = morphology_controls()
    bad = [r for r in rows if not r.get('valid', False)]
    summary = {
        'layer_height_mm': .2, 'planes': 'Layer centres z=0.1+0.2*i mm, below max model z; vertex coincidences nudged +0.00001 mm and individually logged.',
        'section_count': len(rows), 'first_z_mm': rows[0]['actual_z_mm'], 'last_z_mm': rows[-1]['actual_z_mm'],
        'valid_section_count': len(rows)-len(bad), 'invalid_sections': bad,
        'area_range_mm2': [min(r.get('area_mm2',0) for r in rows),max(r.get('area_mm2',0) for r in rows)],
        'component_histogram': dict(Counter(r.get('components') for r in rows)),
        'hole_histogram': dict(Counter(r.get('holes') for r in rows)),
        'section_area_integrated_volume_mm3': float(sum(r.get('area_mm2',0) for r in rows)*.2),
        'morphology_controls': controls,
        'method': 'Raw triangle-plane intersections; snapped endpoint keys at 1e-6mm. Require graph degree exactly 2, no duplicate segments, simple valid loops and no crossing/touching loop boundaries. Nested rings combined by parity. No contour repair or union to conceal raw defects.',
        'morphology_method': 'For every actual polygon section: erosion/dilation opening and dilation/erosion closing at diameters 0.6,0.8,1.0,1.2mm using GEOS mitre joins, and original-minus-opened / closed-minus-original areas. Mitre joins reduce corner-rounding artefacts; all layer data retained in CSV.',
        'thin_wall_interpretation': 'Opening loss is a screening observation of narrow protrusions/tips, not a universal minimum 3D wall-thickness measurement. Closing fill screens narrow void/recess widths. Small roof apex sections may vanish. This cannot establish layer adhesion, material strength, nozzle recovery, supports, or measured as-built wall thickness.',
        'passed_contour_legality': not bad,
        'morphology_summary': {}
    }
    for diameter in [.6,.8,1.,1.2]:
        key = f'{diameter:.1f}'
        relevant = [r for r in rows if f'opening_{key}_loss_mm2' in r]
        losses = sorted(relevant,key=lambda r:r[f'opening_{key}_loss_mm2'],reverse=True)
        summary['morphology_summary'][key] = {
            'layers_with_loss_above_0_01_mm2': sum(r[f'opening_{key}_loss_mm2']>.01 for r in relevant),
            'layers_opened_empty': [r['requested_z_mm'] for r in relevant if r[f'opening_{key}_empty']],
            'maximum_loss_mm2': max(r[f'opening_{key}_loss_mm2'] for r in relevant),
            'maximum_loss_percent': max(r[f'opening_{key}_loss_percent'] for r in relevant),
            'maximum_closing_fill_mm2': max(r[f'closing_{key}_fill_mm2'] for r in relevant),
            'top_loss_layers': [{'z_mm':r['requested_z_mm'],'loss_mm2':r[f'opening_{key}_loss_mm2'],'loss_percent':r[f'opening_{key}_loss_percent']} for r in losses[:8]]
        }
    return summary


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--stl', type=Path, default=ROOT/'models/v1/model.stl'); args=parser.parse_args()
    started=time.time(); QA.mkdir(exist_ok=True)
    tri, vertices, faces, stored_normals=raw_stl(args.stl)
    topo, normals=topology(tri,vertices,faces,stored_normals)
    jwrite(QA/'geometry-topology.json', {'model_sha256':sha(args.stl),**topo})
    collision=collisions(tri,vertices,faces,normals)
    jwrite(QA/'geometry-collisions.json', {'model_sha256':sha(args.stl),**collision})
    exact=exact_collisions(tri,vertices,faces)
    jwrite(QA/'geometry-exact-collisions.json', {'model_sha256':sha(args.stl),**exact})
    layer=sections(tri)
    volume_approx=layer['section_area_integrated_volume_mm3']; volume=topo['signed_volume_mm3']
    layer['section_volume_vs_mesh_relative_difference_percent']=100*(volume_approx-volume)/volume
    report={
        'model_relative_path': args.stl.resolve().relative_to(ROOT).as_posix(), 'model_sha256':sha(args.stl),
        'parameters_sha256':sha(ROOT/'parameters.json'), 'source_sha256':sha(ROOT/'source/build_model.py'),
        'script_sha256':sha(Path(__file__)), 'versions': {'numpy':np.__version__,'shapely':shapely.__version__},
        'distance_tolerance_mm':EPS,'topology':topo,'triangle_collisions':collision,'exact_triangle_collisions':exact,'sections_and_thin_feature_screening':layer,
        'elapsed_seconds':round(time.time()-started,3),
        'overall_assessment':'Numerical geometry checks and limited manufacturing screens only; NOT a complete quality or printability pass. Thin-feature losses are retained and require slicer/independent review. No physical print performed.',
        'remaining_limits':[
            'Self-intersections receive exact integer/rational refinement on quantized STL coordinates, with a separately implemented floating cross-check and synthetic controls. Custom code is not formally verified.',
            'Horizontal 0.2mm sections can miss sub-layer or near-vertical details. Morphological screening is not a global 3D local-thickness certificate.',
            'No printer, filament, adhesion, strength, support removal or physical-print validation in this script.',
            'Support accessibility and real PrusaSlicer validation are separate checks, not implied by manifold topology.',
            'This QA does not establish architectural fidelity, measured scale, unseen rear openings, or omitted northeast corner geometry.'
        ]
    }
    jwrite(QA/'geometry-report.json',report)
    md = f'''# Geometry QA evidence\n\nModel SHA-256: `{report['model_sha256']}`\n\nRaw binary STL: {topo['raw_triangle_count']} triangles; {topo['exact_coordinate_welded_vertices']} exact-coordinate vertices. Topology checks: {'PASS' if topo['passed'] else 'FAIL'}; {topo['bad_edge_count']} bad edges; {topo['bad_vertex_link_count']} bad vertex links; {len(topo['degenerate_triangles'])} degenerate faces; {topo['face_connected_components']} face-connected component(s). Signed volume {volume:.6f} mm³.\n\nExhaustive pair screening: {collision['all_unordered_triangle_pairs']} pairs, {collision['all_aabb_candidate_pairs_refined']} inclusive-AABB candidates refined, {collision['unexpected_pair_count']} unexpected intersections. This is floating-point numerical refinement, not an exact-arithmetic proof. Controls: {'PASS' if all(c['passed'] for c in collision['controls']) else 'FAIL'}.\n\nAll {layer['section_count']} horizontal layer-centre planes at 0.2 mm spacing: {layer['valid_section_count']} legal contours; component histogram {layer['component_histogram']}; hole histogram {layer['hole_histogram']}. Section-integrated volume differs from mesh volume by {layer['section_volume_vs_mesh_relative_difference_percent']:.6f}%. Raw contour graphs are checked before polygon construction and are not repaired.\n\nActual section polygons were opened and closed at 0.6, 0.8, 1.0 and 1.2 mm diameters. At 0.8 mm, maximum opening loss is {layer['morphology_summary']['0.8']['maximum_loss_mm2']:.6f} mm² ({layer['morphology_summary']['0.8']['maximum_loss_percent']:.6f}% maximum per-section loss); {layer['morphology_summary']['0.8']['layers_with_loss_above_0_01_mm2']} sections lose more than 0.01 mm². Losses are observations of narrow details/tips; they are not hidden or treated as an unconditional pass. Opening/closing controls: {'PASS' if layer['morphology_controls']['passed'] else 'FAIL'}, including a deliberately 0.4 mm finger and 0.4 mm slot, and a retained 2 mm finger.\n\nSee `geometry-report.json` for all pair results, controls, tolerances, limitations and morphology summaries, `geometry-layer-sections.csv` for every measured plane, and `geometry-layer-sections.png` for selected polygon sections.\n\nThis does **not** establish complete quality, support removability, printer readiness or physical printing success. The separate slicer/support checks and independent review remain necessary.\n'''
    (QA/'geometry-summary.md').write_text(md,encoding='utf8')
    print(json.dumps({'sha256':report['model_sha256'],'topology_passed':topo['passed'],'collision_unexpected_pairs':collision['unexpected_pair_count'],'collision_candidate_count':collision['all_aabb_candidate_pairs_refined'],'legal_sections':layer['valid_section_count'],'section_count':layer['section_count'],'morphology_0_8':layer['morphology_summary']['0.8'],'elapsed_seconds':report['elapsed_seconds']},indent=2))


if __name__ == '__main__': main()
