"""Freeze candidate evidence locally and run independent, sequential QA.
No author paths are written; all command outputs are new and retained.
A completed run is not automatically a passed model.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time

def require(c,m):
 if not c:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
VIEWS={'front','rear','local-plus-y','local-minus-y','local-plus-x','local-minus-x','top','court-open','court-high-wings','entry','court-stair'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--author-root',type=Path,required=True);ap.add_argument('--version',required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--geometry-only',action='store_true');ap.add_argument('--freeze-manifest',type=Path,required=True);ap.add_argument('--expected-freeze-sha256',required=True);args=ap.parse_args()
 require(not args.out.exists(),'Output directory exists; never reuse or overwrite evidence');args.out.mkdir(parents=True)
 author=args.author_root.resolve();out=args.out.resolve();model=author/'models'/args.version;preview=author/'previews'/args.version
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
 env.pop('PYTHONOPTIMIZE',None);env['PYTHONDONTWRITEBYTECODE']='1'
 inventory={};author_manifest_inventory={};independent_inventory={};rows=[];summary={'completed':False,'strict_passed':False,'candidate_version':args.version,'stl_sha256':args.expected_sha256,'executions':rows}
 start=time.time()
 def freeze(src,dst):
  require(src.is_file(),f'Missing frozen input {src.name}');digest=sha(src);require(author_manifest_inventory.get(str(src.relative_to(author)))==digest,'Input absent from or differs from author freeze manifest');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);require(sha(dst)==digest,'Snapshot copy differs');inventory[str(src.relative_to(author))]=digest
 def run(name,cmd):
  begin=time.time();log=out/'execution-logs'/(name+'.log');log.parent.mkdir(exist_ok=True)
  with log.open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env)
  row={'name':name,'returncode':p.returncode,'elapsed_seconds':time.time()-begin,'command':cmd,'log_file':str(log.relative_to(out)),'log_sha256':sha(log)};rows.append(row);write(out/'executions.json',rows);print(json.dumps(row),flush=True);return p.returncode
 try:
  require(sha(args.freeze_manifest)==args.expected_freeze_sha256,'Author freeze manifest hash differs');freeze_data=json.loads(args.freeze_manifest.read_text());require(freeze_data['version']==args.version and freeze_data['stl_sha256']==args.expected_sha256,'Author freeze candidate differs')
  for record in freeze_data['files']:
   relative=record['path'];p=Path(relative);require(not p.is_absolute() and '..' not in p.parts and relative not in author_manifest_inventory,'Invalid/duplicate author freeze path');require((author/p).stat().st_size==record['bytes'] and sha(author/p)==record['sha256'],'Author freeze member differs: '+relative);author_manifest_inventory[relative]=record['sha256']
  shutil.copyfile(args.freeze_manifest,out/'author-freeze-manifest.json');require(sha(out/'author-freeze-manifest.json')==args.expected_freeze_sha256,'Copied author manifest differs');write(out/'author-freeze-validation.json',{'passed':True,'file_count':len(author_manifest_inventory),'manifest_sha256':args.expected_freeze_sha256,'stl_sha256':args.expected_sha256})
  require(sha(model/'model.stl')==args.expected_sha256,'Original STL differs from the supplied frozen SHA-256')
  for name in ['model.stl','build_model.py','parameters.json','upper_wing_fin_positions.json','color-regions.json','build-report.json']:
   freeze(model/name,out/'frozen'/'models'/args.version/name)
  require(sha(out/'frozen'/'models'/args.version/'model.stl')==args.expected_sha256,'Copied frozen STL differs from supplied hash')
  if not args.geometry_only:
   for name in ['scene.blend','render_preview.py','independent-appearance-review.json']:freeze(model/name,out/'frozen'/'models'/args.version/name)
   freeze(preview/'render-manifest.json',out/'frozen'/'previews'/args.version/'render-manifest.json')
   manifest=json.loads((out/'frozen'/'previews'/args.version/'render-manifest.json').read_text());require(manifest['stl_sha256']==args.expected_sha256 and set(manifest['views'])==VIEWS,'Original view manifest inconsistent')
   for name,row in manifest['views'].items():
    require(sha(preview/(name+'.png'))==row['sha256'],'Original PNG manifest hash mismatch');freeze(preview/(name+'.png'),out/'frozen'/'previews'/args.version/(name+'.png'));require(sha(out/'frozen'/'previews'/args.version/(name+'.png'))==row['sha256'],'Copied frozen PNG manifest hash mismatch')
  canonical=[('source/build_model.py','build_model.py'),('source/upper_wing_fin_positions.json','upper_wing_fin_positions.json'),('parameters.json','parameters.json')]
  if not args.geometry_only:canonical.append(('source/render_preview.py','render_preview.py'))
  canonical_matches={}
  for relative,name in canonical:
   freeze(author/relative,out/'frozen'/relative);canonical_matches[relative]=sha(out/'frozen'/relative)==sha(out/'frozen'/'models'/args.version/name)
  summary['canonical_sources_match_tested_version_snapshots']=canonical_matches
  require(all(canonical_matches.values()),'Canonical documented sources differ from tested version snapshots')
  for src in sorted((author/'verification').iterdir()):
   if src.is_file() and src.suffix in ['.py','.cpp']:freeze(src,out/'frozen'/'verification'/src.name)
  for name in ['README.md','CURRENT-STATUS.md','PRINTING-LIMITS.md','GEOMETRY-PRINT-PLAN.md','ESTIMATES-AND-SIMPLIFICATIONS.md','requirements.txt','toolchain.json','sources.json']:
   freeze(author/name,out/'frozen'/'documentation'/name)
  own_tools=Path(__file__).resolve().parent
  for name in ['run_independent_candidate.py','inspect_and_rerender_blend.py','compare_source_scene.py','png_exact_compare.py','sanitize_png_previews.py','diagnose_recorded_cpp_rays.py','exact_ray_diagnosis.py']:
   src=own_tools/name;dst=out/'frozen'/'independent-tools'/name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(src,dst);require(sha(src)==sha(dst),'Independent tool snapshot differs');independent_inventory[name]=sha(dst)
  write(out/'independent-tool-inventory.json',independent_inventory)
  write(out/'frozen-input-inventory.json',inventory)
  frozen=out/'frozen';stl=frozen/'models'/args.version/'model.stl';ver=frozen/'verification'
  for mode,opts in [('normal',[]),('optimized',['-O'])]:
   base=out/'geometry'/mode;base.mkdir(parents=True)
   py=[sys.executable,'-B',*opts]
   run(mode+'-standard',py+[str(ver/'run_qa.py'),'--stl',str(stl),'--out',str(base/'standard'),'--expected-longest-mm','210'])
   run(mode+'-exact-intersections',py+[str(ver/'check_original_intersections.py'),'--stl',str(stl),'--expected-sha256',args.expected_sha256,'--out',str(base/'intersections.json'),'--progress'])
   run(mode+'-intersection-controls',py+[str(ver/'check_intersection_controls.py'),'--out-dir',str(base/'intersection-controls')])
  repro=out/'reproduction';(repro/'source').mkdir(parents=True)
  for name in ['build_model.py','upper_wing_fin_positions.json']:shutil.copyfile(frozen/'models'/args.version/name,repro/'source'/name)
  shutil.copyfile(frozen/'models'/args.version/'parameters.json',repro/'parameters.json')
  code=run('source-stl-reproduction',[sys.executable,'-B',str(repro/'source'/'build_model.py'),'--output-dir',str(repro/'models'/args.version)])
  recreated=repro/'models'/args.version
  summary['source_rebuild']={'returncode':code,'original_stl_bitwise_identical':(recreated/'model.stl').is_file() and sha(recreated/'model.stl')==args.expected_sha256,'original_color_regions_bitwise_identical':(recreated/'color-regions.json').is_file() and sha(recreated/'color-regions.json')==sha(frozen/'models'/args.version/'color-regions.json')}
  if not args.geometry_only:
   shutil.copyfile(frozen/'models'/args.version/'render_preview.py',repro/'source'/'render_preview.py')
   script=frozen/'independent-tools'/'compare_source_scene.py'
   run('source-scene-state-reproduction',['blender','--background','--threads','1','--python-exit-code','1','--python',str(script),'--','--source',str(repro/'source'/'render_preview.py'),'--version',args.version,'--original-blend',str(frozen/'models'/args.version/'scene.blend'),'--manifest',str(frozen/'previews'/args.version/'render-manifest.json'),'--expected-stl-sha256',args.expected_sha256,'--out',str(out/'source-scene-reproduction')])
   script=frozen/'independent-tools'/'inspect_and_rerender_blend.py'
   run('saved-blend-eleven-rerenders',['blender','--background','--threads','1','--python-exit-code','1','--python',str(script),'--','--blend',str(frozen/'models'/args.version/'scene.blend'),'--stl',str(stl),'--manifest',str(frozen/'previews'/args.version/'render-manifest.json'),'--expected-sha256',args.expected_sha256,'--out',str(out/'saved-blend-rerenders')])
  unchanged={name:sha(author/name)==digest for name,digest in author_manifest_inventory.items()};unchanged['AUTHOR_FREEZE_MANIFEST']=sha(args.freeze_manifest)==args.expected_freeze_sha256
  own_unchanged={name:sha(own_tools/name)==digest and sha(frozen/'independent-tools'/name)==digest for name,digest in independent_inventory.items()}
  summary.update(completed=True,independent_tool_rechecks=own_unchanged,all_independent_tools_unchanged=all(own_unchanged.values()),all_original_frozen_inputs_unchanged=all(unchanged.values()),original_input_rechecks=unchanged,
    all_processes_exit_zero=all(r['returncode']==0 for r in rows),scope='Execution inventory only. Every report and required artifact must be independently inspected. Original numerical strict failures remain failures even if an exact supplementary diagnosis explains individual flags.')
 except Exception as e:summary.update(error_type=type(e).__name__,error=str(e))
 summary['elapsed_seconds']=time.time()-start;write(out/'independent-execution-summary.json',summary)
 return 0 if summary['completed'] and summary['all_original_frozen_inputs_unchanged'] and summary['all_independent_tools_unchanged'] else 1
if __name__=='__main__':raise SystemExit(main())
