"""Create deterministic-content delivery archive, excluding references and logs."""
from pathlib import Path
import hashlib,zipfile
P=Path(__file__).resolve().parent
files=['README.md','sources.md','model.stl','scene.blend','build_model.py','render_preview.py','validate_model.py','verify_rebuild.py','package_model.py','verify_blend.py','blend_validation.json','requirements.txt','validation.json','rebuild_validation.json','previews/front.png','previews/rear.png','previews/elevation.png']
for name in files: assert (P/name).is_file(),name
h=''.join(hashlib.sha256((P/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in sorted(files))
(P/'SHA256SUMS.txt').write_text(h)
archive=P.parent/'palace-museum-north-model.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in sorted(files+['SHA256SUMS.txt']):
  info=zipfile.ZipInfo('palace-museum-north-model/'+name,date_time=(2026,10,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,(P/name).read_bytes(),compresslevel=9)
print(archive)
print('SHA256:',hashlib.sha256(archive.read_bytes()).hexdigest())
