from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent; root=out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
wins={int(re.search(r'sash(\d+)',p['name'])[1]):p for p in parts if re.fullmatch(r'Ground timber sash\d+ surround',p['name'])}
checks['ten_unique_lower_windows']=set(wins)==set(range(1,11)) and sum(bool(re.fullmatch(r'Ground timber sash\d+ surround',p['name'])) for p in parts)==10
expected={1:('N',2.42),10:('N',12.1),2:('W',2.095),3:('W',14.62),4:('W',21.98),5:('S',1.64),6:('S',4.91),7:('S',12.1),8:('E',22),9:('E',2.095)}
for n,p in wins.items():
 b=bounds(p)/5;b[:,2]-=.55;c=b.mean(axis=0);side,u=expected[n]; axis=1 if side in 'NS' else 0
 checks[f'window{n}_location']=abs(c[axis]-u)<.1 and abs(c[1-axis]-{'N':0,'S':23.32,'W':0,'E':14.53}[side])<.1
 detail[f'window{n}']=b.tolist()
for n in [21,22,23]:checks[f'missing{n}_cutter']=f'West missing iron leaf{n} recess cutter' in named
checks['missing11_cutter']='South missing door11 recess cutter' in named
for n in [11,21,22,23]:checks[f'no_complete_leaf{n}']=not any(re.search(rf'(?:door|leaf){n} leaf$',p['name']) for p in parts)
ch=bounds(named['Tapered concrete chimney'])/5;checks['chimney_36_06m']=abs((ch[1,2]-ch[0,2])-36.06)<1e-6
checks['chimney_actual_mouth_cut']='Chimney top-mouth recess' in named and named['Chimney top-mouth recess']['operation']=='subtract'
D=np.load(root/'mesh-data.npz');v=D['vertices'];f=D['faces'];m=trimesh.Trimesh(v,f,process=False)
# Pure union-find: no optional scipy/networkx graph engine required.
parent=list(range(len(v))); rank=[0]*len(v)
def find(i):
 while parent[i]!=i:
  parent[i]=parent[parent[i]];i=parent[i]
 return i
for a,b in m.edges:
 ra,rb=find(int(a)),find(int(b))
 if ra!=rb:
  if rank[ra]<rank[rb]:ra,rb=rb,ra
  parent[rb]=ra
  if rank[ra]==rank[rb]:rank[ra]+=1
component_count=len({find(i) for i in range(len(v))})
detail['mesh_component_count']=component_count
checks['mesh_watertight']=bool(m.is_watertight);checks['mesh_winding']=bool(m.is_winding_consistent);checks['one_component']=component_count==1
stl=trimesh.load(root/'model.stl',process=False);checks['stl_triangle_coordinates']=stl.triangles.shape==m.triangles.shape and np.allclose(stl.triangles,m.triangles,atol=1e-5)
with zipfile.ZipFile(root/'model.3mf') as z:r=ET.fromstring(z.read('3D/3dmodel.model'))
ns={'m':r.tag.split('}')[0][1:]};vv=np.array([[float(e.attrib[k]) for k in 'xyz']for e in r.findall('.//m:vertex',ns)]);ff=np.array([[int(e.attrib[k])for k in ['v1','v2','v3']]for e in r.findall('.//m:triangle',ns)])
checks['3mf_coordinates']=np.allclose(v,vv,atol=1e-7);checks['3mf_triangles']=np.array_equal(f,ff)
adds=[];cuts=[]
for p in parts:
 q=mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64)))
 (cuts if p.get('operation')=='subtract' else adds).append(q)
rebuilt=mf.Manifold.batch_boolean(adds,mf.OpType.Add)-mf.Manifold.batch_boolean(cuts,mf.OpType.Add)
detail['reunion_volume_mm3']=rebuilt.volume();detail['final_volume_mm3']=m.volume;detail['relative_volume_delta']=abs(rebuilt.volume()-m.volume)/m.volume
checks['reunion_volume_matches_with_simplification']=detail['relative_volume_delta']<1e-4
checks['reunion_one_component']=len(rebuilt.decompose())==1
checks={k:bool(v) for k,v in checks.items()};result={'checks':checks,'passed':all(checks.values()),'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent CSG/source-index/format check; not trial print or exact complete historic reconstruction.'}
(out/'model-v3-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'checks':checks,'volume_delta':detail['relative_volume_delta']},indent=2))

assert result["passed"], "Independent model checks failed"
