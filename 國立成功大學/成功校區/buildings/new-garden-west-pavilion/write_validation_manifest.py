"""Snapshot all current distributable evidence and its actual content hashes.
Only generated aggregate/manifest files and interpreter bytecode are excluded.
Run after all checks; the validator must independently recalculate this inventory.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
EXCLUDE={'validation.json','validation-inputs.json','SHA256SUMS','freeze-manifest.json'}
def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and p.name not in EXCLUDE}
if __name__=='__main__':
    (R/'validation-inputs.json').write_text(json.dumps({'algorithm':'sha256','files':inventory(R)},indent=2)+'\n')
