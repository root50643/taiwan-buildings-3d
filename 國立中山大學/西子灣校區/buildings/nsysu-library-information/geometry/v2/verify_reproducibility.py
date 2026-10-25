"""Clean public-source-only rebuild and exact STL/3MF/nine-PNG parity.
No reference images, original legacy package, network, or private files are inputs.
python verify_reproducibility.py --blender blender --lib3mf-python python
"""
import argparse,hashlib,json,pathlib,shutil,subprocess,sys,tempfile
import numpy as np
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--blender',default='blender');ap.add_argument('--lib3mf-python',default=sys.executable);a=ap.parse_args();r=a.out
sources=['build_model.py','render_model.py','export_3mf.py','params.json','requirements.txt','requirements-3mf.txt']
def run(cmd):
 p=subprocess.run(cmd,capture_output=True,text=True)
 if p.returncode:raise RuntimeError('Rebuild subprocess failed: '+p.stderr[-2000:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'method':'Clean separate directory containing only the six public rebuild inputs; no source pixels/private files/network','inputs':{n:sha(r/n)for n in sources},'files':{},'png':{},'native_binary_note':'Blend file bytes can include serialization state; native geometry/material/edit/save/reopen is checked separately.'}
with tempfile.TemporaryDirectory(prefix='nsysu-public-rebuild-')as td:
 t=pathlib.Path(td)
 for n in sources:shutil.copy2(r/n,t/n)
 run([sys.executable,str(t/'build_model.py')]);run([a.lib3mf_python,str(t/'export_3mf.py')]);run([a.blender,'--background','--factory-startup','--disable-autoexec','-t','4','-P',str(t/'render_model.py')])
 for n in ['model.stl','model.3mf','mesh-data.npz','plan-section-data.npz','build-summary.json','construction-parts.json','render-manifest.json']:
  eq=sha(r/n)==sha(t/n);report['files'][n]={'byte_identical':eq,'sha256':sha(r/n)};assert eq,n
 for n in ['front','rear','south','north','east','west','roof','plan','roof-oblique']:
  p=r/'previews'/f'{n}.png';q=t/'previews'/f'{n}.png';im=Image.open(p);jm=Image.open(q);byte=sha(p)==sha(q);pix=im.mode==jm.mode and im.size==jm.size and im.tobytes()==jm.tobytes();report['png'][n]={'byte_identical':byte,'pixels_identical':pix,'sha256':sha(p),'size':list(im.size)};assert byte and pix,n
 # A real parameter edit must alter geometry while leaving baseline source bytes alone.
 old=(t/'params.json').read_bytes();p=json.loads(old);p['machine_center_xy_m'][1]+=1.0;(t/'params.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');run([sys.executable,str(t/'build_model.py')]);changed=sha(t/'model.stl')!=sha(r/'model.stl');assert changed;report['parameter_edit_changes_geometry']=changed
report['all_pass']=True;(r/'qa').mkdir(exist_ok=True);(r/'qa/reproducibility.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
