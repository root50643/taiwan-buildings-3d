"""Run delivered CSU Childcare Building validation scripts with explicit interpreters."""
from pathlib import Path
import argparse,subprocess,sys,os
A=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--lib3mf-python',required=True);p.add_argument('--blender',default='blender');a=p.parse_args()
for name in ['qa_model.py','check_features.py']:subprocess.run([sys.executable,str(A/name)],check=True)
e=dict(os.environ,BUILD_PYTHON=sys.executable);subprocess.run([a.lib3mf_python,str(A/'verify_exchange.py')],env=e,check=True)
for name in ['verify_scene.py','verify_render.py']:subprocess.run([a.blender,'-b','-t','4','--python-exit-code','1','--python',str(A/name)],check=True)
print('CSU CHILDCARE BUILDING RAW MESH / EXCHANGE / SCENE / RENDER CHECKS PASS; NO PHYSICAL PRINT CLAIM')
