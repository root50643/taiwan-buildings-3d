"""Original photo-derived NPTU exterior miniature. Units: mm.
Visual estimates from cited public photographs, not a measured survey.
No third-party 3D geometry; see sources.json for scope and unknown elevations.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def cyl(x,y,z,r,h,n=120):return Manifold.cylinder(h,r,r,circular_segments=n).translate((x,y,z))
def sector(r1,r2,a,b,z,h):
 ts=np.linspace(math.radians(a),math.radians(b),max(3,int(abs(b-a)/2)+1))
 pts=[(r2*math.cos(t),r2*math.sin(t)) for t in ts]+[(r1*math.cos(t),r1*math.sin(t)) for t in ts[::-1]]
 return CrossSection([pts]).extrude(h).translate((0,0,z))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def gable(x,y,z,w,d,h):parts.append(profile([(x-w/2,z),(x+w/2,z),(x,z+h)],y,d))
def paired_front(x,y,z,w=4.8,h=4.6):
 for dx in [-w/4,w/4]:cut(x+dx,y,z,w/2-.65,2.4,h)
def band_front(x,y,z,w,h,n):
 for i in range(n):cut(x-w/2+(i+.5)*w/n,y,z,w/n-1.0,2.4,h)
# Wuyu: high rear block, twin end towers, lower courtyard wings and front gatehouse.
# The open court is backed by completed-photo evidence; dimensions remain estimates.
add(0,0,0,150,140,3)
add(0,31,2.8,132,28,125.2)
# Flat-topped end towers rise above the principal facade.
for x in [-54,54]:add(x,25,2.8,24,40,134.2)
# Intermediate shoulder masses step forward of the upper towers.
for x in [-54,54]:add(x,11,2.8,24,24,88.2)
# Five-storey side galleries and four-storey front range enclose a real open courtyard.
for x in [-54,54]:add(x,-20,2.8,24,44,46.2)
add(0,-46,2.8,132,18,36.2)
# Deep central gatehouse supports the observed large gabled roof.
add(0,-44,2.8,29,31,38.2)
# Main front entrance passes through the lower range; no enclosed interior shell.
cut(0,-44,2.9,18,40,12)
# Two circular-front stair cores flank the low hall's central entrance.
for x in [-12.5,12.5]:parts.append(cyl(x,-30,2.8,4.4,39.2,48))
add(0,-44,40.4,36,35,1.8);gable(0,-44,41.8,36,35,11.5)
# Lower range outer windows: four stories, grouped narrow lights not generic square bays.
for x in [-49,-31,31,49]:
 for z in [7,15.5,24,32]:band_front(x,-55,z,14.5,4.8,4)
for x in [-12.5,12.5]:
 for z in [7,15.5,24,32]:cut(x,-25.5,z,3.2,2.5,4.8)
# Low range courtyard side: grouped windows with projecting jambs.
for x in [-31,31]:
 for z in [7,15.5,24,32]:band_front(x,-36.7,z,14.5,4.8,4)
# Side galleries on courtyard and outer sides, including their long bands and paired jambs.
for side in [-1,1]:
 for y in [-35,-24,-13,-2]:
  for z in [7,16,25,34,43]:
   cut(side*42,y,z,2.6,8.0,4.9)
   cut(side*66,y,z,2.6,8.0,4.9)
  for dy in [-4.9,4.9]:add(side*41.5,y+dy,5,1.8,1.4,43)
# Main courtyard elevation: low open galleries, intermediate narrow bands, upper recessed bays.
for z in [7,16,25]:
 for x in [-29,29]:cut(x,16.7,z,17,5.5,5.9)
for z in [34,43]:
 for x in [-28,28]:band_front(x,16.7,z,14.0,5.2,4)
# Central large glass panel covers the distinct middle group of floors.
cut(0,16.7,49,22,3.4,39)
# Glass fields stay continuous: tiny facade mullions omitted rather than coarse solid stripes.
for x in [-29,29]:
 for z in [52,61,70,79]:
  cut(x,16.6,z,12.5,4.0,6)
  # Balcony edge is rooted in the facade and is deliberately stout at miniature scale.
  details.append(box(x,17.2,z-.4,13,3.8,1.2))
# Higher levels switch from single paired windows to horizontal banks and back to paired lights.
for x in [-38,-30,-22,22,30,38]:paired_front(x,16.7,90,4.8,4.8)
for z in [99,108]:
 for x in [-30.5,30.5]:band_front(x,16.7,z,21,4.8,6)
for z in [117,123]:
 for x in [-38,-30,-22,22,30,38]:paired_front(x,16.7,z,4.8,3.7)
# The middle vertical bay has two separate glazed fields under a central pediment.
for z in [91,100]:cut(0,16.7,z,22,3.4,4.8)
# These two fields are continuous horizontal glazing, not masonry-separated lights.
cut(0,16.7,109,22,3.4,17)
# No coarse horizontal bar across this observed single glass field.
# Slender adjoining paired-window strips border the central glass.
for x in [-15.5,15.5]:
 for z in [34,43,52,61,70,79,90,99,108,117,123]:paired_front(x,16.7,z,4.4,4.6 if z<117 else 3.7)
# Main roof pediment and the visible upper end-tower ventilation squares.
gable(0,31,127.6,30,28,7.3)
cut(0,16.7,127.7,7,2.2,4.2)
for x in [-54,54]:
 for z in [96,105,114,123]:cut(x,5.0,z,4.6,2.4,4.7)
 cut(x,5.0,130,8.0,2.4,4.7)
 # Their inward-facing glazed strips are distinct from masonry fronts.
 for z in [54,66,78,90,102,114,126]:cut(x-12*(1 if x>0 else -1),10,z,2.5,10,9)
# Intermediate shoulder fronts: a central paired strip and broader flanking recesses.
for x in [-54,54]:
 for z in [54,63,72,81]:
  paired_front(x,-1.3,z,4.4,4.8)
  for dx in [-7.4,7.4]:cut(x+dx,-1.3,z,7,2.6,4.8)
# Observed side elevations carry continuous horizontal bands, with their tower ends solid.
for side in [-1,1]:
 for z in [54,63,72,81]:
  for y in [4,15]:cut(side*66,y,z,2.8,8.1,5.0)
 for z in [96,108,120]:
  for y in [25,35]:cut(side*66,y,z,2.5,5.4,4.7)
# Opposite rear elevation is photographed: central projecting glazed curved drum.
parts.append(cyl(0,45,2.8,14,85,96))
# Remove the circle half buried in the main block by union, not a separate shell.
for z,h in [(54,31)]:
 cuts.append(sector(12.2,16,20,160,z,h).translate((0,45,0)))
# Upper rear central glass / pediment and characteristic grouped side windows.
cut(0,44.5,94,22,5.0,32)
# Continuous tall rear glazed field, distinct from the shorter front glazed field.
for z in [54,63,72,81,90]:
 for x in [-44,-28,28,44]:band_front(x,45.2,z,13,4.9,3)
for z in [99,108,117,123]:
 for x in [-38,-30,-22,22,30,38]:paired_front(x,45.2,z,4.8,4.7 if z<117 else 3.7)
# Rear tower windows are kept only on photographed regions; lowest obstructed parts remain plain.
for x in [-54,54]:
 for z in [81,90,99,108,117,126]:cut(x,46.1,z,4.8,2.4,4.8)
# Parapet caps and the low-range exposed flat roof ledges are 1.6 mm thick.
for x in [-54,54]:
 add(x,-20,48.3,24.8,44.8,1.6)
 add(x,11,90.3,24.8,24.8,1.6)
 add(x,25,136.3,24.8,40.8,1.6)
add(0,-46,38.3,132.8,18.8,1.6)
# Low entry stairs. Court sculpture, trees and canopies are intentionally omitted.
for i in range(4):add(0,-62+i*1.7,2.8,27,2.0,.55*(i+1))

solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
print('PARTS', [(round(s.volume(),4),s.bounding_box()) for s in solid.decompose()])
assert len(solid.decompose())==1, 'Detached part: fix source geometry'
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.is_winding_consistent
mesh.export(OUT/'model.stl')
print('mm',mesh.extents,'triangles',len(mesh.faces))
