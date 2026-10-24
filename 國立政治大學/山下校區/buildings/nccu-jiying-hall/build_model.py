"""NCCU Jiying Hall — source-relative approximate complete main-building exterior."""
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
palette=[('weathered_ivory_tiles','#CBCBC1',255),('ochre_pebbled_spandrel','#A58F6F',255),('opaque_glazing_proxy','#657A7D',255),('dark_metal_rails','#404C4B',255),('flat_roof_concrete','#A6AAA2',255),('bounded_contact_stone','#999282',255),('muted_teal_entry_fascia','#537F7C',255)]
def q(v):return round(v*1024)/1024
def poly(points,z0,z1):return CrossSection([[(q(x),q(y)) for x,y in points]],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(q(z1)-q(z0)).translate((0,0,q(z0)))
def cube(x0,x1,y0,y1,z0,z1):
 x0,x1,y0,y1,z0,z1=map(q,(x0,x1,y0,y1,z0,z1));return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def trace(points):return [((x-630)/20,(530-y)/20) for x,y in points]
def pb(x0,x1,y0,y1,z0,z1,c,n):
 a,b=trace([(x0,y1),(x1,y0)]);add(cube(a[0],b[0],a[1],b[1],z0,z1),c,n)
def pp(points,z0,z1,c,n):add(poly(trace(points),z0,z1),c,n)
# Shared grid in665 original pixels, common support not independent layer image bounds.
ground=[(300,357),(395,357),(395,277),(870,277),(870,357),(965,357),(965,700),(870,700),(870,780),(395,780),(395,700),(300,700)]
balcony=[(270,327),(365,327),(365,247),(900,247),(900,327),(995,327),(995,730),(900,730),(900,810),(365,810),(365,730),(270,730)]
upper=[(225,350),(385,350),(385,208),(880,208),(880,350),(1040,350),(1040,710),(880,710),(880,855),(385,855),(385,710),(225,710)]
# B1CW transforms to east half only; basement geometry is exterior footing proxy.
basement=[(587,281),(970,281),(970,705),(874,705),(874,788),(587,788)]
pp(basement,0,1.40,5,'661_CW_partial_east_basement_bounded_exterior_footing')
# West half follows rising grade: a thin natural contact/plinth rather than full B1.
pp(ground,1.15,1.65,5,'first_floor_natural_contact_plinth_not_full_basement')
# Narrow perimeter footings ground west side; underside stays open, not full B1 fill.
for a,b in zip(ground,ground[1:]+ground[:1]):
 if min(a[0],b[0])<587:
  if a[0]==b[0]:pb(a[0]-4,a[0]+4,min(a[1],b[1]),max(a[1],b[1]),0,1.30,5,'west_bounded_wall_footing_open_underside')
  else:pb(min(a[0],b[0]),min(max(a[0],b[0]),590),a[1]-4,a[1]+4,0,1.30,5,'west_bounded_wall_footing_open_underside')
# Lower enclosed rooms set behind true open balconies and outer columns.
pp(ground,1.60,5.20,0,'662_complete_ground_rooms_mass_proxy')
pp(ground,5.15,9.0,0,'664_complete_second_floor_recessed_rooms_mass_proxy')
pp(balcony,5.06,5.35,0,'second_floor_true_cantilever_balcony_slab')
# Ground entrance recess on southeast wing; cut before union, keep actual air void.
a,b=trace([(943,696),(970,596)])
gi=next(i for i,r in enumerate(part_records) if r['name']=='662_complete_ground_rooms_mass_proxy');parts[gi]=(parts[gi]-cube(a[0],b[0],a[1],b[1],1.65,4.86)).as_original();material_for_id[parts[gi].original_id()]=0
a,b=trace([(295,464),(322,364)]);parts[gi]=(parts[gi]-cube(a[0],b[0],a[1],b[1],1.65,4.86)).as_original();material_for_id[parts[gi].original_id()]=0
# Third storey cross occupied central rooms; never a lightwell.
pp(upper,9.0,12.55,0,'665_full_cross_third_storey_occupied_central_rooms')
pp(upper,12.50,12.80,4,'bounded_flat_roof_no_invented_equipment')
# Upper sloping shoulder undercut: subtract triangular-prism strips on the short return faces.
# Roof and upper wall remain outermost, lower edge is modestly pulled back.
def shoulder_y(x0,x1,y,sign,name):
 # vertical section triangle, extruded alongx (source approximate slope only)
 pts=[(0,0),(0,3.55),(1.0,0)]
 # custom vertices using bottom out/in; subtraction translated to boundary at z9
 xx0=(x0-630)/20;xx1=(x1-630)/20; yy=(530-y)/20
 vs=np.array([[xx0,yy,9],[xx1,yy,9],[xx0,yy,12.55],[xx1,yy,12.55],[xx0,yy-sign*1.0,9],[xx1,yy-sign*1.0,9]])
 tm=trimesh.convex.convex_hull(vs);return Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)))
third=parts[-2]
for x0,x1,y,sg,n in [(225,385,350,1,'NW'),(880,1040,350,1,'NE'),(225,385,710,-1,'SW'),(880,1040,710,-1,'SE')]:third=third-shoulder_y(x0,x1,y,sg,n)
third=third.as_original();material_for_id[third.original_id()]=0;parts[-2]=third
#665 explicit north/west roofedge strips; no mirrored full-depth east/south eaves.
pb(385,880,167,210,12.45,12.80,0,'665_north_deeper_eave_source_grey_strip')
pb(188,227,350,710,12.45,12.80,0,'665_west_deeper_eave_source_grey_strip')
pb(1038,1048,350,710,12.48,12.80,0,'east_bounded_thin_roof_edge')
pb(385,880,853,863,12.48,12.80,0,'south_bounded_thin_roof_edge')
for x in [395,490,585,680,775,870]:pb(x-2,x+2,170,213,12.22,12.50,0,'north_eave_support_beam_proxy')
for y in [357,470,585,700]:pb(191,230,y-2,y+2,12.22,12.50,0,'west_eave_support_beam_proxy')
# Visible structural support grid at facade corners with intermediate columns.
for x in [300,395,490,585,680,775,870,965]:
 for y in ([357,700] if x in [300,965] else [277,780]):
  pb(x-5,x+5,y-5,y+5,1.35,9.05,0,'real_two_storey_columns_not_painted')
# Long open balcony fronts: opaque lower panels and distinct open rails.
for x0,x1,y,out in [(365,900,247,-1),(365,900,810,1)]:
 pb(x0,x1,y-3,y+3,5.30,6.08,1,'photo_brown_balcony_spandrel')
 pb(x0,x1,y-1,y+1,6.48,6.55,3,'balcony_continuous_open_top_rail')
 for x in range(x0+4,x1,24):pb(x,x+1.5,y-1,y+1,6.03,6.52,3,'balcony_open_rail_posts')
for y0,y1,x in [(327,730,270),(327,730,995)]:
 pb(x-3,x+3,y0,y1,5.30,6.08,1,'side_balcony_brown_spandrel')
 pb(x-1,x+1,y0,y1,6.48,6.55,3,'side_balcony_open_top_rail')
 for y in range(y0+4,y1,24):pb(x-1,x+1,y,y+1.5,6.03,6.52,3,'side_balcony_rail_posts')
# Return balcony parapets join facade, do not seal balcony air.
for x0,x1,y in [(270,365,327),(900,995,327),(270,365,730),(900,995,730)]:pb(x0,x1,y-2,y+2,5.30,6.08,0,'short_return_balcony_edge')
for x,y0,y1 in [(365,247,327),(900,247,327),(365,730,810),(900,730,810)]:pb(x-2,x+2,y0,y1,5.30,6.08,0,'short_return_balcony_edge')
# Window bands are opaque proxies; real setback lower floors is geometric.
def win_y(x0,x1,y,z0,z1,label):
 pb(x0,x1,y-1,y+1,z0,z1,2,label)
 for x in np.arange(x0,x1+1,23):pb(x-.65,x+.65,y-1.5,y+1.5,z0,z1,0,'window_vertical_frames_approx')
 for z in [z0,z0+(z1-z0)*.72,z1]:pb(x0,x1,y-1.5,y+1.5,z-.035,z+.035,0,'window_transom_approx')
def win_x(y0,y1,x,z0,z1,label):
 pb(x-1,x+1,y0,y1,z0,z1,2,label)
 for y in np.arange(y0,y1+1,23):pb(x-1.5,x+1.5,y-.65,y+.65,z0,z1,0,'side_window_vertical_frames')
 for z in [z0,z0+(z1-z0)*.72,z1]:pb(x-1.5,x+1.5,y0,y1,z-.035,z+.035,0,'side_window_transom')
for z in [1.65,5.35]:
 for y in [277,780]:win_y(402,863,y,z+.45,z+3.0,'lower_floor_recessed_window_band')
 for x in [300,965]:win_x(470 if x==300 and z==1.65 else 365,590 if x==965 and z==1.65 else 692,x,z+.45,z+3.0,'lower_floor_side_recessed_window_band')
# Top bands: brown spandrels and framed glazing; short wing return walls remain ivory.
for y in [208,855]:
 pb(391,874,y-1,y+1,9.0,9.97,1,'third_storey_brown_spandrel')
 win_y(395,870,y,10.0,12.25,'upper_band_glazing_proxy')
 for x in [395,490,585,680,775,870]:pb(x-2,x+2,y-4,y+4,9.0,12.60,0,'upper_visible_pier')
for x in [225,1040]:
 pb(x-1,x+1,354,706,9.0,9.97,1,'upper_side_brown_spandrel')
 win_x(358,702,x,10.0,12.25,'upper_side_glazing_proxy')
 for y in [357,470,585,700]:pb(x-4,x+4,y-2,y+2,9.0,12.60,0,'upper_side_pier')
# Photo658 east entrance near southeast end: actual air recess and opaque doorplane.
win_x(600,692,943,1.66,4.70,'658_recessed_fullheight_entry_door')
win_x(368,460,322,1.66,4.70,'662_west_recessed_fullheight_entry_door')
pb(248,320,358,470,4.88,5.18,0,'658_west_candidate_broad_attached_entry_canopy')
pb(246,252,358,470,4.80,5.38,6,'658_west_candidate_muted_teal_fascia_no_source_texture')
# 662CCW southeast bent outer stair naturally follows diagonal corner landing.
for i in range(8):
 e=i*5;z=1.65-i*.19
 pts=[(775,780),(870,780),(870,700),(965,700),(965,580),(1005+e,580),(1005+e,700),(865,840+e),(775,840+e)]
 pp(pts,0,z,5,'662_southeast_bent_grounded_stair')
# Northwest diagonal exterior entrance staircase shown by1F, without inferred mirrored fittings.
for i in range(8):
 e=i*5;z=1.65-i*.19
 pts=[(395,277),(585,277),(585,247-e),(395,247-e),(270-e,372),(270-e,475),(300,475),(300,357),(395,357)]
 pp(pts,0,z,5,'662_northwest_bent_grounded_stair')
#659 bounded west-side slope candidate; notduplicated on other side.
pb(225,297,456,474,0,1.65,5,'west_ramp_to_entry_landing_connection')
a,b=trace([(225,690),(260,460)])
vs=np.array([[a[0],a[1],0],[b[0],a[1],0],[a[0],b[1],0],[b[0],b[1],0],[a[0],a[1],.20],[b[0],a[1],.20],[a[0],b[1],1.65],[b[0],b[1],1.65]])
tm=trimesh.convex.convex_hull(vs);add(Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32))),5,'photo659_west_candidate_supported_slope_proxy')
for xx in [225,260]:
 a,b=trace([(xx,690),(xx,460)]);beam((a[0],a[1],1.1),(b[0],b[1],2.55),.07,3,'slope_metal_handrail')
 for i in range(8):
  yy=690-i*(230/7);z=.2+i*(1.45/7);pb(xx-.7,xx+.7,yy-.7,yy+.7,z-.04,z+.94,3,'ramp_handrail_posts')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學集英樓','revision':'v2','scope':'complete cross-shaped three-storey body, partial B1 exterior footing, true recessed balconies, upper sloping shoulders and natural steps/ramp','coordinate_transform':'665 master X=(px-630)/20 Y=(530-py)/20 scale4mm per approximate unit','outlines':{'ground':ground,'balcony':balcony,'upper':upper,'partial_basement':basement},'shared_plan_registration':{'661':'CW90, .777 then(+470,+172)','662':'CCW90 then(+155,+200)','664':'180 then x+100 y*.953+168','665':'master original'},'photo_mapping':'same unchanged mesh; west facade viewed from northwest and southwest stronger candidate; east alternative notuniquelyexcluded, orientation to be independently gated, not EXIF recovery','limits':['Official simple layouts not measured as-built','Capture date unknown, not2026condition','Roof bounded flatcap no independentRF','Heights,finewindows,colors and unseen facade details approximate','Basement interior not modeled','No physical print or supportfree claim']}
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
