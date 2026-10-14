"""Verify saved Blend rerenders every delivered PNG pixel-for-pixel, plus metadata.
Does not overwrite any deliverable. Blender must be available on PATH.
"""
from pathlib import Path
import subprocess,tempfile,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
manifest=json.loads((R/'render-manifest.json').read_text())
checks={'manifest_matches_actual_stl':manifest['stl_sha256']==hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}
results={}
with tempfile.TemporaryDirectory() as td:
 t=Path(td)
 script="""import bpy,json
from pathlib import Path
R=Path(%r);T=Path(%r)
s=bpy.context.scene;c=s.camera;m=json.loads((R/'render-manifest.json').read_text())
for name,v in m['views'].items():
 c.location=v['camera_location'];c.rotation_euler=v['camera_rotation_euler'];c.data.ortho_scale=v['ortho_scale']
 s.render.filepath=str(T/(name+'.png'));bpy.ops.render.render(write_still=True)
"""%(str(R),str(t))
 (t/'render.py').write_text(script)
 subprocess.run(['blender','-b',str(R/'scene.blend'),'-t','3','-P',str(t/'render.py')],check=True,capture_output=True)
 for name,v in manifest['views'].items():
  p=R/'previews'/(name+'.png');a=Image.open(p);b=Image.open(t/(name+'.png'));ap=a.convert('RGBA').tobytes();bp=b.convert('RGBA').tobytes()
  data={'size_px':list(a.size),'metadata_empty':not bool(a.info),'rgba_sha256':hashlib.sha256(ap).hexdigest(),'blend_rerender_rgba_sha256':hashlib.sha256(bp).hexdigest()}
  checks[name+'_pixels_match_saved_blend']=a.size==b.size and ap==bp
  checks[name+'_metadata_empty']=not bool(a.info)
  checks[name+'_manifest_pixel_hash_matches']=data['rgba_sha256']==v['rgba_sha256']
  checks[name+'_manifest_png_hash_matches']=hashlib.sha256(p.read_bytes()).hexdigest()==v['png_sha256']
  results[name]=data
report={'passed':all(checks.values()),'checks':checks,'images':results,'method':'Fresh temporary renders of saved scene.blend with the recorded views. Pixel bytes are compared to delivered metadata-free PNGs. STL/Blend triangle identity checked separately.'}
(R/'preview-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
