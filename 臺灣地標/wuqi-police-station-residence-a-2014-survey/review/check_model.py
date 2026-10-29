from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,sys
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else out.parent
parts=json.loads((root/'construction-parts.json').read_text());checks={};detail={}
named={p['name']:p for p in parts};byname=lambda n:[p for p in parts if p['name']==n]
bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
S=10.;BASE=.2
checks['timber_dimensions']=np.allclose(np.ptp(np.array(named['Timber office weatherboard body']['vertices']),axis=0)/S,[5.67,4.93,2.96],atol=.002)
checks['RC2_extent']=np.allclose(bounds(named['Later two-storey RC mass'])/S,[[0,4.93,.2],[3.52,10.227,6.85]],atol=.002)
checks['flat_roof_not_parapet_height']=np.isclose(bounds(named['1931 actual roof slab'])[1,2]/S-BASE,4.58,atol=.002)
checks['frontcrest685']=np.isclose(bounds(named['Asymmetrical front ornamental parapet'])[1,2]/S-BASE,6.85,atol=.002)
checks['timber_ridge480']=np.isclose(bounds(named['Timber office gable roof'])[1,2]/S-BASE,4.8,atol=.002)
checks['A_roof576']=np.isclose(bounds(named['Residence A stepped main roof'])[1,2]/S-BASE,5.76,atol=.002)
checks['A_low_corridor280']=np.isclose(bounds(named['Residence A north low corridor'])[1,2]/S-BASE,2.8,atol=.002)
checks['A_lean_roof313']=np.isclose(bounds(named['Residence A low north lean-to'])[1,2]/S-BASE,3.13,atol=.002)
checks['A_far_rear_plane']=np.isclose(bounds(named['Residence A far rear gable brick'])[1,1]/S,15.547,atol=.002)
checks['A_short_rear_plane']=np.isclose(bounds(named['Residence A short rear brick gable'])[1,1]/S,13.69,atol=.002)
checks['RC_back_windows_not_mirrored']=np.isclose(np.ptp(np.array(named['A103 rear ground opaque glazing']['vertices'])[:,0])/S,.822,atol=.002) and np.isclose(np.ptp(np.array(named['A103 rear upper opaque glazing']['vertices'])[:,0])/S,1.2,atol=.002)
checks['existing_lamp_not_restored_badge']='Existing central red lamp' in named and not any('旭日' in p['name'] or '黨徽' in p['name'] for p in parts)
checks['entry_three_steps']=sum(p['name'].startswith('Three entry steps ') for p in parts)==3
checks['four_tallframe_uprights']=sum(p['name'].startswith('Tall rectangular feature upright ') for p in parts)==4
checks['tallframe_top960']=all(np.isclose(bounds(p)[1,2]/S-BASE,9.6,atol=.002) for p in parts if p['name'].startswith('Tall rectangular feature upright '))
checks['far_gable_outside_roof_edge']=bounds(named['Residence A far rear gable brick'])[1,1]>bounds(named['Residence A stepped main roof'])[1,1]
checks['short_gable_outside_roof_edge']=bounds(named['Residence A short rear brick gable'])[1,1]/S>13.65
checks['no_invented_timber_front_transoms']=not any(p['name'].startswith('A102 front ') and 'separate transom' in p['name'] for p in parts)
for n in ['Rear tallbay1 current small window','Rear tallbay2 current small window','Rear horizontal window','Rear gable window']:
 checks[n+'_visible_outerplane']=bounds(named[n+' opaque glazing'])[1,1]/S>15.547
D=np.load(root/'mesh-data.npz');v=D['vertices'];f=D['faces'];m=trimesh.Trimesh(v,f,process=False)
# Inspect actual final exposed outward-facing mesh, not only component existence.
centres=m.triangles_center/S;centres[:,2]-=BASE
mask=(centres[:,0]<.01)&(centres[:,0]>-.15)&(centres[:,1]>1.8)&(centres[:,1]<3.1)&(centres[:,2]>3.6)&(centres[:,2]<4.4)&(m.face_normals[:,0]<-.5)
detail['timber_triangle_exposed_material_ids']=np.unique(D['materials'][mask]).tolist()
checks['timber_gable_boardjoints_exposed_final_mesh']=np.sum(m.area_faces[mask & (D['materials']==1)])>.1
checks['timber_gable_exposed_painted_not_rooftile']=np.sum(m.area_faces[mask & (D['materials']==0)])>20 and not np.any(D['materials'][mask]==2)
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
checks['materials_ids_valid']=bool(np.all((D['materials']>=0)&(D['materials']<11)))
checks['all_parts_manifold']=all(mf.Manifold(mf.Mesh64(np.array(p['vertices'],dtype=np.float64),np.array(p['faces'],dtype=np.uint64))).status()==mf.Error.NoError for p in parts)
def probe(a,b):
 a=np.array(a,float);b=np.array(b,float);a[2]+=BASE;b[2]+=BASE
 return mf.Manifold.cube(((b-a)*S).tolist()).translate((a*S).tolist())

for n,a,b in [('timber_gable_overhang_air',[-.20,2,3.9],[-.10,2.9,4.2]),('entry_recess_open',[8.2,.04,.8],[9.4,.20,2.2]),('A_rear_notch_clear_beyond_canopy',[10,14.2,.6],[11.5,15,4]),('tallframe_open',[8.4,5.05,8.0],[8.8,5.6,8.4]),('lowcorridor_not_fullheight',[4.3,11,3.35],[4.8,12,4.0])]:
 checks[n]=abs((rebuilt^probe(a,b)).volume())<1e-6
for n,a,b in [('RC_two_storey_solid',[1,6,4],[2,7,6]),('A_roof_return_solid',[9.26,14,4],[9.34,14.5,4.8])]:
 q=probe(a,b);checks[n]=(rebuilt^q).volume()/q.volume()>.99
checks={k:bool(v) for k,v in checks.items()}
result={'passed':all(checks.values()),'checks':checks,'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent2014-10 surveyed connected office/ResidenceA geometry, controls and CSG/format audit. Raster controls±3%/local0.2m; not detailed interiors or structural/printing certification. Visual review separate.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed'],'Independent checks failed'
