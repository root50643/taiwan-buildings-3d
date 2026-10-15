"""Original OCU bounded massing candidate. Nominal heights, no surveyed floor plan."""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType
R=Path(__file__).parent;P=[];C=[];F=[];GL=1.3
# x east, y north before -2.5degree plan rotation. Roof-derived plan is a bounded candidate.
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z+GL))
def prism(p,z,h):return CrossSection([np.array(p,float)]).extrude(h).translate((0,0,z+GL))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,96).translate((x,y,z+GL))
def ring(x,y,z,ro,ri,h):return cyl(x,y,z,ro,h)-cyl(x,y,z-.01,ri,h+.02)
def arcband(cx,cy,z,ro,ri,h,t0,t1):
 a=np.linspace(t0,t1,97);return prism([(cx+ro*np.cos(t),cy+ro*np.sin(t))for t in a]+[(cx+ri*np.cos(t),cy+ri*np.sin(t))for t in a[::-1]],z,h)
def beam(a,b,w,d):
 a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v);z=np.array([0.,0.,1.]);xx=np.cross([0,1,0],v/L)
 if np.linalg.norm(xx)<.1:xx=np.cross([1,0,0],v/L)
 xx/=np.linalg.norm(xx);yy=np.cross(v/L,xx);T=np.column_stack([xx,yy,v/L,a+[0,0,GL]])
 return Manifold.cube((w,d,L)).translate((-w/2,-d/2,0)).transform(T)
P.append(box(1,-3,-GL,88,62,GL))
# Rear high wing, west lower roof and east projecting higher block.
P += [box(-12,11,0,40,18,50),box(22,7,0,28,26,55)]
# End service cores articulate rear silhouette.
P += [box(-29,11,0,8,19,51.5),box(34,11,0,8,22,57.0)]
# West cylindrical glazed tower: capped, not an open shaft.
P += [cyl(-27,-1,0,7.7,55.8),cyl(-27,-1,50.0,8.05,5.8),cyl(-27,-1,55.6,8.5,1.0)]
# Source-visible inward flare: bounded continuous thin skirt, outer crown remains open.
outer=Manifold.cylinder(3.2,8.3,9.7,96).translate((-27,-1,56.0+GL))
inner=Manifold.cylinder(3.24,7.45,8.85,96).translate((-27,-1,55.98+GL))
P.append(outer-inner)
# Open radial double crown and upward braces rooted in cap.
P += [ring(-27,-1,59.5,13.4,12.55,.85),ring(-27,-1,59.5,11.95,11.10,.85)]
for t in np.linspace(0,2*np.pi,16,endpoint=False):
 P.append(beam((-27+7.5*np.cos(t),-1+7.5*np.sin(t),55.7),(-27+13*np.cos(t),-1+13*np.sin(t),59.7),1.05,1.05))
# Print-only radial backing webs between the inner skirt and each sloping brace.
# These stay below the double-ring top, preserving outer annular sky holes.
for t in np.linspace(0,2*np.pi,16,endpoint=False):
 q=CrossSection([np.array([[7.9,56.3],[8.5,56.3],[12.38,59.72],[8.8,59.72]])]).extrude(1.10)
 # Local profile x=radius,y=height; extrusion is tangential width.
 T=np.array([[np.cos(t),0,-np.sin(t),-27+.55*np.sin(t)],[np.sin(t),0,np.cos(t),-1-.55*np.cos(t)],[0,1,0,GL]])
 P.append(q.transform(T))
# Full-height short radial links join both near-horizontal crown rings.
for t in np.linspace(0,2*np.pi,16,endpoint=False):
 q=box(12,0,59.5,2.5,1.10,.85).rotate((0,0,float(np.degrees(t)))).translate((-27,-1,0))
 P.append(q)
# South low library in unequal portions and recessed entry: no automatic exposed B2/B1.
P += [box(18,-16,0,34,24,18),box(-27,-14,0,13,21,17.5)]
# Low front wing links at ground level behind the open recess, not a full-height infill.
P.append(box(-8,-16,0,25.2,24,17.5))
# Right upper low wing terrace is stepped, open parapet and white doorway frame.
P.append(box(12,-19.8,17.3,46,15.6,5.7))
C.append(box(18,-27.2,0.6,26,3.6,4.4))
# Backing face remains at recessed lobby; three rooted front piers.
for x in [6,18,30]:F.append(box(x,-27.4,0,1.5,1.5,5.4))
P.append(box(18,-28.3,5.1,30,2.5,.85))
# Source-visible front high windows: west dense small groups, east broad lower bands + top small rows.
for z,h in [(27,2.7),(32,2.7),(37,2.7),(42,1.8),(46,1.8)]:
 for x in np.arange(-17.8,7,3.2):C.append(box(x,1.98,z,1.55,.48,h))
for z in [17,22]:
 for x in [-10,-1]:C.append(box(x,1.98,z,6.4,.5,2.7))
for z in [23,28,33,38]:
 for x in [12,19,26,32]:C.append(box(x,-6.03,z,5.35,.5,2.7))
for z in [43,47,51]:
 for x in np.arange(11,34,3.1):C.append(box(x,-6.03,z,1.5,.5,1.7))
# Back north elevation: upper small punched windows, lower broad groups. Not a copy of south frames.
for z in [14.8,18.3,21.8,25.3,28.8,32.3]:
 for x in np.arange(-22,31,5.2):C.append(box(x,20.03,z,3.9,.5,1.9))
for z in [35.8,39.0,42.2,45.4,48.0]:
 for x in np.arange(-22,31,3.1):C.append(box(x,20.03,z,1.6,.5,1.2))
# Sparse vertical glazing of source-visible west core, unknown east end stays conservative.
for z in [14,18,22,26,30,34,38,42,46]:C.append(box(-33.03,10,z,.5,1.3,2.6))
# Curved glass: vertical frame roots overlap horizontal rings by 0.04m at both ends.
# Explicit overlap prevents near-zero source gaps collapsing into internal opposite faces at STL float32 export.
for z in np.arange(18.0,49.0,3.2):
 h=2.55;C.append(arcband(-27,-1,z,7.95,7.35,h,np.pi-.23,2*np.pi+.23))
 for t in np.linspace(np.pi+.1,2*np.pi-.1,11):F.append(box(-27+7.42*np.cos(t),-1+7.42*np.sin(t),z-.04,.65,.65,h+.08))
for z in np.arange(17.4,50.0,3.2):F.append(ring(-27,-1,z,7.95,7.1,.64))
# Silver cap restrained horizontal panel lines, retaining a continuous root.
for z in [51.5,53.0,54.5]:C.append(ring(-27,-1,z,8.2,7.9,.25))
# Dark low library window groups and yellow-like shading strips rendered monochrome.
for z in [7.0,12.1]:
 for x in [5.5,13.5,21.5,29.5]:
  if not(z==7.0 and x in [13.5,21.5]):
   C.append(box(x,-28.03,z,5.8,.65,3.1));F.append(box(x,-27.9275,z+1.65,6,1.255,.55))
for z in [6.8,11.8]:
 C.append(box(-27,-24.53,z,8,.6,3.1));F.append(box(-27,-24.45,z+1.65,8.3,1.3,.55))
for x in [-5,6,17,28]:
 C.append(box(x,-27.63,19.0,8.3,.6,2.8));F.append(box(x,-27.5625,20.35,8.5,1.225,.55))
for z in [7.0,12.1]:
 for x in [-16,-8,0]:
  C.append(box(x,-28.03,z,5.8,.65,3.1));F.append(box(x,-27.9275,z+1.65,6,1.255,.55))
# Source-visible lower-row double-width glass, shallow original back retained.
C.append(box(17.5,-28.03,7.0,13.8,.65,3.1))
for x in [12.0,14.75,17.5,20.25,23.0]:F.append(box(x,-27.85,7.0,.55,.75,3.1))
F.append(box(17.5,-27.85,8.3,13.8,.75,.55))
# Source front terrace: broad grey row plus a low left opening and a taller white frame.
for x in [-7.4,1.4]:F.append(box(x,-27.75,17.3,1.3,2.3,10.2))
P.append(box(-3,-27.75,26.2,10.1,2.3,1.3))
P.append(box(-3,-27.25,17.8,7.8,1.2,8.9))
C.append(box(-3,-27.9,18.9,7.3,.5,6.7))
F.append(box(-19.3,-27.75,17.3,1.3,2.3,5.2));P.append(box(-13.4,-27.75,21.3,12.8,2.3,1.2))
# North source-visible low podium and one long grouped window row.
P.append(box(1,22,0,70,6.2,9.5))
for x in [-24,-13,-2,9,20,30]:
 C.append(box(x,25.13,4.7,8.0,.6,3.2));F.append(box(x,24.9875,6.1,8.2,1.375,.55))
F.append(box(1,25.1,9.1,70,.75,.65))
# Minimal rooftop equipment visible in both orthophotos.
P += [box(31,12,57,6,8,1.2),box(24,9,55,5,5,1.4)]
# Entrance steps, each grounded and overlapping.
for i in range(4):P.append(box(18,-30.2-i*.65,0,30+i*.5,1.5,.30*(4-i)))
solid=Manifold.batch_boolean(P,OpType.Add)
for c in C:solid=solid-c
for f in F:solid=solid+f
solid=solid.rotate((0,0,-2.5));bb=solid.bounding_box();S=150/max(bb[3]-bb[0],bb[4]-bb[1],bb[5]-bb[2]);solid=solid.scale((S,S,S));a=solid.to_mesh64();m=trimesh.Trimesh(np.asarray(a.vert_properties,dtype=np.float32)[:,:3],np.asarray(a.tri_verts),process=False);m.export(R/'model.stl');print('scale',S,'extent',m.extents,'shells',len(solid.decompose()))
