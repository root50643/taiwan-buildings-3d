"""Render every actual-STL preview again; assert exact PNG SHA matches."""
from pathlib import Path
import tempfile,subprocess,shutil,hashlib,json
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
with tempfile.TemporaryDirectory() as td:
 t=Path(td)
 for n in ['model.stl','render_preview.py']:shutil.copy(r/n,t/n)
 subprocess.run(['blender','-b','-t','5','-P',str(t/'render_preview.py')],check=True,capture_output=True)
 for p in sorted((r/'previews').glob('*.png')):
  a=sha(p);b=sha(t/'previews'/p.name);assert a==b,(p.name,a,b)
  rows.append({'file':'previews/'+p.name,'sha256':a,'rebuild_sha256':b})
(r/'preview-rebuild-check.json').write_text(json.dumps({'passed':True,'checks':{'every_png_exact_rebuild':True,'render_source_is_delivered_stl':True},'images':rows},indent=2))
