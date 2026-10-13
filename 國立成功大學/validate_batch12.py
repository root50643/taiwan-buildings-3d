"""Fail-closed batch gate; requires Python model dependencies and Blender. Not a slicer."""
from pathlib import Path
import subprocess,json,concurrent.futures,hashlib
R=Path(__file__).resolve().parent
def run(rel):
 d=R/rel
 for script,name in [('validate_model.py','validation.json'),('validate_sections.py','cross_sections.json'),('check_thin.py','thin-feature-check.json')]:
  p=subprocess.run(['python',str(d/script)],capture_output=True,text=True);assert p.returncode==0,(d,script,p.stdout,p.stderr)
  x=json.loads((d/name).read_text());assert x['stl_sha256']==hashlib.sha256((d/'model.stl').read_bytes()).hexdigest()
  if 'passed' in x:assert x['passed']
  if 'checks' in x:assert all(v is True for v in x['checks'].values())
 print(d.name,'PASS',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,['光復校區/buildings/hsiu-chi-building', '光復校區/buildings/management-college-building', '勝利校區/buildings/swimming-ball-sports-building']))
