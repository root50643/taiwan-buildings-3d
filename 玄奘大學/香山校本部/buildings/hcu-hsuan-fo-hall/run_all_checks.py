"""Run HCU hall checks; dependencies per requirements.txt, Blender separately installed."""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib
A=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--blender',default='blender');p.add_argument('--rebuild-dir',type=Path);args=p.parse_args()
for name in ['qa_model.py','check_features.py','verify_exchange.py']:subprocess.run([sys.executable,str(A/name)],check=True)
for name in ['verify_scene.py','verify_render.py']:subprocess.run([args.blender,'-b','-t','4','--python-exit-code','1','--python',str(A/name)],check=True)
if args.rebuild_dir:subprocess.run([sys.executable,str(A/'rebuild.py'),'--output',str(args.rebuild_dir),'--blender',args.blender,'--threads','4'],check=True)
print('HCU Hsuan Fo Hall requested checks completed; read thin-layer failures in qa-layers.json, not a printability certificate')
