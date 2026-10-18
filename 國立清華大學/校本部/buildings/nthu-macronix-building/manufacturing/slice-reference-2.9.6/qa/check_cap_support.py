"""Relate the first cap overhang path to its actual generated interface."""
from pathlib import Path
import gzip,json,hashlib,collections
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
H=Path(__file__).resolve().parent;out=H/'cap-support-link.json'
if out.exists():raise FileExistsError('Keep the original output.')
SUP={'Support material','Support material interface'};model=[];support=[]
for line in gzip.open(H/'positive-extrusion-segments.jsonl.gz','rt'):
 s=json.loads(line);z=s['p1'][2]
 if s['role'] in SUP and 53.0<z<54.3:support.append(s)
 elif s['role'] not in SUP and s['role']!='Skirt/Brim' and z in [54.15,54.3]:model.append(s)
def fp(rows):return unary_union([LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2,quad_segs=8) for s in rows])
roi=box(-40,-11.5,-4,-4.5);now=fp([s for s in model if s['p1'][2]==54.3])&roi;prior=fp([s for s in model if s['p1'][2]==54.15])&roi
pieces=list(now.geoms) if hasattr(now,'geoms') else [now]
outer=next(p for p in pieces if p.intersection(prior).area<1e-8)
selected=[s for s in model if s['p1'][2]==54.3 and LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2,quad_segs=8).intersection(outer).area>1e-8]
lower=min(s['p1'][2]-s['height'] for s in selected)
byz=collections.defaultdict(list)
for s in support:byz[s['p1'][2]].append(s)
links=[]
for z,rows in sorted(byz.items()):
 inter=fp(rows)&outer
 if inter.area>1e-8:links.append(dict(support_Z_top_mm=z,overlap_in_XY_mm2=inter.area,declared_model_bead_bottom_minus_support_top_mm=lower-z,roles=dict(collections.Counter(s['role'] for s in rows if LineString([s['p0'][:2],s['p1'][:2]]).buffer(s['width']/2,quad_segs=8).intersection(outer).area>1e-8))))
d=dict(gcode_sha256=json.loads((H/'support-audit.json').read_text())['gcode_sha256'],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_same_layer_and_prior_model_only_split_retained=True,cap_outer_component_Z_top_mm=54.3,cap_outer_component_area_mm2=outer.area,actual_cap_paths=dict(segments=len(selected),line_numbers=[s['line'] for s in selected],roles=dict(collections.Counter(s['role'] for s in selected)),declared_widths_mm=sorted({s['width'] for s in selected}),declared_heights_mm=sorted({s['height'] for s in selected}),lowest_declared_deposited_Z_mm=lower),actual_support_interface_under_outer_path=links,interpretation='The outer cap at Z54.3 is an overhang extrusion with its declared HEIGHT, not an absent line or an automatically unsupported floating island. Use the actual lower bead Z and actual support interface Z to read the configured contact gap. XY overlap / declared dimensions do not prove material flow, sag, bond or removable support.',physical_print_test=False,support_removal_demonstrated=False)
out.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps(d,indent=2))
