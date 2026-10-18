"""Independent scene field/frames and non-scene fixed-file binding; read only."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
from independent_blend_field_audit import compare as field_compare
from independent_zstd_frames import compare as frame_compare

def sha(data):return hashlib.sha256(data).hexdigest()
def require(value,message):
    if not value:raise RuntimeError(message)
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--package-root',type=Path,required=True)
    p.add_argument('--staging',type=Path,required=True);p.add_argument('--baseline',default='6e68368');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.output.exists(),'Fresh output directory required');a.output.mkdir(parents=True)
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
    def git(*args):return subprocess.check_output(['git','-C',str(a.repo),*args],env=env)
    baseline=git('rev-parse',a.baseline).decode().strip();prefix=a.package_root.resolve().relative_to(a.repo.resolve()).as_posix()
    stage_manifest=json.loads((a.staging/'manifest.json').read_text());rows=[]
    for record in stage_manifest['files']:
        name=record['path'];old=git('show',baseline+':'+prefix+'/'+name);new=(a.staging/name).read_bytes()
        require(sha(old)==record['original_sha256'] and sha(new)==record['delivered_sha256'],'Scene manifest hash differs')
        report=field_compare(old,new);region=report['changed_field_regions'][0]
        frame=frame_compare(old,new,region['field_start'],region['field_end_exclusive'])
        require(report['passed'] and frame['passed'],'Independent field/frame check failed')
        require(report['decoded_changed_byte_count']==record['changed_byte_count'],'Changed-byte count differs')
        require(region['field_start']==record['field']['expanded_range'][0] and region['field_end_exclusive']==record['field']['expanded_range'][1],'Independent SDNA field offsets differ')
        report.update(path=name,frames=frame)
        (a.output/(Path(name).parent.name+'-independent-byte-review.json')).write_text(json.dumps(report,indent=2)+'\n')
        rows.append(report)
    before_findings=sum(r['source_binary_scan_findings'] for r in rows);after_findings=sum(r['delivered_binary_scan_findings'] for r in rows)
    existing=[]
    allowed={'README.md','PUBLICATION.md','QA.md','source/validate_publication.py','models/v1/scene.blend','models/v2/scene.blend'}
    for entry in git('ls-tree','-rz',baseline,'--',prefix).split(b'\0'):
        if not entry:continue
        meta,name=entry.split(b'\t',1);oid=meta.decode().split()[2];name=name.decode();relative=name[len(prefix)+1:]
        path=a.package_root/relative;require(path.is_file(),'An original package file is missing')
        data=path.read_bytes();actual_oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        existing.append({'path':relative,'baseline_git_blob':oid,'current_git_blob':actual_oid,'sha256':sha(data),
            'unchanged':actual_oid==oid,'declared_existing_change_allowed':relative in allowed})
    unexpected=[r['path'] for r in existing if not r['unchanged'] and not r['declared_existing_change_allowed']]
    require(not unexpected,'Unexpected modification outside declared metadata/prose files')
    checks={'two_scenes_independently_pass_field_and_frame_audits':len(rows)==2 and all(r['passed'] and r['frames']['passed'] for r in rows),
        'source_decoded_binary_scan_before_is_false_with_two_findings':before_findings==2,
        'staged_decoded_binary_scan_after_is_true_with_zero_findings':after_findings==0,
        'no_unexpected_changes_to_preexisting_files':not unexpected}
    r={'passed':all(checks.values()),'checks':checks,'baseline_commit':baseline,'staging_manifest_sha256':sha((a.staging/'manifest.json').read_bytes()),
        'source_decoded_binary_scan_passed':before_findings==0,'source_decoded_binary_findings':before_findings,
        'delivered_decoded_binary_scan_passed':after_findings==0,'delivered_decoded_binary_findings':after_findings,
        'scene_reports':[{'path':row['path'],'old_sha256':row['source_compressed_sha256'],'new_sha256':row['delivered_compressed_sha256'],'changed_decoded_bytes':row['decoded_changed_byte_count']} for row in rows],
        'preexisting_file_count':len(existing),'preexisting_files':existing,'unexpected_preexisting_changes':unexpected,
        'scope':'Read-only staged metadata verification. No scene save, renderer, slicer, geometry rebuild, Git mutation or publication. Blender semantic signatures require separate comparison.',
        'historical_hygiene_limitation':'The initial 13-true publication report and Library v2 receipts are retained unchanged as historical results. Their raw-byte/text/PNG scanner did not decode compressed BLEND internals and missed two host-directory values. This report records the new before-false/after-true binary finding rather than changing old passed flags.'}
    (a.output/'independent-summary.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='preexisting_files'},indent=2))
    return 0 if r['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
