"""Re-runnable, millimetre-scale mesh / assembly QA. No mesh repair is performed.

Input schema and limitations: see README.md. Raw flags are never discarded.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, math, platform, time, shutil, copy, os
from pathlib import Path
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon
from rtree import index as rindex

EPS = 1e-6

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def json_write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def plain(v):
    if isinstance(v, np.ndarray): return v.tolist()
    if isinstance(v, np.generic): return v.item()
    return v

def tree_for(bounds):
    prop=rindex.Property(); prop.dimension=3
    return rindex.Index(((i,tuple(b),None) for i,b in enumerate(bounds)), properties=prop)

def cut_interval(tri, d, line):
    pts=[]
    for i in range(3):
        j=(i+1)%3
        if abs(d[i])<=EPS: pts.append(tri[i])
        if d[i]*d[j]<-EPS*EPS:
            pts.append(tri[i]+(tri[j]-tri[i])*d[i]/(d[i]-d[j]))
    if not pts: return None
    q=np.asarray(pts)@line
    return float(q.min()),float(q.max())

def triangle_contacts(mesh):
    """All AABB candidate pairs, exact plane cuts / planar polygon intersections.

    Includes shared-vertex pairs; permits only the shared topological simplex.
    No random or reduced face sample, no spatial pair cap.
    """
    ts=mesh.triangles; fn=mesh.face_normals; faces=mesh.faces
    bs=np.column_stack((ts.min(axis=1)-EPS,ts.max(axis=1)+EPS)); tree=tree_for(bs)
    counts={'all_faces':len(ts),'aabb_pairs':0,'plane_rejected':0,'coplanar_pairs':0,
            'expected_topological_contacts':0,'nonadjacent_point_contacts':0,
            'nonadjacent_line_contacts':0,'proper_intersections':0,'coplanar_overlap':0}
    records=[]
    for i,a in enumerate(ts):
        for j in tree.intersection(tuple(bs[i])):
            if j<=i: continue
            counts['aabb_pairs']+=1
            b=ts[j]; na=fn[i]; nb=fn[j]
            da=(a-b[0])@nb; db=(b-a[0])@na
            if da.min()>EPS or da.max()<-EPS or db.min()>EPS or db.max()<-EPS:
                counts['plane_rejected']+=1; continue
            common=np.intersect1d(faces[i],faces[j]); ncommon=len(common)
            line=np.cross(na,nb); llen=np.linalg.norm(line)
            kind=None; measure=0.
            if llen<EPS:
                if np.max(abs(da))>EPS: continue
                counts['coplanar_pairs']+=1
                drop=int(np.argmax(abs(na)))
                p=Polygon(np.delete(a,drop,axis=1)); q=Polygon(np.delete(b,drop,axis=1))
                geom=p.intersection(q)
                if geom.is_empty: continue
                measure=float(geom.area)
                if measure>EPS*EPS:
                    kind='coplanar_overlap'
                elif ncommon:
                    # A convex triangle pair cannot meet beyond a shared edge
                    # without positive overlap area; a shared vertex may hide a
                    # non-topological line and is checked explicitly.
                    if ncommon==1 and geom.length>EPS:
                        kind='nonadjacent_line_contacts'; measure=float(geom.length)
                    else: counts['expected_topological_contacts']+=1; continue
                elif geom.length>EPS:
                    kind='nonadjacent_line_contacts';measure=float(geom.length)
                else: kind='nonadjacent_point_contacts'
            else:
                line/=llen
                aa=cut_interval(a,da,line); bb=cut_interval(b,db,line)
                if aa is None or bb is None: continue
                low=max(aa[0],bb[0]); high=min(aa[1],bb[1])
                if high<low-EPS: continue
                measure=max(0.,high-low)
                if ncommon>=2:
                    counts['expected_topological_contacts']+=1;continue
                if measure<=EPS:
                    if ncommon: counts['expected_topological_contacts']+=1;continue
                    kind='nonadjacent_point_contacts'
                elif ncommon==1: kind='proper_intersections'
                else:
                    # A line lying wholly on one triangle edge is self-contact;
                    # an interval interior to both triangles is crossing.
                    edge_a=any(abs(da[k])<=EPS and abs(da[(k+1)%3])<=EPS for k in range(3))
                    edge_b=any(abs(db[k])<=EPS and abs(db[(k+1)%3])<=EPS for k in range(3))
                    kind='nonadjacent_line_contacts' if edge_a or edge_b else 'proper_intersections'
            if kind:
                counts[kind]+=1
                records.append({'faces':[int(i),int(j)],'kind':kind,'measure_mm_or_mm2':measure,
                                'shared_vertices':int(ncommon)})
    counts['pass_no_non_topological_contact']=len(records)==0
    return {'method':'all triangle AABB pairs; plane-cut intervals + coplanar Shapely intersection; epsilon 1e-6 mm',
            'counts':counts,'records':records}

def section_analysis(mesh, step, extra, out, part_id):
    lo,hi=mesh.bounds[:,2]; heights=np.arange(lo+step/2, hi, step)
    heights=np.unique(np.r_[heights,[h for h in extra if lo+EPS<h<hi-EPS]])
    paths=mesh.section_multiplane([0,0,0],[0,0,1],heights)
    records=[]; previous=None; unsupported=[]
    for h,p in zip(heights,paths):
        if p is None: records.append({'z_mm':float(h),'area_mm2':0,'loops':0});previous=None;continue
        polys=list(p.polygons_full)
        g=shapely.union_all(polys)
        opened=g.buffer(-0.4,join_style=2).buffer(0.4,join_style=2)
        thin=g.difference(opened)
        # Opening is a screening signal. Sharp taper tips also survive here.
        rec={'z_mm':float(h),'area_mm2':float(g.area),'loops':len(polys),
             'opening_0p8mm_residual_area_mm2':float(thin.area)}
        if previous is not None:
            dz=float(h-previous[0]); outward=g.difference(previous[1].buffer(dz+0.01))
            rec['area_beyond_previous_45deg_allowance_mm2']=float(outward.area)
            if outward.area>0.05: unsupported.append({'z_mm':float(h),'area_mm2':float(outward.area)})
        records.append(rec);previous=(h,g)
    json_write(out/f'{part_id}_sections.json',records)
    # Record a compact, independently inspectable vector section subset.
    if paths:
        chosen=sorted(set([0,len(paths)//4,len(paths)//2,3*len(paths)//4,len(paths)-1]))
        drawings=[]
        for k in chosen:
            p=paths[k]
            if p is None: continue
            for line in p.discrete:
                coords=' '.join(f'{x:.3f},{-y:.3f}' for x,y in line)
                drawings.append(f'<polyline points="{coords}" fill="none" stroke="black" stroke-width="0.12"/>')
        bounds=mesh.bounds;v=f'{bounds[0,0]-1} {-bounds[1,1]-1} {mesh.extents[0]+2} {mesh.extents[1]+2}'
        (out/f'{part_id}_section_overlay.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{v}">'+''.join(drawings)+'</svg>',encoding='utf-8')
    return {'count':len(records),'step_mm':step,'detail_file':f'{part_id}_sections.json',
            'max_area_mm2':max((r['area_mm2'] for r in records),default=0.),
            'nonempty_layers':sum(r['area_mm2']>0 for r in records),
            'raw_45deg_outward_layer_flags':unsupported,
            'raw_opening_0p8mm_flags':sum(r.get('opening_0p8mm_residual_area_mm2',0)>0.05 for r in records),
            'limitations':'0.8 mm morphological opening is a screening signal, not a proven minimum wall thickness; taper corners can flag. 45-degree outward layer areas include bridgeable decorative ledges; evaluate slicing and support access separately.'}

def ray_thickness(mesh, threshold):
    eps=1e-5
    origins=mesh.triangles_center-mesh.face_normals*eps
    directions=-mesh.face_normals
    locations, rays, tris=mesh.ray.intersects_location(origins,directions,multiple_hits=False)
    distances=np.full(len(origins),np.nan)
    distances[rays]=np.linalg.norm(locations-origins[rays],axis=1)+eps
    good=distances[np.isfinite(distances)]
    bad=np.where(distances<threshold-1e-5)[0]
    supplemental=[]
    for i in np.where(~np.isfinite(distances))[0]:
        # Edge-aligned rays can fall through a numerical triangulation seam.
        # Keep the original miss and retain four tangentially offset checks.
        normal=mesh.face_normals[i]
        seed=np.eye(3)[int(np.argmin(abs(normal)))];u=np.cross(normal,seed);u/=np.linalg.norm(u)
        v=np.cross(normal,u)
        offsets=np.asarray([u,-u,v,-v])*1e-4
        tests=origins[i]+offsets
        hits,rayids,_=mesh.ray.intersects_location(tests,np.repeat(directions[i][None,:],4,axis=0),multiple_hits=False)
        ds=np.full(4,np.nan);ds[rayids]=np.linalg.norm(hits-tests[rayids],axis=1)+eps
        supplemental.append({'face':int(i),'original_centroid_mm':mesh.triangles_center[i].tolist(),
                             'tangential_offset_mm':0.0001,'offset_distances_mm':[float(x) if np.isfinite(x) else None for x in ds]})
    return {'method':'inward normal first-hit ray from every face centroid, unsampled; offset 0.00001 mm',
            'faces_tested':len(origins),'missed_rays':int(np.sum(~np.isfinite(distances))),
            'minimum_mm':float(good.min()) if len(good) else None,
            'percentiles_mm':np.percentile(good,[1,5,50,95]).tolist() if len(good) else [],
            'threshold_mm':threshold,'raw_thin_face_ids':bad.tolist(),
            'raw_thin_face_count':len(bad),
            'supplemental_original_misses':supplemental,
            'limitations':'All face centroids tested; this is evidence at those rays, not a proof of arbitrary-point minimum thickness. Acute bevels/roof tips can report short distances.'}

def point_segment_sq(p,a,b):
    ab=b-a; d=np.einsum('ij,ij->i',ab,ab)
    t=np.divide(np.einsum('ij,ij->i',p-a,ab),d,out=np.zeros(len(ab)),where=d>1e-20)
    q=a+np.clip(t,0,1)[:,None]*ab
    return np.einsum('ij,ij->i',p-q,p-q)

def segment_distance_sq(a,b,c,d):
    # Endpoint/segment candidates plus valid interior/interior line solution.
    result=np.minimum.reduce([point_segment_sq(a,c,d),point_segment_sq(b,c,d),point_segment_sq(c,a,b),point_segment_sq(d,a,b)])
    u=b-a;v=d-c;w=a-c
    aa=np.einsum('ij,ij->i',u,u);bb=np.einsum('ij,ij->i',u,v);cc=np.einsum('ij,ij->i',v,v)
    dd=np.einsum('ij,ij->i',u,w);ee=np.einsum('ij,ij->i',v,w);den=aa*cc-bb*bb
    s=np.divide(bb*ee-cc*dd,den,out=np.full(len(u),np.nan),where=abs(den)>1e-16)
    t=np.divide(aa*ee-bb*dd,den,out=np.full(len(u),np.nan),where=abs(den)>1e-16)
    valid=(s>=0)&(s<=1)&(t>=0)&(t<=1)
    q=w+s[:,None]*u-t[:,None]*v
    result[valid]=np.minimum(result[valid],np.einsum('ij,ij->i',q[valid],q[valid]))
    return result

def mesh_distance(a,b):
    # Triangle-pair distance minima occur vertex/face or edge/edge.
    va=trimesh.proximity.closest_point(b,a.vertices)[1]
    vb=trimesh.proximity.closest_point(a,b.vertices)[1]
    dist=float(min(va.min(),vb.min()))
    ea=a.vertices[a.edges_unique];eb=b.vertices[b.edges_unique]
    bs=np.column_stack((eb.min(axis=1),eb.max(axis=1)));tree=tree_for(bs)
    tested=0
    for edge in ea:
        bound=np.r_[edge.min(axis=0)-dist-EPS,edge.max(axis=0)+dist+EPS]
        ids=list(tree.intersection(tuple(bound)))
        if not ids: continue
        other=eb[ids]; tested+=len(ids)
        q=segment_distance_sq(np.repeat(edge[0][None,:],len(ids),axis=0),np.repeat(edge[1][None,:],len(ids),axis=0),other[:,0],other[:,1])
        dist=min(dist,math.sqrt(max(0.,float(q.min()))))
        if dist<EPS: return 0.,tested
    return dist,tested

def assembly_analysis(parts, expectations):
    records=[]
    expected={frozenset((r['a'],r['b'])):r for r in expectations}
    for (ida,a),(idb,b) in itertools.combinations(parts.items(),2):
        rule=expected.get(frozenset((ida,idb)))
        gaps=np.maximum(a.bounds[0]-b.bounds[1],b.bounds[0]-a.bounds[1])
        bbox_gap=float(np.linalg.norm(np.maximum(gaps,0)))
        volume=0.;error=None
        if bbox_gap<EPS:
            try:
                inter=trimesh.boolean.intersection([a,b],engine='manifold',check_volume=True)
                volume=abs(float(inter.volume)) if inter is not None else 0.
            except Exception as e: error=str(e)
        distance,edges=mesh_distance(a,b) if volume<1e-6 else (0.,0)
        flags=[]
        max_volume=rule.get('max_intersection_mm3',1e-5) if rule else 1e-5
        if error: flags.append('BOOLEAN_UNCERTAIN')
        if volume>max_volume: flags.append('PENETRATION_VOLUME')
        if not rule and distance<EPS: flags.append('UNEXPECTED_CONTACT')
        if rule and distance+EPS<rule.get('min_clearance_mm',0): flags.append('CLEARANCE_TOO_SMALL')
        if rule and distance-EPS>rule.get('max_clearance_mm',math.inf): flags.append('EXPECTED_CONTACT_GAP')
        records.append({'a':ida,'b':idb,'expected_contact':rule is not None,'intersection_mm3':volume,
                        'surface_clearance_mm':distance,'bbox_gap_mm':bbox_gap,'edge_pairs_tested':edges,
                        'flags':flags,'boolean_error':error,'expectation':rule})
    return {'method':'all part pairs; manifold intersection volume; bidirectional all-vertex/triangle distances and all potentially closer edge/edge pairs',
            'pairs':records,'pass':all(not r['flags'] for r in records)}

def main():
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',required=True);p.add_argument('--section-step',type=float,default=0.2);p.add_argument('--reuse-report')
    args=p.parse_args(); manifest=Path(args.manifest).resolve();data=json.loads(manifest.read_text(encoding='utf-8-sig'))
    if data.get('units')!='mm': raise ValueError('Manifest must explicitly declare units=mm')
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    result={'schema_version':1,'manifest_sha256':sha(manifest),'units':'mm','versions':{'python':platform.python_version(),'trimesh':trimesh.__version__,'shapely':shapely.__version__},'parts':[]}
    cache_path=Path(args.reuse_report).resolve() if args.reuse_report else None
    cached=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path else None
    assembled={}
    for part in data['parts']:
        t=time.monotonic();pid=part['id'];path=manifest.parent/part['stl'];raw=trimesh.load_mesh(path,process=False)
        m=raw.copy();m.merge_vertices();flags=[]
        old=next((r for r in cached['parts'] if r['id']==pid and r['sha256']==sha(path)),None) if cached else None
        if old and old['thickness_summary']['threshold_mm']==part.get('min_feature_mm',0.8) and old['sections']['step_mm']==args.section_step:
            lo,hi=m.bounds[:,2]
            desired=np.unique(np.r_[np.arange(lo+args.section_step/2,hi,args.section_step),[h for h in data.get('section_heights_mm',[]) if lo+EPS<h<hi-EPS]])
            old_heights=[r['z_mm'] for r in json.loads((cache_path.parent/f'{pid}_sections.json').read_text())]
            if len(old_heights)==len(desired) and np.allclose(old_heights,desired,atol=1e-9,rtol=0):
                rec=copy.deepcopy(old);rec['reused_geometry_qa_from']=os.path.relpath(cache_path,out).replace('\\','/')
                rec['reuse_basis']='Exact STL SHA-256, thickness threshold and complete section-height list match; raw flags unchanged.'
                for suffix in ['_sections.json','_section_overlay.svg','_thickness.json','_triangle_contacts.json']:
                    source=cache_path.parent/f'{pid}{suffix}'
                    if source.is_file():shutil.copyfile(source,out/source.name)
                assembled[pid]=m.copy();assembled[pid].apply_transform(np.asarray(part.get('assembly_transform',np.eye(4))))
                result['parts'].append(rec);json_write(out/'mesh_qa.json',result)
                print(pid,'exact-SHA cached geometry QA; assembly rechecked',flush=True)
                continue
        components=m.split(only_watertight=False)
        degenerates=np.where(m.area_faces<1e-10)[0]
        duplicate_count=len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0))
        for fail,condition in [('NOT_WATERTIGHT',not m.is_watertight),('INCONSISTENT_WINDING',not m.is_winding_consistent),('NONPOSITIVE_VOLUME',m.volume<=0),('DEGENERATE_FACES',len(degenerates)>0),('DUPLICATE_FACES',duplicate_count>0),('COMPONENT_COUNT',len(components)!=part.get('expected_components',1))]:
            if condition:flags.append(fail)
        contacts=triangle_contacts(m);json_write(out/f'{pid}_triangle_contacts.json',contacts)
        if not contacts['counts']['pass_no_non_topological_contact']:flags.append('SELF_CONTACT_OR_INTERSECTION')
        thickness=ray_thickness(m,part.get('min_feature_mm',0.8))
        if thickness['raw_thin_face_count']:flags.append('FACE_CENTROID_THICKNESS_SCREEN')
        if thickness['missed_rays']:flags.append('THICKNESS_RAY_MISS')
        sections=section_analysis(m,args.section_step,data.get('section_heights_mm',[]),out,pid)
        if sections['raw_opening_0p8mm_flags']:flags.append('SECTION_THIN_OPENING_SCREEN')
        if sections['raw_45deg_outward_layer_flags']:flags.append('SECTION_45DEG_OVERHANG_SCREEN')
        json_write(out/f'{pid}_thickness.json',thickness)
        down=(m.face_normals[:,2]<-math.cos(math.radians(45)))&(m.triangles_center[:,2]>m.bounds[0,2]+0.05)
        assembled[pid]=m.copy();assembled[pid].apply_transform(np.asarray(part.get('assembly_transform',np.eye(4))))
        rec={'id':pid,'stl':part['stl'],'sha256':sha(path),'vertices_raw':len(raw.vertices),'vertices_merged':len(m.vertices),'faces':len(m.faces),'dimensions_mm':m.extents.tolist(),'bounds_mm':m.bounds.tolist(),'volume_mm3':float(m.volume),'surface_area_mm2':float(m.area),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'components':len(components),'component_faces':[len(c.faces) for c in components],'degenerate_face_ids':degenerates.tolist(),'duplicate_face_count':duplicate_count,'triangle_contact_counts':contacts['counts'],'thickness_summary':{k:v for k,v in thickness.items() if k!='raw_thin_face_ids'},'sections':sections,'downward_45deg_face_count_above_bed':int(down.sum()),'raw_flags':flags,'elapsed_seconds':round(time.monotonic()-t,3)}
        result['parts'].append(rec);json_write(out/'mesh_qa.json',result)
        print(pid,json.dumps({'faces':len(m.faces),'components':len(components),'flags':flags}),flush=True)
    result['assembly']=assembly_analysis(assembled,data.get('expected_contacts',[]))
    result['limitations']=['No physical print or trial fit performed.','Screen flags remain raw. Any subsequent disposition must cite separate evidence; raw findings are not overwritten.','Input STL is not repaired, remeshed, simplified, or rescaled. Identical STL vertex positions are merged only for topology analysis.']
    json_write(out/'mesh_qa.json',result)

if __name__=='__main__':main()
