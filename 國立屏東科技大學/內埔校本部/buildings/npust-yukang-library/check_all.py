from pathlib import Path
import json,hashlib,gzip
R=Path(__file__).parent;Q=R/'qa'
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
dense=load(Q/'dense/initial-summary.json');corners=load(Q/'warning-corners-summary.json');roots=load(Q/'dense/backed-mullions-summary.json')
checks={'raw_mesh':load(R/'raw-mesh-check.json')['passed'],'source_and_blend_rebuild':load(R/'validation.json')['passed'],'all_png_byte_rebuild':load(R/'preview-rebuild-check.json')['passed'],'every_original_polygon_survives_unsplit':load(Q/'layer-component-check.json.gz')['passed'],'dense_controls_without_flags':dense['control_flags']==0,'all_dense_first_solid_chords_at_least_0_8mm':dense['short_under0_8']==0,'all_original_corner_outside_0_41_loss_zero':all(v['max_true_corner_outside_0_41_mm2']==0 for v in corners['families'].values()),'every_backed_mullion_predetermined_root_over_0_8':roots['under0_8_root_count']==0}
r={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'checks':checks,'passed':all(checks.values()),'status':'Finite exceptions pending independent review:107 backed relief mullions,3179 original corner-loss samples including23 true-corner-outside nonzero north-frame cases; false values deliberately retained.','not_a_print_guarantee':True}
(Q/'all-checks.json').write_text(json.dumps(r,indent=2));print(r);raise SystemExit(0 if r['passed']else 1)
