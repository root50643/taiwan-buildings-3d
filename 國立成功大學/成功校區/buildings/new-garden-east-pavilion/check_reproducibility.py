"""Rebuild in an isolated temporary folder; optionally re-render all six views.
The deliverable is read-only during replay. Original coordinates are never repaired.
"""

import sys
sys.dont_write_bytecode=True
def require(condition, message='Required check failed'):
    if not bool(condition): raise RuntimeError(message)
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
with tempfile.TemporaryDirectory(prefix='ncku-east-replay-') as td:
    D=Path(td)
    for n in ['build_model.py','parameters.json','render_preview.py','probe_scene.py']:
        shutil.copyfile(R/n,D/n)
    b=subprocess.run([sys.executable,str(D/'build_model.py')],capture_output=True,text=True)
    require((b.returncode==0), (b.stderr))
    checks={'isolated_stl_byte_identical':sha(D/'model.stl')==sha(R/'model.stl')}
    views=[]
    if args.render:
        p=subprocess.run(['blender','--python-exit-code','1','-b','-t','1','--python',str(D/'render_preview.py')],capture_output=True,text=True)
        require((p.returncode==0 and (D/'scene.blend').exists()), (p.stdout+p.stderr))
        probe=subprocess.run(['blender','--python-exit-code','1','-b',str(D/'scene.blend'),'--python',str(D/'probe_scene.py')],capture_output=True,text=True)
        require((probe.returncode==0 and (D/'scene-check.json').exists()), (probe.stdout+probe.stderr))
        scene=json.loads((D/'scene-check.json').read_text());checks['isolated_scene_same_original_triangles']=scene['passed']
        for path in sorted((R/'previews').glob('*.png')):
            same=(D/'previews'/path.name).exists() and sha(path)==sha(D/'previews'/path.name)
            views.append({'path':'previews/'+path.name,'identical':same,'sha256':sha(path)})
        checks['all_preview_bytes_identical']=len(views)==6 and all(q['identical'] for q in views)
    out={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'source_sha256':sha(R/'build_model.py'),'parameters_sha256':sha(R/'parameters.json'),'render_script_sha256':sha(R/'render_preview.py'),'render_replayed':args.render,'previews':views,
         'note':'Blend container bytes may include serialization differences; exact saved original geometry is verified separately.'}
out['evidence_sources']={n:__import__('hashlib').sha256((R/n).read_bytes()).hexdigest() for n in ['check_reproducibility.py', 'build_model.py', 'parameters.json', 'render_preview.py', 'probe_scene.py']}
(R/'reproducibility.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));require((out['passed']), ('Required check failed'))
