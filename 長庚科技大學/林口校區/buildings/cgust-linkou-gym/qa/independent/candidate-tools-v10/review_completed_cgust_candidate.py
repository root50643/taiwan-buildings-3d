"""Case-bound CGUST v10 frozen STL 66f0516f final audit of fresh frozen evidence.
All original numerical strict=false results remain false; every flag needs its
exact original-recorded-line proof. Unchanged Tianmu source/render checks follow.
"""
from pathlib import Path
import argparse,hashlib,json,sys
VIEWS={'front','rear','west','east','south','north','top','courtyard-gallery','courtyard-arcade'}
def require(v,m):
    if not v:raise RuntimeError(m)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--author',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists(),'Refuse existing review output');a.out.mkdir(parents=True)
    run=a.run.resolve();author=a.author.resolve();frozen=run/'frozen';tracked={};case_source=Path(__file__).with_name('inspect_flagged_cgust_mode.py');case_hash=sha(case_source);report={'case_review_source_sha256':case_hash,'passed':False,'bounded_verification_passed':False,'original_numerical_strict_passed':False,'review_source_sha256':sha(__file__),'optimization_level':sys.flags.optimize,'scope':'Required complete fresh original-STL gates, source and saved scene reproduction, nine images, and exact publication bindings. Finite rays/sections do not establish global minimum thickness or a physical-print guarantee.'}
    def key(p):
        p=Path(p).resolve()
        if p.is_relative_to(run):return 'run/'+str(p.relative_to(run))
        if p.is_relative_to(author):return 'author/'+str(p.relative_to(author))
        raise RuntimeError('Unscoped evidence path')
    def track(p,digest=None):
        p=Path(p);h=sha(p);k=key(p);r={'bytes':p.stat().st_size,'sha256':h};require(digest is None or h==digest,'Hash differs: '+k);require(k not in tracked or tracked[k]==r,'Evidence changed during read: '+k);tracked[k]=r;return h
    def read(p):
        raw=Path(p).read_bytes();require(hashlib.sha256(raw).hexdigest()==track(p),'JSON changed during read');return json.loads(raw)
    def yes(d,keys,label):require(all(d.get(k) is True for k in keys),label+' required true fields absent/false')
    try:
        execution=read(run/'independent-execution-summary.json');yes(execution,['completed','all_frozen_inputs_and_tools_unchanged'],'Execution');require(execution['strict_passed'] is False,'Execution ledger must not invent strict acceptance');track(run/'independent-runner.py',execution['runner_sha256'])
        version=execution['version'];stl=frozen/'models'/version/'model.stl';stlhash=track(stl,execution['stl_sha256']);report.update(version=version,stl_sha256=stlhash)
        freeze=read(run/'author-freeze-manifest.json');require(freeze['version']==version and freeze['stl_sha256']==stlhash,'Freeze identity mismatch')
        for row in freeze['files']:
            for root in [author,frozen]:require((root/row['path']).stat().st_size==row['bytes'],'Frozen size mismatch');track(root/row['path'],row['sha256'])
        verify=read(run/'author-freeze-validation.json');yes(verify,['passed'],'Freeze validation');track(run/'author-freeze-manifest.json',verify['manifest_sha256'])
        require(verify['file_count']==len(freeze['files']),'Freeze count mismatch')
        sys.path[:0]=[str(frozen/'qa/tools'),str(frozen/'qa/verification'),str(frozen/'qa/render-tools')]
        from inspect_flagged_cgust_mode import inspect_mode
        from qa_common import checker_inventory
        from png_exact_compare import compare as compare_png,SANITIZE_TEXT_KEYS
        names={'source-stl-reproduction','source-scene-state-reproduction','saved-blend-nine-rerenders','public-png-metadata-cleanup'}|{m+'-'+s for m in ['normal','optimized'] for s in ['standard','exact-intersections','intersection-controls','dense-evidence','exact-recorded-rays']}
        ledger=execution['executions'];require(len(ledger)==len(names) and {r['name'] for r in ledger}==names,'Missing, repeated or unexpected execution stage')
        for row in ledger:require(type(row['returncode']) is int and row['returncode']==(1 if row['name'] in ['normal-standard','optimized-standard'] else 0) and row['finished'] is True,'Stage failed/incomplete: '+row['name']);track(run/row['log_file'],row['log_sha256'])
        inventory=checker_inventory();modes={}
        for mode,opt in [('normal',0),('optimized',1)]:
            base=run/'geometry'/mode;stage_map={'standard':'standard','intersections':'exact-intersections','intersection-controls':'intersection-controls','dense-evidence':'dense-evidence'};exits={k:next(r['returncode'] for r in ledger if r['name']==mode+'-'+v) for k,v in stage_map.items()}
            modes[mode]=inspect_mode(base,stlhash,execution['expected_longest_mm'],inventory,opt,exits,stl)
            for p in base.rglob('*'):
                if p.is_file():track(p)
            denseaudit=read(base/'dense-evidence.json');yes(denseaudit,['passed','completed','all_original_numerical_flag_predicates_recomputed','all_expected_flag_indices_and_reasons_match'],'Dense coverage/predicate audit');require(denseaudit['original_numerical_strict_passed'] is False and denseaudit['stl_sha256']==stlhash and denseaudit['source_sha256']==sha(frozen/'qa/tools/validate_dense_evidence.py') and denseaudit['dense_report_sha256']==sha(base/'standard/dense/dense-check.json'),'Dense audit binding mismatch')
            raw=read(base/'standard/raw/raw-mesh-check.json');sec=read(base/'standard/sections/section-check.json');dense=read(base/'standard/dense/dense-check.json');inter=read(base/'intersections.json')
            require(sec['pitch_mm']==.2 and sec['offsets_from_z_min_mm']==[.031,.071,.137] and sec['opening_reference_width_mm']==.8 and sec['per_polygon_loss_limit']==.01,'Section policy mismatch')
            require(dense['samples_per_original_face']==10 and dense['minimum_required_chord_mm']==.8 and dense['origin_outside_offset_mm']==1e-5,'Dense policy mismatch')
            modes[mode].update(layers=sec['sampled_layers'],polygons=sec['original_polygon_count'],rays=dense['samples'],flags=dense['flagged_sample_count'],short_rays=dense['under_0p8mm_count'],minimum_numerical_first_chord_mm=dense['minimum_first_chord_mm'],candidate_pairs=inter['broad_phase']['candidate_pairs_checked'],bad_pairs=inter['bad_pair_count'])
        require(modes['normal']==modes['optimized'],'Normal and optimized scientific evidence differ');report['geometry']=modes
        source=execution['source_rebuild'];require(source['returncode']==0 and source['original_stl_bitwise_identical'] is True and source['original_color_regions_bitwise_identical'] is True,'Source reconstruction failed')
        for name in ['model.stl','color-regions.json']:track(run/'reproduction/models'/version/name,track(frozen/'models'/version/name))
        scene=read(run/'source-scene-reproduction/source-scene-audit.json');yes(scene,['passed','all_nine_camera_definitions_match','exact_scene_state_matches','source_unchanged','original_blend_unchanged','manifest_unchanged'],'Source scene');require(scene['state_difference_count']==0 and scene['state_differences']==[] and set(scene['camera_definition_checks'])==VIEWS and all(v is True for v in scene['camera_definition_checks'].values()),'Source camera/state differs')
        track(frozen/'qa/render-tools/compare_source_scene.py',scene['checker_sha256']);track(frozen/'models'/version/'render_preview.py',scene['source_sha256']);track(frozen/'models'/version/'scene.blend',scene['original_blend_sha256']);track(frozen/'previews'/version/'render-manifest.json',scene['manifest_sha256']);track(run/'reproduction/models'/version/'scene.blend',scene['generated_blend_sha256'])
        require(read(run/'source-scene-reproduction/source-scene-state.json')==read(run/'source-scene-reproduction/original-scene-state.json'),'Actual serialized saved scenes differ')
        renderdir=run/'saved-blend-rerenders';render=read(renderdir/'blend-rerender-audit.json');yes(render,['passed','strict_passed'],'Saved scene/rerender');require(render['inspect_only'] is False and len(render['views'])==9 and {r['view'] for r in render['views']}==VIEWS and all(v is True for v in render['checks'].values()),'Incomplete render proof')
        required_render_checks=set(['all_nine_decoded_rgba_bytes_identical', 'all_nine_metadata_only_cleanups_proved', 'all_nine_nonremoved_metadata_identical', 'cycles_cpu_renderer', 'denoising_disabled', 'exact_world_directed_triangle_multiset_matches', 'exactly_64_samples', 'fixed_nonanimated_render_seed', 'frozen_image_resolution', 'inspector_source_unchanged', 'manifest_blend_binding_matches', 'manifest_render_policy_matches', 'manifest_per_view_projection_lens_policy_matches', 'mesh_normally_visible', 'mesh_stl_hash_matches', 'millimetre_units', 'no_animation_or_drivers', 'no_compositor_or_sequencer', 'no_environment_image_textures', 'no_external_photo_images', 'no_hidden_replacement_mesh', 'no_image_textures', 'no_light_shader_nodes', 'no_modifiers', 'no_object_constraints', 'no_shader_node_groups', 'no_shape_keys', 'no_unexpected_renderable_objects', 'no_view_layer_material_overrides', 'one_camera_two_suns', 'one_cpu_render_thread', 'original_blend_unchanged', 'original_manifest_unchanged', 'original_stl_unchanged', 'original_triangle_count_matches', 'png_comparator_source_unchanged', 'saved_initial_camera_matches_front', 'scene_stl_hash_matches']);require(set(render['checks'])==required_render_checks,'Required render flags missing or unexpected')
        for field,p in [('source_sha256',frozen/'qa/render-tools/inspect_and_rerender_blend.py'),('png_comparator_source_sha256',frozen/'qa/render-tools/png_exact_compare.py'),('original_blend_sha256',frozen/'models'/version/'scene.blend'),('original_stl_sha256',stl),('original_manifest_sha256',frozen/'previews'/version/'render-manifest.json')]:track(p,render[field])
        public=run/'public-previews';pm=read(public/'render-manifest.json');cleanup=read(public/'metadata-cleanup-binding.json');yes(cleanup,['passed'],'Metadata cleanup');require(set(pm['views'])==set(cleanup['views'])==VIEWS and pm['stl_sha256']==cleanup['stl_sha256']==stlhash and set(cleanup['removal_whitelist'])==set(SANITIZE_TEXT_KEYS),'Public view/cleanup policy mismatch')
        track(public/'render-manifest.json',cleanup['public_manifest_sha256']);track(frozen/'qa/render-tools/sanitize_png_previews.py',cleanup['batch_source_sha256']);track(frozen/'qa/render-tools/png_exact_compare.py',cleanup['sanitizer_sha256']);track(frozen/'previews'/version/'render-manifest.json',cleanup['source_manifest_sha256']);images={}
        for row in render['views']:
            name=row['view'];m=pm['views'][name];c=cleanup['views'][name];require(row['posed_world_directed_geometry_matches_stl'] is True and c==row['original_metadata_cleanup'],'Per-view evaluated geometry or cleanup differs')
            track(public/(name+'.png'),m['sha256']);track(renderdir/'sanitized-original'/(name+'.png'),m['sha256']);track(frozen/'previews'/version/(name+'.png'),m['original_raw_png_sha256']);track(renderdir/(name+'.png'),row['rerendered_raw_png_sha256']);track(renderdir/'sanitized-rerender'/(name+'.png'),row['rerendered_metadata_cleanup']['sanitized_png_sha256'])
            comparison=compare_png(public/(name+'.png'),renderdir/'sanitized-rerender'/(name+'.png'),m['sha256']);yes(comparison,['passed','decoded_rgba_bytes_identical','all_nonvolatile_metadata_identical'],'Public vs rerender');require(comparison==row['sanitized_png_comparison'],'Recorded image comparison differs');require(m['decoded_rgba_sha256']==c['sanitized_rgba_sha256']==comparison['original_rgba_sha256']==comparison['rerendered_rgba_sha256'],'RGBA binding mismatch')
            images[name]={'public_png_sha256':m['sha256'],'original_raw_png_sha256':m['original_raw_png_sha256'],'decoded_rgba_sha256':m['decoded_rgba_sha256'],'decoded_rgba_bytes_identical':True,'all_surviving_metadata_identical':True,'cleaned_file_bitwise_identical':comparison['whole_png_file_bytes_identical'],'raw_file_bitwise_identical':row['raw_png_files_bitwise_identical']}
        for logical,r in tracked.items():
            k,rel=logical.split('/',1);p=(run if k=='run' else author)/rel;require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Evidence changed during review: '+logical)
        require(sha(__file__)==report['review_source_sha256'] and sha(case_source)==case_hash,'Reviewer changed during run');report.update(passed=True,bounded_verification_passed=True,original_numerical_strict_passed=False,images=images,source_stl_bitwise_identical=True,source_color_regions_bitwise_identical=True,source_saved_scene_state_matches=True,scene_state_verification_scope=scene['scope'],all_read_evidence_unchanged=True,evidence_inventory=tracked)
    except Exception as e:report.update(error_type=type(e).__name__,error=str(e))
    (a.out/'review-result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':report['passed'],'error':report.get('error'),'tracked_files':len(tracked)}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
