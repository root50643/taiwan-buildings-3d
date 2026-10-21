"""Reopen delivered scene; deterministic all-five-view byte comparison."""
import bpy,json,struct,hashlib,tempfile
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'))
results={}
with tempfile.TemporaryDirectory() as td:
 for r in json.loads((A/'qa/render-manifest.json').read_text())['files']:
  scene=bpy.context.scene;cam=scene.camera;cam.location=r['camera'];cam.rotation_euler=(Vector(r['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=r['ortho_scale'];bpy.context.view_layer.update()
  p=Path(td)/Path(r['path']).name;scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
  raw=p.read_bytes();clean=raw[:8];pos=8
  while pos<len(raw):
   n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
   if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
   pos+=n+12
  assert clean==(A/r['path']).read_bytes(),r['path'];results[r['path']]=hashlib.sha256(clean).hexdigest()
(A/'qa/render-reopen-validation.json').write_text(json.dumps(dict(all_five_camera_reopen_render_exact=True,front_sha256=results['previews/front.png'],files_identical=results,method='same Blender CPU Cycles seed 0; strip PNG text/date metadata only; unchanged geometry and materials'),indent=2)+'\n')
