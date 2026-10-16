"""Isolated mutations prove named stale-evidence and fresh privacy gates fail closed."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[];evidence=[]
with tempfile.TemporaryDirectory(prefix='nccu-aggregate-control-') as td:
    D=Path(td)/'package';shutil.copytree(R,D)
    def validate():
        p=subprocess.run([sys.executable,'-B','-O',str(D/'validate_model.py'),'--integrity-only'],capture_output=True,text=True)
        report=json.loads((D/'validation.json').read_text()) if (D/'validation.json').exists() else {}
        return p,report
    def record(name,rel,process,report,reason,mutation):
        rejected=process.returncode!=0 and report.get('integrity_passed') is False and reason
        rows.append({'control':name,'rejected':bool(rejected),'returncode':process.returncode,'target':rel})
        evidence.append({'control':name,'mutation':mutation,'mutated_target_sha256':sha(D/rel),'report':report,
                         'stdout':process.stdout.replace(str(D),'.'),'stderr':process.stderr.replace(str(D),'.')})
    p,rep=validate()
    if p.returncode or rep.get('integrity_passed') is not True:raise RuntimeError('Integrity-control baseline failed: '+p.stdout+p.stderr)
    for name,rel in [('readme_changed','README.md'),('preview_changed','previews/front.png'),('checker_changed','verification/check_raw_mesh.py'),('stl_changed','model.stl'),('report_changed','qa/raw/raw-mesh-check.json')]:
        target=D/rel;old=target.read_bytes();target.write_bytes(old+b'\nExpected stale evidence mutation\n');p,rep=validate()
        # Corrupt JSON deliberately fails parsing; other cases require the named inventory gate.
        reason=rep.get('checks',{}).get('exact_current_distributable_inventory') is False if name!='report_changed' else rep.get('error_type')=='JSONDecodeError'
        record(name,rel,p,rep,reason,{'append':'Expected stale evidence mutation','original_sha256':hashlib.sha256(old).hexdigest()});target.write_bytes(old)
    for rel in ['qa/nested/validation.json','qa/nested/freeze-manifest.json']:
        target=D/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('{}');p,rep=validate()
        record('nested_excluded_name:'+rel,rel,p,rep,rep.get('checks',{}).get('exact_current_distributable_inventory') is False,{'create':'empty JSON object'});target.unlink()
    rel='qa/compressed-private-control.json.gz';target=D/rel;target.write_bytes(gzip.compress(('/'+'Users'+'/private-control/file').encode(),mtime=0))
    subprocess.run([sys.executable,'-B',str(D/'write_validation_manifest.py')],check=True,capture_output=True)
    p,rep=validate();reason=rep.get('artifact_scan',{}).get('checks',{}).get('no_private_paths_or_credentials') is False and rel in rep.get('artifact_scan',{}).get('flagged_paths',[])
    record('compressed_private_path',rel,p,rep,reason,{'create':'gzip of a constructed synthetic user-home path; source contains exact construction'});target.unlink()
    from PIL import Image,PngImagePlugin
    rel='previews/front.png';target=D/rel;old=target.read_bytes();im=Image.open(target);im.load();meta=PngImagePlugin.PngInfo();meta.add_text('unexpected_metadata','control');im.save(target,pnginfo=meta)
    subprocess.run([sys.executable,'-B',str(D/'write_validation_manifest.py')],check=True,capture_output=True)
    p,rep=validate();reason=rep.get('artifact_scan',{}).get('checks',{}).get('all_png_decoded_crc_clean') is False
    record('fresh_png_metadata',rel,p,rep,reason,{'add_png_text':{'unexpected_metadata':'control'}});target.write_bytes(old)
(R/'aggregate-control-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
out={'passed':all(q['rejected'] for q in rows),'stl_sha256':sha(R/'model.stl'),'evidence_sha256':sha(R/'aggregate-control-evidence.json'),'checker_sources_sha256':{n:sha(R/n) for n in ['check_aggregate_controls.py','validate_model.py','check_artifacts.py','write_validation_manifest.py']},'integrity_baseline_passed':True,'optimized_python':True,'production_unchanged':True,'controls':rows,'limits':'Integrity-only mode does not convert a strict geometry failure into approval.'}
(R/'aggregate-controls.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(0 if out['passed'] else 1)
