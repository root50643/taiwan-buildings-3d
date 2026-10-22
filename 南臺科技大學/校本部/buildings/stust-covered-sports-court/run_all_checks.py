"""STUST 2020 covered sports court checks; no physical-print certification."""
from pathlib import Path
import subprocess,sys,os
A=Path(__file__).resolve().parent
for n in ['qa_model.py','check_features.py']:
 subprocess.run([sys.executable,str(A/n)],check=True)
subprocess.run([os.environ.get('LIB3MF_PYTHON',sys.executable),str(A/'verify_exchange.py')],check=True)
for n in ['verify_scene.py','verify_render.py']:
 subprocess.run(['blender','-b','-t','4','--python-exit-code','1','--python',str(A/n)],check=True)
print('Read QA layer/local thin failures; these checks are not a physical-print certificate.')
