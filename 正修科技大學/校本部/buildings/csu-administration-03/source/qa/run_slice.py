"""Actual generic CLI slicing; does not execute printer motion."""
from pathlib import Path
import argparse,json,re,subprocess,sys,time
from qa_common import sha256,write_json

EXPECTED_SLICER='7fd50b52d1cc3da87dbcb71e45e764412dd45688bea028f351333e86d9769704'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--slicer',type=Path,required=True)
    p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--profile',type=Path,default=Path(__file__).with_name('geometry-review-0.4mm-0.2mm-solid100-no-support.ini'))
    a=p.parse_args()
    if a.out.exists():raise RuntimeError('Fresh slicing output required')
    if sha256(a.slicer)!=EXPECTED_SLICER:raise RuntimeError('PrusaSlicer binary hash differs')
    a.out.mkdir(parents=True);digest=sha256(a.stl);rows=[]
    def run(name,command):
        t=time.time();r=subprocess.run([str(x) for x in command],capture_output=True)
        stdout=r.stdout.decode('utf-8',errors='replace');stderr=r.stderr.decode('utf-8',errors='replace')
        def public(value):
            replacements=[(str(a.slicer.parent),'[slicer-dir]'),(str(a.stl),a.stl.name),(str(a.out),'[slice-output]'),
                          (str(a.profile),a.profile.name),(str(Path(__file__).parent),'[qa-tools]'),(sys.executable,'[python]')]
            for private,label in sorted(replacements,key=lambda x:-len(x[0])):value=value.replace(private,label)
            return value
        text=public('STDOUT\n'+stdout+'\nSTDERR\n'+stderr)
        (a.out/(name+'.log')).write_text(text,encoding='utf-8')
        row={'stage':name,'exit_code':r.returncode,'seconds':time.time()-t,'log':name+'.log',
             'diagnostic_lines':[line for line in text.splitlines() if re.search(r'warn|error|repair|support|overhang|floating|loose|outside|empty',line,re.I)]}
        rows.append(row);print(json.dumps(row),flush=True);return r.returncode
    info=run('info',[a.slicer,'--datadir',a.out/'cli-data','--info',a.stl])
    gcode=a.out/'QA-NOT-MACHINE-READY.gcode'
    sliced=run('slice',[a.slicer,'--datadir',a.out/'cli-data','--load',a.profile,
              '--threads','2','--center','110,110','--export-gcode','--output',gcode,a.stl])
    audit=None
    if sliced==0 and gcode.exists():
        audit=run('audit',[sys.executable,'-B',Path(__file__).with_name('audit_gcode.py'),gcode,'--stl',a.stl,'--output',a.out])
    r={'completed':audit is not None,'passed':info==sliced==audit==0 and sha256(a.stl)==digest,
       'input_stl':a.stl.name,'input_sha256':digest,'input_sha256_after':sha256(a.stl),
       'tool':'PrusaSlicer 2.9.6 portable console','tool_sha256':EXPECTED_SLICER,
       'profile':a.profile.name,'profile_sha256':sha256(a.profile),'commands':rows,
       'gcode':gcode.name,'gcode_sha256':sha256(gcode) if gcode.exists() else None,
       'limits':'Actual generic 0.4mm nozzle / 0.2mm layer / 100% rectilinear / no-support slicing only. Not machine-calibrated Gcode and no physical print, adhesion, tolerance or assembly trial.'}
    r['artifact_inventory']={x.name:{'bytes':x.stat().st_size,'sha256':sha256(x)} for x in sorted(a.out.iterdir()) if x.is_file()}
    write_json(a.out/'slice-summary.json',r);return 0 if r['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
