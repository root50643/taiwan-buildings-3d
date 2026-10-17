"""Run narrowly WFU-bound artifact-parser tests with complete unittest/subtest ledger.
Caller owns the shared single-CPU lock. These are synthetic controls only.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,io,json,os,sys,unittest
HELPER='3a1c5ecf34dbe7b90d747cc191ecf9cf536878e6143362f083f1ad4a76c23d14'
TEST='255dd8664f5979d5b1b0153b79456451de1b7d5f049dc0c5c8475c3deab0b3db'
def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists() and len(os.sched_getaffinity(0))==1,'Need fresh output and one CPU');a.out.mkdir(parents=True);root=Path(__file__).resolve().parent;helper=root/'artifact_structure.py';test=root/'test_artifact_structure.py';require(sha(helper)==HELPER and sha(test)==TEST,'Frozen reviewed sources differ');sys.path.insert(0,str(root));spec=importlib.util.spec_from_file_location('artifact_tests',test);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);rows=[]
 class Ledger(unittest.TextTestResult):
  def addSuccess(self,t):super().addSuccess(t);rows.append({'test':t.id(),'kind':'method','passed':True})
  def addSubTest(self,t,sub,err):super().addSubTest(t,sub,err);rows.append({'test':sub.id(),'kind':'subtest','passed':err is None})
  def addFailure(self,t,err):super().addFailure(t,err);rows.append({'test':t.id(),'kind':'failure','passed':False})
  def addError(self,t,err):super().addError(t,err);rows.append({'test':t.id(),'kind':'error','passed':False})
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Ledger).run(unittest.defaultTestLoader.loadTestsFromModule(module));log=a.out/'unittest.log';log.write_text(stream.getvalue());unchanged=sha(helper)==HELPER and sha(test)==TEST;passed=result.wasSuccessful() and result.testsRun==13 and not result.skipped and unchanged and rows and all(r['passed'] for r in rows);report={'passed':bool(passed),'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'test_count':result.testsRun,'subtest_count':sum(r['kind']=='subtest' for r in rows),'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),'cases':rows,'helper_sha256':HELPER,'test_source_sha256':TEST,'launcher_source_sha256':sha(__file__),'log_sha256':sha(log),'all_sources_unchanged':unchanged,'scope':'Fresh synthetic structural/math parser controls only. Includes exact descriptor/lattice/interval/chord, section schedule/polygon/sum, and exact intersection contact mutations. No geometry computation, model acceptance or strict-flag change.'};(a.out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':bool(passed),'optimization_level':sys.flags.optimize,'test_count':result.testsRun,'subtest_count':report['subtest_count']}));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
