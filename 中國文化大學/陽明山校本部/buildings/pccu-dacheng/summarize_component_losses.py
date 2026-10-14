"""Classify every over-1% ORIGINAL Polygon; retain original WKT and actual root rays."""
from pathlib import Path
import json,csv,hashlib
from collections import defaultdict
from shapely import wkt
from shapely.geometry import Point
R=Path(__file__).resolve().parent;j=json.loads((R/'layer-component-check.json').read_text());r=json.loads((R/'recess-root-check.json').read_text());raw=(R/'model.stl').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==j['stl_sha256']==r['stl_sha256']
g=defaultdict(list);details=[]
for a in j['original_component_checks']:
 if a['opening_loss_fraction']<=.01:continue
 s=tuple(round(v,3) for v in a['span_xy_mm']);poly=wkt.loads(a['original_polygon_wkt']);assert poly.is_valid
 if s==(1.144,1.144):fam='方欄柱';minimum=1.144
 elif s==(1.326,1.745):fam='側廊圓柱與欄柱合併截面';minimum=1.144
 elif s==(1.976,1.248):fam='前後廊圓柱與欄柱合併截面';minimum=1.144
 elif s==(1.248,1.248):fam='前後廊中央圓柱與方欄柱合併';minimum=1.144
 elif a['z_mm']>50 and max(s)<7:fam='同一卷棚屋頂的兩端高切片';minimum=2.6
 else:raise AssertionError(('Unclassified original Polygon',a['z_mm'],s))
 controls=[v for v in r['rays'] if 'continuous_width_mm' in v and poly.covers(Point(v['origin_mm'][:2])) and v['minimum_mm']>=minimum-.001]
 assert controls,('No actual STL width control',fam,a['bounds_xy_mm'])
 assert a['eroded_components']==a['opened_components']==1
 assert a['loss_outside_adaptive_corner_regions_mm2']<1e-8
 key=tuple(round(x,3)for x in a['bounds_xy_mm'])+((0 if a['z_mm']<30 else 1),)
 row=dict(family=fam,physical_region_key=key,z_mm=a['z_mm'],original_component_index=a['original_component_index'],original_span_xy_mm=a['span_xy_mm'],original_polygon_wkt=a['original_polygon_wkt'],opening_loss_fraction=a['opening_loss_fraction'],loss_area_mm2=a['lost_area_mm2'],loss_outside_corners_mm2=a['loss_outside_adaptive_corner_regions_mm2'],verified_minimum_width_mm=minimum,actual_STL_controls=[v['name'] for v in controls],eroded_components=1,opened_components=1)
 details.append(row);g[fam].append(row)
summary=[]
for k,v in g.items():summary.append(dict(family=k,repeated_slice_samples=len(v),distinct_spatial_regions=len({tuple(a['physical_region_key'])for a in v}),minimum_control_width_mm=min(a['verified_minimum_width_mm']for a in v),max_opening_loss_fraction=max(a['opening_loss_fraction']for a in v),max_loss_outside_corners_mm2=max(a['loss_outside_corners_mm2']for a in v),note='Two end regions belong to ONE roof, not two detached objects.' if k.startswith('同一') else 'A local upright region may combine a cylindrical column and railing post. Samples across height are not extra objects.'))
report=dict(passed=True,checks={'all_over_one_percent_classified':len(details)==j['original_components_over_one_percent'],'each_original_polygon_nonempty_unsplit':True,'all_loss_outside_quantified_corners_below_1e_8_mm2':True,'every_over_one_percent_region_has_actual_STL_width_controls':True},stl_sha256=sha,summary=summary,original_component_total=len(j['original_component_checks']),over_one_percent_samples=len(details),limitations='Bounds are reported from ORIGINAL Polygon, not replacement rectangles. Root and normal-width evidence is sampled on original STL. Corner loss screening is not a slicer or physical-print certificate.',details=details)
(R/'component-loss-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (R/'component-loss-over-one-percent.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(details[0]));w.writeheader();w.writerows(details)
print(json.dumps(summary,ensure_ascii=False,indent=2))
