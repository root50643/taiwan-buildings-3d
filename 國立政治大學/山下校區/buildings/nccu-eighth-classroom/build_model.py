"""NCCU Eighth Classroom — source-relative approximate complete main-building exterior."""
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
palette=[('warm_white_stucco','#DBD9CE',255),('terracotta_side_panel','#BC7158',255),('opaque_teal_glazing_proxy','#386567',255),('dark_metal_frames','#434B4C',255),('grey_low_roof_envelope','#62686A',255),('bounded_stone_steps','#99968A',255)]
def q(v):return round(v*1024)/1024
def cube(x0,x1,y0,y1,z0,z1):
 x0,x1,y0,y1,z0,z1=map(q,(x0,x1,y0,y1,z0,z1));return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def b(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
# Common normalized plan derived from571/572 after their statedCCW orientation.
# X left to right; front corridor negativeY. Not geographic north or surveyed metres.
b(-15,15,-5.5,5.5,0,.65,5,'bounded_attached_foundation_and_ground_floor_landing')
# Ground rooms stop behind true3.2deep corridor, except the rightmost display room.
b(-11.8,15,-2.3,5.5,.60,4.2,0,'571_ground_recessed_rooms_and_back_wall')
b(-15,-11.7,2.7,5.5,.60,4.2,0,'571_left_stair_rear_service_room')
b(-15,-14.65,-2.3,5.5,.60,4.25,0,'left_short_side_solid_wall_not_glass')
b(9.2,15,-5.5,-2.2,.60,4.25,0,'571_far_right_display_room_closes_corridor')
# First-floor soffit/slab with actual common stairwell hole, not filled solely for QA.
slab=cube(-15,15,-5.5,5.5,4.12,4.43)-cube(-14.6,-12.85,-2.25,1.55,4.0,4.6)
add(slab,0,'572_slab_with_common_left_stairwell_opening')
b(-11.8,15,-2.3,5.5,4.40,8.50,0,'572_upper_room_mass_behind_glass_corridor')
b(-15,-11.7,2.7,5.5,4.40,8.50,0,'572_upper_left_rear_room_mass')
b(-15,-14.65,-2.3,5.5,4.40,8.50,0,'569_upper_short_side_white_solid_wall')
b(-14.75,-11.7,2.45,2.8,4.4,8.5,0,'upper_stair_rear_wall')
# Actual internal stair connects 1F open colonnade to2F enclosed corridor air.
for i in range(16):
 y=-2.2+i*.25;z=.65+(i+1)*(3.78/16)
 b(-14.5,-12.9,y,1.80,.60,z,5,'common_left_stair_tread_riser_approx')
b(-14.6,-11.7,1.55,2.48,4.12,4.43,0,'common_upper_stair_landing')
# Ground-floor free standing columns under glass elevation; nofake full open farend.
for x in [-14.4,-10.4,-6.4,-2.4,1.6,5.6,9.4]:b(x-.19,x+.19,-5.48,-5.05,.61,4.22,3,'568_ground_colonnade_structural_pier')
# Opaque glazing as thin material surfaces, hollow true corridor behind.
b(-15,15,-5.5,-5.33,4.40,8.48,2,'568_upper_front_glazed_corridor_plane')
b(-15,-14.83,-5.5,-2.25,4.4,8.48,2,'569_left_glazing_return_only_corridor_width')
b(14.83,15,-5.5,-2.25,4.4,8.48,0,'unknown_far_short_return_neutral_not_glass_mirror')
# Front glass horizontal transoms and vertical mullions approximate observed cadence.
for x in np.arange(-14.95,15.01,1.5):b(x-.04,x+.04,-5.56,-5.30,4.4,8.50,3,'front_glass_vertical_frame_approx')
for z in [4.42,4.73,5.30,7.46,8.12,8.46]:
 b(-15.04,15.04,-5.57,-5.29,z-.045,z+.045,3,'front_glass_horizontal_transom_approx')
 b(-15.07,-14.78,-5.55,-2.27,z-.045,z+.045,3,'short_corner_glass_transom')
for y in [-5.45,-4.4,-3.3,-2.3]:b(-15.07,-14.78,y-.04,y+.04,4.4,8.50,3,'short_corner_glass_vertical_frame')
# Thin opaque windows/doors lie on actual recessed white backwall.
for x in [-10.4,-6.4,-2.4,1.6,5.6]:
 b(x-.50,x+.50,-2.36,-2.26,.65,3.35,3,'recessed_ground_door_opaque_proxy')
 b(x+1.0,x+2.05,-2.36,-2.26,1.35,3.35,2,'recessed_ground_window_opaque_proxy')
b(10.1,11.3,-5.56,-5.45,.65,3.35,3,'far_end_display_room_door_proxy')
#569 leftwall orange rectangular tilezone: one side only, no sourcepixel texture.
b(-15.035,-14.96,-.20,3.50,1.75,7.55,1,'569_left_short_side_terracotta_rectangular_panel')
# Tile joints shallow solid darker lines are omitted, not guessed imagery.
# Two distinct grounded short stair interfaces per571, orthogonal at left/front.
for i in range(3):
 h=.65-i*.19;reach=(i+1)*.33
 b(-15-reach,-14.95,-5.5,-2.55,0,h,5,'571_left_short_end_three_step_access')
 b(-14.05,-8.75,-5.5-reach,-5.45,0,h,5,'571_front_long_side_three_step_access')
# Low source-limited roof closure. Nofull ridge/hip/gableassertion for unseen roof.
b(-15.45,15.45,-5.87,5.82,8.43,8.64,4,'low_roof_envelope_unmeasured_unseen_back_roof')
# Seen front eave/shortreturn cap only; small raised ridge segmentnotwholelongridge.
b(-15.46,15.46,-5.91,-5.58,8.60,8.77,4,'569_visible_front_grey_eave_cap')
b(-15.48,-15.12,-5.91,5.84,8.60,8.77,4,'569_visible_left_short_eave_cap')
# bounded observed short triangular fold, low & local. Not a complete roof taxonomy.
v=np.array([[-15.3,-.1,8.62],[-14.4,-.1,8.62],[-15.3,1.0,9.05],[-14.4,1.0,9.05],[-15.3,2.1,8.62],[-14.4,2.1,8.62]])
tm=trimesh.convex.convex_hull(v);add(Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32))),4,'569_seen_local_short_fold_low_envelope_proxy')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學第八教室／校友服務中心','inventory':'60-9 / mapA11(09), singleidentity','revision':'v2','scope':'complete two-storey rectangle, actual ground colonnade, farend enclosed display room, common stair core, upper glazed corridor and restricted corner, both grounded short stair interfaces, boundedlowroof','coordinate_transform':'common frame left-to-rightX, front negativeY; normalized approximate30x11 units at4mm/unit; not surveyed dimensions or north','source_registration':{'571':'CCW90reading, firstfloorleftstair/backwall/rightclosedroom','572':'CCW90reading, commonstair/core/frontcorridor, normalizedsameouterframe'},'limits':['Official fire safety schematics not measured as-built','Capture date unknown, not2026condition','Low roof envelope only; no recovered fullroof type/ridgelength/rearslope','Heights, finewindows, tilepattern and colors approximate','Unseen rear kept neutral','No physical print or supportfree claim']}
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
