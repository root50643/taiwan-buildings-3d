"""Fail-closed full author checks. No repair and no whole-layer loss shortcut."""
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EXPECTED='01277bf8746a2ae19b5abe792d334756caa2e22db1252f5d586e1951069ec7a0'
assert sha(R/'model.stl')==EXPECTED,'Unapproved geometry: revise and review explicitly'
assert sha(R/'check_thin_features.py')=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
assert sha(R/'check_layer_components.py')=='365e437af0d3d6defc2f52adf3e8601ac3643a14e15e03c8c8610b10bb8061a5'
steps=[]
for script in ['check_raw_mesh.py','validate_model.py','check_thin_features.py','check_all_layers.py','check_layer_components.py','check_component_detail.py','check_feature_rays.py','check_render_rebuild.py']:
 p=subprocess.run([sys.executable,str(R/script)],check=True,capture_output=True,text=True)
 steps.append({'script':script,'exit_code':p.returncode,'sha256':sha(R/script)})
reports={}
for name in ['raw-mesh-check.json','validation.json','layer-component-check.json','component-detail.json','feature-rays.json','render-manifest.json']:
 d=json.loads((R/name).read_text());assert d['passed'] and all(d['checks'].values()),name
 if 'stl_sha256' in d:assert d['stl_sha256']==EXPECTED,name
 reports[name]=d
raw=reports['raw-mesh-check.json'];v=reports['validation.json'];c=reports['component-detail.json'];r=reports['feature-rays.json'];p=reports['render-manifest.json']
assert all(x['checks']['independent_png_bytes_identical'] for x in p['views'])
assert len(p['views'])==8 and sha(R/'model.stl')==EXPECTED
checks={'approved_STL_unchanged':True,'raw_binary_exact_topology_passed':True,'source_rebuild_STL_SHA_identical':True,'Blend_geometry_identical':True,'all_original_layer_components_valid_survive_and_do_not_split':True,'every_original_polygon_loss_at_most_one_percent':c['individual_polygons_over_one_percent']==0,'all_feature_normal_root_and_open_space_rays_pass':True,'all_8_PNG_bytes_and_pixels_independently_reproduce':True,'all_8_scripts_exit_zero':len(steps)==8 and all(x['exit_code']==0 for x in steps),'canonical_validator_SHAs_match':True}
assert all(checks.values())
summary={'passed':True,'status':'author_QA_passed_independent_review_pending','checks':checks,'stl_sha256':EXPECTED,'dimensions_mm':v['dimensions_mm'],'triangles':raw['triangles'],'surface_shells':raw['surface_shells'],'sampled_layers':c['sampled_layers'],'original_polygon_count':len(c['original_component_checks']),'maximum_whole_layer_opening_loss_fraction':c['maximum_opening_loss_fraction'],'maximum_individual_polygon_opening_loss_fraction':c['maximum_individual_polygon_loss_fraction'],'individual_polygons_above_one_percent':c['individual_polygons_over_one_percent'],'selected_normal_ray_count':len(r['normal_thickness_samples']),'selected_root_ray_count':len(r['root_samples']),'selected_open_space_ray_count':len(r['open_space_samples']),'minimum_selected_normal_width_mm':min(x['thickness_mm'] for x in r['normal_thickness_samples']),'steps':steps,'report_sha256':{name:sha(R/name) for name in list(reports)+['thin-feature-check.json','layer-opening-check.json']},'limits':['照片比例近似，公尺高度、屋脊及地形非實測。','法向厚度、根接與淨空只為指定射線，不是全方向最小壁厚。','未實體試印或實際切片工具路徑；遮棚、連橋與陽台需評估支撐，勿任意縮小。']}
(R/'qa-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
