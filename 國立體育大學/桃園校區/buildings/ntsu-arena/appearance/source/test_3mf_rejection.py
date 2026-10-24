"""Negative controls against actual saved 3MF content through strict native validation."""
from pathlib import Path
import argparse,tempfile,zipfile,xml.etree.ElementTree as ET,subprocess,sys,json,shutil,copy
sys.dont_write_bytecode=True
from common import *
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.out;D=load(a.stl,root/'parameters.json',root/'palette.json');src=Path(__file__).resolve().parent;original=root/'ntsu-arena-appearance.3mf';before=sha(original.read_bytes());ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(original)as z:parts={n:z.read(n)for n in z.namelist()}
neutral=D['parameters']['neutral_original_face_ids'][0]
rear=next(i for i,t in enumerate(D['triangles'])if min(q[1]for q in t)>=-1e-4 and all(abs(math.hypot(q[0],q[1])-60.8)<1e-4 for q in t)and min(q[2]for q in t)>=10-1e-4 and max(q[2]for q in t)<=33.7+1e-4)
def change_material(tree,face,value):
 tr=tree.find('.//m:triangles',ns)[face]
 for k in ['p1','p2','p3']:tr.set(k,str(value))
def reorder(tree):
 tr=tree.find('.//m:triangles',ns);first=tr[0];second=tr[1];tr.remove(first);tr.insert(1,first)
def corners(tree):
 tr=tree.find('.//m:triangles',ns)[0];v=[tr.get(k)for k in ['v1','v2','v3']]
 for k,x in zip(['v1','v2','v3'],[v[1],v[2],v[0]]):tr.set(k,x)
def shifted(tree):
 v=tree.find('.//m:vertices',ns)[0];v.set('x',repr(float(v.get('x'))+.00001))
def transparent(tree):tree.find('.//m:basematerials',ns)[3].set('displaycolor','#49535680')
cases=[('neutral_face_white',lambda t:change_material(t,neutral,2)),('rear_glass_colored',lambda t:change_material(t,rear,3)),('white_rim_green',lambda t:change_material(t,D['parameters']['regions']['horizontal_roof_rim_lip']['original_face_ids'][0],1)),('transparent_glass',transparent),('face_record_reordering',reorder),('corner_cyclic_reordering',corners),('coordinate_drift',shifted)];result={}
with tempfile.TemporaryDirectory(prefix='3mf-negative-')as tmp:
 t=Path(tmp)
 for n in ['parameters.json','palette.json']:shutil.copyfile(root/n,t/n)
 for name,change in cases:
  tree=ET.fromstring(parts['3D/3dmodel.model']);change(tree)
  with zipfile.ZipFile(t/original.name,'w',compression=zipfile.ZIP_DEFLATED)as z:
   for key,value in parts.items():z.writestr(key,ET.tostring(tree,encoding='utf-8',xml_declaration=True)if key=='3D/3dmodel.model'else value)
  q=subprocess.run([sys.executable,str(src/'verify_3mf.py'),'--stl',str(a.stl),'--out',str(t)],capture_output=True,text=True)
  need(q.returncode!=0 and ('AssertionError'in q.stderr or 'ValueError'in q.stderr),'Invalid actual 3MF was accepted or failed for unrelated reason: '+name);result[name]='REJECTED'
need(sha(original.read_bytes())==before,'Production 3MF changed');dump(root/'qa/3mf-negative-controls.json',{'status':'PASS','actual_saved_3mf_native_validation_negative_controls':result,'original_3mf_unchanged':True});print(result)
