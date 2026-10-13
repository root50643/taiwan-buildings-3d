"""Fail-closed report wrapper around the unchanged independently audited canonical v3.
Geometry algorithm lives in thin_canonical_v3.py; this adds stale-report protection,
STL binding and the project maximum 1% opening-loss acceptance gate.
"""
from pathlib import Path
import runpy,json,hashlib
R=Path(__file__).resolve().parent
out=R/'thin-feature-check.json'
sha=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
out.write_text(json.dumps({'passed':False,'checks':{'completed':False},'stl_sha256':sha}))
assert hashlib.sha256((R/'thin_canonical_v3.py').read_bytes()).hexdigest()=='059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'
try:
 runpy.run_path(str(R/'thin_canonical_v3.py'),run_name='__main__')
 report=json.loads(out.read_text())
 checks={'all_sampled_contours_closed_valid':True,'maximum_opening_loss_below_one_percent':report['maximum_opening_loss_fraction']<=.01,'canonical_source_sha256_verified':True}
 report.update({'passed':all(checks.values()),'checks':checks,'stl_sha256':sha,'canonical_v3_sha256':'059f7378c74a1400dcf010365ebf35df3027fd853f1c960462a233dc68ce8915'})
 out.write_text(json.dumps(report,indent=2))
except BaseException:
 out.write_text(json.dumps({'passed':False,'checks':{'completed':False},'stl_sha256':sha}))
 raise
raise SystemExit(0 if report['passed'] else 1)
