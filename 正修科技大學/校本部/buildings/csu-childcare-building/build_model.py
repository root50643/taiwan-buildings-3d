"""CSU Childcare Building / 正修科技大學幼兒保育館. Photo-proportion exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_base','#8A9690',255),('ivory_tile','#DDDFD6',255),('gray_taupe_bands','#A9AAA4',255),('brown_brick_frames','#766055',255),('opaque_blue_green_glass','#365255',255),('pv_blue','#304967',255),('pv_silver_grid','#ADB7BD',255),('pale_metal_roof','#C4CDCF',255)]
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

# Display mm, not surveyed real-world dimensions. +Y = wavy front, -Y = straight rear.
box((0,0,1.5),(270,84,3),0,'display_base_not_terrain')
def poly(points,z,h,col,name):add(CrossSection([points]).extrude(h).translate((0,0,z)),col,name)
def front_y(x):
 # Differently sized wavy/angled bays; faceted approximation of the photographed curve.
 return float(np.interp(x,[-98,-88,-75,-63,-52,-40,-25,-12,2,16,31,45,58,72,84,96],[24,28,29,26,23,24,28,29,27,24,24,27,29,27,24,22]))
xs=np.linspace(-98,96,99);front=[(float(x),front_y(x)) for x in xs]
plan=[(-98,-24),(96,-24)]+list(reversed(front))
# Original five levels below the distinct setback sixth floor, solidified interior.
main=CrossSection([plan]).extrude(96).translate((0,0,3))
main-=Manifold.cube((24,16,18),True).translate((72,-23,13))
add(main,1,'five_floor_main_envelope_with_recessed_entry')
box((72,-15.3,12),(13,1.5,16),4,'recessed_ground_entry_full_height_door')
box((72,-16,12),(1,1.5,16),3,'entry_door_divider')
# Window bands as opaque face panels, outer edges follow the wavy front.
for level in range(5):
 z=12+18*level
 # Opaque surface band; solid interior retained, not a surveyed window recess.
 for j,(x1,x2) in enumerate([(-96,-66),(-63,-35),(-32,-4),(-1,28),(31,59),(62,91)]):
  pp=[(x1,19),(x2,19)]+[(float(x),front_y(x)+.25) for x in np.linspace(x2,x1,17)]
  # Opaque dark inset rather than architecturally invented internal rooms.
  poly(pp,z,9.2,4,'front_wavy_window_band')
  for x in np.linspace(x1+2,x2-2,5):box((x,front_y(x)+.4,z+4.6),(.9,1.5,9.5),3,'front_window_mullion')
 # Spandrel stripes and slim outer sun lips, following waviness.
 for a,b in zip(front,front[1:]):
  beam((a[0],a[1]+.4,z-2),(b[0],b[1]+.4,z-2),1.3,2,'front_following_gray_band')
 # Rear window ribbon is deliberately straight and not front mirrored.
 if level==0:
  box((-19,-24.35,z+4.6),(150,1.5,9.2),4,'rear_ground_window_band_clear_entry')
  box((90,-24.35,z+4.6),(8,1.5,9.2),4,'rear_ground_window_end')
 else:box((-1,-24.35,z+4.6),(186,1.5,9.2),4,'rear_straight_window_band')
 for x in np.arange(-92,93,8):
  if level==0 and 57<x<87:continue
  box((x,-25.1,z+4.6),(.9,1.1,9.6),3,'rear_window_mullion')
 if level>0:box((-1,-25.1,z-1),(190,2.5,2.2),2,'rear_horizontal_gray_band')
# Front tall white ribs break up wavy horizontal windows.
for x in [-64,-33,-2,29,60,93]:
 box((x,front_y(x)+.5,51),(3.0,3.2,96),1,'front_white_vertical_rib')
 box((x,front_y(x)+1,98),(4.5,4.1,4),1,'front_rib_cap')
# Rear low two-storey brown major frames, upper light piers and projecting open lattice.
for x in [-94,-62,-30,2,34,66,94]:
 if x!=66:box((x,-26,23),(3.5,5,40),3,'rear_two_storey_brown_pier')
 box((x,-25.6,70),(2.5,4,55),1,'rear_upper_white_pier')
for z in [24,42]:box((0,-26,z),(190,5,3.6),3,'rear_brown_frame_beam')
box((-19,-26,6),(150,5,3.6),3,'rear_ground_brown_beam_clear_entry')
for z in [61,98]:
 box((0,-30.1,z),(192,2.2,2.8),2,'rear_open_sunshade_outer_rail')
 for x in np.arange(-94,96,8):box((x,-27,z),(1.8,7.5,2.8),2,'rear_open_sunshade_crossbeam')
# Larger rear continuous overhang below the added storey; sixth floor steps back.
box((0,-23,100),(197,10,2.5),1,'rear_large_eave_below_setback_sixth')
box((0,0,100),(198,48,2.2),2,'fifth_roof_terrace_slab')
box((0,-1,109),(188,35,17.0),1,'added_sixth_storey_setback')
for sy in [-1,1]:
 for x in range(-88,91,14):
  box((x,-1+sy*17.7,109.2),(9,1.5,9),4,'sixth_floor_setback_windows')
  box((x,-1+sy*18,109.2),(.9,1.6,9),2,'sixth_floor_window_mullion')
# Front sixth-floor open terrace and deep central floating canopy on supports.
box((8,24,103),(158,1.8,5),1,'front_terrace_parapet')
for x in [-20,30,70]:box((x,19,110),(2.4,2.4,20),1,'sixth_front_canopy_post')
box((25,19,119),(110,13,3),1,'sixth_front_projected_canopy')
# Different end towers: right high rectilinear tile shell and full-height inset glazing.
box((110,-1,61),(28,52,116),1,'right_rectilinear_tower')
for z in [15,33,51,69,87,105]:
 for yy in [-11,10]:
  box((124.25,yy,z),(1.4,16,11),4,'right_short_end_paired_wide_window_bands')
  box((125,yy,z+2),(1.4,16,1),3,'right_short_end_window_transom')
  box((125,yy,z),(1.4,1,11),3,'right_short_end_window_mullion')
 box((113,25.3,z),(20,1.5,3),2,'right_front_gray_horizontal_bands')
 box((102,25.6,z),(5,1.7,9),4,'right_front_narrow_stack')
# Broad front glazing core with separate narrow strip, white cap and low terrace.
box((86.5,25.3,51),(29,7.4,96),1,'front_glass_core_white_surround')
box((83.5,29.25,49),(17,1.5,88),4,'front_broad_full_height_glazing')
box((97,29.25,49),(3.5,1.5,88),4,'front_separate_narrow_glazing_strip')
for x in [76,80,84,88,92,95.4,98.6]:box((x,30,49),(.85,1.5,84),6,'front_glazing_mullion')
for z in np.arange(8,94,6):
 box((83.5,30,z),(17,1.5,.85),6,'front_glazing_transom')
 box((97,30,z),(3.5,1.5,.85),6,'front_narrow_glazing_transom')
for z in [36,72]:box((86.5,30,z),(29,2.0,2.6),2,'glazing_core_floor_crossband')
capxs=np.linspace(72,101,18)
capfront=[(float(x),29+2*math.sin((x-72)/29*math.pi/2)) for x in capxs]
capplan=capfront+[(x,y-2.5) for x,y in reversed(capfront)]
poly(list(reversed(capplan)),96,21,1,'front_glass_core_curved_white_upper_cap')
for x in [79,85,91]:box((x,30.8,108),(2.4,2.8,8),4,'three_narrow_upper_glass_core_slots')
box((86.5,24,100.2),(29,12,1.5),2,'front_glass_core_low_open_terrace_floor')
for x in [72,100]:box((x,24,108.5),(2,12,17),1,'front_glass_core_cap_side_return')
box((100,-27,57),(3.2,1.7,90),4,'rear_side_tower_narrow_vertical_recess')
box((111,0,120),(29,54,3),2,'right_tower_high_platform')
# Left exposed stairs have real air between landings and zigzag flights.
box((-105,0,60),(9,48,114),1,'left_stair_inner_wall')
box((-121,-20,61),(4,8,116),1,'left_stair_back_pier')
box((-121,20,63.5),(4,6,121),1,'left_stair_front_pier')
# Broad real short-end stair wall, pierced rather than deleted into a naked frame.
wall=Manifold.cube((3.5,29,116),True).translate((-121,-5.5,61))
for zz in [17,35,53]:
 cut=Manifold.hull_points([(x,y,z) for x in [-125,-117] for y,z in [(-17,zz), (6,zz+13), (6,zz+2)]])
 wall-=cut
for zz in [82,100]:wall-=Manifold.cube((8,12,11),True).translate((-121,-7,zz))
add(wall,1,'stair_short_end_white_wall_with_true_triangle_and_rectangle_openings')
# Curved short-end balconies bulge outward; open central landing floor slabs only.
angles=np.linspace(math.pi/2,3*math.pi/2,25)
curve=[(-116+10*math.cos(a),10*math.sin(a)+12) for a in angles]
landing=[(-103,2),(-103,22),(-116,22)]+curve[1:]+[(-103,2)]
for level in range(6):
 z=5+18*level
 poly(landing,z,2,1,'left_curved_stair_landing')
 guard=curve+[(x+1.8,y) for x,y in reversed(curve)]
 poly(guard,z+1.5,4.2,1,'curved_platform_solid_guard')
 # two flights with center switch landing, treads join sloped supporting beams.
 for k in range(12):
  yy=-16+k*3.0 if level%2==0 else 17-k*3.0
  zz=z+1.8+k*1.5
  box((-115,yy,zz),(9,3.8,1.6),1,'left_external_stair_tread')
 beam((-115,-16 if level%2==0 else 17,z+1),(-115,17 if level%2==0 else -16,z+17.5),3,1,'left_stair_diagonal_stringer')
box((-115,-16,4.5),(9,5,3),1,'stair_foot_connected_plinth')
# Stepped tower crown, not equal to the straight opposite end.
for yy,hh in [(-18,124),(-5,127),(8,130)]:box((-108,yy,(hh+115)/2),(13,2.5,hh-115),1,'left_stepped_crown')
box((-116,20,123),(20,4,5),1,'left_crown_crosspiece')
# Central high white volume and adjacent distinctly lower shallow curved metal roof.
box((-10,-1,128),(45,34,21),1,'central_high_white_roof_volume')
for x in [-23,-8,8]:box((x,16.5,126),(4,1.5,9),4,'central_high_box_front_windows')
box((-50,-1,121.5),(34,34,8),1,'adjacent_lower_roof_volume')
# Longitudinal x axis, shallow curved cross section across width, actual 2mm roof shell.
ys=np.linspace(-19,18,25)
for ya,yb in zip(ys,ys[1:]):
 za=127+2.2*(1-((ya+.5)/18.5)**2);zb=127+2.2*(1-((yb+.5)/18.5)**2)
 add(Manifold.hull_points([(x,y,z) for x in [-68,-31] for y,z0 in [(ya,za),(yb,zb)] for z in [z0-1.8,z0]]),7,'low_shallow_curved_metal_roof')
for y in [-18.6,17.6]:box((-49.5,y,126),(37,1.4,2),7,'curved_roof_edge_thickened_termination')
# PV six clearly separated arrays, two over high white box, low arrays either side.
pv_groups=[(-84,25,119.5),(-21,19,139.5),(1,19,139.5),(38,30,122),(73,30,122),(111,29,124)]
for i,(cx,w,bz) in enumerate(pv_groups):
 # High edge rear, low edge front, preserved ventilated gap under every array.
 def pz(y):return bz+3.7-(y+19)*.10
 for x in [cx-w/2+2,cx+w/2-2]:
  for y in [-17,17]:
   bottom=138.5 if i in [1,2] else (121 if i==5 else 117)
   top=pz(y)
   box((x,y,(bottom+top)/2),(1.2,1.2,top-bottom+.5),6,'pv_support_post')
 add(Manifold.hull_points([(x,y,z) for x in [cx-w/2,cx+w/2] for y in [-19,19] for z in [pz(y)-1.1,pz(y)]]),5,'separate_sloping_pv_array')
 box((cx,-19,pz(-19)+.3),(w+1,1.3,1.0),6,'pv_high_edge_thickened_cap')
 for x in np.linspace(cx-w/2,cx+w/2,7):beam((x,-19,pz(-19)-.1),(x,19,pz(19)-.1),.35,6,'pv_grid_longitudinal')
 for y in np.linspace(-19,19,9):beam((cx-w/2,y,pz(y)-.1),(cx+w/2,y,pz(y)-.1),.35,6,'pv_grid_crossbar')
# Brown open entrance pergola on rear, low steps; no filled false entrance box.
for x in [57,87]:
 for y in [-27,-38]:box((x,y,23),(3.5,3.5,40),3,'two_storey_entry_pergola_post')
for x in [57,67,77,87]:box((x,-32.5,43),(2,15,3),3,'entry_open_pergola_crossbeam')
for y in [-27,-38]:
 for zz in [24,43]:box((72,y,zz),(33,3,3),3,'two_storey_entry_pergola_rail')
for k in range(3):box((72,-31-k*2.4,3.5+k*.55),(28,14-k*3,1.3),2,'entry_low_steps')
FEATURES=dict(subject='正修科技大學幼兒保育館',version='2024-08-27 visible PV exterior',storeys=6,roof_projections_not_full_seventh_floor=True,front_wave_rear_straight=True,asymmetric_end_towers=True,pv_groups=len(pv_groups),source_proportion_not_surveyed=True,opaque_glazing=True,interior_solidified=True,physical_print_tested=False)

# Reflection establishes image handedness: curved stair left in the front view.
parts=[p.mirror((1,0,0)) for p in parts]
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
