"""NCCU Dazhi Hall — source-relative approximate complete main-building exterior."""
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
palette=[('weathered_warm_concrete','#BDBFB6',255),('light_structural_concrete','#DEDED4',255),('opaque_bluegrey_glass_proxy','#657C80',255),('aluminium_frames_and_braces','#B9C3C4',255),('dark_recessed_doors','#465150',255),('bounded_stone_steps','#96978D',255)]
def q(v):return round(v*1024)/1024
def cube(x0,x1,y0,y1,z0,z1):
 x0,x1,y0,y1,z0,z1=map(q,(x0,x1,y0,y1,z0,z1));return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def b(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
# Four equal registered floors: common 60x10 frame; drawings are not surveyed dimensions.
F=.5;H=3.3;cores=[(-29.65,-25.25),(25.25,29.65)]
b(-30,30,-5,5,0,F,5,'bounded_main_foundation_no_full_site')
# Exterior grade at finite right approach only; not a landscape platform.
b(29.8,37.4,-5.2,-2.9,0,.18,5,'finite_external_stair_footing')
partitions=[[-25,-16,-7,-2,2,7,25],[-25,-20.5,-11.5,-7,-2,7,12.5,18,25],[-25,-19.4,-13.8,-8.2,-2.6,3,8.6,14.2,19.8,25],[-25,-19.4,-13.8,-8.2,-2.6,3,8.6,14.2,19.8,25]]
for k in range(4):
 z=F+k*H;zt=z+H; slab=cube(-30,30,-5,5,z-.27,z)
 if k:
  for x0,x1 in cores:slab-=cube(x0,x1,-3.05,1.15,z-.4,z+.1)
 add(slab,1,f'{k+1}F_slab_registered_end_stair_openings')
 # Main classroom wall with actual window apertures and opaque glazing sheets.
 wall=cube(-30,30,4.7,5,z,zt)
 for i in range(13):
  x=-28.7+i*4.4; a=x+.42; bb=min(x+3.78,29.6)
  if bb<=a:continue
  wall-=cube(a,bb,4.6,5.1,z+.72,z+2.85)
  b(a-.02,bb+.02,4.78,4.91,z+.70,z+2.87,2,f'{k+1}F_classroom_window_opaque_proxy')
  for xx in [a,(2*a+bb)/3,(a+2*bb)/3,bb]:b(xx-.045,xx+.045,4.72,5.08,z+.70,z+2.87,3,'classroom_window_frame_approx')
  for zz in [z+.72,z+1.27,z+2.83]:b(a,bb,4.72,5.08,zz-.045,zz+.045,3,'classroom_window_transom_approx')
 add(wall,0,f'{k+1}F_windowed_classroom_long_wall')
 # Unseen corridor elevation is restrained parapet/columns, not mirrored window facade.
 back=cube(-30,30,-5,-4.72,z,zt)
 for xx in [-21,-9,3,15]:back-=cube(xx-.6,xx+.6,-5.1,-4.6,z+1.3,z+2.4)
 add(back,0,f'{k+1}F_unseen_neutral_corridor_wall_limited_openings_approx')
 # Both mostly solid short walls; 2F entry opens only in right corridor extension.
 left=cube(-30,-29.7,-5,5,z,zt);right=cube(29.7,30,-5,5,z,zt)
 if k==0:
  left-=cube(-30.1,-29.6,-4.65,-3.2,z,z+2.5)
 if k==1:right-=cube(29.6,30.1,-4.65,-3.2,z,z+2.5)
 add(left,0,f'{k+1}F_left_short_wall');add(right,0,f'{k+1}F_right_short_wall_entry_if2F')
 # Room/corridor separation with real unclosed door apertures connecting interior air.
 roomwall=cube(-25,25,-3.2,-2.94,z,zt)
 for aa,bb in zip(partitions[k],partitions[k][1:]):
  roomwall-=cube(aa+.6,aa+1.55,-3.3,-2.8,z,z+2.35)
 for x in partitions[k]:b(x-.12,x+.12,-3.2,4.85,z,zt,1,f'{k+1}F_schematic_classroom_partition_approx')
 add(roomwall,0,f'{k+1}F_classroom_corridor_wall_with_doorways')
 # Left single sanitary zone and right paired sanitary zones register handedness.
 for x0,x1 in [(-29.7,-25.0),(25.0,29.7)]:
  service=cube(x0,x1,.95,1.20,z,zt)
  service-=cube(x0+.4,x0+1.35,.8,1.3,z,z+2.25)
  if x0>0:service-=cube(x0+2.65,x0+3.6,.8,1.3,z,z+2.25)
  add(service,1,f'{k+1}F_left_single_service' if x0<0 else f'{k+1}F_right_paired_service')
 b(27.23,27.47,1.0,4.85,z,zt,1,f'{k+1}F_right_service_pair_partition_not_left')
 # Internal two-flight return stairs stay distinct from external approach.
 if k<3:
  for x0,x1 in cores:
   mid=(x0+x1)/2
   for i in range(9):
    y=-3+i*.35; h=z+(i+1)*H/18
    b(x0+.05,mid-.10,y,y+.38,h-.28,h,5,'internal_end_stair_first_flight_thin_step_plate')
    yr=-.2-i*.35;h=z+H/2+(i+1)*H/18
    b(mid+.10,x1-.05,yr,yr+.38,h-.28,h,5,'internal_end_stair_return_flight_thin_step_plate')
   b(x0+.05,x1-.05,.10,.85,z+H/2-.28,z+H/2,5,'internal_end_stair_midlanding_thin_slab')
   b(mid+.10,x1-.05,-3.18,-2.55,z+H-.27,z+H,1,'internal_end_stair_upper_exit_landing')
# Tall piers beside windows and corridor column line shared by all floors.
for x in [-30]+[-25.0+i*4.55 for i in range(12)]+[30]:
 if x>30:continue
 b(x-.15,x+.15,4.91,5.19,.45,13.72,1,'677_full_height_facade_pier_approx')
 b(x-.15,x+.15,-5.12,-4.72,.45,13.72,1,'common_corridor_column_line')
# Selected visible-style reinforced brace bays: approximate, not exact member survey.
for x in [-15,2.6,20.2]:
 for k in range(4):
  z=F+k*H
  beam((x-1.6,5.12,z+.08),(x,5.12,z+3.22),.16,3,'677_reinforcement_diagonal_approx')
  beam((x,5.12,z+3.22),(x+1.6,5.12,z+.08),.16,3,'677_reinforcement_diagonal_approx')
# Flat low roof closure: no RF tower, machinery or additional occupied floor.
b(-30.25,30.25,-5.25,5.25,13.67,13.95,1,'bounded_low_flat_roof_approx')
# 2F narrow longitudinal attached landing and straight outer flight.
# Normalized plan extension 6.8 units; lower endpoint bounded to required ground contact.
z=F+H
b(29.8,31.45,-5,-3.05,z-.30,z,5,'2F_right_external_attached_approach_landing')
for i in range(18):
 x=31.35+i*.30;h=z-(i+1)*(z-.18)/18
 b(x,x+.33,-4.83,-3.22,.10,max(.2,h),5,'676_external_straight_tread_riser_approx')
# Side retaining rails follow stair pitch, not a second building wing.
for yy in [-5.0,-3.2]:
 b(29.8,31.5,yy,yy+.18,z-.3,z+.92,0,'2F_landing_solid_side_rail')
 for i in range(18):
  x=31.35+i*.30;h=z-(i+1)*(z-.18)/18
  b(x,x+.33,yy,yy+.18,.1,max(.2,h)+.92,0,'676_stair_solid_sidewall_approx')
# Abstract metal entry gate, original lettering and logos deliberately absent.
for yy in [-4.6,-4.3,-4,-3.7,-3.4]:b(29.87,30.05,yy-.035,yy+.035,z,z+2.45,4,'676_abstract_entry_gate_bar')
b(29.87,30.05,-4.65,-3.2,z+2.4,z+2.52,4,'676_abstract_entry_gate_header')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學大智樓','inventory':'60-19 / A24(19)','revision':'v3','scope':'whole four-storey narrow main body, both end stairs, single long corridor, asymmetric sanitary plan anchors, finite2Fright landing and full external straight stair','coordinate_transform':'CCW plan-reading X left-to-right, Y positive classroom side; common60x10 normalized units,2.5mm/unit; not geographic north or surveyed metres','source_registration':{'679':'1F shared end stairs left single/right paired service','680':'2F sameframe with right longitudinal approach','681':'3F same mainframe','683':'4F same mainframe'},'limits':['Official fire-layoutschematics not surveyed as-built','Photo676 endentry candidate and677 classroomlongside candidate: no uniquelyproven end/compass','Unknownphotoyear not verified2026condition','Roof approximate lowflat closure no tower','Interior partitions simplified schematic; dimensions heights finewindows braces steps colors approximate','Unseen corridor elevation neutral mostlysolid withlimitedopenings approximate; no mirrored windows asfact','No sourcepixels/logos/lettering included; no physicalprint claim']}
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
