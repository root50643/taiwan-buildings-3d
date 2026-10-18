"""Interpret same-layer footprint splits using actual preceding model paths.

No initial screen is changed. Intersection is a deposited-width geometric
overlap only, not a proof of real interlayer adhesion or bridge quality.
"""
from pathlib import Path
import gzip,json,hashlib,collections
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
HERE=Path(__file__).resolve().parent
output=HERE/'model-path-layer-supplement.json'
if output.exists():raise FileExistsError('Preserve existing evidence.')
original=HERE/'model-path-audit.json';report=json.loads(original.read_text())
SUP={'Support material','Support material interface','Skirt/Brim'}
layers=collections.defaultdict(list)
for line in gzip.open(HERE/'positive-extrusion-segments.jsonl.gz','rt'):
 s=json.loads(line)
 if s['role'] not in SUP:layers[round(s['p1'][2],6)].append(s)
def fp(z,roi):
 rows=[]
 for s in layers[z]:
  p=s['p0'];q=s['p1'];r=s['width']/2
  if max(p[0],q[0])+r>=roi[0] and min(p[0],q[0])-r<=roi[2] and max(p[1],q[1])+r>=roi[1] and min(p[1],q[1])-r<=roi[3]:rows.append(s)
 return unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2,quad_segs=8) for s in rows])&box(*roi)
def components(p):return list(p.geoms) if hasattr(p,'geoms') else ([] if p.is_empty else [p])
zs=sorted(layers);g=[];cache={}
for row in report['G_unresolved_tests']:
 if row['feature']!='vertical':continue
 z=row['Z_top_mm'];prev=max(x for x in zs if x<z);x=row['X_mm'];roi=[x-.55,-20.15,x+.55,-18.0]
 curr=fp(z,roi);below=fp(prev,roi);front=box(x-.4,-20.11,x+.4,-19.9)
 pieces=[p for p in components(curr) if p.intersection(front).area>1e-8]
 priorrow=next(r for r in report['G_layers'] if r['Z_top_mm']==prev)
 priorfin=next(r for r in priorrow['vertical_fins'] if r['X_mm']==x)
 g.append(dict(original_same_layer_test=row,previous_model_Z_mm=prev,previous_layer_fin_front_to_backwall_continuity=priorfin['continuous_bead_footprint_from_front_to_backwall'],front_component_overlaps_previous_deposition_area_mm2=[p.intersection(below).area for p in pieces],all_front_components_have_nonzero_prior_layer_overlap=bool(pieces) and all(p.intersection(below).area>1e-8 for p in pieces),current_horizontal_bar_layer=next(r for r in report['G_horizontal_layers'] if r['Z_top_mm']==z)))
roof=[]
for name,rr in report['roof_and_cap_actual_layers'].items():
 roi=[-53,-45,9,-6.9] if name=='A_roof' else [-40,-11.5,-4,-4.5]
 for r in rr:
  if r['path_connected_components']<2:continue
  z=r['Z_top_mm'];prev=max(x for x in zs if x<z);curr=fp(z,roi);below=fp(prev,roi)
  pieces=components(curr)
  roof.append(dict(region=name,Z_top_mm=z,previous_model_Z_mm=prev,original_same_layer_component_count=r['path_connected_components'],cropped_actual_component_count=len(pieces),components=[dict(area_mm2=p.area,bounds_mm=list(p.bounds),overlap_previous_model_deposition_area_mm2=p.intersection(below).area,distance_previous_model_deposition_mm=p.distance(below)) for p in pieces]))
d=dict(source_report_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),gcode_sha256=report['support_audit_gcode_sha256'],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),initial_same_layer_flags_retained=True,G_actual_layer_dependency_checks=g,roof_same_layer_splits_previous_layer_checks=roof,interpretation=['The 12 same-layer corridor failures occur at the first layers of four horizontal relief bars; actual extrusion runs across the bar and some bridge paths. They are not 12 absent fins or failed prints.','Each tested front component is separately checked for overlap with actual deposition at the previous model Z, whose fin path connects to the wall. This is a local 3D deposition-dependency observation, not measured interlayer strength.','Roof component counts may describe geometrically separated horizontal portions of the sloped roof. Prior-layer overlap is recorded rather than treating same-layer count>1 as a free floating island.','Support contact, extrusion calibration, bridge sag and hard-support damage remain untested physically. No second slice or geometry change.'],physical_print_test=False,support_removal_demonstrated=False)
output.write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps(dict(G_checks=len(g),G_all_nonzero_prior_overlap=all(r['all_front_components_have_nonzero_prior_layer_overlap'] for r in g),G_all_prior_fins_attached_to_wall=all(r['previous_layer_fin_front_to_backwall_continuity'] for r in g),roof_split_layers=len(roof),roof_components_without_prior_overlap=sum(p['overlap_previous_model_deposition_area_mm2']<=1e-8 for r in roof for p in r['components'])),indent=2))
