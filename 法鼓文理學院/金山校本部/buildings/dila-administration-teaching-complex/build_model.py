"""DILA connected GA/GB/GC complex, source-bound exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from DILA source observations.
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

# Approximate metre-like coordinates traced proportionally from drawing-1.
# IMAGE (u right,v down) -> WORLD (X=v,Y=u), not (u,v). Correct handedness.
# Front = -Y, GC left (-X), GB right (+X), GA behind (+Y).
SCALE=2.1
palette=[('display_plinth','#87918A',255),('fairfaced_concrete','#B9BBB0',255),('dark_opaque_glazing','#344C54',255),('metal_rails_fins','#68757B',255),('roof_planting','#6E8145',255),('paving','#A8AA9D',255),('dry_green_roof','#899067',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,col,name):add(cube(x0,x1,y0,y1,z0,z1),col,name)
def poly(points,z,h,col,name):add(CrossSection([points]).extrude(h).translate((0,0,z)),col,name)
def rail(a,b,z,name):
 beam((*a,z+.2),(*b,z+.2),.43,3,name+'_bottom');beam((*a,z+1.05),(*b,z+1.05),.43,3,name+'_top')
 n=max(2,int(np.linalg.norm(np.array(a)-b)/1.4)+1)
 for u in np.linspace(0,1,n):
  p=np.array(a)*(1-u)+np.array(b)*u;beam((*p,z),(*p,z+1.05),.43,3,name+'_post')
def stairs(x0,x1,y0,y1,z0,z1,name,axis='y',solid=False):
 # Distinct treads on an inclined solid slab; no fill underneath external flight.
 n=max(3,round(abs(z1-z0)/.22));w=x1-x0
 if axis=='y':
  pts=[(x,y,z+d) for x in [x0,x1] for y,z in [(y0,z0),(y1,z1)] for d in [-.5,0]]
 else:pts=[(x,y,z+d) for y in [y0,y1] for x,z in [(x0,z0),(x1,z1)] for d in [-.5,0]]
 add(Manifold.hull_points(pts),1,name+'_inclined_slab')
 for j in range(n):
  u=j/n;v=(j+1)/n;z=z0+(z1-z0)*v
  if axis=='y':block(x0,x1,y0+(y1-y0)*u,y0+(y1-y0)*v+.025,(1.3 if solid else z-.5),z,5,name+'_tread')
  else:block(x0+(x1-x0)*u,x0+(x1-x0)*v+.025,y0,y1,(1.3 if solid else z-.5),z,5,name+'_tread')
 for side in [0,1]:
  a=(x0+side*w,y0,z0) if axis=='y' else (x0,y0+side*(y1-y0),z0)
  b=(x0+side*w,y1,z1) if axis=='y' else (x1,y0+side*(y1-y0),z1)
  beam(tuple(np.array(a)+[0,0,1]),tuple(np.array(b)+[0,0,1]),.43,3,name+'_rail')
  for u in np.linspace(0,1,max(3,n//4)):
   p=np.array(a)*(1-u)+np.array(b)*u;beam(tuple(p),tuple(p+[0,0,1]),.43,3,name+'_post')
def pane_y(x0,x1,y,z0,z1,name):
 block(x0,x1,y-.12,y+.12,z0,z1,2,name+'_glass')
 for x in np.arange(x0,x1+.01,2.1):block(x-.12,x+.12,y-.23,y+.23,z0-.1,z1+.1,3,name+'_mullion')
 for z in [z0,z0+(z1-z0)*.62,z1]:block(x0-.1,x1+.1,y-.22,y+.22,z-.12,z+.12,3,name+'_transom')
def pane_x(x,y0,y1,z0,z1,name):
 block(x-.12,x+.12,y0,y1,z0,z1,2,name+'_glass')
 for y in np.arange(y0,y1+.01,2.1):block(x-.23,x+.23,y-.12,y+.12,z0-.1,z1+.1,3,name+'_mullion')
 for z in [z0,z0+(z1-z0)*.62,z1]:block(x-.22,x+.22,y0-.1,y1+.1,z-.12,z+.12,3,name+'_transom')
def roof_rect(x0,x1,y0,y1,z,name,col=4):
 block(x0,x1,y0,y1,z-.1,z+.35,5,name+'_roof')
 block(x0+.9,x1-.9,y0+.9,y1-.9,z+.25,z+.46,col,name+'_planting')
 for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:beam((*a,z+.65),(*b,z+.65),.6,1,name+'_parapet')
# Base does not portray entire campus or bridge. Ground terraces are deliberately local.
block(-3,113,-5,88,0,1.5,0,'local_display_plinth_not_surveyed_terrain')
block(-1,47,-1,68,1.4,6.2,5,'GC_local_hillside_support')
block(47,85,0,40,1.4,3.0,5,'lower_court_ground')
block(24,110,68,86,1.4,7.8,1,'GA_buried_substructure_closed_not_cutaway')
block(84,111,14,84,1.4,4,1,'GB_visible_lower_slope_substructure')
# GA four main floors, recessed inner wall behind true open galleries.
block(24,108,72,84,7.7,25.8,1,'GA_four_floor_enclosed_core')
# The top short and long frames are separated at x47..51.
# Cut the whole core too: upper floor gap is genuine through space.
parts[-1]=(parts[-1]-cube(47,51,71.8,84.2,21.3,26)).as_original();material_for_id[parts[-1].original_id()]=1
# Open transverse ground portals from source photo19, not full underground cutaway.
parts[-1]=(parts[-1]-cube(47,55,71.8,84.2,12.8,16.5)).as_original();material_for_id[parts[-1].original_id()]=1
for x0,x1 in [(24.8,46.2),(51.8,108.2)]:
 parts[-1]=(parts[-1]-cube(x0,x1,81.5,84.2,22.05,25.65)).as_original();material_for_id[parts[-1].original_id()]=1
for z in [8,12.5,17,21.5]:
 block(24,108,68,73,z-.55,z,1,'GA_open_gallery_slab')
 for x in [25,35.5,46,57,68,79,90,101,107]:block(x-.45,x+.45,68.1,69.15,z-.1,z+4.5,1,'GA_gallery_pier')
 rail((24.4,68.2),(107.6,68.2),z,'GA_court_guard')
 for x0,x1 in [(25,34),(36,45),(56,66),(68,77),(79,88),(90,99),(101,107)]:pane_y(x0,x1,71.9,z+.55,z+3.65,'GA_recessed_inner_window')
 # Rear windows are proportionally simplified because trees obscure small divisions.
 for x0,x1 in [(25,34),(36,45),(52,62),(64,74),(76,86),(88,98),(100,107)]:pane_y(x0,x1,81.53 if z==21.5 else 84.02,z+.8,z+3.5,'GA_rear_approximate_window')
# Top storey deep thick frames, two independent roof boxes, no solid curtain across gap.
for x0,x1 in [(23,47),(51,109)]:
 block(x0,x1,67,84.5,21.15,21.8,1,'GA_top_frame_floor');block(x0,x1,67,84.5,25.7,26.4,1,'GA_top_frame_roof')
 for x in [x0,x1-.75]:block(x,x+.75,67,84.5,21.2,26.3,1,'GA_top_frame_end_wall')
 roof_rect(x0+.5,x1-.5,67.5,84,26.4,'GA_top_green_roof',6)
 for x in np.arange(x0+11,x1-1,12):block(x-.35,x+.35,68.4,83.1,26.75,26.99,5,'GA_roof_plot_divider')
block(27,35,75,82,26.3,28.2,1,'GA_short_roof_service');block(28,34,76,81,28.1,28.4,5,'GA_service_roof')
block(79,85,75.5,79.5,26.7,27.0,2,'GA_visible_dark_roof_flat_cap_unspecified_equipment')
block(46.5,51.5,80.5,83.5,21.2,21.8,1,'GA_upper_gap_rear_link')
rail((47,80.6),(51,80.6),21.8,'GA_gap_link_guard')
# GC two storeys, three blocks with genuine open slots between and a fourth by GA.
for i,(y0,y1) in enumerate([(3,20),(24.5,41.5),(46,63)]):
 block(27,44,y0,y1,6.1,16.7,1,'GC_classroom_block_'+str(i))
 for z in [8,12.5]:
  pane_x(44.05,y0+.6,y1-.6,z+.45,z+3.7,'GC_court_recessed_window')
  pane_x(26.95,y0+.6,y1-.6,z+.45,z+3.7,'GC_hall_side_window')
 roof_rect(25.8,46,y0-.4,y1+.4,17,'GC_roof_'+str(i),6)
 # Pathways lie on green roof, not unsupported aerial beams.
 for a,b in [((27,y0+1),(45,y1-1)),((27,y1-1),(40,y0+1))]:beam((*a,17.53),(*b,17.53),.65,5,'GC_diagonal_roof_path')
for z in [8,12.5,17]:
 for x0,x1 in [(24,27.2),(43.8,47)]:block(x0,x1,2.5,68.5,z-.6,z,1,'GC_continuous_open_gallery')
 if z<17:
  for x in [24.6,46.3]:
   for y in np.arange(3,69,8.6):block(x-.35,x+.35,y-.45,y+.45,z-.1,z+4.6,1,'GC_gallery_pier')
  rail((46.6,3),(46.6,68),z,'GC_court_gallery_guard');rail((24.4,3),(24.4,68),z,'GC_outer_gallery_guard')
# GC front solid end with recessed bands and attached glass lift tower.
pane_y(27,44,2.98,8.65,10.8,'GC_front_lower_openings')
pane_y(26,45.8,2.96,12.5,13.05,'GC_front_narrow_bluegray_band')
block(25.9,45.9,2.5,3.15,13.05,16.8,1,'GC_front_upper_broad_blind_concrete_panel')
block(45.5,49.7,15,19,3,19.2,1,'GC_lift_tower');pane_y(46.1,49.1,14.93,4,18.5,'GC_lift_glass');pane_x(49.73,15.6,18.4,4,18.5,'GC_lift_side_glass')
# Three quarter-circle lecture halls: two straight edges and one convex quarter arc.
for i in range(3):
 y=3.8+21.4*i;cx=3.3;r=14.5
 pts=[(cx,y)]+[(cx+r*math.cos(a),y+r*math.sin(a)) for a in np.linspace(0,math.pi/2,65)]
 poly(pts,6.1,6.8,1,'GC_quarter_circle_lecture_hall_'+str(i))
 # Roof planting inset retaining the same 90-degree sector, not a full cylinder.
 pts2=[(cx+.7,y+.7)]+[(cx+.7+(r-1.2)*math.cos(a),y+.7+(r-1.2)*math.sin(a)) for a in np.linspace(0,math.pi/2,65)]
 poly(pts2,12.88,.4,4,'lecture_hall_green_sector_'+str(i))
 arc=[(cx+r*math.cos(a),y+r*math.sin(a),13.35) for a in np.linspace(0,math.pi/2,65)]
 path(arc,.55,1,'lecture_hall_curved_parapet');beam((cx,y,13.35),(cx+r,y,13.35),.55,1,'lecture_hall_straight_parapet');beam((cx,y,13.35),(cx,y+r,13.35),.55,1,'lecture_hall_straight_parapet')
 # Raised podium slab has true elongated light well toward classroom wing.
 deck=cube(2.5,24.3,y-.7,y+20.4,11.7,12.25)-cube(20.1,24.4,y+.5,y+14.8,11.5,12.5)
 # Aperture under the glazed light tube remains open down to ground; dark cap is opaque miniature glazing.
 tube=(19,y+11.2);hole=Manifold.cylinder(1,1.4,1.4,48).translate((*tube,11.5));deck-=hole
 add(deck,5,'lecture_podium_with_lightwell_and_tube_aperture_'+str(i))
 block(20.1,24.2,y+.5,y+14.8,6.15,6.45,4,'sunken_lightwell_planting')
 rail((20.2,y+.5),(20.2,y+14.8),12.25,'lecture_lightwell_guard');rail((24.1,y+.5),(24.1,y+14.8),12.25,'classroom_lightwell_guard')
 block(17.2,27,y+15.4,y+17.5,11.7,12.25,1,'lecture_cross_lightwell_bridge')
 ringm=Manifold.cylinder(1.35,1.65,1.65,64)-Manifold.cylinder(1.6,1.4,1.4,64).translate((0,0,-.1))
 add(ringm.translate((*tube,12.1)),1,'cylindrical_rooflight_curb_'+str(i));add(Manifold.cylinder(.18,1.5,1.5,64).translate((*tube,13.28)),2,'cylindrical_rooflight_glass_'+str(i))
 beam((tube[0]-1.5,tube[1],13.5),(tube[0]+1.5,tube[1],13.5),.25,3,'rooflight_crossbar');beam((tube[0],tube[1]-1.5,13.5),(tube[0],tube[1]+1.5,13.5),.25,3,'rooflight_crossbar')
 stairs(3,17.4,y+17.7,y+20,8,12.25,'lecture_outside_stair_'+str(i),axis='x')
 block(2.6,17.6,y+17.5,y+20.3,6.1,8,1,'lecture_stair_lower_support')
 # Columns supporting podium edges, not filled lightwell.
 for xx,yy in [(19,y),(19,y+17),(3,y+19)]:block(xx-.35,xx+.35,yy-.35,yy+.35,6,12,1,'lecture_podium_pier')
# GB long low connector behind large two-storey hall, broad glass lower level.
block(89,104,34,84,3.9,12,1,'GB_low_connector_core')
for z in [4.6,8.3]:pane_x(88.92,35,82,z,z+3.2,'GB_connector_court_windows');pane_x(104.05,35,82,z,z+3.2,'GB_connector_outer_windows')
for z in [8,12.5]:
 block(85,106,33,84,z-.6,z,1,'GB_low_connector_floor');rail((85.3,34),(85.3,68),z,'GB_connector_court_guard')
 for yy in np.arange(35,82,8):block(85.2,86,yy-.4,yy+.4,4,z,1,'GB_connector_colonnade')
# Hall body and solid right-side wall, deep glazed front and left.
block(87,108,16,34,4,20.8,1,'GB_two_storey_hall_solid_core')
parts[-1]=(parts[-1]-cube(105.7,108.2,17,33,12.8,20.35)).as_original();material_for_id[parts[-1].original_id()]=1
# Photo14 outer elevation: deep frame, top narrow glazing, projecting opaque box with two windows, adjacent tall glass.
pane_x(105.72,17.2,32.8,18.05,20.2,'GB_outer_recessed_upper_band')
pane_x(105.72,17.2,21.4,12.85,20.2,'GB_outer_recessed_tall_glass')
block(105.65,108.7,21.5,32,12.5,18.1,1,'GB_outer_projecting_blind_box')
for ya,yb in [(23,25.5),(28,30.5)]:pane_x(108.72,ya,yb,13.05,15.55,'GB_outer_box_two_windows')
pane_x(108.03,17,33,4.8,11.6,'GB_outer_lower_broad_glass')
block(108,111,16,34,12,12.55,1,'GB_outer_colonnade_overhang')
for yy in [17.5,24.5,32.5]:block(109.4,110.1,yy-.35,yy+.35,4,12.4,1,'GB_outer_lower_colonnade_pier')
for z0,z1 in [(4.8,11.6),(13.1,20.1)]:
 pane_y(87.8,107.2,15.93,z0,z1,'GB_front_tall_glazing');pane_x(86.93,17,32.8,z0,z1,'GB_inner_side_glazing')
 # Outer face is reconstructed separately below: not a duplicate fin face.
for z in [4.5,12.5,21]:block(85.7,109,14.7,35,z-.5,z+.15,1,'GB_projecting_hall_floor')
for x in np.arange(87,108,1.35):block(x-.19,x+.19,14.2,16.1,5,20.8,3,'GB_dense_front_vertical_sun_fin')
for y in np.arange(17,33,1.4):block(85.5,87.15,y-.19,y+.19,12.8,20.8,3,'GB_inner_upper_vertical_fin')
roof_rect(86,109,15,35,21.15,'GB_green_roof')
for x in [93.6,101]:block(x-.4,x+.4,16,34,21.45,21.7,5,'GB_three_green_roof_strip_divider')
block(84,89,33,39,4,23.1,1,'GB_glass_stair_lift_core');pane_x(83.96,33.6,38.5,5,22.5,'GB_core_glass');pane_y(84.6,88.5,32.95,5,22.5,'GB_core_front_glass')
# Different-height court terraces and broad stepped axis. No uniform court fill.
block(47,85,30,40,1.4,4.8,5,'court_middle_landing');block(47,85,52,54,1.4,8.6,5,'court_upper_landing')
block(47,85,67,68.3,1.4,12.5,5,'court_GA_entry_landing')
stairs(62,72,22,30,3,4.8,'court_front_broad_steps',solid=True)
stairs(62,72,40,52,4.8,8.6,'court_middle_broad_steps',solid=True)
stairs(62,72,54,67,8.6,12.5,'court_upper_broad_steps',solid=True)
# Planted terraced side strips flanking central axis, segmented retaining ledges.
for x0,x1 in [(49,60),(74,83)]:
 for y0,y1,z in [(40,45,4.8),(45,49,6.0),(49,53,7.3),(53,57,8.6),(57,61,10),(61,65.5,11.3)]:
  block(x0,x1,y0,y1,1.4,z,1,'court_terrace_retaining');block(x0+.5,x1-.5,y0+.4,y1-.4,z-.02,z+.18,4,'court_terrace_planting')
# Multi-level true open links on both edges; supported floor decks span air.
for x0,x1,ya,yb,z in [(46.4,51,17,68.2,8),(46.4,51,32,68.2,12.5),(46.4,51,60,68.2,17),(82,86,30,68.2,8),(82,86,35,68.2,12.5)]:
 block(x0,x1,ya,yb,z-.55,z,1,'court_multilevel_link_'+str(z));rail((x0+.2,ya),(x0+.2,yb),z,'court_link_guard');rail((x1-.2,ya),(x1-.2,yb),z,'court_link_guard')
 for yy in [ya+1,yb-1]:block(x0+.4,x0+1.1,yy-.4,yy+.4,2.8,z,1,'court_link_support')
# No GC-to-GB transverse bridges: source central bands are stairs/platforms.
# Exposed stairs from galleries to courtyard and lower outside GB side.
stairs(49,52,19,28,3,8,'GC_court_external_stair')
stairs(79,82,30,41,4.8,8,'GB_court_external_stair')
stairs(108,111,18,31,2,4.5,'GB_outer_lower_steps',solid=True)
# Floor/window geometry already connected, no campus bridge, pools or other buildings.
block(86.75,87.1,32.7,33.05,4.5,20.3,3,"GB_glazing_return_seam_solidification")
parts=[p.translate((-55,-40,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'法鼓文理學院・綜合大樓（GA／GB／GC）','campus':'金山校本部','scope':'Complete connected GA 4 main floors, GC 2 floors and three quarter-sector lecture halls, GB 2-storey tall hall and lower connector; courtyard stairs, multilevel bridges and visible slope base. Excludes bridge, dormitories and Yangsheng Hall.','basis':'Architect 2015 project listing and completion photographs with unknown capture date, plus official 2020 usage plan; not a 2026 condition or measured as-built.','nominal_proportional_units_to_display_mm':SCALE,'coordinate_hand':'Plan image u-right -> world +Y; v-down -> world +X; image-to-world handedness corrected before mesh generation. Front -Y faces GC left and GB right.','thin_details':{'rails_mm':.43*SCALE,'small_rooflight_crossbars_mm':.25*SCALE,'slabs_mm':.55*SCALE},'supports':'Bridge undersides, gallery overhangs, lecture podiums, GA top frames and stair slabs require supports. Miniature glazing is opaque; interiors mostly solid. No physical print or universal minimum-wall claim.'}

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
