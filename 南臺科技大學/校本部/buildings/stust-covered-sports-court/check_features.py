"""Geometry-bound architectural and local-manufacturing probes, not a print certificate."""
from pathlib import Path
import json,hashlib
import numpy as np,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,Point,box
A=Path(__file__).resolve().parent
j=json.loads((A/'mesh.json').read_text());v=np.array(j['vertices']);f=np.array(j['faces']);m=md.Manifold(md.Mesh(v.astype('float32'),f.astype('uint32')))
def cut(z):
 g=GeometryCollection()
 for c in m.slice(z).to_polygons():
  if len(c)>2:g=g.symmetric_difference(Polygon(c))
 return g
low=cut(10); checks={}
checks['18_column_centers_solid_at_z10']=all(low.covers(Point(x,y)) for x in [-53,53] for y in np.linspace(-120,120,9))
checks['center_span_clear_at_z10']=low.intersection(box(-40,-119,40,119)).is_empty
checks['south_end_clear_at_z10']=low.intersection(box(-40,-121,40,-119)).is_empty
checks['north_junction_clear_at_z10']=low.intersection(box(-40,119,40,121)).is_empty
# True continuous I cross-sections, not three parallel disconnected strips.
i12=cut(12);checks['exactly_18_continuous_I_columns_at_z12']=len(i12.geoms)==18
checks['each_I_column_web_joins_both_flanges']=all(i12.intersection(box(x-1.3,y-1.3,x+1.3,y+1.3)).geom_type=='Polygon' for x in [-53,53] for y in np.linspace(-120,120,9))
mid=cut(22);checks['east_shading_present']=mid.intersection(box(52,-118,56,118)).area>50
checks['west_no_mirrored_shading']=mid.intersection(box(-56,-118,-52,118)).area<100
checks['west_terraces_only']=cut(5).intersection(box(-65,-110,-56,-20)).area>200
checks['west_stair_break']=cut(7).intersection(box(-60,-15,-56,-5)).area<10
# Sloping roof: highest material vertices are ridge, eaves substantially lower.
roof=np.array(j['face_materials'])==4;rv=v[f[roof].ravel()];checks['ridge_six_mm_above_eave']=rv[abs(rv[:,0])<.01,2].max()-rv[abs(rv[:,0])>54,2].max()>5.9
records=json.loads((A/'qa/design-features.json').read_text())['parts'];checks['nine_named_portals']=len(set(x['name'] for x in records if x['name'].startswith('portal_beam_folded')))==9
checks['18_named_column_webs']=sum(x['name'].startswith('primary_column_web') for x in records)==18
checks['four_blue_courts']=sum(x['name'].startswith('court_') and x['name'].endswith('_blue') for x in records)==4
checks={k:bool(v) for k,v in checks.items()}
local=[]
for label,z,roi in [('east_blades',22,(52.8,-118,54,-92)),('basket_ring',14,(-46.8,-91.4,-43.8,-88.6)),('raised_white_lines',3.9,(-1,-115,1,-65)),('roof_ridge_tip',42.849,(-1,-121,1,121))]:
 g=cut(z).intersection(box(*roi));comps=list(g.geoms) if hasattr(g,'geoms') else [g]
 local.append(dict(feature=label,z_mm=z,region_mm=roi,area_mm2=g.area,positive_components=len(comps),components_vanishing_at_0_8mm=sum(x.buffer(-.4).is_empty for x in comps)))
d=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),checks=checks,all_architecture_checks_pass=all(checks.values()),local_clipped_slices=local,supports_required=True,largest_clear_span_mm=103.6,roof_overhang_mm_approx=2,blade_thickness_mm=.65,marking_width_mm=.35,roof_vertical_thickness_mm=.85,physical_print_tested=False,warning='Global component erosion does not establish local wall thickness. Local clipped regions expose sub-0.8mm blades, rings and lines. Large unsupported roof and hoop arms require support or a user-designed split/orientation. No print-ready/no-support claim.')
(A/'qa/feature-validation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d));assert all(checks.values())
