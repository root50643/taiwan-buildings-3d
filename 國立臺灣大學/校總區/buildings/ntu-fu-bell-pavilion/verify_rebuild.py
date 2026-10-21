"""Independent empty-directory rebuild of geometry and all five actual mesh views."""
from pathlib import Path
import tempfile,subprocess,hashlib,os,json,shutil
A=Path(__file__).resolve().parent
names=['model.stl','model.3mf','mesh.json','palette.json']+['previews/'+n+'.png' for n in ['front','rear','elevation','top','left_oblique']]
with tempfile.TemporaryDirectory(prefix='fu-bell-independent-') as td:
 B=Path(td);(B/'previews').mkdir();(B/'qa').mkdir()
 for n in ['build_model.py','render_model.py']:shutil.copy2(A/n,B/n)
 subprocess.run([os.environ['BUILD_PYTHON'],str(B/'build_model.py')],check=True)
 subprocess.run(['blender','-b','-t','6','--python-exit-code','1','--python',str(B/'render_model.py')],check=True)
 hashes={}
 for n in names:
  h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
  assert h(A/n)==h(B/n),n;hashes[n]=h(A/n)
(A/'qa/isolated-rebuild.json').write_text(json.dumps(dict(empty_directory_rebuild=True,blender_python_exit_code=1,files_identical=hashes,scene_binary_not_compared='Blender stores filepath/save metadata; actual rendered five views and geometry all exact'),indent=2)+'\n')
