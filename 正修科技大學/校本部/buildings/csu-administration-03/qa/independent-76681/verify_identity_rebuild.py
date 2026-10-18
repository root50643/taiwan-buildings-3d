if __name__ == '__main__':
    raise SystemExit('Historical provenance only; use reproduce.py in a fresh output directory. Do not overwrite archived evidence.')

from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
from importlib.metadata import version

ROOT=Path(__file__).resolve().parent
REPO=Path('<REPO_ROOT>')
P=REPO/'正修科技大學/校本部/buildings/csu-administration-03'
COMMIT='76681c5dcedc88d684946780e795d7914a88c075'
sha=lambda b:hashlib.sha256(b).hexdigest()
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
def git(*args):return subprocess.check_output(['git','--git-dir='+str(REPO/'.git'),*args],env=env)
prefix=P.relative_to(REPO).as_posix();bindings=[]
for row in git('ls-tree','-rz',COMMIT,'--',prefix).split(b'\0'):
    if not row:continue
    meta,name=row.split(b'\t',1);oid=meta.decode().split()[2];name=name.decode('utf-8')
    raw=(REPO/name).read_bytes();original=git('cat-file','blob',oid)
    bindings.append({'path':name,'git_blob':oid,'bytes':len(raw),'sha256':sha(raw),'matches_commit':raw==original})
snapshot={f.relative_to(P).as_posix():sha(f.read_bytes()) for f in P.rglob('*') if f.is_file()}
tree_names=git('ls-tree','-r','--name-only',COMMIT).decode('utf-8').splitlines()
rules=[x for x in tree_names if x.lower().endswith(('agents.md','skill.md')) or x.startswith('.agents/') or '/.agents/' in x]
delivery_path=REPO.parent/'delivery.json';delivery=json.loads(delivery_path.read_text(encoding='utf-8'))
receipt_path=REPO.parent/'library-backup/library-verification.json';receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
identity={'commit':COMMIT,'head':git('rev-parse','HEAD').decode().strip(),'tracked_package_files':len(bindings),'all_package_bytes_match_commit':all(r['matches_commit'] for r in bindings),'files':bindings,'candidate_snapshot_before':snapshot,'git_tree_rule_or_skill_paths':rules,'author_Library_delivery_receipt':delivery,'author_Library_verification_receipt':receipt,'delivery_json_sha256':sha(delivery_path.read_bytes()),'verification_json_sha256':sha(receipt_path.read_bytes()),'reviewer_Library_download_performed':False,'receipt_identity_matches_expected':delivery['candidate_commit']==COMMIT and delivery['library_file_id']=='libfile_2c2d4cd4e1988191b0451cc967251490' and delivery['size_bytes']==37898165 and delivery['sha256']=='79065a030374b464dd8ab8e2d5e631dec3d8ecc110dc938661b1e6ca248b2c51'}
(ROOT/'identity-and-author-receipt.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf-8')
assert identity['head']==COMMIT and identity['all_package_bytes_match_commit'] and identity['receipt_identity_matches_expected']
stage=ROOT/'rebuild-package';(stage/'source').mkdir(parents=True,exist_ok=True)
shutil.copyfile(P/'source/build_model.py',stage/'source/build_model.py');shutil.copyfile(P/'parameters.json',stage/'parameters.json')
rebuilt=ROOT/'rebuilt';run=subprocess.run([sys.executable,'-B',str(stage/'source/build_model.py'),'--output-dir',str(rebuilt)],capture_output=True,text=True,encoding='utf-8',env=env)
(ROOT/'rebuild.stdout.log').write_text(run.stdout,encoding='utf-8');(ROOT/'rebuild.stderr.log').write_text(run.stderr,encoding='utf-8')
assert run.returncode==0,run.stderr
files=['parts/body.stl','parts/roof.stl','assembly.stl']
report={'returncode':run.returncode,'runtime':{'python':sys.version,'packages':{n:version(n) for n in ['numpy','trimesh','manifold3d']}},'source_and_parameter_copy_exact':(stage/'source/build_model.py').read_bytes()==(P/'source/build_model.py').read_bytes() and (stage/'parameters.json').read_bytes()==(P/'parameters.json').read_bytes(),'files':[{'path':name,'fixed_sha256':sha((P/'models/v2'/name).read_bytes()),'rebuilt_sha256':sha((rebuilt/name).read_bytes()),'byte_identical':(P/'models/v2'/name).read_bytes()==(rebuilt/name).read_bytes()} for name in files],'method':'Only source/build_model.py and parameters.json copied into a new reviewer directory; builder not run in candidate. No mesh repairs or file mutation of candidate.'}
(ROOT/'independent-rebuild.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
assert all(r['byte_identical'] for r in report['files'])
print(json.dumps({'tracked_files':len(bindings),'all_match_commit':identity['all_package_bytes_match_commit'],'rule_paths':rules,'receipt_identity_matches':identity['receipt_identity_matches_expected'],'rebuild':report},ensure_ascii=False,indent=2))
