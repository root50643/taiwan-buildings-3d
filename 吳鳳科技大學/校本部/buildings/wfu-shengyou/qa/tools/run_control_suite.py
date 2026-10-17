"""Fresh synthetic-only controls for geometry, aggregation, descriptors and archive IO."""
from pathlib import Path
import argparse,json,subprocess,sys
from run_full_qa import QA,VER,source_inventory
from qa_common import require,sha256,write_json
from check_controls import fixture_cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();require(not a.out.exists(),'Control output must be new');a.out.mkdir(parents=True);source=source_inventory();rows=[]
    fixture=a.out/'positive_box.stl';fixture.write_bytes(next(data for name,data,_ in fixture_cases() if name=='normal_box'))
    commands=[('positive-full',[sys.executable,'-B',str(QA/'tools/run_full_qa.py'),'--stl',str(fixture),'--expected-sha256',sha256(fixture),'--expected-longest-mm','30','--out',str(a.out/'positive-full')])]
    for mode,flags in [('normal',['-B']),('optimized',['-B','-O'])]:
        commands.extend([(mode+'-fail-closed',[sys.executable,*flags,str(QA/'tools/test_fail_closed.py'),'--baseline',str(a.out/'positive-full'),'--stl',str(fixture),'--out',str(a.out/(mode+'-fail-closed'))]),(mode+'-dense-descriptors',[sys.executable,*flags,str(QA/'tools/test_dense_evidence.py'),'--baseline',str(a.out/'positive-full/normal/standard/dense'),'--stl',str(fixture),'--out',str(a.out/(mode+'-dense-descriptors'))]),(mode+'-archive',[sys.executable,*flags,str(QA/'tools/test_archive_verify.py'),'--out',str(a.out/(mode+'-archive'))])])
    for name,command in commands:
        r=subprocess.run(command,capture_output=True,text=True);(a.out/(name+'.stdout.txt')).write_text(r.stdout);(a.out/(name+'.stderr.txt')).write_text(r.stderr);rows.append({'name':name,'returncode':r.returncode});print(json.dumps(rows[-1]),flush=True)
    okay=all(r['returncode']==0 for r in rows) and source_inventory()==source
    report={'passed':okay,'strict_passed':okay,'tool_sources_sha256':source,'executions':rows,'all_sources_unchanged':source_inventory()==source,'scope':'Fresh model-independent synthetic controls only; no project model was inspected.'};write_json(a.out/'controls-suite-summary.json',report);return 0 if okay else 1
if __name__=='__main__':raise SystemExit(main())
