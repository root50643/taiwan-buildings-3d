#!/usr/bin/env python3
"""Fail-closed mapping, strict decimal drift and whole fixed-buffer privacy controls."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,shutil,subprocess,sys,tempfile,zipfile,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--input',type=Path);p.add_argument('--blender',default='blender');a=p.parse_args();root=a.out;source=a.input or root.parent/'model.stl';checks={}
protected=[source,root/'cjcu-gymnasium-roof-illustration.blend',root/'cjcu-gymnasium-roof-illustration.3mf',root/'mesh-data.npz',root/'face-materials.csv',root/'roof-face-contract.json',root/'palette.json']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
spec=importlib.util.spec_from_file_location('author_builder',root/'build_appearance.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
b,v,f,t=mod.load_stl(source);c=json.loads((root/'roof-face-contract.json').read_text());mod.assign(t,c)
def rejects(name,fn):
 try:fn()
 except (ValueError,AssertionError,IndexError,KeyError):checks[name]=True
 else:raise AssertionError('Control not rejected: '+name)
wrong=copy.deepcopy(c);wrong['face_indices_0_based'][0]=0;rejects('wrong_roof_ID_rejected',lambda:mod.assign(t,wrong))
wrong=copy.deepcopy(c);wrong['faces'][0]['ordered_float32_le_sha256']='0'*64;rejects('bad_oriented_fingerprint_rejected',lambda:mod.assign(t,wrong))
rev=t.copy();i=c['face_indices_0_based'][0];rev[i]=rev[i][::-1];rejects('reversed_roof_winding_rejected',lambda:mod.assign(rev,c))
with tempfile.TemporaryDirectory(prefix='appearance-controls-') as td:
 tmp=Path(td);altered=bytearray(b);altered[84+12]^=1;(tmp/'changed.stl').write_bytes(altered);rejects('one_source_coordinate_byte_change_rejected',lambda:mod.load_stl(tmp/'changed.stl'))
 scanner=root/'verify_path_buffers.py';real=root/'cjcu-gymnasium-roof-illustration.blend'
 clean=subprocess.run([sys.executable,str(scanner),'--blend',str(real),'--report',str(tmp/'buffers.json')],capture_output=True,text=True);assert clean.returncode==0
 fields=json.loads((tmp/'buffers.json').read_text())['fields'];raw=bytearray(real.read_bytes())
 for field in fields:
  off=field['offset'];size=field['fixed_buffer_bytes'];nul=raw.index(0,off,off+size);bad=raw.copy();bad[nul+1:nul+8]=b'PRIVATE';file=tmp/'tainted.blend';file.write_bytes(bad)
  r=subprocess.run([sys.executable,str(scanner),'--blend',str(file)],capture_output=True);assert r.returncode!=0
  checks[field['field']+'_hidden_tail_injection_rejected']=True
 # Factory scene is a negative control, never a deliverable and never printed.
 factory=tmp/'factory.blend';expr='import bpy; bpy.ops.wm.save_as_mainfile(filepath='+repr(str(factory))+')'
 r=subprocess.run([a.blender,'-b','--factory-startup','--python-exit-code','1','--python-expr',expr],capture_output=True);assert r.returncode==0 and factory.exists()
 r=subprocess.run([sys.executable,str(scanner),'--blend',str(factory)],capture_output=True);assert r.returncode!=0;checks['unsanitized_factory_file_rejected']=True
 # Decimal-coordinate drift smaller than a float32 ULP must still be rejected.
 for name in ('mesh-data.npz','face-materials.csv','roof-face-contract.json','palette.json'):shutil.copy2(root/name,tmp/name)
 path=root/'cjcu-gymnasium-roof-illustration.3mf'
 with zipfile.ZipFile(path) as z:files={name:z.read(name) for name in z.namelist()}
 xml=ET.fromstring(files['3D/3dmodel.model']);vertex=next(q for q in xml.iter() if q.tag.endswith('}vertex'));vertex.attrib['x']=repr(float(vertex.attrib['x'])+1e-7);files['3D/3dmodel.model']=ET.tostring(xml)
 with zipfile.ZipFile(tmp/path.name,'w') as z:
  for name,data in files.items():z.writestr(name,data)
 r=subprocess.run([sys.executable,str(root/'validate_appearance.py'),'--out',str(tmp),'--input',str(source)],capture_output=True);assert r.returncode!=0;checks['sub_float32_ULP_decimal_3MF_drift_rejected']=True
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
checks['clean_mapping_and_buffer_controls_pass']=True
(root/'qa'/'negative-controls.json').write_text(json.dumps({'controls':checks,'all_expected_rejections_observed':all(checks.values()),'delivered_inputs_unchanged':True},indent=2)+'\n');print(json.dumps(checks,indent=2))
