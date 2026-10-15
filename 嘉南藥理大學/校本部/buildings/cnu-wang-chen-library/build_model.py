"""Original bounded CNU Wang Chen library exterior; mm output.
Layered terraces, low south arc, taller north open screen and closed curved glazing.
Nominal 46m height is a photo-fit candidate, not measured or official.
"""
from pathlib import Path
import numpy as np,math,trimesh,json,hashlib
from manifold3d import Manifold,CrossSection
R=Path(__file__).resolve().parent;S=1.8;BASE=3.;parts=[];cuts=[];details=[]
def box(x1,x2,y1,y2,z1,z2):return Manifold.cube(((x2-x1)*S,(y2-y1)*S,(z2-z1)*S)).translate((x1*S,y1*S,BASE+z1*S))
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def detail(*a):details.append(box(*a))
def ellipse(rx,ry,z,h):
 p=np.array([[rx*math.cos(t),ry*math.sin(t)] for t in np.linspace(0,2*math.pi,161)[:-1]])*S
 return CrossSection([p]).extrude(h*S).translate((0,0,BASE+z*S))
def body_outline(z,h,extra=0):
 lower=ellipse(26.7+extra,28.7+extra,z,h)^box(-35,35,-35,15,z-.01,z+h+.01)
 cap=ellipse(21.2+extra,21.2+extra,z,h).translate((-2.5*S,8*S,0))^box(-35,35,14.99,35,z-.01,z+h+.01)
 return lower+cap
def sector(rx,ry,ix,iy,a,b,z,h):
 t=np.linspace(math.radians(a),math.radians(b),max(5,int(abs(b-a)*1.3)))
 p=[[rx*math.cos(v),ry*math.sin(v)] for v in t]+[[ix*math.cos(v),iy*math.sin(v)] for v in t[::-1]]
 return CrossSection([np.array(p)*S]).extrude(h*S).translate((0,0,BASE+z*S))
def beam(p1,p2,r):
 # Convex hull of two finite square cross-sections, rooted at both endpoints.
 v=[]
 for p in [p1,p2]:
  for dx in [-r,r]:
   for dy in [-r,r]:
    for dz in [-r,r]:v.append([(p[0]+dx)*S,(p[1]+dy)*S,BASE+(p[2]+dz)*S])
 return Manifold.hull_points(np.array(v))
parts.append(Manifold.cube((150,150,BASE)).translate((-75,-83,0)))
# Three full lower levels, then independently recessed indoor floor envelopes.
parts.append(body_outline(-.02,14.05))
for z,h,south,north in [(14,4.4,-23.0,24.0),(18.4,4.4,-19.0,22.0),(22.8,4.4,-8.0,20.0),(27.2,4.4,-7.0,12.0),(31.6,4.4,-4.0,12.0),(36,4.4,-2.0,12.0)]:
 solid=body_outline(z,h)^box(-27,22.5,south,north,z-.01,z+h+.01)
 if abs(z-18.4)<.01:solid=solid-box(14,28,-24,-9,18.39,22.81)
 parts.append(solid)
 # A defined slab/terrace at each transition; never extend all as enclosed rooms.
 parts.append((body_outline(z,.65,.2)^box(-27.2,23,south-1,north+1,z-.01,z+.7)))
# Fifth level southeast notch and differing 4F/5F terrace limits.
# Southeast notch is subtracted from the indoor F5 volume only, not its screen.
# High east-west main roof, south white wall extends farther than machinery roof.
add(-22.5,22.5,-2.0,15.0,39.8,40.7)
add(-24.0,30.2,-2.9,-1.7,40.0,44.4)
add(-24.0,-22.5,-2.8,13,25,44.4)
add(25.5,30.2,-2.8,12.5,10,44.4)
add(21.8,25.5,-4.5,8.8,0,40.0)
add(24.5,30.0,8.0,15.5,0,43.0)
# West stair core and east projections differ in height and depth.
west_core=box(-28.2,-23.2,-6,12,-.01,41.8)
add(-28.5,-23.0,-6.3,12.3,41.7,42.4)
add(25.0,32.0,-1,6,0,27.5)
add(27.5,34.0,2.0,7.0,0,23.4)
# Rooftop plant / raised service unit, height not antenna.
add(12,19,6,13,40.5,45.4)
add(11.6,19.4,5.6,13.4,45.3,46.0)
# Curved sealed south glass volume tapers and retreats across levels6–9.
pts=[]
for z,rx,ry,cy in [(22.4,11.8,12.0,-7.0),(40.0,10.5,10.0,-2.0)]:
 for t in np.linspace(math.pi,2*math.pi,65):pts.append([rx*math.cos(t)*S,(cy+ry*math.sin(t))*S,BASE+z*S])
glass=Manifold.hull_points(np.array(pts));glass_cuts=[]
# Fine shallow grid engravings backed by the closed curved glass volume.
for t in np.linspace(math.pi+.08,2*math.pi-.08,15):
 # Radially outward-opening groove: do not leave an undercut square-beam lip.
 notch=[]
 for z,rx,ry,cy in [(22.35,11.8,12.0,-7.0),(40.05,10.5,10.0,-2.0)]:
  for angle in [t-.012,t+.012]:
   for depth in [-.12,2.0]:
    notch.append([(rx+depth)*math.cos(angle)*S,(cy+(ry+depth)*math.sin(angle))*S,BASE+z*S])
 glass_cuts.append(Manifold.hull_points(np.array(notch)))
for z in [23,25.8,28.6,31.4,34.2,37.0,39.2]:
 f=(z-22.4)/17.6;rx=11.8-1.3*f;ry=12-2*f;cy=-7+5*f
 ring=sector(rx+2.0,ry+2.0,rx-.12,ry-.12,180,360,z,.16).translate((0,cy*S,0));glass_cuts.append(ring)
for c in glass_cuts:glass=glass-c
parts.append(glass)
# Distinct outer arc screens: south top24m; north top32.8m, two upper open rows.
parts.append(sector(27.2,29.2,26.2,28.2,180,360,0,24.0))

# North high screen follows the traced north cap, not the lower side-axis arc.
# Same-image fit: circle-like cap centered(-2.5,8), radius21.5, ends near y15.
parts.append(sector(21.5,21.5,20.5,20.5,20,160,0,32.8).translate((-2.5*S,8*S,0)))
for half,levels in [(180,[1.3,6.1,10.5,14.9,19.3])]:
 for z in levels:
  for k in range(9):
   a=half+3+k*20;b=half+17+k*20
   # Radial cut through screen and shallow into lower indoor body. Upper north
   # rows are genuinely clear because the indoor body has already retreated.
   cuts.append(sector(27.6,29.6,25.8,27.8,a,b,z,2.65))
for z in [1.3,6.1,10.5,14.9,19.3,23.7,28.1]:
 for k in range(7):cuts.append(sector(21.9,21.9,20.1,20.1,23+k*20,37+k*20,z,2.65).translate((-2.5*S,8*S,0)))
# Upper north transverse grid connects the arc to recessed rear wall.
for z in [27.2,31.6]:
 for x in [-19,-10,-1,8,16]:
  y=8+math.sqrt(21.3**2-(x+2.5)**2);add(x-.45,x+.45,11.6,y+.2,z,z+.8)
for y in [18,22,26]:
 dx=math.sqrt(21.3**2-(y-8)**2);add(-2.5-dx-.15,-2.5+dx+.15,y-.4,y+.4,31.6,32.4)
# South terrace top grille, narrow slats over open setback rather than solid roof.
for x in [-18,-9,0,9,18]:
 y=-29.0*math.sqrt(1-(x/27.0)**2);add(x-.4,x+.4,y-.1,-18.6,22.8,23.6)
for y in [-21,-24,-27]:
 dx=27.0*math.sqrt(1-(y/29.0)**2);add(-dx-.15,dx+.15,y-.4,y+.4,22.8,23.6)
# Photo-backed glazing in the lower north five rows and south low arc.
# North highest two rows remain genuinely open; south fifth-row outer ends
# retain their open terrace sightlines. Recessed panes join the screen piers.
for half in [180]:
 for k in range(9):
  a=half+3+k*20;b=half+17+k*20
  for z in [1.3,6.1,10.5,14.9,19.3]:
   if half==180 and z>19 and k in [0,8]:continue
   details.append(sector(26.7,28.7,25.7,27.7,a-2,b+2,z+.03,2.59))
   for deg in [a+3.5,(a+b)/2,b-3.5]:
    t=math.radians(deg);x,y=26.70*math.cos(t),28.70*math.sin(t)
    details.append(beam((x,y,z+.15),(x,y,z+2.50),.075))
   details.append(sector(26.78,28.78,26.50,28.50,a-1,b+1,z+1.97,.14))
# North lower glazing follows the independently fitted north cap, not the
# southern low ellipse. The top two rows are excluded from backing panes.
for k in range(7):
 a=23+k*20;b=37+k*20
 for z in [1.3,6.1,10.5,14.9,19.3]:
  details.append(sector(21.0,21.0,20.0,20.0,a-2,b+2,z+.03,2.59).translate((-2.5*S,8*S,0)))
  for deg in [a+3.5,(a+b)/2,b-3.5]:
   t=math.radians(deg);x,y=-2.5+21.00*math.cos(t),8+21.00*math.sin(t)
   details.append(beam((x,y,z+.15),(x,y,z+2.50),.075))
  details.append(sector(21.08,21.08,20.80,20.80,a-1,b+1,z+1.97,.14).translate((-2.5*S,8*S,0)))
# West / east side glazing strips, interrupted by substantial floor beams.
for z in [1.2,6.1,10.5,14.9,19.3,23.7,28.1,32.5,36.9]:
 west_core=west_core-box(-28.4,-27.6,-4.4,10.5,z,z+2.8)
 if z>14:cut(22.6,24.8,-4.8,-3.8,z,z+2.8)
for z,fy in [(23.8,-8),(28.2,-7),(32.6,-4),(37.0,-2)]:
 for x in [-19.6,-15.9,-12.2]:
  cut(x-1.2,x+1.2,fy-.3,fy+.8,z,z+2.6)
  # Grouped paired windows with shallow back-rooted frames and upper transom.
  detail(x-.07,x+.07,fy+.67,fy+.85,z+.04,z+2.56)
  detail(x-1.17,x+1.17,fy+.67,fy+.85,z+1.9,z+2.04)
# North recessed red wall, visible behind rather than filling screen's top rows.
for z,by in [(23.7,20),(28.1,12),(32.5,12),(36.9,12)]:
 for x in [-17,-10,-3,4,11,18]:cut(x-2.0,x+2.0,by-.5,by+.3,z,z+2.7)
# Clerestory slots in the tall south white wall, distinct from machine roof.
for x in [-20,-10,0,10,20,27]:cut(x-.43,x+.43,-3.1,-2.35,41.5,42.8)
# East stair facade visible from north: stacked deep rectangular recesses.
for z in [1.3,6.1,10.5,14.9,19.3,23.7,28.1,32.5,36.9,40.5]:
 cut(25.1,29.35,14.6,15.8,z,min(z+2.8,42.65))
details.append(west_core)
for x in [23.2,24.2]:detail(x-.25,x+.25,-4.10,-3.7,1.1,39.8)
for z,by in [(23.7,20),(28.1,12),(32.5,12),(36.9,12)]:
 for x in [-17,-10,-3,4,11,18]:
  if z==23.7 and x==18:continue
  for dx in [-.65,.65]:detail(x+dx-.23,x+dx+.23,by-.65,by-.2,z,z+2.7)
# Entry cut and separate deep rectangular portico / canopy, large front steps.
# Frontmost entry jambs follow an outward radial bevel, removing the broad
# acute intersection with the arc while retaining the full recessed back wall.
entry_poly=np.array([[-15.12,-31.5],[15.12,-31.5],[12,-25],[12,-23.8],[-12,-23.8],[-12,-25]])*S
entry_void=CrossSection([entry_poly]).extrude(5.8*S).translate((0,0,BASE+.9*S))
cuts.append(entry_void)
# Screen panes cannot refill the actual ground-level entrance recess.
details=[p-entry_void for p in details]
add(-13,13,-35.5,-34.4,7.1,8.0)
# Glass canopy slopes upward toward the building; nominal bounds from aerial.
hood=[]
for x in [-12.6,12.6]:
 for y,z in [(-35.3,7.7),(-29.0,9.8)]:
  for dz in [0,.6]:hood.append([x*S,y*S,BASE+(z+dz)*S])
parts.append(Manifold.hull_points(np.array(hood)))
for x in [-12.3,12.3]:add(x-.65,x+.65,-35.2,-33.5,0,7.3)
for x in [-10,-5,0,5,10]:detail(x-.24,x+.24,-24.2,-23.6,1.0,6.5)
for i in range(8):add(-12.5,12.5,-43+i*.75,-29,-.02,.16*(i+1))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
m=solid.simplify(.00005).to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties,dtype=np.float32)[:,:3],np.array(m.tri_verts),process=False);mesh.export(R/'model.stl')
print(json.dumps({'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()}))
