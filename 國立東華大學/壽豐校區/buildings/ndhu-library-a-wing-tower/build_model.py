"""NDHU library Building A: historically referenced H-shaped library and tower.
Official A1-A6 evacuation plans establish wing scope; separate B1-B3 exclude INC.
Exterior: 2020-01-07 south, 2000-06/07 construction-era roof and north evidence.
Original miniature-mm CSG. Not a 2026 as-built reconstruction; no imported mesh.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
P={'base_mm':(150,108,2.5),'wing_center_x':46.3,'wing_width':31.4,'wing_north':36.7,'wing_south':-35.3,'low_wall_top':33.,'main_wall_top':46.,'tower_top':80.2,'crown_pier_mm':4.0}
parts=[];cuts=[];after=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,n=64):return Manifold.cylinder(h,r,r,n).translate((x,y,z))
def hip(x,y,z,w,d,rise):
 # A broad, flat ridge replaces a knife edge for miniature robustness.
 if w>=d:rw=max(5.,w-d+3.);rd=2.8
 else:rw=2.8;rd=max(5.,d-w+3.)
 roof=CrossSection.square((w,d),True).extrude(rise,scale_top=(rw/w,rd/d)).translate((x,y,z))
 parts.append(roof);add(x,y,z+rise-.1,rw,rd,1.0)
def recess_y(x,y,z,w,h,depth=1.3):cuts.append(box(x,y,z,w,depth*2,h))
def recess_x(x,y,z,w,h,depth=1.3):cuts.append(box(x,y,z,depth*2,w,h))
def pane_y(x,y,z,w,h,rows=0):
 recess_y(x,y,z,w,h,1.25)
 # Backed integral ribs: not floating decorative frames.
 for i in range(1,rows+1):after.append(box(x,y+(.95 if y<0 else -.95),z+h*i/(rows+1)-.4,w,1.0,.8))
add(0,0,0,*P['base_mm'])
# Central six-storey main volume, inset in x relative to low wings.
add(0,10.3,2.4,103.2,31.8,43.6)
# Four-storey H side wings; north projections remain short and flat-roofed.
for s in [-1,1]:
 x=s*P['wing_center_x']
 add(x,.7,2.4,31.4,72.,30.6)
 for z in [10.7,19.0,26.1,32.6]:add(x,.7,z,32.2,72.6,1.0)
 hip(x,-4.7,33.0,34.0,64.7,5.2) # continuous low roof wraps the inset high block
 # Northern terrace: lower outer front, higher inward step; no invented hip roof.
 add(x,29.6,32.7,32.2,15.1,1.3)
 add(x-s*4.3,27.6,33.5,21.0,9.8,4.1)
 add(x-s*4.3,27.6,37.3,22.1,10.9,1.3)
 # A narrow integral northern parapet, sized for the miniature.
 add(x,36.4,33.3,32.0,1.8,1.8)
# Main three-roof silhouette; substantial eave bands and separate higher roof.
for z in [10.7,18.7,31.0,45.7]:add(0,10.3,z,104.0,32.6,1.0)
# Undated overhead image in the official 2026-06-23 terrace notice reveals
# a perimeter pitched roof around a broad recessed flat roof, not a solid hip.
parts.append(CrossSection.square((106.8,35.3),True).extrude(4.8,scale_top=(96/106.8,27/35.3)).translate((0,10.3,46.1)))
# The recess stops on the existing solid top; it does not create a hidden shell.
cuts.append(CrossSection.square((78,11),True).extrude(6.0,scale_top=(86/78,21/11)).translate((0,10.3,46.4)))
# Southern high facade: THREE major glazing bays; two tall bands, not six window rows.
for x in [-13.,5.,23.]:
 pane_y(x,-5.65,20.0,12.0,10.0,2)
 pane_y(x,-5.65,33.0,12.0,11.0,2)
# Slender recesses at two major piers are subordinate to the three broad bays.
for x in [-4.,14.]:recess_y(x,-5.7,34.0,1.7,9.0,1.0)
# Upper end window groups remain above the two lower-wing rooflines.
for x in [-43.0,-34.5,38.0,46.5]:pane_y(x,-5.65,41.0,6.6,3.2,0)
# Southern base band, on either side of the recessed central entry.
for x in [-13,13,17,21,25]:recess_y(x,-5.65,12.4,1.8,4.6,.95)
# Deep entry recess and stout lintel. Retain back wall (not an invented interior hall).
cuts.append(box(0,-5.7,2.5,16.8,9.4,10.2))
add(0,-8.7,12.3,20.2,8.0,1.5)
for x in [-9.4,9.4]:add(x,-10.6,2.4,2.4,3.2,10.1)
# North high facade: three broader bays and different end-window groups.
for x in [-22.,0.,22.]:
 pane_y(x,26.25,20.0,15.,9.8,2)
 pane_y(x,26.25,33.0,15.,10.9,2)
for x in [-46,-40,40,46]:pane_y(x,26.25,40.1,3.3,4.2,0)
for x in [-25,-20,-15,-10,10,15,20,25]:recess_y(x,26.25,12.0,1.8,5.0,1.0)
cuts.append(box(0,26.3,2.5,15.0,7.2,9.0))
# Low southern wings. Central tall glass, THREE narrow slots on each side;
# upper floor has three broad grouped windows rather than the lower pattern.
for s in [-1,1]:
 x=s*P['wing_center_x']; y=-35.35
 pane_y(x,y,12.2,9.6,12.8,3)
 for dx in [-12.0,-8.8,-5.6,5.6,8.8,12.0]:
  for z in [12.4,20.1]:recess_y(x+dx,y,z,1.65,5.0,1.0)
 for dx in [-10.5,0,10.5]:pane_y(x+dx,y,27.5,8.2,4.0,0)
 for dx in [-11.0,-3.7,3.7,11.0]:recess_y(x+dx,y,3.6,4.3,5.7,1.2)
 # Side elevations use grouped slots under wider top windows, with uncertain
 # portions simplified rather than claiming a surveyed count.
 for y0 in [-29.7,-22.3,-14.9,-7.5,1.5,10.5,19.5,29.0]:
  for z in [12.2,20.0]:
   for dy in [-1.45,1.45]:recess_x(s*62.0,y0+dy,z,1.6,5.1,1.0)
  recess_x(s*62.0,y0,27.5,5.5,3.8,1.0)
  recess_x(s*62.0,y0,3.8,3.6,5.2,1.0)
 # Courtyard inner faces only in exposed southern and northern portions.
 for y0 in [-28.0,-19.0,-10.0]:
  if s<0 and y0>-15:continue # buried tower/wing intersection must remain solid
  for z in [12.2,20.0]:recess_x(s*30.55,y0,z,3.7,5.0,1.0)
  recess_x(s*30.55,y0,27.5,5.8,3.7,1.0)
 # The three main paired narrow-window groups in the historical rear photo.
 for dx in [-9.5,0.,9.5]:
  for z in [4.0,12.3,20.2,27.6]:
   for a in [-1.4,1.4]:recess_y(x+dx+a,36.75,z,1.65,4.9 if z<27 else 3.7,1.)
 # Northern raised terrace step receives a few confirmed-size narrow slots.
 for dx in [-6,0,6]:recess_y(x-s*4.3+dx,32.55,34.0,2.4,2.8,.9)
# Main exposed east/west upper walls: each side carries broad paired groups.
for s in [-1,1]:
 for yy in [2.5,15.5]:
  pane=box(s*51.65,yy,35.0,2.6,8.0,8.9);cuts.append(pane)
# Low open south forecourt portico. Attached piers, deep air gaps, substantial roof.
for s in [-1,1]:
 add(s*41,-36.2,2.4,42.,4.5,1.0)
 add(s*41,-36.2,10.0,42.,4.5,1.6)
for xx in [-60.0,-47.0,-34.0,-22.0,22.0,34.0,47.0,60.0]:
 add(xx,-36.2,3.2,2.6,3.0,7.0)
# Central portico opening remains broad; side returns climb back to entry.
for s in [-1,1]:
 add(s*23.2,-21.,10.0,3.2,29.0,1.6)
 for yy in [-29,-20,-10]:add(s*23.2,yy,2.4,2.6,2.8,7.9)
# Shallow semicircular entry steps, not a cylindrical infill of the court.
for i,(r,h) in enumerate([(22.5,.7),(21.0,1.3),(19.5,1.9)]):
 disk=cyl(0,-24,2.4,r,h,96)^box(0,-38,2.3,48,28,3.0)
 parts.append(disk)
# Tower: narrow south-west shaft with rusticated base and tall upper fluting.
tx,ty=-25.5,-11.2
add(tx,ty,2.4,12.6,13.6,64.5)
add(tx+2.8,ty+3.5,2.4,12.7,13.8,39.0)
for z in [11.0,18.8,27.0,40.5]:add(tx,ty,z,13.1,14.1,.9)
# The front has three tall recessed flutes, separated by robust integral stiles.
for dx in [-4.,0.,4.]:
 recess_y(tx+dx,ty-6.85,42.0,2.0,20.4,1.0)
 for z in [27.5,32.6,37.7]:recess_y(tx+dx,ty-6.85,z,1.7,3.4,.95)
# Side fluting is similarly vertical, but lower backed wall remains solid.
for s in [-1,1]:
 for dy in [-4.,0.,4.]:recess_x(tx+s*6.35,ty+dy,43.2,2.0,18.9,1.0)
for z in [20.0,14.0]:recess_y(tx,ty-6.85,z,2.0,3.0,1.0)
# Characteristic projecting intermediate glazed/corbel balcony below tall shaft.
add(tx,ty-1.1,31.8,14.6,15.0,1.6)
add(tx,ty-1.1,33.2,14.0,14.6,5.8)
for dx in [-4.5,0,4.5]:recess_y(tx+dx,ty-8.45,34.0,2.2,4.2,.9)
add(tx,ty-1.1,38.8,15.,15.6,1.4)
# Heavy cornice below the two-level viewing crown.
add(tx,ty,64.9,15.0,15.8,2.3)
add(tx,ty,67.1,12.7,13.6,1.8)
# Lower glazed room, with deep window recesses. Corner piers stay >=4 mm.
add(tx,ty,68.5,12.7,13.6,5.2)
for s in [-1,1]:
 recess_y(tx,ty+s*6.85,69.1,4.7,3.5,1.5)
 recess_x(tx+s*6.4,ty,69.1,5.6,3.5,1.5)
add(tx,ty,73.4,14.6,15.3,1.4)
# Fully open top band: four 4 mm piers; broad slab cap, no needle corners.
for sx in [-1,1]:
 for sy in [-1,1]:add(tx+sx*4.35,ty+sy*4.65,74.4,4.,4.,4.3)
add(tx,ty,78.3,16.3,16.6,1.9)
# Execute booleans in a deterministic order; every shape joins the common base.
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in after:solid+=p
assert len(solid.decompose())==1,[(s.volume(),s.bounding_box()) for s in solid.decompose()]
m=solid.simplify(.001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
# Photo-calibrated z compression: the six-storey block is low and wide,
# while the freestanding upper tower shaft retains its taller rhythm.
v=mesh.vertices.copy();z=v[:,2];v[:,2]=np.where(z<=2.5,z,np.where(z<=46,2.5+(z-2.5)*.80,37.3+(z-46)*.96));mesh.vertices=v.astype(np.float32)
mesh.export(OUT/'model.stl')
print({'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'watertight':mesh.is_watertight})
