"""Incremental documentation check; no STL repair, slicing or printer execution.

Uses retained 76681 identities and reads actual raw-STL lines/G-code. Historical
QA flags stay untouched. Rebuilds only in a fresh, validated package-local folder.
"""
from pathlib import Path
import ast,hashlib,json,math,re,subprocess,sys,tempfile
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa/documentation-revision-1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean_ast(path):
    tree=ast.parse(path.read_text(encoding='utf8'))
    for node in ast.walk(tree):
        body=getattr(node,'body',None)
        if isinstance(body,list) and body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):body.pop(0)
    return ast.dump(tree,include_attributes=False)

def gcode(path):
    pos=dict(x=0.,y=0.,z=0.);e=0.;xyz_abs=True;e_abs=True;role='Unknown';width=height=None
    counts={};filament={};overhang=[];support_sizes=set()
    for line_no,line in enumerate(path.read_text(encoding='utf8').splitlines(),1):
        if line.startswith(';TYPE:'):role=line[6:].strip()
        if line.startswith(';WIDTH:'):width=float(line[7:])
        if line.startswith(';HEIGHT:'):height=float(line[8:])
        code=line.split(';',1)[0].strip()
        if not code:continue
        cmd=code.split()[0];vals={m.group(1):float(m.group(2)) for m in re.finditer(r'([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',code)}
        if cmd=='G90':xyz_abs=True;continue
        if cmd=='G91':xyz_abs=False;continue
        if cmd=='M82':e_abs=True;continue
        if cmd=='M83':e_abs=False;continue
        if cmd=='G92':
            for axis in pos:
                if axis.upper() in vals:pos[axis]=vals[axis.upper()]
            if 'E' in vals:e=vals['E']
            continue
        if cmd not in ['G0','G1']:continue
        before=pos.copy();nex=pos.copy()
        for axis in pos:
            if axis.upper() in vals:nex[axis]=vals[axis.upper()] if xyz_abs else pos[axis]+vals[axis.upper()]
        ne=e if 'E' not in vals else vals['E'] if e_abs else e+vals['E'];de=ne-e
        length=math.dist(list(before.values()),list(nex.values()))
        if de>1e-9 and length>1e-9:
            counts[role]=counts.get(role,0)+1;filament[role]=filament.get(role,0.)+de
            if role.startswith('Support'):support_sizes.add((width,height))
            if role=='Overhang perimeter':
                def model(v):return [v['x']-110,v['y']-110,v['z']]
                overhang.append({'line':line_no,'start_model_mm':model(before),'end_model_mm':model(nex),'length_mm':length,'WIDTH_mm':width,'HEIGHT_mm':height})
        pos=nex;e=ne
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'support_segments':counts.get('Support material',0),'interface_segments':counts.get('Support material interface',0),'support_and_interface_filament_mm':sum(v for k,v in filament.items() if k.startswith('Support')),'support_width_height_pairs_mm':sorted(support_sizes),'overhang_perimeter':overhang,'role_counts':counts}

def main():
    frozen=json.loads((Q/'frozen-inputs-at-76681.json').read_text(encoding='utf8'));checks={};changes=[]
    for row in frozen['files']:
        p=ROOT/row['path']
        if not p.exists() or sha(p)!=row['sha256']:changes.append(row['path'])
    metadata=json.loads((Q/'png-metadata-redaction.json').read_text(encoding='utf8'))
    expected_png={f'previews/{v}/{name}.png' for v in ['v1','v2'] for name in ['exploded-two-parts','front-elevation','front-three-quarter','left-elevation','rear-elevation','rear-three-quarter','right-elevation','top']}
    checks['png_metadata_change_scope_exactly16_previews']={r['path'] for r in metadata['files']}==expected_png
    frozen_by_path={r['path']:r for r in frozen['files']}
    checks['png_metadata_original_current_and_pixels_bound']=all(r['original_sha256']==frozen_by_path[r['path']]['sha256'] and r['delivered_sha256']==sha(ROOT/r['path']) and r['idat_sha256_before']==r['idat_sha256_after'] and r['pixels_sha256_before']==r['pixels_sha256_after'] for r in metadata['files'])
    checks['only_expected_existing_files_changed']=set(changes)==set(frozen['allowed_modified_existing_files'])|expected_png
    p=json.loads((ROOT/'parameters.json').read_text(encoding='utf8'));old=json.loads((Q/'parameters-at-76681.json').read_text(encoding='utf8'))
    allowed=json.loads(json.dumps(p));allowed.pop('parameter_semantics',None);allowed['entrance']['door_recess_depth']=old['entrance']['door_recess_depth'];allowed['manufacturing']['maximum_shallow_facade_recess']=old['manufacturing']['maximum_shallow_facade_recess']
    checks['only_statement_fields_changed_in_parameters']=allowed==old and p['entrance']['door_recess_depth']==p['manufacturing']['maximum_shallow_facade_recess']==0.65
    checks['corrected_audit_docstring_only_ast_identical']=clean_ast(ROOT/'source/qa_audit_gcode.py')==clean_ast(Q/'legacy-source/qa_audit_gcode.py')
    checks['fixed_geometry_generator_unchanged']=sha(ROOT/'source/build_model.py')==next(x['sha256'] for x in frozen['files'] if x['path']=='source/build_model.py')
    required={'parts/body.stl':'e388dff1247334ec5e79530e45a1b7e5e85d1a630aff0a9d6d53720f1362ee6c','parts/roof.stl':'7d1c8840ee11649ec4c57984ff1a0cc2c2a3916f37fc21888e7ead0f631fed04','assembly.stl':'6d3a8796831cd83bd7e012664dd8f094b6e700998031e71db38567fc1ecff416'}
    fixed={name:sha(ROOT/'models/v2'/name) for name in required};checks['all_three_fixed_stl_sha_unchanged']=fixed==required
    mesh=trimesh.load_mesh(ROOT/'models/v2/parts/body.stl',process=False)
    origins=np.array([[0,-40,15.5],[0,-40,22.5]],float);directions=np.array([[0,1,0],[0,1,0]],float)
    loc,ids,_=mesh.ray.intersects_location(origins,directions,multiple_hits=True)
    ys=[sorted(set(float(x[1]) for x in loc[ids==i])) for i in [0,1]]
    depth=ys[0][0]-ys[1][0]
    line={'raw_body_sha256':fixed['parts/body.stl'],'rays':{'origins_mm':origins.tolist(),'directions':directions.tolist(),'intersection_y_mm':ys},'door_back_y':ys[0][0],'front_above_door_y':ys[1][0],'door_depth_mm':depth,'continuous_material_behind_door_mm':ys[0][-1]-ys[0][0]}
    checks['raw_door_depth_matches_independent_measurement']=abs(depth-0.6500015258789062)<1e-9
    slices=[gcode(ROOT/'qa/v2/slicing/body-auto45/QA-NOT-MACHINE-READY.gcode'),gcode(ROOT/'qa/v2/slicing/body/QA-NOT-MACHINE-READY.gcode')]
    checks['both_actual_door_top_paths_length_16_6']=all(len(x['overhang_perimeter'])==1 and abs(x['overhang_perimeter'][0]['length_mm']-16.6)<1e-8 for x in slices)
    expected_start=np.array([-8.3,-28.975,20.2]);expected_end=np.array([8.3,-28.975,20.2])
    checks['actual_path_coordinates_width_height_match']=all(np.allclose(x['overhang_perimeter'][0]['start_model_mm'],expected_start,atol=1e-9,rtol=0) and np.allclose(x['overhang_perimeter'][0]['end_model_mm'],expected_end,atol=1e-9,rtol=0) and x['overhang_perimeter'][0]['WIDTH_mm']==0.4 and x['overhang_perimeter'][0]['HEIGHT_mm']==0.4 for x in slices)
    auto=slices[0];checks['actual_auto45_support_interface_counts_match']=auto['support_segments']==20930 and auto['interface_segments']==61223 and abs(auto['support_and_interface_filament_mm']-7273.39394)<1e-5
    rebuilt=[]
    with tempfile.TemporaryDirectory(prefix='.doc-rebuild-',dir=Q) as work:
        assert Path(work).resolve().parent==Q.resolve()
        proc=subprocess.run([sys.executable,'-B',str(ROOT/'source/build_model.py'),'--output-dir',work],capture_output=True)
        checks['current_statement_parameters_rebuild_exit_zero']=proc.returncode==0
        for name in required:
            dest=Path(work)/name;rebuilt.append({'file':name,'sha256':sha(dest) if dest.exists() else None,'bytes_equal':dest.exists() and dest.read_bytes()==(ROOT/'models/v2'/name).read_bytes()})
        checks['current_statement_parameters_rebuild_identical']=all(x['bytes_equal'] for x in rebuilt)
        if proc.returncode==0:(Q/'current-parameters-rebuild-report.json').write_bytes((Path(work)/'build-report.json').read_bytes())
    strict=json.loads((ROOT/'qa/v2/final-evidence-validation.json').read_text(encoding='utf8'))['strict_geometry_passed']
    checks['strict_manufacturing_false_retained']=strict is False
    report={'documentation_revision_verified':all(checks.values()),'baseline_commit':frozen['baseline_commit'],'geometry_changed':not checks['all_three_fixed_stl_sha_unchanged'],'strict_manufacturing_passed':strict,'physical_print_performed':False,'current_parameter_sha256':sha(ROOT/'parameters.json'),'historical_parameter_sha256':sha(Q/'parameters-at-76681.json'),'validator_source_sha256':sha(Path(__file__)),'changed_existing_files':changes,'fixed_stl_sha256':fixed,'door_raw_line_measurement':line,'actual_gcode_readback':slices,'current_parameters_rebuild':rebuilt,'png_metadata_mapping_sha256':sha(Q/'png-metadata-redaction.json'),'checks':checks,'limitations':'Incremental documentation/identity check only. Recess depth is not overhang span. No print, support removal, sharp-eave, warpage, glue or tolerance validation. Original geometry flags and historical hashes preserved.'}
    (Q/'incremental-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'documentation_revision_verified':report['documentation_revision_verified'],'door_depth_mm':depth,'checks':checks},indent=2));raise SystemExit(0 if all(checks.values()) else 1)
if __name__=='__main__':main()
