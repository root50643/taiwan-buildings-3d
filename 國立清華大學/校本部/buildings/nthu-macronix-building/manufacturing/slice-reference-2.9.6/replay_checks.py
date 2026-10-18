"""Replay preserved audit scripts from a self-contained backup; no slicing.

Example, run from the extracted backup root:
python candidate-repo/<package>/manufacturing/slice-reference-2.9.6/replay_checks.py --archive-root . --output-name replay-new
Requires the package requirements plus matplotlib. Input G-code is fixed by SHA.
"""
from pathlib import Path
import argparse,shutil,subprocess,sys,hashlib
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--archive-root',type=Path,required=True);p.add_argument('--output-name',default='replay-new');a=p.parse_args()
root=a.archive_root.resolve();out=root/a.output_name
if out.parent!=root or out.exists():raise ValueError('Choose a new immediate child directory; no existing evidence is overwritten.')
gcode=root/'slicing-work/reference-NOT-MACHINE-READY.gcode'
assert hashlib.sha256(gcode.read_bytes()).hexdigest()=='7f614cbe4a31e59cfed5e843f90b797f1032984c173da044284fc36ab18219de'
package=HERE.parents[1]
assert hashlib.sha256((package/'manufacturing/fill-hidden-gaps/model.stl').read_bytes()).hexdigest()=='6801f9c41c9fd986df4167523ec36195e715d6a38a680c09aff002cba1351b2a'
out.mkdir()
scripts=['audit_supports.py','support_routes.py','check_model_paths.py','check_layer_links.py','check_cap_support.py']
for n in scripts:shutil.copyfile(HERE/'qa'/n,out/n)
for n in scripts:
 args=[sys.executable,str(out/n)]
 if n=='check_model_paths.py':args+=['--stl',str(package/'manufacturing/fill-hidden-gaps/model.stl')]
 subprocess.run(args,cwd=root,check=True)
print('Replayed original audit algorithms into',out,'; no slicer invocation or geometry change.')
