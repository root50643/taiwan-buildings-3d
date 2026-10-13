"""Run all fail-closed numerical checks. No mesh or polygon repair is performed.
Python 3.12 + requirements.txt; Blender 4.3.2+ on PATH.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
SHA='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
expected=['validate_model.py','check_layers.py','check_contour_validity.py','check_thin_features.py']
results=[]
for name in expected:
 proc=subprocess.run([sys.executable,str(R/name)],cwd=R,capture_output=True,text=True)
 results.append({'script':name,'exit_code':proc.returncode})
 if proc.returncode:
  print(proc.stdout);print(proc.stderr,file=sys.stderr)
  (R/'qa-summary.json').write_text(json.dumps({'passed':False,'checks':{name:False},'runs':results},indent=2)+'\n')
  raise SystemExit(proc.returncode)
v=json.loads((R/'validation.json').read_text());l=json.loads((R/'layer-check.json').read_text());c=json.loads((R/'contour-validity-check.json').read_text());t=json.loads((R/'thin-feature-check.json').read_text())
checks={
 'all_four_validators_exit_zero':all(x['exit_code']==0 for x in results),
 'all_raw_geometry_rebuild_blend_checks_true':v['passed'] and all(v['checks'].values()),
 'all_0_2mm_sections_degree_two_closed':l['all_sampled_contours_closed'] and not l['issues'],
 'all_individual_and_combined_polygons_valid':c['all_sampled_contours_closed_and_valid'],
 'canonical_fail_closed_v3_sha_verified':hashlib.sha256((R/'check_thin_features.py').read_bytes()).hexdigest()==SHA,
 'thin_screen_reference_width_0_8mm':t['reference_width_mm']==.8,
 'thin_screen_max_loss_below_one_percent':t['maximum_opening_loss_fraction']<.01,
 'no_polygon_repair_fallback':all('buffer(0)' not in (R/f).read_text() and 'make_valid' not in (R/f).read_text() for f in expected),
 'model_sha_matches_validated_stl':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()==v['stl_sha256']}
report={'passed':all(checks.values()),'checks':checks,'runs':results,'model_sha256':v['stl_sha256'],'canonical_validator_sha256':SHA,'layer_pitch_mm':.2,'first_z_mm':.071,'layer_count':c['sampled_layers'],'thin_sample_count':t['sampled_layers'],'maximum_0_8mm_opening_loss_fraction':t['maximum_opening_loss_fraction'],'physical_print_test_performed':False,'slicer_toolpath_test_performed':False,'full_wall_thickness_analysis_performed':False}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
