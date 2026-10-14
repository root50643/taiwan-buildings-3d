"""Reference rectangles explain numeric offset differences; never replace/repair raw input."""
from pathlib import Path
import json,hashlib
import numpy as np
from shapely.geometry import Polygon,box,MultiPoint
R=Path(__file__).resolve().parent;data=json.loads((R/'feature-loss-locations.json').read_text());rows=[]
for r in data['high_loss_components']:
 if abs(r['bbox_area_mm2']-r['original_area_mm2'])>=1e-5:continue
 p=Polygon(r['original_exterior_mm'],r['original_holes_mm']);assert p.is_valid
 b=box(*r['bounds']);diff=p.symmetric_difference(b).area;assert diff<1e-5
 # Diagnostic reference only. Original per-Polygon acceptance stays unchanged.
 ref=b.difference(b.buffer(-.4).buffer(.4));bounds=r['bounds'];corners=[(bounds[0],bounds[1]),(bounds[0],bounds[3]),(bounds[2],bounds[1]),(bounds[2],bounds[3])]
 off=max(min(abs(x-bounds[0]),abs(x-bounds[2]),abs(y-bounds[1]),abs(y-bounds[3])) for x,y in p.exterior.coords)
 rows.append({'z_mm':r['z_mm'],'bounds':r['bounds'],'raw_opening_loss_fraction':r['opening_loss_fraction'],'reference_box_opening_loss_fraction':ref.area/b.area,'raw_symmetric_difference_from_reference_box_mm2':diff,'maximum_raw_vertex_off_rect_edges_mm':off,'raw_loss_outside_original_vertex0p41_mm2':r['loss_outside_0p41_vertex_mm2'],'reference_loss_outside_rect_corner0p41_mm2':ref.difference(MultiPoint(corners).buffer(.41)).area})
rep={'passed':True,'not_repair':True,'scope':'Diagnostic reference boxes only; raw section polygons and all raw erosion/opening checks remain unchanged. No threshold relaxation. Independent review required.','count':len(rows),'maximum_raw_reference_area_difference_mm2':max(x['raw_symmetric_difference_from_reference_box_mm2'] for x in rows),'maximum_raw_vertex_edge_distance_mm':max(x['maximum_raw_vertex_off_rect_edges_mm'] for x in rows),'maximum_raw_loss_fraction':max(x['raw_opening_loss_fraction'] for x in rows),'maximum_reference_box_loss_fraction':max(x['reference_box_opening_loss_fraction'] for x in rows),'raw_corner_outside_samples':sum(x['raw_loss_outside_original_vertex0p41_mm2']>1e-10 for x in rows),'rows':rows,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}
(R/'rectangle-control-check.json').write_text(json.dumps(rep,indent=2));print({k:v for k,v in rep.items() if k!='rows'})
