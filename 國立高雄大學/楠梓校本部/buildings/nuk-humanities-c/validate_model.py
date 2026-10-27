#!/usr/bin/env python3
"""Raw-mesh, STL and core 3MF consistency checks. No tolerance-based repair or sealing."""
import pathlib,json,zipfile,xml.etree.ElementTree as ET,struct,hashlib,collections
import numpy as np
import trimesh,manifold3d as mf
r=pathlib.Path(__file__).resolve().parent;d=np.load(r/'mesh-data.npz');v=d['vertices'];f=d['faces'];mi=d['materials'];t=trimesh.Trimesh(v,f,process=False)
assert np.isfinite(v).all();assert len(f)>0;assert f.min()>=0 and f.max()<len(v)
tri=v[f];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
edges=np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);ue,cnt=np.unique(edges,axis=0,return_counts=True);assert np.all(cnt==2),np.unique(cnt,return_counts=True)
assert np.all(area>1e-10);assert t.is_watertight and t.is_winding_consistent and t.volume>0
parents=list(range(len(v)))
def find(x):
 while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
 return x
for a,b in ue:
 x,y=find(int(a)),find(int(b));parents[x]=y
components=len({find(i)for i in np.unique(f)});assert components==1
raw=(r/'model.stl').read_bytes();n=struct.unpack('<I',raw[80:84])[0];assert len(raw)==84+n*50 and n==len(f)
a=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')]))
assert np.array_equal(a['vertices'],tri.astype(np.float32))
# Exact-coordinate indexing of STL preserves the file's raw triangles; no epsilon merging.
sv,ix=np.unique(a['vertices'].reshape(-1,3),axis=0,return_inverse=True);sf=ix.reshape(-1,3);st=trimesh.Trimesh(sv,sf,process=False);assert st.is_watertight and st.is_winding_consistent
ns={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(r/'model.3mf')as z:
 assert set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'};root=ET.fromstring(z.read('3D/3dmodel.model'))
assert root.attrib['unit']=='millimeter';objs=root.findall('c:resources/c:object',ns);assert len(objs)==1
verts=root.findall('.//c:vertices/c:vertex',ns);tris=root.findall('.//c:triangles/c:triangle',ns)
v3=np.array([[float(e.get(k))for k in 'xyz']for e in verts]);f3=np.array([[int(e.get(k))for k in ['v1','v2','v3']]for e in tris]);maxerr=float(np.abs(v3-v).max());assert maxerr<1e-6 and np.array_equal(f3,f)
assert all(e.get('pid')=='1' and [e.get(k)for k in ['p1','p2','p3']]==[str(int(m))]*3 for e,m in zip(tris,mi))
base=root.findall('c:resources/c:basematerials/c:base',ns);palette=json.loads((r/'editable-parts.json').read_text())['palette'];assert [x.get('displaycolor')for x in base]==[p['hex']+'FF'for p in palette]
# Reimport into the Boolean engine without any repairing, maintaining the exact indexed topology.
man=mf.Manifold(mf.Mesh(np.asarray(v,np.float32),np.asarray(f,np.uint32)));assert man.status()==mf.Error.NoError
report={'raw_mesh':{'vertices':len(v),'triangles':len(f),'finite':True,'all_edges_incidence_2':True,'min_triangle_area_mm2':float(area.min()),'watertight':True,'winding_consistent':True,'connected_components':components,'positive_volume_mm3':float(t.volume),'manifold_reimport_status':str(man.status()),'no_repair_operations':True},'stl':{'binary_triangle_count':n,'triangle_coordinates_exact_float32_match':True,'raw_triangle_reindexed_exact_coordinates_watertight':True,'epsilon_welding':False},'3mf':{'unit':'millimeter','one_mesh_object':True,'exact_triangle_indices':True,'max_vertex_error_mm':maxerr,'all_face_materials_match':True,'palette_count':len(base),'external_assets':False,'validation':'core XML and full geometry/material roundtrip; not lib3mf strict-reader validation'},'limitations':['No physical print','Boolean manifold and edge checks are not a guarantee of FFF supportability','No full-scale as-built survey or current-state claim','Fine frames, rails and awnings need slicer review; not certified minimum wall thickness']}
(r/'qa').mkdir(exist_ok=True);(r/'qa/mesh-exchange-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
