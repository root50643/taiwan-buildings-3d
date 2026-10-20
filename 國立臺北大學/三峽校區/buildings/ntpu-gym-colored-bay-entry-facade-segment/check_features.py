"""Coordinate-registered local occupancy and exposed-detail erosion tests."""
from pathlib import Path
import json,numpy as np
from shapely.geometry import Polygon,Point,box
from qa_model import raw_read
from manifold3d import Manifold,Mesh
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=Manifold(Mesh(v.astype(np.float32),f.astype(np.uint32)))
def section(z):
 g=Polygon()
 for c in m.slice(z).to_polygons():g=g.symmetric_difference(Polygon(c))
 return g
checks=[]
def test(label,x,y,z,expected):
 got=section(z).covers(Point(x,y));checks.append({'feature':label,'xyz_mm':[x,y,z],'solid_expected':expected,'solid_actual':got,'pass':got==expected});assert got==expected,label
test('blue deep projection',52,-9,32,True)
test('blue front recessed glazing pocket',63,-10.7,33,False)
test('blue glazing backed not transparent',63,-9.5,33,True)
test('blue right glazed return recess',78.8,-2,33,False)
test('yellow independent shallower projection',146,-6,30,True)
test('yellow recessed pane',152,-7.8,30,False)
test('red entrance frame',112,-5,21,True)
test('red recessed pane',119,-5.8,21,False)
test('upper beam true sky slot',105,4,46,False)
test('upper beam material',105,4,49,True)
test('left balcony true recess',9,0,24,False)
test('ground floor recessed arcade',26,0,8,False)
test('upper vertical narrow glazing recess',89,1,32,False)
test('plain cut back not authentic exterior',100,7,32,True)
# Local footprint, unlike whole-component survival, isolates small raised mullions.
local=[]
for label,z,rect in [('blue_front_mullion',33,(63.375,-10.56,64.125,-9.72)),('blue_frame_left',33,(49,-11,59.4,-9.7)),('sky_beam',49,(100,1.5,110,5.5)),('left_balcony_rail',30,(2,-3.6,16,-2.4))]:
 g=section(z).intersection(box(*rect));e=g.buffer(-.4);local.append({'feature':label,'z_mm':z,'clip_mm':rect,'area_mm2':g.area,'survives_0_8mm_local_erosion':not e.is_empty,'eroded_area_mm2':e.area})
assert all(x['area_mm2']>0 for x in local)
(A/'qa/local-features.json').write_text(json.dumps({'occupancy':checks,'local_erosion':local,'warning':'Local loss is reported, not excused by whole-component survival. 0.75mm mullions may merge or vanish in FFF. No slicer or physical test.'},indent=2)+'\n')
print(json.dumps(local))
