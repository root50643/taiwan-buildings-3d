"""Regenerate generic QA G-code in a chosen output directory; never a machine profile."""
from pathlib import Path
import argparse,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--slicer',required=True);p.add_argument('--output-dir',required=True);args=p.parse_args()
out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
profile=ROOT/'qa/slicer/qa-generic-0.4mm-0.2mm-support-auto.ini'
model=ROOT/'models/v1/model.stl';exe=Path(args.slicer).resolve()
cmd=[str(exe),'--datadir',str(out/'isolated-runtime-data'),'--load',str(profile),'--threads','2','--export-gcode','--output',str(out/'candidate-support-auto.gcode'),str(model)]
r=subprocess.run(cmd,capture_output=True)
(out/'stdout.log').write_bytes(r.stdout);(out/'stderr.log').write_bytes(r.stderr)
(out/'invocation.json').write_text(json.dumps({'returncode':r.returncode,'command':cmd,'slicer_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'profile_sha256':hashlib.sha256(profile.read_bytes()).hexdigest(),'purpose':'Generic QA only, not machine-ready; no physical print.'},indent=2)+'\n')
print('Slicer exit',r.returncode);raise SystemExit(r.returncode)
