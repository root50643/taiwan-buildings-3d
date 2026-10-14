"""Independently rebuild and re-render every public PNG from the delivered STL."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};results=[]
with tempfile.TemporaryDirectory() as td:
 T=Path(td)
 for f in ['build_model.py','render_preview.py']:shutil.copy(R/f,T/f)
 subprocess.run([sys.executable,str(T/'build_model.py')],check=True,capture_output=True,text=True)
 checks['independent_rebuild_stl_sha_matches']=sha(R/'model.stl')==sha(T/'model.stl')
 subprocess.run(['blender','-b','-t','2','-P',str(T/'render_preview.py')],check=True,capture_output=True,text=True)
 for p in sorted((R/'previews').glob('*.png')):
  im=Image.open(p);im.load();other=Image.open(T/'previews'/p.name);other.load()
  same=im.mode==other.mode and im.size==other.size and im.tobytes()==other.tobytes()
  checks[p.stem+'_actual_stl_pixels_match']=same
  checks[p.stem+'_no_private_metadata']=not im.info
  results.append({'file':'previews/'+p.name,'dimensions_px':list(im.size),'sha256':sha(p),'pixels_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'independent_pixels_sha256':hashlib.sha256(other.tobytes()).hexdigest()})
report={'passed':all(checks.values()),'checks':checks,'method':'Fresh directory; regenerate STL from original parameters; render actual rebuilt STL in Blender; compare full uncompressed PNG pixel bytes and require delivered PNG metadata empty. Scene mesh independently checked by validate_model.py.','images':results}
(R/'render-reproduction-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
