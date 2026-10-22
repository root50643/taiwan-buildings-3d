"""Run MUST fountain checks; lib3mf may use separate Python via --exchange-python."""
from pathlib import Path
import argparse,subprocess,sys,os
A=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--blender',default='blender');p.add_argument('--exchange-python',default=sys.executable);p.add_argument('--rebuild-dir',type=Path);args=p.parse_args()
for n in ['qa_model.py','check_features.py']:subprocess.run([sys.executable,str(A/n)],check=True)
subprocess.run([args.exchange_python,str(A/'verify_exchange.py')],env={**os.environ,'BUILD_PYTHON':sys.executable},check=True)
for n in ['verify_scene.py','verify_render.py']:subprocess.run([args.blender,'-b','-t','4','--python-exit-code','1','--python',str(A/n)],check=True)
if args.rebuild_dir:subprocess.run([sys.executable,str(A/'rebuild.py'),'--output',str(args.rebuild_dir),'--blender',args.blender,'--threads','4'],check=True)
print('MUST fountain checks complete; inspect reports, not physical print certification')
