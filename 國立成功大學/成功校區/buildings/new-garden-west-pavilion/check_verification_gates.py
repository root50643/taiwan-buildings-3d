"""Expected-failure controls for normal thickness and optimized/tool exits.
Fixtures and diagnostic outputs are preserved; production geometry is read-only.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from build_model import box,save_stl
R=Path(__file__).resolve().parent;O=R/'verification-control-results';O.mkdir(exist_ok=True)
rows=[]
for name,shape,expect in [('thin_slab',box(0,10,0,10,0,.6),False),
                          ('thin_wall',box(0,.6,0,10,0,10),False),
                          ('thick_positive',box(0,10,0,10,0,3),True)]:
 d=O/name;d.mkdir(exist_ok=True);save_stl(shape,d/'model.stl')
 for f in ['check_dense_surface.py','dense_original.cpp','original_rays.py']:shutil.copyfile(R/f,d/f)
 proc=subprocess.run([sys.executable,'-O',str(d/'check_dense_surface.py')],capture_output=True,text=True)
 (d/'stdout.txt').write_text(proc.stdout);(d/'stderr.txt').write_text(proc.stderr.replace(str(R),'.'))
 rep=json.loads((d/'dense-short-chords.json').read_text())
 ok=(proc.returncode==0)==expect and rep['passed']==expect
 if not expect:ok=ok and rep['under_0p8mm_count']>0 and rep['checks']['all_first_chords_ge_0p8mm'] is False
 rows.append({'control':name,'passed':ok,'optimized_python':True,'returncode':proc.returncode,'input_sha256':hashlib.sha256((d/'model.stl').read_bytes()).hexdigest()})
# Run the known broken original-face fixture under optimized Python as well.
d=R/'negative-control-results/missing_triangle'
proc=subprocess.run([sys.executable,'-O',str(d/'check_raw_mesh.py')],capture_output=True,text=True)
rep=json.loads((d/'raw-mesh-check.json').read_text())
rows.append({'control':'raw_mesh_failure_survives_python_O','passed':proc.returncode!=0 and rep['passed'] is False,'returncode':proc.returncode})
# Blender defaults can return 0 for a Python exception; enforce its documented
# explicit error-exit option and prove it with this intentional exception.
b=O/'intentional_blender_failure.py';b.write_text("raise RuntimeError('Expected verification control failure')\n")
proc=subprocess.run(['blender','-b','-t','1','--python-exit-code','1','--python',str(b)],capture_output=True,text=True)
(O/'blender-failure.log').write_text((proc.stdout+proc.stderr).replace(str(R),'.'))
rows.append({'control':'blender_python_exception_nonzero','passed':proc.returncode!=0 and 'Expected verification control failure' in proc.stdout+proc.stderr,'returncode':proc.returncode})
r={'passed':all(q['passed'] for q in rows),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'checks':{q['control']:q['passed'] for q in rows},'controls':rows}
(R/'verification-gates.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if not r['passed']:raise SystemExit(1)
