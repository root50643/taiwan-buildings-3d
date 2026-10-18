"""Fail-closed author QA. Independent review and physical printing are separate."""
from pathlib import Path
import subprocess,sys,hashlib,json
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def publication_review_state(stl_sha256):
 # Publication history and review evidence are metadata, not QA check results.
 published_sha='df84e1b7a4290b799082c7d2a2d23427fd6bb5cb3719ee2c82f73c152c84847b'
 matches=stl_sha256==published_sha
 record=R/'cross-warning-layers.json'
 record_sha='002a00d36a27d129191c2603c7e4cd971f79f5fc358d5ab0e9de28ecd4b8dd25'
 # This existing JSON record is pinned as canonical LF text; Git may check it
 # out with CRLF on Windows. Do not confuse that conversion with missing evidence.
 record_matches=record.is_file() and hashlib.sha256(record.read_bytes().replace(b'\r\n',b'\n')).hexdigest()==record_sha
 return {'publication':{'status':'published' if matches else 'current_stl_not_matched_to_publication_record',
   'record_commit':'897897849bca52f9e43f6b573f71600927d93221',
   'record_stl_sha256':published_sha,'current_stl_matches_record':matches},
  'independent_review':{'overall_release_status':'unconfirmed',
   'evidence_inventory_checked_date':'2026-10-18',
   'note':'A complete dated and scoped overall independent release record has not been confirmed; this is not a review-failure finding.',
   'specific_exception_record':{'status':'record_present_for_fixed_stl' if matches and record_matches else 'not_confirmed_for_current_files',
    'path':'cross-warning-layers.json','canonical_lf_sha256':record_sha,'current_record_matches_canonical_lf_sha':record_matches,
    'scope':'Recorded independent localization/root-ray review of the 44 cross-shaft/crossbar opening-loss layers only; not whole-model release or print approval.'}}}

# A stopped rerun must not leave a previous run's passed summary as its result.
initial={'passed':None,'status':'author_digital_QA_incomplete','scope':'This invocation has started but has not completed the checks; inspect its exit status and diagnostics.'}
initial.update(publication_review_state(sha(R/'model.stl') if (R/'model.stl').is_file() else None))
(R/'qa-summary.json').write_text(json.dumps(initial,indent=2),encoding='utf8',newline='\n')
expected='df84e1b7a4290b799082c7d2a2d23427fd6bb5cb3719ee2c82f73c152c84847b'
assert sha(R/'model.stl')==expected,'Do not validate an unapproved geometry as the approved candidate'
assert sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
steps=[]
for name in ['validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_render_rebuild.py']:
 result=subprocess.run([sys.executable,str(R/name)],check=True,capture_output=True,text=True)
 steps.append({'script':name,'exit_code':result.returncode,'script_sha256':sha(R/name)})
v=json.loads((R/'validation.json').read_text(encoding='utf8'));c=json.loads((R/'layer-component-check.json').read_text(encoding='utf8'));p=json.loads((R/'render-manifest.json').read_text(encoding='utf8'))
assert v['passed'] and all(v['checks'].values())
assert c['passed'] and all(c['checks'].values())
assert p['passed'] and all(p['checks'].values())
assert sha(R/'model.stl')==expected and v['stl_sha256']==expected and p['stl_sha256']==expected
checks={'approved_stl_unchanged':sha(R/'model.stl')==expected and v['stl_sha256']==expected and p['stl_sha256']==expected,'all_validation_checks_true':v['passed'] is True and all(x is True for x in v['checks'].values()),'one_connected_surface_no_internal_shells':v['surface_shells']==1,'all_original_polygons_survive_without_split':all(x['eroded_components']==1 and x['opened_components']==1 for x in c['original_component_checks']),'all_seven_images_independently_reproduce':p['passed'] is True and all(x is True for x in p['checks'].values()),'all_scripts_exit_zero':all(x['exit_code']==0 for x in steps),'canonical_v3_sha_verified':sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915','canonical_component_validator_sha_verified':sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'}
assert all(checks.values())
reports={f:sha(R/f) for f in ['validation.json','thin-feature-check.json','layer-opening-check.json','layer-component-check.json','render-manifest.json']}
report={'passed':all(checks.values()),'status':'author_digital_QA_passed' if all(checks.values()) else 'author_digital_QA_failed','checks':checks,'stl_sha256':expected,'dimensions_mm':v['dimensions_mm'],'triangles':v['triangles'],'surface_shells':v['surface_shells'],'sampled_layers_0_2mm':c['sampled_layers'],'original_polygon_count':len(c['original_component_checks']),'maximum_opening_loss_fraction':c['maximum_opening_loss_fraction'],'layers_over_one_percent_opening_loss':c['layers_over_one_percent_opening_loss'],'steps':steps,'report_sha256':reports,'appearance_approval':'2026-10-14 parent reviewed source-actual-900 and roof-ground-900; approximate curve/terrain disclosure required','limitations':['未作實體試印或實際切片工具路徑驗證。','0.8mm opening不是全方向最小壁厚；細十字架與尖角有面積損失，零消失／分裂另逐Polygon強制檢查。','自由曲面與地形為來源比例近似，不是實測；44層十字架局部例外有既有核對紀錄；完整總體獨立放行紀錄未確認，並非審查失敗。']}
report.update(publication_review_state(sha(R/'model.stl')))
(R/'qa-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8',newline='\n');print(json.dumps(report,ensure_ascii=False,indent=2))
