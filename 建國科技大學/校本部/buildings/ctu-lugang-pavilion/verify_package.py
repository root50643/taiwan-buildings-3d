"""Verify delivered files and evidence binding for 建國科技大學綠崗亭."""
from pathlib import Path
import hashlib,json,subprocess,sys
A=Path(__file__).parent
for line in (A/'SHA256SUMS').read_text().splitlines():
 h,n=line.split('  ',1);assert hashlib.sha256((A/n).read_bytes()).hexdigest()==h,n
sha=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest()
for n,key in [('release.json','stl_sha256'),('qa-topology.json','sha256'),('qa-layers.json','stl_sha256'),('qa/feature-validation.json','stl_sha256'),('qa/exchange-validation.json','source_STL_SHA256')]:assert json.loads((A/n).read_text())[key]==sha,n
assert json.loads((A/'qa/scene-validation.json').read_text())['scene_sha256']==hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest()
for n,h in json.loads((A/'qa/isolated-rebuild.json').read_text())['files_identical'].items():assert hashlib.sha256((A/n).read_bytes()).hexdigest()==h,n
for r in json.loads((A/'qa/render-manifest.json').read_text())['files']:assert hashlib.sha256((A/r['path']).read_bytes()).hexdigest()==r['sha256']
assert json.loads((A/'qa/render-reopen-validation.json').read_text())['front_sha256']==hashlib.sha256((A/'previews/front.png').read_bytes()).hexdigest()
assert len(list((A/'previews').glob('*.png')))==5
assert json.loads((A/'qa/identity-validation.json').read_text())['all_text_names_consistent']
review=json.loads((A/'qa/independent-appearance-review.json').read_text());assert review['status']=='PASS_SOURCE_BOUND_EXTERIOR_APPROXIMATION'
for r in review['artifacts']:
 assert (A/r['path']).stat().st_size==r['bytes'] and hashlib.sha256((A/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
print('PASS: checksums, topology/exchange/feature/release bindings, scene, isolated rebuild and five rendered PNG bindings')
