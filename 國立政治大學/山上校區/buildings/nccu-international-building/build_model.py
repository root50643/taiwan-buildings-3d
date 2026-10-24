"""NCCU International Building — source-relative approximate complete main-building exterior."""
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
palette=[('rose_tile','#A77970',255),('cream_tile_bands','#D1C9B6',255),('opaque_glazing','#52615F',255),('pale_frames','#C2C9C3',255),('roof_concrete','#91958C',255),('slope_proxy','#85856F',255),('entry_terracotta','#A85F45',255)]
def poly(points,z0,z1):return CrossSection([points],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(z1-z0).translate((0,0,z0))
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
def trace(p):return [((x-85)/10,(250-y)/10) for x,y in p]
left=trace([(85,175),(386,175),(386,250),(376,250),(376,276),(362,286),(303,286),(250,325),(138,325),(85,286)])
full=trace([(85,175),(338,175),(338,191),(388,191),(388,175),(650,175),(650,134),(805,134),(805,233),(778,250),(376,250),(376,276),(362,286),(303,286),(250,325),(138,325),(85,286)])
high=trace([(174,175),(338,175),(338,191),(388,191),(388,175),(650,175),(650,134),(805,134),(805,250),(376,250),(376,276),(362,286),(303,286),(303,250),(174,250)])
# Shared main stair x=22..25.3,y=2.1..7.5 anchors every floor; no page-offset setbacks.
add(poly(left,.65,4.22)-cube(11.3,13.7,-8,0,.64,4.23),0,'B1_left_polygon_with_front_slot_recess')
add(poly(left,4.15,11.25),0,'1F_2F_left_polygon_and_full_rectangular_core_only')
add(poly(full,11.15,21.7),0,'3F_4F_5F_complete_connected_left_middle_right_body')
add(poly(high,21.65,25.2),0,'6F_only_labelled610_and_east_band_middle_rightwing')
# 5F right end becomes square rather than chamfered.
block(69.2,72,0,2,18.15,21.72,0,'5F_squared_right_front_end')
# Independent low terraces: left polygon and far-left upper bay stay unfilled above5F.
lowroof=trace([(85,175),(338,175),(338,191),(386,191),(386,250),(376,250),(376,276),(362,286),(303,286),(250,325),(138,325),(85,286)])
add(poly(lowroof,21.65,21.82),4,'left_low_roof_deck_two_blank_6F_zones')
# highest roof matches registered R; inset only candidate central lift overrun.
add(poly(high,25.16,25.42),4,'R_main_connected_roof_not_seventh_floor')
for pts,z in [(lowroof,21.8),(high,25.4)]:
 cs=CrossSection([pts],fillrule=__import__("manifold3d").FillRule.EvenOdd);add((cs-cs.offset(-.22)).extrude(.58).translate((0,0,z)),0,'open_low_roof_parapet')
block(21.55,28.0,-3.62,.1,25.1,29.6,0,'central_front_named_tower_and_candidate_R_inset_core_approx')
block(21.4,28.15,-3.77,.25,29.55,29.88,1,'named_tower_cream_cap')
# Front central polygonal glazed bay, and far-left end glazed stair.
endstair=trace([(85,225),(73,225),(67,230),(67,244),(74,248),(85,248)])
add(poly(endstair,.65,21.75),2,'left_end_projecting_glazed_stair_core')
central=trace([(303,250),(338,250),(338,278),(329,286),(303,286)])
# Main body already supplies this bay; external facade relief below supplies glass, no coincident recolour solid.
rightstair=trace([(650,175),(650,127),(657,121),(676,121),(683,127),(683,175)])
add(poly(rightstair,11.15,26.1),0,'right_rear_stair_projection_3F_to_R_registered_core')
add(poly(rightstair,26.06,26.3),4,'right_stair_roof_cap_approx')
# Opaque glass facade relief, never unsupported floating panes; neutral unknown rear fine windows.
def facade(a,b,z0,z1,count,name):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);t=(b-a)/np.linalg.norm(b-a);L=np.linalg.norm(b-a);n=np.array([t[1],-t[0]])
 def patch(u0,u1,v0,v1,h0,h1,col,label):
  c=a+(u0+u1)/2*t+(v0+v1)/2*n; add(Manifold.cube((u1-u0,v1-v0,h1-h0),True).transform([[t[0],n[0],0,c[0]],[t[1],n[1],0,c[1]],[0,0,1,(h0+h1)/2]]),col,label)
 for i in range(count):
  u0=(i+.13)*L/count;u1=(i+.87)*L/count
  patch(u0,u1,-.08,.08,z0,z1,2,name)
  for u in [u0,(u0+u1)/2,u1]:patch(u-.045,u+.045,.03,.15,z0-.04,z1+.04,3,'window_vertical_frame_approx')
  for z in [z0,z1]:patch(u0-.04,u1+.04,.03,.15,z-.045,z+.045,3,'window_horizontal_frame_approx')
 # thin cream continuous sill/header, visible source signature
 patch(.09,L-.09,-.05,.13,z0-.23,z0-.09,1,'cream_horizontal_tile_band')
for floor in range(1,6):
 z=.7+3.5*floor
 for a,b,n in [((0,-3.6),(5.3,-7.5),2),((5.3,-7.5),(16.5,-7.5),4),((16.5,-7.5),(21.8,-3.6),2)]:facade(a,b,z+.65,z+2.6,n,'left_polygon_front_windows')
for floor in range(3,7):
 z=.7+3.5*floor
 facade((30,0),(69.2,0),z+.65,z+2.6,13,'right_front_long_wing_windows')
 # central front window bay behind the platform, between tower and right wing
 facade((28,-3.6),(29.1,-2.6),z+.65,z+2.6,1,'middle_junction_windows')
# Source856 end has three upper slits, a broad lower grille and a low band, not five identical slits.
for floor in range(1,6):
 z=.7+3.5*floor
 if floor>=3:facade((0,7.5),(0,2.5),z+1.35,z+1.9,1,'856_three_upper_end_horizontal_slits')
 elif floor==2:facade((0,7.5),(0,2.5),z+.45,z+2.85,1,'856_large_lower_screen_proxy')
 else:facade((0,7.5),(0,2.5),z+.65,z+1.45,1,'856_low_horizontal_band')
 facade((21.8,7.5),(0,7.5),z+.65,z+2.6,7,'856_adjoining_longside_window_bays')
# Visible central polygonal glazing must sit outside the solid body, not hidden coplanarly inside it.
for floor in range(3,7):
 z=.7+3.5*floor
 for a,b in [((21.8,-3.6),(24.4,-3.6)),((24.4,-3.6),(25.3,-2.8))]:facade(a,b,z+.30,z+2.95,1,'855_central_polygonal_glazed_bay')
# central glazed tower/frame horizontals and stair glazed edges.
for z in [4.2,7.7,11.2,14.7,18.2,21.7,25.1]:
 if z<=21.7:add(CrossSection([endstair],fillrule=__import__('manifold3d').FillRule.EvenOdd).offset(.07).extrude(.16).translate((0,0,z-.08)),3,'left_glazed_stair_floor_frame')

# Tight outline-following display plinth; slope body beneath right wing is ground, not invented rooms.
site=trace([(65,168),(338,168),(388,184),(388,168),(643,168),(643,127),(813,125),(813,295),(405,295),(398,300),(338,347),(280,347),(245,333),(132,333),(77,292),(65,250)])
add(poly(site,0,.72),5,'low_tight_display_plinth')
right_support=trace([(340,192),(388,192),(388,175),(650,175),(650,134),(805,134),(805,250),(376,250),(362,286),(338,286)])
add(poly(right_support,.65,11.22),5,'disclosed_unmeasured_ground_support_below_right3F_wing')
# A sloped outer face, not a fictitious three-storey facade, joins exposed grade to right3F.
slope=CrossSection([[(-4.4,.65),(0.03,.65),(0.03,11.22)]],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(41.8)
add(slope.transform([[0,0,1,30.2],[1,0,0,0],[0,1,0,0]]),5,'right_front_sloping_ground_proxy')
for x,y in endstair:
 beam((x,y,.75),(x,y,21.72),.13,3,'left_end_glazed_stair_vertical_frame')
# Photo855 front grade reaches roughly2F; keep lower856 end entrance and real B1/1F behind.
def grade_strip(a,b,width,top):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);t=(b-a)/np.linalg.norm(b-a);n=np.array([t[1],-t[0]]);L=np.linalg.norm(b-a)
 sec=CrossSection([[(-.10,.65),(width,.65),(.25,top),(-.10,top)]],fillrule=__import__('manifold3d').FillRule.EvenOdd).extrude(L+.16)
 add(sec.transform([[n[0],0,t[0],a[0]-.08*t[0]],[n[1],0,t[1],a[1]-.08*t[1]],[0,1,0,0]]),5,'855_local_front_grade_rises_to_2F_not_deleted_floor')
for a,b in [((0,-3.6),(5.3,-7.5)),((5.3,-7.5),(16.5,-7.5)),((16.5,-7.5),(21.8,-3.6))]:grade_strip(a,b,3.5,7.65)
# Join adjacent front slope facets at polygon corners; no invented gaping sawtooth terrain gaps.
for prev,q,nxt in [((0,-3.6),(5.3,-7.5),(16.5,-7.5)),((5.3,-7.5),(16.5,-7.5),(21.8,-3.6))]:
 q=np.array(q);ta=q-np.array(prev);ta=ta/np.linalg.norm(ta);tb=np.array(nxt)-q;tb=tb/np.linalg.norm(tb);na=np.array([ta[1],-ta[0]]);nb=np.array([tb[1],-tb[0]])
 pts=[[*(q+na*.20),7.65],[*(q+nb*.20),7.65],[*(q-na*.12),.65],[*(q-nb*.12),.65],[*(q+na*3.5),.65],[*(q+nb*3.5),.65]]
 add(Manifold.hull_points(pts),5,'joined_front_slope_corner')
# Narrow terraced shelf below the attached platform, leaving its recessed soffit void above.
undergrade=[(21.45,-3.3),(36.4,-1.2),(36.4,-6.7),(32.8,-9.0),(27,-9.0),(23,-7.9),(21.45,-6.4)]
add(poly(undergrade,.65,7.58),5,'limited_platform_terraced_grade_not_solid_to_soffit')
# Curved attached front entry platform extends from middle front; deliberately open undercroft.
platform=[(22,-3.4),(39,-.4),(39,-5.4),(36,-8.7),(31,-10.4),(27,-10.5),(24,-9.6),(22,-8)]
add(poly(platform,10.65,11.45),6,'attached_curved_front_entry_platform')
for x,y in [(23,-7.2),(28,-8.5),(35,-7.0)]:
 add(Manifold.cylinder(10.2,.40,.40,16).translate((x,y,.65)),6,'visible_platform_support_column_approx')
# Retaining stair at right meets upper ground; no arbitrarily floating stair end.
for i in range(16):block(38.2,41.4,-9.5+i*.58,-8.86+i*.58,.65,.75+(i+1)*.66,6,'right_attached_slope_access_steps')
# Boundary wall/landing lower width; support under slab not solid filled atrium.
block(37.8,41.7,-9.7,-9.1,.65,1.0,6,'stair_bottom_landing')
block(38.2,41.4,-.5,.3,10.8,11.5,6,'stair_upper_ground_interface')
# One limited photographed retaining/column portal proxy beside slope stair, explicitly cropped.
block(41.0,47.0,-8.7,-5.7,7.2,8.0,6,'finite_right_access_portal_thick_top')
for x in [41.0,46.2]:block(x,x+.8,-8.7,-5.7,.65,7.25,6,'finite_right_access_portal_piers')
block(46.2,47.0,-5.8,-.1,.65,10.9,6,'limited_access_thick_side_retaining_wall')
block(40.8,47.2,-8.9,-5.5,0,.72,5,'finite_portal_cropped_ground_interface')
# Coarse true diagonal screen bars on856 lower square opening, not a texture or invented fine lattice count.
for y in [3.5,4.5,5.5,6.5]:
 beam((-.12,y,8.2),(-.12,min(y+1.5,7.0),10.5),.16,1,'856_coarse_diagonal_screen_bar')
 beam((-.12,y,10.5),(-.12,min(y+1.5,7.0),8.2),.16,1,'856_coarse_cross_screen_bar')
# platform low rim, intentionally coarse and attached rather than print-fragile railings.
path([(x,y,11.85) for x,y in platform[2:]+[platform[0]]],.70,6,'deep_solid_platform_planter_rim_approx')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學國際大樓','scope':'complete connected B1-6F/R main building, attached platform and stairs; limited slope proxy','coordinate_transform':'X=(reading pixel x-85)/10,Y=(250-reading pixel y)/10; proper y-up, not mirrored; R registered main stair shift57px','outline_design':full,'left_outline_design':left,'high_roof_design':high,'nominal_scale_mm_per_approx_design_unit':SCALE,'floor_levels_mm':[SCALE*(.7+3.5*i) for i in range(7)],'roof_mm':25.42*SCALE,'limits':['Photo date unknown, not verified2026 condition','No measured heights, exact scale or surveyed terrain','R inset assigned candidate central core, not new wing','Far-left6F blank bay and polygon front retained as lower roofs','Unknown rear fine windows neutral; visible windows are approximate','Source rights unresolved; private only, no blanketCC','No physical print or support-free guarantee']}
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
