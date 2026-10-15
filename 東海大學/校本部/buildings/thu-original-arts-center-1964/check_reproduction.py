#!/usr/bin/env python3
"""Compare independently rebuilt STL bytes and independently rendered pixel arrays."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(primary,replay):
 a=sha(primary/'model.stl');b=sha(replay/'model.stl');views=[]
 for name in ['preview-entrance.png','preview-courtyard.png','preview-plan.png']:
  p,q=Image.open(primary/name),Image.open(replay/name)
  pb,qb=p.tobytes(),q.tobytes();views.append({'file':name,'mode':p.mode,'size':list(p.size),'same_mode_and_dimensions':p.mode==q.mode and p.size==q.size,'same_pixels':pb==qb,'primary_pixel_sha256':hashlib.sha256(pb).hexdigest(),'replay_pixel_sha256':hashlib.sha256(qb).hexdigest(),'same_png_bytes':sha(primary/name)==sha(replay/name)})
 blend=json.loads((replay/'qa-blend.json').read_text())
 checks={'exact_stl_bytes_equal':a==b,'all_three_render_pixel_arrays_equal':all(v['same_mode_and_dimensions'] and v['same_pixels'] for v in views),'replay_blend_matches_exact_stl':blend['passed'] and blend['stl_sha256']==a}
 r={'stl_sha256':a,'replay_stl_sha256':b,'passed':all(checks.values()),'checks':checks,'views':views,'note':'PNG metadata and saved Blender serialization are not claimed byte-identical. STL bytes and actual render pixels are compared directly. Both scenes are checked against original oriented STL triangles.'}
 (primary/'qa-reproduction.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return r['passed']
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--primary',type=Path,default=HERE/'output');a.add_argument('--replay',type=Path,default=HERE/'reproduction');x=a.parse_args();raise SystemExit(0 if check(x.primary,x.replay) else 1)
