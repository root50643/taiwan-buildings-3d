"""Re-render copied actual STL in a separate directory; compare every PNG pixel.
No source photograph is used or included. Never silently substitute a repair.
"""
from pathlib import Path
import tempfile,subprocess,shutil,hashlib,json,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
with tempfile.TemporaryDirectory() as t:
 T=Path(t)
 for f in ['model.stl','render_preview.py','render_top_edges.py']:shutil.copy(R/f,T/f)
 subprocess.run(['blender','-b','-t','4','-P',str(T/'render_preview.py')],check=True,capture_output=True)
 subprocess.run([sys.executable,str(T/'render_top_edges.py')],check=True,capture_output=True)
 for name in ['front','north','rear','west','east','top','aerial','swfit','eastfit','top-lines']:
  p=R/'previews'/f'{name}.png';q=T/'previews'/p.name
  a=np.asarray(Image.open(p).convert('RGBA'));b=np.asarray(Image.open(q).convert('RGBA'))
  checks={'dimensions_1200x900':a.shape==(900,1200,4),'nonblank':len(np.unique(a[:,:,:3].reshape(-1,3),axis=0))>100,'independent_render_pixels_identical':bool(np.array_equal(a,b)),'independent_png_bytes_identical':p.read_bytes()==q.read_bytes()}
  assert all(checks.values()),(name,checks)
  rows.append({'view':name,'file':str(p.relative_to(R)),'sha256':sha(p.read_bytes()),'pixel_sha256':sha(a.tobytes()),'checks':checks})
report={'passed':True,'checks':{'ten_actual_stl_images_verified':len(rows)==10,'all_independent_pixel_rebuilds_match':all(r['checks']['independent_render_pixels_identical'] for r in rows)},'stl_sha256':sha((R/'model.stl').read_bytes()),'render_script_sha256':sha((R/'render_preview.py').read_bytes()),'views':rows,'limits':'Pixel identity verifies reproducible rendering of the delivered STL, not architectural fidelity.'}
(R/'render-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
