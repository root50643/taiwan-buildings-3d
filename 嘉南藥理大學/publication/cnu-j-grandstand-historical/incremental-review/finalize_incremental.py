"""Seal incremental review outputs without modifying the candidate or remote."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parent / 'cnu-j-incremental-review-7cf0563a0685.zip'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    prov = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
    author = json.loads((ROOT / 'author-delivery.json').read_text(encoding='utf-8-sig'))
    identity = json.loads((ROOT / 'identity-profile-gcode.json').read_text(encoding='utf-8'))
    archive_results = json.loads((ROOT / 'package-and-archive.json').read_text(encoding='utf-8'))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    original = Path(prov['source_directory'])
    rows = []
    for entry in prov['files']:
        row = {'path': entry['path'], 'fixed_sha256': entry['sha256']}
        for label, base in [('original', original), ('review_copy', ROOT / 'candidate')]:
            row[label + '_sha256'] = sha((base / entry['path']).read_bytes())
            assert row[label + '_sha256'] == entry['sha256'], (label, entry['path'])
        rows.append(row)
    assert len(rows) == 145
    repository = Path(author['local_checkout'])
    head = subprocess.run(['git', f'--git-dir={repository / ".git"}', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    assert head.returncode == 0 and head.stdout.strip() == prov['fixed_commit']
    save('no-change-check.json', {'checked_at_utc': now, 'candidate_commit': prov['fixed_commit'],
        'original_head': head.stdout.strip(), 'files_checked': len(rows),
        'all_original_and_review_copy_fixed_hashes_unchanged': True, 'files': rows,
        'scope': 'Rehashed all 145 package files against fixed commit capture. No write to original or remote; no forensic claim about unrelated host or remote history.'})
    expected_prefix = author['package_path'] + '/'
    assert len(prov['diff_from_base']) == 145
    assert all(x['status'] == 'A' and x['path'].startswith(expected_prefix) for x in prov['diff_from_base'])
    instructions = []
    for rel in ['README.md', '嘉南藥理大學/README.md', '嘉南藥理大學/校本部/README.md']:
        data = (ROOT / 'repo-context' / rel).read_bytes()
        assert (repository / rel).read_bytes() == data
        instructions.append({'file': rel, 'sha256': sha(data)})
    applicable_agent_files = [str(q / 'AGENTS.md') for q in [original, *original.parents] if (q / 'AGENTS.md').is_file()]
    assert not applicable_agent_files
    save('scope-check.json', {'candidate_commit': prov['fixed_commit'], 'base_commit': prov['base_commit'],
        '145_added_files_only_in_target_package': True, 'public_count_or_other_building_edits': False,
        'instructions_read_and_current_hashes_checked': instructions,
        'applicable_AGENTS_files_found': applicable_agent_files, 'remote_or_publication_actions_performed': False})
    print_rows = []
    for part, qty in [('main_body', 1), ('roof', 1), ('column', 10), ('mast_brace_frame', 10)]:
        row = next(r for r in identity['fixed_print_stls'] if r['path'] == f'parts/{part}-print.stl')
        print_rows.append({**row, 'quantity': qty})
    summary = {
        'candidate_commit': prov['fixed_commit'], 'base_commit': prov['base_commit'],
        'previous_full_review_candidate': prov['old_candidate_commit'], 'reviewed_at_utc': now,
        'decision': 'GO_UNDER_EXISTING_FIXED_STL_CONDITIONS',
        'mandatory_publication_blockers': [], 'environment_or_file_transfer_blockers': [],
        'original_main_automatic_bridge_route_accepted': False,
        'unconditional_physical_manufacturing_certification': False,
        'print_files': print_rows, 'unique_part_geometries': 4, 'physical_piece_count': 22,
        'package_file_count': 145, 'unchanged_old_files': 52, 'changed_old_text_seal_files': 6,
        'added_files': 87, 'removed_old_files': 0,
        'geometry_scene_sources_and_all_previews_byte_unchanged': True,
        'profile_sha256': identity['reviewed_profile_sha256'],
        'profile_byte_identical_to_previous_independent_correction': True,
        'actual_profile_changes': identity['actual_setting_changes_from_original'],
        'actual_gcode_sha256': identity['actual_gcode']['sha256'],
        'actual_gcode_only_first_generated_time_line_differs': True,
        'gcode_canonical_sha256': identity['actual_gcode']['canonical_sha256'],
        'gcode_compared_lines': identity['actual_gcode']['line_count'],
        'evidence_integration': {'source_files': 69, 'integrated_files': 73,
            'byte_identical_files': 52, 'strict_path_role_substitution_only_files': 17,
            'numeric_boolean_null_JSON_leaves_preserved': 898548,
            'original_failures_and_580_restricted_points_preserved': True},
        'documentation': {'valid_local_links': 42, 'referenced_report_hashes_verified': 14,
            'current_guidance_supersedes_original_main_pass': True,
            '100_percent_scale_15_percent_infill_clear': True,
            'finite_sampling_not_claimed_as_complete_validation': True},
        'backup': {'bytes': archive_results['archive_bytes'], 'sha256': archive_results['archive_sha256'],
            'ZIP_entries_CRC_checked': 149, 'outer_manifest_files_verified': 148,
            'package_files_against_fixed_git_blobs': 145,
            'already_materialized_official_ZIP_bytes_match': True,
            'retained_Library_receipt': {'id': 'libfile_03684283aedc8191900c89f2971270aa', 'version': 1},
            'fresh_Library_download_or_native_metadata_query': False},
        'conditions_remaining': [
            'Machine-specific reslice: actual short-axis platform bridge direction and retained removable bridge support; angle number alone is insufficient after rotation/slicer change.',
            'Approximately 8.3mm internal bridging capability, or revised infill/solid layers with reslice and inspection.',
            'Staged lateral support fragmentation before assembly; finite point/ray/dogleg evidence is not complete tool, captured-block, other-support, adhesion or force validation. Unsafe access requires revised/compatible soluble support and reslice.',
            '50 clearance adhesive positioning joints; clean sockets/elephant foot, dry-align, use compatible gap-filling glue and jig. Nominal53.4mm versus estimated natural seating53.25mm are not measured fit.',
            'No physical print, support/brim removal, dry fit, glue/bending/transport strength tests. Broad canopy warping and fine-frame handling risks remain.',
            'Historical photograph composite and at least25% dimensional uncertainty; not2026 current-state precision survey.'
        ],
        'work_not_repeated': ['Full geometry/self-intersection/pair collisions/interface measurements', 'Generator rebuild', 'Scene rerender', 'Photo acquisition', 'Slicing', 'Bridge/support numerical recomputation', 'Physical tests'],
        'all_145_original_files_unchanged_during_review': True,
        'original_candidate_or_remote_writes': False, 'publication_performed': False,
        'report': 'INCREMENTAL-REVIEW.md'
    }
    save('review-summary.json', summary)
    manifests = []
    excluded = {'candidate', '__pycache__'}
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT)
        if not path.is_file() or set(rel.parts) & excluded or path.name in {'delivery.json', 'delivery-manifest.json'}:
            continue
        data = path.read_bytes()
        manifests.append({'path': rel.as_posix(), 'bytes': len(data), 'sha256': sha(data)})
    # Local report links must work before sealing. The candidate snapshot is
    # deliberately not duplicated in the audit ZIP; the original145-file ZIP is
    # independently bound by package-and-archive.json and retained Library v1.
    for rel in ['INCREMENTAL-REVIEW.md', 'docs-audit/DOCUMENT-REVIEW.md', 'evidence-audit/EVIDENCE-REVIEW.md']:
        for target in re.findall(r'\]\(([^)]+)\)', (ROOT / rel).read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                assert ((ROOT / rel).parent / target.split('#')[0]).exists(), (rel, target)
    save('delivery-manifest.json', {'candidate_commit': prov['fixed_commit'], 'created_at_utc': now,
        'payload_files': len(manifests), 'payload_bytes': sum(r['bytes'] for r in manifests), 'files': manifests,
        'scope': 'Incremental review only: reports, scripts, raw comparison results, copied repo instructions. The 145-file candidate snapshot is held locally and in the independently verified author ZIP; not duplicated here. No raw G-code, source photos, raw HTML or Git database.'})
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for r in manifests:
            z.write(ROOT / r['path'], ROOT.name + '/' + r['path'])
        z.write(ROOT / 'delivery-manifest.json', ROOT.name + '/delivery-manifest.json')
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        assert len(z.infolist()) == len(manifests) + 1
        for r in manifests:
            assert sha(z.read(ROOT.name + '/' + r['path'])) == r['sha256']
    delivery = {'candidate_commit': prov['fixed_commit'], 'decision': summary['decision'],
        'mandatory_publication_blockers': [], 'completed_at_utc': now,
        'report': str(ROOT / 'INCREMENTAL-REVIEW.md'), 'summary': str(ROOT / 'review-summary.json'),
        'archive': str(ARCHIVE), 'archive_bytes': ARCHIVE.stat().st_size,
        'archive_sha256': sha(ARCHIVE.read_bytes()), 'archive_files': len(manifests) + 1,
        'ZIP_CRC_and_each_payload_SHA_verified': True, 'all_145_original_files_unchanged': True,
        'original_or_remote_write_or_publication': False, 'remaining_environment_blockers': []}
    save('delivery.json', delivery)
    print(json.dumps(delivery, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
