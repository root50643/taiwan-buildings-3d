from pathlib import Path
import json,gzip,hashlib,numpy as np
R=Path(__file__).resolve().parent;sha=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
def load(n):
 p=R/n;return json.loads(gzip.decompress(p.read_bytes()))if n.endswith('.gz')else json.loads(p.read_text())
c=load('original-face-normal-evidence.json.gz');d=load('dense-independent-root-evidence.json.gz');a=load('adaptive-origin-evidence.json');b=load('all-six-boundary-controls.json');root=load('corrected-origin-root-check.json');short=load('short-chord-root-evidence.json');loss=load('component-loss-evidence.json')
assert all(x['stl_sha256']==sha for x in [c,d,a,b,root,short,loss])
centroid_ok=all(x['inside_surface']and not x['outside_surface']and x['first_chord_midpoint_inside']and not x['after_first_exit_inside']for x in c['samples'])
air_ids={x['sample_index']for x in a['samples']};boundary_ids={x['sample_index']for x in b['samples']}
raw_bad={x['sample_index']for x in d['samples']if not x['inside_surface']or x['outside_surface']or not x['first_chord_midpoint_inside']or x['after_first_exit_inside']}
assert air_ids=={20581,20582,20584,31753,31755,31757}and boundary_ids=={52766,52829,53046,87367,87535,94710}
air_ok=all(abs(t['winding']-(1 if t['role']in ['inside_surface','first_material_midpoint']else 0))<1e-8 for x in a['samples']for t in x['tests'])
boundary_ok=all(all(abs(t['winding']-(1 if t['role']=='mid'else 0))<1e-8 for t in y['tests']) for x in b['samples']for y in x['controls'][1:])
root_ok=short['below_08_root_span']==0 and root['passed'] and all(x['longest_connected_root_span_mm']>=.8 and x['midpoint_inside']for x in d['short_roots']if x['dense_sample_index']not in air_ids)
checks={'all_original_centroid_flags':centroid_ok,'only_exactly_documented_dense_cases':raw_bad==air_ids|boundary_ids,'all_six_air_origins_recast_from_proven_outside':air_ok,'all_six_boundary_sets_have_valid_same_face_controls':boundary_ok,'all_true_short_segments_have_first_exit_backing':root_ok,'exact_input_triangles_preserved':d['exact_original_geometry_and_winding_equal']}
r={'passed':False,'ready_for_independent_review':all(checks.values()),'stl_sha256':sha,'resolved_evidence_checks':checks,'original_dense_diagnostic_passed':not raw_bad,'original_dense_bad_sample_ids':sorted(raw_bad),'original_layer_high_loss_samples':loss['warning_samples'],'exceptions_independently_approved':False,'original_face_samples':len(c['samples']),'dense_samples':d['sample_count'],'original_dense_flag_counts':d['flag_counts'],'original_fixed_pair_short_count':d['short_root_count'],'actual_material_short_dense_count':d['short_root_count']-3,'meaning':'Original false retained. Correction and boundary evidence are complete but are not independent approval. No global minimum-wall or physical print guarantee.'};(R/'surface-root-summary.json').write_text(json.dumps(r,indent=2));assert r['ready_for_independent_review'];print(r)
