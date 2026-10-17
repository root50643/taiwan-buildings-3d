"""Inspect bytecode created by the completed Blender run, without executing it.
Recompile exact frozen PNG source in the same embedded interpreter and compare the
entire timestamp-pyc bytes. Preserve original cache as private evidence, then
remove only its location from the source tree by renaming the cache directory.
"""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib._bootstrap_external,json,os,stat,struct
from pathlib import Path
Q=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
SRC=Q/'final-v13-r1/frozen/qa/render-tools/png_exact_compare.py'
CACHE=SRC.parent/'__pycache__/png_exact_compare.cpython-313.pyc'
EXPECTED='8534792905d7fb329e40ccc0277690e2c658ae5f5636b3d2dcb53c2e50ba0cdb'
def need(v,m):
 if not v:raise RuntimeError(m)
def h(b):return hashlib.sha256(b).hexdigest()
def main():
 own=Path(__file__).read_bytes();need(len(os.sched_getaffinity(0))==1,'One CPU required');need(sys.version_info[:2]==(3,13) and sys.flags.optimize==0,'Original Blender Python3.13 normal mode required')
 source=SRC.read_bytes();cache=CACHE.read_bytes();info=SRC.stat();ci=CACHE.stat();need(h(source)==EXPECTED,'Frozen source differs');need(stat.S_ISREG(ci.st_mode) and not CACHE.is_symlink(),'Ordinary cache required');need(len(cache)>16,'Pyc header incomplete')
 magic,flags,mtime,size=struct.unpack('<4sIII',cache[:16]);need(flags==0 and mtime==int(info.st_mtime)&0xffffffff and size==len(source),'Pyc does not bind current exact source timestamp/size')
 code=compile(source,str(SRC),'exec',dont_inherit=True,optimize=0)
 regenerated=bytes(importlib._bootstrap_external._code_to_timestamp_pyc(code,int(info.st_mtime),len(source)))
 need(regenerated==cache,'Full pyc is not the deterministic compilation of exact selected source')
 need(sorted(p.name for p in CACHE.parent.iterdir())==[CACHE.name],'Unexpected other frozen cache entries')
 summary=json.loads((Q/'final-v13-r1/independent-execution-summary.json').read_text());need(summary['completed'] is True and summary['all_frozen_inputs_and_tools_unchanged'] is True,'Completed immutable full/replay required')
 selection=json.loads((Q/'final-v13-r1/author-freeze-manifest.json').read_text());need(len(selection['files'])==53 and all('__pycache__' not in r['path'] and not r['path'].endswith(('.pyc','.pyo')) for r in selection['files']),'Fresh runner selection unexpectedly contains bytecode')
 before={'original_relative_path':'final-v13-r1/frozen/qa/render-tools/__pycache__/'+CACHE.name,'bytes':len(cache),'sha256':h(cache),'mtime_ns':ci.st_mtime_ns,'ctime_ns':ci.st_ctime_ns,'mode':stat.S_IMODE(ci.st_mode)}
 dest=O/'quarantined-cache';need(not dest.exists(),'Fresh quarantine required');CACHE.parent.rename(dest)
 need((dest/CACHE.name).read_bytes()==cache and SRC.read_bytes()==source and Path(__file__).read_bytes()==own,'Original cache/source changed while preserving')
 report={'passed':True,'scope':'No bytecode was executed by this inspection. A cache generated during the already-completed unique Blender run is fully byte-identical to compiling the exact selected source with the same embedded Python. Preserve original cache bytes privately; remove only source-tree cache location before read-only postflight. This is not a claim that the entire Blender run had no cache, and grants no model or publication approval.','model_go':False,'cache_before':before,'preserved_path':'cache-origin-v13/quarantined-cache/'+CACHE.name,'source_sha256':EXPECTED,'source_bytes':len(source),'python':sys.version,'actual_optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'pyc_timestamp_source_size_match':True,'entire_recompiled_pyc_byte_identical':True,'frozen_initial_selection_had_no_bytecode':True,'full_runner_input_source_unchanged':True,'original_cache_preserved_bitwise':True,'source_sha256_unchanged_after_quarantine':h(SRC.read_bytes()),'orchestration_source_sha256':h(own)}
 with (O/'cache-origin-proof.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'passed':True,'entire_recompiled_pyc_byte_identical':True,'original_cache_preserved_bitwise':True}))
main()
