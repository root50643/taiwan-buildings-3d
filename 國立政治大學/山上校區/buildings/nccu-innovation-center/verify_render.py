"""Reopen delivered scene and rerender saved front camera; compare PNG pixels/bytes."""
import subprocess,os
import bpy,json,struct,hashlib,tempfile
from pathlib import Path
A=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'front.png';bpy.context.scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
  pos+=n+12
 p.write_bytes(clean);subprocess.run([os.environ.get('BUILD_PYTHON','python3'),str(A/'caption_preview.py'),str(p)],check=True);clean=p.read_bytes()
 assert clean==(A/'previews/front.png').read_bytes()
(A/'qa/render-reopen-validation.json').write_text(json.dumps(dict(scene_front_camera_reopen_render_exact=True,front_sha256=hashlib.sha256(clean).hexdigest(),method='same Blender CPU Cycles seed 0, strip only PNG textual/date metadata; unchanged geometry and materials'),indent=2)+'\n')
