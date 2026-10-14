"""Fail-closed aggregate QA. Blender must be on PATH. No mesh repair."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=sha(R/'model.stl')
pinned={'check_thin_features.py':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','check_layer_components.py':'365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
for name,expected in pinned.items():assert sha(R/name)==expected,(name,'canonical verifier changed')
scripts=['validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_open_spaces.py','check_previews.py']
for script in scripts:subprocess.run([sys.executable,str(R/script)],check=True)
assert sha(R/'model.stl')==original,'QA must not modify original STL'
reports={name:json.loads((R/name).read_text()) for name in ['validation.json','thin-feature-check.json','layer-opening-check.json','layer-component-check.json','open-space-check.json','preview-check.json']}
for name,r in reports.items():
 assert r.get('passed',True) is True,(name,'failed')
 assert all(r.get('checks',{}).values()),name
components=reports['layer-component-check.json']['original_component_checks']
report={'passed':True,'model':'NTUNHS Wenjiao 1965 original main building exterior approximation','stl_sha256':original,'checks':{'all_validation_processes_exit_zero':True,'all_json_checks_true':True,'canonical_v3_verifier_hash_matches':True,'canonical_per_polygon_verifier_hash_matches':True,'original_stl_unchanged_by_qa':True,'every_0_2mm_original_polygon_survives_and_remains_single':all(r['eroded_components']==1 and r['opened_components']==1 for r in components),'actual_stl_blend_rebuild_png_agree':True},'sampled_layers_0_2mm':reports['layer-component-check.json']['sampled_layers'],'original_polygon_count':len(components),'maximum_opening_loss_fraction':reports['layer-component-check.json']['maximum_opening_loss_fraction'],'layer_pitch_mm':.2,'start_offset_mm':.071,'reference_width_mm':.8,'canonical_verifier_sha256':pinned,'report_sha256':{name:sha(R/name) for name in reports},'scope_limits':['Digital geometric screening only; no physical print or slicer toolpath validation.','No claim of exhaustive all-direction minimum wall thickness.','The original 1965 exterior is an evidence-based approximation, not a current as-built survey.']}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
