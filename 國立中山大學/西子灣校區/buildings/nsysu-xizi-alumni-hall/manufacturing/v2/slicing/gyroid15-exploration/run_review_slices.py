"""Run actual six-part CLI slices into this private review staging directory."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
TASK = ROOT.parent
EXE = TASK/'manufacturing-tools/PrusaSlicer-2.9.6/PrusaSlicer-2.9.6/prusa-slicer-console.exe'
MODELS = TASK/'candidate/國立中山大學/西子灣校區/buildings/nsysu-xizi-alumni-hall/manufacturing/v2/models'
PROFILE = ROOT/'geometry-review-0.4mm-0.15mm-no-support.ini'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(args, logfile):
    started = time.time()
    p = subprocess.run([str(v) for v in args], cwd=ROOT, capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW, timeout=900)
    stdout = p.stdout.decode('utf-8',errors='replace')
    stderr = p.stderr.decode('utf-8',errors='replace')
    logfile.write_text('STDOUT\n'+stdout+'\nSTDERR\n'+stderr,encoding='utf-8')
    return {'argv':[str(v) for v in args], 'returncode':p.returncode,
        'seconds':time.time()-started, 'stdout_log':str(logfile.relative_to(ROOT)),
        'diagnostic_lines':[line for line in (stdout+'\n'+stderr).splitlines()
                           if re.search(r'warn|error|repair|support|overhang|floating|loose|outside|empty',line,re.I)]}


def main():
    source = MODELS/'build-report.json'
    report = json.loads(source.read_text(encoding='utf-8-sig'))
    assert report['physical_part_count'] == 6
    (ROOT/'inputs-build-report.json').write_bytes(source.read_bytes())
    prepared = ROOT/'geometry-review-0.4mm-0.2mm-no-support.ini'
    prep_cmd = [EXE,'--datadir',ROOT/'profile-data','--load',prepared,
        '--layer-height','0.15','--first-layer-height','0.15','--save',PROFILE]
    prep = run(prep_cmd,ROOT/'profile-save-0.15mm.log')
    assert prep['returncode'] == 0 and PROFILE.exists(),prep
    (ROOT/'profile-generation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    def part(p):
        inputfile = MODELS/p['stl']
        actual = sha(inputfile)
        if actual != p['stl_sha256']:
            raise RuntimeError('Input SHA changed: '+p['id'])
        folder = ROOT/p['id']
        folder.mkdir(exist_ok=True)
        info_cmd = [EXE,'--datadir',folder/'cli-data','--info',inputfile]
        info = run(info_cmd,folder/'info.stdout.log')
        outputfile = folder/'geometry-review-NOT-MACHINE-READY.gcode'
        slice_cmd = [EXE,'--datadir',folder/'cli-data','--load',PROFILE,
            '--threads','2','--center','110,110','--export-gcode',
            '--output',outputfile,inputfile]
        sliced = run(slice_cmd,folder/'slice.stdout.log')
        result = {'id':p['id'],'input_stl':str(inputfile),'input_stl_sha256':actual,
            'expected_stl_sha256':p['stl_sha256'],'input_bytes':inputfile.stat().st_size,
            'profile':str(PROFILE),'profile_sha256':sha(PROFILE),
            'info':info,'slice':sliced,'input_sha256_after':sha(inputfile),
            'gcode':str(outputfile),'gcode_exists':outputfile.exists()}
        if sliced['returncode']==0 and outputfile.exists():
            audit_cmd=[sys.executable,'-B',ROOT/'audit_gcode.py',outputfile,'--stl',inputfile,'--output',folder]
            result['audit']=run(audit_cmd,folder/'audit.stdout.log')
        (folder/'commands-and-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'id':p['id'],'info_exit':info['returncode'],
            'slice_exit':sliced['returncode'],'audit_exit':result.get('audit',{}).get('returncode'),
            'diagnostics':sliced['diagnostic_lines']},ensure_ascii=False),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(part,report['parts']))
    summary={'python':platform.python_version(),'tool_exe':str(EXE),'tool_exe_sha256':sha(EXE),
        'profile':str(PROFILE),'profile_sha256':sha(PROFILE),
        'source_build_report_sha256':sha(source),
        'parts':results,'claims':'Actual CLI slicing only; not a physical print, printer calibration or ready-to-print G-code.',
        'all_slices_and_audits_exit_zero':all(p['info']['returncode']==0 and p['slice']['returncode']==0
            and p.get('audit',{}).get('returncode')==0 and p['input_stl_sha256']==p['input_sha256_after'] for p in results)}
    (ROOT/'slicer-run-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    if not summary['all_slices_and_audits_exit_zero']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
