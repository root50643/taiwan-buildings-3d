#!/usr/bin/env python3
"""Clean deterministic rebuilds and intentional-corruption controls.

Run with the unchanged parent model folder. Test artifacts stay in --work-dir;
none of the corruptions or edited native models is a deliverable.
"""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import zipfile
import validate_3mf as validator

HERE=Path(__file__).resolve().parent


def write_zip(path, parts):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED,allowZip64=False) as z:
        for name,data in parts.items():
            i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16
            z.writestr(i,data)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model-dir',type=Path,default=HERE.parent)
    p.add_argument('--stl',type=Path);p.add_argument('--blend',type=Path)
    p.add_argument('--work-dir',type=Path,required=True)
    p.add_argument('--report',type=Path)
    a=p.parse_args();stl=a.stl or a.model_dir/'model.stl';blend=a.blend or a.model_dir/'scene.blend'
    work=a.work_dir.resolve();work.mkdir(parents=True,exist_ok=True)
    if work==HERE or HERE in work.parents:raise ValueError('Use a disposable work directory outside the supplement')
    appearances=HERE/'appearance-original.json';bindings=HERE/'face-materials.csv'
    before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in (stl,blend,appearances,bindings)}
    outputs=[];reports=[]
    for name in ('rebuild-a','rebuild-b'):
        folder=work/name
        if folder.exists():raise ValueError('Clean rebuild directory already exists: '+name)
        folder.mkdir();out=folder/'cnu-wang-chen-library.3mf'
        subprocess.run([sys.executable,str(HERE/'export_3mf.py'),'--stl',str(stl),'--blend',str(blend),'--output',str(out)],check=True,capture_output=True,text=True)
        outputs.append(out);reports.append(validator.validate(out,stl,blend,appearances,bindings))
    if outputs[0].read_bytes()!=outputs[1].read_bytes():raise ValueError('Whole ZIP rebuild differs')
    if reports[0]['package_member_hashes']!=reports[1]['package_member_hashes']:raise ValueError('Extracted part rebuild differs')
    shipped=HERE/'cnu-wang-chen-library.3mf'
    if outputs[0].read_bytes()!=shipped.read_bytes():raise ValueError('Shipped artifact differs from clean rebuild')
    with zipfile.ZipFile(outputs[0]) as z:parts={n:z.read(n) for n in z.namelist()}
    model=parts['3D/3dmodel.model'].decode();triangles=re.findall(r'<triangle [^>]+/>',model)
    first=triangles[0];v1=re.search(r'v1="(\d+)"',first).group(1);v2=re.search(r'v2="(\d+)"',first).group(1)
    coord=re.search(r'<vertex x="([^"]+)"',model).group(1)
    bits=struct.unpack('<I',struct.pack('<f',float(coord)))[0]
    drift=struct.unpack('<f',struct.pack('<I',bits+1))[0]
    wrong_winding=first.replace('v1="'+v1+'"','v1="SWAP"').replace('v2="'+v2+'"','v2="'+v1+'"').replace('v1="SWAP"','v1="'+v2+'"')
    mutated_assignment=re.sub(r'p([123])="1"',r'p\1="0"',first)
    controls={
        'triangle_record_order':(model.replace(first,'__FIRST__',1).replace(triangles[1],first,1).replace('__FIRST__',triangles[1]),'Same-index triangle/corner/winding mismatch'),
        'reversed_winding':(model.replace(first,wrong_winding,1),'Same-index triangle/corner/winding mismatch'),
        'one_float32_ulp':(model.replace('<vertex x="'+coord+'"','<vertex x="'+format(Decimal.from_float(drift),'f')+'"',1),'Same-index triangle/corner/winding mismatch'),
        'inexact_same_float32_decimal':(model.replace('<vertex x="'+coord+'"','<vertex x="'+format(Decimal(coord)+Decimal('0.000000000000000000001'),'f')+'"',1),'Coordinate is not exact float32 decimal'),
        'wrong_units':(model.replace('unit="millimeter"','unit="meter"',1),'Model unit/attributes mismatch'),
        'wrong_material_assignment':(model.replace(first,mutated_assignment,1),'Same-index material assignment mismatch'),
        'direct_linear_8bit_color':(model.replace('displaycolor="#EDEDE8FF"','displaycolor="#D9D9CFFF"',1),'Material color/name mismatch'),
        'mixed_material_triangle':(model.replace(first,first.replace('p2="1"','p2="0"'),1),'Invalid material index/gradient'),
        'bad_property_resource':(model.replace(first,first.replace('pid="1"','pid="7"'),1),'Invalid property resource'),
        'hidden_extra_object':(model.replace('</resources>','<object id="99" type="model"/></resources>',1),'Unexpected resources/hidden geometry'),
        'unit_scale_transform':(model.replace('<item objectid="2"/>','<item objectid="2" transform="0.001 0 0 0 0.001 0 0 0 0.001 0 0 0"/>',1),'Nonidentity/multiple build item'),
        'missing_exact_color_metadata':(re.sub(r'<metadata name="tb:appearance-original".*?</metadata>','',model,count=1),'Unexpected model children/hidden geometry'),
    }
    negatives={}
    negative_dir=work/'negative-controls';negative_dir.mkdir(exist_ok=False)
    for name,(text,expected) in controls.items():
        if text==model:raise ValueError('Ineffective control: '+name)
        changed=dict(parts);changed['3D/3dmodel.model']=text.encode();path=negative_dir/(name+'.3mf');write_zip(path,changed)
        try:validator.validate(path,stl,blend,appearances,bindings)
        except ValueError as e:
            if str(e)!=expected:raise ValueError(f'Control {name} failed at unintended check: {e}') from e
            negatives[name]={'rejected':True,'reason':str(e)}
        else:raise ValueError('Validator accepted corruption: '+name)
    for name,target in [('unsafe_zip_member','../unexpected.txt'),('unreferenced_package_part','3D/hidden.model')]:
        changed=dict(parts);changed[target]=b'not allowed';path=negative_dir/(name+'.3mf');write_zip(path,changed)
        try:validator.validate(path,stl,blend,appearances,bindings)
        except ValueError as e:
            if str(e)!='Package member allowlist/order/uniqueness mismatch':raise
            negatives[name]={'rejected':True,'reason':str(e)}
        else:raise ValueError('Validator accepted extra part: '+name)
    # Decimal rounding is deliberately unsafe even if silhouettes look identical.
    six=re.sub(r'(?<=\s)([xyz])="(-?\d+(?:\.\d+)?)"',lambda m:m[1]+'="'+format(float(m[2]),'.6f')+'"',model)
    changed=dict(parts);changed['3D/3dmodel.model']=six.encode();path=negative_dir/'six_decimal_rounding.3mf';write_zip(path,changed)
    try:validator.validate(path,stl,blend,appearances,bindings)
    except ValueError as e:
        if str(e)!='Coordinate is not exact float32 decimal':raise
        negatives['six_decimal_rounding']={'rejected':True,'reason':str(e)}
    else:raise ValueError('Validator accepted six-decimal rounding')
    # Test overwrite protection on disposable pinned copies, never on originals.
    guard_stl=work/'guard-source-copy.stl';shutil.copyfile(stl,guard_stl)
    guard_alias=work/'guard-source-hardlink.3mf';guard_alias.hardlink_to(guard_stl)
    guard_hash=hashlib.sha256(guard_stl.read_bytes()).hexdigest();export_guards={}
    for name,out in [('same_input_path',guard_stl),('hardlink_input_alias',guard_alias)]:
        run=subprocess.run([sys.executable,str(HERE/'export_3mf.py'),'--stl',str(guard_stl),'--blend',str(blend),'--output',str(out)],capture_output=True,text=True)
        if run.returncode==0 or 'Refusing' not in run.stderr or hashlib.sha256(guard_stl.read_bytes()).hexdigest()!=guard_hash:raise ValueError('Export overwrite guard failed: '+name)
        export_guards[name]={'rejected_before_write':True,'disposable_input_unchanged':True}
    for f,h in before.items():
        if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h:raise ValueError('Input changed')
    result={'status':'PASS','whole_zip_rebuild_identical':True,'extracted_parts_rebuild_identical':True,'rebuild_matches_shipped':True,
            'model_sha256':reports[0]['model_sha256'],'negative_controls':negatives,'negative_control_count':len(negatives),
            'export_overwrite_guards':export_guards,'inputs_byte_unchanged':True,'xml_validation':reports[0]}
    text=json.dumps(result,indent=2)+'\n'
    if a.report:a.report.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
