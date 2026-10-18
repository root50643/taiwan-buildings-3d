from pathlib import Path
import json, hashlib, math, sys, argparse
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, Point, LineString, box

HERE=Path(__file__).resolve().parent
OUT=HERE if (HERE/'input-original.stl').exists() else next((HERE/'candidate-repo').rglob('check_layers.py')).parent/'qa/risk-followup-e45f8d6'
parser=argparse.ArgumentParser()
parser.add_argument('--input',default='input-original.stl')
parser.add_argument('--expected-sha',default='9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8')
parser.add_argument('--reference',default='input-layer-check-original.json')
parser.add_argument('--output',default='layer_loss_components.json')
args=parser.parse_args()
INPUT=OUT/args.input
EXPECTED=args.expected_sha
assert hashlib.sha256(INPUT.read_bytes()).hexdigest()==EXPECTED
mesh=trimesh.load(INPUT,force='mesh',process=True)
cache={}
tri=np.asarray(mesh.triangles)
def vertical_interval(x,y,z):
 # Intersection with the same fixed XY, no sampling offset. Inclusive edge
 # hits are clustered within 1e-6 mm to avoid double-counting triangulation.
 a=tri[:,0,:2];b=tri[:,1,:2];c=tri[:,2,:2]
 v0=b-a;v1=c-a;v2=np.array([x,y])-a
 den=v0[:,0]*v1[:,1]-v1[:,0]*v0[:,1]
 valid=np.abs(den)>1e-12
 u=np.zeros(len(tri));v=np.zeros(len(tri))
 u[valid]=(v2[valid,0]*v1[valid,1]-v1[valid,0]*v2[valid,1])/den[valid]
 v[valid]=(v0[valid,0]*v2[valid,1]-v2[valid,0]*v0[valid,1])/den[valid]
 valid &= (u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
 hits=np.sort(tri[valid,0,2]+u[valid]*(tri[valid,1,2]-tri[valid,0,2])+v[valid]*(tri[valid,2,2]-tri[valid,0,2]))
 unique=[]
 for h in hits:
  if not unique or abs(h-unique[-1])>1e-6:unique.append(float(h))
 intervals=[unique[i:i+2] for i in range(0,len(unique)-1,2)]
 containing=[p for p in intervals if p[0]-1e-6<=z<=p[1]+1e-6]
 return dict(all_solid_z_intervals_mm=intervals,containing_flag_interval_mm=containing,containing_vertical_solid_depth_mm=max((q-p for p,q in containing),default=None),unpaired_surface_hits=len(unique)%2)
def axis_lengths(region,rp):
 x,y=rp.x,rp.y
 out={}
 for axis,line in [('x',LineString([(-200,y),(200,y)])),('y',LineString([(x,-200),(x,200)]))]:
  g=region.intersection(line)
  parts=[g] if g.geom_type=='LineString' else list(g.geoms) if hasattr(g,'geoms') else []
  connected=[p for p in parts if p.distance(rp)<1e-6]
  out[f'containing_{axis}_chord_mm']=max((p.length for p in connected),default=None)
  out[f'containing_{axis}_chord_endpoints_mm']=[list(p.coords) for p in connected]
 return out
def section(z):
 if z in cache:return cache[z]
 seg=trimesh.intersections.mesh_plane(mesh,[0,0,1],[0,0,float(z)])
 pts=seg[:,:,:2].reshape(-1,2); parent=list(range(len(pts)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for aa,bb in cKDTree(pts).query_pairs(1e-4):
  aa,bb=find(aa),find(bb)
  if aa!=bb:parent[bb]=aa
 adj={};edges=set()
 for i in range(0,len(pts),2):
  a=tuple(pts[find(i)]);b=tuple(pts[find(i+1)])
  if a==b:continue
  edges.add(tuple(sorted([a,b])))
 for a,b in edges:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
 assert edges and all(len(v)==2 for v in adj.values()), z
 region=Polygon();unused=set(edges)
 while unused:
  a,b=next(iter(unused));start=a;points=[a];prev=a;cur=b;unused.remove(tuple(sorted([a,b])))
  while cur!=start:
   points.append(cur);nxt=next(x for x in adj[cur] if x!=prev)
   unused.discard(tuple(sorted([cur,nxt])));prev,cur=cur,nxt
  poly=Polygon(points);assert poly.is_valid
  region=region.symmetric_difference(poly)
 cache[z]=region
 return region
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in g.geoms for p in polys(x)]
def metric(g):
 return dict(area_mm2=float(g.area),bounds_xy_mm=list(g.bounds),wkt=g.wkt)
def classify(p,z):
 x0,y0,x1,y1=p.bounds
 if p.area<.001:return 'subthreshold_boundary_residue_not_physically_classified'
 if x0>=16.9 and x1<=34 and -20.2<=y0<=-18.3 and 7<z<38.1:
  return 'connector_vertical_relief_rib'
 if -57<x0 and x1<9 and -45<y0 and y1<-4 and z>=39:
  if y0<-40:return 'new_low_roof_slope_boundary'
  if EXPECTED=='00f6bbdd09196fba873d843bb9d50a1c3aad4e19e760978333dce6f49740627c':return 'new_r2_roof_slope_boundary'
  if y1<=-7.69:return 'new_main_roof_slope_boundary'
  return 'new_clerestory_actual_thin_crescent'
 if 4<x0 and x1<6 and y0<-53 and z<33:
  return 'existing_stair_cheek_sloping_tip'
 return 'unresolved'
rows=[]
for z in np.arange(.100013,mesh.bounds[1,2],.2):
 region=section(float(z)); opened=region.buffer(-.4,join_style=2).buffer(.4,join_style=2)
 lost=region.difference(opened)
 if lost.area>.2:
  comp=[]
  for p in sorted(polys(lost),key=lambda p:(-p.area,p.bounds)):
   r=metric(p);r['classification']=classify(p,z)
   # Same fixed plane: neighbourhood solid occupancy and opening contact.
   rp=p.representative_point(); r['representative_xy_mm']=list(rp.coords)[0]
   for radius in [.4,.8,1.6]:
    disk=rp.buffer(radius,resolution=64)
    r[f'local_solid_area_r{radius}_mm2']=float(region.intersection(disk).area)
   r['distance_to_retained_core_mm']=float(p.distance(region.intersection(opened)))
   r['contact_length_with_retained_core_mm']=float(p.boundary.intersection(opened.boundary.buffer(1e-7)).length)
   if p.area>=.001:
    r.update(axis_lengths(region,rp))
    r.update(vertical_interval(rp.x,rp.y,float(z)))
    # Same XY component bbox at fixed adjacent planes, never substituted for
    # the original warning plane. These local sections reveal taper direction.
    window=box(*p.bounds)
    r['same_bbox_adjacent_plane_solid_area_mm2']={str(d):float(section(float(z+d)).intersection(window).area) for d in [-.4,-.2,0,.2,.4]}
   comp.append(r)
  rows.append(dict(z_mm=round(float(z),5),actual_z_mm=float(z),loss_area_mm2=float(lost.area),section_area_mm2=float(region.area),solid_contour_components=len(polys(region)),lost_components=comp))
report=dict(input_sha256=EXPECTED,original_threshold_width_mm=.8,original_threshold_loss_area_mm2=.2,actual_z_formula='.100013 + index*.2 using numpy arange',classification_area_bucket_mm2=.001,classification_bucket_does_not_change_original_screen=True,flagged_layers=len(rows),layers=rows)
refpath=OUT/args.reference
assert refpath.exists(), 'The fixed original layer-check reference is required'
if refpath.exists():
 ref=json.loads(refpath.read_text())
 assert ref['stl_sha256']==EXPECTED
 assert len(rows)==ref['thin_screen']['flagged_layers']
 assert [r['z_mm'] for r in rows]==[r['z_mm'] for r in ref['thin_screen']['flagged_heights']]
 assert all(abs(r['loss_area_mm2']-o['opening_loss_area_mm2'])<.000006 for r,o in zip(rows,ref['thin_screen']['flagged_heights']))
 report['original_record_reproduction']={'flagged_heights_match':True,'all_loss_areas_match_to_original_5_decimals':True,'record_sha256':hashlib.sha256(refpath.read_bytes()).hexdigest()}
from collections import Counter
counts=Counter();compcounts=Counter();areas=Counter();ranges={}
for row in rows:
 classes=set()
 for p in row['lost_components']:
  c=p['classification'];classes.add(c);compcounts[c]+=1;areas[c]+=p['area_mm2'];ranges.setdefault(c,[]).append(row['z_mm'])
 counts.update(classes)
report['classification_summary']={c:dict(flagged_layer_count=counts[c],lost_component_count=compcounts[c],sum_fixed_section_loss_area_mm2=areas[c],z_range_mm=[min(ranges[c]),max(ranges[c])]) for c in counts}
resvals=[sum(p['area_mm2'] for p in r['lost_components'] if p['classification']=='subthreshold_boundary_residue_not_physically_classified') for r in rows]
resmax=max(resvals,default=0);residx=resvals.index(resmax) if resvals else None
flagmax=max(rows,key=lambda r:r['loss_area_mm2']) if rows else None
report['residual_scale_evidence']={'residual_total_fixed_section_area_mm2':sum(resvals),'residual_total_divided_by_single_layer_threshold_for_scale_only':sum(resvals)/.2,'residual_max_single_layer_area_mm2':resmax,'residual_max_single_layer_z_mm':rows[residx]['z_mm'] if residx is not None else None,'residual_max_single_layer_divided_by_threshold':resmax/.2,'max_flag_loss_area_mm2':flagmax['loss_area_mm2'] if flagmax else 0,'max_flag_height_mm':flagmax['z_mm'] if flagmax else None,'max_flag_divided_by_threshold':flagmax['loss_area_mm2']/.2 if flagmax else 0}
(OUT/args.output).write_text(json.dumps(report,indent=2))
(OUT/(Path(args.output).stem+'-summary.json')).write_text(json.dumps({k:v for k,v in report.items() if k!='layers'},indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='layers'},indent=2))
