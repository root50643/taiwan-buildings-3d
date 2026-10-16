"""Isolated source, saved-Blend and nine-preview reproduction verification.
Derived from the generic freeze/rebuild flow of run_independent_candidate.py.
No geometry QA is run here. Full rendering requires explicit --rerender.
Original files are read-only, outputs are fresh, and failures remain on disk.
"""
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
VIEWS={'front','rear','west','east','south','north','top','entry-detail','roof-detail'}
TOOLS=['run_source_render_verification.py','compare_source_scene.py','inspect_and_rerender_blend.py','png_exact_compare.py','sanitize_png_previews.py','test_png_exact_compare.py']
def require(v,m):
    if not v: raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--author-root',type=Path,required=True);ap.add_argument('--version',required=True);ap.add_argument('--expected-stl-sha256',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--rerender',action='store_true');a=ap.parse_args()
    root=a.author_root.resolve();out=a.out.resolve();own=Path(__file__).resolve().parent
    require(out.is_relative_to(root/'qa/render-check'),'Output must be under author qa/render-check');require(not out.exists(),'Never reuse or overwrite evidence');out.mkdir(parents=True)
    inventory={};tool_inventory={};executions=[];summary={'completed':False,'passed':False,'version':a.version,'expected_stl_sha256':a.expected_stl_sha256,'rerender_requested':a.rerender,'executions':executions}
    def run(name,cmd):
        start=time.monotonic();log=out/'logs'/(name+'.log');log.parent.mkdir(exist_ok=True)
        with log.open('w') as handle:result=subprocess.run(cmd,stdout=handle,stderr=subprocess.STDOUT)
        row={'name':name,'command':cmd,'exit_code':result.returncode,'seconds':time.monotonic()-start,'log':str(log.relative_to(out)),'log_sha256':sha(log)};executions.append(row);write(out/'executions.json',executions);print(json.dumps(row),flush=True);require(result.returncode==0,name+' process failed; see retained log')
    def freeze(relative):
        src=root/relative;dest=out/'frozen'/relative;require(src.is_file(),'Missing input '+str(relative));h=sha(src);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);require(sha(dest)==h,'Copy changed');inventory[str(relative)]={'sha256':h,'bytes':src.stat().st_size};return dest
    try:
        model=Path('models')/a.version;preview=Path('previews')/a.version
        for name in ['model.stl','scene.blend','parameters.json','color-regions.json','build_model.py','render_preview.py','build-report.json']:freeze(model/name)
        for name in ['source/build_model.py','source/render_preview.py','parameters.json']:freeze(Path(name))
        mf=freeze(preview/'render-manifest.json');manifest=json.loads(mf.read_text());frozen=out/'frozen';m=frozen/model
        require(sha(m/'model.stl')==a.expected_stl_sha256 and manifest['stl_sha256']==a.expected_stl_sha256,'STL freeze binding mismatch')
        require(set(manifest['views'])==VIEWS,'Exactly nine formal views required');require(manifest['blend_sha256']==sha(m/'scene.blend'),'Manifest Blend hash mismatch');require(manifest['render_source_sha256']==sha(m/'render_preview.py'),'Manifest render source hash mismatch')
        for name,row in manifest['views'].items():require(sha(freeze(preview/(name+'.png')))==row['sha256'],'Preview PNG differs from manifest: '+name)
        matches={name:sha(frozen/name)==sha(m/Path(name).name) for name in ['source/build_model.py','source/render_preview.py','parameters.json']};summary['canonical_sources_match_model_snapshots']=matches;require(all(matches.values()),'Canonical source/model snapshots mismatch')
        for name in TOOLS:
            src=own/name;dst=out/'tools'/name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(src,dst);tool_inventory[name]=sha(src);require(sha(dst)==tool_inventory[name],'Tool snapshot mismatch')
        write(out/'input-freeze.json',inventory);write(out/'tool-freeze.json',tool_inventory)
        repro=out/'reproduction';(repro/'source').mkdir(parents=True)
        for name in ['build_model.py','render_preview.py']:shutil.copyfile(m/name,repro/'source'/name)
        shutil.copyfile(m/'parameters.json',repro/'parameters.json')
        run('source-rebuild',[sys.executable,'-B',str(repro/'source/build_model.py'),'--output-dir',str(repro/model)])
        rebuild={name:{'original_sha256':sha(m/name),'rebuilt_sha256':sha(repro/model/name),'bytes_identical':(m/name).read_bytes()==(repro/model/name).read_bytes()} for name in ['model.stl','color-regions.json','parameters.json','build_model.py','build-report.json']}
        write(out/'source-rebuild.json',{'passed':all(r['bytes_identical'] for r in rebuild.values()),'files':rebuild});require(all(r['bytes_identical'] for r in rebuild.values()),'Source rebuild not byte identical')
        common=['blender','--background','--threads','1','--python-exit-code','1','--python']
        run('source-scene-state',common+[str(out/'tools/compare_source_scene.py'),'--','--source',str(repro/'source/render_preview.py'),'--version',a.version,'--original-blend',str(m/'scene.blend'),'--manifest',str(mf),'--expected-stl-sha256',a.expected_stl_sha256,'--out',str(out/'source-scene')])
        args=['--blend',str(m/'scene.blend'),'--stl',str(m/'model.stl'),'--manifest',str(mf),'--expected-sha256',a.expected_stl_sha256]
        run('blend-inspect',common+[str(out/'tools/inspect_and_rerender_blend.py'),'--',*args,'--out',str(out/'blend-inspect'),'--inspect-only'])
        for label,options in [('normal',[]),('optimized',['-O'])]:
            run('png-controls-'+label,[sys.executable,'-B',*options,str(out/'tools/test_png_exact_compare.py'),'--out',str(out/('png-controls-'+label))])
        if a.rerender:
            run('saved-blend-nine-rerenders',common+[str(out/'tools/inspect_and_rerender_blend.py'),'--',*args,'--out',str(out/'saved-blend-rerenders')])
        run('metadata-only-cleanup',[sys.executable,'-B',str(out/'tools/sanitize_png_previews.py'),'--manifest',str(mf),'--expected-manifest-sha256',sha(mf),'--expected-stl-sha256',a.expected_stl_sha256,'--out',str(out/'sanitized-previews')])
        checks={name:sha(root/name)==row['sha256'] and sha(frozen/name)==row['sha256'] for name,row in inventory.items()};tools={name:sha(own/name)==h and sha(out/'tools'/name)==h for name,h in tool_inventory.items()}
        summary.update(original_input_rechecks=checks,tool_rechecks=tools,completed=True,passed=all(checks.values()) and all(tools.values()),full_nine_view_rerender_verified=a.rerender)
        require(summary['passed'],'An input/tool changed during verification')
    except Exception as e:summary.update(passed=False,error_type=type(e).__name__,error=str(e))
    write(out/'SOURCE-RENDER-VERIFICATION.json',summary);print(json.dumps({'completed':summary['completed'],'passed':summary['passed'],'error':summary.get('error'),'full_nine_view_rerender_verified':summary.get('full_nine_view_rerender_verified',False)}));return 0 if summary['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
