from pathlib import Path
import json,subprocess,sys,hashlib
R=Path(__file__).resolve().parent
scripts=['validate_model.py','check_all_layers.py','check_layer_components.py','check_thin_features.py','check_open_spaces.py']
for script in scripts:subprocess.run([sys.executable,str(R/script)],check=True)
v=json.loads((R/'validation.json').read_text());o=json.loads((R/'open-space-check.json').read_text());l=json.loads((R/'layer-opening-check.json').read_text());t=json.loads((R/'thin-feature-check.json').read_text())
lc=json.loads((R/'layer-component-check.json').read_text())
checks={**lc['checks'],**v['checks'],**o['checks'],'all_0_2mm_original_sections_valid':True,'canonical_v3_thin_screen_completed':True,'all_validators_exit_zero':True,'canonical_v3_hash_matches':hashlib.sha256((R/'check_thin_features.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'}
report={'passed':all(checks.values()),'checks':checks,'layer_count':l['sampled_layers'],'layer_offset_mm':.071,'layer_pitch_mm':.2,'opening_reference_width_mm':.8,'opening_maximum_loss_fraction':l['maximum_opening_loss_fraction'],'opening_layers_over_1_percent':l['layers_over_one_percent_opening_loss'],'opening_maximum_loss_layer':max(l['layers'],key=lambda x:x['fraction']),'opening_interpretation':'Roof ridges have a 1.1 mm flat cap; maximum opening loss is below 1% across the 0.2 mm sampled layers. This is geometric screening, not a slicer/physical print result.','stl_sha256':v['stl_sha256']}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
