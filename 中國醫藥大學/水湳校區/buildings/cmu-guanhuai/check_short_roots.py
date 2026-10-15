"""Every short dense sample: preserve its normal/air, pair/triple actual-face root.
Unresolved samples fail closed; directions never selected by longest ray search.
"""
from pathlib import Path
import csv,gzip,tempfile,subprocess,json,hashlib,collections,trimesh,math
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as td:
 t=Path(td);m=trimesh.load(R/'model.stl',process=False);m.triangles.astype('float64').tofile(t/'tri.bin');selected=0
 with (t/'queries.txt').open('w') as f:
  for r in csv.DictReader(gzip.open(R/'dense-samples.csv.gz','rt')):
   if float(r['first_solid'])>=.8:continue
   selected+=1;air=float(r['air_after']);air=air if math.isfinite(air) else -1
   f.write(' '.join([r[k] for k in ['face','sample','x','y','z','first_solid']]+[str(air)])+'\n')
 subprocess.run(['g++','-O3','-std=c++17',str(R/'corner_roots.cpp'),'-o',str(t/'roots')],check=True)
 subprocess.run([str(t/'roots'),str(t/'tri.bin'),str(t/'queries.txt'),str(R/'short-root-classification.csv')],check=True)
rows=list(csv.DictReader((R/'short-root-classification.csv').open()));counts=dict(collections.Counter(r['classification'] for r in rows));fail=[r for r in rows if r['classification']=='unresolved'];j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'selected_short_samples':selected,'rows':len(rows),'classification_counts':counts,'unresolved':fail,'passed':len(rows)==selected and not fail,'limitations':'Original normal short chord and later air remain separate. Pair uses entry and its actual first exit; triple adds the actual pair-direction first exit. Root direction inward constraints and four controls are retained. This is finite sampling, not a global wall guarantee.'};(R/'short-root-summary.json').write_text(json.dumps(j,indent=2));print('counts',counts,'unresolved',len(fail));assert j['passed']
