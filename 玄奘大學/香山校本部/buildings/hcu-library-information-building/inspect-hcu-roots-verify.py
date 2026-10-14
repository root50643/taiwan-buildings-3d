"""Original-STL local-normal and architecture-root audit for the HCU library candidate.
Run alongside model.stl, or pass --model /path/to/model.stl. Outputs are written
beside this script. No mesh repair, union, vertex merge, or geometry modification.
Requires numpy, trimesh and rtree. Any failed check is saved and exits nonzero.
Sampling cannot establish the mathematical continuous whole-object minimum wall,
actual slicer toolpaths, or physical print performance.
"""
from pathlib import Path
import gzip
import json,hashlib,time
import numpy as np,trimesh
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--model',type=Path,default=Path(__file__).with_name('model.stl'));args=parser.parse_args()
R=Path(__file__).resolve().parent;F=args.model.resolve()
EXPECTED='8ae3f5c554f88fe7cdcf4cfe240e81ddc40b00daecdd2796d787434f0f81f966'
assert hashlib.sha256(F.read_bytes()).hexdigest()==EXPECTED,'Unexpected STL revision'
m=trimesh.load(F,force='mesh',process=False)
tri=m.triangles; norms=m.face_normals
print('STL',len(tri),hashlib.sha256(F.read_bytes()).hexdigest(),flush=True)
EPS=1e-4
orig=m.triangles_center+EPS*norms;dirs=-norms
out=[]
for lo in range(0,len(tri),300):
 oo=orig[lo:lo+300];dd=dirs[lo:lo+300]
 hit,ray,face=m.ray.intersects_location(oo,dd,multiple_hits=True)
 ds=np.einsum('ij,ij->i',hit-oo[ray],dd[ray])
 for j in range(len(oo)):
  mask=(ray==j)&(ds>1e-8);inds=np.where(mask)[0]; inds=inds[np.argsort(ds[inds])]
  rows=[]
  for ix in inds:
   rec={'distance_mm':float(ds[ix]),'point_mm':hit[ix].tolist(),'face_id':int(face[ix]),'dot_ray_face_normal':float(dd[j]@norms[face[ix]])}
   if not rows or abs(rec['distance_mm']-rows[-1]['distance_mm'])>1e-6:rows.append(rec)
  out.append({'sample_face_id':lo+j,'surface_point_mm':m.triangles_center[lo+j].tolist(),'outside_ray_origin_mm':oo[j].tolist(),'direction':dd[j].tolist(),'outward_normal':norms[lo+j].tolist(),'all_hits':rows,'first_solid_normal_chord_mm':rows[1]['distance_mm']-rows[0]['distance_mm'] if len(rows)>=2 else None})
 print(lo+len(oo),flush=True)
report={'stl_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'method':'Original unprocessed STL triangle centroids, inward local face-normal rays from outward epsilon offset. All original hit face IDs, normal signs and hit coordinates retained. This scan is complemented below by independent inside/outside and identified-feature root checks; it is not a global minimum-wall certificate.','eps_mm':EPS,'face_count':len(tri),'samples':out}

from pathlib import Path
import numpy as np,trimesh,json,hashlib
m=trimesh.load(F,process=False);tri=m.triangles;nn=m.face_normals;cc=m.triangles_center;EPS=1e-4;S=1.15;B=1.6
old=report;assert old['stl_sha256']==hashlib.sha256(F.read_bytes()).hexdigest()
def contains(points):
 points=np.array(points);out=[]
 for lo in range(0,len(points),250):out.extend(m.contains(points[lo:lo+250]).tolist())
 return out
# Independent generic-direction parity from the ray library, on unmodified triangles.
for tag,pts in [('inside_surface',cc-EPS*nn),('outside_surface',cc+EPS*nn)]:
 flags=contains(pts)
 for s,b in zip(old['samples'],flags):s[tag]=b
 print(tag,'true',sum(flags),'n',len(flags),flush=True)
mid=[];after=[]
for s in old['samples']:
 a=s['all_hits'];o=np.array(s['outside_ray_origin_mm']);d=np.array(s['direction']);mid.append(o+d*(a[0]['distance_mm']+a[1]['distance_mm'])/2);after.append(o+d*(a[1]['distance_mm']+EPS))
for tag,pts in [('first_chord_midpoint_inside',mid),('after_first_exit_inside',after)]:
 flags=contains(pts)
 for s,b in zip(old['samples'],flags):s[tag]=b
 print(tag,'true',sum(flags),'n',len(flags),flush=True)
(R/'inspect-hcu-roots-all-faces.json.gz').write_bytes(gzip.compress(json.dumps(old,separators=(",",":")).encode(),mtime=0))

def mm(x,y,z):return np.array([x*S,y*S,B+z*S])
def cast(oo,dd,ids=None,labels=None):
 oo=np.array(oo);dd=np.array(dd);out=[]
 for lo in range(0,len(oo),250):
  origins=oo[lo:lo+250];directions=dd[lo:lo+250];hit,ray,face=m.ray.intersects_location(origins,directions,multiple_hits=True);ds=np.einsum('ij,ij->i',hit-origins[ray],directions[ray])
  for j in range(len(origins)):
   inds=np.where((ray==j)&(ds>1e-8))[0];inds=inds[np.argsort(ds[inds])];rows=[]
   for ix in inds:
    rec={'distance_mm':float(ds[ix]),'point_mm':hit[ix].tolist(),'face_id':int(face[ix]),'dot_ray_face_normal':float(directions[j]@nn[face[ix]])}
    if not rows or abs(rec['distance_mm']-rows[-1]['distance_mm'])>1e-6:rows.append(rec)
   out.append({'label':labels[lo+j]if labels is not None else None,'sample_face_id':int(ids[lo+j])if ids is not None else None,'ray_origin_mm':origins[j].tolist(),'direction':directions[j].tolist(),'all_hits':rows})
 return out
local=(cc-[0,0,B])/S
masks={
 'entry_two_piers_and_beam':(local[:,0]>=4)&(local[:,0]<=19.5)&(local[:,1]<=-49.3)&(local[:,2]>=4.1)&(local[:,2]<=14.3),
 'entry_clipped_round_cornice':(local[:,0]>=4.15)&(local[:,0]<=19.45)&(local[:,1]<-57.45)&(local[:,2]>12.4),
 'long_barrel_roof_and_service':(np.abs(local[:,0])<=7.01)&(local[:,1]>=-31.01)&(local[:,2]>=29.49),
 'side_roof_service':(local[:,0]>=-19.01)&(local[:,0]<=-13.99)&(local[:,1]>=34.99)&(local[:,1]<=43.01)&(local[:,2]>=29.49),
}
# Each region all face centroids plus 3 near-vertex and 3 near-edge points, 1% inset avoids shared-edge rays.
weights=np.array([[1/3]*3,[.98,.01,.01],[.01,.98,.01],[.01,.01,.98],[.495,.495,.01],[.495,.01,.495],[.01,.495,.495]])
oo=[];dd=[];ids=[];labels=[];surfaces=[]
for name,mask in masks.items():
 for f in np.where(mask)[0]:
  for w in weights:
   q=w@tri[f];oo.append(q+EPS*nn[f]);dd.append(-nn[f]);ids.append(f);labels.append(name);surfaces.append(q)
rows=cast(oo,dd,ids,labels)
inside=contains(np.array(surfaces)+EPS*np.array(dd));outside=contains(oo)
for row,q,ins,outs in zip(rows,surfaces,inside,outside):
 row['surface_point_mm']=q.tolist();row['inside_surface']=ins;row['outside_surface']=outs;h=row['all_hits'];row['first_solid_normal_chord_mm']=h[1]['distance_mm']-h[0]['distance_mm']if len(h)>=2 else None
mid=[];after=[]
for row in rows:
 h=row['all_hits'];o=np.array(row['ray_origin_mm']);d=np.array(row['direction']);assert len(h)>=2
 mid.append(o+d*(h[0]['distance_mm']+h[1]['distance_mm'])/2);after.append(o+d*(h[1]['distance_mm']+EPS))
for tag,pts in [('first_chord_midpoint_inside',mid),('after_first_exit_inside',after)]:
 flags=contains(pts)
 for r,b in zip(rows,flags):r[tag]=b
 print('DENSE',tag,'true',sum(flags),'n',len(flags),flush=True)
res={'stl_sha256':old['stl_sha256'],'method':'Original triangle normals with centroid and 1% inset barycentric vertex/edge probes. Original ray hits retained. Independent generic-direction parity for +/-0.0001 mm surface probes. Not a global continuous minimum-wall certificate.','sample_count':len(rows),'samples':rows}
(R/'inspect-hcu-roots-feature-dense.json.gz').write_bytes(gzip.compress(json.dumps(res,separators=(",",":")).encode(),mtime=0))
for name in masks:
 rr=[r for r in rows if r['label']==name];small=sorted(rr,key=lambda r:r['first_solid_normal_chord_mm']if r['first_solid_normal_chord_mm']is not None else -1)
 print('FEATURE',name,len(rr),'inside',sum(r['inside_surface']for r in rr),'outside',sum(r['outside_surface']for r in rr),'MIN10',[(r['sample_face_id'],r['surface_point_mm'],r['first_solid_normal_chord_mm'])for r in small[:10]],flush=True)
# Internal probes directly trace columns, narrow side-band roots, beam notches, roof roots and backing.
oo=[];dd=[];labels=[]
def add(name,p,d):oo.append(mm(*p));dd.append(np.array(d,float));labels.append(name)
for which,x in [('left',5.5),('right',18.1)]:
 for y in [-57.1,-54,-49.6]:
  for z in [4.2,4.31,8,12.75]:
   for axis in range(3):
    for sign in [-1,1]:
     d=np.eye(3)[axis]*sign;add('pier_'+which+f'_y{y}_z{z}_axis{axis}_sign{sign}',(x,y,z),d)
for which,sgn in [('left',-1),('right',1)]:
 for z in [5,15,26]:
  for y in [-49.06,-48.9]:
   for d in [(0,-1,0),(0,1,0),(-sgn,0,0),(sgn,0,0),(0,0,-1),(0,0,1)]:add('removed_outer_pilaster_'+which+f'_y{y}_z{z}',(sgn*58.05,y,z),d)
for x in [-5.5,0,5.5]:
 for y in [-30.8,0,40.9,41.5]:
  for z in [29.55,30]:
   # central arch may not include all edge points at z30; inside statuses explicitly retained.
   for d in [(0,0,-1),(0,0,1),(0,1,0),(0,-1,0)]:add(f'barrel_root_x{x}_y{y}_z{z}',(x,y,z),d)
for x in [-6.8,0,6.8]:
 for y in [41.2,45,48.8]:
  for z in [29.35,31]:
   for d in [(0,0,-1),(0,0,1),(0,1,0),(0,-1,0)]:add(f'service_root_x{x}_y{y}_z{z}',(x,y,z),d)
for x in [5,11,18.5]:
 for y in [-58.05,-57.5,-56.8]:
  for d in [(0,0,-1),(0,0,1),(0,-1,0),(0,1,0)]:add(f'cornice_x{x}_y{y}',(x,y,14.05),d)
# Every short facade centroid: trace into solid behind relief, away from the small normal chord.
for s in old['samples']:
 if s['first_solid_normal_chord_mm']<.8:
  q=np.array(s['surface_point_mm'])+EPS*np.array(s['direction'])
  oo.append(q);dd.append([0,1,0]);labels.append('sub0p8_face_'+str(s['sample_face_id'])+'_backing')
# Both directions are retained for every subreference centroid to distinguish shallow cuts from air-backed sheets.
for sample in old['samples']:
 if sample['first_solid_normal_chord_mm']<.8:
  q=np.array(sample['surface_point_mm'])+EPS*np.array(sample['direction'])
  for d,label in [([0,-1,0],'forward_root'),([0,0,-1],'lower_root')]:
   oo.append(q);dd.append(d);labels.append('sub0p8_face_'+str(sample['sample_face_id'])+'_'+label)
# Rear porch corners and pier/wall junctions are checked after all source booleans.
for z in [12.65,13.85]:
 for axis in range(3):
  for sign in [-1,1]:add(f'beam_rear_join_z{z}_axis{axis}_sign{sign}',(4.375,-49.21,z),np.eye(3)[axis]*sign)
for x in [5.5,18.1]:
 for y in [-49.29,-49.0,-48.51]:
  for z in [5.5,10,12.7]:
   for d in [(0,-1,0),(0,1,0)]:add(f'pier_wall_join_x{x}_y{y}_z{z}',(x,y,z),d)
for z in [29.7,30.3]:
 for d in [(0,0,-1),(0,0,1)]:add(f'side_service_root_z{z}',(-16.5,39,z),d)
rr=cast(oo,dd,labels=labels);flags=contains(oo)
for r,b in zip(rr,flags):r['origin_inside']=b
(R/'inspect-hcu-roots-root-rays.json.gz').write_bytes(gzip.compress(json.dumps({'stl_sha256':old['stl_sha256'],'method':'Internal intended-root probes with original ray face IDs/hits and independent generic-direction inside test; all non-inside probes are explicitly retained as air or boundary, not evidence of solid.','samples':rr},separators=(',',':')).encode(),mtime=0))
print('ROOTS',len(rr),'inside',sum(flags),flush=True)

# Fail-closed checks and physical classifications of every short centroid chord.
checks={}
checks['exact_original_stl_sha']=hashlib.sha256(F.read_bytes()).hexdigest()==EXPECTED
checks['all_original_face_samples_complete']=len(old['samples'])==len(tri)
def sided(s):return s['inside_surface'] and not s['outside_surface'] and s['first_chord_midpoint_inside'] and not s['after_first_exit_inside']
checks['all_original_faces_inside_outside_and_first_interval']=all(sided(s)for s in old['samples'])
checks['all_dense_samples_inside_outside_and_first_interval']=all(sided(s)for s in rows)
checks['all_dense_designated_architectural_chords_at_least_0p8mm']=all(s['first_solid_normal_chord_mm'] is not None and s['first_solid_normal_chord_mm']>=.8 for s in rows)
by={r['label']:r for r in rr};groups={};short=[]
for s in old['samples']:
 if s['first_solid_normal_chord_mm']>=.8:continue
 fi=s['sample_face_id'];q=(np.array(s['surface_point_mm'])-[0,0,B])/S
 back=by[f'sub0p8_face_{fi}_backing'];down=by[f'sub0p8_face_{fi}_lower_root'];fw=by[f'sub0p8_face_{fi}_forward_root']
 def first(r):return r['all_hits'][0]if r['all_hits']else None
 bh=first(back);dh=first(down);fh=first(fw)
 if q[1]<-57:
  kind='grounded_entry_step_edge';ok=(-60.001<=q[1]<=-57.69 and q[2]<4.101 and dh is not None and abs(dh['point_mm'][2])<1e-6)
 elif q[2]<4.01:
  kind='grounded_front_terrace_or_recess_corner';ok=(abs(q[0])<=57.801 and -49.301<=q[1]<=-48.879 and bh is not None and bh['distance_mm']>17 and dh is not None and abs(dh['point_mm'][2])<1e-6)
 else:
  kind='shallow_backed_facade_relief_or_recess_edge';ok=(abs(q[0])<=57.801 and -49.121<=q[1]<=-48.879 and bh is not None and bh['distance_mm']>17)
 ok=ok and back['origin_inside'] and down['origin_inside'] and fw['origin_inside']
 row={'face_id':fi,'kind':kind,'surface_point_mm':s['surface_point_mm'],'first_normal_solid_chord_mm':s['first_solid_normal_chord_mm'],'continuous_backing_first_exit_mm':bh,'continuous_forward_root_first_exit_mm':fh,'lower_first_exit_mm':dh,'classification_passed':bool(ok)}
 short.append(row);groups.setdefault(kind,[]).append(row)
checks['every_subreference_centroid_located_and_backed_or_grounded']=all(s['classification_passed']for s in short)
# The removed outer strips must be air; other deliberate interior root probes must be solid.
actual=[r for r in rr if not r['label'].startswith('removed_outer_pilaster_')]
removed=[r for r in rr if r['label'].startswith('removed_outer_pilaster_')]
checks['all_intended_internal_root_origins_inside']=all(r['origin_inside']for r in actual)
checks['former_outer_strip_probe_positions_are_air']=all(not r['origin_inside']for r in removed)
piervertical=[r for r in rr if r['label'].startswith('pier_')and '_axis2_'in r['label']]
checks['both_piers_continuous_to_base_and_upper_beam']=all(r['all_hits']and ((abs(r['all_hits'][0]['point_mm'][2])<1e-6)if r['direction'][2]<0 else(r['all_hits'][0]['point_mm'][2]>=17.69999))for r in piervertical)
widths=[]
for side in ['left','right']:
 for y in [-57.1,-54,-49.6]:
  a=by[f'pier_{side}_y{y}_z8_axis0_sign-1'];b=by[f'pier_{side}_y{y}_z8_axis0_sign1'];widths.append(a['all_hits'][0]['distance_mm']+b['all_hits'][0]['distance_mm'])
checks['both_piers_transverse_solid_width_at_least_2p06mm']=min(widths)>=2.06
rear=[]
for z in [12.65,13.85]:
 dims=[]
 for axis in range(3):
  a=by[f'beam_rear_join_z{z}_axis{axis}_sign-1'];b=by[f'beam_rear_join_z{z}_axis{axis}_sign1'];dims.append(a['all_hits'][0]['distance_mm']+b['all_hits'][0]['distance_mm'])
 rear.append({'probe_local_model':[4.375,-49.21,z],'three_axis_first_solid_spans_mm':dims})
checks['beam_rear_join_has_full_17p48mm_width_and_1p725mm_height']=all(r['three_axis_first_solid_spans_mm'][0]>=17.479 and r['three_axis_first_solid_spans_mm'][2]>=1.724 for r in rear)
join=[r for r in rr if r['label'].startswith('pier_wall_join_')]
checks['both_pier_back_edges_join_wall_without_window_cut_gap']=all(r['origin_inside']and r['all_hits'] and r['all_hits'][0]['distance_mm']>=8 for r in join)
bar=[r for r in rr if r['label'].startswith(('barrel_root_','service_root_','side_service_root_'))and r['direction']==[0.0,0.0,-1.0]]
# At service rear overhang y48.8, the solid root is the original thick roof soffit, rather than the ground base.
rooted_bar=[r for r in bar if '_y48.8_' not in r['label']]
checks['roof_and_service_supported_core_vertical_roots']=all(r['origin_inside']and r['all_hits']and r['all_hits'][0]['point_mm'][2]<=B+26.70001*S for r in rooted_bar)
rear_service=[]
for x in [-6.8,0,6.8]:
 for z in [29.35,31]:
  name=f'service_root_x{x}_y48.8_z{z}';hitrows=[r for r in rr if r['label']==name]
  down=next(r for r in hitrows if r['direction']==[0.,0.,-1.]);up=next(r for r in hitrows if r['direction']==[0.,0.,1.]);front=next(r for r in hitrows if r['direction']==[0.,-1.,0.])
  rear_service.append({'label':name,'vertical_first_solid_span_mm':down['all_hits'][0]['distance_mm']+up['all_hits'][0]['distance_mm'],'continuous_forward_root_mm':front['all_hits'][0]['distance_mm'],'underside_z_mm':down['all_hits'][0]['point_mm'][2],'air_gap_to_lower_roof_mm':down['all_hits'][1]['distance_mm']-down['all_hits'][0]['distance_mm']})
checks['rear_service_short_thick_overhang_has_forward_root']=all(r['vertical_first_solid_span_mm']>=3.219 and r['continuous_forward_root_mm']>=8.969 and abs(r['underside_z_mm']-(B+29.2*S))<1e-5 and abs(r['air_gap_to_lower_roof_mm']-1.84)<1e-5 for r in rear_service)
feature_summary={}
for name in masks:
 sample=[r for r in rows if r['label']==name];minimum=min(sample,key=lambda r:r['first_solid_normal_chord_mm']);feature_summary[name]={'sample_count':len(sample),'minimum_first_solid_normal_chord_mm':minimum['first_solid_normal_chord_mm'],'minimum_sample':minimum}
summary={'stl_sha256':EXPECTED,'face_count':len(tri),'all_face_centroid_samples':len(old['samples']),'dense_feature_samples':len(rows),'root_ray_count':len(rr),'reference_width_mm':.8,'checks':checks,'passed':all(checks.values()),'features':feature_summary,'pier_transverse_widths_mm':widths,'beam_rear_join':rear,'rear_service_overhang_probes':rear_service,'rear_service_overhang_note':'The rear service block has a 0.575 mm rear projection beyond the solar-roof backing, plus narrow side margins; its vertical solid depth is 3.22 mm. The air gap below the rear projection is 1.84 mm. It is checked as a thick short cantilever with a continuous forward root, not falsely described as vertically solid to the base at every point.','short_chord_categories':{k:{'count':len(v),'minimum_first_normal_chord_mm':min(r['first_normal_solid_chord_mm']for r in v),'minimum_continuous_backing_mm':min(r['continuous_backing_first_exit_mm']['distance_mm']for r in v)}for k,v in groups.items()},'all_short_chord_classifications':short,'method':'Unmodified STL triangles, original winding normals and face IDs; local-normal rays start 0.0001 mm outside the surface. The first solid interval is checked by independent generic-direction parity at outside/inside surface points, its midpoint and after its exit. Centroids cover every original face. Selected architectural surfaces add seven barycentric probes per triangle. Short chords are not discarded: every one is independently localized to shallow backed relief or grounded step/terrace corner using retained directional root rays.','scope_limitations':['This is a finite sampling audit, not a mathematical continuous global minimum-wall certificate.','Shallow relief edges can have very small local-normal chords: minimum recorded 0.046001 mm; their independent supporting material is checked, but visual print resolution is not guaranteed.','No physical print, Cura/Prusa toolpath or support-free claim.','Use with the separate topology, layer-contour, per-Polygon erosion/opening, exact-rebuild and saved-scene checks.'],'raw_evidence_files':['inspect-hcu-roots-all-faces.json.gz','inspect-hcu-roots-feature-dense.json.gz','inspect-hcu-roots-root-rays.json.gz']}
summary['raw_evidence_sha256']={name:hashlib.sha256((R/name).read_bytes()).hexdigest()for name in summary['raw_evidence_files']}
summary['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(R/'inspect-hcu-roots-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'checks':checks,'passed':summary['passed'],'features':{k:{'sample_count':v['sample_count'],'minimum_first_solid_normal_chord_mm':v['minimum_first_solid_normal_chord_mm']}for k,v in feature_summary.items()}},separators=(',',':')))
assert summary['passed'],[k for k,v in checks.items()if not v]
