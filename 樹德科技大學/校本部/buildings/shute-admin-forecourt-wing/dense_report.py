"""Read compressed per-face raw diagnostic records without dropping failures."""
import gzip,json,hashlib
from pathlib import Path
def load_dense_report(root):
 root=Path(root);r=json.loads((root/'dense-short-chords.json').read_text())
 if 'short_chords_file' in r:
  p=root/r['short_chords_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['short_chords_sha256']
  r['short_chords']=json.load(gzip.open(p,'rt'))
 return r
