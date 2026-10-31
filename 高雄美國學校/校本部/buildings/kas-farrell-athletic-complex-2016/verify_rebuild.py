from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib,numpy as np
p=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='tnfsh-hall-rebuild-') as d:
 q=Path(d);shutil.copy2(p/'build_model.py',q/'build_model.py');subprocess.run([sys.executable,str(q/'build_model.py')],check=True,stdout=subprocess.DEVNULL)
 a=np.load(p/'mesh-data.npz');b=np.load(q/'mesh-data.npz');c={k:bool(np.array_equal(a[k],b[k]))for k in ['vertices','faces','materials']};c['stl_sha256_equal']=hashlib.sha256((p/'model.stl').read_bytes()).digest()==hashlib.sha256((q/'model.stl').read_bytes()).digest();r={'checks':c,'passed':all(c.values()),'scope':'Independent fresh-directory procedural rebuild, no original source photos required'};(p/'REBUILD-QA.json').write_text(json.dumps(r,indent=2));print(r);assert r['passed']
