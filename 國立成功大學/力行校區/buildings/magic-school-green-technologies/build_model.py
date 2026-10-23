"""NCKU Magic School, 2011–2013 source-bound whole-building exterior upgrade."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NCKU source observations.
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

# Coordinates follow unmirrored 1F/3F plan: +X toward auditorium, +Y toward rear stairs.
# Relative side names are authoritative; no geodetic survey coordinate claim.
SCALE=5.0
palette=[('display_base','#929B91',255),('warm_gray_concrete','#B9B39D',255),('opaque_dark_glazing','#344547',255),('metal_frames_rails','#AFB4AC',255),('blue_eave_and_PV','#225E89',255),('red_steel_and_rain_collector','#B82F25',255),('garden_green','#647E3A',255),('garden_light_green','#98A363',255),('auditorium_gray_metal_roof','#6B7779',255),('yellow_wind_turbines','#D5AF28',255),('dark_recess_louvers','#4C504B',255),('PV_dark_blue_cells','#213C59',255),('wood_entry_louvers','#65503B',255)]
def cube(a,b,c,d,e,f):return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def block(a,b,c,d,e,f,col,name):add(cube(a,b,c,d,e,f),col,name)
def sheet(rows,thick,col,name):
 # Grid skin with true volume, not a solid wedge to ground.
 vs=np.array(rows);ny,nx,_=vs.shape;v=np.r_[vs.reshape(-1,3), (vs-np.array([0,0,thick])).reshape(-1,3)];n=nx*ny;f=[]
 for j in range(ny-1):
  for i in range(nx-1):
   a=j*nx+i;b=a+1;c=b+nx;d=a+nx;f += [[a,b,c],[a,c,d],[a+n,c+n,b+n],[a+n,d+n,c+n]]
 edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(n-2,n-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
 for a,b in zip(edge,edge[1:]+edge[:1]):f += [[a,a+n,b+n],[a,b+n,b]]
 tm=trimesh.Trimesh(v,f,process=False);tm.fix_normals();add(Manifold(Mesh(np.array(tm.vertices,dtype=np.float32),np.array(tm.faces,dtype=np.uint32))),col,name)
def rail(points,h=.95,w=.13):
 for a,b in zip(points,points[1:]):
  a=np.array(a);b=np.array(b)
  for z in [.3,.6,h]:beam(a+[0,0,z],b+[0,0,z],w,3,'open_metal_guardrail')
  for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/2)+1)):
   p=a+(b-a)*t;beam(p,p+[0,0,h],w,3,'guardrail_post')
def window_y(x0,x1,y,z0,z1,label):
 block(x0,x1,y-.09,y+.09,z0,z1,3,label+'_frame');block(x0+.13,x1-.13,y-.12,y+.12,z0+.13,z1-.13,2,label+'_pane')
 for x in np.arange(x0+.8,x1,.85):block(x-.045,x+.045,y-.14,y+.14,z0,z1,3,label+'_mullion')
 block(x0,x1,y-.14,y+.14,z1-.52,z1-.44,3,label+'_transom')
def window_x(y0,y1,x,z0,z1,label):
 block(x-.09,x+.09,y0,y1,z0,z1,3,label+'_frame');block(x-.12,x+.12,y0+.13,y1-.13,z0+.13,z1-.13,2,label+'_pane')
 for y in np.arange(y0+.8,y1,.85):block(x-.14,x+.14,y-.045,y+.045,z0,z1,3,label+'_mullion')
 block(x-.14,x+.14,y0,y1,z1-.52,z1-.44,3,label+'_transom')
def stairs(a,b,width,n,label):
 a=np.array(a);b=np.array(b)
 for t in np.linspace(0,1,n):
  p=a+(b-a)*t;box(p,(width,abs(b[1]-a[1])/n+.06,.17),3,label+'_tread')
 for dx in [-width*.43,width*.43]:beam(a+[dx,0,-.15],b+[dx,0,-.15],.22,3,label+'_stringer')
 rail([a+[-width/2,0,0],b+[-width/2,0,0]]);rail([a+[width/2,0,0],b+[width/2,0,0]])
block(-3,44,-4,31,0,.32,0,'NON_SITE_thin_display_plinth')
block(-.3,40.3,-.3,28.3,.25,.75,1,'visible_building_platform_hidden_B1_omitted')
# Two office wings and auditorium block, retaining central two-storey atrium.
block(0,24,1.5,6,.65,8.6,1,'front_office_wing_interior_simplified')
add(cube(0,24,20,28,.65,8.6)-cube(10,17,26.75,28.3,4.9,7.8),1,'rear_office_wing_with_recessed_2F_balcony')
# Third storey is the roof-profile volume below, not a flat box protruding above planting.
for x in [1.5,7,12.5,18]:window_y(x,x+3.5,2.26,9.2,10.9,'third_storey_front_setback_window_band')
block(22,25,6,20,.65,12.6,1,'hall_interface_circulation_spine')
# Auditorium lower classrooms and tall enclosure. Roof follows longitudinal unequal gable.
block(25,40,0,28,.65,11.8,1,'auditorium_and_lower_classrooms')
# Boat end is a broad solid auditorium wall above one narrow lower band.
window_y(26.2,38.8,-.05,1.5,2.65,'boat_side_low_window_band')
block(25.8,39.1,-.65,.04,2.9,3.1,4,'boat_side_blue_low_shade')
window_y(38.25,38.95,-.05,8.1,11.7,'boat_side_edge_vertical_window')
for z in [2.1,6.1]:
 window_x(1,26,40.04,z,z+1.55,'hall_outer_window_band')
for y in [0.8,9.5,18.5,26.5]:block(39.9,40.4,y-.22,y+.22,.75,12,1,'hall_outer_pier')
# Source body/GBC completed oblique: grouped vertical openings on -Y office face.
for x in [16,17.6,19.2,20.8]:
 for z in [1.2,5.4]:window_y(x,x+1.12,1.44,z,z+2.1,'body_side_grouped_vertical_openings')
# True central atrium volume: two office strips and open galleries, roof above but not filled.
for z in [4.6,8.5]:
 block(0,23.8,5.8,8,z-.22,z,1,'atrium_front_open_gallery_slab')
 block(0,23.8,18,20.2,z-.22,z,1,'atrium_rear_open_gallery_slab')
 block(20.2,24,8,18,z-.22,z,1,'atrium_end_bridge_slab')
 rail([(0,8,z),(20.2,8,z),(20.2,18,z),(0,18,z)])
for x in [1,6,11,16,21]:
 for y in [7.7,18.3]:block(x-.17,x+.17,y-.17,y+.17,.7,9.9+.2*(x+1)+1.6*((y-14)/15)**2-.28,1,'atrium_pillars')
for z in [1.4,5.5]:
 for x in [1,7,13,19]:window_y(x,x+3.5,5.96,z,z+2,'atrium_office_opening');window_y(x,x+3.5,20.03,z,z+2,'atrium_rear_opening')
# Registered -X entrance faces the atrium long axis, not the south office wall.
# Wood upper louvers behind the three red arcs; real lower entry is empty.
for y in [8,10,16,18]:block(-.1,.2,y-.16,y+.16,.75,9.9+.2*.9+1.6*((y-14)/15)**2-.3,3,'entry_frame_post')
for z in np.arange(6.2,9.45,.32):block(-.15,.2,8,18,z,z+.12,12,'wood_entry_upper_open_louver')
for y in [8.0,17.85]:block(-.15,.2,y,y+.15,.75,6.3,12,'wood_entry_jamb')
# Silver louver panel at one side of entry and wrapped corner only.
for y in [18.4,23,27.8]:block(-.2,.15,y-.12,y+.12,.75,9.9+.2*.9+1.6*((y-14)/15)**2-.3,3,'corner_screen_posts')
for z in np.arange(1.1,9.75,.32):
 block(-.25,.17,18.4,28,z,z+.11,3,'silver_corner_screen_gap')
 block(-.25,2.2,27.85,28.2,z,z+.11,3,'silver_screen_corner_return')
# West attached upper gallery along the south office portion, red supports under eave.
block(-1.4,1.8,-.1,8.1,4.55,4.85,3,'entry_face_attached_upper_gallery')
rail([(-1.4,.1,4.85),(-1.4,8.1,4.85)])
for y in [0.6,2.9,5.2,7.5]:beam((-1.45,y,.72),(-1.15,y,9.9+.2*(-.15)+1.6*((y-14)/15)**2-.28),.23,5,'inclined_red_entry_columns')
# Source entrance frontage uses restrained doors/louver shutters, not all glass.
for y in [1,3.6]:
 for z in [1.2,5.4]:
  block(-.08,.12,y,y+1.6,z,z+2.2,10,'entry_office_dark_shutter')
  for zz in np.arange(z+.15,z+2.15,.22):block(-.15,.14,y,y+1.6,zz,zz+.07,3,'entry_office_shutter_blade')
# body/06/85: the entry gallery wraps the -X/-Y corner as an L, not one face only.
block(-.1,15.5,-1.4,1.8,4.55,4.85,3,'south_return_upper_gallery_slab')
rail([(-1.4,.1,4.85),(-1.4,-1.4,4.85),(15.4,-1.4,4.85),(15.4,1.5,4.85)])
block(-.2,15.6,-1.8,1.8,8.65,8.9,1,'south_return_canopy_below_setback_third_floor')
block(-.2,15.6,-1.83,-1.58,8.65,8.96,4,'south_return_blue_eave_band')
for x in [1.8,5.1,8.4,11.7,15]:beam((x,-1.45,.72),(x+.25,-1.45,8.82),.23,5,'south_return_inclined_red_columns')
for x in [2,6.8,11.6]:
 for z in [1.2,5.3]:window_y(x,x+2.9,1.44,z,z+2.1,'south_gallery_recessed_dark_openings')
# Actual red-arc portal leads directly into central atrium.
block(-3,.5,9,16,.3,.8,1,'entry_step_platform')
for k in range(3):
 pts=[]
 for t in np.linspace(0,1,25):
  ang=t*math.pi/2;pts.append((-1.0-k*.65,14.5-(4.2-.5*k)*(1-math.cos(ang)),.8+(5.6-.8*k)*math.sin(ang)))
 path(pts,.26,5,'three_curved_red_entry_canopies')
 for a,b in zip(pts,pts[1:]):sheet([[a,(.3,a[1],a[2])],[b,(.3,b[1],b[2])]],.14,5,'entry_canopy_skin_rooted_at_portal')
# Ramp alongside entrance, separate from the garden stairs and rain stairs.
sheet([[(-2.8,16,.8),(-1.5,16,.8)],[(-2.8,27,.34),(-1.5,27,.34)]],.3,1,'source85_entry_access_ramp')
rail([(-2.8,16,.8),(-2.8,27,.34)],.65)
# Curved vegetated roof skin over office/atrium part, rises to equipment/tower rear.
def rz(x,y):return 9.9+.20*(x+1)+1.6*((y-14)/15)**2
xs=np.linspace(-1.8,21,40);ys=np.linspace(-1,28.5,35)
# Closed third-storey office strips, with top profile following the planted skin.
for ya,yb in [(2.3,6),(20,28)]:sheet([[(x,y,rz(x,y)-.45) for x in np.linspace(0,24,25)] for y in np.linspace(ya,yb,8)],8,1,'third_storey_office_strip_under_roof')
sheet([[(x,y,rz(x,y)) for x in xs] for y in ys],.48,1,'continuous_curved_green_roof_structural_skin')
path([(-1.8,y,rz(-1.8,y)) for y in ys],.28,4,'blue_entry_curved_eave')
for y in [-1,28.5]:path([(x,y,rz(x,y)) for x in xs],.28,4,'blue_side_eave')
for i,x in enumerate(np.linspace(-1.4,19.8,15)):
 for ya,yb in [(-.7,7.6),(9,28.2)]:
  yy=np.linspace(ya,yb,25)
  sheet([[(xx,y,rz(xx,y)+.12) for xx in [x,x+1.12]] for y in yy],.16,6 if i%3 else 7,'registered_garden_planting_band')
  path([(x,y,rz(x,y)+.19) for y in yy],.14,3,'garden_band_retaining_lip')
for x in np.arange(-1.3,21,.53):
 z=rz(x,8.3)+.12;block(x,x+.54,7.7,8.9,z-.15,z,3,'garden_access_stair_tread')
rail([(-1.3,8.5,rz(-1.3,8.5)),(21,8.5,rz(21,8.5))],.8)
block(20.5,25,-.2,28,13.0,14.3,1,'registered_rear_equipment_platform')
# Distinct tall ventilation towers; source back view has tapered big stack and middle stair block.
block(21,25,18,27,13.0,17.8,1,'office_buoyancy_vent_tower')
window_x(18.6,26.4,20.96,14.3,16.7,'tower_entry_facing_dark_glass')
cap=[(21,17.7),(25,17.7),(25,20.3),(24,20.9),(21,19.4)]
add(CrossSection([cap]).extrude(9.1).transform([[1,0,0,0],[0,0,-1,27.05],[0,1,0,0]]),8,'office_vent_tall_folded_gray_cap')
# Rear central stair projection with real arched ground void.
st=cube(17.8,23.2,26.5,29,.65,15.1)
p=[(19.4,.5),(21.4,.5),(21.4,2.8)]+[(20.4+math.cos(t),2.8+math.sin(t)) for t in np.linspace(0,math.pi,25)[1:]]
cut=CrossSection([p]).extrude(3.5).transform([[1,0,0,0],[0,0,-1,29.5],[0,1,0,0]])
add(st-cut,1,'rear_stair_tower_true_arched_entry')
add(CrossSection([p]).extrude(.08).transform([[1,0,0,0],[0,0,-1,28.06],[0,1,0,0]]),10,'rear_arch_recess_dark_entry_leaf')
for x in [18.5,21.6]:
 for z in [4.6,7,9.4,11.8]:window_y(x,x+.65,29.04,z,z+1.8,'stair_tower_vertical_slit')
# Source82 +Y office side: two principal window groups, one genuinely recessed 2F balcony.
for x0,x1 in [(2.5,8.8),(10,17)]:
 for z in [1.5,9.2]:window_y(x0,x1,28.04,z,z+1.8,'long_window_side_two_groups')
window_y(2.5,8.8,28.04,5.5,7.3,'long_window_side_2F_right_group')
window_y(10.2,16.8,26.78,5.2,7.5,'long_window_side_recessed_balcony_back')
block(9.8,17.2,26.7,29.2,4.62,4.92,1,'source82_recessed_balcony_slab')
rail([(9.8,28,4.92),(9.8,29.2,4.92),(17.2,29.2,4.92),(17.2,28,4.92)])
# Source GBC rear: central wider projecting window and lower door under the broad stack.
for x0,x1 in [(24.4,29.1),(35,39.5)]:
 for z in [1.5,5.6]:window_y(x0,x1,28.04,z,z+1.8,'rear_stack_flanking_windows')
block(29.6,34.7,28,28.85,4.7,5.1,1,'rear_central_window_projecting_sill')
window_y(29.8,34.5,28.78,5.1,7.5,'rear_stack_central_wide_projected_window')
block(30.3,33.8,28,28.1,.75,3.5,10,'rear_stack_lower_entry')
# Broad auditorium exhaust tower: taper profile is not a rectangular replacement wall.
prof=[(26,8.6),(38,8.6),(38,14),(35.8,17),(35.8,21),(28.3,21),(28.3,17),(26,14)]
add(CrossSection([prof]).extrude(2.5).transform([[1,0,0,0],[0,0,-1,28.3],[0,1,0,0]]),1,'auditorium_tapered_buoyancy_stack')
cap=[(25.7,20.7),(28.4,20.7),(28.4,23.3),(27.2,24.0),(25.7,22.5)]
add(CrossSection([cap]).extrude(7.7).transform([[0,0,1,28.2],[1,0,0,0],[0,1,0,0]]),8,'auditorium_stack_tall_folded_gray_cap')
# Independent auditorium double pitch metal roof, with real air space above to PV.
def hr(y):return 12.3+(y+1)*.24 if y<=17 else 16.62-(y-17)*.36
for ya,yb in [(-1,17),(17,29)]:sheet([[(x,y,hr(y)) for x in [24.5,40.5]] for y in [ya,yb]],.32,8,'auditorium_independent_double_pitch_roof')
# Seal upper side triangular wall under roof, not the floating PV clearance.
for x in [25,39.65]:
 sheet([[(x,y,hr(y)-.25),(x+.35,y,hr(y)-.25)] for y in [-.1,17,28]],3.0,1,'hall_upper_side_profile')
# Back-side rain collector exterior stair, separate red vertical collector and top umbrella.
block(40,42,21.4,23.1,.7,14.2,5,'red_rainwater_vertical_collector')
for level in [1,5,9,13]:
 block(39.8,43.4,19.3,21.4,level,level+.2,3,'rain_stair_attached_landing')
 rail([(43.4,19.3,level+.2),(43.4,21.4,level+.2),(40,21.4,level+.2)])
for i in range(3):stairs((42,19.4,1.2+i*4),(42,25.5,5.2+i*4),1.8,18,'rain_exterior_stair')
for z in [5,9,13]:
 block(39.8,43.3,25.3,27,z,z+.2,3,'rain_stair_rear_landing');rail([(43.3,25.3,z+.2),(43.3,27,z+.2),(40,27,z+.2)])
sheet([[(39.6,19,14.4),(44,19,14.4)],[(39.6,27.8,15),(44,27.8,15)]],.25,5,'red_rain_collection_umbrella')
beam((41,22,.75),(41,22,14.6),.3,5,'rain_collector_spine')
# Leaf-shaped floating PV, a single photograph-bound tilted pose (62/77/78/79).
# Long axis along hall, no fusion with double-pitched roof beneath it.
def pvz(y):return 15.3+.24*(y+2)
def pvw(y):return 1.0+6.5*max(0,math.sin(math.pi*(y+3)/28))**.7
py=np.linspace(-2.9,24.9,51);rows=[]
for y in py:rows.append([(32+u*pvw(y),y,pvz(y)+.30*(1-u*u)) for u in np.linspace(-1,1,17)])
sheet(rows,.24,11,'single_pose_floating_leaf_PV_array')
for y in np.linspace(-2.5,24.5,17):
 w=pvw(y);beam((32-w,y,pvz(y)-.4),(32+w,y,pvz(y)-.4),.16,3,'PV_backframe_rib')
 for x in [32-w,32+w]:beam((x,y,pvz(y)-.4),(x,y,pvz(y)),.14,3,'PV_backframe_upright')
for u in [-.72,0,.72]:path([(32+u*pvw(y),y,pvz(y)-.45) for y in py],.21,3,'PV_longitudinal_backframe')
for u in [-1,1]:path([(32+u*pvw(y),y,pvz(y)+.05) for y in py],.16,3,'PV_edge_frame')
for y in np.linspace(-1,24.5,22):
 w=pvw(y);beam((32-w+.1,y,pvz(y)+.33),(32+w-.1,y,pvz(y)+.33),.055,3,'PV_approximate_panel_grid')
# Visible A-frame fixed proxy supporting the selected movable PV posture.
for x in [27,37]:
 beam((x,9,hr(9)),(x,17,19.65),.38,3,'PV_Aframe_front_leg');beam((x,25,hr(25)),(x,17,19.65),.38,3,'PV_Aframe_rear_leg')
beam((26.7,17,19.65),(37.3,17,19.65),.43,3,'PV_rotation_axis_static_proxy')
for x in [27,37]:block(x-.32,x+.32,16.6,17.4,19.25,19.83,3,'PV_visible_axis_bearing')
# PV access stair from tower-side platform to high support.
stairs((25.5,23,15.1),(25.5,17,19.7),1.1,20,'PV_maintenance_access')
block(23,27,22,24,14.8,15.1,3,'PV_access_connecting_landing')
# Folded shade canopy and rooftop walkway, clearly not a further PV leaf.
start_folded=len(parts)
block(12,24,21,23,14.2,14.5,3,'roof_walkway_attached_to_tower')
for x in [13,18]:beam((x,22,14.4),(x,22,17.5),.18,3,'folded_shade_posts')
sheet([[(12,21,18.313),(16,21,17.313),(20,21,18.513)],[(12,23,17.413),(16,23,18.213),(20,23,17.413)]],.18,1,'folded_origami_shade')
rail([(12,21,14.5),(24,21,14.5)])
parts[start_folded:]=[p.transform([[0,1,0,0],[-1,0,0,30],[0,0,1,0]]) for p in parts[start_folded:]]
# Wind-turbine tower distinct from broad buoyancy vents and rain collector.
start_wind=len(parts)
block(19.5,25,23,26.5,17,17.3,5,'wind_tower_upper_platform')
beam((20,24,rz(20,13)-.12),(20,24,17.1),.3,5,'wind_platform_support');beam((24,24,14.18),(24,24,17.1),.3,5,'wind_platform_support')
for x in [21.2,23.5]:
 for y in [24,25.2]:beam((x,y,17.2),(x,y,28.5 if x>22 else 27),.24,5,'wind_tower_red_open_leg')
for z in [17.3,19.7,22.1,24.5,26.9]:
 for y in [24,25.2]:beam((21.2,y,z),(23.5,y,z),.22,5,'wind_tower_crossbar');beam((21.2,y,z),(23.5,y,min(z+2.4,28.5)),.18,5,'wind_tower_diagonal')
for x in [21.8,23.1]:
 for z in [18.3,20.6,22.9,25.2,27.0]:
  if x<22 and z>26:continue
  ringm=Manifold.cylinder(.36,.60,.60,24)-Manifold.cylinder(.6,.44,.44,24).translate((0,0,-.1))
  add(ringm.rotate((90,0,0)).translate((x,23.92,z)),9,'yellow_wind_turbine_ring')
  for t in [0,2.094,4.189]:beam((x,23.74,z),(x+.5*math.cos(t),23.74,z+.5*math.sin(t)),.11,9,'simplified_wind_rotor_blade')
# Two observed spherical tanks on attached red platforms, no invented rear plumbing.
for x,z in [(19.2,17.4),(25.4,16.5)]:
 block(x-1.15,x+1.15,23.2,25.5,z-.25,z,5,'water_tank_platform');add(Manifold.sphere(1.03,32).scale((1,1,.9)).translate((x,24.3,z+.78)),3,'observed_spherical_water_tank')
 beam((x,24.3,(rz(x,13.3) if x<21 else hr(13.3))-.12),(x,24.3,z),.28,5,'tank_platform_support')
parts[start_wind:]=[p.translate((0,-11,0)) for p in parts[start_wind:]]
# Nine visible rooftop units in 73, coarse proxies only, no hidden pipe invention.
for x in [20.6,22.1,23.6]:
 for y in [1,3,5]:
  block(x,x+1.25,y,y+1.2,14.2,15.2,3,'visible_rooftop_equipment_proxy');block(x+.1,x+1.15,y-.02,y+.06,14.5,15.1,10,'visible_unit_grille')
# Attached boat-shaped balcony, separate from excluded independent foreground landscape boat.
poly=[(27,-.05),(38,-.05),(37.5,-1.6),(36,-3),(33,-3.7),(29,-2.8),(27,-1.3)]
add(CrossSection([poly[::-1]]).extrude(.22).translate((0,0,9.5)),3,'attached_boat_balcony_deck')
rail([(x,y,9.72) for x,y in poly]+[(27,-.05,9.72)],.95)
for x in np.linspace(27.5,37.5,11):
 d=1.1+2.3*math.sin(math.pi*(x-27)/11)
 pts=[(x,-d*t,9.5-1.9*math.sin(math.pi*t)) for t in np.linspace(0,1,19)]
 path(pts,.21,3,'boat_balcony_hanging_curved_rib')
path([(x,-(1.1+2.3*math.sin(math.pi*(x-27)/11))*.5,7.6) for x in np.linspace(27.5,37.5,30)],.24,3,'boat_balcony_lower_keel')
path([(37.5,-1.6,9.5),(38,-2.4,10.5),(38,-2.5,11.7),(37.7,-2.4,12),(37.3,-2.3,11.7),(37.5,-2.3,11.3)],.25,3,'boat_balcony_upturned_curled_prow')
# Third buoyancy tower on +X auditorium side, opposite the rain stair's other edge (84).
block(39.3,41.2,17.5,19.15,8.5,21.1,1,'third_narrow_auditorium_buoyancy_tower')
cap=[(17.5,20.9),(19.15,20.9),(19.15,23.4),(18.4,24.0),(17.5,22.7)]
add(CrossSection([cap]).extrude(1.95).transform([[0,0,1,39.25],[1,0,0,0],[0,1,0,0]]),8,'third_narrow_tower_tall_gray_folded_cap')
# Preserve the source82 balcony void through the simplified upper-office fill as well.
for i,r in enumerate(part_records):
 if r['name']=='third_storey_office_strip_under_roof':
  m=(parts[i]-cube(10,17,26.75,28.3,4.9,7.8)).as_original();material_for_id[m.original_id()]=r['material'];parts[i]=m
# 1F plan -Y service/restroom projection: low semicircular outer boundary only.
# The 3F plan does not repeat this arc; no speculative three-storey cylinder.
service=[(16,3),(23,3),(23,0)]+[(19.5+3.5*math.cos(t),-3.5*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
add(CrossSection([service[::-1]]).extrude(4.35).translate((0,0,.22)),1,'one_F_semicircular_service_projection')
add(CrossSection([service[::-1]]).extrude(.18).translate((0,0,4.55)),1,'low_service_projection_roof_approximate_transition')
# Normalize as display millimeters without implying measured scale.
parts=[p.translate((-20,-13,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立成功大學力行校區孫運璿綠建築研究大樓／綠色魔法學校','existing_identity_upgrade':True,'version':'2011-08-03 EXIF views plus 2013 publication exterior, cross-checked with 1F/3F plans; not 2026 current equipment','scope':'Whole above-ground building, attached ramps stairs balcony and roof structures; no adjacent buildings or independent foreground boat','coordinates':'Plan hand preserved: +X toward auditorium, +Y rear towers; relative names used, no compass assertion','nominal_display_factor':SCALE,'roof_topology':['continuous curved planted skin over office/atrium','independent auditorium unequal double pitch metal roof','floating leaf PV in single observed tilt pose'],'supports':'Supports required beneath floating PV, stair treads, canopy, boat balcony and eaves. Not physically printed. Closed simplified office/hall interiors; open central atrium. Hidden B1 and fine services omitted.','buoyancy_ventilation_towers':3,'entry_and_south_return_gallery':'L-shaped, not mirror of north long-window facade','one_F_service_projection':'low semicircular footprint only; upper transition approximate','minimum_detail_nominal_mm':.055*SCALE,'dimension_claim':'proportional exterior interpretation only, no complete dimensioned RF or measured BIM'}

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
