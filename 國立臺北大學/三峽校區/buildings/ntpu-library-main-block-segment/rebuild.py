"""Rebuild geometry plus five actual-mesh views in a clean directory and compare bytes."""
from pathlib import Path
import argparse,subprocess,shutil,hashlib,json,sys
A=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--blender',default='blender');p.add_argument('--threads',default='4');args=p.parse_args();R=args.output.resolve()
assert R!=A and not R.exists(), 'Use a new output directory, never the delivered model directory'
R.mkdir(parents=True);(R/'previews').mkdir();(R/'qa').mkdir()
for n in ['build_model.py','render_model.py']:shutil.copy2(A/n,R/n)
subprocess.run([sys.executable,str(R/'build_model.py')],check=True)
subprocess.run([args.blender,'-b','-t',args.threads,'--python-exit-code','1','--python',str(R/'render_model.py')],check=True)
files=['model.stl','model.3mf','mesh.json','palette.json']+['previews/'+n+'.png' for n in ['front','rear','elevation','top','left_oblique']]
hashes={}
for n in files:
 assert (R/n).read_bytes()==(A/n).read_bytes(),n
 hashes[n]=hashlib.sha256((A/n).read_bytes()).hexdigest()
(A/'qa/isolated-rebuild.json').write_text(json.dumps(dict(method='Independent directory geometry generation and full five-view Blender render using delivered rebuild.py, fail-on-Python-error; exact bytes',files_identical=hashes,all_five_previews_identical=True,delivered_generators_sha256={n:hashlib.sha256((A/n).read_bytes()).hexdigest() for n in ["build_model.py","render_model.py"]}),indent=2)+'\n')
print('INDEPENDENT REBUILD ALL NINE ARTIFACTS EXACT')
