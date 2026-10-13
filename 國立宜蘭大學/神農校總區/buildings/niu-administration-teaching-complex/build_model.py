"""國立宜蘭大學綜合行政教學大樓，公開實拍/逃生平面衍生近似外觀。
Self-authored solid miniature, no third-party mesh. Millimetres, base down.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def hip(x,y,z,w,d,h):parts.append(CrossSection.square((w,d),center=True).extrude(h,scale_top=(.87,.035)).translate((x,y,z)))
# -Y faces the main gate. U-shaped group is one model, not three counted buildings.
add(0,0,0,124,150,3)
add(0,-50,2.8,108,26,48.2)
for x in [-42,42]:
 add(x,13,2.8,24,102,38.2)
 # Inward facing open galleries. Slots are real deep recesses; parapets remain fused.
 for level in range(4):
  z=4+level*9.0
  for y in [-27,-14,-1,12,25,38,51]:
   cut(x-(10.1 if x>0 else -10.1),y,z+2.1,5.3,10.8,5.4)
 # Outer face windows; groups follow classroom bays rather than uniform wallpaper.
 for level in range(4):
  z=5.1+level*9.0
  for y in [-26,-15,-4,7,18,29,40,51]:
   cut(x+(11.8 if x>0 else -11.8),y,z,2.6,8.3,5.1)
 for z in [11.5,20.5,29.5,38.5]:add(x,13,z,25,102,1.6)
 # End face contrasts: narrow slit plus larger classroom window.
 for z in [5.5,14.5,23.5,32.5]:
  cut(x-5.8,64,z,7.4,2.8,5.2);cut(x+5.6,64,z,1.8,2.8,5.2)
 # Low roof parapets and service cores from high-angle official photos.
 for xx in [x-11.2,x+11.2]:add(xx,13,40,1.6,102,2.1)
 for y in [-37,63]:add(x,y,40,24,1.6,2.1)
 for yy in [-23,40]:add(x+(-4 if x<0 else 4),yy,40.8,9,12,7.3)
 # Exposed stair tower, asymmetric side locations evident in the courtyard photo.
 yy=52 if x<0 else 37
 add(x+(9 if x<0 else -9),yy,3,5.5,12,43.8)
 # Ground-floor entrance canopy at the open end, plus stout attached posts.
 add(x,65,10.2,26,9,1.5)
 for xx in [x-10,x+10]:add(xx,68.2,3,1.9,1.9,7.5)
# Admin front: five-storey sculpted recess grid with alternating widths.
# Rectangular tapered cuts form deep chamfered stone reveals.
def tapered_front_window(x,z,w,h,shift=0,y=-63):
 # Asymmetric reveal is a convex frustum, wide outer opening and shifted inner pane.
 # Original front photo p.173: unequal window groups and row-by-row stagger.
 p=CrossSection.square((w,h),center=True).extrude(2.8,scale_top=(.70,.70),twist_degrees=0)
 # shear in section depth gives a left/right offset to the inset pane.
 p=p.transform(((1,0,shift/2.8,0),(0,1,0,0),(0,0,1,0)))
 p=p.rotate((-90,0,0)).translate((x,y-.12,z+h/2))
 cuts.append(p)
# Pixel-derived outer-window intervals from the official frontal photograph.
# Obscured lowest two storeys use conservative grouped estimates (no survey claim).
rows={
 41.2:[(50,196,22),(236,333,15),(372,500,-12),(539,629,13),(666,868,-12),(892,1000,6),(1084,1290,-17),(1325,1374,0),(1395,1590,-14)],
 32.0:[(50,145,9),(184,333,12),(371,450,11),(479,627,13),(666,785,7),(841,1000,3),(1040,1124,-8),(1158,1290,10),(1362,1505,0)],
 22.8:[(50,195,15),(235,333,10),(371,489,1),(539,627,9),(666,836,-3),(875,1000,8),(1042,1142,0),(1180,1305,0),(1362,1505,0)],
 13.6:[(50,145,10),(184,333,10),(371,450,10),(479,627,10),(1040,1142,-8),(1180,1305,0),(1362,1505,0)],
 4.4:[(50,195,10),(235,333,10),(371,489,0),(539,627,5),(1042,1142,0),(1180,1305,0),(1362,1505,0)]}
for z,groups in rows.items():
 for left,right,delta in groups:
  x=(left+right)/2/1650*108-54;w=(right-left)/1650*108
  tapered_front_window(x,z,w,7.5,delta/1650*108)
# Tall central ground passage, remains visibly open toward the courtyard.
cut(.8,-50,3,24,28,17.2)
add(.8,-65.0,20.2,27,5.8,1.5)
for x in [-12.4,14.0]:add(x,-66.1,3,1.8,1.8,17.6)
# Admin end elevations: deep square bays and solid piers.
for x in [-54,54]:
 for y in [-58,-49,-40]:
  for z in [5.3,14.3,23.3,32.3,41.3]:cut(x,y,z,3.5,5.8,6.0)
# Courtyard-facing admin facade: glazed central stack, taller end bars.
for x in [-38,-25,-12,1,14,27,40]:
 for z in [6,15,24,33,42]:
  if abs(x)<30 or z>41:cut(x,-37,z,8.2,3.2,5.8)
for x in [-25,25]:
 add(x,-35.5,3,3,2.3,52)
 cut(x,-35.7,7,1.2,2.8,37)
# Slender hipped roof silhouette seen above the back elevation; no invented plant.
hip(0,-50,50.8,111,29,2.3)
add(0,-63.1,50.5,110,1.5,2.5)
for x in [-25,25]:add(x,-45,52.0,4,5,4.1)
# Mid-courtyard covered footbridge: open below, strong enough for a miniature.
add(0,-9,17.0,63,7.4,1.8)
add(0,-9,24.1,63,8.5,1.6)
for x in [-29,-20,-10,0,10,20,29]:
 for y in [-12.3,-5.7]:add(x,y,18.6,1.5,1.5,5.7)
for y in [-12.3,-5.7]:add(0,y,18.6,63,1.5,1.6)
# Lower courtyard terrace and circular meeting area retain void above base.
add(0,-30,2.9,58,14,1.3)
for k in range(4):add(0,-21+k*1.4,2.9,56,1.6,1.4-.28*k)
parts.append(Manifold.cylinder(.8,17,17,circular_segments=80).translate((0,41,2.9)))
# Border seat is a backed low arc, avoids filament-sized isolated railings.
ring=Manifold.cylinder(1.4,18.5,18.5,circular_segments=80)-Manifold.cylinder(2,17.1,17.1,circular_segments=80).translate((0,0,-.2))
ring=ring ^ box(0,6,0,45,23,3)
parts.append(ring.translate((0,41,3)))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
print("components",[(p.volume(),p.bounding_box()) for p in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(1e-5).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'faces',len(mesh.faces))
