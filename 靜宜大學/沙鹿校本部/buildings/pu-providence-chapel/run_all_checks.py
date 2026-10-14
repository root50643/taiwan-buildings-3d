"""Fail-closed author QA. Independent review and physical printing are separate."""
from pathlib import Path
import subprocess,sys,hashlib,json
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='df84e1b7a4290b799082c7d2a2d23427fd6bb5cb3719ee2c82f73c152c84847b'
assert sha(R/'model.stl')==expected,'Do not validate an unapproved geometry as the approved candidate'
assert sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
steps=[]
for name in ['validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_render_rebuild.py']:
 result=subprocess.run([sys.executable,str(R/name)],check=True,capture_output=True,text=True)
 steps.append({'script':name,'exit_code':result.returncode,'script_sha256':sha(R/name)})
v=json.loads((R/'validation.json').read_text());c=json.loads((R/'layer-component-check.json').read_text());p=json.loads((R/'render-manifest.json').read_text())
assert v['passed'] and all(v['checks'].values())
assert c['passed'] and all(c['checks'].values())
assert p['passed'] and all(p['checks'].values())
assert sha(R/'model.stl')==expected and v['stl_sha256']==expected and p['stl_sha256']==expected
checks={'approved_stl_unchanged':True,'all_validation_checks_true':True,'one_connected_surface_no_internal_shells':v['surface_shells']==1,'all_original_polygons_survive_without_split':all(x['eroded_components']==1 and x['opened_components']==1 for x in c['original_component_checks']),'all_seven_images_independently_reproduce':True,'all_scripts_exit_zero':all(x['exit_code']==0 for x in steps),'canonical_v3_sha_verified':True,'canonical_component_validator_sha_verified':True}
assert all(checks.values())
reports={f:sha(R/f) for f in ['validation.json','thin-feature-check.json','layer-opening-check.json','layer-component-check.json','render-manifest.json']}
report={'passed':True,'status':'author_QA_passed_independent_review_pending','checks':checks,'stl_sha256':expected,'dimensions_mm':v['dimensions_mm'],'triangles':v['triangles'],'surface_shells':v['surface_shells'],'sampled_layers_0_2mm':c['sampled_layers'],'original_polygon_count':len(c['original_component_checks']),'maximum_opening_loss_fraction':c['maximum_opening_loss_fraction'],'layers_over_one_percent_opening_loss':c['layers_over_one_percent_opening_loss'],'steps':steps,'report_sha256':reports,'appearance_approval':'2026-10-14 parent reviewed source-actual-900 and roof-ground-900; approximate curve/terrain disclosure required','limitations':['未作實體試印或實際切片工具路徑驗證。','0.8mm opening不是全方向最小壁厚；細十字架與尖角有面積損失，零消失／分裂另逐Polygon強制檢查。','自由曲面與地形為來源比例近似，不是實測；獨立幾何複核尚待進行。']}
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
