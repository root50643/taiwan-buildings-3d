"""Read-only current release delta and decoded privacy checks; no geometry QA."""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,io,json,re,subprocess

MODEL=Path(__file__).resolve().parents[1]
PREFIX='正修科技大學/校本部/buildings/csu-administration-03'
ORIGINAL='6e683682473c2d1dbdf221b47270e0c909bd6eb0'
CHANGED={'README.md','PUBLICATION.md','QA.md','source/validate_publication.py','models/v1/scene.blend','models/v2/scene.blend'}
PRIVATE=re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+|/(?:home|Users)/[A-Za-z0-9_.-]+/',re.I)
CREDENTIAL=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{40,}')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise SystemExit('Choose a new output; historical reports are not overwritten')
    root=Path(subprocess.check_output(['git','-C',str(MODEL),'rev-parse','--show-toplevel']).decode().strip())
    def git(*a):return subprocess.check_output(['git','-C',str(root),*a])
    def sha(data):return hashlib.sha256(data).hexdigest()
    spec=importlib.util.spec_from_file_location('fixed_scene_redaction',MODEL/'source/redact_scene_paths.py')
    tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
    def views(path,data):
        result=[('raw',data)]
        if data.startswith(b'\x1f\x8b'):result.append(('all_gzip_members',gzip.decompress(data)))
        if path.endswith('.blend'):
            result.append(('all_BLEND_zstd_data_frames',b''.join(f['data'] for f in tool.split_frames(data))))
        return result
    def findings(path,data):
        found=[];expanded=[]
        for kind,view in views(path,data):
            if kind!='raw':expanded.append({'path':path,'view':kind,'bytes':len(view),'sha256':sha(view)})
            for name,pattern in [('private_host_path',PRIVATE),('credential_like_literal',CREDENTIAL)]:
                for encoding,scan in [('byte',view),('NUL_removed',view.replace(b'\0',b''))]:
                    hits=list(pattern.finditer(scan))
                    if hits:found.append({'path':path,'view':kind,'pattern':name,'representation':encoding,'match_count':len(hits),'offsets':[m.start() for m in hits]})
        return found,expanded
    oldtree=[]
    for raw in git('ls-tree','-r','-z',ORIGINAL).split(b'\0'):
        if not raw:continue
        meta,path=raw.split(b'\t',1);name=path.decode()
        if name.startswith(PREFIX+'/') or name in ['README.md','model-packages.json','正修科技大學/README.md','正修科技大學/校本部/README.md','全國大專院校/README.md','全國大專院校/coverage.json','全國大專院校/institutions.json','全國大專院校/institutions.csv']:
            oldtree.append((name,meta.decode().split()[2]))
    batch=io.BytesIO(subprocess.check_output(['git','-C',str(root),'cat-file','--batch'],input=''.join(blob+'\n' for _,blob in oldtree).encode()))
    comparisons=[];before=[]
    for path,blob in oldtree:
        header=batch.readline().split();assert header[0].decode()==blob and header[1]==b'blob'
        old=batch.read(int(header[2]));assert batch.read(1)==b'\n'
        new=(root/path).read_bytes();same=old==new
        comparisons.append({'path':path,'original_bytes':len(old),'original_sha256':sha(old),'current_bytes':len(new),'current_sha256':sha(new),'identical':same})
        found,_=findings(path,old);before.extend(found)
    current=[];after=[];expanded=[]
    for p in sorted(MODEL.rglob('*')):
        if not p.is_file() or p.resolve()==args.output.resolve():continue
        data=p.read_bytes();rel=p.relative_to(MODEL).as_posix()
        current.append({'path':rel,'bytes':len(data),'sha256':sha(data)})
        found,decoded=findings(rel,data);after.extend(found);expanded.extend(decoded)
    actual_changed={x['path'][len(PREFIX)+1:] for x in comparisons if x['path'].startswith(PREFIX+'/') and not x['identical']}
    outside_changes=git('diff','-z','--name-only',ORIGINAL,'--').decode().strip('\0').split('\0')
    outside_changes+=[x for x in git('ls-files','--others','--exclude-standard','-z').decode().strip('\0').split('\0') if x]
    outside=[p for p in outside_changes if p and not p.startswith(PREFIX+'/')]
    manifest=json.loads((MODEL/'qa/scene-path-redaction-1/redaction-manifest.json').read_bytes())
    scene_checks=[]
    for row in manifest['files']:
        data=(MODEL/row['path']).read_bytes();decoded=b''.join(f['data'] for f in tool.split_frames(data))
        lo,hi=row['field']['expanded_range']
        scene_checks.append({'path':row['path'],'current_size_SHA256_match':len(data)==row['delivered_bytes'] and sha(data)==row['delivered_sha256'],
          'all_frames_decoded_SHA256_match':sha(decoded)==row['delivered_expanded_sha256'],
          'relative_dir_and_NUL_fill_match':decoded[lo:hi]==b'//'+b'\0'*(hi-lo-2)})
    mp=json.loads((root/'model-packages.json').read_bytes())
    counts={'total':mp['total_packages'],'campus':mp['higher_education_model_packages'],'schools':mp['all_repository_institutions_with_models'],'new_catalog':mp['new_campus_packages'],'CSU':mp['schools']['正修科技大學']['count']}
    broken=[]
    for p in [MODEL/'README.md',MODEL/'PUBLICATION.md',MODEL/'QA.md',MODEL/'qa/scene-path-redaction-1/README.md']:
        for target in re.findall(r'\]\(([^\n)]+)\)',p.read_text(encoding='utf8')):
            target=target.strip('<>').split('#')[0]
            if target and (p.parent/target).resolve()==args.output.resolve():continue  # This fresh report is generated after input validation.
            if target and '://' not in target and not (p.parent/target).exists():broken.append({'path':p.relative_to(MODEL).as_posix(),'link':target})
    unique_before={x['path'] for x in before}
    checks={'all_403_original_release_files_present':len(comparisons)==403,
      'existing_changes_only_six_metadata_and_explanatory_files':actual_changed==CHANGED,
      'eight_indexes_and_other_397_files_identical':sum(x['identical'] for x in comparisons)==397,
      'no_changes_outside_model_package_since_original_release':not outside,
      'original_full_binary_scan_failure_recorded':unique_before=={PREFIX+'/models/v1/scene.blend',PREFIX+'/models/v2/scene.blend'},
      'current_raw_gzip_and_all_BLEND_frames_no_private_or_credential_pattern':not after,
      'current_scene_manifest_and_relative_directory_match':all(all(v for k,v in x.items() if k!='path') for x in scene_checks),
      'counts_unchanged':counts=={'total':496,'campus':464,'schools':107,'new_catalog':425,'CSU':2},
      'current_explanatory_links_exist':not broken}
    report={'scope':'Metadata release delta, exact existing-byte preservation and decoded privacy pattern check; not full manufacturing, physical print, source research, slicing or render QA.',
      'checker_sha256':sha(Path(__file__).read_bytes()),
      'original_release_commit':ORIGINAL,'before_full_binary_scan_passed':False,'before_distinct_files_with_private_host_path':len(unique_before),'before_findings':before,
      'after_findings':after,'checks':checks,'passed':all(checks.values()),'strict_manufacturing_passed':False,'physical_print_performed':False,
      'counts':counts,'current_files_scanned_excluding_this_report':len(current),'current_total_bytes_excluding_this_report':sum(x['bytes'] for x in current),
      'decoded_views':expanded,'scene_checks':scene_checks,'existing_files':comparisons,'current_inventory':current,'outside_changes':outside,'broken_links':broken,
      'limitations':'Pattern scan is finite; original/full Blender stream and scene semantic comparisons are separately independently reviewed. No claim of generic malware/secret-proof binary analysis.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({k:report[k] for k in ['passed','checks','before_full_binary_scan_passed','before_distinct_files_with_private_host_path','current_files_scanned_excluding_this_report']},indent=2))
    raise SystemExit(0 if report['passed'] else 1)

if __name__=='__main__':main()
