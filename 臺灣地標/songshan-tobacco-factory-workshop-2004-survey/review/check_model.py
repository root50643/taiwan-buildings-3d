from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent; root=out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
byname=lambda name:[p for p in parts if p['name']==name]
S=10/3
checks['nineteen_corridor_posts_for_eighteen_bays']=len(byname('West corridor post'))==19
checks['main_bay_uprights_both_faces']=len(byname('Main bay upright'))==38
checks['ten_addition_uprights_five_each_side']=len(byname('North addition bay upright'))==10
checks['two_long_dormer_backings']=len([p for p in parts if 'long dormer backing' in p['name']])==2
checks['four_visible_cap_shafts']=len(byname('Visible roof cap shaft proxy'))==4
checks['caps_correct_longitudinal_control']=np.allclose([bounds(p).mean(axis=0)[0]/S for p in byname('Visible roof cap shaft proxy')],[38.5,50,72,79])
checks['west_only_corridor']=len(byname('West open corridor lean-to roof'))==1 and all(bounds(p)[1,1]/S<0 for p in byname('West corridor post')) and not any('East corridor' in p['name'] for p in parts)
checks['west_two_narrow_doors']=len([p for p in parts if re.match(r'West bay\d+ narrow door field$',p['name'])])==2
checks['east_one_offset_door']=len(byname('East bay12 small offset door'))==1
checks['asymmetric_addition_doors']=np.isclose(bounds(byname('W addition door field')[0]).mean(axis=0)[0]/S,18.013*2.5/5,atol=.001) and np.isclose(bounds(byname('E addition door field')[0]).mean(axis=0)[0]/S,18.013*1.5/5,atol=.001)
checks['north_three_sash_bays']=len([p for p in parts if re.match(r'North end lower sash\d surround$',p['name'])])==3
checks['south_three_tall_openings']=len([p for p in parts if re.match(r'South end tall opening\d dark lower panel$',p['name'])])==3
checks['no_other_building_joinery_table']=not any('339' in p['evidence'] or '341' in p['evidence'] for p in parts)
for side,indices in [('W',[1,4,15]),('E',[4,10,15])]:
 checks[side+'_altered_opening_indices']=[int(re.search(r'bay(\d+)',p['name'])[1]) for p in parts if re.match(side+r' main altered bay\d+ dark field$',p['name'])]==indices
checks['south_three_high_transoms']=len([p for p in parts if re.match(r'South end upper transom\d surround$',p['name'])])==3
for side,face,back in [('W',2.1,4.1),('E',10.67,8.67)]:
 pv=np.array(byname(side+' long dormer cap')[0]['vertices'])/S;pv[:,2]-=.60
 zface=pv[np.isclose(pv[:,1],face,atol=.001),2].max();zback=pv[np.isclose(pv[:,1],back,atol=.001),2].max()
 checks[side+'_dormer_cap_rises_inward']=zback>zface+.5
 roofz=lambda y:8.1-(8.1-4.6)*abs(y-12.77/2)/(12.77/2+.30)
 checks[side+'_dormer_front_back_lifts']=np.isclose(zface-roofz(face),.45,atol=.002) and np.isclose(zback-roofz(back),.08,atol=.002)
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
# Sample corridor void between posts below roof and away from main wall.
probe=mf.Manifold.cube([.8*S,.8*S,1.0*S]).translate([20*S,-1.8*S,1.2*S])
void_intersection=rebuilt^probe
checks['corridor_midbay_is_open']=abs(void_intersection.volume())<1e-9
detail['corridor_probe_volume_mm3']=void_intersection.volume()
checks={k:bool(v) for k,v in checks.items()};result={'checks':checks,'passed':all(checks.values()),'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent CSG/source-index/format check; not trial print or exact complete historic reconstruction.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'checks':checks,'volume_delta':detail['relative_volume_delta']},indent=2))

assert result["passed"], "Independent model checks failed"
