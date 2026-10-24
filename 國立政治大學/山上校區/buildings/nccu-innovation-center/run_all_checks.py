from pathlib import Path
import subprocess,sys
A=Path(__file__).resolve().parent
for name in ['qa_model.py','check_features.py','check_cavity_clearance.py','verify_exchange.py']:subprocess.run([sys.executable,str(A/name)],check=True)
for name in ['verify_scene.py','verify_render.py']:subprocess.run(['blender','-b','-t','4','--python-exit-code','1','--python',str(A/name)],check=True)
print('EXECUTED TECHNICAL GATES COMPLETE; RETAIN CAVITY AND THIN/SUPPORT WARNINGS, NOT PRINT CERTIFICATION')
