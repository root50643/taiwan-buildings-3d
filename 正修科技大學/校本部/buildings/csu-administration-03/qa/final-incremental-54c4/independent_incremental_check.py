if __name__ == '__main__':
    raise SystemExit('Historical provenance only. This fixed-review script depends on the old snapshot and external receipts; do not rerun it against the published package or overwrite archived evidence.')

from pathlib import Path
import ast,collections,hashlib,io,json,os,shutil,struct,subprocess,sys,zlib
from PIL import Image

ROOT=Path(__file__).resolve().parent
REPO=Path('<REPO_ROOT>')
P=REPO/'正修科技大學/校本部/buildings/csu-administration-03'
OLD='76681c5dcedc88d684946780e795d7914a88c075';NEW='54c4ad2a30e6600e85fbf054d4c384f9e5304748'
prefix=P.relative_to(REPO).as_posix();env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','--git-dir='+str(REPO/'.git'),*args],env=env)
def tree(commit):
    ans={}
    for row in git('ls-tree','-rz',commit,'--',prefix).split(b'\0'):
        if not row:continue
        meta,name=row.split(b'\t',1);name=name.decode('utf-8');ans[name[len(prefix)+1:]]=meta.decode().split()[2]
    return ans
def blob(oid):return git('cat-file','blob',oid)
old,new=tree(OLD),tree(NEW)
modified=sorted(n for n in old.keys()&new.keys() if old[n]!=new[n]);added=sorted(new.keys()-old.keys());removed=sorted(old.keys()-new.keys())
bindings=[]
for name,oid in new.items():
    raw=(P/name).read_bytes();bindings.append({'path':name,'git_blob':oid,'bytes':len(raw),'sha256':sha(raw),'matches_commit':raw==blob(oid)})
snapshot={p.relative_to(P).as_posix():sha(p.read_bytes()) for p in P.rglob('*') if p.is_file()}
all_changed_repo=git('diff','--name-only','-z',OLD,NEW).decode('utf-8').split('\0');outside=[n for n in all_changed_repo if n and not n.startswith(prefix+'/')]
media=[]
for name in old:
    if name.lower().endswith(('.stl','.blend','.gcode')):
        media.append({'path':name,'unchanged':name in new and old[name]==new[name],'sha256':sha((P/name).read_bytes())})
def chunks(raw):
    assert raw[:8]==b'\x89PNG\r\n\x1a\n';i=8;ans=[]
    while i<len(raw):
        n,typ=struct.unpack_from('>I4s',raw,i);end=i+n+12;data=raw[i+8:i+n+8]
        assert end<=len(raw) and zlib.crc32(typ+data)&0xffffffff==struct.unpack_from('>I',raw,i+n+8)[0]
        ans.append((typ,data,raw[i:end]));i=end
        if typ==b'IEND':break
    assert i==len(raw);return ans
pngs=[]
for name in modified:
    if not name.endswith('.png'):continue
    a=blob(old[name]);b=(P/name).read_bytes();ca,cb=chunks(a),chunks(b)
    assert len(ca)==len(cb)
    differing=[i for i,(x,y) in enumerate(zip(ca,cb)) if x[2]!=y[2]]
    imga,imgb=Image.open(io.BytesIO(a)),Image.open(io.BytesIO(b));imga.load();imgb.load()
    idata=b''.join(x[1] for x in ca if x[0]==b'IDAT');idatb=b''.join(x[1] for x in cb if x[0]==b'IDAT')
    row={'path':name,'old_sha256':sha(a),'new_sha256':sha(b),'dimensions':list(imga.size),'mode':imga.mode,'PNG_CRC_valid':True,'changed_chunk_indices':differing,'only_File_text_value_replaced':len(differing)==1 and all(ca[i][0]==cb[i][0]==b'tEXt' and ca[i][1].split(b'\0',1)[0]==cb[i][1].split(b'\0',1)[0]==b'File' for i in differing),'delivered_File_value':[cb[i][1].split(b'\0',1)[1].decode('utf-8') for i in differing],'all_non_File_chunks_exact':all(x[2]==y[2] for x,y in zip(ca,cb) if not(x[0]==b'tEXt' and x[1].split(b'\0',1)[0]==b'File')),'IDAT_exactly_equal':idata==idatb,'decoded_pixels_exactly_equal':imga.size==imgb.size and imga.mode==imgb.mode and imga.tobytes()==imgb.tobytes(),'decoded_pixel_sha256':sha(imgb.tobytes())}
    pngs.append(row)
pa=json.loads(blob(old['parameters.json']));pb=json.loads((P/'parameters.json').read_text(encoding='utf-8'))
def leaves(v,p=''):
    if isinstance(v,dict):
        return {k2:v2 for k,val in v.items() for k2,v2 in leaves(val,p+'.'+k if p else k).items()}
    return {p:v}
la,lb=leaves(pa),leaves(pb);changed_params={k:{'old':la[k],'new':lb[k]} for k in la.keys()&lb.keys() if la[k]!=lb[k]}
def ast_without_module_doc(t):
    a=ast.parse(t)
    if a.body and isinstance(a.body[0],ast.Expr) and isinstance(a.body[0].value,ast.Constant) and isinstance(a.body[0].value.value,str):a.body.pop(0)
    return ast.dump(a,include_attributes=False)
audit_name='source/qa_audit_gcode.py';audit_ast_equal=ast_without_module_doc(blob(old[audit_name]).decode('utf-8'))==ast_without_module_doc((P/audit_name).read_text(encoding='utf-8'))
builder_unchanged=old['source/build_model.py']==new['source/build_model.py']
stage=ROOT/'current-parameter-rebuild-package';(stage/'source').mkdir(parents=True,exist_ok=True)
shutil.copyfile(P/'source/build_model.py',stage/'source/build_model.py');shutil.copyfile(P/'parameters.json',stage/'parameters.json')
run=subprocess.run([sys.executable,'-B',str(stage/'source/build_model.py'),'--output-dir',str(ROOT/'current-parameter-rebuilt')],capture_output=True,text=True,encoding='utf-8',env=env)
(ROOT/'rebuild.stdout.log').write_text(run.stdout,encoding='utf-8');(ROOT/'rebuild.stderr.log').write_text(run.stderr,encoding='utf-8')
assert run.returncode==0,run.stderr
rebuild=[{'path':n,'sha256':sha((P/'models/v2'/n).read_bytes()),'current_parameter_rebuild_byte_identical':(ROOT/'current-parameter-rebuilt'/n).read_bytes()==(P/'models/v2'/n).read_bytes()} for n in ['parts/body.stl','parts/roof.stl','assembly.stl']]
author_validation=json.loads((P/'qa/documentation-revision-1/incremental-validation.json').read_text(encoding='utf-8'))
receipt_path=REPO.parent/'delivery.json';receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
receipt_ok=receipt['candidate_commit']==NEW and receipt['library_file_id']=='libfile_2c2d4cd4e1988191b0451cc967251490' and receipt['version_number']==1 and receipt['size_bytes']==38615220 and receipt['sha256']=='63d0e0616f9661a76da0f49f6852fec60a7ab086a8be2ba8f45e3e0607372d82' and receipt['file_count']==382 and receipt['model_package_files']==377 and receipt['all_entries_size_sha256_crc_match']
# Original failure files remain byte-identical; only current prose summaries changed.
original_failure_files=['qa/v2/final-evidence-validation.json','qa/v2/body/body-original-normal-ambiguity-review.json','qa/v1/roof/roof-original-flag-endpoints.json','qa/v2/slicing/body-auto45/gcode-audit.json','qa/v2/slicing/body-auto45/slice-summary.json','qa/v2/slicing/body-auto45/corrected-audit/gcode-audit.json']
failure_bindings=[{'path':n,'unchanged':old[n]==new[n]} for n in original_failure_files]
expected_existing_nonpng={'QA.md','README.md','parameters.json','qa/v2/QA-NOTES.md','source/qa/README.md','source/qa_audit_gcode.py'}
result={'baseline_commit':OLD,'fixed_commit':NEW,'head':git('rev-parse','HEAD').decode().strip(),'baseline_tracked_file_count':len(old),'current_tracked_file_count':len(new),'all_current_tracked_bytes_match_commit':all(r['matches_commit'] for r in bindings),'modified_existing_files':modified,'added_files':added,'removed_files':removed,'outside_package_changed_paths':outside,'expected_modified_nonPNG_files_only':set(modified)-{r['path'] for r in pngs}==expected_existing_nonpng,'fixed_STL_scene_Gcode_files':media,'all_old_STL_scene_Gcode_byte_identical':all(r['unchanged'] for r in media),'geometry_builder_byte_identical':builder_unchanged,'PNG_checks':pngs,'all_16_PNG_only_File_text_and_same_IDAT_pixels':len(pngs)==16 and all(r['only_File_text_value_replaced'] and r['all_non_File_chunks_exact'] and r['IDAT_exactly_equal'] and r['decoded_pixels_exactly_equal'] for r in pngs),'parameter_changes_to_existing_values':changed_params,'only_expected_statement_values_changed':set(changed_params)=={'entrance.door_recess_depth','manufacturing.maximum_shallow_facade_recess'} and all(v['old']==0.45 and v['new']==0.65 for v in changed_params.values()),'added_parameter_leaf_keys':sorted(lb.keys()-la.keys()),'audit_algorithm_AST_unchanged_after_removing_module_docstring':audit_ast_equal,'current_parameter_rebuild':rebuild,'original_failure_evidence_byte_identical':failure_bindings,'author_14_validation_checks_preserved_and_true':len(author_validation['checks'])==14 and all(author_validation['checks'].values()),'author_strict_manufacturing_still_false':author_validation['strict_manufacturing_passed'] is False,'author_physical_print_still_false':author_validation['physical_print_performed'] is False,'author_Library_receipt':receipt,'author_Library_receipt_identity_matches':receipt_ok,'reviewer_Library_download_or_upload_performed':False,'candidate_snapshot_before':snapshot,'tracked_file_bindings':bindings,'scope':'Incremental commit/diff, PNG chunk/pixels, parameter rebuild, text semantics and author receipt. No repeat full geometry/slice/render/physical test.'}
(ROOT/'independent-incremental-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert result['head']==NEW and result['all_current_tracked_bytes_match_commit'] and not removed and not outside
assert result['all_old_STL_scene_Gcode_byte_identical'] and result['geometry_builder_byte_identical'] and result['all_16_PNG_only_File_text_and_same_IDAT_pixels']
assert result['only_expected_statement_values_changed'] and result['audit_algorithm_AST_unchanged_after_removing_module_docstring'] and all(r['current_parameter_rebuild_byte_identical'] for r in rebuild)
assert all(r['unchanged'] for r in failure_bindings) and receipt_ok
print(json.dumps({k:v for k,v in result.items() if k not in ['tracked_file_bindings','candidate_snapshot_before','PNG_checks','author_Library_receipt','fixed_STL_scene_Gcode_files','added_files']},ensure_ascii=False,indent=2))
