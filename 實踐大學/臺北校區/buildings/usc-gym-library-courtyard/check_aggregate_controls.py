"""Negative controls prove failed, stale, missing and relaxed evidence is rejected."""
from pathlib import Path
import hashlib,json,shutil,tempfile,sys
import validate_model as validator
R=Path(__file__).resolve().parent
results=[]
with tempfile.TemporaryDirectory(prefix='usc-aggregate-controls-') as td:
 root=Path(td)
 for p in R.iterdir():
  if p.is_file() and (p.suffix in ['.py','.json','.blend'] or p.name=='model.stl'):shutil.copy2(p,root/p.name)
 for name in ['verification','previews']:shutil.copytree(R/name,root/name)
 shutil.copytree(R/'qa/current',root/'qa/current')
 baseline=validator.inspect(root);results.append({'case':'unaltered_current_bundle','expected_passed':True,'observed_passed':baseline['passed'],'control_passed':baseline['passed'] is True})
 cases=[
 ('wrong_compression_format','qa/current/dense/dense-check.json',lambda q:q.update(csv_compression='gzip')),
 ('unknown_compression_format','qa/current/dense/dense-check.json',lambda q:q.update(csv_compression='unknown')),
 ('wrong_compressed_csv_hash','qa/current/dense/dense-check.json',lambda q:q.update(csv_compressed_sha256='0'*64)),
 ('wrong_compressed_csv_bytes','qa/current/dense/dense-check.json',lambda q:q.update(csv_compressed_bytes=1)),
 ('wrong_lossless_csv_hash','qa/current/dense/dense-check.json',lambda q:q.update(uncompressed_csv_sha256='0'*64)),
 ('missing_gate_records','qa/current/qa-summary.json',lambda q:q.pop('gate_reports',None)),
 ('wrong_gate_report_hash','qa/current/qa-summary.json',lambda q:q['gate_reports'][0].update(report_sha256='0'*64)),
 ('missing_raw_checks','qa/current/raw/raw-mesh-check.json',lambda q:q.pop('checks',None)),
 ('empty_raw_checks','qa/current/raw/raw-mesh-check.json',lambda q:q.update(checks={})),
 ('missing_raw_flag','qa/current/raw/raw-mesh-check.json',lambda q:q['checks'].pop('exact_coordinate_edges_two_faces',None)),
 ('missing_strict_passed','qa/current/raw/raw-mesh-check.json',lambda q:q.pop('strict_passed',None)),
 ('missing_feature_checks','architectural-features.json',lambda q:q.pop('checks',None)),
 ('empty_feature_checks','architectural-features.json',lambda q:q.update(checks=[])),
 ('missing_feature_probe','architectural-features.json',lambda q:q['checks'].pop()),
 ('raw_failure','qa/current/raw/raw-mesh-check.json',lambda q:q.update(passed=False)),
 ('relaxed_ray_threshold','qa/current/dense/dense-check.json',lambda q:q.update(minimum_required_chord_mm=.4,minimum_first_chord_mm=.7)),
 ('retained_ray_flag','qa/current/dense/dense-check.json',lambda q:q.update(flagged_sample_count=1)),
 ('retained_slice_failure','qa/current/sections/section-check.json',lambda q:q.update(failed_polygon_count=1)),
 ('closed_contact_failure','qa/current/intersections/original-intersections.json',lambda q:q.update(bad_pair_count=1)),
 ('false_feature_probe','architectural-features.json',lambda q:q['checks'][0].update(passed=False)),
 ('stale_feature_mesh','architectural-features.json',lambda q:q.update(stl_sha256='0'*64)),
 ('stale_rebuild_source','reproducibility.json',lambda q:q.update(build_source_sha256='0'*64)),
 ('stale_scene','scene-check.json',lambda q:q.update(blend_sha256='0'*64)),
 ('missing_render_view','render-manifest.json',lambda q:q.get('views',{}).pop('top',None)),
 ]
 for name,rel,fn in cases:
  p=root/rel;old=p.read_bytes();q=json.loads(old);fn(q);p.write_text(json.dumps(q));observed=validator.inspect(root);p.write_bytes(old)
  results.append({'case':name,'expected_passed':False,'observed_passed':observed['passed'],'control_passed':observed['passed'] is False,'rejection_flags':observed['failed_checks']})
 # Current-model negative controls bind the declared container as well as both hashes.
 dp=root/'qa/current/dense/dense-check.json';ap=root/'qa/current/qa-summary.json';db=dp.read_bytes();ab=ap.read_bytes();dq=json.loads(db);cp=dp.parent/dq['csv_file'];cb=cp.read_bytes()
 for name in ['missing_current_csv','corrupt_current_csv','gzip_disguised_as_current_xz']:
  changed=json.loads(db)
  if name=='missing_current_csv':cp.unlink()
  elif name=='corrupt_current_csv':
   payload=bytearray(cb);payload[-15]^=1;cp.write_bytes(payload)
  else:
   import gzip,lzma
   with lzma.open(cp,'rb') as h:payload=h.read()
   cp.write_bytes(gzip.compress(payload,mtime=0))
  if cp.exists():changed['csv_compressed_sha256']=hashlib.sha256(cp.read_bytes()).hexdigest();changed['csv_compressed_bytes']=cp.stat().st_size
  dp.write_text(json.dumps(changed));aq=json.loads(ab)
  for row in aq['gate_reports']:
   if row['gate']=='dense':row['report_sha256']=hashlib.sha256(dp.read_bytes()).hexdigest()
  ap.write_text(json.dumps(aq));observed=validator.inspect(root);cp.write_bytes(cb);dp.write_bytes(db);ap.write_bytes(ab)
  results.append({'case':name,'expected_passed':False,'observed_passed':observed['passed'],'control_passed':observed['passed'] is False,'rejection_flags':observed['failed_checks']})
 # Even updating the surrounding report hash cannot conceal a wrong lossless CSV hash.
 dp=root/'qa/current/dense/dense-check.json';ap=root/'qa/current/qa-summary.json';db=dp.read_bytes();ab=ap.read_bytes()
 dq=json.loads(db);dq['uncompressed_csv_sha256']='0'*64;dp.write_text(json.dumps(dq));aq=json.loads(ab)
 for row in aq['gate_reports']:
  if row['gate']=='dense':row['report_sha256']=hashlib.sha256(dp.read_bytes()).hexdigest()
 ap.write_text(json.dumps(aq));observed=validator.inspect(root);dp.write_bytes(db);ap.write_bytes(ab)
 results.append({'case':'coordinated_wrong_lossless_csv_hash','expected_passed':False,'observed_passed':observed['passed'],'control_passed':observed['passed'] is False and 'dense_lossless_csv_hash' in observed['failed_checks'],'rejection_flags':observed['failed_checks']})
 for name,rel in [('changed_preview','previews/top.png'),('changed_stl_header','model.stl')]:
  p=root/rel;old=p.read_bytes();q=bytearray(old);q[0]^=1;p.write_bytes(q);observed=validator.inspect(root);p.write_bytes(old)
  results.append({'case':name,'expected_passed':False,'observed_passed':observed['passed'],'control_passed':observed['passed'] is False,'rejection_flags':observed['failed_checks']})
 p=root/'architectural-features.json';old=p.read_bytes();p.unlink();observed=validator.inspect(root);p.write_bytes(old);results.append({'case':'missing_required_report','expected_passed':False,'observed_passed':observed['passed'],'control_passed':observed['passed'] is False,'rejection_flags':observed['failed_checks']})
report={'python_optimization_level':sys.flags.optimize,'passed':all(r['control_passed'] for r in results),'controls':results,'source_validator_sha256':hashlib.sha256((R/'validate_model.py').read_bytes()).hexdigest(),'source_control_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'limits':'Synthetic mutations of copied reports/artifacts test aggregation logic, not architecture or physical printing.'}
(R/'aggregate-controls.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
