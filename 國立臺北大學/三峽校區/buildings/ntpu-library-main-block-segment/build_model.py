"""NTPU Library + Information Center, source-bound exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,Mesh64,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NTPU Library + Information Center source observations.
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

# 2014 completed photographs01–08,14,15,17,18,20,22,29,30 and plans31–38.
# X is the plan horizontal axis: lake negative, main entrance positive. Y plan vertical.
# Dimensions proportional, not survey; nominal above-ground height35.95 author text only.
SCALE=2.5
palette=[('neutral_display_base','#989D99',255),('pale_S_skin_and_eaves','#D5D8D2',255),('gray_blue_opaque_window_proxy','#53656B',255),('subdued_metal_frames','#626C6B',255),('stone_platforms_and_stairs','#B9B8AD',255),('central_roof_translucent_proxy','#A4C5D0',120),('terrace_paving','#9C9D93',255),('silver_gray_opaque_facade_panels','#A3AFB1',255)]
def cube(a,b,c,d,e,f):return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def block(a,b,c,d,e,f,col,name):add(cube(a,b,c,d,e,f),col,name)
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,40).translate((x,y,z))
def solid_loft(rows,col,name):
 # Four consistently oriented corners on successive stations, full closed skin.
 vs=np.array([p for r in rows for p in r],float);fs=[]
 fs.extend([(0,2,1),(0,3,2)])
 for k in range(len(rows)-1):
  for j in range(4):a=k*4+j;b=k*4+(j+1)%4;c=b+4;d=a+4;fs.extend([(a,b,c),(a,c,d)])
 n=(len(rows)-1)*4;fs.extend([(n,n+1,n+2),(n,n+2,n+3)])
 m=Manifold(Mesh64(np.asarray(vs,dtype=np.float64),np.asarray(fs,dtype=np.uint64)))
 if m.volume()<0:m=Manifold(Mesh64(np.asarray(vs,dtype=np.float64),np.asarray(fs,dtype=np.uint64)[:,::-1].copy()))
 add(m,col,name)
# Base includes only immediate ground transition; partial B1 court cut stays above bottom.
base=cube(-73,57,-31,31,0,3.6)-cube(-13,0,-19,19,1.2,4)
add(base,0,'display_base_with_local_B1_sunken_court')
block(-13,0,-19,19,1.15,1.45,4,'B1_court_floor_not_entire_axis')
for y in [-19,19]:block(-13,.2,y-.22,y+.22,1.3,3.9,4,'sunken_court_retaining_wall')
# Main high wings: 1F–6F closed-room envelope proxy, 7F setback, genuine central void.
for sign in [-1,1]:
 ya,yb=sorted([sign*5.90,sign*27]);block(0,50,ya,yb,3.4,32.8,2,'high_wing_six_storey_window_backing')
 ya7,yb7=sorted([sign*6,sign*24]);block(5.5,45,ya7,yb7,32.7,37.65,2,'recessed_7F_occupied_wing')
 block(0,50,ya,yb,32.6,33.0,4,'7F_setback_terrace_slab')
 # Source01/17: recessed7F has visible major piers, sill and window divisions, not black blank wall.
 for x in [5.5,45]:
  block(x-.15,x+.15,ya7,yb7,32.8,33.55,7,'7F_recessed_opaque_sill')
  for y in [sign*6.35,sign*15.0,sign*23.65]:
   block(x-.28,x+.28,y-.32,y+.32,32.8,37.9,4,'7F_recessed_major_pier')
  for y in np.arange(ya7+.6,yb7,.0+1.8):
   block(x-.18,x+.18,y-.055,y+.055,33.5,37.65,3,'7F_recessed_window_vertical')
  for z in [35.1,37.4]:block(x-.19,x+.19,ya7,yb7,z-.07,z+.07,3,'7F_recessed_window_transom')
 # facade end grids and inward atrium grids, subdivision is intentionally coarsened.
 for x in [0,50]:
  block(x-.20,x+.20,ya,yb,3.4,32.8,2,'continuous_end_glazing_backplane')
  for y in np.arange(ya+.6,yb,.95):block(x-.26,x+.26,y-.075,y+.075,3.6,32.8,3,'end_vertical_frame')
  for z in [3.8,8.5,13.3,18.1,22.9,27.7,32.5]:block(x-.28,x+.28,ya,yb,z-.14,z+.14,3,'end_floor_frame')
 for x in np.arange(.5,50,1.8):block(x-.075,x+.075,sign*6-.14,sign*6+.14,3.6,37.5,3,'atrium_vertical_frame')
 for z in [8.5,13.3,18.1,22.9,27.7,32.5]:block(0,50,sign*6-.15,sign*6+.15,z-.12,z+.12,3,'atrium_horizontal_frame')
 # Independent non-mirrored S cladding patterns, deep ribbon outline rather than paint.
 centers=[2.4,11.0,20.0,29.2,38.5,47.0] if sign<0 else [2.0,10.3,19.8,29.0,38.2,47.2]
 amps=[2.25,2.15,2.35,2.3,2.1,2.15] if sign<0 else [-2.1,-2.35,-2.2,-2.25,-2.15,-2.3]
 for i,(cx,amp) in enumerate(zip(centers,amps)):
  rows=[]
  for z in np.linspace(3.6,32.8,45):
   t=(z-3.6)/29.2;shift=amp*math.sin(2*math.pi*t+(.3 if sign>0 else -.4)+i*.09);w=6.7+(.45*math.sin(math.pi*t+i));a=max(0,cx+shift-w/2);b=min(50,cx+shift+w/2);out=sign*(27.25+1.1*math.sin(math.pi*t)**2)
   y0,y1=sorted([sign*26.95,out]);rows.append([(a,y0,z),(b,y0,z),(b,y1,z),(a,y1,z)])
  solid_loft(rows,1,'independent_S_skin_'+str(sign)+'_'+str(i))
 # Double shallow curvature: principal transverse Y bow corroborated end photos07/17.
 for y0,y1 in zip(np.linspace(5.9,30,13)[:-1],np.linspace(5.9,30,13)[1:]):
  y0,y1=sorted([sign*y0,sign*y1]);rows=[]
  for x in np.linspace(-2.8,52.8,29):
   z0=38.0+.30*((x-25)/27.8)**2+1.05*(y0/30)**2;z1=38.0+.30*((x-25)/27.8)**2+1.05*(y1/30)**2
   rows.append([(x,y0,z0),(x,y1,z1),(x,y1,z1+.5),(x,y0,z0+.5)])
  solid_loft(rows,1,'high_wing_shallow_upturned_eave')
 # Opaque spandrel/panel patches mixed with real window bands: not all-glass end walls.
 for x in [0,50]:
  for j,y in enumerate(np.arange(ya+.55,yb-1,1.9)):
   for k,z in enumerate([4.2,9.0,13.8,18.6,23.4,28.2]):
    if (j+k)%4!=0:block(x-.25,x+.25,y,y+1.65,z,z+(2.5 if j%3 else 1.3),7,'end_opaque_silver_spandrel_panel')
# Photo02 / plan32 bottom-arrow side doorway only; no invented matching opposite canopy.
for sign in [-1]:
 block(20,26,sign*27.5-.18,sign*27.5+.18,3.55,7.4,2,'S_side_entry_dark_glazed_door_proxy')
 block(19.6,26.4,min(sign*26.5,sign*29.2),max(sign*26.5,sign*29.2),7.35,7.65,1,'S_side_entry_shallow_canopy')
# Roof columns follow the shallow eave rather than bridge floating disconnected islands.
for x in [6,18,31,44]:
 for y in [-24,-6,6,24]:
  z=38.0+.30*((x-25)/27.8)**2+1.05*(y/30)**2
  beam((x,y,32.8),(x,y,z+.15),.52,4,'recessed_7F_eave_support_column')
# Glazed central canopy and open X bracing do NOT create a deep opaque roof plate.
block(-2.8,52.8,-6.1,6.1,38.12,38.34,5,'central_translucent_glazed_canopy')
for x in [0,12.5,25,37.5,50]:
 beam((x,-6,37.9),(x,6,37.9),.52,3,'canopy_cross_frame')
for x in [0,12.5,25,37.5]:
 beam((x,-6,37.2),(x+12.5,6,37.2),.65,1,'canopy_X_brace');beam((x,6,37.2),(x+12.5,-6,37.2),.65,1,'canopy_X_brace')
for y in [-3,0,3]:beam((-2.8,y,38.2),(52.8,y,38.2),.15,3,'canopy_long_mullion')
# Floor-specific bridge locations mapped from plans34–38 (x offsets not reused).
def bridge(xa,xb,z0,z1,width,label):
 a=np.array([xa,-7.0,z0]);b=np.array([xb,7.0,z1]);d=b-a;normal=np.array([d[1],-d[0],0]);normal=normal/np.linalg.norm(normal)*width/2
 rows=[]
 for t in [0,1]:
  p=a+d*t;rows.append([tuple(p-normal),tuple(p+normal),tuple(p+normal+[0,0,.42]),tuple(p-normal+[0,0,.42])])
 solid_loft(rows,4,label+'_deck')
 # Visible stair treads where a floor-to-floor rise is documented (not a plain ramp).
 if abs(z1-z0)>.1:
  for k in range(18):
   ta=k/18;tb=(k+1)/18;p0=a+d*ta;p1=a+d*tb;top=max(p0[2],p1[2])+.46
   rows=[]
   for p in [p0,p1]:
    rows.append([tuple(p-normal*.90+[0,0,.20]),tuple(p+normal*.90+[0,0,.20]),tuple((p+normal*.90)*[1,1,0]+[0,0,top]),tuple((p-normal*.90)*[1,1,0]+[0,0,top])])
   solid_loft(rows,4,label+'_individual_stair_tread')
 # Coarsened enclosed glazed bridge canopy; no full-atrium floor infill.
 rows=[]
 for t in [0,1]:
  p=a+d*t;rows.append([tuple(p-normal+[0,0,2.70]),tuple(p+normal+[0,0,2.70]),tuple(p+normal+[0,0,3.02]),tuple(p-normal+[0,0,3.02])])
 solid_loft(rows,5,label+'_glazed_top')
 for side in [-1,1]:
  p=a+side*normal;q=b+side*normal
  beam(p+[0,0,2.8],q+[0,0,2.8],.17,3,label+'_top_rail')
  # thin glass side plates, preserves spatial air above and below bridge.
  rows=[]
  for t in [0,1]:
   r=p+(q-p)*t;rows.append([tuple(r-normal*.10+[0,0,.20]),tuple(r+normal*.10+[0,0,.20]),tuple(r+normal*.10+[0,0,2.9]),tuple(r-normal*.10+[0,0,2.9])])
  solid_loft(rows,2,label+'_side_glass_proxy')
  for t in np.linspace(0,1,8):
   r=p+(q-p)*t;beam(r,r+[0,0,2.8],.13,3,label+'_rail_post')
# Plans34–38 distinguish true stair/seat runs from lower glass-roof projections.
# Only two source-supported inclined bridges; no invented4F5F or6F7F stair.
for xa,xb,z0,z1,w,n in [(17,20,13.25,13.25,3.6,'3F_diagonal_bridge'),(35,32,13.25,18.05,4.2,'3F4F_stair'),(12,8,18.05,18.05,3.6,'4F_bridge'),(24,20,22.85,22.85,3.8,'5F_bridge'),(15,19,22.85,27.65,4.1,'5F6F_stair'),(39,43,27.65,27.65,3.8,'6F_bridge'),(21,25,32.45,32.45,3.9,'7F_bridge')]:bridge(xa,xb,z0,z1,w,n)
# Low information wings are ONLY 2 occupied levels; distinct paved roof terraces.
for sign in [-1,1]:
 ya,yb=sorted([sign*6,sign*27]);block(-40,-15,ya,yb,3.4,13.0,2,'two_storey_information_wing')
 block(-40.3,-14.7,ya-.15,yb+.15,12.95,13.3,6,'3F_low_roof_terrace')
 for x in np.arange(-39.5,-15,.95):
  block(x-.07,x+.07,sign*27-.16,sign*27+.16,3.6,12.95,3,'information_long_facade_frame')
 for y in np.arange(ya+.5,yb,.95):block(-40.16,-39.84,y-.07,y+.07,3.6,12.95,3,'information_short_end_frame')
 for z in [3.9,8.4,12.6]:
  block(-40,-15,sign*27-.18,sign*27+.18,z-.1,z+.1,3,'information_floor_frame');block(-40.18,-39.82,ya,yb,z-.1,z+.1,3,'information_short_floor_frame')
 for y in [ya,yb]:beam((-40,y,14.25),(-15,y,14.25),.16,3,'low_terrace_guard')
 for x in [-40,-15]:beam((x,ya,14.25),(x,yb,14.25),.16,3,'low_terrace_end_guard')
 for x in np.arange(-40,-14,2.5):
  for y in [ya,yb]:beam((x,y,13.2),(x,y,14.25),.13,3,'low_terrace_guard_post')
 block(-20,-13,sign*6-1.8,sign*6+1.8,12.9,15.2,4,'low_terrace_stair_core')
 # Published3F roof-terrace inner curved division; low curb only, no invented curved shell.
 curve=[(-38,sign*7,13.45),(-34,sign*8.5,13.45),(-30,sign*8,13.45),(-27,sign*9.5,13.45),(-27.5,sign*15,13.45),(-29,sign*21,13.45),(-29,sign*25.5,13.45)]
 path(curve,.35,4,'low_terrace_curved_inner_boundary')
 # Large opaque silver side panels documented by photo18, no all-glass long side.
 block(-39.9,-21,sign*27-.19,sign*27+.19,3.65,12.85,7,'information_long_side_opaque_silver_cladding')
 for x in np.arange(-39.8,-21,2.7):block(x-.045,x+.045,sign*27-.22,sign*27+.22,3.65,12.85,1,'opaque_panel_vertical_joint')
# 2F continuous boulevard and real light wells; individual openings stop at lower floor.
wells=[(-46,0,2.3),(-36,-1.5,2.4),(-30,2.2,1.5),(-27,-3,1.3),(-21,1,2.1),(-12,3,1.4),(-8,-2,1.6),(3,0,1.6),(14,2.0,2.0),(22,-1.5,1.6),(31,-2,1.4),(40,1.2,2)]
# The1F low information body and main reading-floor middle are continuous in plan32.
# Bore individual shafts only to their lower floor, not through the display base.
for xa,xb,label in [(-40,-15,'information_1F_continuous_center'),(0,50,'library_1F_continuous_reading_center')]:
 lower=cube(xa,xb,-6.05,6.05,3.4,8.15)
 for x,y,r in wells:
  if xa<x<xb:lower-=cyl(x,y,3.7,r,5.1)
 add(lower,2,label)
deck=cube(-64,51,-6,6,8.1,8.6)
for x,y,r in wells:deck-=cyl(x,y,7.9,r,.9)
add(deck,4,'2F_boulevard_with_true_circular_well_mouths')
for x,y,r in wells:
 add(cyl(x,y,8.35,r+.18,.35)-cyl(x,y,8.2,r,.7),4,'lightwell_stone_open_rim')
 add(cyl(x,y,9.5,r+.08,.14)-cyl(x,y,9.4,r-.04,.4),3,'lightwell_open_rail')
 for a in np.linspace(0,2*math.pi,9)[:-1]:beam((x+r*math.cos(a),y+r*math.sin(a),8.5),(x+r*math.cos(a),y+r*math.sin(a),9.55),.13,3,'lightwell_rail_post')
 # empty cylindrical shaft implied by rim; no fictional full-depth through-base holes.
for x in [-60,-51,-43,-12,-2]:
 for y in [-5.2,5.2]:add(cyl(x,y,1.4 if -13<x<0 else 3.4,.45,6.8 if -13<x<0 else 4.8),4,'boulevard_support_column')
# Terminal lake stair and front entrance stair. Solid steps are coarse printable proxy.
for i in range(18):
 x=-72+i*.46;block(x,x+.5,-5.8,5.8,3.5,3.7+(i+1)*4.9/18,4,'lake_terminal_stair')
# Central grade-level glazed vestibule retained between TWO flanking access stairs.
block(49.8,54,-3.5,3.5,3.55,8.2,2,'main_grade_level_glazed_entrance_vestibule')
block(49.8,54.3,-3.7,3.7,8.15,8.5,4,'main_entrance_vestibule_canopy')
for y in [-3.5,-1.15,1.15,3.5]:block(53.9,54.12,y-.07,y+.07,3.6,8.2,3,'main_entrance_glazed_door_frame')
for sign in [-1,1]:
 ya,yb=sorted([sign*3.8,sign*7.8])
 for i in range(15):
  x=50.1+i*.38;block(x,x+.42,ya,yb,3.5,8.5-i*4.8/15,4,'main_entrance_flanking_stair')
# Low lake-end portal above the 2F axis, not an added occupied floor.
block(-40.5,-39.3,-6.2,6.2,12.43,13.6,4,'information_lake_portal_horizontal_lintel')
for y in [-5.7,5.7]:block(-40.5,-39.3,y-.35,y+.35,8.3,13.4,4,'information_lake_portal_jamb')
# B1 court stairs restricted to local courtyard side, not whole axis sinking.
for s in [-1,1]:
 for i in range(10):
  y=s*(10+i*.55);block(-10,-5,min(y,y+s*.58),max(y,y+s*.58),1.3,1.5+i*.24,4,'B1_court_access_stair')
parts=[p.translate((-0,0,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'ntpu-library-main-block-segment','version':'2014 completed photographic series and author published B1–7F plans','scope':'Whole high library pair + two-storey information pair + 2F boulevard/lake terminal stair/local B1 court; no unrelated campus','scale_mm_per_proportional_unit':SCALE,'height_source':'Author overall35.95m used only for proportional guidance; no survey scale','high_wings':2,'low_wings':2,'low_occupied_levels':2,'low_terrace_level':'3F','separate_central_translucent_canopy':True,'different_S_skin_patterns':True,'floor_specific_bridges':True,'well_count_approximation':len(wells),'excluded':'concept39–45 dimensions, concept45 extra low floors/PV, render46–53, hidden roof equipment','supports':'eaves, bridges, boulevard, rails require supports; no physical print; opaque window proxies and translucent canopy appearance, no structural certification'}
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
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);nn=cr/np.linalg.norm(cr,axis=1)[:,None]
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
