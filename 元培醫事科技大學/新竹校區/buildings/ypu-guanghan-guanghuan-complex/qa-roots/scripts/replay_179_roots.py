"""Replay the 179 current-STL sample catalog; this does not generate a global dense scan."""
from pathlib import Path
import argparse,json,collections,numpy as np
from original_geometry import OriginalGeometry,segment_distance,output_directory,EXPECTED_SHA
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model',type=Path,required=True)
parser.add_argument('--samples',type=Path,default=P/'evidence/current-179-root-evidence.json')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
R=output_directory(args.output,P/'evidence');SHA=EXPECTED_SHA
g=OriginalGeometry(args.model,SHA)
T,nn,fa,ee,patch,pairs,m=g.T,g.nn,g.fa,g.ee,g.patch,g.pairs,g.m
cast,inside,segdist=g.cast,g.inside,segment_distance
from scipy.optimize import minimize
catalog=json.loads(args.samples.read_text());assert catalog['stl_sha256']==SHA
rows=catalog['samples'];assert len(rows)==179
allgraph=collections.defaultdict(set)
for a,b in pairs:allgraph[a].add(b);allgraph[b].add(a)
def allpaths(x,y):
 result=[]
 if y in allgraph[x]:result.append([x,y])
 for a in allgraph[x]:
  if a==y:continue
  if y in allgraph[a]:result.append([x,a,y])
  for b in allgraph[a]:
   if b in[x,a,y]:continue
   if y in allgraph[b]:result.append([x,a,b,y])
 return result
out=[]
for r in rows:
 fid=r['face'];xf=r['first_exit_face'];p=np.array(r['surface_mm']);end=p-nn[fid]*r['classification_actual_span_mm'];origin=(p+end)/2;candidates=[]
 for path in allpaths(int(patch[fid]),int(patch[xf])):
  es=[]
  for a,b in zip(path[:-1],path[1:]):
   ids=pairs[tuple(sorted([a,b]))];i=min(ids,key=lambda i:segdist(*ee[i],p,end));dist=segdist(*ee[i],p,end)
   es.append({'adjacency_index':i,'original_faces':fa[i].tolist(),'distance_from_first_solid_chord_mm':dist,'convex':bool(m.face_adjacency_convex[i]),'angle_degrees':float(np.degrees(m.face_adjacency_angles[i])),'edge_endpoints_mm':ee[i].tolist()})
  if max(e['distance_from_first_solid_chord_mm']for e in es)>.8:continue
  ids=[fid,xf]
  for node in path[1:-1]:ids.extend(np.where(patch==node)[0].tolist())
  ids=sorted(set(ids));ns=nn[ids];bisector=-(nn[fid]+nn[xf]);bisector/=np.linalg.norm(bisector);dots=ns@bisector
  candidates.append({'patch_chain':path,'edges':es,'normal_face_ids':ids,'normals':ns,'endpoint_bisector':bisector,'endpoint_dots':dots,'pure_convex':all(e['convex']for e in es),'endpoint_all_inward':bool(max(dots)<-1e-7),'max_edge_distance_mm':max(e['distance_from_first_solid_chord_mm']for e in es)})
 # Geometry-only priority: pure convex with common endpoint direction, else closest actual local boundary chain.
 candidates.sort(key=lambda c:(not(c['pure_convex']and c['endpoint_all_inward']),c['max_edge_distance_mm'],len(c['patch_chain'])))
 assert candidates,(fid,r['sample'],'no local actual chain')
 c=candidates[0];di=c['endpoint_bisector'];ns=c['normals'];method='source_exit_inward_bisector';optimization=None
 if not c['endpoint_all_inward']:
  k=len(ns);fun=lambda w:float((w@ns)@(w@ns));jac=lambda w:2*ns@(w@ns)
  sol=minimize(fun,np.ones(k)/k,jac=jac,bounds=[(0,1)]*k,constraints=[{'type':'eq','fun':lambda w:w.sum()-1,'jac':lambda w:np.ones(k)}],method='SLSQP',options={'ftol':1e-14,'maxiter':1000});vec=sol.x@ns;di=-vec/np.linalg.norm(vec);optimization={'success':bool(sol.success),'weights':sol.x.tolist(),'closest_normal_cone_vector_norm':float(np.linalg.norm(vec))};method='all_actual_chain_normal_max_margin_inward_direction'
 dots=ns@di;assert max(dots)<-1e-7
 hh=cast(origin,di);span=hh[0]['distance_mm'];ctrl={'origin_inside':inside(origin),'at_0_8mm_inside':inside(origin+.8*di),'root_midpoint_inside':inside(origin+span/2*di),'air_after_first_exit':inside(origin+(span+1e-5)*di)}
 patchgeom=[]
 for node in c['patch_chain'][1:-1]:
  ids=np.where(patch==node)[0];ts=T[ids];area=np.linalg.norm(np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]),axis=1)/2;alt=2*area/np.linalg.norm(ts-np.roll(ts,-1,axis=1),axis=2).max(axis=1)
  patchgeom.append({'patch_id':node,'original_face_ids':ids.tolist(),'triangle_area_mm2':area.tolist(),'triangle_minimum_altitude_mm':alt.tolist(),'minimum_triangle_altitude_mm':float(alt.min())})
 out.append({**r,'first_material_midpoint_mm':origin.tolist(),'selected_local_actual_boundary_chain':{k:v for k,v in c.items()if k not in['normals','endpoint_bisector','endpoint_dots']},'chain_actual_face_normals':ns.tolist(),'original_endpoint_bisector_direction':c['endpoint_bisector'].tolist(),'original_endpoint_bisector_dot_all_faces':c['endpoint_dots'].tolist(),'final_direction_method':method,'common_inward_direction':di.tolist(),'common_inward_dot_all_faces':dots.tolist(),'optimization':optimization,'first_connected_root_mm':span,'root_all_hits':hh,'controls':ctrl,'intermediate_patch_original_geometry':patchgeom,'prior_sha_correspondence_by_exact_surface_point':r.get('prior_sha_correspondence_by_exact_surface_point'),'pure_convex_chain_claim':c['pure_convex']})
counts=dict(collections.Counter(r['final_direction_method']for r in out));mixed=[r for r in out if not r['pure_convex_chain_claim']];maxmargin=[r for r in out if r['final_direction_method'].startswith('all_')]
summary={'stl_sha256':SHA,'original_faces':len(T),'original_triangle_acceleration_preserves_exact_coordinates_and_winding':True,'replayed_new_original_samples':len(out),'pure_convex_samples':len(out)-len(mixed),'mixed_actual_convex_concave_seam_samples':len(mixed),'direction_method_counts':counts,'minimum_connected_first_exit_root_mm':min(r['first_connected_root_mm']for r in out),'minimum_max_margin_root_mm':min(r['first_connected_root_mm']for r in maxmargin),'minimum_all_face_margin_for_max_margin_samples':min(-max(r['common_inward_dot_all_faces'])for r in maxmargin),'all_direction_dots_inward':all(max(r['common_inward_dot_all_faces'])<0 for r in out),'all_inside_and_air_controls_correct':all(all(r['controls']['origin_inside'])and all(r['controls']['at_0_8mm_inside'])and all(r['controls']['root_midpoint_inside'])and not any(r['controls']['air_after_first_exit'])for r in out),'all_roots_at_least_0_8':all(r['first_connected_root_mm']>=.8 for r in out),'remaining_micro_width_actual_seam_faces':sorted({f for r in out for q in r['intermediate_patch_original_geometry']for f,a in zip(q['original_face_ids'],q['triangle_minimum_altitude_mm'])if a<.001}),'method':'New current-STL original face IDs and exact triangles. Local graph has at most two intermediate actual near-coplanar patches; all actual shared crease segments within .8mm of first material chord. The 178 mixed chains retain one genuine concave seam edge and are never labeled pure convex. All actual intermediate triangle normals are included. Use source/exit inward bisector when inward to all faces; otherwise geometry-only max-margin normal-cone direction, optimized before ray casting and independent of root length. First connected exit only.','limitations':['178 mixed convex/concave chains cannot support a pure convex-corner exception. Original micro-width seam facets are recorded, not collapsed or repaired.','The common inward root supports a bounded directional backing interpretation for these samples only; it does not establish global minimum wall thickness or automatic printability.','This is author diagnostic evidence, not independent acceptance.']}
(R/'current-179-root-summary.json').write_text(json.dumps(summary,indent=2));(R/'current-179-root-evidence.json').write_text(json.dumps(json.loads(json.dumps({**summary,'non_finite_original_air_gaps_serialized_as_null':True,'samples':out}),parse_constant=lambda value:None),indent=2,allow_nan=False));print(json.dumps(summary,indent=2))
