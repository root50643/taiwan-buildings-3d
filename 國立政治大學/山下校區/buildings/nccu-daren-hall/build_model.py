"""NCCU Daren Hall — source-relative approximate complete main-building exterior."""
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





SCALE=2.5
palette=[('weathered_grey_concrete','#979B94',255),('light_structural_piers','#D0D2C8',255),('opaque_bluegrey_window_proxy','#60777B',255),('aluminium_frames','#B9C3C4',255),('dark_entry_recess','#465150',255),('stone_approach_steps','#B2ADA0',255)]
def q(v):return round(v*1024)/1024
def cube(x0,x1,y0,y1,z0,z1):
 x0,x1,y0,y1,z0,z1=map(q,(x0,x1,y0,y1,z0,z1));return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def b(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
F=.5;H=3.3
b(-30,30,-4.5,4.5,0,F,5,'bounded_main_foundation')
partitions=[[-30,-21.7,-12.7,-5,2,7,13.7,22,30],[-30,-25.7,-20.8,-15.7,-9.3,-3.6,2,7,13.7,18.5,22,30],[-30,-25.7,-20.8,-15.7,-9.3,-3.6,2,7,13.7,18.5,22,30],[-30,-25.7,-20.8,-15.7,-9.3,-3.6,2,7,13.7,18.5,22,30]]
for k in range(4):
 z=F+H*k;zt=z+H
 slab=cube(-30,30,-4.5,4.5,z-.27,z)
 if k:slab-=cube(2.15,6.85,-1.8,3.55,z-.4,z+.1)
 add(slab,1,f'{k+1}F_registered_slab_single_central_stair_opening')
 # Photographs are candidates for the same enclosed corridor facade, not opposing facades.
 wall=cube(-30,30,-4.5,-4.23,z,zt)
 for i in range(28):
  a=-29.6+i*2.125;bb=min(a+1.78,29.7)
  if k==1 and a<7 and bb>2:continue
  wall-=cube(a,bb,-4.6,-4.1,z+.75,z+2.75)
  b(a-.01,bb+.01,-4.4,-4.28,z+.74,z+2.76,2,'front_opaque_window_proxy')
  for xx in [a,(a+bb)/2,bb]:b(xx-.04,xx+.04,-4.58,-4.20,z+.73,z+2.77,3,'front_window_mullion')
  for zz in [z+.75,z+2.05,z+2.75]:b(a,bb,-4.58,-4.20,zz-.04,zz+.04,3,'front_window_transom')
 if k==1:wall-=cube(2.15,6.85,-4.6,-4.1,z,z+2.6)
 if k==0:wall-=cube(2.15,3.2,-4.6,-4.1,z,z+2.4)
 add(wall,0,f'{k+1}F_enclosed_corridor_front_wall')
 # Rear window pattern is explicitly a restrained approximate closure, not source-proven mirroring.
 rear=cube(-30,30,4.23,4.5,z,zt)
 for aa in [-26,-18,-10,-2,10,18,26]:
  rear-=cube(aa-1.15,aa+1.15,4.1,4.6,z+1,z+2.5)
  b(aa-1.16,aa+1.16,4.30,4.42,z+.99,z+2.51,2,'unseen_rear_limited_window_approx')
 add(rear,0,f'{k+1}F_rear_approximate_wall')
 b(-30,-29.7,-4.5,4.5,z,zt,0,'left_short_wall');b(29.7,30,-4.5,4.5,z,zt,0,'right_short_wall')
 roomwall=cube(-29.7,29.7,-1.95,-1.70,z,zt)
 roomwall-=cube(2.1,6.9,-2.1,-1.5,z,z+2.7)
 for aa,bb in zip(partitions[k],partitions[k][1:]):
  if aa==2:continue
  roomwall-=cube(aa+.65,aa+1.6,-2.1,-1.5,z,z+2.35)
 add(roomwall,0,'room_corridor_wall_actual_open_doorways')
 for x in partitions[k][1:-1]:b(x-.12,x+.12,-1.85,4.35,z,zt,1,'source_schematic_room_partition')
 if k:
  service=cube(-29.7,-15.7,.4,.64,z,zt)
  for x in [-28,-23.7,-18.8]:service-=cube(x,x+1.1,.3,.75,z,z+2.2)
  add(service,1,'left_subdivided_service_rooms_not_mirrored_right')
 if k<3:
  # Finite step plates overlap by .03 and rise .183; soffits track the tread heights.
  for i in range(9):
   y=-1.8+i*.5;h=z+(i+1)*H/18
   b(2.18,4.38,y,y+.53,h-.28,h,5,'central_first_flight_finite_plate')
   yr=2.2-i*.5;h=z+H/2+(i+1)*H/18
   b(4.62,6.82,yr,yr+.53,h-.28,h,5,'central_return_flight_finite_plate')
  b(2.18,6.82,2.7,3.5,z+H/2-.28,z+H/2,5,'central_midlanding_finite_slab')
  b(4.62,6.82,-2.12,-1.27,z+H-.27,z+H,1,'central_upper_exit_landing')
for x in [-30]+[-27.55+i*2.125 for i in range(27)]+[30]:
 if 2.01<x<6.99:
  b(x-.14,x+.14,-4.72,-4.25,.45,3.8,1,'entry_pier_lower_only')
  b(x-.14,x+.14,-4.72,-4.25,6.45,13.73,1,'entry_pier_above_canopy_only')
 else:b(x-.14,x+.14,-4.72,-4.25,.45,13.73,1,'visible_full_height_facade_pier')
# Source-visible upper horizontal shades, simplified count and finite thickness.
for zbar in [12.92,13.12,13.32,13.52]:b(-29.9,29.9,-4.92,-4.56,zbar,zbar+.075,3,'visible_top_horizontal_louver_approx')
for x in [-14.8,-2.05,10.70,23.45]:
 for k in range(3):
  for i in range(5):
   zz=.5+k*3.3+1.0+i*.22
   b(x-.23,x+.23,-4.71,-4.50,zz,zz+.07,3,'finite_pier_short_crossmember_approx')
b(-30.2,30.2,-4.7,4.7,13.67,13.97,1,'low_flat_roof_bounded_approximation')
# One common-XY external stair, not separate stairs inferred from duplicate plan levels.
z=F+H
b(1.95,7.05,-6.0,-4.35,z-.3,z,5,'2F_central_entry_landing')
b(1.8,7.2,-6.3,-4.15,z+2.65,z+2.9,1,'photo686_entry_canopy')
for xx in [2.15,6.85]:b(xx-.09,xx+.09,-4.6,-4.2,z,z+2.6,4,'dark_entry_frame')
b(2.15,6.85,-4.6,-4.2,z+2.5,z+2.6,4,'dark_entry_header_open_passage')
# Complete rise to a finite local grade and lower landing, not clipping flight at model datum.
b(1.75,7.25,-12.8,-5.85,0,.18,5,'defined_local_grade_and_lower_landing')
for i in range(18):
 y=-6.0-(i+1)*.33;h=z-(i+1)*(z-.18)/18
 b(2.15,6.85,y,y+.36,.15,max(.20,h),5,'full_external_tread_to_local_grade')
 for a,bb in [(1.90,2.15),(6.85,7.10)]:b(a,bb,y,y+.36,.15,max(.20,h)+.85,0,'stair_flanking_solid_rail')
# Finite attached ramp along same corridor side; pitch/length approximate, not a full landscape.
ramp_points=[[x,y,z] for x,top in [(7.,3.8),(27.,.4)] for y in [-5.95,-4.55] for z in [top-.30,top]]
ramp=trimesh.convex.convex_hull(np.array(ramp_points))
add(Manifold(Mesh(np.array(ramp.vertices,dtype=np.float32),np.array(ramp.faces,dtype=np.uint32))),5,'bounded_ramp_exact_walking_top_endpoints')
b(26.5,28,-6.0,-4.3,0,.40,5,'ramp_lower_local_landing')
for i in range(11):
 x=7+i*2;zz=z+(x-7)/20*(.40-z)
 b(x-.06,x+.06,-6.02,-5.90,zz-.1,zz+.85,3,'ramp_finite_rail_post')
beam((7,-5.96,z+.70),(27,-5.96,1.25),.12,3,'ramp_sloping_rail')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學大仁樓','inventory':'60-20 / A25(20)','revision':'v2','scope':'whole four-storey main body, single central return stair, enclosed corridor,2Fcentral entrance and complete finite approach','coordinate_transform':'Common60x9 normalized schematic frame; CCW plan reading not compass;2.5mm/unit not survey','limits':['Official fire layout not as-built','Unknown photo year not current2026 verification','686 2Fentry and687 samecorridorface bounded candidates','Flat roof rearwindows interior step heights colors and ramp approximate','No basement tower or sourcepixels','No physical print certification']}
# Coalesce same-material construction primitives before final material Boolean. This removes
# artificial coplanar construction seams without nearest recolouring across material boundaries.
grouped=[];group_material_ids={}
for col in range(len(palette)):
 same=[part for part,record in zip(parts,part_records) if record['material']==col]
 g=Manifold.batch_boolean(same,OpType.Add).as_original()
 group_material_ids[g.original_id()]=col;grouped.append(g)
parts=grouped;material_for_id=group_material_ids
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
# Preserve Boolean run provenance through simplification: never nearest-surface paint broad triangles.
m=m.set_tolerance(0.000001).simplify(0.000001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
colors=np.empty(len(fs),dtype=int);maxdist=0
for i,rid in enumerate(me.run_original_id):colors[me.run_index[i]//3:me.run_index[i+1]//3]=material_for_id[rid]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);assert np.all(np.linalg.norm(cr,axis=1)>0),('float32 export degeneracy: repair generator, not QA',tri[np.linalg.norm(cr,axis=1)==0].tolist());nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_assignment_method="Boolean original-run provenance retained through simplification; no nearest recolouring",parts=part_records)
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
