"""Independently rerender actual STL and compare clean PNG pixels and metadata."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,tempfile
from PIL import Image
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as td:
 tmp=Path(td)
 for name in ['model.stl','render_preview.py','clean_previews.py']:shutil.copy(R/name,tmp/name)
 subprocess.run(['blender','-b','-t','2','-P',str(tmp/'render_preview.py')],check=True,capture_output=True)
 subprocess.run([sys.executable,str(tmp/'clean_previews.py')],check=True,capture_output=True)
 records=[]
 for path in sorted((R/'previews').glob('*.png')):
  a=Image.open(path);b=Image.open(tmp/'previews'/path.name)
  same=a.size==b.size and a.mode==b.mode and a.tobytes()==b.tobytes()
  clean=not a.info and not b.info
  assert same and clean,(path.name,same,a.info)
  records.append({'file':'previews/'+path.name,'pixels_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':a.size,'matches_independent_actual_stl_render':same,'metadata_empty':clean})
 report={'passed':True,'checks':{'all_previews_match_independent_actual_stl_rerender':True,'all_png_metadata_empty':True,'no_private_path_metadata':True},'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'images':records}
 (R/'preview-check.json').write_text(json.dumps(report,indent=2));print({'passed':True,'images':len(records)})
