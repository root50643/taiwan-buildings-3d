"""Independent raw binary-STL topology audit. No repair/welding libraries."""
from pathlib import Path
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import json
import math
import platform
import struct

HERE = Path(__file__).resolve().parent
SOURCE = Path(r"<HISTORICAL_OTHER_MODEL_ROOT>")

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def audit(path):
    data=path.read_bytes()
    n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n, 'STL size inconsistent'
    rows=[struct.unpack_from('<12fH',data,84+i*50) for i in range(n)]
    normals=[r[:3] for r in rows]
    triangles=[tuple(tuple(r[3+3*j:6+3*j]) for j in range(3)) for r in rows]
    assert all(math.isfinite(x) for r in rows for x in r[:12])
    positions=sorted(set(p for t in triangles for p in t))
    ix={p:i for i,p in enumerate(positions)}
    faces=[tuple(ix[p] for p in t) for t in triangles]
    scale=max(float(c).as_integer_ratio()[1] for p in positions for c in p)
    integer=[tuple(int(Fraction(c)*scale) for c in p) for p in positions]
    incidences=defaultdict(list)
    links=defaultdict(list)
    face_neighbors=defaultdict(set)
    for fi,f in enumerate(faces):
        for u,v in zip(f,f[1:]+f[:1]):
            incidences[tuple(sorted((u,v)))].append((fi,u,v))
        for k,v in enumerate(f): links[v].append((f[(k+1)%3],f[(k+2)%3]))
    for edge,rows_ in incidences.items():
        for i in range(len(rows_)):
            for j in range(i):
                face_neighbors[rows_[i][0]].add(rows_[j][0]); face_neighbors[rows_[j][0]].add(rows_[i][0])
    components=[]; unseen=set(range(n))
    while unseen:
        todo=[next(iter(unseen))]; found=set()
        while todo:
            i=todo.pop()
            if i not in found: found.add(i); todo.extend(face_neighbors[i]-found)
        unseen-=found; components.append(sorted(found))
    badlinks=[]
    for vi,edges in links.items():
        adj=defaultdict(list)
        for u,v in edges: adj[u].append(v); adj[v].append(u)
        seen=set(); todo=[next(iter(adj))]
        while todo:
            i=todo.pop()
            if i not in seen: seen.add(i); todo.extend(adj[i])
        if len(seen)!=len(adj) or any(len(v)!=2 for v in adj.values()): badlinks.append(vi)
    cross_int=[cross(sub(integer[f[1]],integer[f[0]]),sub(integer[f[2]],integer[f[0]])) for f in faces]
    degenerate=[i for i,c in enumerate(cross_int) if c==(0,0,0)]
    volumes=[]
    for component in components:
        determinant=sum(dot(integer[faces[i][0]],cross(integer[faces[i][1]],integer[faces[i][2]])) for i in component)
        volumes.append(Fraction(determinant,6*scale**3))
    normal_lengths=[math.sqrt(dot(v,v)) for v in normals]
    deviations=[]; cosines=[]
    for normal,c in zip(normals,cross_int):
        length=math.sqrt(dot(c,c)); normalized=[v/length for v in c]
        deviations.append(max(abs(a-b) for a,b in zip(normal,normalized)))
        cosines.append(dot(normal,c)/(math.sqrt(dot(normal,normal))*length))
    bad_edges=[list(e) for e,v in incidences.items() if len(v)!=2]
    bad_orient=[list(e) for e,v in incidences.items() if len(v)==2 and v[0][1:]!=v[1][1:][::-1]]
    duplicate_groups=[list(f) for f,c in Counter(tuple(sorted(f)) for f in faces).items() if c>1]
    euler=len(positions)-len(incidences)+n
    checks={
      'binary_length_exact':True,'coordinates_and_saved_normals_finite':True,
      'zero_exact_degenerate_triangles':not degenerate,'zero_duplicate_triangles':not duplicate_groups,
      'every_raw_exact_coordinate_edge_two_faces':not bad_edges,
      'every_raw_vertex_link_one_cycle_multigraph':not badlinks,
      'opposite_directed_incidence_on_each_edge':not bad_orient,
      'one_edge_connected_surface_component':len(components)==1,
      'every_component_positive_exact_signed_volume':all(v>0 for v in volumes),
      'saved_normals_unit_within_1e_5':max(abs(x-1) for x in normal_lengths)<1e-5,
      'saved_normals_match_computed_direction_within_1e_5':max(deviations)<1e-5,
    }
    return {'input':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),
      'method':'Independent struct parser; exact stored-coordinate identity only; integer cross products, edge incidence and multigraph vertex links; exact rational signed volume; no repair, proximity welding, mesh library or source validator.',
      'all_listed_checks_passed':all(checks.values()),'checks':checks,
      'faces':n,'vertices':len(positions),'edges':len(incidences),'surface_components':len(components),
      'component_face_counts':list(map(len,components)),
      'component_exact_signed_volume_rationals':[str(v) for v in volumes],
      'component_signed_volumes_mm3':[float(v) for v in volumes],
      'integer_units_per_mm':scale,'euler_characteristic':euler,
      'orientable_genus_if_one_closed_component':(2-euler)//2 if len(components)==1 and not bad_edges and not badlinks and not bad_orient else None,
      'bounds_mm':[[min(p[k] for p in positions) for k in range(3)],[max(p[k] for p in positions) for k in range(3)]],
      'dimensions_mm':[max(p[k] for p in positions)-min(p[k] for p in positions) for k in range(3)],
      'max_saved_normal_length_error':max(abs(x-1) for x in normal_lengths),
      'max_saved_normal_component_error':max(deviations),'minimum_saved_normal_direction_cosine':min(cosines),
      'non_two_face_edges':bad_edges,'bad_vertex_links':badlinks,'inconsistent_directed_edges':bad_orient,
      'exact_degenerate_faces':degenerate,'duplicate_triangles':duplicate_groups,
      'nonzero_stl_attribute_count':sum(r[-1]!=0 for r in rows),
      'limitations':['Does not prove self-intersection freedom by itself; separate exact contact check addresses that property.',
        'Positive volume and manifold topology do not prove a printable minimum feature, removable support, slicer success or physical print.']}

if __name__=='__main__':
    report={'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':platform.python_version(),
      'final_r2':audit(SOURCE/'model.stl'),
      'e45_preserved':audit(SOURCE/'qa/risk-followup-e45f8d6/input-original.stl'),
      'formal_slicer_run':False,'physical_print_test':False}
    (HERE/'independent-raw-topology.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:{p:report[k][p] for p in ['sha256','all_listed_checks_passed','faces','vertices','edges','surface_components','component_signed_volumes_mm3','euler_characteristic']} for k in ['final_r2','e45_preserved']},indent=2))
