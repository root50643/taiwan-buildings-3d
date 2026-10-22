#!/usr/bin/env python3
"""Audit raw exported triangles. Exact coordinate welding is bookkeeping, not healing.
No normal repair, hole fill, degenerate deletion, rounding of contours, or thin exemptions.
"""
from pathlib import Path
import json, struct, hashlib, argparse
from collections import Counter, defaultdict
import numpy as np
import trimesh
import manifold3d as md
from shapely.geometry import Polygon, GeometryCollection
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent

def raw_read(p):
    data=p.read_bytes(); n=struct.unpack('<I',data[80:84])[0]
    rec=np.frombuffer(data,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
    vertices,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True)
    return rec,vertices,inv.reshape(-1,3)

def qa(out):
    rec,v,f=raw_read(out/'model.stl'); cross=np.cross(rec['v'][:,1]-rec['v'][:,0],rec['v'][:,2]-rec['v'][:,0]);lens=np.linalg.norm(cross,axis=1)
    mesh=trimesh.Trimesh(v,f,process=False)
    edges=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]); unique,counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
    orientation=Counter(map(tuple,edges.tolist()))
    bad_oriented=sum(orientation[tuple(e)]!=orientation[tuple(e[::-1])] for e in unique)
    # Every closed 2-manifold vertex link must be one connected simple cycle.
    links=defaultdict(list)
    for a,b,c in f:
        links[int(a)].append((int(b),int(c)));links[int(b)].append((int(c),int(a)));links[int(c)].append((int(a),int(b)))
    bad_links=[]
    for vertex,ledges in links.items():
        graph=defaultdict(set)
        for a,b in ledges: graph[a].add(b);graph[b].add(a)
        visited=set(); stack=[next(iter(graph))]
        while stack:
            a=stack.pop()
            if a in visited: continue
            visited.add(a);stack.extend(graph[a]-visited)
        if len(visited)!=len(graph) or any(len(n)!=2 for n in graph.values()) or len(ledges)!=len(graph):bad_links.append(vertex)
    normals_match=np.sum(cross*rec['n'],axis=1)
    r={'method':'Raw binary STL; exact-equality welding only, no repairs','sha256':hashlib.sha256((out/'model.stl').read_bytes()).hexdigest(),'triangles':len(f),'vertices_exact_weld':len(v),'nonfinite_values':int((~np.isfinite(rec['v'])).sum()+(~np.isfinite(rec['n'])).sum()),'zero_area_triangles':int((lens==0).sum()),'duplicate_faces':len(f)-len(np.unique(np.sort(f,axis=1),axis=0)),'edge_incidence_not_two':int((counts!=2).sum()),'edge_orientation_failures':bad_oriented,'vertex_link_failures':len(bad_links),'stored_normals_nonpositive_dot':int((normals_match<=0).sum()),'stored_normal_unit_max_error':float(np.max(abs(np.linalg.norm(rec['n'],axis=1)-1))),'watertight':bool(mesh.is_watertight),'consistent_winding':bool(mesh.is_winding_consistent),'connected_shells':len(mesh.split(only_watertight=False)),'positive_signed_volume_mm3':float(mesh.volume),'dimensions_mm':mesh.extents.tolist()}
    (out/'qa-topology.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
    assert r['watertight'] and r['consistent_winding'] and r['connected_shells']==1 and all(r[k]==0 for k in ['nonfinite_values','zero_area_triangles','duplicate_faces','edge_incidence_not_two','edge_orientation_failures','vertex_link_failures','stored_normals_nonpositive_dot']), 'Raw topology gate failed: do not trust slicing invalid input'
    raw=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
    layers=[];failures=[]
    # Exact 0.2 mm multiples above base; sample top-0.001 additionally to test high rims.
    zvals=np.r_[np.arange(.2,float(v[:,2].max()),.2),float(v[:,2].max())-.001]
    for z in zvals:
        contours=raw.slice(float(z)).to_polygons()
        signed=[]
        for c in contours:
            c=np.asarray(c,dtype=float)
            if len(c)<3:continue
            area=.5*np.sum(c[:,0]*np.roll(c[:,1],-1)-np.roll(c[:,0],-1)*c[:,1])
            signed.append((area,Polygon(c)))
        geom=GeometryCollection()
        for _,p in signed:
            geom=geom.symmetric_difference(p)
        comps=list(geom.geoms) if geom.geom_type=='MultiPolygon' else ([geom] if not geom.is_empty else [])
        bad=[]
        for i,p in enumerate(comps):
            eroded=p.buffer(-.4,quad_segs=16)
            if eroded.is_empty:bad.append({'component':i,'area_mm2':float(p.area),'bounds_mm':list(p.bounds)})
        row={'z_mm':float(z),'contours':len(contours),'components':len(comps),'invalid_contours':sum(not p.is_valid for _,p in signed),'invalid_result':not geom.is_valid,'failed_0_8mm_components':bad}
        layers.append(row)
        if bad or row['invalid_contours'] or row['invalid_result'] or not comps: failures.append(row)
    report={'stl_sha256':r['sha256'],'method':'manifold cross-sections of raw STL at unrounded 0.2mm multiples plus top minus0.001mm; all polygon coordinates retained with even-odd nesting, including islands inside holes; each positive connected component tested against exact -0.4mm Shapely erosion; zero thin-feature exemptions, all failures retained as warnings rather than minimum-wall certification','layer_count':len(layers),'all_contours_valid':all(x['invalid_contours']==0 and not x['invalid_result'] for x in layers),'all_components_survive_0_8mm':not failures,'failures':failures,'layers':layers}
    (out/'qa-layers.json').write_text(json.dumps(report,indent=2)+'\n');print('LAYER SUMMARY',json.dumps({k:v for k,v in report.items() if k!='layers'}),flush=True)
    assert report['all_contours_valid'] and all(x['components']>0 for x in layers), 'Invalid or empty global slice'
    # Sloped stair rails and small rooflight details create transient sub-nozzle horizontal islands.
    # Retain ALL failed erosion rows; never relabel this as a minimum-wall pass.
    if not report['all_components_survive_0_8mm']: print('WARNING: sub-0.8mm transient slice islands retained; see local normal thickness and support report',flush=True)
    return r,report
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=ROOT);args=a.parse_args();qa(args.out)
