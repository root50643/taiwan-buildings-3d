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

def qa(out,topology_only=False):
    rec,v,f=raw_read(out/'model.stl'); tri=rec['v'].astype(np.float64); cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lens=np.linalg.norm(cross,axis=1)
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
    r={'method':'Raw binary STL; exact-equality welding only, no repairs','sha256':hashlib.sha256((out/'model.stl').read_bytes()).hexdigest(),'triangles':len(f),'vertices_exact_weld':len(v),'nonfinite_values':int((~np.isfinite(rec['v'])).sum()+(~np.isfinite(rec['n'])).sum()),'zero_area_triangles':int((lens==0).sum()),'duplicate_faces':len(f)-len(np.unique(np.sort(f,axis=1),axis=0)),'edge_incidence_not_two':int((counts!=2).sum()),'edge_orientation_failures':bad_oriented,'vertex_link_failures':len(bad_links),'stored_normals_nonpositive_dot':int((normals_match<=0).sum()),'stored_normal_unit_max_error':float(np.max(abs(np.linalg.norm(rec['n'].astype(np.float64),axis=1)-1))),'watertight':bool(mesh.is_watertight),'consistent_winding':bool(mesh.is_winding_consistent),'connected_shells':len(mesh.split(only_watertight=False)),'positive_signed_volume_mm3':float(mesh.volume),'dimensions_mm':mesh.extents.tolist()}
    unit = cross / np.maximum(lens[:, None], 1e-300)
    r['stored_normal_alignment_max_error']=float(np.max(np.linalg.norm(unit-rec['n'].astype(np.float64),axis=1)))
    gates = {k:r[k]==0 for k in ['nonfinite_values','zero_area_triangles','duplicate_faces','edge_incidence_not_two','edge_orientation_failures','vertex_link_failures','stored_normals_nonpositive_dot']}
    gates.update({'watertight':r['watertight'],'consistent_winding':r['consistent_winding'],'one_shell':r['connected_shells']==1,'positive_volume':np.isfinite(r['positive_signed_volume_mm3']) and r['positive_signed_volume_mm3']>0,'max_dimension_150mm':all(0<d<=150 for d in r['dimensions_mm']),'stored_unit_normals':r['stored_normal_unit_max_error']<=1e-6,'stored_normal_alignment':r['stored_normal_alignment_max_error']<=1e-6,'nonnegative_z':bool(v[:,2].min()>=0)})
    r['gates']={k:bool(v) for k,v in gates.items()};r['passed']=all(r['gates'].values())
    (out/'qa-topology.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
    if not r['passed'] or topology_only:return r,None
    from qa_sections import check_sections
    report=check_sections(out/'model.stl',out)
    return r,report
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=ROOT/'output');a.add_argument('--topology-only',action='store_true');args=a.parse_args();r,report=qa(args.out,args.topology_only)
    raise SystemExit(0 if r['passed'] and (args.topology_only or (report and report['passed'])) else 1)
