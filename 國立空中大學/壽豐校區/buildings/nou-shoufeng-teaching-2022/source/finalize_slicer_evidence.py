"""Verify delivered slicing evidence and bind final reproduction sources by SHA-256.
Run after run_slicer.py and inspect_gcode.py. No slicer or machine is controlled.
"""
from pathlib import Path
import argparse, hashlib, json

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=parser.parse_args()
    root=a.root;qa=root/'qa';summary=json.loads((qa/'slicer-summary.json').read_text(encoding='utf-8'))
    params=json.loads((root/'parameters.json').read_text(encoding='utf-8'))
    checks=[]
    for part in summary['parts']:
        model=next(v for v in params['parts'] if v['name']==part['part'])
        checks.append({'part':part['part'],'stl_matches':sha(root/'models'/model['stl'])==part['input_stl_sha256']==model['sha256'],
                       'gcode_matches':sha(qa/part['gcode'])==part['gcode_sha256'],
                       'log_matches':sha(qa/part['log'])==part['log_sha256'],
                       'preview_matches':sha(qa/part['path_preview'])==part['path_preview_sha256'],
                       'profile_matches':not part['embedded_profile_verification']['mismatches_against_qa_config'],
                       'interface_z_matches':part['planar_interface_verification']['primary_interface_z_matches_stl'],
                       'slab_transition_matches':part['planar_interface_verification']['slab_footprint_transition_confirmed']})
    oldroot=qa/'history'/'slicer-0.15mm'
    old=json.loads((oldroot/'slicer-summary.json').read_text(encoding='utf-8'))
    history=[]
    for part in old['parts']:
        history.append({'part':part['part'],'gcode_matches':sha(oldroot/part['gcode'])==part['gcode_sha256'],
                        'log_matches':sha(oldroot/part['log'])==part['log_sha256'],
                        'preview_matches':sha(oldroot/part['path_preview'])==part['path_preview_sha256']})
    sources={p.name:sha(p) for p in [root/'source'/'run_slicer.py',root/'source'/'inspect_gcode.py',Path(__file__).resolve()]}
    record={
        'scope':'Final delivered reproduction scripts and current immutable slicing evidence. Original executed slice commands remain in slicer-run-record.json.',
        'source_sha256':sources,'summary_sha256':sha(qa/'slicer-summary.json'),
        'run_record_sha256':sha(qa/'slicer-run-record.json'),'parameters_sha256':sha(root/'parameters.json'),
        'parameters_binding_matches':sha(root/'parameters.json')==summary['parameters_sha256'],
        'bundled_base_profile':'slicer/base-profile.ini','bundled_base_profile_sha256':sha(qa/'slicer'/'base-profile.ini'),
        'bundled_base_matches_executed_base_sha256':sha(qa/'slicer'/'base-profile.ini')==summary['base_config_sha256'],
        'final_profile':summary['qa_config'],'final_profile_sha256':sha(qa/summary['qa_config']),
        'final_profile_binding_matches':sha(qa/summary['qa_config'])==summary['qa_config_sha256'],
        'current_checks':checks,'all_current_evidence_matches':all(all(v for k,v in x.items() if k!='part') for x in checks),
        'history_0p15mm_summary_sha256':sha(oldroot/'slicer-summary.json'),
        'history_0p15mm_file_checks':history,
        'all_archived_0p15mm_evidence_matches':all(all(v for k,v in x.items() if k!='part') for x in history),
        'reproduction_commands':[
            'python source/run_slicer.py --slicer /path/to/prusa-slicer-console --work /path/to/isolated-writable-work --layer-height 0.20',
            'python source/inspect_gcode.py',
            'python source/finalize_slicer_evidence.py'],
        'dependencies':'PrusaSlicer 2.9.6; Python with numpy, scipy, Pillow, matplotlib. No other task files or externally stored base config are required.',
        'physical_validation':'No physical print, support-removal or fit test performed. G-code is QA ONLY, not machine-ready.'}
    (qa/'slicer-reproducibility.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
