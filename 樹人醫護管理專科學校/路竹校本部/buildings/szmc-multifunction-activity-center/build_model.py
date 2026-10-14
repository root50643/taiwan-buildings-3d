"""樹人2016多功能活動中心，平面／照片有界原型，非實測。mm。
Plan coordinates refer to 3840px ground plan, +x right and +y down on paper.
North points paper upper-right. Upper plan aligned +45px x, unchanged y.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,Mesh64
R=Path(__file__).resolve().parent
PX=1.18/22.9; UNIT=1.18; Z0=1.6
parts=[];cuts=[];late=[]
def xy(p):return ((p[0]-2000)*PX,(1400-p[1])*PX)
def Z(m):return Z0+m*UNIT
def boxmm(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def rect(x0,y0,x1,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def cs(p):
 if sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))<0:p=p[::-1]
 return CrossSection([p])
def poly(pp,z,h):return cs([xy(p) for p in pp]).extrude(h).translate((0,0,z))
def addbox(x0,y0,x1,y1,z,h):parts.append(poly(rect(x0,y0,x1,y1),Z(z),h*UNIT))
def cutbox(x0,y0,x1,y1,z,h):cuts.append(poly(rect(x0,y0,x1,y1),Z(z),h*UNIT))
def roofheight(x,y):
 px=x/PX+2000;py=1400-y/PX
 return Z(18-3.5*(px-890)/1540-4*max(1800-py,0)/1120)
def loft(pp,bottom,top):
 m=cs([xy(p) for p in pp]).extrude(1).to_mesh64();v=np.asarray(m.vert_properties).copy();v[:,2]=[bottom+(top(x,y)-bottom)*z for x,y,z in v[:,:3]]
 return Manifold(Mesh64(np.ascontiguousarray(v,dtype=np.float64),np.array(m.tri_verts,dtype=np.uint64,order="C",copy=True)))
def roof(pp):
 a=loft(pp,Z0,roofheight);b=loft(pp,Z0,lambda x,y:roofheight(x,y)-1.15);return a-b
# Continuous 150mm base and deliberately limited terrain footprint.
parts.append(boxmm(0,0,0,150,106,1.6))
# Main gym solid proxy: no inaccessible internal hollow shell.
parts.append(loft(rect(1060,835,2280,1745),Z0-.1,lambda x,y:roofheight(x,y)-.8))
# Ground service strips and raised library/media wing traced independently.
addbox(950,740,1135,1890,-.05,4.4)
addbox(1135,740,1520,900,-.05,4.4)
addbox(2280,835,2440,1745,-.05,8.8)
addbox(1280,1745,1908,2060,-.05,8.6)
addbox(2440,1625,3270,1990,-.05,8.6)
# Thin proxy wall beneath outdoor/gallery circulation; deep recesses preserve reading.
addbox(1900,1935,2445,2060,-.05,8.6)
addbox(1900,1740,2445,1790,-.05,8.6)
# Crossing foyer is open at ground and locally open to the roof above.
# Finite bridge deck joins the media centre and eastern wing.
addbox(1885,1930,2460,2070,4.1,.85)
for x in [2010,2280,2445]:
 addbox(x-13,1935,x+13,1961,-.05,4.3)
# Main large slope and lower long wing; seams do not create separate buildings.
parts.append(roof(rect(890,680,2430,1800)))
parts.append(roof(rect(890,1800,3350,2060)))
parts.append(roof(rect(2430,1610,3350,1800)))
# Aerial long opening is over circulation, not cut through the covered ball court.
cutbox(1450,1795,3070,1905,10.4,15)
for x in [1790,2180,2570,2960]:
 late.append(roof(rect(x-13,1770,x+13,1800)));late.append(roof(rect(x-13,1800,x+13,1925)))
# Paper-left grass-facing folded white facade, top and lower boundary differ.
# A thick slanted plate; its lower corner connects to soil/base rather than floats.
def facade_yz(points,xpaper,thickness,shear=0):
 # points are paper y and elevation metres; extrude normal to x.
 coords=[((1400-y)*PX,Z(z)) for y,z in points]
 q=cs(coords).extrude(thickness)
 return q.transform(np.array([[0,shear,1,(xpaper-2000)*PX],[1,0,0,0],[0,1,0,0]],dtype=float))
parts.append(facade_yz([(680,13.6),(1800,12),(1800,10.8),(1350,6.3),(1100,1.0),(930,1.0)],1020,6.0,-.12))
# Long field-facing folded fascia left of foyer, tilted outwards near its foot.
def facade_xz(points,ypaper,thickness,shear=0):
 coords=[((x-2000)*PX,Z(z)) for x,z in points]
 q=cs(coords).extrude(thickness)
 return q.transform(np.array([[1,0,0,0],[0,shear,-1,(1400-ypaper)*PX],[0,1,0,0]],dtype=float))
parts.append(facade_xz([(1255,3.0),(1390,11.2),(2380,10.5),(2460,1.8),(2340,1.8),(2310,3.0)],1990,5.37,.13))
# Right-end deep folded corner drops towards ground beside the outdoor staircase.
parts.append(facade_xz([(2890,11.0),(3310,11.8),(3400,1.0),(3260,1.0)],1980,4.86,.08))
# Deep folded return at the campus end of the long wing, visible in MAYU03.
parts.append(facade_yz([(1610,11.65),(2060,11.8),(2060,.8),(1990,.8)],3250,5.20,0))
# Opposite pond-facing corner fold and lower window wall, bounded from MAYU05.
parts.append(facade_yz([(835,10.5),(1160,7.2),(1660,2.0),(1745,2.0),(1745,10.9)],2390,3.83,.08))
# Folded return at lowest roof corner connects the eave to the backstage wall.
parts.append(facade_yz([(670,10.4),(850,11.0),(850,0),(680,0)],2397,33*PX,0))
# Landscape berm over the lower ground service volume. This is not another floor.
parts.append(loft(rect(680,740,1065,1180),Z0-.05,lambda x,y:Z(max(.2,.8*(x/PX+2000-680)/(1065-680)))))
parts.append(loft(rect(680,1390,1065,1890),Z0-.05,lambda x,y:Z(max(.2,4.2*(x/PX+2000-680)/(1065-680)))))
# Continuous glazing, with shallow recesses and fine frames fused to backing.
# Grass facade: top follows the actual lower diagonal of the opaque folded plate.
cuts.append(facade_yz([(1300,4.4),(1745,4.4),(1745,10.0),(1350,6.1),(1300,5.1)],1040,2.16,0))
for y in np.linspace(1320,1720,11):
 top=5.1+(y-1300)*(4.9/445)
 late.append(poly(rect(1069,y-8,1084,y+8),Z(4.4),(top-4.4)*UNIT))
for x in np.linspace(1135,2190,12):cutbox(x-28,815,x+28,855,4.8,4.0)
# Field-side long white-fold horizontal slot and lower curtain band.
cutbox(1615,2040,2385,2110,6.0,2.2)
cutbox(1300,2040,2400,2110,.55,2.1)
for x in np.linspace(1640,2360,13):late.append(poly(rect(x-8,2038,x+8,2049),Z(6.0),2.2*UNIT))
for x in np.linspace(1320,1870,10):late.append(poly(rect(x-8,2038,x+8,2049),Z(.55),2.1*UNIT))
# Right two-storey curtain wall; diagonal top stops below the white end fold.
glass=[(2470,.55),(3220,.55),(3220,1.90),(2990,8.15),(2470,8.15)]
cuts.append(facade_xz(glass,1970,7.2,0))
for x in np.linspace(2490,3200,15):
 top=min(8.15,1.90+(3220-x)*(6.25/230))
 late.append(poly(rect(x-8,1968,x+8,1979),Z(.55),(top-.55)*UNIT))
late.append(poly(rect(2470,1968,3120,1979),Z(4.15),.85))
# Pond side upper/lower groups only where visible, not mirrored facade geometry.
for x in np.linspace(2505,3200,9):
 for z in [.65,5.1]:cutbox(x-30,1600,x+30,1650,z,2.25)
for y in np.linspace(965,1570,9):
 for z in [.6,5.0]:
  if not (y>1370 and z>4):cutbox(2405,y-25,2475,y+25,z,2.3)
# Open undercroft slots in the foyer ground-level passage.
cutbox(1930,1920,2410,2090,.15,3.7)
for x in [2010,2280]:late.append(poly(rect(x-14,1930,x+14,1965),Z(-.05),4.25*UNIT))
# Two exterior stair flights, backed as stepped solids; delicate handrails omitted.
def stair(x0,y0,x1,y1,zrise,n=12):
 dx=x1-x0;dy=y1-y0;lp=(dx*dx+dy*dy)**.5;length=lp*PX;width=80*PX
 profile=[(0,Z(-.05)),(length,Z(-.05)),(length,Z(zrise))]
 for i in range(n-1,-1,-1):
  profile.append((length*i/n,Z(zrise*(i+1)/n)))
  if i:profile.append((length*i/n,Z(zrise*i/n)))
 q=cs(profile).extrude(width);xx,yy=xy((x0,y0));ux=dx/lp;uy=-dy/lp;vx=-uy;vy=ux
 late.append(q.transform(np.array([[ux,0,vx,xx-vx*width/2],[uy,0,vy,yy-vy*width/2],[0,1,0,0]],dtype=float)))
stair(990,2170,1160,1860,4.2,14)
stair(3340,2145,3070,1990,4.2,12)
# Foyer visible interior stair backed to side wall, no floating fine treads.
stair(2230,1905,2230,1780,4.2,10)
# Three low landscape terraces on the field side, clear of the doorway.
for j in range(3):addbox(1250,2100+j*70,3310,2140+j*70,-.05,.75-.2*j)
for j in range(3):addbox(1980,2050+j*80,2130,2135+j*80,-.05,.80-.2*j)
late.append(poly(rect(1880,2040,2460,2135),Z(-.05),.85*UNIT))
solid=parts[0]
for p in parts[1:]:solid+=p
for c in cuts:solid-=c
for p in late:solid+=p
# Finite high-corner plateau: remove the last 0.20m of a mathematical sharp tip.
solid-=boxmm(0,0,Z(17.8),200,160,10)
print('components',[(s.volume(),s.bounding_box()) for s in solid.decompose()]);assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True);mesh.export(R/'model.stl');print(mesh.extents,mesh.is_watertight)
