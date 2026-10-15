"""Strict JSON, complete relative file inventories and immutable digest checks."""

import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json
DERIVED={'artifact-integrity.json','freeze-manifest.json','SHA256SUMS'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
 def reject(v):raise ValueError('Nonfinite JSON value: '+v)
 return json.loads(Path(path).read_text(),parse_constant=reject)
def require(value,message):
 if not bool(value):raise RuntimeError(message)
def files(root,exclude=()):
 root=Path(root);out={}
 for p in sorted(root.rglob('*')):
  require(not p.is_symlink(),'Symlink is not allowed in a frozen package')
  name=p.relative_to(root).as_posix()
  if p.is_file() and name not in exclude:
   out[name]={'sha256':sha(p),'bytes':p.stat().st_size}
 return out
def source_inventory(root):
 return {n:v for n,v in files(root).items() if Path(n).suffix in {'.py','.cpp'} or n=='requirements.txt'}
def write_json(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
