"""AEUST v15 read-only source/author comparison and public preview binding."""
from pathlib import Path
import hashlib,json,copy
Q=Path(__file__).resolve().parents[1];R=Q/'final-v15-r1';F=R/'frozen';A=F/'qa/v15-full';I=R/'geometry';VIEWS={'front','rear','west','east','south','north','top','courtyard-gallery','courtyard-arcade'}
def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,d):require(not p.exists(),'Never replace evidence');p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
rows=[]
for mode in ['normal','optimized']:
 files=['standard/qa-summary.json','standard/raw/raw-mesh-check.json','standard/sections/section-check.json','standard/sections/section-details.json.gz','standard/sections/section-failures.json.gz','standard/dense/dense-check.json','standard/dense/dense-original.csv.xz','standard/dense/dense-flagged-samples.json.gz','standard/dense/dense-short-samples.json.gz','dense-evidence.json','intersections.json','intersections.json.contacts.jsonl.gz']
 for rel in files+['exact-recorded-rays/exact-recorded-ray-summary.json','exact-recorded-rays/exact-recorded-ray-details.jsonl.gz']:
  original=(F/'qa/v15-recorded-rays'/mode/Path(rel).name) if rel.startswith('exact-recorded-rays/') else A/mode/rel;ind=I/mode/rel;identical=original.read_bytes()==ind.read_bytes();exceptions=[]
  if not identical:
   a,b=read(original),read(ind)
   if rel=='intersections.json':exceptions=['elapsed_seconds'];a.pop('elapsed_seconds');b.pop('elapsed_seconds')
   elif rel=='exact-recorded-rays/exact-recorded-ray-summary.json':
    exceptions=['elapsed_seconds','input_and_tool_sha256.intersections_report'];a.pop('elapsed_seconds');b.pop('elapsed_seconds')
    require(a['input_and_tool_sha256'].pop('intersections_report')==sha(A/mode/'intersections.json') and b['input_and_tool_sha256'].pop('intersections_report')==sha(I/mode/'intersections.json'),'Exact summary is not bound to its own unchanged intersection report')
   else:raise RuntimeError('Unexpected author/independent byte difference '+mode+'/'+rel)
   require(a==b,'Unexpected scientific difference '+mode+'/'+rel)
  rows.append({'mode':mode,'logical_file':rel,'author_sha256':sha(original),'independent_sha256':sha(ind),'bitwise_identical':identical,'only_allowed_non_scientific_differences':exceptions,'scientific_evidence_identical':True})
write(R/'author-independent-science-comparison.json',{'passed':True,'stl_sha256':sha(F/'models/v15/model.stl'),'both_modes_all_scientific_evidence_identical':True,'original_producer_files_unchanged':True,'comparisons':rows,'scope':'Original producer files preserved in full. Only intersection execution elapsed_seconds, exact-diagnosis elapsed_seconds and their hash-bound intersection report references may differ; no numerical value, ray/flag record, exact contact/event, slice or predicate is rewritten.'})
s=read(F/'qa/source-review/final-v15/SOURCE-APPEARANCE-GO.json');pm=read(R/'public-previews/render-manifest.json');cleanup=R/'public-previews/metadata-cleanup-binding.json'
require(s['decision']=='SOURCE-APPEARANCE-GO' and s['revision']=='v15' and s['outstanding_source_appearance_blockers']==[] and s['public_safe'] is True,'Source appearance GO incomplete')
art=s['artifacts'];require(art['stl_sha256']==sha(F/'models/v15/model.stl') and art['blend_sha256']==sha(F/'models/v15/scene.blend'),'Source model identity differs')
require(art['original_render_manifest_sha256']==sha(F/'previews/v15/render-manifest.json') and art['render_source_sha256']==sha(F/'source/render_preview.py') and art['parameters_sha256']==sha(F/'parameters.json') and art['color_regions_sha256']==sha(F/'models/v15/color-regions.json') and art['build_source_sha256']==sha(F/'source/build_model.py'),'Source artifact binding differs')
require(s['checks']['all_nine_original_png_hashes_match_manifest'] is True and s['checks']['all_nine_images_individually_visually_reviewed'] is True and s['checks']['ordered_triangle_coordinates_exactly_match_original_stl'] is True,'Source source/scene review incomplete')
require(set(pm['views'])==VIEWS and {x['name'] for x in art['original_pngs']}==VIEWS and len(art['original_pngs'])==9,'Source/public view coverage differs')
require(sha(R/'public-previews/render-manifest.json')==sha(F/'qa/render-check/v15-author-preflight/sanitized-previews/render-manifest.json') and sha(cleanup)==sha(F/'qa/render-check/v15-author-preflight/sanitized-previews/metadata-cleanup-binding.json'),'Author and independent public manifest/metadata cleanup differs')
views={}
for row in art['original_pngs']:
 name=row['name'];p=R/'public-previews'/(name+'.png');author=F/'qa/render-check/v15-author-preflight/sanitized-previews'/(name+'.png');m=pm['views'][name]
 require(sha(p)==sha(author)==m['sha256'],'Source-bound public PNG differs '+name)
 require(row['rgba_sha256']==m['decoded_rgba_sha256'] and row['original_png_sha256']==m['original_raw_png_sha256']==sha(F/'previews/v15'/(name+'.png')),'Source raw/pixel identity differs '+name)
 require(row['pixel_dimensions']==[1000,780] and row['visually_reviewed'] is True and row['assessment']=='PASS_WITH_DISCLOSED_APPROXIMATIONS','Source view review incomplete '+name)
 views[name]={'public_png_sha256':sha(p),'original_raw_png_sha256':row['original_png_sha256'],'decoded_rgba_sha256':row['rgba_sha256'],'author_independent_public_files_bitwise_identical':True,'source_review_verdict':row['assessment'],'source_observation':row['observation']}
write(R/'source-appearance-binding.json',{'passed':True,'stl_sha256':sha(F/'models/v15/model.stl'),'source_review_sha256':sha(F/'qa/source-review/final-v15/SOURCE-APPEARANCE-GO.json'),'original_author_science_freeze_sha256':sha(F/'qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json'),'public_manifest_sha256':sha(R/'public-previews/render-manifest.json'),'metadata_cleanup_binding_sha256':sha(cleanup),'decision':s['decision'],'views':views,'scope':'Binds the early representative exterior source review to exact independently verified raw PNG, cleaned PNG and RGBA, STL, Blend, renderer, parameters, color regions and original build source. All dimensions are model-space estimates; source chronology, unknown surfaces, opaque original glass colors, local-axis view names, support requirements and unprinted status remain disclosed. The unchanged original author science freeze is separately bound.'})
print(json.dumps({'passed':True,'scientific_comparisons':len(rows),'source_review_views':len(views)}))

original_freeze=read(F/'qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json');adapter=read(R/'author-freeze-manifest.json')
require(adapter['original_author_manifest_path']=='qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json' and sha(F/adapter['original_author_manifest_path'])==adapter['original_author_manifest_sha256'] and sha(R/'author-freeze-manifest.json')==read(R/'author-freeze-validation.json')['manifest_sha256'],'Original author freeze differs')
require(adapter['version']==original_freeze['revision']=='v15' and len(adapter['files'])==len(original_freeze['files'])+1,'Freeze schema adapter count differs')
expected={k:v for k,v in original_freeze['files'].items()};actual={row['path']:{'bytes':row['bytes'],'sha256':row['sha256']} for row in adapter['files'] if row['path']!='qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json'}
require(expected==actual,'Freeze schema adapter changed any original member')
write(R/'original-freeze-adapter-binding.json',{'passed':True,'original_author_freeze_sha256':sha(F/'qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json'),'runner_adapter_sha256':sha(R/'author-freeze-manifest.json'),'original_members':len(expected),'runner_members':len(adapter['files']),'original_member_mapping_exact':True,'original_manifest_itself_frozen_as_additional_file':True,'no_original_member_omitted_or_rewritten':True})
