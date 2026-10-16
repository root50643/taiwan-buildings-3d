"""Bind every current deliverable, report and checker; no trust in old passed flags."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
EXCLUDE={'validation.json','validation-inputs.json','SHA256SUMS','freeze-manifest.json'}
def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and str(p.relative_to(root)) not in EXCLUDE}
if __name__=='__main__':
    (R/'validation-inputs.json').write_text(json.dumps({'algorithm':'sha256','files':inventory(R),'limits':'Integrity binding is not an independent approval or a geometry repair.'},indent=2)+'\n')
