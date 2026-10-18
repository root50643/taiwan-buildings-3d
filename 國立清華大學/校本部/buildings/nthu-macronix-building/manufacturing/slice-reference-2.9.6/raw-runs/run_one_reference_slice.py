import datetime
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'slicing-work'
EXE = Path(r'<slicer-tool-workspace>\manufacturing-tools\PrusaSlicer-2.9.6\PrusaSlicer-2.9.6\prusa-slicer-console.exe')
SOURCE_PROFILE = Path(r'<slicer-tool-workspace>\slicer-review-solid-staging\geometry-review-0.4mm-0.15mm-solid-rectilinear-no-support.ini')
EXPECTED_MODEL = '6801f9c41c9fd986df4167523ec36195e715d6a38a680c09aff002cba1351b2a'
EXPECTED_SOURCE_PROFILE = '7c300f9ea4a193facecf8c88c8aee94da19630b79f5d1cfb56da204fb4966442'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert not WORK.exists(), 'Slicing-work must be a new directory; never overwrite prior run evidence.'
matches = [p for p in (ROOT / 'candidate-repo').rglob('model.stl')
           if p.parent.name == 'fill-hidden-gaps' and digest(p) == EXPECTED_MODEL]
assert len(matches) == 1, matches
INPUT = matches[0]
assert digest(SOURCE_PROFILE) == EXPECTED_SOURCE_PROFILE
WORK.mkdir()
shutil.copyfile(INPUT, WORK / 'input-model.stl')
shutil.copyfile(SOURCE_PROFILE, WORK / 'source-profile.ini')
for p in (ROOT / 'slicer-inventory-evidence').glob('prusa-*.txt'):
    shutil.copyfile(p, WORK / p.name)
overrides = {
    'support_material':'1',
    'support_material_auto':'1',
    'support_material_style':'snug',
    'support_material_threshold':'45',
    'support_material_with_sheath':'0',
    'support_material_closing_radius':'0.5',
}
source_text = SOURCE_PROFILE.read_text(encoding='utf-8')
seen = set()
lines = []
for line in source_text.splitlines():
    key = line.split(' = ', 1)[0]
    if key in overrides:
        line = key + ' = ' + overrides[key]
        seen.add(key)
    lines.append(line)
assert seen == set(overrides)
PROFILE = WORK / 'derived-single-material-snug-REFERENCE.ini'
PROFILE.write_text('\n'.join(lines)+'\n', encoding='utf-8')
GCODE = WORK / 'reference-NOT-MACHINE-READY.gcode'
PROJECT = WORK / 'reference-NOT-MACHINE-READY.3mf'
common = [str(EXE), '--datadir', str(WORK / 'cli-data'), '--load', str(PROFILE),
          '--threads', '2', '--center', '110,110']
report = {
    'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'purpose':'One actual reference slice of fixed hidden-fill variant; NOT machine-ready and not a physical print or removal demonstration.',
    'source_model':str(INPUT), 'source_model_sha256':digest(INPUT),
    'input_copy_sha256':digest(WORK / 'input-model.stl'),
    'source_profile':str(SOURCE_PROFILE), 'source_profile_sha256':digest(SOURCE_PROFILE),
    'derived_profile':str(PROFILE), 'derived_profile_sha256':digest(PROFILE),
    'overrides_only':overrides,
    'tool_exe':str(EXE), 'tool_exe_sha256':digest(EXE),
    'orientation':'Original Z-up base down, 100% scale; --center 110,110 translation only, no rotations.',
    'support_strategy':{
        'single_material_hard_supports':True,
        'support_from_buildplate_only':False,
        'reason_for_everywhere':'The entire model includes a 3 mm base, so buildplate-only support would not reach most architectural overhangs. Supports may start on the model base or ledges.',
        'auto':True, 'threshold_degrees_from_horizontal':45, 'style':'snug',
        'sheath':False,'closing_radius_mm':0.5,'top_contact_distance_mm':0.2,
        'xy_spacing':'50% of external perimeter width',
        'interface_layers':3,'interface_spacing_mm':0,'support_pattern':'rectilinear',
        'support_spacing_mm':2.5,
        'dont_support_bridges':True,
        'bridge_limitation':'Slicer-detected bridges are intentionally excluded from support; they require actual path and anchoring review and physical testing.'
    },
    'reference_equipment':{
        'bed_mm':[220,220], 'max_height_mm':200, 'nozzle_mm':0.4,
        'layer_mm':0.15,'first_layer_mm':0.15,'extrusion_width_mm':0.45,
        'perimeter_generator':'arachne','perimeters':3,'fill_density':'100%',
        'fill_pattern':'rectilinear','filament_type':'PLA','filament_diameter_mm':1.75,
        'temperature_C':200,'bed_temperature_C':0,
        'warning':'Inherited generic reference values only. No identified user printer, firmware, extrusion, temperature, adhesion, cooling or removal calibration. Do not send this G-code to hardware.'
    },
    'physical_print_performed':False,
    'geometry_changed':False,
    'runs':[]
}
report_path = WORK / 'slicer-run-summary.json'

def save_report():
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def run(action, args):
    entry={'action':action,'argv':args,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    report['runs'].append(entry)
    save_report()
    start=time.monotonic()
    proc=subprocess.run(args,capture_output=True,timeout=600)
    out=WORK/(action+'.stdout.log')
    err=WORK/(action+'.stderr.log')
    out.write_bytes(proc.stdout)
    err.write_bytes(proc.stderr)
    entry.update({'returncode':proc.returncode,'seconds':time.monotonic()-start,
                  'stdout':out.name,'stdout_sha256':digest(out),
                  'stderr':err.name,'stderr_sha256':digest(err)})
    save_report()
    print(json.dumps(entry,ensure_ascii=False),flush=True)
    return proc.returncode

save_report()
rc=run('slice',common+['--export-gcode','--output',str(GCODE),str(WORK/'input-model.stl')])
if rc==0:
    run('project-export',common+['--export-3mf','--output',str(PROJECT),str(WORK/'input-model.stl')])
report['source_model_sha256_after']=digest(INPUT)
report['input_copy_sha256_after']=digest(WORK/'input-model.stl')
report['outputs']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)}
                   for p in (GCODE,PROJECT) if p.exists()]
assert report['source_model_sha256_after']==EXPECTED_MODEL
assert report['input_copy_sha256_after']==EXPECTED_MODEL
save_report()
print(json.dumps({'summary':str(report_path),'outputs':report['outputs']},ensure_ascii=False,indent=2))
