"""Original bounded UCH Library exterior. Five above-ground floors, two basements not exposed as extra storeys.
Floor plans and 2020/2024 photos control topology; all elevations are image-based trial estimates.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,Mesh64,OpType,CrossSection
R=Path(__file__).parent;S=150/52;ZH=.75;GL=2.;parts=[];cuts=[];frames=[];belts=[]
def pt(x,y,z):return (x*S,y*S,GL+z*S*ZH)
def box(x,y,z,w,d,h):return Manifold.cube((w*S,d*S,h*S*ZH)).translate(((x-w/2)*S,(y-d/2)*S,GL+z*S*ZH))
def prism(poly,z,h):
 n=len(poly);v=[pt(x,y,k)for k in [z,z+h]for x,y in poly];f=[]
 for j in range(1,n-1):f.extend([[0,j+1,j],[n,n+j,n+j+1]])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,n+j],[i,n+j,n+i]])
 m=Manifold(Mesh64(np.array(v),np.array(f,np.uint64)));assert str(m.status()).endswith('NoError');return m
parts.append(Manifold.cube((150,138.46153846,2)).translate((-75,-72.115384615,0)))
# North bar and changing lower southern infill, traced across 1F/2F/3F plans.
parts+=[box(0,5,0,40,10,12.0),box(0,-5,0,20,10,4.4),box(5,-4,4.4,10,8,3.6),box(.5,-5,8.0,31,10,4.0)]
# Third-floor balcony slab across the two recessed south corners; open volume beneath.
parts.append(box(0,0,8.0,40,20,.40))
# Fourth/fifth storey upper T body. Tall blank parapet/fifth-floor hall zone is retained.
parts.append(box(0,0,11.95,40,20,13.55))
parts.append(box(0,-15,11.45,20.5,10,12.817))
# West semi-ellipse exists through4F, but5F outline is straight.
a=np.linspace(np.pi/2,3*np.pi/2,49);west=[(-20+4.5*np.cos(t),5+5*np.sin(t))for t in a]
parts.append(prism(west,0,17.3))
# North arced service core is present in every1–5F plan; only its roof is slightly lower.
a=np.linspace(0,np.pi,65);north=[(12.5*np.cos(t),10+5*np.sin(t))for t in a]
parts.append(prism(north,0,24.0))
# Two continuous external stair cores; solid ends with shallow glazed strips.
for x in [-12.4,12.4]:parts.append(box(x,-11.5,0,6.2,3,28.4))
# Front south bridge wing supports and corner columns ground the large voids.
for x in [-9.65,9.65]:parts.append(box(x,-19.45,0,1.2,1.1,11.5))
for x in [-19.45,19.45]:parts.append(box(x,-9.45,0,1.1,1.1,12.05))
# West entrance raised platform, broad approach steps and a low glazed canopy.
parts.append(box(-17.1,-6.1,0,13.6,9.6,1.2))
for i in range(6):parts.append(box(-22.6-i*.43,-6.1,0,.65,9.2,.2*(6-i)))
parts.append(box(-17.5,-6.1,4.1,13.6,9.8,.45))
for x in [-23.5,-20,-16,-11.5]:
 for y in [-10.6,-1.6]:parts.append(box(x,y,1.1,.48,.48,3.1))
# Rooted lower glazing behind the entrance canopy.
for y in [-8,-5,-2]:
 cuts.append(box(-9.98,y,1.7,.55,2.25,2.1))
# One tall grouped opening with a central horizontal frame: source has two glass rows, not four.
for side in [-1,1]:
 for y,w in ([(-5.4,6.6),(4.0,7.6)] if side<0 else [(-5.4,6.6),(2.2,3.4),(7,3.4)]):
  z=14.8;h=4.4
  if side<0 and y>0:z=17.35;h=1.85 #4F rounded bay occludes the lower part; no hidden cavity.
  cuts.append(box(side*19.98,y,z,.32,w,h))
  for dy in np.linspace(-w/2,w/2,max(2,int(w/1.2)-1)+2)[1:-1]:frames.append(box(side*19.87,y+dy,z,.35,.30,h))
  if h>3:frames.append(box(side*19.87,y,16.8,.33,w,.40))
# Photographed west-main-window short southern return, not the unknown south-wing end.
cuts.append(box(-17.75,-9.98,14.8,3.4,.32,4.4))
for x in [-18.32,-17.18]:frames.append(box(x,-9.87,14.8,.30,.35,4.4))
frames.append(box(-17.75,-9.87,16.8,3.4,.33,.40))
# Two visible west high-wall circular windows; backed shallow recesses, approximate diameter.
for y,z in [(-5.4,22.4),(7.0,20.8)]:
 cuts.append(Manifold.cylinder(.6*S,.45*S,.45*S,48).rotate((0,90,0)).translate(pt(-20.3,y,z)))
# East north half3F visible two grouped windows, below the high window bands.
for y in [2.2,7.0]:
 cuts.append(box(19.98,y,8.7,.62,3.4,2.0))
 for dy in [-1.0,0,1.0]:frames.append(box(19.74,y+dy,8.7,.55,.35,2.0))
# South upper wing visible window rows on both east/west sides and its front.
for z in [13.9,18.4]:
 for side in [-1,1]:
  cuts.append(box(side*10.23,-15.1,z,.60,6.5,1.7))
  for y in np.linspace(-17.7,-12.5,6):frames.append(box(side*10.0,y,z,.55,.35,1.7))
 # South-facing end is not independently photographed; leave conservative wall.
# Recessed3F balconies have back glazing; leave open air in front rather than solid infill.
for side,x in [(-1,-14.98),(1,15.98)]:
 cuts.append(box(x,-5.0,8.7,.6,7.6,2.25))
 for y in np.linspace(-8.2,-1.8,7):frames.append(box(x-side*.23,y,8.7,.55,.35,2.25))
# Glazed stair strips retain broad solid jambs and backed reveals.
for x in [-12.4,12.4]:
 for z,h in [(1.4,3.2),(5.8,3.1),(10.0,3.1),(14.2,2.6),(17.7,3.2),(23.2,4.3)]:
  cuts.append(box(x,-12.98,z,2.3,.32,h));frames.append(box(x,-12.87,z+h*.52,2.3,.33,.40))
  side=-1 if x<0 else 1
  cuts.append(box(x+side*3.08,-11.45,z,.32,1.7,h));frames.append(box(x+side*2.98,-11.45,z+h*.52,.33,1.7,.40))
# Radial sectors provide clean shallow curved glazing; avoid overlapping tangent cutters and thin wedges.
def curved_band(t0,t1,outer,inner,z,h):
 ts=np.linspace(t0,t1,max(3,int((t1-t0)/.035)+2));poly=[((-20+outer[0]*np.cos(t))*S,(5+outer[1]*np.sin(t))*S)for t in ts]+[((-20+inner[0]*np.cos(t))*S,(5+inner[1]*np.sin(t))*S)for t in ts[::-1]]
 from shapely.geometry import Polygon
 assert Polygon(poly).is_valid and Polygon(poly).area>0
 return CrossSection([np.array(poly)]).extrude(h*S*ZH).translate((0,0,GL+z*S*ZH))
for z,h in [(2,2.2),(6,2.2),(10.3,2.2)]:
 for t in np.linspace(np.pi/2+.22,3*np.pi/2-.22,7):cuts.append(curved_band(t-.135,t+.135,(4.65,5.15),(4.32,4.82),z,h))
cuts.append(curved_band(np.pi/2+.08,3*np.pi/2-.08,(4.65,5.15),(4.32,4.82),14.2,2.3))
for t in np.linspace(np.pi/2+.18,3*np.pi/2-.18,14):frames.append(curved_band(t-.032,t+.032,(4.47,4.97),(4.20,4.70),14.2,2.3))
# Horizontal facade belts and low rooftop equipment; no guessed north window grid.
for z in [4.1,7.8,11.8]:belts.append(box(0,5,z,40.3,10.3,.38))
for z in [11.3,23.9]:belts.append(box(0,-15,z,20.8,10.3,.38))
for x in [-12.4,12.4]:
 for z in [4.1,7.8,11.8,17.1,21.5]:belts.append(box(x,-11.5,z,6.5,3.3,.38))
parts.append(box(-12,5,25.4,9,5,1.1));parts.append(box(-5,6,25.4,3.5,3,1.7))
solid=Manifold.batch_boolean(parts,OpType.Add)
for c in cuts:solid=solid-c
for f in frames:solid=solid+f
for belt in belts:solid=solid+belt # Preserve structural belts; window cuts cannot leave thin exterior lips.
assert len(solid.decompose())==1,[(o.volume(),o.bounding_box())for o in solid.decompose()]
a=solid.to_mesh64();m=trimesh.Trimesh(np.asarray(a.vert_properties,dtype=np.float32)[:,:3],np.asarray(a.tri_verts),process=False);m.export(R/'model.stl');print(m.extents,m.volume,m.is_watertight)
