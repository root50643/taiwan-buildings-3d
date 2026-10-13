from pathlib import Path
import hashlib
r=Path(__file__).resolve().parent
for row in (r/'SHA256SUMS').read_text().splitlines():
 h,name=row.split('  ',1);p=r/name
 assert p.is_file(),name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
print('All SHA256SUMS entries match.')
