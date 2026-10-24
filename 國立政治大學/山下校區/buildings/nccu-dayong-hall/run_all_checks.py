from pathlib import Path
import subprocess,sys,os
A=Path(__file__).resolve().parent
for name in ['qa_model.py','check_features.py','check_rays.py','check_all_face_rays.py','check_interfaces.py','check_true_ramp_interface.py','verify_exchange.py']:subprocess.run([sys.executable,str(A/name)],check=True)
for name in ['verify_scene.py','verify_render.py']:subprocess.run([os.environ.get('BLENDER','blender'),'-b','-t','4','--python-exit-code','1','--python',str(A/name)],check=True)
