"""Summarize quantified original-coordinate diagnosis without changing gate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('diagnosis',type=Path);ap.add_argument('--json',type=Path,required=True)
a=ap.parse_args();data=a.diagnosis.read_bytes();r=json.loads(data)
pairs=r['pairs'];tol=1e-6
near=[]
for p in pairs:
    residuals=[abs(x) for k in ['float_signed_a_to_b_plane_mm','float_signed_b_to_a_plane_mm'] for x in p[k]]
    near.append(max(residuals))
result={
    'scope':'Summary of exact rational diagnosis on only previously flagged pairs; original generic gate stays failed.',
    'stl_sha256':r['input_sha256'],'generic_report_sha256':r['report_sha256'],
    'diagnosis_sha256':hashlib.sha256(data).hexdigest(),
    'diagnosis_script_sha256':r['diagnostic_script_sha256'],
    'all_flags_covered_once':r['all_flags_covered_once'],'flag_count':len(pairs),
    'exact_classifications':dict(Counter(p['exact']['classification'] for p in pairs)),
    'true_unexpected_exact_intersection_count':sum(not p['exact']['intersection_confined_to_shared_topology'] for p in pairs),
    'original_float_flag_kinds':dict(Counter(p['original_flag']['kind'] for p in pairs)),
    'generic_tolerance_mm_unchanged':tol,
    'pairs_all_six_vertex_plane_residuals_within_1e_6_mm':sum(x<=tol for x in near),
    'maximum_across_pairs_of_six_vertex_plane_residuals_mm':max(near,default=None),
    'minimum_across_pairs_of_six_vertex_plane_residuals_mm':min(near,default=None),
    'unit_normal_cross_norm_min':min((p['unit_normal_cross_norm'] for p in pairs),default=None),
    'unit_normal_cross_norm_max':max((p['unit_normal_cross_norm'] for p in pairs),default=None),
    'quantified_examples':{kind:next((p for p in pairs if p['exact']['classification']==kind),None) for kind in sorted(set(p['exact']['classification'] for p in pairs))},
    'report_unchanged_after_exact_diagnosis':r['generic_report_unchanged'],
    'does_not_override_generic_report_exit_status':True,
    'limit':'Exact Fraction calculations apply to finite STL binary32 coordinates and these flagged pairs only. Other pairs were subject to the complete-AABB floating screen; this is not a formal whole-mesh exact proof.',
}
a.json.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='quantified_examples'},indent=2))
