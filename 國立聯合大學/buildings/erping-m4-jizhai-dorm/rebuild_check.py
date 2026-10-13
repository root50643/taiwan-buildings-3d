"""Rebuild from a portable source copy and compare binary STL SHA-256.
Run: python rebuild_check.py (requires requirements.txt in your Python environment).
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
from importlib.metadata import version
HERE=Path(__file__).resolve().parent
original=hashlib.sha256((HERE/'model.stl').read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='nuu-model-rebuild-') as td:
 td=Path(td);shutil.copy(HERE/'build_model.py',td/'build_model.py')
 subprocess.run([sys.executable,str(td/'build_model.py')],cwd=td,check=True)
 rebuilt=hashlib.sha256((td/'model.stl').read_bytes()).hexdigest()
report={'passed':original==rebuilt,'original_stl_sha256':original,'rebuilt_stl_sha256':rebuilt,'method':'Run a standalone copy of build_model.py in a new temporary directory; compare binary STL SHA-256.','dependencies':{p:version(p) for p in ['numpy','trimesh','manifold3d']}}
(HERE/'rebuild-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
