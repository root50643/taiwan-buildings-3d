"""Rebuild into a fresh temporary directory and compare fixed STL byte identities."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    v=json.loads((ROOT/'parameters.json').read_text(encoding='utf8'))['version']
    fixed=ROOT/'models'/v;qa=ROOT/'qa'/v;qa.mkdir(parents=True,exist_ok=True);out=qa/'rebuild-check.json'
    with tempfile.TemporaryDirectory(prefix='.rebuild-',dir=qa) as work:
        # Validate the exact cleanup target before TemporaryDirectory removes it.
        assert Path(work).resolve().parent==qa.resolve()
        p=subprocess.run([sys.executable,'-B',str(ROOT/'source/build_model.py'),'--output-dir',work],capture_output=True)
        report={'command':'python -B source/build_model.py --output-dir <fresh-temporary-directory>',
            'exit_code':p.returncode,'generator_sha256':sha(ROOT/'source/build_model.py'),
            'parameter_sha256':sha(ROOT/'parameters.json'),'files':[]}
        for rel in ['parts/body.stl','parts/roof.stl','assembly.stl']:
            test=Path(work)/rel
            row={'file':rel,'fixed_sha256':sha(fixed/rel),'rebuilt_sha256':sha(test) if test.exists() else None}
            row['bytes_equal']=test.exists() and (fixed/rel).read_bytes()==test.read_bytes()
            report['files'].append(row)
        report['passed']=p.returncode==0 and all(f['bytes_equal'] for f in report['files'])
        if p.returncode:
            report['stderr']=p.stderr.decode('utf8',errors='replace').replace(work,'<fresh-temporary-directory>').replace(str(ROOT),'<model-root>')
        out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
        print(json.dumps(report,indent=2))
        raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__':main()
