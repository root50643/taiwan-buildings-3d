"""Read-only publication delta checks; no geometry, slicing or historical QA rerun."""
from pathlib import Path
import argparse,csv,hashlib,io,json,re,subprocess

MODEL=Path(__file__).resolve().parents[1]
PREFIX='正修科技大學/校本部/buildings/csu-administration-03'
BASE='c4c23d900b4b55f9e0905f235af023687fa5cc14'
REVIEW='54c4ad2a30e6600e85fbf054d4c384f9e5304748'
INDEXES=['README.md','model-packages.json','正修科技大學/README.md','正修科技大學/校本部/README.md',
 '全國大專院校/README.md','全國大專院校/coverage.json','全國大專院校/institutions.json','全國大專院校/institutions.csv']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise SystemExit('Choose a new output; historical validation is never overwritten')
    root=Path(subprocess.check_output(['git','-C',str(MODEL),'rev-parse','--show-toplevel']).decode().strip())
    def git(*a):return subprocess.check_output(['git','-C',str(root),*a])
    def old(path,ref=BASE):return git('show',ref+':'+path)
    def load(path):return json.loads((root/path).read_bytes())
    def prior(path):return json.loads(old(path))
    def sha(data):return hashlib.sha256(data).hexdigest()
    checks={}
    for ref in [BASE,REVIEW]:subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',ref,'HEAD'],check=True)
    baseline=[];changed=[]
    for raw in git('ls-tree','-r','-z',REVIEW,'--',PREFIX).split(b'\0'):
        if not raw:continue
        meta,name=raw.split(b'\t',1);path=name.decode();data=old(path,REVIEW);current=(root/path).read_bytes()
        same=data==current
        baseline.append({'path':path[len(PREFIX)+1:],'review_bytes':len(data),'review_sha256':sha(data),'current_bytes':len(current),'current_sha256':sha(current),'identical':same})
        if not same:changed.append(path[len(PREFIX)+1:])
    checks['all_377_reviewed_files_present']=len(baseline)==377
    checks['only_reviewed_README_release_status_changed']=changed==['README.md']
    checks['generator_parameters_STL_scene_Gcode_previews_unchanged']=all(x['identical'] for x in baseline if x['path']!='README.md')
    changes=git('diff','-z','--name-only',BASE,'--').decode().strip('\0').split('\0')
    untracked=git('ls-files','--others','--exclude-standard','-z').decode().strip('\0').split('\0')
    outside=sorted(p for p in changes+untracked if p and not p.startswith(PREFIX+'/'))
    checks['only_eight_indexes_outside_new_package']=outside==sorted(INDEXES)
    checks['new_package_absent_at_base']=not git('ls-tree','-r','-z',BASE,'--',PREFIX)
    mp=load('model-packages.json');cmp=prior('model-packages.json')
    expect=json.loads(json.dumps(cmp))
    expect.update(total_packages=496,new_campus_packages=425,higher_education_model_packages=464,updated='2026-10-18')
    expect['schools']['正修科技大學']['count']=2
    expect['schools']['正修科技大學']['cover']=PREFIX+'/previews/v2/front-three-quarter.png'
    checks['model_package_index_only_expected_fields_changed']=mp==expect
    checks['package_count_equations_and_school_counts']=(sum(x['count'] for x in mp['schools'].values())==425 and len(mp['schools'])==106 and mp['total_packages']==mp['legacy_packages']+425==496 and mp['higher_education_model_packages']==425+38+1==464 and mp['non_higher_education_model_packages']==32 and mp['all_repository_institutions_with_models']==107 and mp['schools']['嘉南藥理大學']['count']==2 and mp['schools']['國立中山大學']['count']==4)
    cov=load('全國大專院校/coverage.json');pcov=prior('全國大專院校/coverage.json')
    allowed={'newly_published_model_packages','all_repository_model_packages','all_repository_higher_education_model_packages','model_counts_updated_date','counting_scope','count_equations'}
    checks['coverage_only_expected_fields_changed']=all(cov[k]==v for k,v in pcov.items() if k not in allowed) and set(cov)==set(pcov)
    checks['coverage_counts_match_catalog']=(cov['newly_published_model_packages']==425 and cov['all_repository_model_packages']==496 and cov['all_repository_higher_education_model_packages']==464 and cov['all_repository_institutions_with_at_least_one_model']==107 and cov['institutions_without_published_models']==51)
    inst=load('全國大專院校/institutions.json');pinst=prior('全國大專院校/institutions.json')
    pairs=list(zip(inst,pinst));changes_inst=[a['institution_id'] for a,b in pairs if a!=b]
    target=next(x for x in inst if x['institution_id']=='moe-1037');ptarget=next(x for x in pinst if x['institution_id']=='moe-1037')
    fields={'modeling_status','validation_status','publication_status','published_model_package_count'}
    checks['institution_JSON_only_CSU_four_fields_changed']=(len(inst)==len(pinst)==158 and changes_inst==['moe-1037'] and {k for k in target if target[k]!=ptarget[k]}==fields and target['published_model_package_count']==2)
    raw=(root/'全國大專院校/institutions.csv').read_bytes();praw=old('全國大專院校/institutions.csv')
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))));prows=list(csv.DictReader(io.StringIO(praw.decode('utf-8-sig'))))
    cr=next(x for x in rows if x['institution_id']=='moe-1037');pcr=next(x for x in prows if x['institution_id']=='moe-1037')
    checks['CSV_BOM_other_rows_and_CSU_statuses_preserved']=(raw.startswith(b'\xef\xbb\xbf')==praw.startswith(b'\xef\xbb\xbf') and len(rows)==len(prows)==158 and [a['institution_id'] for a,b in zip(rows,prows) if a!=b]==['moe-1037'] and {k for k in cr if cr[k]!=pcr[k]}==fields-{'published_model_package_count'} and all(cr[k]==target[k] for k in fields-{'published_model_package_count'}) and [s for s in raw.splitlines() if not s.startswith(b'moe-1037,')]==[s for s in praw.splitlines() if not s.startswith(b'moe-1037,')])
    broken=[]
    for p in [root/x for x in INDEXES if x.endswith('.md')]+[MODEL/'README.md',MODEL/'PUBLICATION.md']:
        for link in re.findall(r'\]\(([^\n)]+)\)',p.read_text(encoding='utf8')):
            link=link.strip('<>').split('#')[0]
            if not link or '://' in link:continue
            target_path=p.parent/link
            if target_path==MODEL/'qa/publication-incremental/validation.json':continue
            if not target_path.exists():broken.append({'file':p.relative_to(root).as_posix(),'link':link})
    checks['release_entry_local_links_exist']=not broken
    checks['no_workflow_CI_configured']=not (root/'.github/workflows').exists()
    record={'scope':'Publication index, fixed-input and link validation only; NOT full manufacturing, slicing, source research or physical print QA',
      'integration_base':BASE,'independently_reviewed_commit':REVIEW,'package_path':PREFIX,
      'counts':{'total':496,'campus':464,'schools':107,'new_catalog':425,'CSU':2},
      'checks':checks,'passed':all(checks.values()),'strict_manufacturing_passed':False,'physical_print_performed':False,
      'reviewed_existing_files':baseline,'outside_package_changes':outside,'broken_links':broken,
      'ci_note':'No repository workflow configuration; local validation must not be described as CI.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'checks':checks,'passed':record['passed'],'reviewed_files':len(baseline),'outside_package_changes':len(outside)},ensure_ascii=False,indent=2))
    raise SystemExit(0 if record['passed'] else 1)

if __name__=='__main__':main()
