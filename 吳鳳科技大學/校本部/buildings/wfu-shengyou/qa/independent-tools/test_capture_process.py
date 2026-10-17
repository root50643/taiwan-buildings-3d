"""Small adapter-only controls. Producer runs are explicitly injected test outcomes.
No WFU mesh, STL geometry checks or model result is used or implied.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import argparse, contextlib, hashlib, io, json, os, shutil, sys
import capture_process as m

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    a = parser.parse_args()
    a.out = a.out.resolve()
    require(not a.out.exists() and len(os.sched_getaffinity(0)) == 1, 'Fresh one-CPU test output required')
    a.out.mkdir(parents=True)
    baseline = a.baseline.resolve()
    manifest = baseline/'PREFLIGHT-REUSE.json'
    h = m.sha(manifest)
    case_rows = []
    initial_sources = m.inventory(baseline/'tooling')
    def fixture(name):
        root = a.out/name
        stl = root/'models/v1/model.stl'
        stl.parent.mkdir(parents=True)
        stl.write_bytes(b'Explicitly synthetic capture test input; this is not a geometry fixture.\n')
        out, capture, full = root/'producer', root/'capture', root/'full'
        contract = dict(qa_root=baseline/'tooling', revision='v1', expected_stl_sha256=m.sha(stl), expected_longest_mm=220., tooling_manifest=manifest, expected_tooling_manifest_sha256=h, stl=stl)
        return root, out, capture, full, contract
    def contract_case(name, mutation=None, needle=None):
        root, out, capture, full, contract = fixture(name)
        if mutation:
            mutation(contract)
        error = None
        try:
            observed = m.validate_contract(SimpleNamespace(**contract))
            require(observed == initial_sources, 'Positive source map differs')
        except Exception as e:
            error = str(e)
        accepted = error is None
        passed = accepted if needle is None else not accepted and needle in error
        row = dict(case=name, kind='input-contract', expected_accept=needle is None, accepted=accepted, error=error, passed=passed)
        case_rows.append(row)
        write(root/'result.json', row)
        require(passed, name)
    contract_case('exact_original_28_source_contract')
    with mock.patch.object(m.sys,'executable','/explicitly-not-the-selected-python'):
        contract_case('wrong_capture_interpreter',needle='Use selected modeling-toolchain Python')
    contract_case('wrong_stl_hash', lambda c:c.update(expected_stl_sha256='0'*64), 'STL hash differs')
    for label,value in [('short','f'*63),('nonhex','g'*64),('upper','F'*64)]:
        contract_case('malformed_hash_'+label, lambda c,v=value:c.update(expected_stl_sha256=v), 'Expected STL SHA256 required')
    for label,value in [('zero',0),('negative',-1),('nan',float('nan')),('infinity',float('inf')),('boolean',True)]:
        contract_case('extent_'+label, lambda c,v=value:c.update(expected_longest_mm=v), 'Finite positive expected extent required')
    for label,value in [('path','../v1'),('empty',''),('text','final')]:
        contract_case('revision_'+label, lambda c,v=value:c.update(revision=v), 'Canonical vN revision required')
    contract_case('revision_identity', lambda c:c.update(revision='v2'), 'exact models/vN/model.stl')
    contract_case('manifest_hash', lambda c:c.update(expected_tooling_manifest_sha256='0'*64), 'Tooling manifest hash differs')
    def changed_manifest(c, name, edit):
        d=json.loads(c['tooling_manifest'].read_bytes());edit(d);p=c['stl'].parents[2]/(name+'.json');write(p,d);c.update(tooling_manifest=p,expected_tooling_manifest_sha256=m.sha(p))
    contract_case('manifest_not_passed',lambda c:changed_manifest(c,'manifest',lambda d:d.update(passed=False)), 'Completed original tool reuse preflight required')
    contract_case('manifest_source_mutation',lambda c:changed_manifest(c,'manifest',lambda d:d['sources']['tools/run_full_qa.py'].update(sha256='0'*64)), 'Exact tested 28-tool roster differs')
    contract_case('manifest_missing_tool',lambda c:changed_manifest(c,'manifest',lambda d:d['sources'].pop('tools/run_full_qa.py')), 'Exact tested 28-tool roster differs')
    def capture_case(name, kind='full', mode='normal', producer_exit=1, edit_pre=None, edit_runtime=None, missing_report=False, late=None, expected_return=None, expected_error=None):
        root,out,capture,full,c = fixture(name)
        args=['--kind',kind,'--mode',mode,'--stl',str(c['stl']),'--out',str(out),'--capture',str(capture),'--qa-root',str(c['qa_root']),'--revision',c['revision'],'--expected-stl-sha256',c['expected_stl_sha256'],'--expected-longest-mm','220','--tooling-manifest',str(manifest),'--expected-tooling-manifest-sha256',h]
        if kind=='exact':
            args += ['--full',str(full)]
            std=full/mode/'standard'
            raw={'passed':True,'strict_passed':True,'stl_sha256':c['expected_stl_sha256']}
            dense={'strict_passed':False,'under_0p8mm_count':0,'flagged_sample_count':1}
            write(std/'raw/raw-mesh-check.json',raw);write(full/mode/'intersections.json',raw);write(std/'dense/dense-check.json',dense)
        if edit_pre:
            edit_pre(root,out,capture,full,args,c)
        def injected(command, stdout, stderr, env):
            require(env['PYTHONDONTWRITEBYTECODE']=='1' and all(env[k]=='1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')) and 'PYTHONOPTIMIZE' not in env,'Child environment differs')
            i=command.index(str(capture/'runtime_launcher.py'));runtime,target=Path(command[i+1]),Path(command[i+2]);target_args=command[i+3:]
            expected_prefix=[str(m.PYTHON),'-B',*(['-O'] if mode=='optimized' else [])]
            require(command[:i]==expected_prefix,'Selected interpreter/optimization argument differs')
            expected_target=c['qa_root']/'tools'/('run_full_qa.py' if kind=='full' else 'diagnose_recorded_cpp_rays.py')
            expected_args=['--stl',str(c['stl']),'--expected-sha256',c['expected_stl_sha256']]
            if kind=='full':expected_args+=['--expected-longest-mm','220.0','--out',str(out)]
            else:
                std=full/mode/'standard'
                expected_args+=['--flags',str(std/'dense/dense-flagged-samples.json.gz'),'--dense-report',str(std/'dense/dense-check.json'),'--raw-report',str(std/'raw/raw-mesh-check.json'),'--intersections-report',str(full/mode/'intersections.json'),'--out',str(out)]
            require(target==expected_target and target_args==expected_args,'Exact independent producer target/argument contract differs')
            require(runtime==capture/'runtime.json' and (capture/'runtime_launcher.py').read_text()==m.BOOT,'Runtime launcher contract differs')
            rr={'optimization_level':1 if '-O' in command else 0,'cpu_affinity':sorted(os.sched_getaffinity(0)),'python_executable':str(m.PYTHON),'target':str(target),'target_sha256':m.sha(target),'target_arguments':target_args}
            if edit_runtime:edit_runtime(rr)
            write(runtime,rr)
            if not missing_report:
                write(out/('full-qa-summary.json' if kind=='full' else 'exact-recorded-ray-summary.json'),{'fixture_only':True,'strict_passed':False,'injected_producer_returncode':producer_exit})
            stdout.write(b'Synthetic injected producer output only.\n');stderr.write(b'')
            if late:late(c)
            return SimpleNamespace(returncode=producer_exit)
        caught=None;code=None
        try:
            with mock.patch.object(m.subprocess,'run',injected),contextlib.redirect_stdout(io.StringIO()):
                code=m.main(args)
        except Exception as e:caught=str(e)
        rec=json.loads((capture/'execution.json').read_bytes()) if (capture/'execution.json').is_file() else None
        wanted=producer_exit if expected_return is None else expected_return
        if expected_error:
            passed=(caught is not None and expected_error in caught) or (rec is not None and code==wanted and rec['completed'] is False and expected_error in rec.get('error',''))
        else:
            passed=code==wanted and caught is None and rec['completed'] is True and rec['returncode']==producer_exit and rec['runtime']['optimization_level']==(1 if mode=='optimized' else 0) and rec['tool_sources_before']==rec['tool_sources_after']==initial_sources and rec['tooling_manifest_sha256']==h
            report=out/('full-qa-summary.json' if kind=='full' else 'exact-recorded-ray-summary.json')
            passed=passed and json.loads(report.read_bytes())['strict_passed'] is False
        row={'case':name,'kind':'injected-capture-control','passed':bool(passed),'capture_return':code,'producer_exit':producer_exit,'expected_error':expected_error,'caught':caught,'completed':rec.get('completed') if rec else None}
        case_rows.append(row);write(root/'result.json',row);require(passed,name)
    for code in [0,1,2]:capture_case('full_original_exit_'+str(code),producer_exit=code)
    for mode in ['normal','optimized']:capture_case('exact_original_exit1_'+mode,kind='exact',mode=mode)
    capture_case('full_optimized_rejected',mode='optimized',expected_error='Full wrapper must start normal')
    capture_case('full_with_full_argument_rejected',edit_pre=lambda r,o,c,f,args,contract:args.extend(['--full',str(f)]),expected_error='Full wrapper must start normal')
    capture_case('existing_capture_rejected',edit_pre=lambda r,o,c,f,args,contract:c.mkdir(),expected_error='must both be NEW')
    capture_case('overlap_capture_rejected',edit_pre=lambda r,o,c,f,args,contract:args.__setitem__(args.index('--capture')+1,str(o/'capture')),expected_error='must be separate trees')
    def prerequisite(field,value,which='dense'):
        def edit(r,o,c,f,args,contract):
            p=f/'normal'/('standard/dense/dense-check.json' if which=='dense' else 'standard/raw/raw-mesh-check.json');d=json.loads(p.read_bytes());d[field]=value;write(p,d)
        return edit
    for field,value,label in [('under_0p8mm_count',1,'short'),('under_0p8mm_count',False,'bool_short'),('flagged_sample_count',0,'empty_flags'),('flagged_sample_count',True,'bool_flags'),('strict_passed',True,'strict_upgraded')]:
        capture_case('exact_'+label,kind='exact',edit_pre=prerequisite(field,value),expected_error='zero short rays and positive original flags')
    capture_case('exact_failed_raw',kind='exact',edit_pre=prerequisite('strict_passed',False,'raw'),expected_error='Exact prerequisite failed')
    capture_case('missing_producer_report',missing_report=True,expected_return=2,expected_error='Producer summary missing')
    capture_case('wrong_runtime_mode',edit_runtime=lambda r:r.update(optimization_level=1),expected_return=2,expected_error='Actual optimization mode mismatch')
    capture_case('boolean_runtime_mode',edit_runtime=lambda r:r.update(optimization_level=False),expected_return=2,expected_error='Actual optimization mode mismatch')
    capture_case('wrong_runtime_affinity',edit_runtime=lambda r:r.update(cpu_affinity=[]),expected_return=2,expected_error='Runtime CPU binding differs')
    capture_case('wrong_runtime_source',edit_runtime=lambda r:r.update(target_sha256='0'*64),expected_return=2,expected_error='Runtime producer binding differs')
    capture_case('late_stl_mutation',late=lambda c:c['stl'].write_bytes(b'changed synthetic input'),expected_return=2,expected_error='Original sources/STL changed')
    require(m.inventory(baseline/'tooling')==initial_sources and m.sha(manifest)==h,'Original sources changed')
    report={'passed':all(r['passed'] for r in case_rows),'scope':__doc__,'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'cases':case_rows,'case_count':len(case_rows),'capture_source_sha256':m.sha(Path(m.__file__)),'test_source_sha256':m.sha(__file__),'original_tooling_manifest_sha256':h,'all_original_tool_sources_unchanged':True,'model_verified':False}
    write(a.out/'results.json',report);print(json.dumps({'passed':report['passed'],'case_count':len(case_rows),'optimization_level':sys.flags.optimize}))
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
