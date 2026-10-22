"""Run NUK humanities A/B delivered raw mesh/exchange/scene checks."""
from pathlib import Path
import argparse,subprocess,sys,os,json
A=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--lib3mf-python',required=True);p.add_argument('--blender',default='blender');a=p.parse_args()
for n in ['qa_model.py','check_features.py']:subprocess.run([sys.executable,str(A/n)],check=True)
assert json.loads((A/'qa-layers.json').read_text())['all_components_survive_0_8mm']
subprocess.run([a.lib3mf_python,str(A/'verify_exchange.py')],env=dict(os.environ,BUILD_PYTHON=sys.executable),check=True)
for n in ['verify_scene.py','verify_render.py']:subprocess.run([a.blender,'-b','-t','4','--python-exit-code','1','--python',str(A/n)],check=True)
print('NUK A/B raw mesh, exchange, editable scene and render checks pass; no physical print claim')
