"""YZU Building5 + 2006 library extension, bounded candidate, not survey.
Metre coordinates X east Y north; main high roof ca51x51m, nominal31m.
Export at1.5mm per estimated metre, base-inclusive longest150mm.
"""
from pathlib import Path
import json,numpy as np,trimesh
from manifold3d import Manifold,OpType
O=Path(__file__).resolve().parent;P=[];C=[];D=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):P.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):C.append(box(x,y,z,w,d,h))
def hull(v):return Manifold.hull_points(v)
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,48).translate((x,y,z))
def grid_roof(x,y,z,w,d):
 # Closed glass roof with shallow backed grid, never an open roof hole.
 q=box(x,y,z,w+.15,d+.15,.9)
 for a in np.arange(x-w/2+.55,x+w/2-.55,1.8):
  for b in np.arange(y-d/2+.55,y+d/2-.55,1.8):q=q-box(a,b,z+.68,1.15,1.15,.4)
 P.append(q)
def solar(x,y,z,w,d):
 q=box(x,y,z,w,d,.4)
 for a in np.linspace(x-w/2,x+w/2,max(1,round(w/3))+1)[1:-1]:q=q-box(a,y,z+.27,.25,d+.1,.2)
 for b in np.linspace(y-d/2,y+d/2,max(1,round(d/3))+1)[1:-1]:q=q-box(x,b,z+.27,w+.1,.25,.2)
 P.append(q)
def glass_x(x,y,z,w,h):
 cut(x,y,z,.7,w,h)
 for b in np.arange(y-w/2+1.1,y+w/2,1.65):D.append(box(x+(.3 if x<0 else -.3),b,z,.6,.38,h))
 for zz in np.arange(z+1.5,z+h,1.8):D.append(box(x+(.3 if x<0 else -.3),y,zz,.6,w-.3,.3))
def glass_y(x,y,z,w,h):
 cut(x,y,z,w,.7,h)
 for a in np.arange(x-w/2+1.1,x+w/2,1.65):D.append(box(a,y+.3,z,.38,.6,h))
 for zz in np.arange(z+1.5,z+h,1.8):D.append(box(x,y+.3,zz,w-.3,.6,.3))
# 82x100m base, nominal origin at main roof centre; adjacent buildings excluded.
add(6,-20,-2,82,100,2)
# Old main body and actual west flared frame, not a filled facade box.
add(0,0,-.1,51,51,1.3)
frame=box(-15.5,0,0,21,51,31)
# Two sloping side walls derived from official plan's wide mouth to narrow throat.
P.append(frame-hull([(x,y,z) for x,lo,hi in [(-27,-23.6,23.6),(-4.6,-17.2,12)] for y in [lo,hi] for z in [1.2,29.1]]))
# U-shaped high rear body around the covered inner court.
add(10.25,18.75,0,30.5,13.5,31)
add(10.25,-21.35,0,30.5,8.3,31)
add(18.25,-2.6,0,14.5,29.2,31)
grid_roof(3.2,-2.6,30.1,15.6,29.2)
# Inner galleries and bridge slabs: connected to real enclosing wings.
for z in [5.4,9.5,13.6,17.7,21.8,25.9]:
 add(3.3,10.5,z,15.8,3.1,.7)
 add(3.3,-15.7,z,15.8,3.1,.7)
 # low backed solid gallery parapet, not free hairline railing
 D.append(box(3.7,9.1,z+.6,16.6,.85,1.0))
 D.append(box(3.7,-14.3,z+.6,16.6,.85,1.0))
# Recessed rear gallery bays visible through the monumental opening.
for z in [5.4,9.5,13.6,17.7,21.8,25.9]:
 for y in [-12,-5,2,9]:cut(11,y,z+1,1.0,4.6,2.4)
 for x in [-1,4,9]:cut(x,12,z+1,2.8,.8,2.3)
# Suspended glass meeting box, two lower piers and an upper hanger.
add(-14,8.7,9,10,21.4,10.3)
add(-14,8.7,8.6,10.6,22, .7)
for y in [-1.1,14.0]:P.append(cyl(-17.0,y,1.1,.85,7.8))
P.append(cyl(-12.8,-.6,19.1,.8,10.3))
# West glass face: fine backed divisions rather than hollow shell.
# Two tall glazing storeys with finer horizontal transom bands; all wall-backed.
for y in np.arange(-.5,18.6,1.72):
 for z,h in [(9.65,.55),(10.45,.55),(11.25,1.5),(13.05,.65),(14.8,.55),(15.6,.55),(16.4,1.5),(18.2,.45)]:cut(-19.0,y,z,.65,1.35,h)
# Side glass on the box's south exposed face, fully wall-backed.
glass_y(-13.4,-2.0,9.5,8.1,9.3)
# Main entry steps and secondary stair to the right of the hanging box.
for i in range(8):add(-30+i*.55,0,0,.8,45,.15*(i+1))
for i in range(18):add(-18.5+i*.65,-8.2,1.1,.85,5.8,.37*(i+1))
add(-13.5,-15.0,1.1,5.8,4.0,7.2)
# Entry small box: shallow wall-backed panes, no projecting fine mullions.
for yy in [-15.9,-14.1]:
 for zz in [1.8,4.0,6.2]:cut(-16.4,yy,zz,.24,1.15,1.6)
# South visible facade: broad horizontal transoms with a lowered central glazing group,
# framed by two major piers; lower portions masked by extension are not invented.
for z in [12.8,16.9,21.0,25.1]:
 cut(10.2,-25.5,z+1.25,13.6,.65,.65)
 cut(10.2,-25.5,z,6.5,.65,1.9)
 for x in [8.1,10.2,12.3]:D.append(box(x,-25.28,z,.28,.55,1.9))
 for x in [-2,23]:
  cut(x,-25.5,z+.2,1.25,.6,2.2)
  cut(x,-25.5,z+2.65,2.6,.6,.6)
cut(10.2,-25.5,28.2,13.6,.65,.8)
for x in [1.5,18.8]:add(x,-25.8,12.1,1.35,.85,18.9)
# East observed area: wide upper transom + offset narrow tall lower slit.
# The far north portion is deliberately not filled with a guessed window array.
for y in [14,16.1,18.2,20.3,22.4,24.0]:
 for z in [3.7,7.8,11.9,16.0,20.1,24.2]:
  cut(25.5,y,z+2.55,.65,1.6,.85)
  cut(25.5,y+.5,z,.65,.45,2.55)
 cut(25.5,y,1.1,.65,1.6,.9)
add(25.95,12,0,1.5,1.3,31.6)
# North exterior window details are unverified and deliberately omitted.
# 2006 south extension:3F over B1, nominal12.2m roof, separately covered court.
# East strip projects farther south and east; not merged into the high box.
add(3.2,-41.0,0,24,31.4,12.2)
add(23.2,-50.9,0,16,11.6,12.2)
add(23.2,-29.85,0,16.15,9.1,12.2)
add(35.7,-36.5,0,13.0,55.8,12.2)
# western/central infill floor under the lower glass atrium.
add(23.2,-39.7,0,16.1,13.4,11.4)
grid_roof(23.2,-39.7,11.3,16,13.2)
# Side wing glass is a recessed curtain-wall pattern, not open library floors.
for x in [-8.8,42.2]:
 for y,z,w,h in [(-41.1,1.0,29,9.8)]:
  cut(x,y,z,.65,w,h)
  for b in np.arange(y-w/2+1,y+w/2,3.2):D.append(box(x+(.3 if x<0 else -.3),b,z,.55,.42,h))
  for zz in [4.3,7.6,10.1]:D.append(box(x+(.3 if x<0 else -.3),y,zz,.55,w-.3,.45))
for x,w,y in [(3.2,23,-56.7),(23.2,15,-56.7),(35.7,12,-64.4)]:glass_y(x,y,1.0,w,9.8)
# Southwest strip confirmed as a low glazed wing by 2018 south/west photographs.
add(-21,-38.2,0,9,25.6,10.3)
add(-21,-38.2,10.3,9.5,25.8,.7)
for x in [-25.5,-16.5]:
 cut(x,-38.2,1.0,.65,23.5,8.5)
 for y in np.arange(-49.4,-26.7,3.2):D.append(box(x+(.3 if x< -20 else -.3),y,1.0,.6,.4,8.5))
 for z in [3.8,6.6,9.2]:D.append(box(x+(.3 if x< -20 else -.3),-38.2,z,.6,23.3,.4))
# Actual broad photovoltaic fields from2024 orthophoto, shallow backed relief.
for x,y,w,d in [(-10.4,2,7.8,47),(18,-.2,12,49),(3,-21.8,30,6)]:solar(x,y,31.0,w,d)
for x,y,w,d in [(1.8,-41,12,26),(23,-52.5,14,7),(35.7,-40.7,10,27)]:solar(x,y,12.2,w,d)
# Major roof services, bounded heights. No copied tower from neighbouring Building6.
add(5.0,19.9,30.9,6.2,14.8,2.5)
for y in [15.2,19.3,23.4]:add(5,y,33.3,3.2,2.4,.9)
for y in [-15,-8,-1,6,13,21]:add(-22,y,31,1.9,3.4,1.1)
# Eastern low roof terrace and short equipment strip behind high body.
add(34.2,3.4,0,16.5,19,8.5)
# Northern car forecourt is ground, not a guessed roof mass.
solid=Manifold.batch_boolean(P,OpType.Add)-Manifold.batch_boolean(C,OpType.Add)
solid=solid+Manifold.batch_boolean(D,OpType.Add)
solid=solid.scale((1.5,1.5,1.5)).translate((0,0,3)).simplify(.00001)
m=solid.to_mesh64();mesh=trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:,:3]),faces=np.asarray(m.tri_verts),process=True);mesh.export(O/'model.stl')
print(mesh.bounds,mesh.is_watertight,len(mesh.faces))
(O/'draft-parameters.json').write_text(json.dumps({'status':'bounded candidate, not frozen','main_roof_m':31,'extension_roof_m':12.2,'main_roof_plan_m':[51,51],'mm_per_estimated_m':1.5,'southwest_strip_identity':'low glazed wing, height10.3m provisional','ground':'bounded, B1 grade not surveyed'},indent=2))
