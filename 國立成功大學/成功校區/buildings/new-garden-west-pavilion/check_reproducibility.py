"""Rebuild in an isolated temporary folder; optionally re-render all six views.
The deliverable is read-only during replay. Original coordinates are never repaired.
"""

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
with tempfile.TemporaryDirectory(prefix='ncku-west-replay-') as td:
    D=Path(td)
    for n in ['build_model.py','parameters.json','render_preview.py','probe_scene.py']:
        shutil.copyfile(R/n,D/n)
    copied_hashes={n:sha(D/n) for n in ['build_model.py','parameters.json','render_preview.py','probe_scene.py']}
    b=subprocess.run([sys.executable,str(D/'build_model.py')],capture_output=True,text=True)
    require(b.returncode==0, b.stderr)
    checks={'isolated_stl_byte_identical':sha(D/'model.stl')==sha(R/'model.stl')}
    views=[]
    if args.render:
        p=subprocess.run(['blender','-b','-t','1','--python-exit-code','1','--python',str(D/'render_preview.py')],capture_output=True,text=True)
        require(p.returncode==0 and (D/'scene.blend').exists(), p.stdout+p.stderr)
        probe=subprocess.run(['blender','-b',str(D/'scene.blend'),'--python-exit-code','1','--python',str(D/'probe_scene.py')],capture_output=True,text=True)
        require(probe.returncode==0 and (D/'scene-check.json').exists(), probe.stdout+probe.stderr)
        scene=json.loads((D/'scene-check.json').read_text());checks['isolated_scene_same_original_triangles']=scene['passed']
        for path in sorted((R/'previews').glob('*.png')):
            same=(D/'previews'/path.name).exists() and sha(path)==sha(D/'previews'/path.name)
            views.append({'path':'previews/'+path.name,'identical':same,'sha256':sha(path)})
        checks['all_preview_bytes_identical']=len(views)==6 and all(q['identical'] for q in views)
    checks['all_copied_source_hashes_still_current']=all(sha(R/n)==h for n,h in copied_hashes.items())
    out={'passed':all(checks.values()),'checks':checks,'stl_sha256':sha(R/'model.stl'),'source_sha256':copied_hashes['build_model.py'],'parameters_sha256':copied_hashes['parameters.json'],'render_script_sha256':copied_hashes['render_preview.py'],'copied_source_hashes':copied_hashes,'render_replayed':args.render,'previews':views,
         'note':'Blend container bytes may include serialization differences; exact saved original geometry is verified separately.'}
(R/'reproducibility.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));require(out['passed'], 'Required condition failed')
