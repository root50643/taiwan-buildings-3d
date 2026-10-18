"""Compare decoded candidate and independently rendered front images."""
from pathlib import Path
import hashlib
import json
import os
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scene-evidence'
p=Image.open(Path(os.environ['CHENGQIN_PACKAGE']).resolve()/'previews/v1/front.png')
q=Image.open(OUT/'independent-front.png')
a=p.convert('RGBA')
b=q.convert('RGBA')
assert a.size==b.size
d=np.abs(np.asarray(a).astype(float)-np.asarray(b).astype(float))
result=dict(candidate_size=a.size,independent_size=b.size,
    pixels_equal=a.tobytes()==b.tobytes(),
    mean_absolute_channel_difference_8bit=float(d.mean()),
    max_channel_difference_8bit=float(d.max()),
    differing_pixel_count=int(np.any(d>0,axis=2).sum()),
    candidate_pixels_sha256=hashlib.sha256(a.tobytes()).hexdigest(),
    independent_pixels_sha256=hashlib.sha256(b.tobytes()).hexdigest(),
    candidate_info_keys=list(p.info),independent_info_keys=list(q.info),
    metadata_difference_keys=sorted(k for k in set(p.info)|set(q.info) if p.info.get(k)!=q.info.get(k)))
(OUT/'independent-front-pixel-comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
