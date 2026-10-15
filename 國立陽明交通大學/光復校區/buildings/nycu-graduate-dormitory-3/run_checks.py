"""Complete author-side evidence pipeline. Strict short-normal failure is retained.
No publication approval is granted by this runner; independent review is separate.
"""
from pathlib import Path
import subprocess,sys,json,hashlib,os
R=Path(__file__).resolve().parent;stl=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest();steps=[]
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MALLOC_ARENA_MAX':'2','LP_NUM_THREADS':'1'}
for name,expected in [('check_provenance.py',0),('check_raw_mesh.py',0),('check_component_detail.py',0),('check_dense_surface.py',1),('check_corner_roots.py',0),('check_full_intervals.py',0),('check_negative_controls.py',0),('check_reproducibility.py',0)]:
 p=subprocess.run([sys.executable,str(R/name)],cwd=R,env=env,capture_output=True,text=True)
 item={'script':name,'script_sha256':hashlib.sha256((R/name).read_bytes()).hexdigest(),'expected_exit_code':expected,'actual_exit_code':p.returncode,'passed':p.returncode==expected};steps.append(item);print(json.dumps(item),flush=True)
 if p.returncode!=expected:print(p.stdout[-5000:]);print(p.stderr[-5000:]);raise RuntimeError(name+' failed evidence pipeline')
 assert hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()==stl,'Original STL changed while checking'
dense=json.loads((R/'dense-short-chords.json').read_text());roots=json.loads((R/'corner-roots.json').read_text());full=json.loads((R/'full-interval-check.json').read_text())
assert dense['passed'] is False and dense['under_0p8mm_count']==roots['original_short_count']==roots['witness_count']
assert all(v for k,v in dense['checks'].items() if k!='all_first_chords_ge_0p8mm')
assert roots['passed'] and full['passed']
reports=['raw-mesh-check.json','component-detail.json','dense-short-chords.json','corner-roots.json','full-interval-check.json','negative-controls.json','reproducibility.json']
for name in reports:assert json.loads((R/name).read_text())['stl_sha256']==stl,(name,'wrong STL')
out={'stl_sha256':stl,'author_evidence_passed':True,'strict_dense_passed':False,'strict_dense_short_count':dense['under_0p8mm_count'],'all_specific_corner_witnesses_and_full_intervals_passed':True,'independent_approval':'Required separately for this fresh v2; no previous approval is reused','steps':steps,'reports':{name:hashlib.sha256((R/name).read_bytes()).hexdigest()for name in reports}}
(R/'qa-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
