"""Independent read-only audit of original binary STL coordinates.

Does not import candidate QA. Exact predicates are reused from our independently
written prior review, with their positive/negative controls rerun here.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib, itertools, json, math, struct, time
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64
import exact_predicates as ex

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'candidate'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o): p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def load(p):
    data=p.read_bytes(); n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n
    raw=[tuple(tuple(struct.unpack_from('<3f',data,84+50*i+12+12*k)) for k in range(3)) for i in range(n)]
    den=max(v.as_integer_ratio()[1] for t in raw for p in t for v in p)
    grid=[tuple(tuple(int(F(v)*den) for v in p) for p in t) for t in raw]
    return raw,grid,den
def audit(p):
    start=time.time(); raw,tris,den=load(p); ns=[ex.normal(t) for t in tris]
    lo=np.array([[min(p[k] for p in t) for k in range(3)] for t in tris],dtype=np.int64)
    hi=np.array([[max(p[k] for p in t) for k in range(3)] for t in tris],dtype=np.int64)
    classes=Counter(); bad=[]
    for i,t in enumerate(tris):
        js=np.flatnonzero(np.all(hi[i]>=lo[i+1:],axis=1)&np.all(hi[i+1:]>=lo[i],axis=1))+i+1
        for jj in js:
            j=int(jj);kind,detail=ex.pair(t,tris[j],ns[i],ns[j]);classes[kind]+=1
            if kind=='unexpected_intersection': bad.append({'faces':[i,j],**detail})
    m=trimesh.load_mesh(p,process=True)
    out={'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,
         'coordinate_grid_denominator':den,'exact_topology':ex.topology(tris,den),
         'all_pair_count':len(tris)*(len(tris)-1)//2,'exact_AABB_candidate_count':sum(classes.values()),
         'exact_pair_classifications':dict(classes),'unexpected_intersections':bad,
         'trimesh_crosscheck':{'bounds_mm':m.bounds.tolist(),'volume_mm3':float(m.volume),
          'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),
          'components':len(m.split(only_watertight=False))},'runtime_seconds':time.time()-start}
    write(HERE/(p.stem+'-exact.json'),out)
    print(p.name,'exact_candidates',sum(classes.values()),'unexpected',len(bad),flush=True)
    return out,raw,m
def tri_counter(a):
    return Counter(tuple(sorted(tuple(float(v) for v in p) for p in t)) for t in np.asarray(a))
def normalized_counter(a,tol=1e-5):
    return Counter(tuple(sorted(tuple(int(round(float(v)/tol)) for v in p) for p in t)) for t in np.asarray(a))
def axis_hits(raw,origin,axis):
    """Exact line/triangle plane intersections. No ray determinant tolerance.

    Project onto plane perpendicular to axis; exact 2D containment is sufficient
    for the convex triangle. Parallel faces are omitted; all distinct intersected
    surface axis coordinates are retained, then nearest two directions chosen.
    """
    o=tuple(F(v) for v in origin); keep=[k for k in range(3) if k!=axis]; hits=set()
    for tr in raw:
        t=tuple(tuple(F(v) for v in p) for p in tr); n=ex.normal(t)
        if not n[axis]: continue
        p2=tuple(o[k] for k in keep);t2=[tuple(p[k] for k in keep) for p in t]
        if not ex.inside2(p2,t2): continue
        c=(ex.dot(n,t[0])-sum(n[k]*o[k] for k in keep))/n[axis]
        hits.add(c)
    return sorted(hits)
def cavity(raw,origin,axis):
    hs=axis_hits(raw,origin,axis); val=F(origin[axis])
    low=max(v for v in hs if v<val); high=min(v for v in hs if v>val)
    return {'low_mm':float(low),'high_mm':float(high),'width_mm':float(high-low),
            'low_exact':str(low),'high_exact':str(high)}
def oblique_caliper(raw,origin,direction):
    o=tuple(F(v) for v in origin);d=tuple(F(v) for v in direction);hits=set()
    for tr in raw:
        t=tuple(tuple(F(v) for v in p) for p in tr);n=ex.normal(t);den=ex.dot(n,d)
        if not den:continue
        u=ex.dot(n,ex.sub(t[0],o))/den;pt=tuple(o[k]+u*d[k] for k in range(3))
        drop=max(range(3),key=lambda k:abs(n[k]));keep=[k for k in range(3) if k!=drop]
        if ex.inside2(tuple(pt[k] for k in keep),[tuple(p[k] for k in keep) for p in t]):hits.add(u)
    lo=max(v for v in hits if v<0);hi=min(v for v in hits if v>0)
    return {'width_mm':float(hi-lo)*math.sqrt(float(ex.dot(d,d))),
        'origin_mm':[float(v) for v in o],'direction':[float(v) for v in d],
        'low_line_parameter_exact':str(lo),'high_line_parameter_exact':str(hi)}
def main():
    start=time.time(); asm=json.loads((ROOT/'assembly.json').read_text('utf-8'))
    names=['main_body','roof','column','mast_brace_frame']; res={};raws={};meshes={}
    for name in names:
        for mode in ['assembly','print']:
            key=name+'-'+mode;res[key],raws[key],meshes[key]=audit(ROOT/'parts'/(key+'.stl'))
    overview,oraw,omesh=audit(ROOT/'model.stl')
    # A proper rotation plus a translation must relate the two STLs. Compute
    # directly from raw triangles, not by invoking candidate orient().
    transforms=[]
    for name in names:
        a=np.asarray(raws[name+'-assembly']);p=np.asarray(raws[name+'-print'])
        rot=np.eye(3)
        if name=='roof': rot=np.diag([1,-1,-1])
        if name in ['column','mast_brace_frame']: rot=np.array([[0,0,-1],[0,1,0],[1,0,0]])
        moved=a@rot.T; translation=-moved.reshape(-1,3).min(axis=0); expected=moved+translation
        maxdelta=float(np.max(np.abs(expected-p)))
        transforms.append({'part':name,'proper_rotation_matrix':rot.tolist(),'determinant':float(np.linalg.det(rot)),
          'translation_mm':translation.tolist(),'same_triangle_order':len(a)==len(p),
          'max_coordinate_difference_mm':maxdelta,'equal_after_binary32_quantization':bool(np.array_equal(expected.astype(np.float32),p.astype(np.float32))),
          'within_1e-5_mm':maxdelta<=1e-5})
    placements=asm['placements']; transformed=[];solids=[];inventory=Counter()
    for p in placements:
        inventory[p['part']]+=1; key=p['part']+'-assembly';t=np.array(p['translation_mm'],float)
        transformed.extend((np.array(raws[key])+t).astype(np.float32))
        m=meshes[key];s=Manifold(Mesh64(np.asarray(m.vertices,np.float64),np.asarray(m.faces,np.uint64)))
        solids.append((p,s.translate(t.tolist())))
    exact_equal=tri_counter(transformed)==tri_counter(oraw)
    expected=np.asarray(transformed);observed=np.asarray(oraw)
    overview_match={'expected_inventory':{'main_body':1,'roof':1,'column':10,'mast_brace_frame':10},
       'measured_inventory':dict(inventory),'placements':placements,'piece_count':len(placements),
       'inventory_matches':inventory==Counter({'main_body':1,'roof':1,'column':10,'mast_brace_frame':10}),
       'triangles_expected':len(expected),'triangles_observed':len(observed),
       'exact_binary32_triangle_multiset_equal':exact_equal,
       'same_order_max_coordinate_difference_mm':float(np.max(np.abs(expected-observed))),
       'overview_sha256':sha(ROOT/'model.stl'),
       'overview_not_single_print_piece':True}
    pairs=[]
    for (pa,a),(pb,b) in itertools.combinations(solids,2):
        inter=a^b
        pairs.append({'a':f"{pa['part']}#{pa['copy']}",'b':f"{pb['part']}#{pb['copy']}",
                      'intersection_volume_mm3':float(inter.volume()),'intersection_status':str(inter.status()),
                      'intersection_triangle_count':inter.num_tri()})
    collision={'piece_count':len(solids),'pair_count':len(pairs),'pairs':pairs,
       'maximum_intersection_volume_mm3':max(p['intersection_volume_mm3'] for p in pairs),
       'nonempty_intersection_pairs':[p for p in pairs if p['intersection_triangle_count']>0],
       'method':'Manifold3D Boolean intersection of independently loaded unmodified STL coordinates; exact whole-overview triangle audit separately checks surface contacts. No intersecting material is accepted solely by a loose volume threshold.'}
    slots=[]
    for x in sorted(p['translation_mm'][0] for p in placements if p['part']=='column'):
        requests=[('body','main_body-assembly',15,24.5,2.8,4.4),('roof_lower','roof-assembly',15,34.1,2.8,4.4)]
        requests += [('roof_upper','roof-assembly',y,37,2.2,3.4) for y in [-24,15,27]]
        for typ,key,y,z,pegx,pegy in requests:
            cx=cavity(raws[key],[x,y,z],0);cy=cavity(raws[key],[x,y,z],1)
            # Peg widths independently taken at the mating key's middle height.
            peg='column-assembly' if typ!='roof_upper' else 'mast_brace_frame-assembly'
            pz=24.5 if typ=='body' else 34.1 if typ=='roof_lower' else 37
            kx=cavity(raws[peg],[0,y,pz],0);ky=cavity(raws[peg],[0,y,pz],1)
            zz=axis_hits(raws[key],[x,y,z],2);kz=axis_hits(raws[peg],[0,y,z],2)
            if typ=='body':zgap=min(kz)-max(v for v in zz if v<z)
            elif typ=='roof_lower':zgap=min(v for v in zz if v>z)-max(kz)
            else:zgap=min(kz)-max(v for v in zz if v<z)
            slots.append({'type':typ,'x_mm':x,'y_mm':y,'z_probe_mm':z,'x_cavity':cx,'y_cavity':cy,
              'key_x_mm':kx['width_mm'],'key_y_mm':ky['width_mm'],
              'actual_total_clearance_x_mm':cx['width_mm']-kx['width_mm'],
              'actual_total_clearance_y_mm':cy['width_mm']-ky['width_mm'],
              'key_tip_to_blind_end_gap_mm':float(zgap),
              'left_clearance_mm':kx['low_mm']+x-cx['low_mm'],
              'right_clearance_mm':cx['high_mm']-kx['high_mm']-x,
              'front_clearance_mm':ky['low_mm']-cy['low_mm'],
              'rear_clearance_mm':cy['high_mm']-ky['high_mm'],
              'nominal_total_clearance_mm':.4})
    # End faces independently located along centreline, not source parameters.
    zbody=axis_hits(raws['main_body-assembly'],[81,15,24.5],2)
    zroof=axis_hits(raws['roof-assembly'],[81,15,34.1],2)
    roof_shoulder=axis_hits(raws['roof-assembly'],[81,F('12.4'),35.5],2)
    zcol=axis_hits(raws['column-assembly'],[0,15,30],2)
    zframe=axis_hits(raws['mast_brace_frame-assembly'],[0,15,37],2)
    # The column's centreline does not intersect shoulder surfaces. A point near
    # y=12.4 (outside the key, inside shoulder) locates the two seating planes.
    shoulder=axis_hits(raws['column-assembly'],[0,F('12.4'),30],2)
    frame_shoulder=axis_hits(raws['mast_brace_frame-assembly'],[0,F('13'),38],2)
    surfaces={'body_axis_z_surfaces_mm':[float(v) for v in zbody],
      'roof_axis_z_surfaces_mm':[float(v) for v in zroof],
      'roof_shoulder_z_surfaces_mm':[float(v) for v in roof_shoulder],
      'column_axis_z_surfaces_mm':[float(v) for v in zcol],
      'column_shoulder_z_surfaces_mm':[float(v) for v in shoulder],
      'frame_axis_z_surfaces_mm':[float(v) for v in zframe],
      'frame_shoulder_z_surfaces_mm':[float(v) for v in frame_shoulder]}
    bodyfloor=max(v for v in zbody if v<24.5);roofceil=min(v for v in zroof if v>34.1)
    rooftopfloor=max(v for v in zroof if v<37);underside=min(roof_shoulder); rooftop=max(roof_shoulder)
    clearances={'column_body_floor_gap_mm':float(min(zcol)-bodyfloor),
       'column_roof_ceiling_gap_mm':float(roofceil-max(zcol)),
       'column_body_shoulder_gap_mm':float(min(shoulder)-26),
       'column_roof_shoulder_gap_mm':float(underside-max(shoulder)),
       'frame_roof_socket_floor_gap_mm':float(min(zframe)-rooftopfloor),
       'frame_roof_shoulder_gap_mm':float(min(frame_shoulder)-rooftop),
       'roof_web_between_opposite_sockets_mm':float(rooftopfloor-roofceil)}
    # Selected physically relevant flat/brace widths. These are locally measured
    # calipers, not a claim of exhaustive global minimum thickness.
    features={'column_x_mm':cavity(raws['column-assembly'],[0,15,28],0)['width_mm'],
       'frame_x_mm':cavity(raws['mast_brace_frame-assembly'],[0,15,52],0)['width_mm'],
       'mast_y_mm':cavity(raws['mast_brace_frame-assembly'],[0,15,52],1)['width_mm'],
       'roof_field_z_mm':cavity(raws['roof-assembly'],[0,0,36],2)['width_mm']}
    features['long_brace_perpendicular']=oblique_caliper(raws['mast_brace_frame-assembly'],[0,F('-4.5'),F('44.5')],[0,F('-11.8'),39])
    features['short_brace_perpendicular']=oblique_caliper(raws['mast_brace_frame-assembly'],[0,21,F('44.5')],[0,F('-11.8'),-12])
    controls=ex.controls()
    out={'commit':'3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a',
      'scope':'8 unique assembly/print STLs independently audited, plus the 22-piece overview; no candidate QA imported, no repairs, no original files written.',
      'exact_algorithm_sha256':sha(HERE/'exact_predicates.py'),'runner_sha256':sha(Path(__file__)),
      'parts':res,'overview':overview,'proper_print_transform_checks':transforms,
      'assembled_overview_match':overview_match,'collision_check':collision,
      'socket_measurement_method':'Exact line-plane intersection and projected point-in-triangle predicates on binary32 STL coordinates; 50 independent sockets, actual key widths, no ray tolerance.',
      'socket_count':len(slots),'socket_measurements':slots,'interface_z_surfaces':surfaces,
      'interface_gap_measurements_mm':clearances,'selected_feature_calipers_mm':features,
      'minimum_measured_total_xy_clearance_mm':min(min(r['actual_total_clearance_x_mm'],r['actual_total_clearance_y_mm']) for r in slots),
      'minimum_measured_one_side_xy_clearance_mm':min(min(r[k] for k in ['left_clearance_mm','right_clearance_mm','front_clearance_mm','rear_clearance_mm']) for r in slots),
      'controls':controls,'all_controls_pass':all(c['ok'] for c in controls.values()),
      'all_original_input_hashes_unchanged':all(sha(ROOT/r['file'])==r['sha256'] for r in list(res.values())+[overview]),
      'runtime_seconds':time.time()-start,
      'limitations':['No physical print, fit, glue strength or handling test.',
       'Numerical clearance does not certify printer dimensional accuracy; use dry fit, cleanup and gap-filling adhesive.',
       'The 22-component overview is for assembly only, not a single connected print STL.',
       'Main body true exterior overhangs still need support; support and G-code reviewed separately.',
       'Selected interface and thickness calipers are not an exhaustive arbitrary-direction minimum-wall proof.']}
    write(HERE/'geometry-summary.json',out)
    print(json.dumps({'parts':len(res),'overview_match':overview_match,'max_collision_volume':collision['maximum_intersection_volume_mm3'],
      'slots':len(slots),'clearances':clearances,'controls':out['all_controls_pass']},indent=2))
if __name__=='__main__':main()
