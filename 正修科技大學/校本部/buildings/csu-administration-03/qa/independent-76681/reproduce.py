"""Run imported independent algorithms into a new output directory.

Only path bindings change in a temporary copy. Historical identity/finalize
scripts are never executed. Original archived conclusions are never replaced.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys

HERE=Path(__file__).resolve().parent
FIXED='76681c5dcedc88d684946780e795d7914a88c075'
EXPECTED={'body':'e388dff1247334ec5e79530e45a1b7e5e85d1a630aff0a9d6d53720f1362ee6c',
          'roof':'7d1c8840ee11649ec4c57984ff1a0cc2c2a3916f37fc21888e7ead0f631fed04'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['controls','geometry','manufacturing','scene','rebuild'],required=True)
    p.add_argument('--package-root',type=Path,default=HERE.parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();pkg=a.package_root.resolve();out=a.output.resolve()
    if out.exists():raise RuntimeError('Output must be a new directory; archived reports cannot be overwritten')
    if out==HERE or HERE in out.parents or pkg==out or pkg in out.parents:
        raise RuntimeError('Use a separate review output directory outside the model package')
    actual={name:sha(pkg/f'models/v2/parts/{name}.stl') for name in EXPECTED}
    if actual!=EXPECTED:raise RuntimeError('Actual print parts do not match fixed reviewed SHA-256')
    out.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    result={'mode':a.mode,'fixed_review_commit':FIXED,'actual_STL_SHA256':actual,
            'historical_reports_modified':False,'full_historical_identity_or_finalizer_rerun':False}
    if a.mode=='controls':
        contact=module('imported_contact',HERE/'verification-helpers/independent_contact_check.py')
        topology=module('imported_topology',HERE/'verification-helpers/independent_raw_topology.py')
        controls=contact.controls();raw={n:topology.audit(pkg/f'models/v2/parts/{n}.stl') for n in EXPECTED}
        for name,row in raw.items():row['input']=f'models/v2/parts/{name}.stl'
        result.update(controls=controls,control_evaluations=sum(x['evaluations'] for x in controls),raw_topology=raw,
            passed=all(x['all_permutations_and_pair_swaps_match'] for x in controls) and all(x['all_listed_checks_passed'] for x in raw.values()))
    elif a.mode=='rebuild':
        repo=pkg.parents[3];prefix=pkg.relative_to(repo).as_posix();stage=out/'fixed-build-package';(stage/'source').mkdir(parents=True)
        source_hashes={}
        for name in ['source/build_model.py','parameters.json']:
            raw=subprocess.check_output(['git','-C',str(repo),'show',f'{FIXED}:{prefix}/{name}'],env=dict(env,GIT_OPTIONAL_LOCKS='0'))
            (stage/name).write_bytes(raw);source_hashes[name]=hashlib.sha256(raw).hexdigest()
        run=subprocess.run([sys.executable,'-B',str(stage/'source/build_model.py'),'--output-dir',str(out/'rebuilt')],env=env,capture_output=True)
        (out/'stdout.txt').write_bytes(run.stdout);(out/'stderr.txt').write_bytes(run.stderr)
        same={name:sha(out/'rebuilt'/name)==sha(pkg/'models/v2'/name) for name in ['parts/body.stl','parts/roof.stl','assembly.stl']} if run.returncode==0 else {}
        result.update(returncode=run.returncode,fixed_git_source_sha256=source_hashes,byte_identity=same,
                      passed=run.returncode==0 and len(same)==3 and all(same.values()))
    else:
        source={'geometry':HERE/'agent-geometry/independent_csu_geometry.py',
                'manufacturing':HERE/'agent-manufacturing/independent_csu_manufacturing.py',
                'scene':HERE/'independent_scene_check.py'}[a.mode]
        text=source.read_text(encoding='utf-8')
        bindings={'geometry':[("OLD=HERE.parents[1]/'agent-geometry'","OLD=Path(os.environ['CSU_REVIEW_HELPERS'])"),
                              ("P=Path(r'<MODEL_ROOT>')","P=Path(os.environ['CSU_REVIEW_PACKAGE_ROOT'])")],
                  'manufacturing':[("PKG=Path(r'<MODEL_ROOT>')","PKG=Path(os.environ['CSU_REVIEW_PACKAGE_ROOT'])")],
                  'scene':[("P=Path('<MODEL_ROOT>')","P=Path(os.environ['CSU_REVIEW_PACKAGE_ROOT'])")]}[a.mode]
        for old,new in bindings:
            if text.count(old)!=1:raise RuntimeError('Unexpected imported binding line; refusing broad rewriting')
            text=text.replace(old,new)
        text='import os\n'+text
        compile(text,source.name,'exec')
        script=out/source.name;script.write_text(text,encoding='utf-8')
        env.update(CSU_REVIEW_PACKAGE_ROOT=str(pkg),CSU_REVIEW_HELPERS=str(HERE/'verification-helpers'))
        run=subprocess.run([sys.executable,'-B',str(script)],env=env,capture_output=True)
        (out/'stdout.txt').write_bytes(run.stdout);(out/'stderr.txt').write_bytes(run.stderr)
        result.update(imported_script_sha256=sha(source),temporary_path_bound_script_sha256=sha(script),
                      returncode=run.returncode,passed=run.returncode==0,
                      path_bindings_only=True,limitation='A fresh rerun is not the historical reviewer execution and does not replace its source hashes or conclusions.')
    result['actual_STL_SHA256_after']={name:sha(pkg/f'models/v2/parts/{name}.stl') for name in EXPECTED}
    result['inputs_unchanged']=result['actual_STL_SHA256_after']==actual
    result['passed']=result['passed'] and result['inputs_unchanged']
    (out/'rerun-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mode':a.mode,'passed':result['passed'],'inputs_unchanged':result['inputs_unchanged']}))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
