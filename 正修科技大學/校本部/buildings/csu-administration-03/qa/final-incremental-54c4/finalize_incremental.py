if __name__ == '__main__':
    raise SystemExit('Historical provenance only. This fixed-review script depends on the old snapshot and external receipts; do not rerun it against the published package or overwrite archived evidence.')

from pathlib import Path
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parent
P=Path('<MODEL_ROOT>')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((ROOT/'independent-incremental-evidence.json').read_text(encoding='utf-8'))
imports=json.loads((ROOT/'imported-evidence-crosscheck.json').read_text(encoding='utf-8'))
now={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file()};before=a['candidate_snapshot_before']
changed=sorted(n for n in set(now)|set(before) if now.get(n)!=before.get(n))
broken=[s for s in re.findall(r'\]\(([^)]+)\)',(ROOT/'FINAL-INCREMENTAL-REVIEW.zh-TW.md').read_text(encoding='utf-8')) if not s.startswith(('http:','https:')) and not(ROOT/s).exists()]
receipt_path=P.parents[4]/'library-backup/library-verification.json'
# Use explicit task receipt rather than relying on directory depth.
receipt_path=Path('<AUTHOR_TASK_ROOT>/library-backup/library-verification.json')
r=json.loads(receipt_path.read_text(encoding='utf-8'))
receipt_matches=r['candidate_commit']==a['fixed_commit'] and r['library_file_id']==a['author_Library_receipt']['library_file_id'] and r['version_number']==1 and r['size_bytes']==38615220 and r['sha256']=='63d0e0616f9661a76da0f49f6852fec60a7ab086a8be2ba8f45e3e0607372d82' and r['file_count']==382 and r['model_package_files']==377 and r['all_entries_size_sha256_crc_match'] and r['all_model_files_match_frozen_commit_git_blob_ids']
result={'fixed_commit':a['fixed_commit'],'baseline_commit':a['baseline_commit'],'incremental_decision':'GO','mandatory_publication_blockers':[],'previous_documentation_requirement_resolved':True,'whole_model_qualification':'Original conditional GO with manufacturing/assembly/machine-specific limits unchanged; not physical print approval.','tracked_package_files':a['current_tracked_file_count'],'all_tracked_bytes_match_commit':a['all_current_tracked_bytes_match_commit'],'modified_existing_files':len(a['modified_existing_files']),'added_files':len(a['added_files']),'removed_files':len(a['removed_files']),'outside_package_changed_paths':a['outside_package_changed_paths'],'candidate_snapshot_unchanged_during_review':not changed,'candidate_changed_during_review':changed,'original_STL_scene_Gcode_all_byte_identical':a['all_old_STL_scene_Gcode_byte_identical'],'generator_byte_identical':a['geometry_builder_byte_identical'],'only_expected_statement_parameter_changes':a['only_expected_statement_values_changed'],'all_three_current_parameter_rebuild_STLs_identical':all(v['current_parameter_rebuild_byte_identical'] for v in a['current_parameter_rebuild']),'all_16_PNG_same_IDAT_and_pixels_only_File_text_change':a['all_16_PNG_only_File_text_and_same_IDAT_pixels'],'audit_AST_unchanged_without_docstring':a['audit_algorithm_AST_unchanged_after_removing_module_docstring'],'imported_review_source_and_delivery_SHA_match':imports['all_original_and_delivered_SHA_bindings_match'],'imported_JSON_numeric_boolean_null_values_preserved':imports['all_JSON_scientific_numeric_bool_null_values_preserved'],'imported_Markdown_reports_exact_original_bytes':imports['all_imported_Markdown_reports_exact_original_bytes'],'author_14_incremental_checks_all_true':a['author_14_validation_checks_preserved_and_true'],'strict_manufacturing_false_preserved':a['author_strict_manufacturing_still_false'],'physical_print_false_preserved':a['author_physical_print_still_false'],'Library_author_receipt_matches':receipt_matches,'Library_author_receipt_SHA256':sha(receipt_path),'reviewer_Library_download_upload_performed':False,'new_full_geometry_or_slice_or_render_tests_performed':False,'candidate_mutation_push_publish_performed':False,'report_broken_local_links':broken,'remaining_execution_blockers':[]}
(ROOT/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert not changed and not broken and receipt_matches and result['all_three_current_parameter_rebuild_STLs_identical']
files=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in ('.md','.json','.py','.log') and not any(n in p.parts for n in ['current-parameter-rebuild-package','current-parameter-rebuilt','__pycache__']) and p.name not in ['evidence-manifest.json','delivery.json']]
manifest=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]
(ROOT/'evidence-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=ROOT/'csu-final-incremental-review-54c4ad2.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for row in manifest:z.write(ROOT/row['path'],row['path'])
    z.write(ROOT/'evidence-manifest.json','evidence-manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'] for row in manifest)
delivery={'report':str(ROOT/'FINAL-INCREMENTAL-REVIEW.zh-TW.md'),'evidence_archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'entries':len(manifest)+1,'CRC_and_manifest_verified':True,'original_model_Gcode_PNG_or_third_party_media_included':False,'Library_upload_or_download_by_reviewer':False,'published_or_pushed_by_reviewer':False}
(ROOT/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(delivery,ensure_ascii=False,indent=2))
