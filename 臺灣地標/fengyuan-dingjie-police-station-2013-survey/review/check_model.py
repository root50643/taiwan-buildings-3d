from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,sys
import numpy as np,trimesh,manifold3d as mf
out=Path(__file__).resolve().parent
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else out.parent
parts=json.loads((root/'construction-parts.json').read_text());checks={};detail={}
named={p['name']:p for p in parts};byname=lambda n:[p for p in parts if p['name']==n]
bounds=lambda p:np.array([np.min(p['vertices'],axis=0),np.max(p['vertices'],axis=0)])
S=10.;BASE=.20
mb=bounds(named['Five-sided two-storey main body'])/S
checks['main_dimensions']=np.allclose(mb[1]-mb[0],[11.44,9.19,8.20],atol=.002)
xy=np.unique(np.round(np.array(named['Five-sided two-storey main body']['vertices'])[:,:2]/S,3),axis=0)
checks['five_main_plan_vertices']=len(xy)==5 and all(any(np.allclose(a,b,atol=.002) for a in xy) for b in [[4.65,0],[11.44,0],[11.44,9.19],[0,9.19],[0,4.65]])
for side,x0,x1,h in [('Northern',0,4.63,3.88),('Southern',4.63,11.44,8.08)]:
 p=named[side+' '+('one' if side=='Northern' else 'two')+'-storey eastannex'];bb=bounds(p)/S
 checks[side+'_annex_extent']=np.allclose(bb[0,:2],[x0,9.15],atol=.002) and np.allclose(bb[1,:2],[x1,11.29],atol=.002)
 checks[side+'_annex_height']=np.isclose(bb[1,2]-BASE,h,atol=.002)
 vv=np.array(p['vertices'])/S;inner=vv[np.isclose(vv[:,1],9.15),2].max();outer=vv[np.isclose(vv[:,1],11.29),2].max()
 checks[side+'_annex_roof_falls_east']=inner>outer
st=named['Roof stair enclosure under single slope'];bb=bounds(st)/S
checks['stair_printed_footprint']=np.allclose((bb[1]-bb[0])[:2],[1.835,1.13],atol=.002)
checks['stair_cap_max1040']=np.isclose(bounds(named['Roof stair sloping cap'])[1,2]/S-BASE,10.40,atol=.002)
vst=np.array(st['vertices'])/S
checks['stair_roof_north_high']=vst[np.isclose(vst[:,0],7.08),2].max()>vst[np.isclose(vst[:,0],8.915),2].max()
bases=sorted(byname('Low circular RC roofbase proxy'),key=lambda p:bounds(p)[0,0]);checks['two_RC_bases']=len(bases)==2
checks['RC_base_position_radius']=len(bases)==2 and all(np.allclose((bounds(p).mean(axis=0)/S)[:2],c,atol=.02) and np.allclose((np.ptp(np.array(p['vertices']),axis=0)/S)[:2],[1.2,1.2],atol=.005) for p,c in zip(bases,[[7.89,1.57],[9.30,1.57]]))
checks['RC_base_low_proxy']=all(np.isclose(np.ptp(np.array(p['vertices'])[:,2])/S,.13,atol=.002) for p in bases)
checks['no_tanks']=not any('tank' in p['name'].lower() for p in parts)
checks['blocked_former_door_infill']='west blockedformerdoor1 opaque wall infill' in named
checks['two_noticeboards']=len(byname('Blank opaque noticeboard'))==2
checks['survey_roller_shutter']='Closed iron roller shutter' in named
checks['no_restored_diamondwindow_geometry']=not any('diamond' in p['name'].lower() and 'covering' not in p['name'].lower() for p in parts)
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

for n,a,b in [('roof_no_perimeter_parapet',[10.8,4,8.6],[11.3,5,9.0]),('north_annex_upper_absent',[1,9.6,5],[2,10.6,7]),('chamfer_removed',[.2,.2,.3],[1,1,7])]:
 checks[n]=abs((rebuilt^probe(a,b)).volume())<1e-7
checks['south_annex_upper_present']=(rebuilt^probe([7,9.6,5],[8,10.6,7])).volume()/probe([7,9.6,5],[8,10.6,7]).volume()>.999
# Geometric exposure test: each short crest accent must extend beyond the actual
# raised crest outer plane n=.15m, not merely survive inside a union.
accent_parts=byname('Entrance crest short horizontal accent')
checks['six_crest_accents']=len(accent_parts)==6
exposure=[]
for p in accent_parts:
 vv=np.array(p['vertices'])/S
 normal=(4.65-vv[:,0]-vv[:,1])/np.sqrt(2)
 exposure.append(float(normal.max()))
detail['crest_accent_outer_normal_m']=exposure
checks['crest_accents_outside_crest_face']=len(exposure)==6 and all(x>.19 for x in exposure)
checks={k:bool(v) for k,v in checks.items()}
result={'passed':all(checks.values()),'checks':checks,'detail':detail,'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['build_model.py','mesh-data.npz','model.stl','model.3mf','construction-parts.json']},'scope':'Independent geometry/source-control/CSG/format check of 2013 A-series survey exterior; graphical dimensions ±3%; roof base heights are proxies, not tanks. No trial print or safety certification. Visual approval is separate.'}
(out/'model-independent-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed'],'Independent checks failed'
