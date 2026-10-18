"""Run independent original-STL gates. Failed evidence never overwritten."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,subprocess,sys
from qa_common import sha256,checker_inventory,write_json


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stl',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--expected-longest-mm',type=float,required=True);a=p.parse_args()
    if a.out.exists():raise RuntimeError('Output must be a fresh directory')
    a.out.mkdir(parents=True);tools=Path(__file__).resolve().parent;before=sha256(a.stl);inventory=checker_inventory()
    stages=[('raw','check_raw_mesh.py',['--out',str(a.out/'raw'),'--expected-longest-mm',str(a.expected_longest_mm)],a.out/'raw/raw-mesh-check.json'),
            ('sections','check_sections.py',['--out',str(a.out/'sections')],a.out/'sections/section-check.json'),
            ('exact-contacts','check_original_intersections.py',['--out',str(a.out/'exact-contacts.json'),'--expected-sha256',before,'--progress'],a.out/'exact-contacts.json'),
            ('manufacturing','check_manufacturing.py',['--out',str(a.out/'manufacturing')],a.out/'manufacturing/manufacturing-check.json')]
    def stage(job):
        name,script,extra,reportfile=job
        command=[sys.executable,'-B',str(tools/script),'--stl',str(a.stl),*extra]
        result=subprocess.run(command,capture_output=True,text=True)
        def public(value):
            for private,replacement in sorted([(str(a.out),'[qa-output]'),(str(a.stl),a.stl.name),
                    (str(tools),'[qa-tools]'),(sys.executable,'[python]')],key=lambda x:-len(x[0])):
                value=value.replace(private,replacement)
            return value
        (a.out/(name+'.stdout.txt')).write_text(public(result.stdout),encoding='utf-8')
        (a.out/(name+'.stderr.txt')).write_text(public(result.stderr),encoding='utf-8')
        report=json.loads(reportfile.read_text()) if reportfile.exists() else {}
        row={'stage':name,'exit_code':result.returncode,'report':str(reportfile.relative_to(a.out)),
                     'report_sha256':sha256(reportfile) if reportfile.exists() else None,
                     'passed':result.returncode==0 and report.get('passed') is True,
                     'checks':report.get('checks'),'error':report.get('error')}
        print(json.dumps(row),flush=True);return row
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(stage,stages))
    checks={'all_stages_pass':all(r['passed'] for r in rows),'stl_unchanged':sha256(a.stl)==before,
            'checker_sources_unchanged':checker_inventory()==inventory}
    report={'passed':all(checks.values()),'completed':len(rows)==len(stages),'stl_sha256':before,
            'expected_longest_mm':a.expected_longest_mm,'checks':checks,'stages':rows,
            'checker_sources_sha256':inventory,
            'scope':'Original raw STL exact topology and exact triangle contacts; finite XY morphology and numerical normal/support screens. No repairs/waivers, global thickness claim or physical trial.'}
    write_json(a.out/'part-qa-summary.json',report);return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
