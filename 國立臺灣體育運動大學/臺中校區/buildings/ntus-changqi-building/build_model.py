"""國立臺灣體育運動大學長啓樓，2017 竣工主體近似。
All source dimensions below are metres, transformed to millimetres once at export.
Original geometry only: no source photo, architectural CAD or third-party mesh embedded.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection
OUT=Path(__file__).resolve().parent
SCALE_MM_PER_M=150.0/68.0
BASE_M=1.2
parts=[];cuts=[];details=[];window_regions=[]
def box(x0,x1,y0,y1,z0,z1):
 assert x1>x0 and y1>y0 and z1>z0
 return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0+BASE_M))
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
def detail(*a):details.append(box(*a))
def north_window(cx,cy,z,w=1.65,h=2.25,depth=.52):
 cut(cx-w/2,cx+w/2,cy-.22,cy+depth,z,z+h);window_regions.append([cx-w/2,cx+w/2,cy-.22,cy+depth,z,z+h])
def south_window(cx,cy,z,w=1.65,h=2.25,depth=.52):
 cut(cx-w/2,cx+w/2,cy-depth,cy+.22,z,z+h);window_regions.append([cx-w/2,cx+w/2,cy-depth,cy+.22,z,z+h])
def west_window(cx,cy,z,w=1.65,h=2.25,depth=.52):
 cut(cx-.22,cx+depth,cy-w/2,cy+w/2,z,z+h);window_regions.append([cx-.22,cx+depth,cy-w/2,cy+w/2,z,z+h])
def east_window(cx,cy,z,w=1.65,h=2.25,depth=.52):
 cut(cx-depth,cx+.22,cy-w/2,cy+w/2,z,z+h);window_regions.append([cx-depth,cx+.22,cy-w/2,cy+w/2,z,z+h])
# Base: 150 x 92.647 mm. Front street facade is the -X elevation.
parts.append(Manifold.cube((68,42,BASE_M+.015)).translate((-4,-8,0)))
# Main six-floor laboratory, corridor and projecting stair/service towers.
add(0,19.7,0,23.0,-.01,27.7)
add(11.7,19.7,-5.5,1.0,-.01,31.1)
add(5.5,19.7,22.0,30.5,-.01,31.1)
# North service core, visible small horizontal windows; lower than highest stair.
add(19.3,26.2,0,8.8,-.01,27.0)
# Lower five-floor wing. Large north-side external notch remains fully open.
add(19.3,57.0,10.5,30.5,-.01,21.4)
# Two-storey north library volume steps out underneath the upper facade.
add(26.2,56.2,8.4,10.6,-.01,8.8)
# Low-wing south projecting offices and eastern stair/end wall.
add(28.6,55.8,30.2,32.0,-.01,21.4)
add(55.4,60.0,17.8,30.5,-.01,25.7)
# Main classroom roof sits above its lower surrounding terraces (section/photos).
add(28.7,55.8,10.5,23.0,21.25,23.15)
# High roof terrace: rim kept above 0.8mm width, no later solar arrays.
for a in [(-.45,.30,-.35,23.35,26.85,28.15),(-.45,19.9,-.35,.35,26.85,28.15),(-.45,19.9,22.65,23.35,26.85,28.15),(19.1,19.9,.0,23.0,27.5,28.15)]:add(*a)
# Roof caps, each rooted to its full stair core; upper louver band is shallow relief.
add(11.25,20.15,-5.9,1.4,31.0,31.9)
add(5.05,20.15,21.6,30.9,31.0,31.9)
# Low roof cornices and robust parapets distinguish gray roof from terrace.
add(19.3,60.2,9.95,10.7,20.6,22.2)
add(28.0,56.0,31.45,32.3,20.55,22.1)
add(19.2,28.8,29.95,30.75,20.6,22.1)
add(59.4,60.25,17.5,30.8,25.05,26.25)
add(55.0,60.25,17.45,18.2,25.05,26.25)
add(55.0,60.25,30.1,30.85,25.05,26.25)
add(28.25,56.05,10.05,10.75,23.0,23.6)
add(28.25,56.05,22.65,23.35,23.0,23.6)
add(28.25,28.95,10.05,23.35,23.0,23.6)
add(55.3,56.05,10.05,23.35,23.0,23.6)
# Terrace boundaries and low relief planting beds: massing is intentional, no flora mesh.
add(20.3,27.5,11.25,22.4,21.35,21.65)
add(35.0,54.8,24.2,30.7,21.35,21.65)
add(.7,15.9,.8,21.9,27.65,27.85)
# North low terrace ledge over the library and visible substantial piers.
add(26.1,56.3,7.7,10.65,8.15,8.9)
# Five main window rows (2F-6F), six vertical bays on the street facade.
levels=[5.1,9.3,13.5,17.7,22.1]
for y in [2.0,5.8,9.6,13.4,17.2,21.0]:
 for z in levels:west_window(0,y,z,w=1.72,h=2.45)
 # Recessed long bay field gives the continuous structural pilaster rhythm.
 cut(-.23,.15,y-1.16,y+1.16,4.65,26.75)
 # Window heads/sills fused to wall, not freestanding thin frames.
 for z in levels:detail(-.20,.24,y-1.0,y+1.0,z-.42,z)
# Three north-side bays; only one exposed south-side bay beside wider stair tower.
for x in [1.9,5.6,9.3]:
 for z in levels:north_window(x,0,z,w=1.72,h=2.45)
 cut(x-1.16,x+1.16,-.23,.15,4.65,26.75)
for z in levels:south_window(2.4,23,z,w=1.72,h=2.45)
cut(1.24,3.56,22.85,23.23,4.65,26.75)
# Broad high rear ribbon just above the low roof, not a mirrored street facade.
east_window(19.7,14.8,24.5,w=12.2,h=1.2)
for y in [10,13,16,19]:detail(19.13,19.74,y-.25,y+.25,24.4,25.9)
# Library glazing at 1F and 2F: three major bays, with robust mullion relief.
for x in [33.0,43.0,52.0]:
 south_window(x,32.0,.75,w=7.3,h=2.75)
 south_window(x,32.0,5.15,w=7.3,h=1.7)
 north_window(x,8.4,.75,w=7.3,h=2.75)
 north_window(x,8.4,5.1,w=7.3,h=2.0)
 for dx in [-2.2,0,2.2]:
  detail(x+dx-.26,x+dx+.26,31.36,32.06,.75,3.50)
  detail(x+dx-.26,x+dx+.26,8.32,9.01,.75,3.50)
# South low wing: nine window columns, three principal rows; link ribbons to west.
for x in [30.35+2.96*i for i in range(9)]:
 cut(x-1.12,x+1.12,31.79,32.23,8.8,20.6)
 for z in [9.35,13.55,17.75]:south_window(x,32,z,w=1.67,h=2.1)
for z,h in [(.75,2.8),(5.1,1.8),(9.35,1.25),(13.55,1.25),(17.75,1.25)]:
 south_window(24.25,30.5,z,w=8.2,h=h)
 for xx in [21.5,24.25,27]:detail(xx-.25,xx+.25,29.84,30.57,z,z+h)
# North low wing is asymmetric: west half full windows, far-east service slots.
for i in range(10):
 x=27.3+2.87*i
 cut(x-1.1,x+1.1,10.27,10.66,8.9,20.6)
 for z in [9.35,13.55]:north_window(x,10.5,z,w=.66 if i>=7 else 1.65,h=2.1)
 if i<5:north_window(x,10.5,17.75,w=1.65,h=2.1)
# End stair has a plain end with narrow slots and broad south-facing windows.
for z in [.8,5.15,9.35,13.55,17.75,22.2]:east_window(60,22.4,z,w=.95,h=2.1)
for z in [5.15,9.35,13.55,17.75]:south_window(57.65,30.5,z,w=2.35,h=2.15)
# North service tower has six narrow horizontal windows. This is not a stair array.
for z in [.95,5.5,9.7,13.9,18.1,23.1]:north_window(22.9,0,z,w=3.1,h=.85)
# Distinct north and south recessed stair/green-wall slots and alternating landings.
# They are open facade recesses, not enclosed internal voids.
cut(13.3,18.6,-5.75,-3.55,4.8,27.0)
cut(8.5,17.0,28.55,30.75,4.8,27.0)
for i,z in enumerate([8.1,12.3,16.5,20.7]):
 # Deep external landings alternate left/right and overlap tower returns.
 x0,x1=(12.8,16.0) if i%2==0 else (12.8,19.0)
 detail(x0,x1,-6.05,-3.45,z,z+.65)
 x0,x1=(8.1,13.7) if i%2==0 else (11.8,17.4)
 detail(x0,x1,28.45,31.05,z,z+.65)
# Top hood spanning each recess and shallow reveal above, all thick rooted pieces.
detail(12.9,19.0,-6.0,-3.45,25.1,25.75)
detail(8.1,17.4,28.45,31.0,25.1,25.75)
cut(13.5,18.45,-5.74,-5.08,26.4,28.25)
cut(8.7,16.8,30.05,30.75,26.4,28.25)
# Roof louver recesses with >=1.2mm wide rooted ribs after scaling.
for cx in np.linspace(12.75,18.65,4):north_window(float(cx),-5.5,29.1,w=.85,h=1.7,depth=.35)
for cx in np.linspace(6.8,18.4,7):south_window(float(cx),30.5,29.1,w=1.05,h=1.7,depth=.35)
for cy in [23.3,25.2,27.1,29.0]:west_window(5.5,cy,29.1,w=1.0,h=1.7,depth=.35)
for cy in [-4.3,-2.4,-.5]:west_window(11.7,cy,29.1,w=1.0,h=1.7,depth=.35)
# Recessed front entrance plus the visibly projecting canopy. No fabricated portal.
cut(-.3,2.1,1.3,10.0,-.005,3.45)
add(-2.5,.45,.8,10.3,3.4,4.05)
# Ground-floor three narrow windows at the remaining street-front segment.
for y in [13.3,17.0,20.7]:west_window(0,y,.55,w=1.65,h=2.75)
# Small side entrance at the north stair and end stair.
north_window(15.65,-5.5,.1,w=2.0,h=2.9,depth=1.1)
east_window(60,23.1,.12,w=1.8,h=2.9,depth=1.05)
# Modest threshold pads, attached to base, not invented ground-floor interior.
detail(-2.0,2.5,1.0,10.1,-.01,.16)
detail(14.1,17.25,-6.6,-3.6,-.01,.16)
detail(58.5,61.3,21.7,24.5,-.01,.16)
# Original roof equipment reduced to two connected, robust clusters.
add(10.5,15.7,18.0,21.4,27.67,28.75)
add(29.5,34.1,25.0,28.5,21.36,22.35)
# Major geometry assembled by boolean union/difference, never repaired after export.
solid=parts[0]
for p in parts[1:]:solid=solid+p
for c in cuts:solid=solid-c
for p in details:solid=solid+p
assert len(solid.decompose())==1,'Disconnected original boolean result'
solid=solid.translate((-30,-13,0)).scale((SCALE_MM_PER_M,-SCALE_MM_PER_M,SCALE_MM_PER_M))
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(OUT/'model.stl')
(OUT/'preview-material-regions.json').write_text(json.dumps({'source_unit':'metres','note':'Preview colors only. Geometry remains the actual delivered STL; STL contains no colors.','windows':window_regions},ensure_ascii=False,indent=2))
params={'school':'國立臺灣體育運動大學','building':'長啓樓','period':'2017竣工原主體','unit':'mm','mm_per_source_metre':SCALE_MM_PER_M,'approximate_scale_denominator':1000/SCALE_MM_PER_M,'dimensions_mm':mesh.extents.tolist(),'levels_above_1F_m':[0,4.6,8.8,13.0,17.2,21.4,27.7,31.9],'height_datum_caveat':'31.9m為1F至最高屋突分段推算；3590總線含地下且與分段差60cm，未補造GL高差。','high_block_lab_structural_span_m':[5.5,6.2,5.0],'high_block_lab_length_m':23.0,'low_wing_roof_height_m':23.15,'estimated_parameters':'足跡轉折/低翼屋頂標高/梯間細部依建築圖與完工照近似，非測繪尺寸。','facade_window_counts':{'street':{'principal_rows':5,'columns':6},'south_low':{'principal_rows':3,'columns':9},'north_low':{'columns':10,'far_end_upper_blanks':5,'far_end_narrow_slots':3}},'original_faces':len(mesh.faces)}
(OUT/'model-parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2))
print(json.dumps(params,ensure_ascii=False))
