"""NCCU Health Center — source-relative approximate complete main-building exterior."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,JoinType
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NCCU source observations.
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(c,s,col,name):add(Manifold.cube(s,True).translate(c),col,name)
def beam(a,b,w,col,name):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;x=np.cross(z,[0,1,0])
 if np.linalg.norm(x)<.01:x=np.cross(z,[1,0,0])
 x/=np.linalg.norm(x);y=np.cross(z,x);T=np.column_stack([x,y,z,(a+b)/2]);add(Manifold.cube((w,w,L+w*.15),True).transform(T),col,name)
def path(points,w,col,name):
 for a,b in zip(points,points[1:]):beam(a,b,w,col,name)
def ring(x,y,z,s,w,col,name):
 for a,b in [((-s/2,-s/2),(s/2,-s/2)),((s/2,-s/2),(s/2,s/2)),((s/2,s/2),(-s/2,s/2)),((-s/2,s/2),(-s/2,-s/2))]:beam((x+a[0],y+a[1],z),(x+b[0],y+b[1],z),w,col,name)


SCALE=4.0
palette=[('concrete','#A6A397',255),('cream_tile_proxy','#C9C4B1',255),('dark_louver','#353B38',255),('opaque_glass','#455653',255),('pale_frames','#D7D8CB',255),('step_safety_edge','#D5AC30',255)]
# World X=(source original pixel Y-125)/20; Y=(pixel X-125)/20.
# This is a proper in-plane rotation after image Y-down conversion, not mirroring.
# Registered 2F trace; lengths are proportional design units, not surveyed metres.
outline=[(0,0),(20,0),(20,3.5),(25.8,9.0),(29.3,9.0),(33.8,13.2),(23.8,13.2),(23.8,13.8),(20,13.8),(20,13.2),(4,13.2),(4,11.1),(0,11.1)]
def poly(points,z0,z1):return CrossSection([points],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
# Local entrance coordinates u along diagonal, v outwards toward lower-right.
A=np.array([20.,3.5]);B=np.array([25.8,9.]);T=(B-A)/np.linalg.norm(B-A);N=np.array([T[1],-T[0]]);L=float(np.linalg.norm(B-A))
def ep(u,v):return (A+u*T+v*N).tolist()
def local(u0,u1,v0,v1,z0,z1):
 c=A+(u0+u1)/2*T+(v0+v1)/2*N
 return Manifold.cube((u1-u0,v1-v0,z1-z0),True).transform([[T[0],N[0],0,c[0]],[T[1],N[1],0,c[1]],[0,0,1,(z0+z1)/2]])
def front(u0,u1,v0,v1,z0,z1,c,n):add(local(u0,u1,v0,v1,z0,z1),c,n)
# Low outline-following plinth rather than a large rectangular slab hiding the pointed wing.
add(CrossSection([outline]).offset(.45).extrude(.7),0,'outline_following_display_plinth')
ground_outline=[(0,0),(20,0),(20,9),(29.3,9),(33.8,13.2),(23.8,13.2),(23.8,13.8),(20,13.8),(20,13.2),(4,13.2),(4,11.1),(0,11.1)]
add(poly(ground_outline,.65,3.75),1,'1F_recess_follows_real_rectangular_main_and_horizontal_wing_edges')
add(poly(outline,3.65,14.4),1,'2F_to_4F_asymmetric_pointed_wing_and_diagonal_enclosure')
add(poly([(20,3.5),(25.8,9),(20,9)],.65,1.37),0,'low_triangular_entrance_landing_not_filled_room')
block(2.2,4.05,11.05,11.95,.65,10.68,1,'1F_2F_3F_small_opposite_stair_projection_absent_4F_R')
# 1F plan has broad exterior steps; upper diagonal enclosure overhangs them.
block(19.98,20.09,5.35,8.55,1.38,3.35,3,'recessed_entry_glazing_on_real_1F_return_wall')
for y in [5.35,6.95,8.55]:block(19.98,20.17,y-.055,y+.055,1.37,3.4,4,'recessed_entry_vertical_frame')
for i in range(4):front(1.3,L-1.1,-1.16,2.0-i*.46,.65,.78+i*.20,0,'four_short_attached_steps')
for i in range(4):front(1.3,L-1.1,1.87-i*.46,2.0-i*.46,.78+i*.20,.82+i*.20,5,'coarse_yellow_step_nosing')
# Dark broad lower glazing and dense black horizontal shade, only evidenced diagonal entry.
front(1.10,L-1.0,-.06,.15,3.7,5.2,3,'entry_lower_glazed_band')
for u in np.linspace(1.1,L-1.,6):front(u-.055,u+.055,.1,.23,3.65,5.25,4,'lower_glazing_frames')
for z in [3.7,5.2]:front(1.05,L-.95,.11,.24,z-.06,z+.06,4,'lower_glazing_transom')
front(1.08,L-.98,-.06,.10,5.3,13.7,2,'black_shade_backing_opaque_proxy')
for z in np.arange(5.4,13.7,.22):front(1.08,L-.98,.05,.24,z,z+.10,2,'simplified_dense_horizontal_louver')
# Three framed openings in a vertical stack seen on same entrance face; approximate positions/count of blades.
for u0,u1 in [(1.35,2.65),(L-3.1,L-1.8)]:
 for z in [5.67,8.88,11.87]:
  front(u0,u1,-.04,.28,z,z+1.15,3,'two_columns_of_three_visible_framed_louver_openings')
  for u in [u0,u1]:front(u-.05,u+.05,.23,.34,z-.05,z+1.2,4,'opening_side_frame')
  for zz in [z,z+1.15]:front(u0-.05,u1+.05,.23,.34,zz-.05,zz+.05,4,'opening_horizontal_frame')
front(.85,L-.75,-.08,.85,13.75,14.35,1,'projecting_top_entrance_cap')
# Three slim low windows in cream end block, bounded positional interpretation.
for x in [26.2,26.75,27.3]:
 block(x-.16,x+.16,8.91,9.05,1.8,3.3,3,'three_low_windows_on_right_cream_wing_return')
for y in [1.65,2.25,2.85]:
 block(19.98,20.09,y-.17,y+.17,1.8,3.3,3,'three_low_windows_on_left_cream_main_return')
# Roof terrace is open above its deck. Only real R access strip is built, never B1 inset.
add(poly(outline,14.35,14.6),0,'complete_roof_terrace_deck')
cs=CrossSection([outline]);wall=cs-cs.offset(-.20)
add(wall.extrude(.65).translate((0,0,14.55)),1,'low_roof_parapet_open_terrace')
block(.05,13.0,.05,4.55,14.5,17.0,1,'R_access_room_and_stair_strip_approx_height')
block(-.02,13.07,-.02,4.62,17.,17.22,0,'R_access_strip_roof')
# Unknown back/far fenestration intentionally neutral: no replicated entrance windows.
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學健康中心大樓','scope':'complete aboveground1F-4F and R, pointed wing and attached entry; hidden B1 interior omitted','coordinate_transform':'X=(original image Y-125)/20,Y=(original image X-125)/20; image Y-down to world Y-up then proper90deg rotation; no mirror; no compass claim','outline_design':outline,'ground_outline_design':ground_outline,'entrance_A':A.tolist(),'entrance_B':B.tolist(),'entrance_length':L,'nominal_scale_mm_per_approx_design_unit':SCALE,'floor_levels_mm':[.7*SCALE,3.7*SCALE,7.2*SCALE,10.7*SCALE],'roof_mm':14.6*SCALE,'limits':['Proportional emergency-plan trace, not certified as-built or measured scale','Right diagonal entrance registration is bounded topology, not surveyed detail','Exact floor heights and roof strip height approximate','Back/far fine windows neutral; no invented mirror glazing','B1 inset is not roof mass; hidden basement rooms omitted','No 2026 capture date or condition claim','Source rights unresolved; private only, no model-wide CC license','No physical print or support-free guarantee']}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.001).simplify(.001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<1.2,(dist.max(),centers[start:start+500][dist.argmax()].tolist());maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);assert np.all(np.linalg.norm(cr,axis=1)>0),'float32 export degeneracy: repair generator, not QA';nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_provenance_nearest_surface_max_distance_mm=maxdist,parts=part_records)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b,'alpha':c} for a,b,c in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
