"""圖書資訊大樓：依公開外觀照片製作的估計微縮模型，尺寸單位 mm。"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# One continuous print bed. Longest extent exactly 150 mm, not surveyed scale.
add(0,0,0,150,104,3)
# Square tall library mass, broad lower information/conference wing, step connector.
add(-39,20,2.8,53,49,61)
add(4,-16,2.8,132,37,32)
add(-3,21,2.8,22,41,41)
# Low right-hand wing extends beyond the tall block as seen in the panorama.
add(38,11,2.8,65,37,30)
# Front recessed glazed entrance below tall blank fascia: modeled as shallow relief.
cut(4,-34.1,7,116,2.2,17)
# Integral round columns across recessed lower entrance; all overlap the structure.
for x in [-49,-43,-8,-2,34,40,58]:
 details.append(Manifold.cylinder(19,1.35,1.35,24).translate((x,-34.4,5)))
# Horizontal sunshade beams backed by the facade, not floating overhangs.
for z in [24.4,27.5]:add(4,-35,z,121,2.4,1.25)
# Foreground stone-screen colonnade and broad stepped terrace from near view.
add(2,-43,3,131,3.4,3)
for x in np.arange(-59,65,11):
 if x != 7:add(float(x),-42.5,5.8,2.8,3.4,17)
add(2,-42.5,22,131,3.4,2.5)
# A low solid terrace at right with an offset open stair flight.
add(44,-39,3,44,12,9)
for i in range(9):add(9,-46+i*1.4,3,16,1.65,(i+1)*.96)
# Rear/public landscape-facing library glazing panel with integral grid.
# Leave enough facade thickness beneath every recessed pane.
for ix in range(6):
 for iz in range(6):cut(-55+ix*6.4,44.2,17+iz*5.3,5.4,1.7,4.35)
# Tall narrow vents/windows above large glazing, a defining visible feature.
for x in np.arange(-55,-17,4.8):cut(float(x),44.2,56,2.8,1.7,4.5)
# Lower three tiers of small windows seen beneath the tall glazing panel.
for x in np.arange(-56,-15,8):
 for z in [6,11.5]:cut(float(x),44.2,z,5,1.7,3.2)
# Side glazing field on tall tower.
for yy in np.arange(5,40,6):
 for zz in np.arange(17,49,5.3):cut(-65.25,float(yy),float(zz),1.7,4.8,4.1)
for yy in np.arange(7,38,6):cut(-65.25,float(yy),56,1.7,3.7,4.4)
# Near-view upper library clerestory slots and long narrow strip below.
for x in np.arange(-55,-18,6):cut(float(x),-4.15,51,3.5,1.6,5.2)
cut(-37,-4.15,45,37,1.6,3)
# Wide horizontal dark slit on low outer wing, with split lower strip.
cut(38,29.2,19,51,1.7,5)
cut(41,29.2,13.5,44,1.7,2.5)
for x in np.arange(15,64,8):details.append(box(float(x),29.45,19,.9,.9,5))
# Sparse side windows; hidden sides are conservative approximation.
for yy in [-19,-11,-3,5,13,21]:cut(70.1,yy,12,1.7,5,3.5)
# Thin tile joint relief on broad visible blank facade (recess depth 0.35 mm).
for z in [29.5,32.3]:cut(4,-34.6,z,129,.7,.35)
for x in np.arange(-60,69,11):cut(float(x),-34.6,27.5,.35,.7,7.1)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for detail in details:solid=solid+detail
m=solid.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('Extents mm',mesh.extents,'watertight',mesh.is_watertight)
