from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent; root=out.parent
parts=json.loads((root/'construction-parts.json').read_text()); checks={}; detail={}
named={p['name']:p for p in parts}; bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
byname=lambda name:[p for p in parts if p['name']==name]
S=10/3;FLOOR=.65;BASE=.6;L=68.435;W=18.18
checks['nineteen_west_high_sashes']=len([p for p in parts if re.match(r'W high sash\d+ surround$',p['name'])])==19
checks['sixteen_east_high_sashes']=len([p for p in parts if re.match(r'E high sash\d+ surround$',p['name'])])==16
checks['nineteen_west_vents']=len([p for p in parts if re.match(r'W base vent\d+$',p['name'])])==19
checks['sixteen_east_vents']=len([p for p in parts if re.match(r'E base vent\d+$',p['name'])])==16
checks['five_front_arch_rect_cuts']=len([p for p in parts if re.match(r'South arcade arch\d rectangular void$',p['name']) and p.get('operation')=='subtract'])==5
checks['five_front_arch_head_cuts']=len([p for p in parts if re.match(r'South arcade arch\d round head$',p['name']) and p.get('operation')=='subtract'])==5
checks['west_return_arch_two_cuts']=all(len(byname(n))==1 and byname(n)[0].get('operation')=='subtract' for n in ['West porch return rectangular void','West porch return round head'])
checks['one_main_gable_only']=len(byname('No1 single longitudinal gable roof'))==1
mb=bounds(byname('No1 main solid envelope')[0])/S
checks['main_footprint_matches_elevation']=np.allclose(mb[1,:2]-mb[0,:2],[L,W],atol=.001)
checks['eave_above_interior_floor']=np.isclose(mb[1,2]-BASE-FLOOR,5.029,atol=.001)
roof=bounds(byname('No1 single longitudinal gable roof')[0])/S
checks['ridge_above_interior_floor']=np.isclose(roof[1,2]-BASE-FLOOR,10.232,atol=.001)
checks['south_arcade_confined_to_No1_width']=np.allclose((bounds(byname('South arcade front wall')[0])/S)[:,1],[0,W],atol=.001)
checks['no_east_arcade_end_wall']=not any('eastern return' in p['name'].lower() for p in parts)
nv=np.array(byname('North low shed enclosure')[0]['vertices'])/S
checks['north_shed_trapezoid']=np.any(np.isclose(nv[:,0],-12.647,atol=.001)) and np.any(np.isclose(nv[:,0],-10.85,atol=.001))
checks['north_two_v_roof_parts']=len(byname('North shallow V shed roof'))==2
checks['north_nine_lattice_diagonals']=len(byname('North visible canopy diagonal'))==9
checks['north_two_sashes']=len([p for p in parts if re.match(r'North shed sash field\d$',p['name'])])==2
checks['east_annex_three_pale_panels']=len([p for p in parts if re.match(r'East attached room panel\d$',p['name'])])==3
checks['no_other_building_joinery_table']=not any('339' in p['evidence'] or '341' in p['evidence'] for p in parts)
checks['roof_terminates_at_gable_planes']=np.allclose(roof[:,0],[0,L],atol=.001)
for side,plane,sign in [('N',0,-1),('S',L,1)]:
 fields=[p for p in parts if re.match(side+r' gable small sash\d opaque pane$',p['name']) or p['name']==side+' gable round vent opaque field']
 checks[side+'_five_gable_fields_project_beyond_roof']=len(fields)==5 and all((bounds(p)[0,0]/S<plane-.09 if sign<0 else bounds(p)[1,0]/S>plane+.09) for p in fields)
for side in ['W','E']:
 fields=[p for p in parts if re.match(side+r' tall wall field\d+$',p['name'])]
 checks[side+'_pale_fields_narrow_1_12m']=all(np.isclose((bounds(p)[1,0]-bounds(p)[0,0])/S,1.12,atol=.001) for p in fields)
 checks[side+'_fields_project_over_courses']=all((bounds(p)[0,1]/S<-.09 if side=='W' else bounds(p)[1,1]/S>W+.09) for p in fields)
 bp=byname(side+' stepped facade buttress');xs=sorted(set(round(bounds(p).mean(axis=0)[0]/S,3) for p in bp))
 raw=[3.308]+[3.636]*17+[3.308];expected=np.cumsum([0]+[q*L/sum(raw) for q in raw])[[9,11,13]]
 checks[side+'_three_three_step_buttresses']=len(bp)==9 and len(xs)==3 and np.allclose(xs,expected,atol=.001)
checks['north_no_central_door_blocking_post']=len(byname('North canopy end upright'))==2 and all(abs(bounds(p).mean(axis=0)[1]/S-W/2)>8 for p in byname('North canopy end upright'))
checks['west_shed_door_neutral_not_glazing']=len(byname('West north shed neutral door'))==1 and byname('West north shed neutral door')[0]['material']==7 and not any('West north shed small door' in p['name'] for p in parts)
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
# Independent solid intersections prove front and return openings are genuinely empty.
probe_volumes=[]
for i in range(5):
 probe=mf.Manifold.cube([.8*S,.6*S,1.0*S]).translate([(L+3.636-.55)*S,((i+.5)*W/5-.3)*S,(BASE+FLOOR+.4)*S])
 probe_volumes.append((rebuilt^probe).volume())
checks['five_front_arches_are_open']=all(abs(v)<1e-8 for v in probe_volumes)
probe=mf.Manifold.cube([.6*S,.8*S,1.0*S]).translate([(L+3.636/2-.3)*S,-.4*S,(BASE+FLOOR+.4)*S])
checks['west_return_is_open']=abs((rebuilt^probe).volume())<1e-8
detail['front_arch_probe_volumes_mm3']=probe_volumes
checks={k:bool(v) for k,v in checks.items()};result={'checks':checks,'passed':all(checks.values()),'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent CSG/source-index/format check; not trial print or exact complete historic reconstruction.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'checks':checks,'volume_delta':detail['relative_volume_delta']},indent=2))

assert result["passed"], "Independent model checks failed"
