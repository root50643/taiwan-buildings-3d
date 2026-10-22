"""NFU CMA Building / 國立虎尾科技大學文理暨管理大樓. 2007-design / completion-photo exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NFU source observations.
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

# Design-derived metre coordinates, uniformly enlarged 2.7 display mm per metre.
# X1=0, X10=81; north low wing y=0..12.2, south high wing y=28.2..49.5.
SCALE=2.7; G=5.5
palette=[('display_base','#8E9791',255),('warm_beige_tile','#CCB992',255),('gray_concrete','#969B98',255),('silver_metal','#ABB4B0',255),('opaque_dark_glazing','#435A5C',255),('ivory_membrane','#F0EEE1',255),('roof_paving','#ABA89A',255),('pale_opaque_blind_panel','#DADBD2',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,col,name):add(cube(x0,x1,y0,y1,z0,z1),col,name)
def poly(points,z,h,col,name):add(CrossSection([points]).extrude(h).translate((0,0,z)),col,name)
# Support slab is not surveyed terrain. True lower court floor is 4.5 m below 1F.
block(-6,86,-9,55,0,1,0,'display_plinth_not_surveyed_terrain')
# Ground platform has a real aperture plus narrow exterior light wells.
terrain=cube(-5,85,-8,54,1,G-.4)
terrain-=cube(35,63.5,12.2,28.2,.9,G+.1)
terrain-=cube(36,80,-2.2,-.1,1.2,G+.1)
terrain-=cube(1,66,49.6,51.8,1.2,G+.1)
add(terrain,6,'ground_platform_open_B1_court_and_light_wells')
block(35,63.5,12.2,28.2,1,1.45,2,'B1_visible_court_floor')
# South nine-storey high wing. Front and back recesses vary independently by floor.
high=cube(0,67,28.2,49.5,1,42.5)
# Ground entrance recess through the inward room line, not through entire block.
high-=cube(18.2,26.8,28.1,38.5,G,10.0)
high-=cube(20,27,46.5,49.6,G,9.8)
# Actual terraces and double-height bays from 5F through 9F plans.
front_voids=[(45,63,28.1,32.7,22.8,30.1),(27,45,28.1,32.7,30.8,34.2),(45,63,28.1,36.7,30.5,42.6),(0,9,28.1,32.7,34.8,42.1),(27,45,28.1,37.2,34.8,42.6),(27,67,28.1,37.2,38.5,42.6)]
for x0,x1,y0,y1,z0,z1 in front_voids:high-=cube(x0,x1,y0,y1,z0,z1)
# Source p45/photo00: intermediate EXTERNAL frame beams divide the double-height
# terrace apertures, without filling their interior voids with a new full slab.
for x0,x1,z in [(45,63,26.5),(0,9,38.5)]:
 block(x0-.2,x1+.2,28.1,28.85,z-.2,z+.45,1,'double_height_terrace_external_crossbeam')
 for x in [x0,x1]:block(x-.2,x+.2,28.1,28.85,z-3.6,z+3.6,1,'double_height_terrace_end_frame')
# Rear balcony is offset from inward stepped terraces; tall semi-outdoor stair slot.
rear_voids=[(27,40.5,45,49.6,30.8,34.1),(27,36,41.5,49.6,34.8,42.6),(19.2,22.5,46.0,49.6,10.8,39.7)]
for q in rear_voids:high-=cube(*q)
# Both short-end stairs have genuine recesses, with different openings.
high-=cube(-.1,2.8,39.4,44.2,10.8,41.8)
high-=cube(64.1,67.1,40.4,45,10.8,41.8)
add(high,1,'south_nine_floor_asymmetric_terraces_and_stair_voids')
# Floor lips and recessed terrace guardrails. No solid dark fake holes.
def rail(a,b,z,name):
 beam((a[0],a[1],z+.2),(b[0],b[1],z+.2),.42,3,name+'_lower')
 beam((a[0],a[1],z+1.05),(b[0],b[1],z+1.05),.42,3,name+'_top')
 dist=np.linalg.norm(np.array(b)-a)
 for u in np.linspace(0,1,max(2,int(dist/2.6)+1)):
  p=np.array(a)*(1-u)+np.array(b)*u;beam((*p,z),(*p,z+1.05),.42,3,name+'_post')
for x0,x1,y,z in [(45,63,28.3,22.6),(27,45,28.3,30.6),(45,63,36.8,30.6),(0,9,28.3,34.6),(27,45,37.3,34.6),(27,67,37.3,38.6)]:
 block(x0-.2,x1+.2,y-.2,y+.5,z-.25,z+.15,2,'front_terrace_floor_lip');rail((x0,y),(x1,y),z,'front_terrace_guard')
for x0,x1,y,z in [(27,40.5,49.4,30.6),(27,36,49.4,34.6)]:
 block(x0,x1,y-1,y+.1,z-.3,z+.1,2,'rear_balcony_lip');rail((x0,y),(x1,y),z,'rear_balcony_guard')
# Flat roofs and parapet, clipped to 9F footprint and rear central notch.
roof=cube(0,67,28.2,49.5,42.5,42.85)-cube(27,67,28.1,37.2,42.4,43)-cube(27,36,41.5,49.6,42.4,43)-cube(0,9,28.1,32.7,42.4,43)
add(roof,6,'high_roof_irregular_refuge_platform')
for pts in [[(0,32.7),(0,49.5),(27,49.5),(27,41.5),(36,41.5),(36,49.5),(67,49.5),(67,37.2),(27,37.2),(27,28.2),(9,28.2),(9,32.7),(0,32.7)]]:
 for a,b in zip(pts,pts[1:]):beam((*a,43.1),(*b,43.1),.6,1,'high_roof_parapet')
# Design roof service rooms are not an invented full tenth storey.
block(0,14,41.5,49.5,42.4,46.0,1,'roof_electrical_generator_rooms')
block(14,22,41.5,49.5,42.4,46.5,1,'roof_stair_and_lift_service')
block(22,27,41.5,49.5,42.4,45.8,1,'roof_water_service_room')
block(63.2,67,41.5,49.5,42.4,46.2,1,'east_roof_stair_service')
# Low north wing: recessed entrance, three levels, open 3F terrace and real roof aperture.
low=cube(18,81,0,12.2,1,18.5)
low-=cube(18,36,-.1,9.1,G,10.1)
low-=cube(45,63,-.1,9.1,14.8,18.6)
low-=cube(67,72,-.1,4.2,10.8,14.1)
add(low,1,'north_three_floor_wing_with_entry_and_open_terrace')
# Ground columns maintain the deep entrance and support the upper floor.
for x in [18.4,26.8,35.6]:block(x-.35,x+.35,.05,.8,G,10.6,1,'low_entry_pier')
block(19,35.5,8.6,9.1,G,9.3,4,'recessed_low_entry_glazing')
for x in [19,24,29,35]:block(x-.15,x+.15,8.3,9.2,G,9.6,3,'entry_glazing_divider')
block(18,81,0,12.2,18.5,18.85,6,'low_roof_slab_before_terrace_cut')
# Remove this roof slab aperture by replacing its solid in parts.
parts[-1]=parts[-1]-cube(45,63,-.2,9.1,18.4,19)
# Retag altered original to preserve material correspondence.
parts[-1]=parts[-1].as_original();material_for_id[parts[-1].original_id()]=6
for a,b in [((18,0),(45,0)),((63,0),(81,0)),((18,0),(18,12.2)),((81,0),(81,12.2)),((18,12.2),(81,12.2))]:beam((*a,19.1),(*b,19.1),.6,1,'low_roof_parapet')
rail((45,.25),(63,.25),14.7,'low_3F_terrace_rail')
block(63,72,0,9.0,18.5,22.3,1,'low_roof_stair_water_service')
# Round auditorium roof is an outdoor platform, not a glass dome.
roundbody=Manifold.cylinder(10.5-1,12.5,12.5,96).translate((9,6,1))
add(roundbody,2,'gray_round_auditorium')
add(Manifold.cylinder(.45,12.4,12.4,96).translate((9,6,10.5)),6,'round_roof_outdoor_platform')
# Continuous low curved parapet and exterior arc ramp wall.
def arc_ring(cx,cy,r0,r1,z,h,a0,a1,col,name):
 aa=np.linspace(a0,a1,75);pts=[(cx+r1*math.cos(a),cy+r1*math.sin(a)) for a in aa]+[(cx+r0*math.cos(a),cy+r0*math.sin(a)) for a in aa[::-1]];poly(pts,z,h,col,name)
arc_ring(9,6,12.1,12.55,10.8,.85,0,2*math.pi,2,'round_platform_low_parapet')
arc_ring(9,6,13.6,14.05,G-.5,1.45,math.pi*.8,math.pi*1.8,2,'curved_entry_ramp_wall')
for a in np.linspace(math.pi*.6,math.pi*1.9,13):
 # Tangential dark narrow slots on photographed cylindrical face, opaque miniature.
 x,y=9+12.48*math.cos(a),6+12.48*math.sin(a)
 slot=Manifold.cube((.65,.32,4.1),True).rotate((0,0,math.degrees(a)-90)).translate((x,y,7.4));add(slot,4,'round_hall_narrow_vertical_glazing')
# Entrance shallow stairs; ground is raised versus B1 court.
for j in range(5):block(19,36,-3+j*.55,1,G-.75+j*.15,G-.6+j*.15,2,'main_entry_shallow_step')
# Differently placed 1F / 2F / 3F bridges, floor decks over genuine air.
bridges=[(62,65,G),(50,53,10.5),(27,30,14.5),(62,65,14.5)]
for x0,x1,z in bridges:
 block(x0,x1,11.8,28.6,z-.5,z+.05,2,'bridge_level_'+str(z));rail((x0,12),(x0,28.4),z,'bridge_west_guard');rail((x1,12),(x1,28.4),z,'bridge_east_guard')
# Courtyard north-side circulation balconies and sloping stairs (no solid underside fill).
for z in [G,10.5,14.5]:
 block(35,63,11.7,14.2,z-.45,z+.1,2,'court_north_balcony');rail((35,14),(63,14),z,'court_balcony_guard')
def stair(a,b,width,rise,name):
 # Inclined enclosed slab plus distinct tread blocks and side handrails.
 a=np.array(a,float);b=np.array(b,float);d=b-a;L=np.linalg.norm(d[:2]);n=np.array([-d[1],d[0]])/L
 # Beam width would be square; a convex prism gives correct stair slab width.
 points=[]
 for p in [a,b]:
  for dz in [-.45,0]:
   for sign in [-1,1]:points.append([p[0]+sign*n[0]*width/2,p[1]+sign*n[1]*width/2,p[2]+dz])
 add(Manifold.hull_points(points),2,name+'_sloping_slab')
 count=max(3,int(abs(d[2])/.22))
 for i in range(count):
  u=(i+.5)/count;p=a+d*u
  # X-aligned courtyard stairs only.
  box((p[0],p[1],p[2]-.05),(L/count+.12,width,.22),2,name+'_tread')
 for sign in [-1,1]:
  aa=a.copy();bb=b.copy();aa[:2]+=sign*n*width/2;bb[:2]+=sign*n*width/2
  beam(tuple(aa+[0,0,1]),tuple(bb+[0,0,1]),.42,3,name+'_handrail')
  for u in np.linspace(0,1,7):
   p=aa*(1-u)+bb*u;beam(tuple(p),tuple(p+[0,0,1]),.42,3,name+'_post')
for z0,z1 in [(1.45,G),(G,10.5),(10.5,14.5)]:
 stair((37,15.2,z0),(49,15.2,z1),2.5,z1-z0,'court_external_stair_'+str(z0))
 for yy in [13.95,16.45]:block(48.7,49.3,yy-.3,yy+.3,z1-.2,z1+1.4,3,'thickened_stair_rail_terminal')
# B1 entrance to visible court and exposed well windows.
for x in [38,44,50,56,61]:
 block(x-1.2,x+1.2,28.0,28.5,2,4.5,4,'B1_court_window')
# Upper and lower windows, frames and protruding louver boxes use source-bound simplified counts.
def window(x,y,z,w=2.3,h=1.9,side=-1):
 block(x-w/2,x+w/2,y-.1,y+.1,z,z+h,4,'opaque_window_panel')
 for xx in [x-w/2,x,x+w/2]:block(xx-.085,xx+.085,y-.18,y+.18,z-.12,z+h+.12,3,'window_mullion')
 for zz in [z-.1,z+h*.65,z+h+.1]:block(x-w/2-.12,x+w/2+.12,y-.2,y+.2,zz-.07,zz+.07,3,'window_transom')
def louver(x,y,z,side):
 block(x-.55,x+.55,y-.15,y+side*.7 if side>0 else y+.15,z,z+1.95,3,'louver_box_back') if side>0 else block(x-.55,x+.55,y-.7,y+.15,z,z+1.95,3,'louver_box_back')
 for zz in np.linspace(z+.15,z+1.85,5):block(x-.6,x+.6,y+side*.72-.15,y+side*.72+.15,zz-.09,zz+.09,2,'louver_horizontal_fins')
def in_void(x,y,z,voids):return any(a-.2<x<b+.2 and c-.3<y<d+.3 and e-.1<z<f+.1 for a,b,c,d,e,f in voids)
for level in range(9):
 z=G+(0 if level==0 else 5+4*(level-1));wz=z+1.4
 for side,y in [(-1,28.12),(1,49.58)]:
  voids=front_voids if side<0 else rear_voids
  for j,x in enumerate(np.arange(3,65,3.5)):
   if side>0 and level==8 and x<18:continue
   if in_void(x,y,wz,voids) or in_void(x,y,wz+1.9,voids):continue
   if level==0 and ((side<0 and 16.5<x<28.5) or (side>0 and 18.5<x<28.5)):continue
   window(x,y,wz,side=side)
   if j%3==1:louver(x+1.35,y,wz,side)
# Photo13: two pale opaque upper panels, not generic glazing.
for x in [4.5,12]:block(x-1.35,x+1.35,49.45,49.68,40,41.8,7,'rear_upper_pale_blind_panel')
# Photo13: continuous narrow corner glazing band and projecting floor sun lips.
block(65.1,66.7,49.45,49.7,G+.7,42.2,4,'rear_east_corner_vertical_glass_band')
for x in [65.0,66.8]:block(x-.1,x+.1,49.4,49.85,G+.6,42.3,3,'rear_corner_glass_vertical_frame')
for lev in range(9):
 z=G+(0 if lev==0 else 5+4*(lev-1))
 block(64.85,67.15,49.4,50.45,z+.25,z+.5,3,'rear_corner_glass_floor_sunlip')
 block(66.9,67.15,47.0,50.45,z+.25,z+.5,3,'rear_corner_sunlip_return')
 block(65.1,66.7,49.55,49.85,z+2.3,z+2.45,3,'rear_corner_glass_transom')
# Insets at terrace back walls, deliberately not fake surface panels across the openings.
for x0,x1,y,z in [(45,63,32.7,24),(27,45,32.7,32),(45,63,36.7,32),(0,9,32.7,36),(27,45,37.2,36),(36,63,37.2,40)]:
 for x in np.arange(x0+1.8,x1-1,3.5):window(x,y-.08,z,side=-1)
for level in range(3):
 z=G+(0 if level==0 else 5+4*(level-1))+1.3
 for side,y in [(-1,-.08),(1,12.28)]:
  for j,x in enumerate(np.arange(20,80,3.5)):
   if side<0 and ((level==0 and x<36) or(level==2 and 45<x<63)or(level==1 and 65.5<x<73.5)):continue
   window(x,y,z,side=side)
   if j%3==1:louver(x+1.35,y,z,side)
# Different short ends: stair decks project out of real recesses; narrow vertical glazing strips.
for x,inside,yy in [(0,2.4,41.8),(67,64.5,42.7)]:
 for lev in range(1,9):
  z=10.5+4*(lev-1)
  block(min(x,inside)-.5,max(x,inside)+.5,yy-2.3,yy+2.3,z-.35,z+.1,2,'end_stair_projecting_landing')
  rail((x,yy-2.2),(x,yy+2.2),z,'end_stair_landing_guard')
  block(x-.12,x+.12,yy+3.6,yy+4.5,z+.7,z+3.1,4,'short_end_narrow_glass')
# Rear slot has platforms rather than a black painted stripe.
for z in np.arange(10.5,39,4):
 block(19.1,22.6,46,49.7,z-.35,z+.1,2,'rear_semiexternal_stair_landing');rail((19.3,49.4),(22.4,49.4),z,'rear_stair_guard')
# Thickened white anticlastic membrane: grid is a surface, not an invented steel net.
def membrane(x0,x1,y0,y1,zbase,amp,thick,name,nx=44,ny=16,skew=0):
 verts=[]
 def point(i,j):
  u=i/nx;v=j/ny
  # Slight concave longitudinal edges; outer corners meet both building walls.
  x=x0+(x1-x0)*u+skew*v
  y=y0+(y1-y0)*v
  x+=1.1*math.sin(math.pi*v)*(1 if u<.5 else -1)*(abs(2*u-1)**3)
  z=zbase+amp*(2*u-1)*(2*v-1)+.7*math.sin(3*math.pi*u)*math.sin(math.pi*v)
  return [x,y,z]
 for k in [0,1]:
  for i in range(nx+1):
   for j in range(ny+1):
    p=point(i,j);p[2]+=k*thick;verts.append(p)
 faces=[];N=(nx+1)*(ny+1)
 for i in range(nx):
  for j in range(ny):
   a=i*(ny+1)+j;b=a+ny+1
   faces.extend([[a,b+1,b],[a,a+1,b+1],[a+N,b+N,b+1+N],[a+N,b+1+N,a+1+N]])
 border=list(range(ny+1))+[i*(ny+1)+ny for i in range(1,nx+1)]+[nx*(ny+1)+j for j in range(ny-1,-1,-1)]+[i*(ny+1) for i in range(nx-1,0,-1)]
 for a,b in zip(border,border[1:]+border[:1]):faces.extend([[b,a,a+N],[b,a+N,b+N]])
 mm=Manifold(Mesh(np.array(verts,dtype=np.float32),np.array(faces,dtype=np.uint32)))
 add(mm,5,name)
# Main membrane supported by both wings. No overfilled court or heavy posts.
membrane(9,67,11.9,28.5,20.5,1.6,.5,'main_courtyard_curved_white_membrane',44,16,4.5)
membrane(26.8,36.2,41.3,49.7,43.2,1.1,.45,'small_roof_notch_white_membrane',18,14)
# Small thickened corner fittings/short ties, not a conjectural dense roof frame.
for x,y,z in [(9,11.9,22.1),(13.5,28.5,18.9),(67,11.9,18.9),(71.5,28.5,22.1)]:
 block(x-.3,x+.3,y-.3,y+.3,z-.25,z+.7,5,'main_membrane_corner_fitting')
 if x==9:beam((x,y,z),(18,12.0,18.7),.5,3,'main_membrane_short_corner_tie')
 if x==71.5:beam((x,y,z),(66.8,28.4,z),.5,3,'main_membrane_short_corner_tie')
block(17.7,18.3,11.65,12.35,18.4,19.2,3,'main_membrane_low_wing_anchor_fitting')
for x,y,z in [(26.8,41.3,44.3),(26.8,49.7,42.1),(36.2,41.3,42.1),(36.2,49.7,44.3)]:
 block(x-.3,x+.3,y-.3,y+.3,min(z-.3,42.4),z+.75,5,'small_membrane_corner_fitting')
# Solidify the submillimetre sealed canopy-to-wall trim pocket at this connection.
block(20.5,21.2,28.05,28.4,19.75,20.1,5,'main_membrane_wall_seam_solidification')
# Reflect one horizontal axis: PDF +y is downward, not right-handed world +y.
# Manifold performs the orientation-preserving mesh reindexing, not a flipped PNG.
# Keep all components joined; center in XY for gallery cameras. Display units millimetres.
parts=[p.translate((-40,23*-1,0)).scale((-SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立虎尾科技大學文理暨管理大樓','campus':'校本部（第三教學區）','scope':'Complete connected exterior approximation: north 3F, south 9F, round auditorium, visible B1 court, 1–3F bridges/stairs, both membranes and roof service rooms. Adjacent humanities building excluded.','basis':'2007 official design drawings plus six architect completion photographs of unknown capture date; not an as-built or 2026 survey.','nominal_scale_mm_per_design_m':SCALE,'ground_level_mm':G*SCALE,'B1_court_floor_mm':1.45*SCALE,'floor_levels_mm':[v*SCALE for v in [G,10.5,14.5,18.5,22.5,26.5,30.5,34.5,38.5,42.5]],'thin_details':{'rails_mm':.42*SCALE,'main_membrane_vertical_thickness_mm':.5*SCALE,'small_membrane_vertical_thickness_mm':.45*SCALE},'supports':'Main and small membranes, bridges, terrace frames and projecting landings need supports; enclosed interiors solidified, no physical print claim.'}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.00005).simplify(.00005)
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
