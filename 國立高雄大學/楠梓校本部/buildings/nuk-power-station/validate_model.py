from pathlib import Path
import json,zipfile,struct,xml.etree.ElementTree as E
import numpy as np,trimesh
p=Path(__file__).resolve().parent;d=np.load(p/'mesh-data.npz');v=d['vertices'];f=d['faces'];m=trimesh.Trimesh(v,f,process=False);checks={}
parent=list(range(len(v)))
def find(i):
 while parent[i]!=i: parent[i]=parent[parent[i]];i=parent[i]
 return i
for a,b in m.edges:
 ra,rb=find(int(a)),find(int(b))
 if ra!=rb:parent[ra]=rb
components=len({find(i) for i in range(len(v))})
checks['finite_vertices']=bool(np.isfinite(v).all());checks['positive_face_areas']=bool((m.area_faces>0).all());checks['watertight']=bool(m.is_watertight);checks['consistent_winding']=bool(m.is_winding_consistent);checks['positive_volume']=bool(m.volume>0);checks['one_connected_component']=components==1
edges=np.sort(m.edges,axis=1);_,counts=np.unique(edges,axis=0,return_counts=True);checks['every_edge_two_faces']=bool((counts==2).all())
b=(p/'model.stl').read_bytes();n=struct.unpack('<I',b[80:84])[0];st=np.frombuffer(b, dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]),offset=84,count=n);checks['stl_triangle_exact']=bool(np.array_equal(st['v'],v[f].astype('<f4')))
with zipfile.ZipFile(p/'model.3mf') as z:
 root=E.fromstring(z.read('3D/3dmodel.model'));ns={'m':root.tag.split('}')[0][1:]};vv=np.array([[float(a.attrib[q]) for q in ['x','y','z']] for a in root.findall('.//m:vertex',ns)]);tt=root.findall('.//m:triangle',ns);ff=np.array([[int(a.attrib[q])for q in ['v1','v2','v3']]for a in tt]);mi=np.array([int(a.attrib['p1'])for a in tt]);checks['3mf_vertex_equal']=bool(np.allclose(vv,v,rtol=0,atol=1e-6));checks['3mf_triangle_equal']=bool(np.array_equal(ff,f));checks['3mf_material_equal']=bool(np.array_equal(mi,d['materials']));checks['3mf_mm_units']=root.attrib['unit']=='millimeter'
report={'checks':checks,'passed':all(checks.values()),'scope':'Geometry and format integrity only, not complete real-building reconstruction or trial print','triangle_count':len(f),'component_count':components};(p/'QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
