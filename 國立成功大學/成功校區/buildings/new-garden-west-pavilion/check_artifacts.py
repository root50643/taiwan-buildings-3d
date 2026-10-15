"""Check distributable paths and PNG metadata; no reference photos are bundled."""

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

from pathlib import Path
import gzip,hashlib,json
from PIL import Image
R=Path(__file__).resolve().parent
patterns=[b'/workspace/',b'/home/agent',b'/tmp/',b'file://',b'Authorization: Bearer']
rows=[];bad=[]
for path in sorted(R.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.name in ['check_artifacts.py','artifact-integrity.json','SHA256SUMS','freeze-manifest.json']:continue
    data=path.read_bytes()
    if path.suffix=='.gz':data=gzip.decompress(data)
    if any(p in data for p in patterns):bad.append(str(path.relative_to(R)))
    if path.suffix=='.png':
        im=Image.open(path);info=im.info
        allowed={'exif','dpi','cycles.ViewLayer.samples'}
        exif=im.getexif()
        clean=set(info)<=allowed and info.get('cycles.ViewLayer.samples')=='64' and set(exif)<={282,283,296}
        rows.append({'path':str(path.relative_to(R)),'size':list(im.size),'metadata_keys':sorted(info),'exif_tags':{str(k):str(v) for k,v in exif.items()},'clean':clean,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
checks={'no_private_absolute_paths_or_auth_tokens':not bad,'six_generated_preview_pngs':len(rows)==6 and all(r['path'].startswith('previews/') for r in rows),
        'png_metadata_only_resolution_and_fixed_samples':all(r['clean'] for r in rows),
        'no_jpeg_reference_photos':not list(R.rglob('*.jpg')) and not list(R.rglob('*.jpeg')),
        'no_blend_backups':not list(R.rglob('*.blend1'))}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'flagged_paths':bad,'pngs':rows,'note':'The scanner source itself contains generic search patterns and is excluded from literal self-matching. This does not authorize any exception in deliverables.'}
(R/'artifact-integrity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));require(report['passed'], 'Required condition failed')
