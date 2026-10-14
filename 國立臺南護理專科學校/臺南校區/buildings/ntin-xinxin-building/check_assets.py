"""Independent saved-Blend reload and actual-pixel preview equivalence."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from PIL import Image,ImageChops
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='ntin-saved-blend-') as d:
 subprocess.run(['blender','-b','-t','4','-P',str(R/'check_saved_blend.py'),'--',d],check=True,capture_output=True)
 result=json.loads((Path(d)/'blend-check.json').read_text())
 for name in ['front','rear','elevation','side','top']:
  im=Image.open(Path(d)/(name+'.png')).convert('RGB');im.save(Path(d)/(name+'-stripped.png'))
  previous=Image.open(R/'previews'/(name+'.png')).convert('RGB')
  result['checks'][f'saved_blend_{name}_pixels_exactly_match_delivery_png']=ImageChops.difference(im,previous).getbbox() is None
  result['checks'][f'saved_blend_{name}_png_sha256_match']=hashlib.sha256((Path(d)/(name+'-stripped.png')).read_bytes()).hexdigest()==hashlib.sha256((R/'previews'/(name+'.png')).read_bytes()).hexdigest()
 result['checks']['all_preview_png_metadata_empty']=all(not Image.open(p).info for p in (R/'previews').glob('*.png'))
 result['checks']['all_preview_png_width_900px']=all(Image.open(p).size[0]==900 and Image.open(p).size[1]<=1400 for p in (R/'previews').glob('*.png'))
 result['passed']=all(result['checks'].values());result['stl_sha256']=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest();result['scene_blend_sha256']=hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest();result['preview_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'previews').glob('*.png'))}
 (R/'asset-consistency-check.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));assert result['passed']
