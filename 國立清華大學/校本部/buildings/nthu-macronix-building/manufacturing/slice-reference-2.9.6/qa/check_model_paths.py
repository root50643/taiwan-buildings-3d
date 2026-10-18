"""Audit actual reference model paths; no slicing or geometry modification.

Run audit_supports.py first. Its JSONL contains actual positive deposition,
including declared width/height, model coordinates, and original G-code lines.
This script makes a finite 2D bead-footprint screen, not a flow simulation.
"""
from pathlib import Path
import argparse,gzip,json,hashlib,collections,math
import numpy as np
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from manifold3d import Manifold,Mesh64
import trimesh

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--segments',type=Path,default=HERE/'positive-extrusion-segments.jsonl.gz');ap.add_argument('--stl',type=Path,required=True);ap.add_argument('--output',type=Path,default=HERE/'model-path-audit.json');a=ap.parse_args()
if a.output.exists():raise FileExistsError('Keep existing evidence; choose a new output.')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.stl)=='6801f9c41c9fd986df4167523ec36195e715d6a38a680c09aff002cba1351b2a'
SUP={'Support material','Support material interface'}
layers=collections.defaultdict(list);counts=collections.Counter()
for line in gzip.open(a.segments,'rt',encoding='utf-8'):
 s=json.loads(line);counts[s['role']]+=1
 if s['role']!='Skirt/Brim':layers[round(s['p1'][2],6)].append(s)
assert counts['Support material']==29675 and counts['Support material interface']==25019
def intersects(s,bounds):
 lo,hi=np.array(bounds[0]),np.array(bounds[1]);p=np.array(s['p0']);q=np.array(s['p1']);r=s['width']/2
 return bool(np.all(np.maximum(p,q)>=lo-np.array([r,r,s['height']])) and np.all(np.minimum(p,q)<=hi+np.array([r,r,0])))
def footprint(rows):
 return unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2,quad_segs=8) for s in rows]) if rows else Polygon()
def polys(p):return list(p.geoms) if hasattr(p,'geoms') else ([] if p.is_empty else [p])
Gbox=[[16.1,-20.5,7],[33.9,-17.9,38]]
grows=[];gridge=[];gmissing=[]
for z,rows in sorted(layers.items()):
 model=[s for s in rows if s['role'] not in SUP and intersects(s,Gbox)]
 if not model:continue
 h=float(np.median([s['height'] for s in model]));mid=z-h/2
 if not 7<mid<38:continue
 f=footprint(model)
 rec=dict(Z_top_mm=z,midheight_reference_mm=mid,model_positive_segments=len(model),line_range=[min(s['line'] for s in model),max(s['line'] for s in model)],extrusion_width_range_mm=[min(s['width'] for s in model),max(s['width'] for s in model)],roles=dict(collections.Counter(s['role'] for s in model)),vertical_fins=[])
 for x in [18,23,28,33]:
  target=box(x-.4,-20.1,x+.4,-18.3);corridor=box(x-.55,-20.15,x+.55,-18.0);pieces=polys(f&corridor)
  front=box(x-.4,-20.11,x+.4,-19.9);back=box(x-.55,-18.3,x+.55,-18.0)
  connected=any(p.intersection(front).area>1e-8 and p.intersection(back).area>1e-8 for p in pieces)
  rr=dict(X_mm=x,continuous_bead_footprint_from_front_to_backwall=connected,target_area_coverage_fraction=float(f.intersection(target).area/target.area))
  rec['vertical_fins'].append(rr)
  if not connected:gmissing.append(dict(Z_top_mm=z,feature='vertical',X_mm=x,line_range=rec['line_range']))
 for low in [14,21,28,35]:
  if low<mid<low+.8:
   target=box(16.5,-20.1,33.5,-18.3);parts=polys(f&box(16.45,-20.15,33.55,-18.0));connected=any(p.intersection(box(16.6,-20.11,16.9,-19.9)).area>1e-8 and p.intersection(box(33.1,-20.11,33.4,-19.9)).area>1e-8 for p in parts)
   rr=dict(Z_top_mm=z,horizontal_bar_bottom_mm=low,continuous_front_bead_footprint_across_bar=connected,target_area_coverage_fraction=float(f.intersection(target).area/target.area),model_positive_segments=len(model),bridge_segments=sum(s['role']=='Bridge infill' for s in model),line_range=rec['line_range'])
   gridge.append(rr)
   if not connected:gmissing.append(dict(Z_top_mm=z,feature='horizontal',bottom_Z_mm=low,line_range=rec['line_range']))
 grows.append(rec)

roofboxes=dict(A_roof=[[-53,-45,39.5],[9,-6.9,51.86]],B_cap=[[-40,-11.5,54.1],[-4,-4.5,55.4]])
roof={}
for name,bounds in roofboxes.items():
 rr=[]
 for z,rows in sorted(layers.items()):
  m=[s for s in rows if s['role'] not in SUP and intersects(s,bounds)]
  if not m:continue
  f=footprint(m);pieces=polys(f);bridges=[s for s in m if s['role']=='Bridge infill']
  rr.append(dict(Z_top_mm=z,positive_segments=len(m),roles=dict(collections.Counter(s['role'] for s in m)),width_range_mm=[min(s['width'] for s in m),max(s['width'] for s in m)],path_connected_components=len(pieces),smallest_component_area_mm2=min((p.area for p in pieces),default=None),line_range=[min(s['line'] for s in m),max(s['line'] for s in m)],bridge_segment_lengths_mm=[s['length'] for s in bridges],model_bbox_centerline=[np.min(np.array([s['p0'] for s in m]+[s['p1'] for s in m]),axis=0).tolist(),np.max(np.array([s['p0'] for s in m]+[s['p1'] for s in m]),axis=0).tolist()]))
 roof[name]=rr

# Actual deposited paths in selected windows, without moving or replacing data.
mesh=trimesh.load(a.stl,process=True)
solid=Manifold(Mesh64(np.ascontiguousarray(mesh.vertices),np.ascontiguousarray(mesh.faces,dtype=np.uint64)))
def section(z):
 out=Polygon()
 for ring in solid.slice(float(z)).to_polygons():out=out.symmetric_difference(Polygon(ring))
 return out
def lines(poly):
 for p in polys(poly):
  if p.is_empty:continue
  if hasattr(p,'exterior'):
   yield np.array(p.exterior.coords)
   for r in p.interiors:yield np.array(r.coords)
choices=[('G: thin relief, actual model layer',14.1,[16,-20.8,34,-17.5]),('C: first window bay / lip',31.75,[33,-23.2,63,-18]),('B: behind clerestory cap',53.7,[-41,-12.5,-3,-3.5]),('A: main roof edge',50.4,[-53,-13,9,-5]),('E: rear window / sill',23.55,[-65,9,65,31]),('G: upper thin relief',35.1,[16,-20.8,34,-17.5])]
fig,axs=plt.subplots(3,2,figsize=(14,11),layout='constrained');viewdata=[]
for ax,(title,target,xy) in zip(axs.flat,choices):
 z=min(layers,key=lambda v:abs(v-target));rows=layers[z];mid=z-float(np.median([s['height'] for s in rows]))/2
 for points in lines(section(mid)):ax.plot(points[:,0],points[:,1],color='#a9a9a9',lw=.5)
 for kind,col,lw in [('model','#147ca0',.7),('support','#d89300',1.1),('interface','#cc2d21',1.2),('bridge','#8953a3',1.0)]:
  def match(s):return (kind=='support' and s['role']=='Support material') or (kind=='interface' and s['role']=='Support material interface') or (kind=='bridge' and s['role']=='Bridge infill') or (kind=='model' and s['role'] not in SUP and s['role']!='Bridge infill')
  selected=[s for s in rows if match(s) and intersects(s,[[xy[0],xy[1],z],[xy[2],xy[3],z]])]
  ax.add_collection(LineCollection([[s['p0'][:2],s['p1'][:2]] for s in selected],colors=col,linewidths=lw))
  viewdata.append(dict(title=title,actual_Z_top_mm=z,kind=kind,line_numbers=[s['line'] for s in selected]))
 ax.set_xlim(xy[0],xy[2]);ax.set_ylim(xy[1],xy[3]);ax.set_aspect('equal');ax.set_title(f'{title}; Z={z:g} mm',fontsize=10);ax.set_xlabel('model X / mm');ax.set_ylabel('model Y / mm');ax.grid(alpha=.15)
fig.suptitle('ONE actual PrusaSlicer 2.9.6 reference slice — G-code 7f614cbe\nblue=model, orange=support, red=interface, purple=bridge; grey=STL section\nNOT MACHINE READY; not physically printed or support-removal validated',fontsize=12)
fig.savefig(HERE/'actual-path-sections.png',dpi=150)
report=dict(schema='actual-model-paths-finite-footprint-v1',stl_sha256=sha(a.stl),segment_cache_sha256=sha(a.segments),support_audit_gcode_sha256=json.loads((HERE/'support-audit.json').read_text())['gcode_sha256'],parser_role_counts=dict(counts),method='Declared G-code positive-deposition centerlines, width/2 round 2D buffers (8 chord subdivisions per quadrant), unioned per actual Z. Fin corridor connectivity requires one bead-footprint component to meet front and backwall test strips. This is a finite deposition-footprint screen, not calibrated flow, layer bonding, local mechanical strength or global path-proof.',G_vertical_layer_count=len(grows),G_vertical_fin_tests=4*len(grows),G_vertical_continuity_failures=sum(not r['continuous_bead_footprint_from_front_to_backwall'] for z in grows for r in z['vertical_fins']),G_horizontal_bar_layer_tests=len(gridge),G_horizontal_continuity_failures=sum(not r['continuous_front_bead_footprint_across_bar'] for r in gridge),G_unresolved_tests=gmissing,G_layers=grows,G_horizontal_layers=gridge,roof_and_cap_actual_layers=roof,visualization_line_references=viewdata,physical_print_test=False,support_removal_demonstrated=False,limitations=['A bead width comment and connected mathematical footprint do not prove real line width, adhesion or fin survival during hard-support removal.','Roof reports retain all components and bridge-length values. Connected same-layer paths do not alone prove prior-layer anchoring or bridge quality.','Selected plot Z values are explicit; plots do not replace a per-layer G-code viewer on the actual calibrated printer profile.','No geometry was changed and no second slice was performed.'])
a.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['G_vertical_layer_count','G_vertical_fin_tests','G_vertical_continuity_failures','G_horizontal_bar_layer_tests','G_horizontal_continuity_failures','G_unresolved_tests']},indent=2))
print(json.dumps({k:dict(layer_count=len(v),first_Z=v[0]['Z_top_mm'],last_Z=v[-1]['Z_top_mm'],component_counts=dict(collections.Counter(x['path_connected_components'] for x in v)),bridge_segments=sum(len(x['bridge_segment_lengths_mm']) for x in v)) for k,v in roof.items()},indent=2))
