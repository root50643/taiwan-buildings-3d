if __name__ == '__main__':
    raise SystemExit('Historical provenance only; use reproduce.py in a fresh output directory. Do not overwrite archived evidence.')

from pathlib import Path
import hashlib,json,re,shutil,zipfile

ROOT=Path(__file__).resolve().parent
P=Path('<MODEL_ROOT>')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identity=json.loads((ROOT/'identity-and-author-receipt.json').read_text(encoding='utf-8'))
rebuild=json.loads((ROOT/'independent-rebuild.json').read_text(encoding='utf-8'))
scene=json.loads((ROOT/'independent-scene-check.json').read_text(encoding='utf-8'))
geo=json.loads((ROOT/'agent-geometry/independent-csu-geometry.json').read_text(encoding='utf-8'))
man=json.loads((ROOT/'agent-manufacturing/independent-csu-manufacturing.json').read_text(encoding='utf-8'))
now={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file()};before=identity['candidate_snapshot_before']
changed=sorted(k for k in set(now)|set(before) if now.get(k)!=before.get(k))
broken=[]
for dest in re.findall(r'\]\(([^)]+)\)',(ROOT/'INDEPENDENT-CSU-REVIEW.zh-TW.md').read_text(encoding='utf-8')):
    if not dest.startswith(('http:','https:')) and not (ROOT/dest).exists():broken.append(dest)
result={'fixed_commit':identity['commit'],'decision':'CONDITIONAL_GO_representative_model_two_print_parts','source_or_geometry_mandatory_revision_identified':False,'mandatory_documentation_correction':{'entrance_door_recess_actual_mm':man['actual_entrance_door_recess_depth_mm'],'declared_unused_depth_parameter_mm':0.45,'action':'Correct door depth to about 0.65mm and distinguish ordinary 0.4mm relief; clarify parameters not used by generator. Keep geometry fixed unless intentionally creating another candidate.'},'required_door_lintel_condition':{'actual_overhang_length_mm':16.6,'position_model_mm':[[-8.3,-28.975,20.2],[8.3,-28.975,20.2]],'auto45_has_actual_support':True,'no_support_baseline_is_not_clearance':True,'physical_sag_and_removal_unverified':True},'STL_SHA256':{n:sha(P/'models/v2'/n) for n in ['parts/body.stl','parts/roof.stl','assembly.stl']},'tracked_package_file_count':identity['tracked_package_files'],'all_files_match_fixed_commit':identity['all_package_bytes_match_commit'],'read_only_snapshot_unchanged':not changed,'candidate_changed_paths':changed,'all_three_rebuilt_STLs_byte_identical':all(r['byte_identical'] for r in rebuild['files']),'scene_two_print_meshes_exact_STL_geometry':scene['all_part_meshes_identical'],'all_nine_preview_SHA_match':all(r['matches'] for r in scene['preview_manifest_hash_checks']),'one_independent_render_created':True,'independent_full_exact_pairs':{'body':73993,'roof':208},'illegal_triangle_contacts':0,'joint_positive_volume_overlap_mm3':0,'joint_exact_contact_area_mm2':1120,'manual_center_and_glue_required':True,'actual_auto45_support_segments':man['actual_support_segment_count'],'actual_auto45_support_filament_mm':man['actual_support_filament_mm'],'global_minimum_wall_proven':False,'all_supports_tool_access_or_forces_proven':False,'physical_print_or_glue_test':False,'reference_Gcode_machine_ready':False,'re_sliced_in_review':False,'candidate_mutation_push_publish_credentials_change':False,'report_local_links_broken':broken,'Library_receipt_matches_expected':identity['receipt_identity_matches_expected'],'Library_download_done_by_reviewer':False,'remaining_execution_blockers':[],'preserved_limits':['One 03A/B/C set, two separate flat-bottom print files; assembly is display only.','Photo-based relative estimates, hidden lower rear areas bounded by observed mass, symbolic relief/fill simplifications and uncertain photo dates; no 2026-current claim.','Original strict manufacturing false, 6 coplanar ray ambiguities, 71 true tapered roof-edge short chords and v1 failures retained.','Actual external supports need fragmentation, tool, removal and surface-quality confirmation; finite sampled routes do not prove global clearance.','200mm base plus brim/warp and machine/material settings need operator confirmation.','Flat butt joint has no XY/yaw registration, glue thickness or tested bonding strength.']}
(ROOT/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert not changed and not broken and result['all_three_rebuilt_STLs_byte_identical']
assert result['STL_SHA256']['parts/body.stl']=='e388dff1247334ec5e79530e45a1b7e5e85d1a630aff0a9d6d53720f1362ee6c'
assert result['STL_SHA256']['parts/roof.stl']=='7d1c8840ee11649ec4c57984ff1a0cc2c2a3916f37fc21888e7ead0f631fed04'
helpers=ROOT/'verification-helpers';helpers.mkdir(exist_ok=True)
old=ROOT.parent/'agent-geometry'
for name in ['independent_raw_topology.py','independent_contact_check.py']:
    shutil.copyfile(old/name,helpers/name)
files=[ROOT/n for n in ['INDEPENDENT-CSU-REVIEW.zh-TW.md','identity-and-author-receipt.json','independent-rebuild.json','rebuild.stdout.log','rebuild.stderr.log','verify_identity_rebuild.py','independent_scene_check.py','independent-scene-check.json','independent-front.png','finalize_review.py','final-verification.json']]
for folder in ['agent-source','agent-geometry','agent-manufacturing','verification-helpers']:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in ('.md','.py','.json','.log','.txt') and '__pycache__' not in p.parts)
manifest=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))]
(ROOT/'evidence-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=ROOT/'csu-administration-independent-review-76681c5.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for r in manifest:z.write(ROOT/r['path'],r['path'])
    z.write(ROOT/'evidence-manifest.json','evidence-manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'] for r in manifest)
delivery={'report':str(ROOT/'INDEPENDENT-CSU-REVIEW.zh-TW.md'),'evidence_archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'entries':len(manifest)+1,'CRC_and_all_manifest_entries_verified':True,'original_candidate_models_or_Gcode_or_third_party_media_included':False,'independent_model_render_included':True,'Library_upload_or_download_by_reviewer':False,'push_publish_performed':False}
(ROOT/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(delivery,ensure_ascii=False,indent=2))
