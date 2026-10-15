"""Precise warning families; no automatic exemption of the original strict tests."""
from pathlib import Path
import json,hashlib
R=Path(__file__).parent;a=json.loads((R/'component-detail.json').read_text());b=json.loads((R/'true-corner-mask.json').read_text());bm={(x['z_mm'],x['original_component_index']):x for x in b['original_component_checks']};groups={}
for q in a['original_component_checks']:
 if q['opening_loss_fraction']<=.01:continue
 box=q['bounds'];family='entry_posts_and_low_step_junction'if box[1]<-35 else 'external_stair_frames_and_treads'if box[0]>50 else 'UNCLASSIFIED'
 x=dict(q);x['loss_outside_0p41_true_corner_mm2']=bm[(q['z_mm'],q['original_component_index'])]['loss_outside_0p41_vertex_mm2'];groups.setdefault(family,[]).append(x)
summary={k:dict(count=len(v),z_range_mm=[min(q['z_mm']for q in v),max(q['z_mm']for q in v)],peak_loss_fraction=max(q['opening_loss_fraction']for q in v),minimum_retained_fraction=min(q['retained_fraction']for q in v),maximum_loss_outside_true_corners_mm2=max(q['loss_outside_0p41_true_corner_mm2']for q in v))for k,v in groups.items()}
checks=dict(all_warnings_classified='UNCLASSIFIED'not in groups,all_warning_polygons_survive_without_split=all(q['eroded_components']==q['opened_components']==1 for v in groups.values()for q in v),warning_count_preserved=sum(len(v)for v in groups.values())==a['individual_polygons_over_one_percent'])
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,summary=summary,groups=groups,status='Evidence only. Original per-component strict false is retained, pending independent decision.')
(R/'warning-families.json').write_text(json.dumps(r,indent=2));print(summary);assert all(checks.values())
