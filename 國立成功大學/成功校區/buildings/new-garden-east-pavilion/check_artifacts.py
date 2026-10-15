"""Scan every current payload and bind its exact bytes to the privacy report."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import gzip,json
from PIL import Image
from integrity_utils import sha,files,write_json,require,DERIVED
R=Path(__file__).resolve().parent
patterns=[b'/workspace/',b'/home/agent',b'/tmp/',b'file://',b'Authorization: Bearer']
rows=[];bad=[];inventory=files(R,DERIVED)
for name in inventory:
 path=R/name;data=path.read_bytes()
 if path.suffix=='.gz':data=gzip.decompress(data)
 # Detector literals are not private paths. Check the remainder of this file.
 if name=='check_artifacts.py':
  data=b'\n'.join(line for line in data.splitlines() if not line.startswith(b'patterns=['))
 if any(p in data for p in patterns):bad.append(name)
 if path.suffix=='.png':
  im=Image.open(path);info=im.info;exif=im.getexif()
  clean=set(info)<={'exif','dpi','cycles.ViewLayer.samples'} and info.get('cycles.ViewLayer.samples')=='24' and set(exif)<={282,283,296}
  rows.append({'path':name,'size':list(im.size),'metadata_keys':sorted(info),'exif_tags':{str(k):str(v) for k,v in exif.items()},'clean':clean,'sha256':sha(path)})
checks={'no_private_paths_or_auth_tokens':not bad,'six_generated_preview_pngs':len(rows)==6 and all(r['path'].startswith('previews/') for r in rows),
        'png_metadata_clean':all(r['clean'] for r in rows),'no_reference_photos':not list(R.rglob('*.jpg')) and not list(R.rglob('*.jpeg')),
        'no_blend_backups_or_python_cache':not list(R.rglob('*.blend1')) and not list(R.rglob('*.pyc'))}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'flagged_paths':bad,'scanned_files':inventory,'pngs':rows,
        'exclusions':['This report itself','freeze-manifest.json','SHA256SUMS'],
        'note':'All payload bytes, including checker source, are bound. Only the detector-literal declaration is ignored during its own literal scan. Derived reports and manifest are bound by the sealed manifest.'}
report['evidence_sources']={n:__import__('hashlib').sha256((R/n).read_bytes()).hexdigest() for n in ['check_artifacts.py', 'integrity_utils.py']}
write_json(R/'artifact-integrity.json',report);print(json.dumps(report,indent=2));require(report['passed'],'Artifact privacy/metadata scan failed')
