from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent; root=out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
# Index by explicit construction feature rather than nursery joinery numbers.
byname=lambda name:[p for p in parts if p['name']==name]
checks['south_four_leaves']=len(byname('South narrow timber leaf'))==4
leaves=byname('South narrow timber leaf');centres=[bounds(p).mean(axis=0)/20 for p in leaves]
checks['south_leaves_centered']=len(centres)==4 and np.allclose([c[1] for c in centres],[1.845,2.495,3.145,3.795],atol=.002)
checks['north_one_door']=len(byname('North door timber field'))==1
checks['east_one_door']=len(byname('East door timber field'))==1
checks['east_utility_north_of_door']=len(byname('East surface utility line'))==4 and all(bounds(p)[1,0]/20<2.0 for p in byname('East surface utility line'))
checks['west_window_not_door']=len(byname('West raised sash surround'))==1 and not any('West door' in p['name'] for p in parts)
for name,count in [('North side window surround',2),('South side window surround',2),('South high transom surround',4),('North door transom surround',1),('East narrow transom surround',1),('West narrow transom surround',1)]:checks[name]=len(byname(name))==count
checks['no_nursery_table_dimensions']=not any('339' in p['evidence'] or '341' in p['evidence'] for p in parts)
hip=named['Four-slope hipped roof'];hv=np.array(hip['vertices'])/20;hv[:,2]-=.15
checks['hip_six_control_vertices']=len(hv)==6
upper=hv[hv[:,2]>4];lower=hv[hv[:,2]<3]
checks['hip_short_east_west_ridge']=upper.shape==(2,3) and np.allclose(upper[:,0],2.38) and np.isclose(np.ptp(upper[:,1]),.86)
checks['four_hip_eave_corners']=lower.shape==(4,3) and np.isclose(np.ptp(lower[:,0]),5.8) and np.isclose(np.ptp(lower[:,1]),6.66)
fb=bounds(named['Survey foundation envelope'])/20
checks['footprint_4_76_by_5_62']=np.allclose(fb[1,:2]-fb[0,:2],[4.76,5.62])
checks['height_4_46_above_base']=np.isclose(max(bounds(p)[1,2] for p in parts)/20-.15,4.46,atol=.002)
detail['south_leaf_centers_metres']=[c.tolist() for c in centres]
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
rebuilt=mf.Manifold.batch_boolean(adds,mf.OpType.Add)
if cuts:rebuilt=rebuilt-mf.Manifold.batch_boolean(cuts,mf.OpType.Add)
detail['reunion_volume_mm3']=rebuilt.volume();detail['final_volume_mm3']=m.volume;detail['relative_volume_delta']=abs(rebuilt.volume()-m.volume)/m.volume
checks['reunion_volume_matches_with_simplification']=detail['relative_volume_delta']<1e-4
checks['reunion_one_component']=len(rebuilt.decompose())==1
checks={k:bool(v) for k,v in checks.items()};result={'checks':checks,'passed':all(checks.values()),'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent CSG/source-index/format check; not trial print or exact complete historic reconstruction.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'checks':checks,'volume_delta':detail['relative_volume_delta']},indent=2))

assert result["passed"], "Independent model checks failed"
