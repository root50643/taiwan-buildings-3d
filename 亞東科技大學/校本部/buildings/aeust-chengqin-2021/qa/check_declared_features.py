from pathlib import Path
import json
import math
import hashlib

root=Path(__file__).resolve().parents[1]
p=json.loads((root/'parameters.json').read_text(encoding='utf8'))
m,c=p['model_mm'],p['connector']
bay=(m['main_length']-2*m['core_length'])/8
pitch=m['body_height_above_base']/12
checks={'front_pier_between_recesses_mm':bay-m['window_width'],
 'front_vertical_solid_between_recesses_mm':pitch-m['window_height'],
 'front_recess_depth_mm':m['front_recess_depth'],
 'front_recess_top_rise_mm':m['front_recess_depth'],
 'connector_band_recess_depth_mm':c['band_recess_depth'],
 'connector_band_top_rise_mm':c['band_top_chamfer'],
 'connector_vertical_solid_between_bands_mm':pitch-c['band_height'],
 'printing_base_thickness_mm':m['base_z'],
 'roof_box_minimum_xy_dimension_mm':min(m['roof_box_length'],m['roof_box_depth']),
 'roof_box_length_within_core':m['roof_box_length']<=m['core_length'],
 'roof_box_depth_within_core':m['roof_box_depth']<=m['core_depth'],
 'front_chamfer_angle_from_vertical_deg':45.0,
 'connector_chamfer_angle_from_vertical_deg':math.degrees(math.atan2(c['band_recess_depth'],c['band_top_chamfer']))}
r={'stl_sha256':hashlib.sha256((root/'models/v1/model.stl').read_bytes()).hexdigest(),
 'parameters_sha256':hashlib.sha256((root/'parameters.json').read_bytes()).hexdigest(),
 'method':'Direct evaluation of declared solid/recess dimensions and core containment; supplements actual STL section screen. No local minimum-thickness solver.',
 'declared_features':checks,
 'assessment':'No freestanding railings, mullions, canopies or thin membranes are generated. Recess depth is surface relief, not wall thickness. Curve facet corners and the taper where a band ends at the cut are intentionally not certified as an everywhere-minimum-width solid.',
 'limitations':'No arbitrary 3D wall-thickness proof, slicer toolpaths, material/adhesion/strength prediction or physical print.'}
(root/'qa/declared-feature-review.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r,indent=2))
