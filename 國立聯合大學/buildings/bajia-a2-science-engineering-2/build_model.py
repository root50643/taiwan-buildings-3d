"""理工二館 A2: photo-interpreted courtyard complex, independent 150 mm model.
The U-shaped mass, pitched roofs, corner lanterns and courtyard are evidence-led;
unseen rear details are explicitly simplified. Units are millimeters.
"""
from pathlib import Path
import numpy as np
import manifold3d as m
import trimesh
OUT=Path(__file__).resolve().parent

def box(x,y,z,sx,sy,sz):return m.Manifold.cube((sx,sy,sz),True).translate((x,y,z))
def union(v):return m.Manifold.batch_boolean(v,m.OpType.Add)
def gable(x,y,z,width,length,rise,axis='y'):
 pts=[[-width/2,-length/2,0],[width/2,-length/2,0],[-width/2,length/2,0],[width/2,length/2,0],[0,-length/2,rise],[0,length/2,rise]]
 r=m.Manifold.hull_points(pts)
 if axis=='x':r=r.rotate((0,0,90))
 return r.translate((x,y,z))
def shed(x,y,z,sx,sy,rise):
 pts=[]
 for xx in [-sx/2,sx/2]:
  for yy in [-sy/2,sy/2]:pts += [[xx,yy,0],[xx,yy,.7+(yy/sy+.5)*rise]]
 return m.Manifold.hull_points(pts).translate((x,y,z))
def roof_panel(x,y,sx,sy,plane):
 pts=[]
 for xx in [x-sx/2,x+sx/2]:
  for yy in [y-sy/2,y+sy/2]:pts += [[xx,yy,plane(xx,yy)-.15],[xx,yy,plane(xx,yy)+.65]]
 return m.Manifold.hull_points(pts)
def hip(x,y,z,sx,sy,h):
 return m.Manifold.hull_points([[-sx/2,-sy/2,0],[sx/2,-sy/2,0],[sx/2,sy/2,0],[-sx/2,sy/2,0],[0,0,h]]).translate((x,y,z))
# Common low base ties the entire courtyard building into one printable body.
parts=[box(0,0,1.5,150,145,3)]
# The three main wings make the visible U-shaped courtyard.
for x in [-50,50]:
 parts += [box(x,4,23,22,80,40),box(x,4,43.5,24,82,1.3),gable(x,4,44.1,24,82,5)]
parts += [box(0,39,23,122,22,40),box(0,39,43.5,124,24,1.3),gable(0,39,44.1,24,124,4.8,'x')]
# Lower front-end blocks, visible on both sides of the official aerial photograph.
for x in [-50,50]:
 parts += [box(x,-42,17.5,22,24,29),box(x,-42,32.4,24,26,1.2),hip(x,-42,33,24,26,2.8)]
# Back facade central tall entrance/glazed bay and raised transverse roof.
parts += [box(0,27.3,26.3,21,4.2,46.6),box(0,34.5,49.7,24,19,1.2),shed(0,34.5,50.2,24,19,4.4)]
# Corner lanterns emerge over the wings. Their recesses are closed, not fragile railings.
for x in [-51,51]:
 parts += [box(x,43,48.7,11,11,9.5),box(x,43,53.4,13,13,1.1),hip(x,43,53.9,13,13,4.3)]
# Paired roof-top vent housings on the long wings and rear wing.
for x in [-50,50]:parts += [box(x,7,49,8,22,2.8),gable(x,7,50.4,9,23,1.4)]
for x in [-30,30]:parts += [box(x,39,48.4,21,7,2.6),gable(x,39,49.6,8,22,1.1,'x')]
# Solar arrays visible in newer official photos 26–29, modeled as relief cells.
for wing in [-50,50]:
 inward=1 if wing<0 else -1
 for off in [3.1,6.2,9.3]:
  for y in np.arange(-28,30,6.5):
   parts.append(roof_panel(wing+inward*off,float(y),2.4,5.8,lambda x,y,w=wing:49.1-abs(x-w)*5/12))
for side in [-1,1]:
 for xx in np.arange(14,46,5.5):
  for yy in [29.2,32.4,35.6]:parts.append(roof_panel(side*float(xx),yy,4.8,2.5,lambda x,y:48.9-(39-y)*4.8/12))
for xx in [-8.1,-2.7,2.7,8.1]:
 for yy in [27.3,31.8,36.3,40.8]:parts.append(roof_panel(xx,yy,4.6,3.8,lambda x,y:50.9+(y-25)*4.4/19))

# Floor belt lines, thickened for print visibility.
for z in [11,19,27,35]:
 for x in [-50,50]:parts.append(box(x,4,z,22.7,80,.8))
 parts.append(box(0,39,z,122,22.7,.8))
for z in [11,19,27]:
 for x in [-50,50]:parts.append(box(x,-42,z,22.7,24,.8))
# Vertical facade piers at the corners and major window bays.
for x in [-38.8,38.8]:
 for y in [-29,-17,-5,7,19]:parts.append(box(x,y,23,1,1.3,40))
for x in [-57,-37,-19,19,37,57]:parts.append(box(x,27.7,23,1.4,1,40))
# Courtyard terrace and walkway pattern seen in the aerial view.
parts += [box(0,-9,3.25,78,76,.7),box(0,-17,3.9,4.5,78,.8)]
for y in [-48,-37,-26,-15,-4,7,18]:parts.append(box(0,y,3.9,74,1.3,.8))
for x in [-36.5,36.5]:parts.append(box(x,-12,3.85,2,72,.7))
# Low front boundary walls in two curved segments.
for side in [-1,1]:
 for j in range(14):
  x=side*(7+j*2.05);y=-56.4+1.6*(abs(x)/36)**2
  parts.append(box(x,y,4.55,2.2,1.7,3.1))
# Raised back landing and broad shallow entrance steps.
parts.append(box(0,22,4.1,25,8,2.2))
for i in range(3):parts.append(box(0,15.5+i*1.4,3.8+i*.4,22,3,1.6+i*.8))
body=union(parts)
cut=[]
# Recessed paired windows along the inner and outer faces of main side wings.
for x in [-50,50]:
 for face in [x-11,x+11]:
  for y in [-27,-15,-3,9,21,33]:
   for z in [7.1,15.1,23.1,31.1,39.1]:
    for dy in [-2.5,2.5]:cut.append(box(face,y+dy,z,1.5,3.8,3.4))
# Back wing windows on courtyard and rear faces.
for face in [28,50]:
 for x in [-53,-41,-29,-17,17,29,41,53]:
  for z in [7.1,15.1,23.1,31.1,39.1]:
   for dx in [-2.5,2.5]:cut.append(box(x+dx,face,z,3.8,1.5,3.4))
# Central entry glazing, strong framing between recesses.
for z in [8,16,24,32,40,46]:
 for x in [-6.5,0,6.5]:cut.append(box(x,25.1,z,4.6,1.5,4.2 if z<46 else 2.5))
# Front-end facades with grouped openings.
for x in [-50,50]:
 for z in [8,16,24]:
  for dx in [-5,0,5]:cut.append(box(x+dx,-54,z,3.5,1.5,4.4))
 for face in [x-11,x+11]:
  for y in [-49,-39]:
   for z in [8,16,24]:cut.append(box(face,y,z,1.5,5.2,4.4))
# Narrow stair glazing panels, a recognizable part of the inner wing facades.
for x in [-38.8,38.8]:
 for z in [9,16,23,30,37]:cut.append(box(x,-22,z,1.8,2.2,5.8))
# Roof lantern horizontal slots, shallow enough to keep a closed core.
for x in [-51,51]:
 for y in [37.5,48.5]:cut.append(box(x,y,51.1,8,1.6,1.7))
 for xx in [x-5.5,x+5.5]:cut.append(box(xx,43,51.1,1.6,8,1.7))
body=body-union(cut)
assert str(body.status())=='Error.NoError'
r=body.to_mesh();mesh=trimesh.Trimesh(vertices=np.asarray(r.vert_properties)[:,:3],faces=np.asarray(r.tri_verts),process=True)
# Omit fully enclosed relief pockets hidden by adjoining volumes.
components=mesh.split()
positive=[c for c in components if c.volume>0]
assert len(positive)==1, "Disconnected positive-volume pieces require repair"
mesh=positive[0]
mesh.export(OUT/'model.stl')
print('Dimensions mm:',mesh.extents,'Triangles:',len(mesh.faces),'Watertight:',mesh.is_watertight)
