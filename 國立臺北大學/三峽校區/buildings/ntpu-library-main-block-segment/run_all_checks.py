"""Run final QA in order; no publication side effects."""
from pathlib import Path
import subprocess,sys
A=Path(__file__).resolve().parent
for n in ['qa_model.py','check_features.py','check_cavities.py','verify_exchange.py']:subprocess.run([sys.executable,str(A/n)],check=True)
for n in ['verify_scene.py','verify_render.py']:subprocess.run(['blender','-b','-t','4','--python-exit-code','1','--python',str(A/n)],check=True)
print('ALL MODEL CHECKS PASSED; inspect retained thin warnings; not publication approval')
