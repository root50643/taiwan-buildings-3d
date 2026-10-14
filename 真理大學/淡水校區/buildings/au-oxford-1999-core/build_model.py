"""Aletheia University Oxford College: 1999 surveyed historic core only.
Original approximate geometry in millimetres; later courtyard/rear additions excluded.
Run in Python with requirements.txt. Public survey drawings support shape, not precise survey scale.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[]; cuts=[]; details=[]
# Coordinate convention: original front at -Y, rear at +Y; left/right viewed from front.
# Overall walls 142 x 116 mm; front portico 14.8 mm deep, hall 42.5 mm deep.
P={'base_width':150.,'base_depth':130.,'base_height':3.,'wing_width':43.,'wing_length':116.,'wing_center':49.5,'wing_eave':24.,'wing_ridge':42.,'hall_width':56.,'hall_front':-43.2,'hall_rear':-.7,'hall_eave':36.,'hall_ridge':51.5,'portico_beam_bottom':28.7,'portico_slab_top':31.6}
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def profile(poly,y,depth):return CrossSection([poly]).extrude(depth).rotate((90,0,0)).translate((0,y+depth/2,0))
def arch(x,y,z,w,h,depth):
 r=w/2;spring=z+h-r
 pts=[(x-r,z),(x+r,z),(x+r,spring)]
 pts.extend((x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,21)[1:])
 return profile(pts,y,depth)
def window(x,y,z,w,h,axis='front',door=False):
 # Recessed openings remain backed by the exterior solid. Fine fanlights/muntins are omitted.
 a=arch(0,0,z,w,h,2.2)
 ring=arch(0,0,z-.2,w+1.5,h+.95,1.7)-arch(0,0,z-.4,w,h+.2,3.)
 mull=box(0,0,z-.15,1.05,2.9,h-w/2+.15) if not door else box(0,0,z-.15,1.05,2.9,h-w/2+.15)
 horizontal=box(0,0,z+h-w/2-.5,w+.4,2.9,1.0)
 sill=box(0,0,z-.9,w+1.2,1.7,1.1)
 if axis=='side':
  a=a.rotate((0,0,90));ring=ring.rotate((0,0,90));mull=mull.rotate((0,0,90));horizontal=horizontal.rotate((0,0,90));sill=sill.rotate((0,0,90))
 cuts.append(a.translate((x,y,0)))
 # relief applied after carving; all faces overlap the backed facade by at least .3 mm.
 details.extend(p.translate((x,y,0)) for p in [ring,mull,horizontal])
 if not door:details.append(sill.translate((x,y,0)))
def finial(x,y,z,h=8.4,w=2.25):
 # Truncated apex minimum 1.15 mm replaces source needle-fine points for printing.
 add(x,y,z-.4,w,w,2.2);add(x,y,z+1.5,w+.6,w+.6,.9)
 add(x,y,z+2.1,w*.86,w*.86,2.0);add(x,y,z+3.7,w+.2,w+.2,.8)
 parts.append(CrossSection.square((w*.78,w*.78),center=True).extrude(h-4.25,scale_top=(1.15/(w*.78),1.15/(w*.78))).translate((x,y,z+4.2)))
def gable_along_y(x,y,z,w,d,h):
 # A 1.2 mm wide flat ridge retains every original polygon during .8 mm opening.
 parts.append(profile([(x-w/2,z),(x+w/2,z),(x+.6,z+h),(x-.6,z+h)],y,d))
def step(x,y,w):
 for i in range(3):add(x,y+i*.85,2.9,w,1.05,.85*(i+1))
# Rectangular print base plus independent raised historic floor platform.
add(0,0,0,150,130,3)
for x in [-49.5,49.5]:
 add(x,0,2.8,43.4,116.4,2.7);add(x,0,5.3,43,116,18.7)
 add(x,0,23.1,44.8,117.2,1.3)
 gable_along_y(x,0,24,44.8,117.2,18)
 # Roof ridge and gable edge bands.
 add(x,0,41.5,1.8,117.6,1.1)
 for yy in [-58.1,58.1]:
  for sign in [-1,1]:
   lo,hi=sorted([x,x+sign*22.4]);z=lambda q:42-abs(q-x)*18/22.4
   parts.append(profile([(lo,z(lo)-.7),(hi,z(hi)-.7),(hi,z(hi)+.65),(lo,z(lo)+.65)],yy,1.7))
  finial(x,yy,42.1)
 # Front one central arch door flanked by two arch windows; rear only two windows.
 window(x,-58,5.3,7.0,18.6,door=True)
 for xx in [x-11.4,x+11.4]:window(xx,-58,10.2,5.7,10.6)
 for xx in [x-11.4,x+11.4]:window(xx,58,10.2,5.7,10.6)
 step(x,-61.1,10)
# Seven main arch windows on each outer long facade, positioned from drawings 6/7.
# Their uneven central spacing is retained rather than replacing with a generic array.
for xx,ys in [(-71,[-47.1,-30.8,-15.0,1.3,12.7,31.1,47.8]),(71,[-48.1,-31.8,-15.0,-.2,12.3,31.3,47.6])]:
 for yy in ys:window(xx,yy,10.2,5.7,10.6,axis='side')
# Inner sides: one arch door near the hall and two windows toward rear (figs 3,8,9).
for xx in [-28,28]:
 window(xx,8.4,5.3,6.8,15.9,axis='side',door=True)
 for yy in [26.4,44.2]:window(xx,yy,10.2,5.7,10.6,axis='side')
# Transverse front hall. Roof is deliberately higher than both long wing ridges.
hf,hr=P['hall_front'],P['hall_rear'];hy=(hf+hr)/2
add(0,hy,3,56,hr-hf,2.5);add(0,hy,5.3,56,hr-hf,30.7)
# Roof ridge follows X, transverse to wings, with slightly extended gable ends.
roof=profile([(-22.25,36),(22.25,36),(.6,51.5),(-.6,51.5)],0,59.2).rotate((0,0,90)).translate((0,hy,0));parts.append(roof)
add(0,hy,51.0,59.4,1.8,1.1)
# Hall eave/coping around its front/back.
for yy in [hf-.4,hr+.4]:add(0,yy,35.0,59.4,2.0,1.4)
for xx in [-29,29]:finial(xx,hy,51.5,h=7.6,w=2.4)
# Hall front wall set behind the open column bays, per fig.12.
window(0,hf,5.3,7.2,20.4,door=True)
for xx in [-15.2,15.2]:window(xx,hf,10.2,5.7,10.6)
# Hall rear courtyard openings: positions from plan; square-headed detail simplified.
# No invented rich arched trim on this incompletely documented elevation.
cuts.append(box(-13.5,hr,10.2,6.2,2.2,10.3));cuts.append(box(14,hr,5.3,6.7,2.2,16))
details.append(box(-13.5,hr,10.05,1.05,2.9,10.6));details.append(box(14,hr,5.15,1.05,2.9,16.3))
# Actual four front piers = three open bays, and a lower horizontal terrace roof.
add(0,-50.6,3,56,15,2.5)
for xx in [-27.0,-9.1,9.1,27.0]:
 add(xx,-57.5,5.2,2.5,2.5,24.2)
 add(xx,-57.5,26.6,3.7,3.6,2.4)
 add(xx,-57.5,5.2,3.1,3.1,1.0)
add(0,-50.6,28.7,58,16.8,2.9)
add(0,-57.8,30.7,59.5,2.5,1.0)
# Front/side parapets; lattice pattern represented by shallow backed diamond relief.
add(0,-57.6,31.4,57,1.5,3.6)
for xx in [-27.5,27.5]:add(xx,-50.4,31.4,1.5,14.5,3.6)
for xx in [-27.5,-9.1,9.1,27.5]:add(xx,-57.6,31.3,2.0,2.1,4.4)
for xx in np.arange(-24.5,26.,2.6):
 diamond=profile([(xx-1,33),(xx,31.9),(xx+1,33),(xx,34.1)],-58.3,.6)
 cuts.append(diamond)
step(0,-61.1,12)
# Three front hall roof triangular vents; individual solid-backed hoods.
def front_dormer(x):
 # True gabled hood: front triangle, horizontal ridge into the parent slope.
 # No rectangular back/body block protrudes above the sloping roof.
 parts.append(profile([(x-4.25,41.5),(x+4.25,41.5),(x+.65,45.6),(x-.65,45.6)],-32.6,6.2))
for xx in [-17.3,0,17.3]:front_dormer(xx)
# Each wing has one outer vent near rear and one inner vent near hall junction.
# Roof plan fig.1 locates these separately; no extra symmetric front/rear row.
for side in [-1,1]:
 x=side*49.5
 for facing,yy in [(side,30),(-side,3.0)]:
  # Gabled hood ridge returns upslope until it is swallowed by the parent roof.
  # The source triangular facade is retained; block-shaped rear supports omitted.
  xo=x+facing*11.5;xi=x+facing*6.0
  verts=[(q,yy-4.5,31.8) for q in [xo,xi]]+[(q,yy+4.5,31.8) for q in [xo,xi]]
  verts += [(xo,yy+dy,35.6) for dy in [-.65,.65]]
  verts += [(xi,yy+dy,37.3) for dy in [-.65,.65]]
  parts.append(Manifold.hull_points(verts))
# Central slender belfry/spire, thickened and truncated for print integrity.
add(0,hy,50.5,3.9,3.9,5.0)
# Small belfry face is a shallow arched recess, not a free 0.3mm wall.
cuts.append(arch(0,hy-1.8,52.0,1.5,2.4,1.1))
parts.append(CrossSection.square((4.9,4.9),center=True).extrude(7.8,scale_top=(1.2/4.9,1.2/4.9)).translate((0,hy,55.1)))
add(0,hy,62.8,1.2,1.2,3.3);add(0,hy,63.8,4.4,1.2,1.2)
solid=Manifold.batch_boolean(parts, __import__('manifold3d').OpType.Add)
solid=solid-Manifold.batch_boolean(cuts, __import__('manifold3d').OpType.Add)
solid=solid+Manifold.batch_boolean(details, __import__('manifold3d').OpType.Add)
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.000005).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(OUT/'model.stl')
print('dimensions_mm',mesh.extents.tolist(),'triangles',len(mesh.faces),'volume_mm3',mesh.volume)
