from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET,sys
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
byname=lambda n:[p for p in parts if p['name']==n]
S=4.;BASE=.50
for label,name,height in [('rear','Connected rear three-storey wing and semicircle',13.58),('main','Main surveyed storey 3',14.98),('stair','Permanent rooftop stair room',18.27),('tank','Survey rooftop water tank',20.35)]:
 checks[label+'_height']=np.isclose(bounds(named[name])[1,2]/S-BASE,height,atol=.001)
checks['three_main_storeys']=all('Main surveyed storey '+str(i) in named for i in [1,2,3])
checks['rear_own_floor_belts']=all('Rear floor belt '+str(z) in named for z in [1.18,4.83,9.18,13.58])
checks['four_entry_columns']=len(byname('Corner entrance column'))==4
piers=sorted(byname('Street gate72cm pier'),key=lambda p:bounds(p)[0,0])
detail['gate_clear_width_m']=(bounds(piers[1])[0,0]-bounds(piers[0])[1,0])/S
checks['gate335cm_clear']=np.isclose(detail['gate_clear_width_m'],3.35,atol=.001)
checks['gate72cm_piers']=all(np.isclose(np.ptp(np.array(p['vertices'])[:,0])/S,.72,atol=.001) for p in piers)
checks['five_equipment_tanks']=sum(p['name'].startswith('Survey roof equipment tank ') for p in parts)==5
checks['no_temporary_shed_constructed']=not any('shed' in p['name'].lower() for p in parts)
checks['rear_external_stair18treads']=sum(p['name'].startswith('Rear exterior stair tread ') for p in parts)==18
checks['rear_external_stair_landing_height']=np.isclose(bounds(named['Rear exterior stair landing'])[1,2]/S-BASE,4.83,atol=.001)
checks['rear_discrepancy_disclosed']='13.38' in named['Connected rear three-storey wing and semicircle']['evidence']
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
stl_merged=trimesh.load(root/'model.stl',process=True)
checks['stl_reopen_watertight']=bool(stl_merged.is_watertight)
checks['stl_reopen_winding']=bool(stl_merged.is_winding_consistent)
with zipfile.ZipFile(root/'model.3mf') as z:r=ET.fromstring(z.read('3D/3dmodel.model'))
ns={'m':r.tag.split('}')[0][1:]};vv=np.array([[float(e.attrib[k]) for k in 'xyz']for e in r.findall('.//m:vertex',ns)]);ff=np.array([[int(e.attrib[k])for k in ['v1','v2','v3']]for e in r.findall('.//m:triangle',ns)])
checks['3mf_coordinates']=np.allclose(v,vv,atol=1e-7);checks['3mf_triangles']=np.array_equal(f,ff)
adds=[];cuts=[]
for p in parts:
 q=mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64)))
 (cuts if p.get('operation')=='subtract' else adds).append(q)
rebuilt=mf.Manifold.batch_boolean(adds,mf.OpType.Add)
if cuts:rebuilt=rebuilt-mf.Manifold.batch_boolean(cuts,mf.OpType.Add)
detail['reunion_volume_mm3']=rebuilt.volume();detail['final_volume_mm3']=m.volume;detail['relative_volume_delta']=abs(rebuilt.volume()-m.volume)/m.volume
checks['reunion_volume_matches_with_simplification']=detail['relative_volume_delta']<1e-4
checks['reunion_one_component']=len(rebuilt.decompose())==1

checks['materials_face_count']=len(D['materials'])==len(f)
checks['materials_ids_valid']=bool(np.all((D['materials']>=0)&(D['materials']<10)))
checks['all_parts_manifold']=all(mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64))).status()==mf.Error.NoError for p in parts)
def probe(a,b):
 a=np.array(a,float);b=np.array(b,float);a[2]+=BASE;b[2]+=BASE
 return mf.Manifold.cube(((b-a)*S).tolist()).translate((a*S).tolist())
for n,a,b in [('gate',[51.7,-.4,.3],[54.8,.1,4.0]),('passage',[51.6,1,.3],[54.9,12,4.0]),('portico',[1.8,2.0,1.5],[2.4,2.6,4.8]),('rear_roof_terrace',[40,21,14.2],[42,23,15.2])]:
 checks[n+'_open']=abs((rebuilt^probe(a,b)).volume())<1e-7
ratios=[]
for p in byname('Corner entrance column'):
 q=mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64)));ratios.append((rebuilt^q).volume()/q.volume())
detail['entrance_column_volume_retained']=ratios;checks['all_four_columns_survive']=len(ratios)==4 and all(r>.999 for r in ratios)
# Semicircular mass is present on the rear wing west side, while adjoining courtyard remains open.
checks['rear_semicircle_solid']=((rebuilt^probe([33.5,21.5,2],[34.0,22,12])).volume()/probe([33.5,21.5,2],[34.0,22,12]).volume())>.999
checks={k:bool(v) for k,v in checks.items()}
result={'passed':all(checks.values()),'checks':checks,'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent source-control/CSG/format inspection. No trial print or safety certification; excludes unresolved temporary rooftop shed.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,indent=2));assert result['passed'],'Independent checks failed'
