"""NTUNHS Erya third student dormitory / 北護爾雅樓. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_plinth','#949A96',255),('warm_white_facade','#D6D7D0',255),('mid_gray_facade','#92948F',255),('dark_recess_and_frames','#454B4B',255),('opaque_glazing','#63767C',255),('green_roof','#74844E',255),('PV_panels','#354B5E',255),('light_metal_rail','#A5AAA5',255)]
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

# Display millimetres, arbitrary model axes, not true north or surveyed scale.
# Floor outline follows official 4/6/7F staircase perimeter; front stepped side is +Y.
# The building is mirrored in X from the published floor diagram to face the street camera.
P=[(-60,-42),(60,-42),(60,-9),(36,-9),(36,12),(12,12),(12,42),(-60,42)]
B=[(-63,-45),(63,-45),(63,-8),(-7,47),(-63,47)]
cs=CrossSection([P]);base=CrossSection([B]);
add(base.offset(6).extrude(3),0,'bounded_display_plinth_not_real_terrain_or_B2')
# Solid closed exterior envelope: slicer controls infill; no invented room interiors.
body=cs.extrude(174).translate((0,0,3))
# Front-facing middle setback wing terminates below the highest main roof.
body-=Manifold.cube((25,23,40),True).translate((24,1.5,172.7))
# Upper roof notch is a genuine external recess, not a generic flat lid.
body-=Manifold.cube((15,19,15),True).translate((4,27,175))
podium=base.extrude(29).translate((0,0,3));body=body+podium
windows=[]
def win(axis,c,pos,z,w,h,name,depth=2.1):
 global body
 if axis=='y':
  cut=Manifold.cube((w,depth+1,h),True).translate((c,pos,z));glass=Manifold.cube((w,1.9,h),True).translate((c,pos-(.85 if (pos>0 or (axis=='y' and pos==-9)) else -.85),z))
 else:
  cut=Manifold.cube((depth+1,w,h),True).translate((pos,c,z));glass=Manifold.cube((1.9,w,h),True).translate((pos-(.85 if (pos>0 or (axis=='y' and pos==-9)) else -.85),c,z))
 body-=cut;add(glass,4,name+'_opaque_recess_glazing');windows.append(dict(axis=axis,c=c,pos=pos,z=z,w=w,h=h,name=name))
# Main front: staggered light parapet cells over dark recessed vertical room bands.
for cx,w,y,top,bays in [(-24,72,42,177,6),(24,24,12,152.7,2)]:
 for bx in np.linspace(cx-w/2+6,cx+w/2-6,bays):
  box((bx,y-.25,(32+top)/2),(9.5,1.8,top-32),3,'front_dark_vertical_recess')
  for level in range(11 if top>170 else 9):
   z=38+12.4*level
   win('y',bx,y,z+3,7.6,8.2,'front_room_window')
   # Alternate lateral offset of solid balcony/AC parapets, visible in p56/63.
   shift=1.7 if (level+round(bx))%2 else -1.7
   box((bx+shift,y+1.1,z-1.4),(6.7,2.6,4.8),1,'staggered_light_front_parapet')
   box((bx,y+1.35,z+6.7),(10.8,2.5,1.2),2,'floor_edge_front_band')
  box((bx-5.4,y+.65,(32+top)/2),(1.35,2.8,top-32),2,'front_vertical_grid')
 for xx in [cx-w/2+1,cx+w/2-1]:box((xx,y+1,(32+top)/2),(2.2,3.2,top-32),1,'large_front_frame_vertical')
 box((cx,y+1.2,top),(w+1,4,2.2),1,'large_front_frame_header')
# Short recessed upper landing at +X has narrow horizontal stair windows, not copied grid.
for level in range(11):
 z=38+level*12.4
 win('y',48,-9,z+2,15,3.3,'recessed_stair_front_narrow_slot')
# Back long face: ten rooms per level in official plans; upper exact cells approximate.
for level in range(11):
 z=38+level*12.4
 for j,x in enumerate(np.linspace(-54,54,10)):
  win('y',x,-42,z+3,7.3,8.0,'rear_room_photo_pattern_approximation')
  box((x+(-1.3 if (level+j)%2 else 1.3),-43,z-1.3),(6.3,2.2,4.5),1,'rear_staggered_panel_approximation')
 box((0,-42.6,z+7),(120,1.8,1.2),2,'rear_floor_edge')
# Gym side short face (+ left in front view): narrow windows with asymmetric placements.
for level in range(11):
 z=38+level*12.4
 for y,w in [(-24,12),(5,13),(27,8)]:win('x',y,-60,z+2,w,3.4,'gym_side_horizontal_slot')
# Opposite narrow end and step return walls; not symmetric copies of front.
for level in range(11):
 z=38+level*12.4
 for y in [-31,-18]:win('x',y,60,z+2,6.5,4.2,'opposite_short_face_window')
for level in range(9):
 z=38+level*12.4
 win('x',2,36,z+2,7,5,'middle_return_window')
 win('x',24,12,z+2,8,4.5,'main_return_window')
# Low skirt: diagonal perimeter, front entrance and full-height glazing.
for x in [-48,-24]:
 win('y',x,47,17.5,17,20,'front_podium_large_opening')
 for xx in [x-9.5,x+9.5]:box((xx,47,17.5),(2,3,25),1,'podium_thick_jamb')
 box((x,47,29.5),(21,3,2.4),1,'podium_thick_lintel')
# Diagonal skirt glazing is set into a gray wall as a closed original panel assembly.
a=np.array([-7.,47.]);b=np.array([63.,-8.]);v=b-a;L=np.linalg.norm(v);u=v/L;out=np.array([-u[1],u[0]])
for j in range(5):
 c=a+u*(10+j*14)
 p=Manifold.cube((11,1.5,18),True).rotate((0,0,math.degrees(math.atan2(u[1],u[0])))).translate((c[0],c[1],17))
 add(p,4,'diagonal_podium_glazing_approximate_subdivision')
for level in [0,1]:
 for x in [-44,-15,15]:win('y',x,-45,10+13*level,17,8.5,'rear_base_other_openings_approximate')
# p64 observed end-bay: thick white upper window frame above full-height ground entrance.
win('y',44,-45,9.9,20,13.8,'rear_observed_ground_entrance_reaches_plinth')
win('y',44,-45,24.0,20,10.5,'rear_observed_upper_large_window')
for x in [32.7,55.3]:box((x,-45.8,23.8),(2.6,4,14),1,'rear_observed_thick_upper_white_jamb')
for z in [17.5,30.1]:box((44,-45.8,z),(25.2,4,2.6),1,'rear_observed_thick_upper_white_header_sill')
for x in [33.1,54.9]:box((x,-45.4,9.9),(1.8,2.6,14),2,'rear_entrance_jamb')
for x in [38.5,44,49.5]:
 box((x,-45.4,9.9),(1.2,2.5,13.8),3,'rear_ground_door_mullion')
 box((x,-45.4,24),(1.2,2.5,10.5),3,'rear_upper_window_mullion')
for y in [-32,-15,4]:win('x',y,-63,12,9,7,'gym_side_low_opening_approximate')
add(body,1,'closed_13_floor_stepped_envelope_with_diagonal_2_floor_skirt')
# Add framing after envelope union: darker side vertical corner strips.
for x,y,h in [(-59.6,41,145),(11.5,31,133),(59.6,-28,145)]:box((x,y,104),(1.6,3.0,h),2,'vertical_corner_accent')
# 3F diagonal roof terrace, concrete surface with bounded rim.
terrace=base-cs
add(terrace.extrude(1.5).translate((0,0,31)),2,'3F_diagonal_landscape_terrace')
# Rim follows diagonal and overlaps podium, robust simplified rather than thin wire.
beam((-7,47,34),(63,-8,34),1.4,7,'diagonal_terrace_top_rail')
for t in np.linspace(0,1,13):
 c=a+(b-a)*t;beam((c[0],c[1],31),(c[0],c[1],34),1.2,7,'diagonal_terrace_rail_post')
# Visible outside stair at main frontage. Deliberate printable closed risers.
for i in range(12):
 h=1.0+(11-i)*1.05;box((-47,51+i*.68,3+h/2),(15,1.5,h),2,'front_external_stair_solid_riser')
box((-47,48.3,15.6),(17,5,1.6),2,'front_external_stair_landing')
for x in [-55.2,-38.8]:
 beam((x,59,6),(x,48,18),1.3,7,'external_stair_inclined_rail')
 box((x,59,5),(1.4,1.4,4),7,'stair_rail_low_post')
 box((x,48,11),(1.4,1.4,16),7,'stair_rail_high_post')
# Upper roof perimeter and distinct roof levels; two grass beds, central raised equipment/PV.
rim=cs-cs.offset(-1.4)
rim3=rim.extrude(3.2).translate((0,0,176.5))
rim3-=Manifold.cube((25,23,20),True).translate((24,1.5,175))
rim3-=Manifold.cube((15,19,20),True).translate((4,27,175))
add(rim3,1,'upper_roof_outer_parapet_respects_notch_and_lower_wing')
# Main left roof green zone and rear-right green zone match p16 massing; exact planting omitted.
for x,y,w,d,z in [(-29,20,47,32,177),(36,-27,38,19,177),(24,1,20,18,152.7)]:
 box((x,y,z+.6),(w,d,1.5),2,'roof_terrace_slab')
 if z>170:box((x,y,z+1.3),(w-5,d-5,1.5),5,'green_roof_bed')
 for xx in [x-w/2,x+w/2]:box((xx,y,z+2),(1.3,d+1.3,4),1,'roof_parapet')
 for yy in [y-d/2,y+d/2]:box((x,yy,z+2),(w+1.3,1.3,4),1,'roof_parapet')
# Central tall roof equipment box, distinct from occupied 13F; frame and PV grid.
box((-8,-18,182),(39,31,12),1,'central_raised_roof_equipment_volume')
for x in [-22,-8,6]:
 for y in [-27,-17,-7]:box((x,y,188.6),(12.7,8.7,1.6),6,'central_roof_PV_panel_approximate_count')
for x in [-28,12]:box((x,-18,189),(1.3,33,2.2),1,'equipment_roof_outer_rim')
# Raised roof dark ventilated face and wide structural frame.
box((-8, -1.8,183),(35,1.6,8.5),3,'equipment_louver_face')
for x in np.arange(-24,10,3):box((x,-.8,183),(1.2,1.8,8.8),7,'roof_louver_fins_simplified')
# Roof notch remains open to sky; recessed low platform with small planting.
box((4,27,168.5),(13,17,2),2,'roof_open_notch_recessed_terrace')
box((4,29,170),(8,10,1.5),5,'recessed_roof_notch_green_patch')
# Short-side rooftop screening lattice, connected robust frame.
for y in np.arange(-40,-9,3):box((59.7,y,182),(1.4,1.3,10),7,'short_end_roof_screen_posts')
box((59.7,-25,187),(1.6,33,1.5),7,'short_end_roof_screen_header')
parts=[p.scale((-1,1,1)) for p in parts]
# Final X reflection aligns front street camera with source, no geographic direction claim.
FEATURES=dict(name='爾雅樓（第三學生宿舍）',school='國立臺北護理健康大學',campus='石牌校區',slug='ntunhs-erya-dorm',selected_version='2021 contractor completion photographs; exact capture dates unknown',aboveground_floors=13,front_main_window_rows=11,middle_projection_window_rows=9,main_roof_z_mm=177,middle_projection_roof_z_mm=152.7,rear_observed_upper_thick_frame_and_ground_entrance_preserved=True,underground_not_modeled=True,estimated_not_surveyed=True,stepped_plan=P,diagonal_skirt_plan=B,rear_upper_windows_approximate=True,gym_side_low_openings_approximate=True,only_official_floor_plans_used=[3,4,6,7],Xuesi_and_gym_and_old_dorms_excluded=True,all_materials_opaque=True,no_actual_print=True,support_free_certified=False,window_records=windows)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.0005).simplify(.0005)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
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
