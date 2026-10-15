import math
def portable(o):
 if isinstance(o,float) and not math.isfinite(o): return None
 if isinstance(o,dict): return {k:portable(v)for k,v in o.items()}
 if isinstance(o,list): return [portable(v)for v in o]
 return o
from pathlib import Path
P=Path(__file__).parent/'classify_short.py';__file__=str(P);s=P.read_text();exec(s[:s.index('helper=')])
rows=json.loads((R/'individual-short-review.json').read_text());out=[]
for r in rows:
 f=r['face'];p=np.array(r['surface_mm']);n=nn[f];mid=p-n*r['classification_actual_span_mm']/2
 if p[0]<-68:
  family='north_upper_backed_mullion';direction=np.array([1.,0,0]);backing_coord=-57.65*1.2;projection=max(0,backing_coord-p[0]);barcenter=(T[f,:,1].mean()+T[r['first_exit_face'],:,1].mean())/2
 else:
  family='west_upper_backed_mullion'if p[1]<0 else 'east_upper_backed_mullion';direction=np.array([0.,1 if p[1]<0 else -1,0]);backing_coord=np.sign(p[1])*24.65*1.2;projection=max(0,abs(p[1])-abs(backing_coord));barcenter=(T[f,:,0].mean()+T[r['first_exit_face'],:,0].mean())/2
 vertex_projection=float((backing_coord-T[f,:,0]).max()) if p[0]<-68 else float((abs(T[f,:,1])-abs(backing_coord)).max())
 hh=sorted(solid.ray_cast(mid,mid+direction*1000),key=lambda h:h.distance);hits=[h for h in hh if h.distance>1e-12]
 assert hits
 rootlength=hits[0].distance*1000
 # Root is geometrically predetermined toward the common original wall backing, never a chosen maximum ray.
 out.append({**r,'feature_family':family,'bar_center_axis_mm':round(float(barcenter),4),'root_start_first_solid_midpoint_mm':mid.tolist(),'root_direction_to_original_wall':direction.tolist(),'first_root_exit_mm':rootlength,'first_root_exit_original_face':int(remap[hits[0].face_id]),'original_root_hits':[{'distance_mm':h.distance*1000,'original_face':int(remap[h.face_id])}for h in hits],'projection_from_original_window_backing_mm':projection,'max_original_face_vertex_projection_mm':vertex_projection,'root_over_0_8':bool(rootlength>=.8),'not_free_standing':True})
with gzip.open(R/'backed-mullions-original-roots.json.gz','wt')as f:json.dump(portable({'stl_sha256':hashlib.sha256(raw).hexdigest(),'method':'All 2996 original normal short chords are opposite side faces of 107 thin backed relief mullions. Root from first material midpoint along predetermined inward original wall direction. All first exit faces retained. Not a global minimum-thickness proof or approval.','rows':out}),f)
s={'samples':len(out),'actual_mullions':len({(r['feature_family'],r['bar_center_axis_mm'])for r in out}),'normal_first_solid_mm_range':[min(r['first_solid_mm']for r in out),max(r['first_solid_mm']for r in out)],'max_exposed_relief_projection_mm':max(r['projection_from_original_window_backing_mm']for r in out),'max_all_original_short_face_vertex_projection_mm':max(r['max_original_face_vertex_projection_mm']for r in out),'minimum_first_continuous_root_mm':min(r['first_root_exit_mm']for r in out),'under0_8_root_count':sum(not r['root_over_0_8']for r in out),'by_family':dict(collections.Counter(r['feature_family']for r in out)),'limited_exception_pending':True}
(R/'backed-mullions-summary.json').write_text(json.dumps(s,indent=2));print(s)
