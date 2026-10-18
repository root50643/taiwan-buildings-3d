"""Bind current v2 files to actual retained QA; never promotes failed gates."""
from pathlib import Path
import argparse,gzip,hashlib,json,sys
sys.path.insert(0,str(Path(__file__).with_name('qa')))
from qa_common import sha256,write_json


def read(p):return json.loads(p.read_text(encoding='utf-8'))
def require(v,m):
    if not v:raise RuntimeError(m)


def main():
    p=argparse.ArgumentParser();p.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    root=a.package_root;tools=root/'source/qa';records=[];checks={};report={'passed':False,'strict_geometry_passed':False,'evidence_integrity_passed':False}
    def bound_sources(report,names):
        inv=report['checker_sources_sha256']
        return all(inv.get(name)==sha256(tools/name) for name in names)
    try:
        body=root/'models/v2/parts/body.stl';roof=root/'models/v2/parts/roof.stl'
        require(sha256(roof)==sha256(root/'models/v1/parts/roof.stl'),'Roof changed; reuse invalid')
        checks['roof_reuse_same_actual_stl_sha256']=True
        strict=[]
        for name,stl,base in [('body',body,root/'qa/v2/body'),('roof',roof,root/'qa/v1/roof')]:
            digest=sha256(stl);raw=read(base/'raw/raw-mesh-check.json');sec=read(base/'sections/section-check.json')
            exact=read(base/'exact-contacts.json');man=read(base/'manufacturing/manufacturing-check.json')
            require(all(r['stl_sha256']==digest for r in [raw,sec,exact,man]),name+' report bound to another STL')
            require(bound_sources(raw,['check_raw_mesh.py','qa_common.py']),name+' raw checker changed')
            require(bound_sources(sec,['check_sections.py','qa_common.py']),name+' section checker changed')
            require(bound_sources(man,['check_manufacturing.py','check_sections.py','qa_common.py']),name+' manufacturing checker changed')
            require(exact['tools']['source_sha256']==sha256(tools/'check_original_intersections.py'),name+' exact checker changed')
            require(exact['completed'] and exact['input_unchanged_during_check'] and exact['broad_phase']['all_bbox_overlapping_pairs_completed'],name+' exact completion missing')
            for fk,hk in [('detail_file','detail_sha256'),('failure_file','failure_sha256')]:
                require(sha256(base/'sections'/sec[fk])==sec[hk],name+' section evidence changed')
            for file,item in man['artifacts'].items():
                path=base/'manufacturing'/file;require(path.stat().st_size==item['bytes'] and sha256(path)==item['sha256'],name+' manufacturing evidence changed')
            contact=exact['all_actual_intersections'];path=base/contact['path'];require(sha256(path)==contact['sha256'],name+' exact contacts changed')
            with gzip.open(path,'rt') as f:actual_contacts=sum(1 for _ in f)
            require(actual_contacts==contact['record_count']==exact['actual_intersection_pair_count'],name+' contact count differs')
            strict.append(all(r['passed'] for r in [raw,sec,exact,man]))
            records.append({'part':name,'stl_sha256':digest,'qa_directory':base.relative_to(root).as_posix(),
                            'topology_passed':raw['passed'],'exact_contacts_passed':exact['passed'],'sections_passed':sec['passed'],
                            'manufacturing_passed':man['passed'],'manufacturing_checks':man['checks'],
                            'normal_short_samples':man['normal_chords']['short_sample_count'],
                            'normal_ambiguous_samples':man['normal_chords']['flagged_sample_count'],
                            'layer_support_flags':man['layer_support']['flagged_layers']})
        checks['actual_geometry_reports_and_all_detail_hashes_current']=True
        c=read(root/'qa/v1/manufacturing-controls/manufacturing-controls.json')
        require(c['passed'] and bound_sources(c,['check_manufacturing_controls.py','check_manufacturing.py','check_sections.py','check_raw_mesh.py','qa_common.py']),'Manufacturing control source changed')
        c=read(root/'qa/v1/intersection-controls/controls-summary.json')
        require(c['passed'] and c['checker_sha256']==sha256(tools/'check_original_intersections.py') and c['controls_source_sha256']==sha256(tools/'check_intersection_controls.py'),'Exact control source changed')
        checks['positive_negative_control_dependency_hashes_unchanged']=True
        slices=[]
        for name,stl,base in [('body',body,root/'qa/v2/slicing/body'),('roof',roof,root/'qa/v1/slicing/roof')]:
            r=read(base/'slice-summary.json');audit=read(base/'gcode-audit.json')
            require(r['passed'] and r['input_sha256']==r['input_sha256_after']==sha256(stl)==audit['input_stl_sha256'],name+' slice input differs')
            require(r['profile_sha256']==sha256(tools/r['profile']),name+' slicing profile differs')
            require(r['gcode_sha256']==audit['gcode_sha256']==sha256(base/r['gcode']),name+' Gcode changed')
            for file,item in r['artifact_inventory'].items():require(sha256(base/file)==item['sha256'] and (base/file).stat().st_size==item['bytes'],name+' slice artifact changed')
            slices.append({'part':name,'qa_directory':base.relative_to(root).as_posix(),'execution_passed':r['passed'],
                           'support_extrusion_segments':audit['support_extrusion_segments'],'bridge_infill_segments':audit['bridge_infill_segments'],
                           'overhang_perimeter_segments':audit['positive_extrusion_segment_counts_by_type'].get('Overhang perimeter',0)})
        checks['actual_slice_inputs_profiles_gcode_and_audits_current']=True
        v2=read(root/'qa/v2/body/part-qa-summary.json')
        require(v2['checks']['stl_unchanged'] and v2['checks']['checker_sources_unchanged'],'v2 run input/source binding failed')
        require(bound_sources(v2,list(v2['checker_sources_sha256'])),'A recorded v2 checker source changed')
        checks['v2_full_recorded_checker_inventory_current']=True
        display=read(root/'qa/v2/assembly-display/raw-mesh-check.json')
        require(display['passed'] and display['stl_sha256']==sha256(root/'models/v2/assembly.stl'),'Assembly display raw report differs')
        checks['assembly_display_raw_solid_binding_current']=True
        report.update(evidence_integrity_passed=all(checks.values()),strict_geometry_passed=all(strict),
                      passed=all(checks.values()) and all(strict),parts=records,slices=slices)
    except Exception as error:report.update(error_type=type(error).__name__,error=str(error))
    report.update(checks=checks,validator_source_sha256=sha256(__file__),
        retained_initial_v1_body_checks=read(root/'qa/v1/body/part-qa-summary.json')['checks'],
        retained_initial_v1_roof_checks=read(root/'qa/v1/roof/part-qa-summary.json')['checks'],
        interpretation='Evidence-integrity checks validate bindings only. They do not waive original failed thin/normal/support gates. v1 wrapper full-folder inventory changed while unrelated slicing tools were added; historical failure remains. Reuse depends explicitly on unchanged algorithms and actual STL hashes. No physical print or machine validation.')
    dest=root/'qa/v2/final-evidence-validation.json';require(not dest.exists(),'Refusing to overwrite validation')
    write_json(dest,report);print(json.dumps(report,indent=2));return 0 if report['evidence_integrity_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
