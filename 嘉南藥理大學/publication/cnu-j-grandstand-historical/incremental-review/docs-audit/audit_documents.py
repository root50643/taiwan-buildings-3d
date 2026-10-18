from pathlib import Path
import datetime, hashlib, json, re, subprocess
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
HERE.mkdir(parents=True, exist_ok=True)
REPO = Path(r'${REPOSITORY}')
PREFIX = '嘉南藥理大學/校本部/buildings/cnu-j-grandstand-historical/'
PACKAGE = REPO / PREFIX
COMMIT = '7cf0563a06858137f51751600348a35198c8f6f2'
OLD = '3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a'
GIT = ['git', '--git-dir=' + str(REPO / '.git'), '-c', 'core.quotePath=false']

def sha(b): return hashlib.sha256(b).hexdigest()
def git(*args):
    p = subprocess.run(GIT + list(args), capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8', 'replace'))
    return p.stdout

inputs = [
    'README.md', 'qa-summary.json', 'qa/README.md',
    'qa/manufacturing-review/README.md', 'qa/history/README.md',
    'manufacturing/reviewed-support/README.md',
    'manufacturing/reviewed-support/main-short-axis-support.ini',
    'manufacturing/reviewed-support/profile-diff.json',
    'manufacturing/reviewed-support/integration-reslice.json',
    'manufacturing/reviewed-support/slice_reviewed_parts.py',
    'qa/manufacturing-review/diagnostic-main-support.ini',
    'qa/independent-support-review/INTEGRATION-README.md',
    'qa/independent-support-review/INDEPENDENT-REVIEW.md',
    'qa/independent-support-review/slicing-support-audit/SLICING-SUPPORT-REVIEW.md',
    'qa/independent-support-review/slicing-support-audit/REVIEW-ONLY-main-short-axis-support.ini',
    'qa/revision-delta-review.json',
]
rows=[]
snapshot={}
for rel in inputs:
    b=(PACKAGE/rel).read_bytes()
    snapshot[rel]=b
    rows.append({'path':rel, 'bytes':len(b), 'sha256':sha(b),
                 'matches_fixed_commit_bytes':b==git('show', COMMIT+':'+PREFIX+rel)})

head=git('rev-parse','HEAD').decode().strip()
patch=git('diff','--no-ext-diff','--unified=3',OLD,COMMIT,'--',
          PREFIX+'README.md', PREFIX+'qa-summary.json', PREFIX+'qa/manufacturing-review/README.md')
(HERE/'public-document-diff.patch').write_bytes(patch)

def ini(b):
    out={}
    for line in b.decode('utf-8-sig').splitlines():
        line=line.strip()
        if not line or line.startswith(('#',';')) or '=' not in line: continue
        k,v=line.split('=',1); out[k.strip()]=v.strip()
    return out
old_config=ini(snapshot['qa/manufacturing-review/diagnostic-main-support.ini'])
new_config=ini(snapshot['manufacturing/reviewed-support/main-short-axis-support.ini'])
delta={k:{'old':old_config.get(k),'new':new_config.get(k)}
       for k in sorted(old_config.keys()|new_config.keys()) if old_config.get(k)!=new_config.get(k)}
profile_reference=snapshot['qa/independent-support-review/slicing-support-audit/REVIEW-ONLY-main-short-axis-support.ini']
profile_result={'actual_config_delta':delta,
    'exactly_required_two_changes':delta=={'bridge_angle':{'old':'0','new':'90'},'dont_support_bridges':{'old':'1','new':'0'}},
    'actual_profile_matches_integrated_independent_reference_bytes':snapshot['manufacturing/reviewed-support/main-short-axis-support.ini']==profile_reference,
    'actual_profile_sha256':sha(snapshot['manufacturing/reviewed-support/main-short-axis-support.ini']),
    'selected_actual_settings':{k:new_config.get(k) for k in ['bridge_angle','dont_support_bridges','support_material','support_material_auto','fill_density','fill_pattern','nozzle_diameter','layer_height','first_layer_height','perimeters','extrusion_width','bed_shape','brim_width','start_gcode','end_gcode']}}

links=[]
for p in sorted(PACKAGE.rglob('*.md')):
    txt=p.read_text(encoding='utf-8-sig')
    for n,line in enumerate(txt.splitlines(),1):
        for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)',line):
            target=match.group(1).strip().strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',target) or target.startswith('#'): continue
            target=unquote(target.split('#',1)[0])
            resolved=(p.parent/target).resolve()
            links.append({'source':p.relative_to(PACKAGE).as_posix(),'line':n,'target':target,'exists':resolved.exists()})

summary=json.loads(snapshot['qa-summary.json'])
bindings=[]
for rel,expected in summary['report_sha256'].items():
    p=PACKAGE/rel
    actual=sha(p.read_bytes()) if p.is_file() else None
    bindings.append({'path':rel,'expected_sha256':expected,'actual_sha256':actual,'matches':actual==expected})

fixed={
 'main_body-print.stl':'64205a0515ec83e40e56a2f855a256556490a1d759481741cef177d42b0b133c',
 'roof-print.stl':'dbb9dfc7850219f8d40213cfb6c0cd944c1f30225dec2f6f3ae358370a9166cb',
 'column-print.stl':'010e3512e0b420d9f40ae1ad7679314cfd841a931aa30a4d6e9ae05a8dd169da',
 'mast_brace_frame-print.stl':'a0cb933ab1bdf6a26ccc20b573a1ea9a5f8a22df93868f6395885c8be3d80cef'}
stls=[{'path':'parts/'+name,'expected_sha256':expected,'actual_sha256':sha((PACKAGE/'parts'/name).read_bytes()),
       'matches':sha((PACKAGE/'parts'/name).read_bytes())==expected} for name,expected in fixed.items()]

criteria=[
 {'topic':'Original main route remains rejected; exit 0 is insufficient','locations':['README.md:3','README.md:38','qa/manufacturing-review/README.md:3','qa/manufacturing-review/README.md:21','qa-summary.json:10','manufacturing/reviewed-support/README.md:3'],'manual_result':'retained'},
 {'topic':'Actual short-axis bridges plus retained support; angle is orientation specific; machine reslice required','locations':['README.md:38','README.md:46','qa/manufacturing-review/README.md:23','manufacturing/reviewed-support/README.md:8','manufacturing/reviewed-support/README.md:16'],'manual_result':'retained'},
 {'topic':'100% scale is distinct from 15% infill; actual reference configuration disclosed','locations':['README.md:36','qa/manufacturing-review/README.md:37','manufacturing/reviewed-support/README.md:13','qa-summary.json:38'],'manual_result':'retained'},
 {'topic':'8.224913 mm body and 8.036027 mm roof internal bridges retained; 2.600011 mm roof socket is not maximum','locations':['README.md:40','qa/manufacturing-review/README.md:25','manufacturing/reviewed-support/README.md:36','qa-summary.json:19'],'manual_result':'retained'},
 {'topic':'Old/new support samples separated; all 580 restricted flags retained; finite checks do not prove full removability','locations':['README.md:42','qa/manufacturing-review/README.md:29','qa/manufacturing-review/README.md:31','qa/manufacturing-review/README.md:33','manufacturing/reviewed-support/README.md:40','qa-summary.json:61'],'manual_result':'retained'},
 {'topic':'Staged side removal before assembly; no straight-forward block extraction; revise support if access unsafe','locations':['README.md:30','README.md:42','qa/manufacturing-review/README.md:33','manufacturing/reviewed-support/README.md:44'],'manual_result':'retained'},
 {'topic':'50 clearance adhesive positioning interfaces, not snap fits; jig and gap-filling adhesive; analytical 53.25 mm seating','locations':['README.md:15','README.md:30','README.md:32','qa/manufacturing-review/README.md:13','qa/manufacturing-review/README.md:17','manufacturing/reviewed-support/README.md:49','qa-summary.json:73'],'manual_result':'retained'},
 {'topic':'Four unique geometries / 22 physical pieces; overview is not print file','locations':['README.md:19','README.md:21','manufacturing/reviewed-support/README.md:21','qa-summary.json:4'],'manual_result':'retained'},
 {'topic':'No physical print, support removal, dry fit or adhesive/transport strength proof; roof warping and thin frames','locations':['README.md:3','README.md:50','qa/manufacturing-review/README.md:43','manufacturing/reviewed-support/README.md:54','qa-summary.json:17'],'manual_result':'retained'},
 {'topic':'Historical reports and raw passes scoped to old candidate; present printing guidance supersedes them','locations':['qa/history/README.md:3','qa/manufacturing-review/README.md:5','qa/independent-support-review/INTEGRATION-README.md:3','qa/independent-support-review/INTEGRATION-README.md:20','qa-summary.json:27'],'manual_result':'clear precedence; no manufacturing acceptance inferred from geometry pass'},
 {'topic':'2006/2010/2012 plus undated historical source composite, not 2026 measured current state','locations':['README.md:3','README.md:15','README.md:68','qa-summary.json:23'],'manual_result':'retained'},
]
unchanged=all((PACKAGE/rel).read_bytes()==b for rel,b in snapshot.items())
result={
 'scope':'Final incremental document/configuration audit only; no rendering, no reslice, no repeated unchanged full geometry, no physical tests; manual semantic reading plus narrow mechanical binding/link checks.',
 'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'fixed_candidate_commit':COMMIT,'old_independently_reviewed_candidate_commit':OLD,'observed_head':head,
 'decision':'GO_WITH_EXISTING_FIXED_STL_AND_MANUFACTURING_CONDITIONS',
 'required_publication_blockers':[],
 'manual_semantic_criteria':criteria,
 'input_bindings':rows,
 'all_input_documents_match_fixed_commit':all(r['matches_fixed_commit_bytes'] for r in rows),
 'configuration_check':profile_result,
 'four_fixed_print_stls':stls,
 'markdown_links':links,'broken_local_markdown_links':[r for r in links if not r['exists']],
 'qa_summary_report_sha_bindings':bindings,
 'all_qa_summary_report_sha_bindings_match':all(r['matches'] for r in bindings),
 'public_document_diff_sha256':sha(patch),
 'reviewed_inputs_unchanged_after_audit':unchanged,
 'tool_attempt_record':[{'action':'Two parallel read-only document/git batches','outcome':'CreateProcess rejected before process creation: exec-server transport disconnected; no file absence inferred; later small read-only retries succeeded.'}],
 'limitations':['The support and bridge numeric analyses are carried forward through unchanged inputs and exact toolpath evidence, not recomputed by this document audit.','The integrated old report still names the old commit and old review-only location; INTEGRATION-README expressly labels it historical, and current README plus reviewed-support entry carry the new route.','The frozen qa-summary still states final parent incremental review was pending at author freeze; this report is subsequent evidence, not a change to that historical timestamped claim.']
}
assert head==COMMIT
assert result['all_input_documents_match_fixed_commit']
assert profile_result['exactly_required_two_changes']
assert profile_result['actual_profile_matches_integrated_independent_reference_bytes']
assert not result['broken_local_markdown_links']
assert result['all_qa_summary_report_sha_bindings_match']
assert all(r['matches'] for r in stls)
assert unchanged
(HERE/'document-audit-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'decision':result['decision'],'input_documents':len(rows),'local_markdown_links_checked':len(links),'broken_links':len(result['broken_local_markdown_links']),'report_sha_bindings':len(bindings),'configuration_delta':delta,'fixed_stls':len(stls),'blockers':[]},ensure_ascii=False,indent=2))
