"""Bind the additional auto-support slice and preserve audit metadata erratum."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).with_name('qa')))
from qa_common import sha256,write_json


def read(p):return json.loads(p.read_text())
def main():
    p=argparse.ArgumentParser();p.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    root=a.package_root;base=root/'qa/v2/slicing/body-auto45';original=read(base/'gcode-audit.json')
    corrected=read(base/'corrected-audit/gcode-audit.json');run=read(base/'slice-summary.json')
    profile=root/'source/qa'/run['profile'];body=root/'models/v2/parts/body.stl';gcode=base/run['gcode']
    unchanged_fields=['actual_extruding_segment_count','positive_extrusion_segment_counts_by_type','support_extrusion_segments',
                      'support_positive_filament_mm','bridge_infill_segments','layer_count_with_positive_xy_extrusion','per_layer']
    checks={'slice_and_both_audits_bound_to_actual_input':run['passed'] and run['input_sha256']==run['input_sha256_after']==original['input_stl_sha256']==corrected['input_stl_sha256']==sha256(body),
            'actual_gcode_unchanged':run['gcode_sha256']==original['gcode_sha256']==corrected['gcode_sha256']==sha256(gcode),
            'profile_current':run['profile_sha256']==sha256(profile),
            'original_slice_artifacts_unchanged':all(sha256(base/name)==item['sha256'] and (base/name).stat().st_size==item['bytes'] for name,item in run['artifact_inventory'].items()),
            'auto_support_enabled_and_threshold_45':all(corrected['support_related_embedded_config'].get(k)==v for k,v in [('support_material','1'),('support_material_auto','1'),('support_material_threshold','45')]),
            'corrected_audit_source_current':corrected['audit_source_sha256']==sha256(root/'source/qa_audit_gcode.py'),
            'all_original_motion_extrusion_measurements_unchanged':all(original[k]==corrected[k] for k in unchanged_fields)}
    report={'evidence_integrity_passed':all(checks.values()),'checks':checks,'input_stl_sha256':sha256(body),
            'original_audit':'qa/v2/slicing/body-auto45/gcode-audit.json','original_audit_sha256':sha256(base/'gcode-audit.json'),
            'corrected_audit':'qa/v2/slicing/body-auto45/corrected-audit/gcode-audit.json','corrected_audit_sha256':sha256(base/'corrected-audit/gcode-audit.json'),
            'gcode_sha256':sha256(gcode),'profile_sha256':sha256(profile),'validator_source_sha256':sha256(__file__),
            'support_extrusion_segments':corrected['support_extrusion_segments'],'support_positive_filament_mm':corrected['support_positive_filament_mm'],
            'support_extrusion_xy_bounds_mm':corrected['support_extrusion_xy_bounds_mm'],
            'support_extrusion_z_bounds_mm':corrected['support_extrusion_z_bounds_mm'],
            'erratum':'The initial inherited audit contained a hardcoded support-disabled limitation sentence. Its measurements and embedded config were correct, and it is retained. The corrected audit reads the actual embedded support state; every original motion/extrusion measurement is unchanged.',
            'interpretation':'Auto-support45 generated actual supports. The no-support baseline cannot establish support-free printability. Exterior relief is open to the outside, but physical support removal, adhesion, finish and assembly have not been tested. Generic Gcode must be re-sliced for the actual machine.'}
    dest=root/'qa/v2/slicing/auto-support-evidence-validation.json'
    if dest.exists():raise RuntimeError('Refusing to overwrite evidence')
    write_json(dest,report);print(json.dumps(report,indent=2));return 0 if report['evidence_integrity_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
