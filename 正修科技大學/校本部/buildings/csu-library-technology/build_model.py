"""Original bounded CSU three-wing library/technology building. Draft for source review, not surveyed."""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,Mesh64,OpType,CrossSection
R=Path(__file__).parent;parts=[];cuts=[];frames=[];GL=1.5
# Local x: clock wing to mural cylinder; local +y: back. Rotate150deg to approximate geographic north.
def tx(x):return x*.86 if abs(x)<=25 else x-np.sign(x)*3.5
def box(x,y,z,w,d,h):
 lo=tx(x-w/2);hi=tx(x+w/2)
 return Manifold.cube((hi-lo,d,h)).translate((lo,y-d/2,z+GL))
def cyl(x,y,z,r,h):return prism([(x+r*np.cos(t),y+r*np.sin(t))for t in np.linspace(0,2*np.pi,65)[:-1]],z,h)
def prism(poly,z,h):return CrossSection([np.array([(tx(x),y)for x,y in poly],float)]).extrude(h).translate((0,0,z+GL))
def section_roof(xs,zs,y0,y1,thick,bottom=None,axis="x"):
 # Closed thick curved board with finite end and side thickness.
 n=len(xs);v=[]
 for y in [y0,y1]:
  for dz in [0,-thick]:
   for x,z in zip(xs,zs):
    xx,yy=(x,y)if axis=='x' else(y,x)
    v.append((tx(xx),yy,(bottom if bottom is not None and dz!=0 else z+dz)+GL))
 f=[]
 for i in range(n-1):
  f.extend([(i,i+1,2*n+i+1),(i,2*n+i+1,2*n+i),(n+i,3*n+i+1,n+i+1),(n+i,3*n+i,3*n+i+1),(i,n+i+1,i+1),(i,n+i,n+i+1),(2*n+i,2*n+i+1,3*n+i+1),(2*n+i,3*n+i+1,3*n+i)])
 f.extend([(0,2*n,n*3),(0,n*3,n),(n-1,2*n-1,4*n-1),(n-1,4*n-1,3*n-1)])
 if axis=="y":f=[(a,c,b)for a,b,c in f]
 m=Manifold(Mesh64(np.array(v),np.array(f,np.uint64)));assert str(m.status()).endswith('NoError'),m.status();return m
parts.append(box(0,7.5,-GL,100,87,GL))
# Three full-height connected wings, never just the library's3storeys.
parts += [box(0,9,0,48,18,36.5),box(-32,0,0,16.15,36,36.5),box(33,20,0,18.15,44,37.5)]
# Curved glazing under main long barrel and short wave roof.
xs=np.linspace(-25,25,61);zs=39+4.8*np.sin(np.linspace(0,np.pi,61))
parts.append(section_roof(xs,zs,-.6,18.6,1.0))

# Main roof lower glass-filled volume under the roof: closed profile extruded across depth.
poly=[(-25,35.8)]+list(zip(xs,zs-0.9))+[(25,35.8)]
# Build solid custom profile using planar crosssection x/z then rotate90deg into y depth.
parts.append(section_roof(xs,zs-.9,-.1,18.1,1,bottom=35.8))
xs2=np.linspace(-18,18,41);zs2=39.6+2.2*np.sin(np.linspace(0,np.pi,41))
parts.append(section_roof(xs2,zs2,-40.5,-23.5,1.0,axis="y"))
poly=[(-40,35.8)]+list(zip(xs2,zs2-.9))+[(-24,35.8)]
parts.append(section_roof(xs2,zs2-.9,-40.1,-23.9,1,bottom=35.8,axis="y"))
# Clock end narrow crowned blade, shallow circular clock.
parts.append(box(-32,-18,0,17,3,39.3));yy=np.linspace(-19.5,-16.5,25);zz=np.minimum(39.3+1.5*np.sin(np.linspace(0,np.pi,25)),40.6);parts.append(section_roof(yy,zz,-40.5,-23.5,1.35,axis="y"))
clock=Manifold.cylinder(.7,.8,.8,48).rotate((0,90,0)).translate((tx(-23.7),-18,38.4+GL));cuts.append(clock)
# Mural cylinder front: open top with shallow retained bottom, no hemisphere.
t=np.linspace(np.pi,2*np.pi,65)
outer=[(39+5.5*np.cos(a),-1+6.5*np.sin(a))for a in t]+[(44.5,2),(33.5,2)]
inner=[(39+4.2*np.cos(a),-1+5.2*np.sin(a))for a in t]+[(43.2,.7),(34.8,.7)]
parts.append(prism(outer,0,41.0));cuts.append(prism(inner,38.5,4))
# Rear curved/chamfered projection visible in both complete roof sources; uncertain wall detail.
a=np.linspace(0,np.pi,33);poly=[(9+11*np.cos(t),18+9*np.sin(t))for t in a];parts.append(prism(poly,0,33.0))
# Back service towers and low equipment, separate from neighbouring green-roof buildings.
parts += [box(-27,22,0,10,8,42),box(34,43,0,10,7,41),box(-36,21,37,7,6,3),box(37,35,37.4,6,7,2)]
# Low internal-L reading area: solid below, stepped open terrace and arc glazing behind.
a=np.linspace(-np.pi/2,0,49);poly=[(-24,0)]+[(-24+18*np.cos(t),18*np.sin(t))for t in a];parts.append(prism(poly,0,9.5))
poly2=[(-24,0)]+[(-24+12*np.cos(t),12*np.sin(t))for t in a];parts.append(prism(poly2,0,16.8))
parts.append(cyl(9,-2.1,0,3.7,11));parts.append(box(-12,-14.7,3,8,7,1))
for x in [-15,-9]:parts.append(box(x,-17,0,1.2,1.2,3.2))
# Known front window groupings only; shallow backing is retained.
for z in [4.0,7.5,11.0,14.5,18.0,21.5,25.0,28.5]:
 for x in [-19,-11,-3,5,13,21]:
  if not (x<0 and z<16.8):cuts.append(box(x,-.03,z,5.5,.5,1.7))
 for y in [-13,-6]:
  if z>17:cuts.append(box(-23.98,y,z,.5,4.5,1.7))
# Clock blade faces the inner court at the end of the short wing.
for z in [3.8,7.2,10.6,14,17.4,20.8,24.2,27.6,31.0]:
 cuts.append(box(-23.48,-18.55,z,.6,.55,2.2))
for y in np.arange(-13,0,4.8):
 top=39.6+2.2*np.sin((y+18)/36*np.pi)-1.4
 cuts.append(box(-23.93,y,34.5,.5,3.9,top-34.5))
# Main top continuous glass with sparse mullions, no deep perforation.
for x in np.arange(-22.5,24,4.5):
 top=min(39+4.8*np.sin((xx+25)/50*np.pi) for xx in [x-1.825,x+1.825])-1.8
 if x>20:top=min(top,36.6) # Keep 0.9m solid below adjoining flat-wing roof.
 cuts.append(box(x,-.03,33.7,3.65,.4,top-33.7))
# The retained original backing between broad glazed recesses forms mullions; no thin isolated overlay posts.
# Cylinder-adjacent outer flat wing: source2024 broad grouped window bands.
for z in [4,7.5,11,14.5,18,21.5,25,28.5,32]:
 cuts.append(box(42.02,23,z,.65,32,1.7))
 for y in np.arange(8,40,4):frames.append(box(41.83,y,z,.8,.75,1.7))
# Source-visible vertical piers separate grouped windows, rather than uniform small-hole rows.
for y in [-15.5,-9.5,-3.5]:frames.append(box(-23.8,y,0,.8,.9,33))
for x in [-22.7,-15,-7,1,9,17]:frames.append(box(x,-.15,0,.8,.8,33))
# Source-visible short-end flare accommodates the large frame beside the narrower D head.
parts.append(box(27.2,-.8,0,12.6,3.4,37.5))
for z,h in [(3.2,8.2),(18.5,6.5)]:
 cuts.append(box(27.2,-2.53,z,10,.7,h))
 for x in [27.2]:frames.append(box(x,-2.3,z,.80,.5,h))
 frames.append(box(27.2,-2.3,z+h*.5,10,.5,.70))
cuts.append(box(27.2,-2.65,12.8,9.8,1.5,4.5))
cuts.append(box(27.2,-2.53,28.0,10,.7,7.0))
for z in [28.3,30.0,31.7,33.4]:frames.append(box(27.2,-2.2875,z,10,1.975,.75))
for x in [21.2,33.2]:frames.append(box(x,-2.8,0,1.5,1.9,37.7))
frames.append(box(27.2,-2.8,36.6,13.5,1.9,1.2))
# Photographed outer short end of the clock wing: only the two visible sparse window axes.
for x in [-36,-29]:
 for z in [4,7.5,11,14.5,18,21.5,25,28.5,32]:cuts.append(box(x,-19.52,z,1.5,.6,2))
# Reading terrace is solid below; shallow curved glazing and rooted parapet preserve its stepped levels.
def arcband(cx,cy,ro,ri,t0,t1,z,h):
 a=np.linspace(t0,t1,65);poly=[(cx+ro*np.cos(t),cy+ro*np.sin(t))for t in a]+[(cx+ri*np.cos(t),cy+ri*np.sin(t))for t in a[::-1]]
 return prism(poly,z,h)
for z,h,rad in [(2.5,4.5,18),(10.0,6.0,12)]:
 cuts.append(arcband(-24,0,rad+.2,rad-.35,-np.pi/2+.06,-.06,z,h))
 for t in np.linspace(-np.pi/2+.10,-.10,12):frames.append(arcband(-24,0,rad-.05,rad-.7,t-.035,t+.035,z,h))
frames.append(arcband(-24,0,11.92,11.3,-np.pi/2+.067,-.067,13.05,.70))
frames.append(arcband(-24,0,18,17.1,-np.pi/2+.04,-.04,9.4,1.1))
for z in [2.5,6.0]:
 cuts.append(arcband(9,-2.1,3.85,3.35,np.pi,2*np.pi,z,2.2))
# Exposed lower reading-terrace ring, separate from the higher reading floor.
frames.append(arcband(-24,0,21.0,17.5,-np.pi/2+.08,-.08,3.0,.9))
frames.append(arcband(-24,0,20.94,20.1,-np.pi/2+.09,-.09,3.75,.9))
# Two tall glazed zones flank the mural and retain their original back wall; the two outer rings are solid.
def elliptic_band(ro,ry,ri,riy,t0,t1,z,h):
 a=np.linspace(t0,t1,49);poly=[(39+ro*np.cos(t),-1+ry*np.sin(t))for t in a]+[(39+ri*np.cos(t),-1+riy*np.sin(t))for t in a[::-1]]
 return prism(poly,z,h)
for z,h in [(1.5,10.7),(14.1,19.0)]:
 for t0,t1 in [(np.pi+.30,1.5*np.pi-.35),(1.5*np.pi+.35,2*np.pi-.10)]:
  cuts.append(elliptic_band(5.7,6.7,5.15,6.15,t0,t1,z,h))
  for zz in np.arange(z+2.6,z+h,3):frames.append(elliptic_band(5.30,6.30,4.9,5.9,t0+.02,t1-.02,zz,.70))
for z in [12.8,33.8]:frames.append(elliptic_band(6.3,7.3,4.9,5.9,np.pi+.02,2*np.pi-.02,z,1.05))
# Main vertical side strips are retained uncut body at the window bounds; no separate narrow strip overlay.
# Central mural is the retained uncut strip between curved glazed fields; avoid overlapping rectangular cuts.
# Fine upper D-head louvers omitted at print scale to retain continuous wall root.
# Minimal continuous rooted linework, grouped facade members.
for z in [3.1,6.6,10.1,13.6,17.1,20.6,24.1,27.6,31.1]:
 frames.append(box(0,-.16,z,48,.75,.75));frames.append(box(-23.84,1,z,.75,34,.75))
solid=Manifold.batch_boolean(parts,OpType.Add)
for c in cuts:solid=solid-c
for f in frames:solid=solid+f
solid=solid.rotate((0,0,150));bb=solid.bounding_box();scale=150/max(bb[3]-bb[0],bb[4]-bb[1],bb[5]-bb[2]);solid=solid.scale((scale,scale,scale))
a=solid.to_mesh64();m=trimesh.Trimesh(np.array(a.vert_properties,dtype=np.float32)[:,:3],np.array(a.tri_verts),process=False);m.export(R/'model.stl');print('scale',scale,'extent',m.extents,'shells',len(solid.decompose()),'watertight',m.is_watertight)
