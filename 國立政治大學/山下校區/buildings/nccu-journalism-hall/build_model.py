"""NCCU Journalism Hall — source-relative approximate complete main-building exterior."""
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
palette=[('muted_red_spandrel','#995D53',255),('weathered_ivory_frame','#D6D4C6',255),('opaque_glazing_proxy','#607779',255),('turquoise_awning','#478B85',255),('flat_roof_concrete','#A4A69B',255),('bounded_contact_stone','#8A897B',255),('entry_pale_stone','#B9B3A1',255)]
def poly(points,z0,z1):return CrossSection([points],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def trace(points):return [((x-75)/14,(310-y)/14) for x,y in points]
def pxbox(x0,x1,y0,y1,z0,z1,c,n):
 a,b=trace([(x0,y1),(x1,y0)]);add(cube(a[0],b[0],a[1],b[1],z0,z1),c,n)
# Master672 reading image. Shared stairs:671 translation(-21,-12),673(-16,-1).
# One-floor opposite foyer is separate from the photographed lower-side entrance.
outline_px=[(75,174),(393,174),(393,108),(472,108),(472,174),(784,174),(784,296),(518,296),(518,309),(344,309),(344,296),(75,296)]
outline=trace(outline_px)
add(CrossSection([outline],fillrule=__import__('manifold3d').FillRule.EvenOdd).offset(.12).extrude(.65),5,'bounded_footprint_contact_not_campus_terrain')
# Enclosed main rooms are exterior mass proxies, not falsely surveyed interiors.
pxbox(75,784,174,296,.60,8.8,1,'complete_two_storey_long_wings')
# Recessed1F central entrance cut out of room mass before material union.
a,b=trace([(392,312),(472,267)])
parts[-1]=(parts[-1]-cube(a[0],b[0],a[1],b[1],1.60,5.05)).as_original();material_for_id[parts[-1].original_id()]=1
pxbox(393,472,108,174,.60,5.20,1,'671_1F_only_rear_projecting_foyer')
pxbox(391,474,106,176,5.15,5.36,4,'one_floor_foyer_flat_cap_no_tall_rear_wing')
# Central3F occupied body: registered stair and rooms, plus small side room.
pxbox(344,518,174,309,5.05,12.4,1,'672_673_central_second_third_floor_rooms')
pxbox(518,574,218,261,8.68,12.4,1,'673_third_floor_small_side_room')
pxbox(344,518,174,309,12.35,12.6,4,'central_true3F_flat_roof')
pxbox(518,574,218,261,12.35,12.6,4,'small_side_room_flat_roof')
# Low wings roof terraces and low parapet + open metal-like top rails.
for lo,hi in [(75,344),(518,784)]:
 pxbox(lo,hi,174,296,8.72,8.95,4,'673_open_wing_roof_terrace_slab')
 for yy in [174,296]:
  pxbox(lo,hi,yy-1.3,yy+1.3,8.92,9.32,0,'668_low_wing_roof_edge')
  pxbox(lo,hi,yy-.65,yy+.65,9.66,9.74,1,'668_roof_terrace_top_rail')
  for xx in range(lo+3,hi,30):pxbox(xx,xx+1.3,yy-.65,yy+.65,9.29,9.70,1,'roof_rail_posts_approximate_spacing')
 for xx in [lo if lo==75 else hi]:
  pxbox(xx-1.3,xx+1.3,174,296,8.92,9.32,0,'low_wing_end_roof_edge')
  pxbox(xx-.65,xx+.65,174,296,9.66,9.74,1,'low_wing_end_top_rail')
  for yy in range(176,296,30):pxbox(xx-.65,xx+.65,yy,yy+1.3,9.29,9.70,1,'roof_end_rail_post')
#668 lower-side front: narrow repeated white fins with red opaque inter-floor band.
pxbox(349,513,308.5,310,7.5,9.95,0,'668_opaque_red_spandrel_not_glass')
pxbox(349,513,308.5,310,11.95,12.35,0,'668_upper_red_band')
def front_window(x0,x1,y,z0,z1,label):
 pxbox(x0,x1,y-.6,y+.6,z0,z1,2,label)
 for x in [x0,(x0+x1)/2,x1]:pxbox(x-.55,x+.55,y+.4,y+1.4,z0-.035,z1+.035,1,'pale_window_mullion')
 for z in [z0,z0+.70,z1]:pxbox(x0-.55,x1+.55,y+.4,y+1.4,z-.035,z+.035,1,'pale_window_transom')
for j in range(12):
 x=350+j*13.4
 front_window(x+1,x+12.0,310,5.48,7.50,'668_second_storey_glazing')
 front_window(x+1,x+12.0,310,9.96,11.95,'668_third_storey_glazing')
for j in range(13):
 x=348+j*13.8;pxbox(x-1.0,x+1.0,309,315,5.08,12.36,1,'668_continuous_white_vertical_fin')
for x in [344,516]:pxbox(x-2,x+2,308,316,1.55,12.6,1,'668_central_outer_frame_pier')
pxbox(342,520,308,316,12.33,12.65,1,'668_central_top_frame')
# Wings:2F horizontal glazing and thin turquoise sunshades. Unseen rear neutral.
for lo,hi in [(75,344),(518,784)]:
 for z in [1.60,5.20]:
  for j in range(5):
   w=(hi-lo)/5;front_window(lo+j*w+5,lo+(j+1)*w-5,296,z+.60,z+2.8,'668_low_wing_front_glazing_approx_bays')
  pxbox(lo+1,hi-1,295.5,305,z+2.95,z+3.07,3,'668_turquoise_front_awning')
  pxbox(lo+1,hi-1,295.5,297,z+.35,z+.55,0,'wing_red_sill_band')
#669 tree-obscured local corner: side glazing on central protrusion, not opposite full facade.
for z in [5.20,8.80]:
 pxbox(517.4,518.6,267,302,z+.6,z+2.75,2,'669_candidate_local_central_side_window')
 for yy in [267,284.5,302]:pxbox(518.2,519.5,yy-.6,yy+.6,z+.55,z+2.80,1,'local_side_window_frame')
 for zz in [z+.55,z+1.25,z+2.8]:pxbox(518.2,519.5,267,302,zz-.04,zz+.04,1,'local_side_transom')
 pxbox(517.6,526,266,303,z+2.95,z+3.07,3,'669_local_side_turquoise_awning')
# Main1F entrance stands recessed beneath occupied second floor and broad canopy.
pxbox(395,469,266.4,267.6,1.60,4.5,2,'668_recessed_fullheight_entry_door_glazing')
for xx in [395,407.3,419.6,431.9,444.2,456.5,469]:pxbox(xx-.55,xx+.55,267.4,268.4,1.60,4.55,1,'668_vertical_door_leaf_frames')
for zz in [1.62,3.95,4.52]:pxbox(394.5,469.5,267.4,268.4,zz-.04,zz+.04,1,'668_entry_threshold_and_upper_transom_not_low_window_bar')
pxbox(343,519,307,333,4.98,5.24,0,'668_broad_entry_canopy')
pxbox(343,519,330,334,4.87,5.32,0,'668_canopy_deep_rounded_profile_approx_rectangular_edge')
#1F broad entry landing and five bounded stairs, not arbitrary ground slab.
pxbox(340,522,295,321,.60,1.60,6,'668_entry_top_landing')
for i in range(6):
 pxbox(334-i*2,528+i*2,320+i*5,326+i*5,.0,1.60-(i+1)*.20,6,'668_broad_front_tread_grounded')
#1F rear foyer has its own low doorway and naturally bounded threshold.
pxbox(419,449,107.4,108.6,.75,3.75,2,'671_opposite_foyer_door_proxy')
pxbox(415,453,99,109,0,.7,6,'rear_foyer_threshold_contact')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學新聞館','revision':'v2','scope':'complete long two-storey wings, central3F and small side room,1F opposite projecting foyer, wing roof terraces, attached entry canopy and grounded steps','coordinate_transform':'672 master X=(px-75)/14 Y=(310-py)/14, scale4mm per approximate unit','outline_reading_pixels':outline_px,'shared_plan_registration':{'671_translation_px':[-21,-12],'672_master':True,'673_translation_px':[-16,-1],'stair_center_master':[425,204],'method':'translation on shared stair and repeated column spacing, never independent full-page scaling'},'photo_mapping':{'668':'lower-side central front, y309, same mesh','669':'candidate local side corner, obscured by trees; not uniquely recovered full reverse facade'},'limits':['Fire equipment diagrams not survey/as-built','Photo capture years unknown, not verified2026 condition','No independent roof or elevations; approximate flat caps and heights','Unknown rear kept neutral, fine windows/colours approximate','No physical print or support-free claim']}
# Coalesce same-material construction primitives before final material Boolean. This removes
# artificial coplanar construction seams without nearest recolouring across material boundaries.
grouped=[];group_material_ids={}
for col in range(len(palette)):
 same=[part for part,record in zip(parts,part_records) if record['material']==col]
 g=Manifold.batch_boolean(same,OpType.Add).as_original().set_tolerance(.001).simplify(.001)
 group_material_ids[g.original_id()]=col;grouped.append(g)
parts=grouped;material_for_id=group_material_ids
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
# Preserve Boolean run provenance through simplification: never nearest-surface paint broad triangles.
m=m.set_tolerance(.001).simplify(.001)
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
