"""Read-only final-incremental import integrity; not a rerun of historical QA."""
from pathlib import Path
import argparse,ast,hashlib,json,re

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    manifest=json.loads((HERE/'import-manifest.json').read_text(encoding='utf-8'))
    source=json.loads((HERE/'evidence-manifest.json').read_text(encoding='utf-8'))
    files=[];private=[];broken=[]
    for row in manifest['files']:
        path=HERE/row['destination_path'];files.append({'path':row['destination_path'],
            'size_SHA256_match':path.is_file() and path.stat().st_size==row['delivered_bytes'] and sha(path)==row['delivered_sha256']})
    mapping={row['destination_path']:row for row in manifest['files']}
    checks={'all_delivered_files_match_recorded_size_SHA256':all(x['size_SHA256_match'] for x in files),
        'source_only_manifest_original_bytes_preserved':sha(HERE/'evidence-manifest.json')==manifest['source_manifest_sha256'],
        'all_original_source_manifest_entries_bound':all(r['path'] in mapping and mapping[r['path']]['source_bytes']==r['bytes'] and mapping[r['path']]['source_sha256']==r['sha256'] for r in source),
        'historical_final_verification_original_bytes_preserved':sha(HERE/'final-verification.json')==manifest['original_final_verification_sha256']}
    historical=manifest['historical_scripts_provenance_only'];guards=[]
    for path in HERE.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in ['.md','.json','.py','.txt','.log']:continue
        text=path.read_text(encoding='utf-8')
        if re.search(r'[A-Za-z]:[\\/](?:Users|Program Files|Windows)',text):private.append(path.relative_to(HERE).as_posix())
        if path.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if link.startswith(('http:','https:','mailto:','#')):continue
                target=link.split('#',1)[0]
                if not (path.parent/target).exists():broken.append({'file':path.relative_to(HERE).as_posix(),'target':target})
        if path.suffix=='.py':
            tree=ast.parse(text,filename=path.name)
            if path.name in historical:
                first=tree.body[0];guards.append(isinstance(first,ast.If) and isinstance(first.body[0],ast.Raise))
    checks.update(no_private_host_paths=not private,all_relative_Markdown_links_resolve=not broken,
                  all_historical_entrypoints_guarded=len(guards)==len(historical) and all(guards))
    pkg=HERE.parents[1];actual={name:sha(pkg/'models/v2'/name) for name in manifest['core_STL_SHA256_before']}
    checks['actual_fixed_STL_SHA256_unchanged']=actual==manifest['core_STL_SHA256_before']==manifest['core_STL_SHA256_after']
    final=json.loads((HERE/'final-verification.json').read_text(encoding='utf-8'))
    checks['historical_GO_and_manufacturing_limits_preserved']=final['incremental_decision']=='GO' and final['strict_manufacturing_false_preserved'] is True and final['physical_print_false_preserved'] is True
    result={'passed':all(checks.values()),'checks':checks,'files':files,'private_path_files':private,'broken_links':broken,
        'actual_fixed_STL_SHA256':actual,'scope':'Import integrity only; no historical full QA rerun, geometry changes, slicing, render, Library transfer or publication action.'}
    if a.output:
        if a.output.exists():raise RuntimeError('Refusing to overwrite validation output')
        a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
