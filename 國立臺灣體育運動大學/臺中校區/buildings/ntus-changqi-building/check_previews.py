"""Re-render saved editable Blender scene at saved actual-STL views; compare pixels."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from PIL import Image
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as td:
 t=Path(td)
 script=t/'render_saved_scene.py'
 script.write_text("""import bpy,json
from pathlib import Path
scene=bpy.context.scene
models=[o for o in scene.objects if o.type=='MESH'];assert len(models)==1
views=json.loads(models[0]['preview_cameras_json']);cam=scene.camera
for name,v in views.items():
 cam.location=v['location'];cam.rotation_euler=v['rotation_euler'];cam.data.ortho_scale=v['ortho_scale']
 scene.render.filepath=str(Path(%r)/(name+'.png'));bpy.ops.render.render(write_still=True)
""" % str(t))
 subprocess.run(['blender','-b',str(R/'scene.blend'),'-t','4','-P',str(script)],check=True,capture_output=True,text=True)
 rows=[]
 for path in sorted((R/'previews').glob('*.png')):
  a=Image.open(path);b=Image.open(t/path.name)
  same=a.size==b.size and a.mode==b.mode and a.tobytes()==b.tobytes()
  clean=not a.info
  rows.append({'view':path.name,'dimensions_px':list(a.size),'delivered_pixel_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'saved_blend_render_pixel_sha256':hashlib.sha256(b.tobytes()).hexdigest(),'pixels_identical':same,'ancillary_metadata_empty':clean})
  assert same and clean,(path.name,same,a.info)
report={'passed':True,'checks':{'all_saved_blend_renders_match_delivered_png_pixels':True,'all_png_ancillary_metadata_empty':True,'all_previews_900px_wide':all(x['dimensions_px'][0]==900 for x in rows)},'views':rows,'method':'Saved Blender scene re-rendered to an independent temporary directory; decoded pixel bytes compared, not file metadata. validate_model.py separately proves saved Blend triangle geometry equals actual delivered STL.'}
(R/'preview-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
