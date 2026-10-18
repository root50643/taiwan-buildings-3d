"""Read-only independent STL audit. No imported candidate QA functions.

Binary32 coordinates are promoted to a common exact integer grid. Every pair
with exactly overlapping AABBs is checked with exact predicates. Nonparallel
triangles use rational one-axis plane-cut intervals; coplanar triangles use
contained vertices plus exact edge-edge intersections (not the author's clip).
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter, defaultdict, deque
import struct, hashlib, json, time, sys
import numpy as np
import trimesh
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, unary_union

ROOT=Path(__file__).resolve().parent
PACKAGE=ROOT.parent/'candidate'
MODEL=PACKAGE/'model.stl'
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def normal(t):return cross(sub(t[1],t[0]),sub(t[2],t[0]))
def orientations(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def between(x,a,b):return min(a,b)<=x<=max(a,b)
def onseg2(p,a,b):return orientations(a,b,p)==0 and all(between(p[k],a[k],b[k]) for k in (0,1))
def inside2(p,t):
 d=[orientations(t[i],t[(i+1)%3],p) for i in range(3)]
 return all(x>=0 for x in d) or all(x<=0 for x in d)
def edgepoints2(a,b,c,d):
 u,v,w=sub(b,a),sub(d,c),sub(c,a)
 den=u[0]*v[1]-u[1]*v[0]
 if den:
  t=F(w[0]*v[1]-w[1]*v[0],den)
  q=F(w[0]*u[1]-w[1]*u[0],den)
  return [tuple(a[k]+t*u[k] for k in (0,1))] if 0<=t<=1 and 0<=q<=1 else []
 return [p for p in (a,b,c,d) if onseg2(p,a,b) and onseg2(p,c,d)]
def cutvalues(tri,distances,axis):
 vals=[]
 for k in range(3):
  j=(k+1)%3
  if distances[k]==0:vals.append(F(tri[k][axis]))
  if distances[k]*distances[j]<0:
   vals.append(F(tri[k][axis]*distances[j]-tri[j][axis]*distances[k],distances[j]-distances[k]))
 return vals
def pair(a,b,na=None,nb=None):
 na=na or normal(a);nb=nb or normal(b)
 da=[dot(sub(p,b[0]),nb) for p in a]
 db=[dot(sub(p,a[0]),na) for p in b]
 shared=set(a)&set(b)
 out={'shared_vertex_count':len(shared)}
 if any(all(s*x>0 for x in ds) for ds in (da,db) for s in (-1,1)):
  return 'disjoint',out
 direction=cross(na,nb)
 if any(direction):
  axis=max(range(3),key=lambda k:abs(direction[k]))
  va,vb=cutvalues(a,da,axis),cutvalues(b,db,axis)
  if not va or not vb:return 'disjoint',out
  lo,hi=max(min(va),min(vb)),min(max(va),max(vb))
  out.update({'axis':axis,'low_grid':str(lo),'high_grid':str(hi)})
  if hi<lo:return 'disjoint',out
  if len(shared)==1 and lo==hi==next(iter(shared))[axis]:return 'shared_vertex_only',out
  if len(shared)==2 and min(p[axis] for p in shared)<=lo<=hi<=max(p[axis] for p in shared):return 'shared_edge_only',out
  return 'unexpected_intersection',out
 if any(da):return 'disjoint',out
 axis=max(range(3),key=lambda k:abs(na[k]))
 keep=[k for k in range(3) if k!=axis]
 aa,bb=[tuple(p[k] for k in keep) for p in a],[tuple(p[k] for k in keep) for p in b]
 pts=set(p for p in aa if inside2(p,bb))|set(p for p in bb if inside2(p,aa))
 for i in range(3):
  for j in range(3):pts.update(edgepoints2(aa[i],aa[(i+1)%3],bb[j],bb[(j+1)%3]))
 out.update({'coplanar':True,'intersection_vertices_grid':[[str(v) for v in p] for p in sorted(pts)]})
 if not pts:return 'disjoint',out
 ss=[tuple(p[k] for k in keep) for p in shared]
 if len(ss)==1 and pts==set(ss):return 'shared_vertex_only',out
 if len(ss)==2 and all(onseg2(p,*ss) for p in pts):return 'shared_edge_only',out
 return 'unexpected_intersection',out

def controls():
 a=((0,0,0),(4,0,0),(0,4,0))
 cases={
 'crossing':(a,((1,1,-2),(1,1,2),(3,1,0)),'unexpected_intersection'),
 'coplanar_overlap':(a,((1,1,0),(5,1,0),(1,5,0)),'unexpected_intersection'),
 'coplanar_containment':(a,((1,1,0),(2,1,0),(1,2,0)),'unexpected_intersection'),
 'edge':(a,((0,0,0),(4,0,0),(2,-2,1)),'shared_edge_only'),
 'coplanar_edge':(a,((0,0,0),(4,0,0),(2,-2,0)),'shared_edge_only'),
 'vertex':(a,((0,0,0),(-1,0,2),(0,-1,2)),'shared_vertex_only'),
 'coplanar_vertex':(a,((0,0,0),(-1,0,0),(0,-1,0)),'shared_vertex_only'),
 'parallel_disjoint':(a,((0,0,1),(4,0,1),(0,4,1)),'disjoint'),
 'aabb_disjoint':(a,((5,5,0),(6,5,0),(5,6,0)),'disjoint')}
 return {k:{'expected':e,'actual':pair(x,y)[0],'ok':pair(x,y)[0]==e} for k,(x,y,e) in cases.items()}

def topology(triangles,scale):
 verts=list(dict.fromkeys(p for t in triangles for p in t));ids={p:i for i,p in enumerate(verts)}
 faces=[tuple(ids[p] for p in t) for t in triangles]
 edges=defaultdict(list);links=defaultdict(list)
 for fi,face in enumerate(faces):
  for k in range(3):
   u,v=face[k],face[(k+1)%3];edges[tuple(sorted((u,v)))].append((fi,u,v))
   links[u].append(tuple(face[q] for q in range(3) if q!=k))
 adjacency=defaultdict(set)
 for es in edges.values():
  for f,u,v in es:
   adjacency[f].update(q[0] for q in es if q[0]!=f)
 seen=set();comps=[]
 for fi in range(len(faces)):
  if fi in seen:continue
  q=[fi];seen.add(fi);component=[]
  while q:
   f=q.pop();component.append(f)
   for n in adjacency[f]-seen:seen.add(n);q.append(n)
  comps.append(component)
 badlinks=[]
 for vertex,ls in links.items():
  nbr=defaultdict(list)
  for u,v in ls:nbr[u].append(v);nbr[v].append(u)
  seenlink=set();q=[next(iter(nbr))]
  while q:
   n=q.pop()
   if n in seenlink:continue
   seenlink.add(n);q+=nbr[n]
  if any(len(v)!=2 for v in nbr.values()) or len(seenlink)!=len(nbr):badlinks.append(vertex)
 volume6=sum(dot(t[0],cross(t[1],t[2])) for t in triangles)
 vol=F(volume6,6*scale**3)
 return {'vertices':len(verts),'triangles':len(faces),'edges':len(edges),
 'boundary_edges':sum(len(es)==1 for es in edges.values()),
 'nonmanifold_edges':sum(len(es)>2 for es in edges.values()),
 'inconsistent_edge_orientations':sum(len(es)==2 and es[0][1:]==es[1][1:] for es in edges.values()),
 'nonmanifold_vertex_link_indices':badlinks,'edge_connected_component_face_counts':[len(c) for c in comps],
 'exact_degenerate_triangle_ids':[i for i,t in enumerate(triangles) if not any(normal(t))],
 'duplicate_faces':len(faces)-len(set(tuple(sorted(f)) for f in faces)),
 'signed_volume_exact_mm3':str(vol),'signed_volume_mm3':float(vol),
 'euler_characteristic':len(verts)-len(edges)+len(faces)}

def event_sections(tris,zvalues):
 """All unique vertex-Z interval midpoints; exact slicing, float polygon assembly.

 This supplements the original uniform screen. It is not a proof of local
 minimum thickness between sampled heights or at every point on a boundary.
 """
 rows=[]
 for z in [(F(a)+F(b))/2 for a,b in zip(zvalues,zvalues[1:])]:
  lines=[]
  for t in tris:
   ds=[F(p[2])-z for p in t]
   pts=[]
   for k in range(3):
    j=(k+1)%3
    if ds[k]==0:pts.append(tuple(F(v) for v in t[k][:2]))
    if ds[k]*ds[j]<0:pts.append(tuple(F(t[k][q])+(F(t[j][q])-F(t[k][q]))*ds[k]/(ds[k]-ds[j]) for q in (0,1)))
   pts=list(dict.fromkeys(pts))
   if len(pts)==2:lines.append(LineString([[float(v) for v in p] for p in pts]))
  # exact rational points from identical edges convert to identical doubles.
  rings=list(polygonize(unary_union(lines)))
  selected=[]
  # polygonize includes inner loops as stand-alone polygons. Material parity is
  # determined by ray intersections of the closed section boundary.
  for poly in rings:
   rp=poly.representative_point();x,y=rp.x,rp.y
   ray_crossings=0
   for line in lines:
    (ax,ay),(bx,by)=line.coords
    if (ay>y)!=(by>y) and x < ax+(y-ay)*(bx-ax)/(by-ay):ray_crossings+=1
   if ray_crossings%2:selected.append(poly)
  mat=unary_union(selected)
  parts=[mat] if mat.geom_type=='Polygon' else list(mat.geoms) if mat.geom_type=='MultiPolygon' else []
  corecounts=[]
  for p in parts:
   c=p.buffer(-.6,join_style='mitre')
   corecounts.append(0 if c.is_empty else 1 if c.geom_type=='Polygon' else len(c.geoms))
  rows.append({'z_mm':float(z),'line_count':len(lines),'material_parts':len(parts),'area_mm2':float(mat.area),'erosion_0p6mm_core_counts':corecounts,'thin_core_flag':any(n!=1 for n in corecounts)})
 return rows

def main():
 start=time.time();data=MODEL.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+50*n
 raw=[tuple(tuple(struct.unpack_from('<3f',data,84+50*i+12+12*k)) for k in range(3)) for i in range(n)]
 den=max(x.as_integer_ratio()[1] for t in raw for p in t for x in p)
 tris=[tuple(tuple(int(F(x)*den) for x in p) for p in t) for t in raw]
 ns=[normal(t) for t in tris]
 lo=np.array([[min(p[k] for p in t) for k in range(3)] for t in tris],dtype=np.int64)
 hi=np.array([[max(p[k] for p in t) for k in range(3)] for t in tris],dtype=np.int64)
 counts=Counter();candidates=[];bad=[]
 for i,a in enumerate(tris):
  js=np.flatnonzero(np.all(hi[i]>=lo[i+1:],axis=1)&np.all(hi[i+1:]>=lo[i],axis=1))+i+1
  for jj in js:
   j=int(jj);kind,detail=pair(a,tris[j],ns[i],ns[j]);counts[kind]+=1
   candidates.append([i,j])
   if kind=='unexpected_intersection':bad.append({'faces':[i,j],**detail})
 floatmesh=trimesh.Trimesh(vertices=np.asarray(raw).reshape((-1,3)),faces=np.arange(n*3).reshape((-1,3)),process=True)
 zlevels=sorted(set(p[2] for t in raw for p in t))
 sections=event_sections(raw,zlevels)
 controls_result=controls()
 out={'input_sha256':hashlib.sha256(data).hexdigest(),'file_bytes':len(data),'original_stl_unchanged':MODEL.read_bytes()==data,
 'algorithm':'Exact common binary integer-grid predicates; rational nonparallel plane-cut intervals; coplanar contained-vertices and edge-edge intersection sets. Independent code, no imported candidate QA functions.',
 'coordinate_integer_grid_denominator':den,'topology':topology(tris,den),
 'trimesh_crosscheck':{'watertight':bool(floatmesh.is_watertight),'winding_consistent':bool(floatmesh.is_winding_consistent),'volume_mm3':float(floatmesh.volume),'bounds_mm':floatmesh.bounds.tolist(),'extents_mm':floatmesh.extents.tolist()},
 'all_triangle_pair_count':n*(n-1)//2,'exact_aabb_candidate_count':len(candidates),'exact_aabb_pair_classifications':dict(counts),'unexpected_intersections':bad,
 'controls':controls_result,
 'event_height_section_screen':{'z_event_count':len(zlevels),'interval_midpoint_count':len(sections),'event_z_mm':zlevels,'width_mm':1.2,'rows':sections,'thin_core_flag_count':sum(r['thin_core_flag'] for r in sections),
 'limitations':'One exact-sliced midpoint per vertex-Z interval; polygon assembly/erosion uses Shapely double precision. Does not prove universal local wall thickness, small protrusions, Z thickness, mechanical strength, extrusion, support or physical print.'},
 'all_control_expectations_met':all(x['ok'] for x in controls_result.values()),'runtime_seconds':time.time()-start,
 'scope_limits':['No mesh repair performed.','Exact pair enumeration is exact for the stored finite STL coordinates and shared coordinate topology, subject to the supplied auditable algorithm and controls; no external formal proof system used.','No slicer, nozzle paths or physical print performed.','Support risk is assessed separately; exact-intersection findings do not waive genuine overhangs.']}
 (ROOT/'independent-exact-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8')
 summary={k:v for k,v in out.items() if k not in ('original_flag_rows','event_height_section_screen')}
 summary['event_height_section_screen']={k:v for k,v in out['event_height_section_screen'].items() if k!='rows'}
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
