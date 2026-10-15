"""Preserve each strict warning and group by original section region; no waiver."""
from pathlib import Path
import json,hashlib
R=Path(__file__).parent
j=json.loads((R/'component-detail.json').read_text());rows=j['original_component_checks'];w=[x for x in rows if x['opening_loss_fraction']>.01]
families={}
for q in w:
 z=q['z_mm'];name='entry_square_posts'if z<20 else 'low_terrace_square_post'if z<90 else 'crown_skirt_brace_junction'if z<99 else 'crown_individual_braces'
 families.setdefault(name,[]).append(q)
report=[]
for name,a in families.items():
 p=max(a,key=lambda x:x['opening_loss_fraction'])
 report.append(dict(family=name,count=len(a),z_min_mm=min(x['z_mm']for x in a),z_max_mm=max(x['z_mm']for x in a),maximum_loss_fraction=p['opening_loss_fraction'],minimum_retained_fraction=min(x['retained_fraction']for x in a),maximum_loss_outside_original_vertex_0p41_mm2=max(x['loss_outside_0p41_vertex_mm2']for x in a),peak_original_polygon=p,all_original_polygon_warnings=a))
checks={'all_strict_warnings_preserved':sum(x['count']for x in report)==len(w),'every_original_polygon_single_after_erosion_and_opening':all(x['eroded_components']==1 and x['opened_components']==1 for x in rows)}
out=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,sampled_layers=j['sampled_layers'],original_polygon_count=len(rows),strict_warning_count=len(w),families=report,judgment='Pending independent review and specific root decision. This grouping does not turn strict false into true; crown junction loss extends slightly beyond 0.41mm vertex neighborhoods and is not claimed to be ordinary rectangular corner loss.')
(R/'warning-families.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items()if k!='families'});assert all(checks.values())
