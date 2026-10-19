"""Verify current evidence and create a local package inventory. No publishing.
Run after all QA tools and renders finish. No mesh repair, no assertions of print fit.
"""
from pathlib import Path
import json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text('utf-8'))
def main():
 excluded={x['path']:x for x in read('qa/diagnostic-gcode-exclusions.json')['files']}
 d=read('assembly.json');mh=sha(ROOT/'assembly.json');g=read('qa/v5-raw/mesh_qa.json');s=read('qa/final_slice_evidence.json');scene=read('qa/scene-independent-report.json');src=read('qa/source-correspondence-seal.json')
 assert g['manifest_sha256']==s['manifest_sha256']==mh
 assert g['assembly']['pass'] and len(g['assembly']['pairs'])==45
 assert len(d['parts'])==len(g['parts'])==len(s['parts'])==10
 for part,geo,sl in zip(d['parts'],g['parts'],s['parts']):
  h=sha(ROOT/part['stl']);assert h==part['sha256']==geo['sha256']==sl['input_sha256']
  assert part['id']==geo['id']==sl['id']
  assert geo['watertight'] and geo['winding_consistent'] and geo['components']==1 and geo['volume_mm3']>0
  assert not geo['degenerate_face_ids'] and not geo['duplicate_face_count'] and geo['triangle_contact_counts']['pass_no_non_topological_contact']
  assert sl['slice_success'] and sl['exit_code']==0
  folder=(ROOT/sl['source_report']).parent
  gp=folder/sl['gcode'];rel=gp.relative_to(ROOT).as_posix()
  if gp.exists():assert sha(gp)==sl['gcode_sha256']
  else:assert rel in excluded and excluded[rel]['sha256']==sl['gcode_sha256']
  assert sha(folder/sl['log'])==sl['log_sha256']
 assert scene['pass'] and scene['scene_sha256']==sha(ROOT/'scene.blend') and scene['assembly_manifest_sha256']==mh
 assert src['input_hash_checks_pass']
 for f in src['files']:assert sha(ROOT/f['file'])==f['sha256'],f['file']
 for f in read('previews/render-manifest.json'):assert sha(ROOT/'previews'/f['file'])==f['sha256'],f['file']
 broken=[]
 for f in ROOT.rglob('*.md'):
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',f.read_text('utf-8')):
   if target.startswith(('https:','http:','#','mailto:')):continue
   target=target.split('#')[0]
   if target and not (f.parent/target).exists():broken.append([f.relative_to(ROOT).as_posix(),target])
 assert not broken,broken
 private=[];png=[]
 for f in sorted(ROOT.rglob('*')):
  if not f.is_file() or f.name in ['PACKAGE-SHA256.json','package-integrity.json','metadata-scan.json']:continue
  b=f.read_bytes()
  if re.search(rb'(?i)[A-Z]:[\\/]Users[\\/]|Documents[\\/]Codex[\\/]|(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9]{16,}',b):private.append(f.relative_to(ROOT).as_posix())
  if f.suffix.lower()=='.png':
   im=Image.open(f);png.append({'file':f.relative_to(ROOT).as_posix(),'metadata_keys':sorted(im.info),'private_path_or_secret_pattern_hit':False})
 assert not private,private
 assert not list(ROOT.rglob('*.blend1'))
 assert not list(ROOT.rglob('*.jpg')) and not list(ROOT.rglob('*.jpeg')) and not list(ROOT.rglob('*.pdf'))
 meta={'private_path_or_secret_pattern_files':private,'png':png,'blend_uncompressed_binary_scanned':True,'scope':'All package files scanned for Windows user paths, private Codex workspace paths and common secret-token prefixes. PNG metadata and full uncompressed blend bytes included.','source_photo_or_pdf_files_in_package':False}
 (ROOT/'qa/metadata-scan.json').write_text(json.dumps(meta,indent=2)+'\n','utf-8')
 assets=sorted((ROOT/'models').glob('*.stl'))+[ROOT/'scene.blend']
 (ROOT/'SHA256SUMS').write_text(''.join(f'{sha(f)}  {f.relative_to(ROOT).as_posix()}\n' for f in assets),'utf-8')
 inventory={f.relative_to(ROOT).as_posix():sha(f) for f in sorted(ROOT.rglob('*')) if f.is_file() and f.name not in ['PACKAGE-SHA256.json','package-integrity.json']}
 (ROOT/'PACKAGE-SHA256.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n','utf-8')
 report={'status':'Independent conditional release for model/source/files and bounded digital slicing; physical support-free manufacturing NOT VERIFIED.','diagnostic_Gcode_publicly_distributed':False,'missing_diagnostics_bound_to_exclusion_manifest':True,'independent_review':'qa/independent-review/README.md','physical_print_or_trial_fit_verified':False,'four_nozzle_printing_verified':False,'physical_instances':10,'distinct_print_stl_types':8,'main_stls_including_nonprint_reference':9,'whole_assembly_bounds_mm':[216.59999465942383,167.20000314712524,43.0],'all_45_assembly_pairs_checked':True,'all_triangles_checked_for_non_topological_contact':True,'raw_geometry_flags_retained':{p['id']:p['raw_flags'] for p in g['parts'] if p['raw_flags']},'all_current_stls_bound_to_actual_slice':True,'scene_reopened_and_exact_stl_geometry_verified':True,'source_correspondence_input_hashes_match':True,'broken_relative_markdown_links':broken,'private_metadata_patterns':private,'assembly_sha256':mh,'scene_sha256':sha(ROOT/'scene.blend'),'package_manifest_sha256':sha(ROOT/'PACKAGE-SHA256.json'),'files_in_package_manifest':len(inventory),'package_bytes':sum((ROOT/n).stat().st_size for n in inventory)}
 (ROOT/'qa/package-integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
