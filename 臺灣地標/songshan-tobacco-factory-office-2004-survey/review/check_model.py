from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent; root=out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
byname=lambda name:[p for p in parts if p['name']==name]
S=10/3;BASE=.6
checks['three_U_masses']=all(len(byname(n))==1 for n in ['West U crossbar','North U arm','South U arm'])
checks['three_hipped_roof_parts']=len([p for p in parts if 'inner hipped roof' in p['name']])==3
for name,height in [('Central three-storey hall',14.88),('Central high stair-clock tower',16.87)]:
 checks[name+'_height']=np.isclose(bounds(byname(name)[0])[1,2]/S-BASE,height,atol=.001)
checks['main_cornice_height']=np.isclose(bounds(byname('West flat eave')[0])[1,2]/S-BASE,10.4,atol=.001)
checks['hip_ridge_height']=np.isclose(bounds(byname('West inner hipped roof')[0])[1,2]/S-BASE,12.82,atol=.001)
for side in ['North','South']:
 b=bounds(byname(side+' gallery upper floor')[0])/S
 checks[side+'_gallery_3m_width']=np.isclose(b[1,0]-b[0,0],3,atol=.001)
 checks[side+'_gallery_12m_length_plus_10cm_join']=np.isclose(b[1,1]-b[0,1],12.1,atol=.001)
 checks[side+'_gallery_6_ground_columns']=len(byname(side+' gallery ground pillar'))==6
 checks[side+'_gallery_two_enclosure_sides']=all(len(byname(side+' gallery '+n+' side wall'))==1 for n in ['north','south'])
checks['source_1940_RC']=any('1940' in p['evidence'] and 'RC' in p['evidence'] for p in parts)
checks['no_unrelated_joinery_tables']=not any('339' in p['evidence'] or '341' in p['evidence'] for p in parts)
checks['no_roof_fall_line_proxies']=not any('roof fall line' in p['name'] for p in parts)
checks['no_transplanted_inner_service_sashes']=not any('inner service sash' in p['name'] for p in parts)
inner=[p for p in parts if 'inner courtyard neutral opening' in p['name'] and p['name'].endswith('opaque pane')]
checks['sixteen_plan_confirmed_courtyard_proxies']=len(inner)==16
checks['courtyard_proxies_plain_1x1']=all(sum(1 for q in parts if q['name']==p['name'].replace('opaque pane','mullion'))==2 and sum(1 for q in parts if q['name']==p['name'].replace('opaque pane','rail'))==2 for p in inner)
checks['courtyard_proxy_width_height']=all(np.allclose((bounds(p)[1]-bounds(p)[0])[[1,2]]/S,[1.5,1.8],atol=.001) for p in inner)
checks['courtyard_proxy_positions']=all(any(np.isclose(bounds(p).mean(axis=0)[1]/S,y,atol=.001) for y in [13.8,17.3,20.6,23.6]) for p in inner)
checks['tower_base_grille_compact']=all(np.allclose((bounds(p)[1]-bounds(p)[0])[[1,2]]/S,[.6,.8],atol=.001) for p in parts if 'front tower base grille opaque pane' in p['name'])
checks['east_end_service_16_fields']=len([p for p in parts if 'East wing-end service' in p['name'] and p['name'].endswith('surround')])==16
checks['shoulder_side_six_sashes']=len([p for p in parts if 'shoulder side narrow sash surround' in p['name']])==6
checks['tower_side_two_base_grilles']=len([p for p in parts if 'front tower base grille surround' in p['name']])==2
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
# Empty-space probes are above the authored support and platforms.
def empty(a,b):
 a=np.array(a);b=np.array(b);a[2]+=BASE;b[2]+=BASE
 return abs((rebuilt ^ mf.Manifold.cube(((b-a)*S).tolist()).translate((a*S).tolist())).volume())<1e-8
checks['U_courtyard_empty']=empty([14,14,1],[50,25,10])
for side,x in [('North',0),('South',61.17)]:
 checks[side+'_lower_gallery_open']=empty([x+.5,27,1],[x+2.5,37.8,4.5])
 checks[side+'_upper_gallery_hollow']=empty([x+.3,27,5.5],[x+2.7,38.3,9.9])
 checks[side+'_gallery_end_uncapped']=empty([x+.3,38.24,5.5],[x+2.7,38.44,9.9])
checks={k:bool(v) for k,v in checks.items()};result={'checks':checks,'passed':all(checks.values()),'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent CSG/source-index/format check; not trial print or exact complete historic reconstruction.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'checks':checks,'volume_delta':detail['relative_volume_delta']},indent=2))

assert result["passed"], "Independent model checks failed"
