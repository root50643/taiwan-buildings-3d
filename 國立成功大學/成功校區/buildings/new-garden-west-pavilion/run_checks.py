"""Full verification of current deliverables, plus isolated source/render replay.
Does not replace the root STL or silently repair any source faces. Stops on failure.
"""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parent

def run(args):
    p=subprocess.run(args,cwd=R)
    if p.returncode!=0:raise SystemExit(p.returncode)
for name in ['check_raw_mesh.py','check_architectural_features.py','check_component_detail.py','check_dense_surface.py',
             'check_negative_controls.py','check_verification_gates.py']:
    run([sys.executable,str(R/name)])
run(['blender','-b',str(R/'scene.blend'),'-t','1','--python-exit-code','1','--python',str(R/'probe_scene.py')])
run([sys.executable,str(R/'check_reproducibility.py'),'--render'])
run([sys.executable,str(R/'check_artifacts.py')])
run([sys.executable,str(R/'write_validation_manifest.py')])
run([sys.executable,str(R/'validate_model.py')])
run([sys.executable,str(R/'check_aggregate_controls.py')])
