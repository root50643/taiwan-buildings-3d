"""Isolated mutation controls for stale aggregate evidence, including Python -O.
Never edits production files. Prints a report; nonzero if any bad copy passes.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
rows=[]
with tempfile.TemporaryDirectory(prefix='ncku-west-aggregate-control-') as td:
    D=Path(td)/'package';shutil.copytree(R,D,ignore=shutil.ignore_patterns('__pycache__'))
    def validate():
        p=subprocess.run([sys.executable,'-O',str(D/'validate_model.py')],capture_output=True,text=True)
        report=json.loads((D/'validation.json').read_text()) if (D/'validation.json').exists() else {}
        return p,report
    p,report=validate()
    if p.returncode!=0 or report.get('passed') is not True:
        raise RuntimeError('Control baseline must pass before any mutation: '+p.stdout+p.stderr)
    for name,relative in [('readme_changed','README.md'),('preview_changed','previews/front.png'),
                          ('checker_changed','check_raw_mesh.py'),('stl_changed','model.stl')]:
        target=D/relative;original=target.read_bytes();target.write_bytes(original+b'\nExpected stale-evidence mutation\n')
        p,report=validate()
        ok=p.returncode!=0 and report.get('passed') is False
        # PNG remains parseable, but its original bytes must no longer match.
        if name in ['readme_changed','preview_changed','checker_changed']:
            ok=ok and report.get('checks',{}).get('exact_current_distributable_inventory') is False
        if name=='stl_changed':
            ok=ok and report.get('checks',{}).get('all_reports_bound_to_current_stl') is False
        rows.append({'control':name,'rejected':ok,'returncode':p.returncode,'changed_file':relative,
                     'failed_checks':[k for k,v in report.get('checks',{}).items() if v is False]})
        target.write_bytes(original)
    # A fresh scanner must reject unexpected PNG metadata, even if an attacker
    # updates the content inventory and earlier report to the modified PNG bytes.
    from PIL import Image,PngImagePlugin
    target=D/'previews/front.png';original=target.read_bytes()
    im=Image.open(target);im.load();meta=PngImagePlugin.PngInfo();meta.add_text('unexpected_metadata','control')
    im.save(target,pnginfo=meta)
    subprocess.run([sys.executable,str(D/'write_validation_manifest.py')],check=True,capture_output=True)
    p,_=validate();fresh=json.loads((D/'artifact-integrity.json').read_text())
    rows.append({'control':'fresh_png_metadata_scan','rejected':p.returncode!=0 and fresh.get('passed') is False,
                 'returncode':p.returncode,'failed_checks':[k for k,v in fresh.get('checks',{}).items() if v is False]})
    target.write_bytes(original)
report={'passed':all(q['rejected'] for q in rows),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),
        'baseline_passed':True,'production_unchanged':True,'optimized_python':True,'controls':rows}
print(json.dumps(report,indent=2))
if not report['passed']:raise SystemExit(1)
