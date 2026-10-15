"""Independent original-face probes; original-author requested rays regenerated, corrected target-specific rays added."""
import importlib.util,sys,numpy as np,json,collections,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('c',str(Path(__file__).resolve().parent/'ntou-revision-components-independent.py'));c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
T=c.T;nn=c.nn;ray=c.ray;winding=c.winding;save=c.save;H=c.H

def normal_probe(family,o,d,label=None):
 o=np.array(o,dtype=float);d=np.array(d,dtype=float);d/=np.linalg.norm(d);hits=ray(o,d);assert hits,(family,o,d)
 first=hits[0];p=o+d*first['distance_mm'];fi=first['original_face'];n=nn[fi];origin=p+n*1e-5;h=ray(origin,-n);assert len(h)>=2,(family,p,h)
 length=h[1]['distance_mm']-h[0]['distance_mm'];air=h[2]['distance_mm']-h[1]['distance_mm'] if len(h)>2 else 1
 ps=[origin,p-n*1e-5,origin-n*(h[0]['distance_mm']+h[1]['distance_mm'])/2,origin-n*(h[1]['distance_mm']+min(air/4,1e-5))];ctrl=[dict(point_mm=q.tolist(),expected=e,winding=winding(q))for q,e in zip(ps,[0,1,1,0])]
 return dict(family=family,label=label,initial_origin_mm=o.tolist(),initial_direction=d.tolist(),initial_origin_winding=winding(o),initial_hits=hits,original_first_face=fi,source_surface_mm=p.tolist(),actual_geometric_normal=n.tolist(),normal_origin_mm=origin.tolist(),normal_all_hits=h,first_normal_chord_mm=length,entry_exit_orientations_valid=h[0]['normal_dot_direction']<0 and h[1]['normal_dot_direction']>0,controls=ctrl,controls_passed=all(abs(q['winding']-q['expected'])<1e-7 for q in ctrl))

def authored_probes():
 out=[]
 def add(f,o,d):out.append(normal_probe(f,o,d))
 for x,r in [(0,1.45),(-41.5,.6),(-35.5,.6)]:
  y=-26.5 if x==0 else -31.6
  for z in [3.13,7.37,11.03]:
   for a in [.17,1.13,2.29,3.41,4.57,5.73]:add('entrance_circular_column'if x==0 else'local_canopy_posts',[x+5*np.cos(a),y+5*np.sin(a),z],[-np.cos(a),-np.sin(a),0])
  add('continuous_support_to_base',[x+.173,y+.131,60],[0,0,-1])
 for x in [-40.4,-38.3,-36.2]:
  for y in [-31.73,-30.39]:add('local_canopy_plate',[x,y,20],[0,0,-1])
 for x in [-9.31,-4.31,4.31,9.31]:add('deep_entry_backing',[x,-34,7.23],[0,1,0])
 for x in [13.31,15.31,19.31,21.31,24.81,27.31,30.31,32.31]:
  for z in [6.13,8.17,10.93]:add('right_window_backing',[x,-33,z],[0,1,0])
 for x in [17.25,28.75]:
  for z in [5.73,7.13,9.13]:add('flush_glazing_bar',[x+.113,-33,z],[0,1,0])
 for x,z in [(-33,5.37),(-31.2,6.87),(-29.4,4.37),(-27.6,6.87),(-43.5,5.37),(-41,7.37)]:add('left_small_window_backing',[x+.13,-33,z],[0,1,0])
 for sx in [-1,1]:
  for y in [-13.17,-1.17,10.83,22.83,34.83]:
   add('side_window_above_repaired_sill',[sx*65,y,15.37],[-sx,0,0]);add('side_window_sill',[sx*58.13,y,17],[0,0,-1])
 for x in np.linspace(-69,69,13):
  for z in [20.071,40.671,41.871]:add('curved_rib_width',[x-2,-22 if z>40 else -38,z],[1,0,0])
 author=c.read(c.B/'designated-roots.json')['rows'];assert len(out)==len(author)==162
 for i,(r,a)in enumerate(zip(out,author)):
  assert r['family']==a['family']
  r.update(author_original_record=a,author_index=i,author_original_face=a['original_face'],author_source_surface_mm=a['source_surface_mm'],author_first_normal_mm=a['first_normal_mm'],source_face_matches=r['original_first_face']==a['original_face'],source_point_delta_mm=float(np.linalg.norm(np.array(r['source_surface_mm'])-a['source_surface_mm'])),first_normal_length_delta_mm=r['first_normal_chord_mm']-a['first_normal_mm'])
  fam=r['family'];p=r['source_surface_mm']
  r['target_classification']='matches_designated_target'
  if fam=='continuous_support_to_base':r['target_classification']='upper_curved_roof_surface_oblique_normal_not_vertical_support'
  elif fam=='local_canopy_plate':r['target_classification']='curved_roof_underside_not_canopy_plate'
  elif fam=='local_canopy_posts'and abs(r['actual_geometric_normal'][0])<1e-6:r['target_classification']='facade_backing_not_canopy_post'
  elif fam=='curved_rib_width'and p[2]==40.671:r['target_classification']='full_merged_roof_span_not_isolated_rib_width'
 return out

def corrected_probes():
 out=[]
 for x,r in [(0,1.45),(-41.5,.6),(-35.5,.6)]:
  y=-26.5 if x==0 else-31.6
  for z in [3.13,7.37,11.03]:
   for a in [.17,1.13,2.29,3.41,4.57,5.73]:
    q=normal_probe('actual_entrance_column'if x==0 else'actual_canopy_post',[x+(r+.001)*np.cos(a),y+(r+.001)*np.sin(a),z],[-np.cos(a),-np.sin(a),0]);p=np.array(q['source_surface_mm']);q['target_assertion']=abs(p[2]-z)<1e-10 and abs(np.linalg.norm(p[:2]-[x,y])-r)<.02 and abs(q['actual_geometric_normal'][2])<1e-5;assert q['target_assertion'],(x,y,z,q['source_surface_mm'],q['actual_geometric_normal']);out.append(q)
 for x in [-40.4,-38.3,-36.2]:
  for y in [-31.73,-30.39]:
   q=normal_probe('actual_canopy_plate_top',[x,y,14],[0,0,-1]);q['target_assertion']=abs(q['source_surface_mm'][2]-12.7)<1e-5 and abs(q['actual_geometric_normal'][2]-1)<1e-10;assert q['target_assertion'];out.append(q)
 for x in np.linspace(-69,69,13):
  for z in [20.071,41.871]:
   q=normal_probe('actual_isolated_curved_rib',[x-1,-22 if z>40 else-38,z],[1,0,0]);q['target_assertion']=abs(q['source_surface_mm'][0]-(x-.85))<1e-5;assert q['target_assertion'];out.append(q)
 for i,q in enumerate(out):
  q["counterpart_author_index"]=i if i<18 else i+1 if i<36 else i+2 if i<54 else i+3 if i<60 else 123+3*((i-60)//2)+(0 if (i-60)%2==0 else 2)
  q["replacement_scope"]="Same intended local target at the same height; source origin moved close to actual surface to avoid intersecting unrelated geometry first."
 return out

def vertical_supports():
 out=[]
 for name,x,y in [('entrance_column',.173,-26.369),('left_canopy_post',-41.327,-31.469),('right_canopy_post',-35.327,-31.469),('canopy_plate_between_posts',-40.4,-31.73),('canopy_plate_middle',-38.3,-30.39)]:
  o=np.array([x,y,60.]);d=np.array([0.,0.,-1.]);h=ray(o,d);bounds=[0]+[x['distance_mm']for x in h]+[h[-1]['distance_mm']+1.]
  ints=[]
  for a,b in zip(bounds[:-1],bounds[1:]):
   mid=(a+b)/2;p=o+d*mid;ww=winding(p);ints.append(dict(start_z_mm=60-a,end_z_mm=60-b,length_mm=b-a,midpoint_mm=p.tolist(),winding=ww,inside=abs(ww-1)<1e-7,outside=abs(ww)<1e-7))
  spans=[s for s in ints if s['inside']];assert all(s['inside']or s['outside']for s in ints)
  q=dict(counterpart_author_index={'entrance_column':18,'left_canopy_post':37,'right_canopy_post':56}.get(name),name=name,origin_mm=o.tolist(),direction=d.tolist(),original_hits=h,all_intervals=ints,material_intervals=spans,down_base_last_exit_z_mm=60-h[-1]['distance_mm'])
  if name.endswith('_post'):q['continuous_canopy_top_to_base_mm']=next(s['length_mm']for s in spans if abs(s['start_z_mm']-12.7)<1e-5 and abs(s['end_z_mm'])<1e-9)
  if name=='entrance_column':q['continuous_top_to_base_mm']=spans[0]['length_mm'];assert abs(spans[0]['end_z_mm'])<1e-9
  # Reverse from underneath independently locates the base-facing original triangle and full first material interval.
  bo=np.array([x,y,-1.]);bh=ray(bo,[0,0,1]);q['bottom_up_hits']=bh;q['bottom_up_first_chord_mm']=bh[1]['distance_mm']-bh[0]['distance_mm'];q['base_bottom_source_normal']=nn[bh[0]['original_face']].tolist()
  out.append(q)
 return out

def warning_roots():
 rows=c.read(c.O/'ntou-revision-components-polygons-evidence.json.gz')['original_component_checks'];warn=[r for r in rows if r['opening_loss_fraction']>.01];out=[]
 for wi,r in enumerate(warn):
  p=c.wkt.loads(r['original_polygon_wkt']);z=r['z_unrounded_mm'];ps=[]
  for ri,ring in enumerate([p.exterior,*p.interiors]):
   P=np.array(ring.coords[:-1]);true=[v['vertex_index']for v in r['true_corners']if v['ring_index']==ri]
   for edgei,(ia,ib)in enumerate(zip(true,true[1:]+true[:1])):
    a,b=P[ia],P[ib];v=b-a;mid=(a+b)/2;n=np.array([v[1],-v[0]])/np.linalg.norm(v)
    if not p.contains(c.Point(mid-n*1e-5)):n=-n
    q=normal_probe(r['warning_family'],[*(mid+n*1e-5),z],[*(-n),0]);q.update(ring_index=ri,true_side_index=edgei);ps.append(q)
  rp=p.representative_point();point=np.array([rp.x,rp.y,z]);dh=ray(point,[0,0,-1]);uh=ray(point,[0,0,1]);controls=[]
  for direction,h in [(np.array([0,0,-1]),dh),(np.array([0,0,1]),uh)]:
   for t,expected in [(0,1),(h[0]['distance_mm']/2,1),(h[0]['distance_mm']+min(1e-5,(h[1]['distance_mm']-h[0]['distance_mm'])/4 if len(h)>1 else 1e-5),0)]:
    pt=point+direction*t;controls.append(dict(point_mm=pt.tolist(),expected=expected,winding=winding(pt)))
  out.append(dict(z_mm=r['z_mm'],component_index=r['original_component_index'],author_component_index=r['author_original_component_index'],family=r['warning_family'],edge_probes=ps,root_point_mm=point.tolist(),down_hits=dh,up_hits=uh,first_down_exit_z_mm=z-dh[0]['distance_mm'],first_up_exit_z_mm=z+uh[0]['distance_mm'],continuous_vertical_first_material_span_mm=dh[0]['distance_mm']+uh[0]['distance_mm'],root_controls=controls,controls_passed=all(abs(q['winding']-q['expected'])<1e-7 for q in controls)))
  if(wi+1)%10==0:print('WARNING ROOT',wi+1,flush=True)
 return out

def famstats(rows):
 return{f:dict(count=len(rs),min_first_normal_chord_mm=min(r['first_normal_chord_mm']for r in rs),max_first_normal_chord_mm=max(r['first_normal_chord_mm']for r in rs),under_0p8_count=sum(r['first_normal_chord_mm']<.8 for r in rs),control_failures=sum(not r['controls_passed']for r in rs),orientation_failures=sum(not r['entry_exit_orientations_valid']for r in rs))for f in sorted(set(r['family']for r in rows))for rs in [[r for r in rows if r['family']==f]]}

if __name__=='__main__':
 a=authored_probes();print('AUTHORED DONE',flush=True);correct=corrected_probes();print('CORRECTED DONE',flush=True);v=vertical_supports();print('VERTICAL DONE',flush=True);w=warning_roots()
 mismatches=[r for r in a if r['target_classification']!='matches_designated_target'];ps=[p for r in w for p in r['edge_probes']]
 summary=dict(stl_sha256=H,author_designated_count=len(a),author_designated_family_results=famstats(a),all_162_original_first_faces_match=all(r['source_face_matches']for r in a),max_author_source_point_delta_mm=max(r['source_point_delta_mm']for r in a),max_author_actual_normal_length_delta_mm=max(abs(r['first_normal_length_delta_mm'])for r in a),author_target_semantics_mismatch_count=len(mismatches),target_mismatch_types=dict(collections.Counter(r['target_classification']for r in mismatches)),corrected_actual_target_probes=len(correct),corrected_actual_target_family_results=famstats(correct),warning_components=len(w),warning_original_side_probes=len(ps),warning_normal_family_results=famstats(ps),warning_vertical_results={f:dict(count=len(rs),first_down_exit_z_range_mm=[min(r['first_down_exit_z_mm']for r in rs),max(r['first_down_exit_z_mm']for r in rs)],first_up_exit_z_range_mm=[min(r['first_up_exit_z_mm']for r in rs),max(r['first_up_exit_z_mm']for r in rs)],minimum_continuous_vertical_first_material_span_mm=min(r['continuous_vertical_first_material_span_mm']for r in rs),root_control_failures=sum(not r['controls_passed']for r in rs))for f in sorted(set(r['family']for r in w))for rs in [[r for r in w if r['family']==f]]},actual_support_lines=v,maximum_control_winding_deviation=max(abs(k['winding']-k['expected'])for r in a+correct+ps for k in r['controls']),method='Independent binary original STL, actual triangle winding-derived geometric normals rather than saved float32 normals; conservative AABB plus longdouble Moller-Trumbore full ray intersections, original face IDs and barycentrics. Full-original-triangle longdouble solid-angle controls at actual first material and next-air spans. Regenerate author162 requested seed rays, retain semantic target mismatches; add source-located corrected cylinder/canopy/rib probes and full top-down/bottom-up vertical material-air intervals. Warning probes are every original true-side midpoint, no bbox thickness substitutes. Finite probes, not global thickness, support-free or printability proof.',exception_approval=False)
 summary['roots_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();save('roots-summary',summary);save('roots-evidence',dict(summary=summary,author_designated_reconstructed=a,corrected_target_probes=correct,warning_components=w),True)
 print('ROOT SUMMARY',json.dumps({k:v for k,v in summary.items()if k!='actual_support_lines'}),flush=True)
