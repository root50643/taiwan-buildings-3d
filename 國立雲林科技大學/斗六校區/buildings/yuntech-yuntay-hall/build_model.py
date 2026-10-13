"""雲泰表演廳外觀縮模；毫米。校方扇形平面、2022/2024實拍及2021屋頂空拍。
自建幾何；2021年底整修後入口。樹遮蔽側翼窗位、屋面微坡與機電簡化估計。
"""
from pathlib import Path
import math,numpy as np,trimesh
from manifold3d import Manifold,CrossSection
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def sector(r,z,h,a=0,b=90,inner=0):
 ang=np.linspace(math.radians(a),math.radians(b),max(3,int((b-a)*2)+1));pts=[(r*math.cos(t),r*math.sin(t)) for t in ang]
 pts+=([(inner*math.cos(t),inner*math.sin(t)) for t in ang[::-1]] if inner else [(0,0)])
 return CrossSection([pts]).extrude(h).translate((0,0,z))
def radial(r,t,z,w,d,h):return box(r,0,z,d,w,h).rotate((0,0,t))
# Local origin is the corner stage. 75.4 x 77.25 m overall plan, independent miniature scale.
# Rectangular base is centered with body later shifted by (-46,-46).
add(46,46,0,150,150,2.8)
# Broad curved forecourt, deliberately no unattached lamp posts or thin railings.
for r,z in [(116,2.6),(114.5,3.3),(113,4.0),(111.5,4.7)]:parts.append(sector(r,z,.85))
# Fan-shaped auditorium, outer curved gallery and straight backstage wings.
parts.append(sector(106,5.3,27.8))
parts.append(sector(110,5.2,24.6,inner=100))
add(-7,48,2.7,14,103,28.4);add(48,-7,2.7,103,14,28.4)
add(-7,104,2.7,19,17,29.8);add(104,-7,2.7,17,19,29.8)
# Thick continuous curved parapet and waist cornice are defining elevations.
parts.append(sector(111,14.7,4.4,0,90,inner=102))
parts.append(sector(110.1,22.8,9.4,0,90,inner=104))
parts.append(sector(110.5,31.6,1.2,0,90,inner=104))
# Main flat/slightly sloped roof simplified to a low fan tier; open drainage groove remains.
parts.append(sector(105,32.7,1.2))
cuts.append(sector(108.2,29.0,7.0,3.7,86.3,inner=106.3))
# 15 primary ground-floor bays counted in the 2024 frontal photo; do not mistake door leaves for columns.
# Clerestory remains a separate, denser row.
for t in np.linspace(3.0,87.0,15):
 cuts.append(radial(109.5,float(t),5.7,9.3,5.6,8.5))
for t in np.linspace(3.1,86.9,36):cuts.append(radial(109.4,float(t),19.1,2.2,3.5,2.9))
# Upper broad panel joints have printable relief rather than paper-thin free frames.
for t in np.linspace(2,88,19):cuts.append(radial(110,float(t),23.6,.85,1.3,7.6))
# Street-facing 2021 renovated entrance on straight wing, recessed large portal.
add(64,-17,2.7,55,12,28.4)
add(64,-23.4,3.5,29,4,19.1)
cut(64,-24,4.2,24,7,13.5)
cut(64,-23.2,24,22,2,3.5)
for x in [40,49,87]:
 for z,h in [(6,7.5),(21,5.5)]:cut(x,-23.1,z,5.4,2.4,h)
for x in [55,60,65,70,75]:details.append(box(x,-21.0,4.5,.9,1.8,12.5))
details.append(box(64,-21.0,13.5,24,1.8,1.0))
for i in range(4):add(64,-27+i*.9,2.7+i*.38,26,1.8,.65)
# Opposite backstage leg: outline is documented, window spacing under trees is approximate.
for y in [12,26,40,54,68,82,96]:
 for z in [6,21]:cut(-14.1,y,z,2.3,5.5,6)
# Roof service blocks visible in plan and aerial; omit small fans and solar-cell microgrid.
add(-5,20,30.5,11,16,5);add(21,-5,30.5,16,11,5)
add(-5,80,30.5,12,24,2.1);add(80,-6,30.5,23,12,2.1)
# Three large backed solar-array panels on main roof from the documented overhead view.
for a,b in [(10,29),(31,50),(52,71)]:parts.append(sector(97,33.8,.9,a,b,inner=32))
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
solid=solid.translate((-46,-46,0))
assert len(solid.decompose())==1,'Disconnected or internal solid'
m=solid.simplify(1e-5).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');print(mesh.extents,mesh.is_watertight)
