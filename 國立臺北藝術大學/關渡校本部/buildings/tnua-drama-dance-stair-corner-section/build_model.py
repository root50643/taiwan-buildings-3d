"""戲劇舞蹈教學大樓外角樓梯塔暨玻璃轉角段；2016刊文與公共藝術頁照片近似（公共藝術照片拍攝日未註）。
毫米；僅擷取玻璃 L 帶、高塔與相鄰短窗段。背面和兩翼都是裁切面。
不重建完整院落、不把2016照片當作2026現況；不是全棟測繪模型。
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
# Rectangular local plinth is a model support, not the complete sloping landscape.
add(5,20,0,108,112,3)
# The brick wing is deliberately cut through the L-shaped glass band.
add(-7,-6,2.8,48,32,111.2)
# Gray wing: only the first two wide bays and the tower-adjacent narrow slot.
add(28,45,2.8,30,38,82.2)
# Exposed stair tower: broad panel, brick return, thin end wall and five landings.
add(42.5,-7,2.8,3.0,30,147.2)
add(17,1.5,2.8,3.0,47,137.2)
add(30,25,2.8,27,2.8,121.2)
for z in [3,31,59,87,115]:add(30,1.5,z,27,49,3.1)
# Top cap spans the tower; the gap above the brick return remains open.
add(30,-7,147.1,29,33,2.9)
# Visible gallery balustrades are thickened. Unseen inner stair flights are omitted.
for z in [31,59,87,115]:
 for x in [20.0,30.0,40.0]:add(x,-23.0,z+2.9,1.5,1.8,9.0)
 for zz in [z+6.0,z+10.0]:add(30.0,-23.0,zz,25.0,1.8,1.45)
# The short return of the stair tower remains open above the low gray wing.
for z in [87,115]:
 for yy in [11.0,21.0]:add(43.0,yy,z+2.9,1.8,1.5,8.0)
 for zz in [z+6.0,z+9.5]:add(43.0,16.0,zz,1.8,13.0,1.45)
# Tall narrow tower opening with a projecting sill near the top.
cut(42.6,-12.0,118,5.0,5.8,19.0)
add(43.6,-12.0,115.5,5.8,8.4,2.8)
# Three distinct four-hole ventilation groups visible on the broad tower panel.
for z in [19.5,55.5,84.0]:
 for yy in [-9.0,-3.3]:
  for zz in [z,z+5.6]:cut(42.6,yy,zz,5.0,2.4,2.6)
# Recessed ground door at the return, below the projecting sign/canopy.
add(30.0,16.0,2.8,27.0,16.0,28.4)
cut(43.1,16.0,4.0,5.0,11.5,25.0)
for z in [7.0,12.0,17.0,22.0,27.0]:details.append(box(42.0,16.0,z,2.5,11.8,1.3))
# A local exit overhang on the gray-wing side, as seen in both source angles.
add(44.0,15.0,31.2,6.0,13.5,3.0)
# L-shaped glazing recess on the brick face (-Y): upper horizontal bar and upright.
cut(-7.0,-22.0,91.9,47.0,4.5,20.6)
cut(10.0,-22.0,37.0,13.0,4.5,75.5)
# Main glazing bands: simplified broad horizontals and verticals, not every pane.
for z in [37+75.5*k/11 for k in range(1,11)]:
 details.append(box(10.0,-21.9,z,13.4,2.6,1.35))
for z in [98.83,105.66]:details.append(box(-7.0,-21.9,z,47.2,2.6,1.35))
for x in [-22.0,-11.0,0.0]:details.append(box(x,-21.9,91.9,1.35,2.6,20.8))
details.append(box(10.0,-21.9,37.0,1.35,2.6,75.7))
# Three brick windows below the horizontal branch; no extension of unseen arrays.
for x in [-24,-13,-2]:cut(x,-22.0,65.0,6.0,4.0,15.0)
# The three nearest lower openings are visible beside the glass corner.
for x in [-13,-2,10]:cut(x,-22.0,10.0,6.0,4.0,20.0)
# One partial middle opening on the cropped left is occluded in the photographs;
# it is intentionally not invented. Back and cut ends have no guessed windows.
# Gray wing has two wide top openings and one narrow slot next to the tower.
for yy in [42.0,54.0]:cut(43.1,yy,62.0,4.0,8.3,15.0)
cut(43.1,31.5,62.0,4.0,2.1,15.0)
# First lower bay is clear; farther lower gray openings are tree-obscured and omitted.
cut(43.1,42.0,36.0,4.0,8.3,15.0)
cut(43.1,42.0,9.0,4.0,8.3,15.0)
# Substantial horizontal louvers only, kept fused to recessed window jambs.
for z in [66.0,70.4]:
 for yy in [42.0,54.0]:details.append(box(42.8,yy,z,2.0,8.55,1.25))
# Shallow cut markers are internal conventions, not claimed architectural features.
cut(-31.0,-6.0,6.0,.9,25.0,.7)
cut(28.0,64.0,6.0,24.0,.9,.7)
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,[(p.volume(),p.bounding_box()) for p in solid.decompose()]
m=solid.simplify(.00001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj')
print('dimensions_mm',mesh.extents,'watertight',mesh.is_watertight,'volume',mesh.volume)
