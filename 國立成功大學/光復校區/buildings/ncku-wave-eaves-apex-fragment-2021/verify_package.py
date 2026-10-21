"""Check report hashes against actual delivery files; no artifact repair."""
from pathlib import Path
import json,hashlib,zipfile
A=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256((A/p).read_bytes()).hexdigest()
stl=sha('model.stl')
for f,k in [('release.json','stl_sha256'),('qa-topology.json','sha256'),('qa-layers.json','stl_sha256'),('qa/local-features.json','stl_sha256'),('qa/exchange-validation.json','source_STL_SHA256')]:assert json.loads((A/f).read_text())[k]==stl,f
assert json.loads((A/'qa/scene-validation.json').read_text())['scene_sha256']==sha('scene.blend')
for r in json.loads((A/'qa/render-manifest.json').read_text())['files']:assert sha(r['path'])==r['sha256']
assert json.loads((A/'qa/render-reopen-validation.json').read_text())['front_sha256']==sha('previews/front.png')
assert zipfile.ZipFile(A/'model.3mf').testzip() is None
for name,h in json.loads((A/'qa/isolated-rebuild.json').read_text())['files_identical'].items():assert sha(name)==h
for name,h in json.loads((A/'qa/source-visual-review.json').read_text())['artifacts_sha256'].items():assert sha(name)==h
assert not list(A.rglob('*.pyc'))
assert len(list((A/'previews').glob('*.png')))==5
assert not list(A.rglob('*.jpg')) and not list(A.rglob('*.jpeg'))
print('All stored QA hashes refer to delivered bytes; five previews; no reference JPEGs.')
