"""Remove renderer metadata; record public pixel hashes without private paths."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
manifest=json.loads((R/'render-manifest.json').read_text())
for p in sorted((R/'previews').glob('*.png')):
 with Image.open(p) as im: clean=Image.frombytes('RGBA',im.size,im.convert('RGBA').tobytes())
 clean.save(p)
 manifest['views'][p.stem]['rgba_sha256']=hashlib.sha256(clean.tobytes()).hexdigest()
 manifest['views'][p.stem]['png_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 assert not Image.open(p).info
(R/'render-manifest.json').write_text(json.dumps(manifest,indent=2))
