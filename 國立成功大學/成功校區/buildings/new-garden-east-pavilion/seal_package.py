"""Explicit authoring operation; inventory a verified copy. Never run on RC1."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import json,subprocess,argparse
ap=argparse.ArgumentParser();ap.add_argument('--author-bootstrap',action='store_true');args=ap.parse_args()
from integrity_utils import sha,write_json,files,source_inventory,require
R=Path(__file__).resolve().parent
# The numerical checks must already have been run. This does not run or repair geometry.
write_json(R/'source-bindings.json',{'files':source_inventory(R)})
scan=subprocess.run([sys.executable,str(R/'check_artifacts.py')],capture_output=True,text=True)
require(scan.returncode==0,'Current payload privacy scan failed: '+scan.stdout+scan.stderr)
preflight=subprocess.run([sys.executable,str(R/'validate_model.py'),'--preflight'],capture_output=True,text=True)
require(preflight.returncode==0,'Current evidence preflight failed: '+preflight.stdout+preflight.stderr)
listed=files(R,{'freeze-manifest.json','SHA256SUMS'})
manifest={'model_id':'ncku-cheng-kung-da-hsin-yuan-east-student-salon','qa_revision':'1.0.0-rc2','geometry_stl_sha256_unchanged_from_rc1':True,'stl_sha256':sha(R/'model.stl'),
          'payload_files':[{'path':n,**q} for n,q in listed.items()],'file_count':len(listed),
          'scope':'Whole east pavilion exterior approximation; strict original-normal diagnostic remains false with individually bounded root evidence.'}
write_json(R/'freeze-manifest.json',manifest)
allfiles=files(R,{'SHA256SUMS'});(R/'SHA256SUMS').write_text(''.join(q['sha256']+'  '+n+'\n' for n,q in allfiles.items()))
mode=['--preflight','--check-inventory'] if args.author_bootstrap else []
result=subprocess.run([sys.executable,str(R/'validate_model.py')]+mode,capture_output=True,text=True)
print(result.stdout);require(result.returncode==0,'Sealed package check failed: '+result.stderr)
print('Manifest SHA256: '+sha(R/'freeze-manifest.json'))
