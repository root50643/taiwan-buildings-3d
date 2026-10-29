from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent; root=out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
byname=lambda name:[p for p in parts if p['name']==name]
S=5/3;BASE=1.2
checks['six_main_body_segments']=sum(p['name'].endswith('solid exterior body') for p in parts)==6
checks['four_chamfered_corners']=len(byname('Main court chamfer body'))==4
checks['four_two_storey_stair_projections']=sum(p['name'].endswith('court staircase envelope') for p in parts)==4
checks['six_small_roof_caps']=len(byname('Small stair roof cap'))==6
checks['two_semicircular_bath_envelopes']=sum(p['name'].endswith('low semicircular bath enclosure') for p in parts)==2
checks['bath_height_proxy']=all(np.isclose(bounds(p)[1,2]/S-BASE,3.5,atol=.001) for p in parts if p['name'].endswith('low semicircular bath enclosure'))
checks['four_stair_body_heights']=all(np.isclose(bounds(p)[1,2]/S-BASE,10.2,atol=.001) for p in parts if p['name'].endswith('court staircase envelope'))
checks['four_stair_caps_1m_proxy']=all(np.isclose(bounds(p)[1,2]/S-BASE,11.2,atol=.001) for p in byname('Small stair roof cap'))
checks['fourteen_thin_shelter_slopes']=sum(p['name'].endswith('thin sheet slope') for p in parts)==14
checks['raised_shelter_bounds']=all(np.allclose((bounds(p)/S)[:,2]-BASE,[12.4,13.6],atol=.001) for p in parts if p['name'].endswith('thin sheet slope'))
checks['hall_monitor_top17m']=np.isclose(bounds(byname('Hall monitor gable')[0])[1,2]/S-BASE,17,atol=.001)
checks['south_strip_three_decks']=len(byname('South external strip deck'))==3
checks['northwest_projection_one_level']=np.isclose(bounds(byname('North west ground projection')[0])[1,2]/S-BASE,4.3,atol=.001)
checks['northeast_connection_F2deck']=np.isclose(bounds(byname('North east raised connection deck')[0])[1,2]/S-BASE,4.3,atol=.001)
checks['courtyard_long_72_proxy_windows']=sum(p['name'].startswith('Court long') and p['name'].endswith('opaque pane') for p in parts)==72
checks['courtyard_short_32_proxy_windows']=sum(p['name'].startswith('Court short') and p['name'].endswith('opaque pane') for p in parts)==32
checks['eight_chamfer_leaf_recesses']=len(byname('Court diagonal ground door cutter'))==8
checks['eight_chamfer_upper_panes']=len(byname('Court diagonal upper plain pane'))==8
checks['source1939RC']=any('1939 RC' in p['evidence'] for p in parts)
checks['survey_added_roof_not_original']=all('later iron-sheet roof addition' in p['evidence'] for p in parts if p['name'].endswith('thin sheet slope'))
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
def empty(a,b):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);a[2]+=BASE;b[2]+=BASE
 return abs((rebuilt ^ mf.Manifold.cube(((b-a)*S).tolist()).translate((a*S).tolist())).volume())<1e-8
for name,a,b in [
 ('main_court',[30,60,.5],[60,130,9]),
 ('north_small_court',[20,18,.5],[24,30,9]),
 ('south_small_court',[69,18,.5],[73,30,9]),
 ('north_shelter_airgap',[5,60,10.6],[10,80,11.7]),
 ('south_shelter_airgap',[80,60,10.6],[85,80,11.7]),
 ('west_outer_shelter_airgap',[20,4,10.6],[30,8,11.7]),
 ('east_shelter_airgap',[30,153,10.6],[35,157,11.7]),
 ('south_strip_lower_open',[93,60,.5],[95,70,3.5]),
 ('south_strip_upper_open',[93,60,5.6],[95,70,9]),
 ('east_upper_middle_open',[50,168,5.6],[60,173,9]),
 ('northeast_connection_no_tower',[-14,147,5.6],[-5,150,9]),
 ('northeast_connection_end_open',[-16,147,4.5],[-15.7,150,5.1])]:checks[name+'_empty']=empty(a,b)
# Check paired central frames in the final CSG, not only construction metadata.
from collections import defaultdict
fg=defaultdict(list)
for p in parts:
 if p['name'].endswith(' door frame'):fg[p['name']].append(p)
central=[ps[1] for ps in fg.values() if len(ps)==3]
central += byname('Court diagonal doorframe')[1::3]
ratios=[]
for p in central:
 q=mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64)))
 ratios.append((rebuilt^q).volume()/q.volume())
detail['paired_central_frame_retained_volume_ratios']=ratios
checks['paired_central_frames_survive_final_cuts']=len(central)>=10 and all(x>.999 for x in ratios)
checks['north_host_field10_has_no_recess_cutter']=not any(p.get('operation')=='subtract' and 'north exterior field10 level0' in p['name'] for p in parts)
probe=mf.Manifold.cube([.18*S,.1*S,1*S]).translate([.02*S,45.85*S,(BASE+1)*S])
checks['north_host45_9_plainwall_solid']=((rebuilt^probe).volume()/probe.volume())>.999
checks={k:bool(v) for k,v in checks.items()};result={'checks':checks,'passed':all(checks.values()),'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent CSG/source-index/format check; not trial print or exact complete historic reconstruction.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'checks':checks,'volume_delta':detail['relative_volume_delta']},indent=2))

assert result["passed"], "Independent model checks failed"
