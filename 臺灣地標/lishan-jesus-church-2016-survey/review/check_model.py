from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,sys
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else out.parent
parts=json.loads((root/'construction-parts.json').read_text());checks={};detail={}
named={p['name']:p for p in parts};byname=lambda n:[p for p in parts if p['name']==n]
bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
S=5.;BASE=.4
checks['main_nominal_envelope']=np.allclose(np.ptp(np.array(named['Main nave solid exterior']['vertices']),axis=0)/S,[13.71,27.96,5.53],atol=.002)
checks['main_roof_ridge923']=np.isclose(bounds(named['Main aged copper roof'])[1,2]/S-BASE,9.23,atol=.002)
for side in ['L','R']:
 bb=bounds(named[side+' transept wall'])/S
 checks[side+'_wing_y_control']=np.allclose(bb[:,1],[14.93,21.96],atol=.002)
 checks[side+'_wing_eave334']=np.isclose(bb[1,2]-BASE,3.34,atol=.002)
 checks[side+'_wing_ridge529']=np.isclose(bounds(named[side+' transept copper roof'])[1,2]/S-BASE,5.29,atol=.002)
 checks[side+'_wing_endtrim553']=np.isclose(bounds(named[side+' transept end gable edge'])[1,2]/S-BASE,5.53,atol=.002)
patches=byname('Left roof red repair sheet patch')
checks['two_repair_patches_left_only']=len(patches)==2 and all(bounds(p)[1,0]<.001 for p in patches)
checks['repair_patch_y_regions']=len(patches)==2 and np.allclose(sorted([bounds(p)[:,1].tolist() for p in patches]),np.array([[0,7.59],[21.96,27.96]])*S,atol=.002)
checks['four_tower_corner_piers']=len(byname('Tower projecting corner pier'))==4
checks['tower_shaft_top1312']=np.isclose(bounds(named['Tower upper square shaft'])[1,2]/S-BASE,13.12,atol=.002)
checks['tower_spire1847']=np.isclose(bounds(named['Tower pyramid copper spire'])[1,2]/S-BASE,18.47,atol=.002)
checks['tower_cross1948']=np.isclose(bounds(named['Tower cross upright'])[1,2]/S-BASE,19.48,atol=.002)
checks['cupola_roof1238']=np.isclose(bounds(named['Roof cupola pyramid'])[1,2]/S-BASE,12.38,atol=.002)
checks['cupola_y18445']=np.isclose(bounds(named['Roof cupola base']).mean(axis=0)[1]/S,18.445,atol=.002)
for side in ['L','R']:
 bb=bounds(named['Cupola '+side+' W8 opaque glazing'])/S
 checks[side+'_W8_hostaligned']=np.allclose(bb[:,2]-BASE,[8.91,10.00],atol=.002)
for side in ['F','B']:
 vv=np.array(named['Cupola '+side+' W9 opaque V-bottom']['vertices'])/S
 checks[side+'_W9_v_center']=np.isclose(vv[np.isclose(vv[:,0],0),2].min()-BASE,9.29,atol=.002)
 checks[side+'_W9_edge_and_top']=np.allclose([vv[:,2].min()-BASE,vv[:,2].max()-BASE],[8.96,10.06],atol=.002)
# Outer wing end gable is itself raised: verify doors reach outside that host.
for side,sign in [('L',-1),('R',1)]:
 p=named[side+' wing D2 closed door leaf proxy']
 outer=np.max(sign*np.array(p['vertices'])[:,0]/S)
 checks[side+'_wing_door_outside_raised_endgable']=outer>14.25
checks['rear_tower_unverified_W6_absent']=not any(p['name'].startswith('Tower B W6') for p in parts)
checks['rear_tower_unverified_full_surround_absent']='Tower B tall surround' not in named
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

for n,a,b in [('porch_front_clear',[-.8,-3.90,.6],[.8,-3.4,2.5]),('porch_left_clear',[-2.15,-2.5,.6],[-1.6,-1.1,2.5]),('porch_right_clear',[1.6,-2.5,.6],[2.15,-1.1,2.5]),('porch_inner_clear',[-1,-3,.6],[1,-.3,2.5])]:
 checks[n]=abs((rebuilt^probe(a,b)).volume())<1e-6
for i,p in enumerate(byname('Tower projecting corner pier')):
 q=mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64)))
 checks['tower_pier_retained_'+str(i)]=(rebuilt^q).volume()/q.volume()>.999
checks={k:bool(v) for k,v in checks.items()}
result={'passed':all(checks.values()),'checks':checks,'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent 2016 survey exterior nominal-control and CSG/format audit. Source axes versus skin and local roof endpoints remain disclosed proxies. No trial print or safety certification. Visual review separate.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed'],'Independent checks failed'
