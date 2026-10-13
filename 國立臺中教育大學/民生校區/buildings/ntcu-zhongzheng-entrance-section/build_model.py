"""NTCU Zhong-zheng Building entrance SECTION. mm; arbitrary rear cutoff.
Two actual tall main columns, three recessed glass bays, continuous clerestory band.
"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent;parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
add(0,0,0,150,68,3)
add(0,2,2.8,138,52,74.2)
# Deep central portico removed from front volume: true empty space below overhang.
cut(0,-18,5,76,40,53)
# Lower porch platform and descending steps.
add(0,-19,2.8,78,23,2.2)
for i in range(3):add(0,-31+i*1.25,2.8,79,2.5,.6*(i+1))
# Two primary rectangular columns. Three glass bays sit behind these, not extra columns.
for x in [-19,19]:
 details.append(box(x,-20.5,4.8,3.8,5.4,53.5))
 details.append(box(x,-23.2,4.8,1.2,1.0,53.5))
# Entrance glazing is a real recessed wall at y=2, with robust surface mullions.
cut(0,1.9,5.1,74,1.8,28.7)
for x in [-36,-28,-19,-9.5,0,9.5,19,28,36]:details.append(box(x,2.2,5.1,1.2,3.0,28.8))
for z in [12,21,28]:details.append(box(0,2.2,z,75,3.0,1.15))
# Dark upper glazing above inscription band, still on rear recess plane.
cut(0,1.9,44,74,1.8,12.7)
for x in np.arange(-35,36,7):details.append(box(float(x),2.2,44,1.1,3.0,12.7))
# Sign-bearing balcony/parapet spans full recess and joins both side walls.
details.append(box(0,-1.0,34,77,7.0,10.3))
# Fine gold lettering deliberately omitted, avoiding invented text geometry.
# Cantilever upper storey wrapping facade and sides. Continuous glass ribbon is recessed.
add(0,1.0,57.5,143,55,4.0)
add(0,1.0,61.2,143,55,14.2) # full continuous backing for flat clerestory band
cut(0,-26.4,64,140,.8,10.0)
for x in np.arange(-68,69,5.8):details.append(box(float(x),-26.0,63.9,1.1,.8,10.2))
details.append(box(0,-26.0,68.5,142,.8,1.0))
# Side ribbon only over evidence-backed near-front portion; back cut is plain.
for x in [-71.4,71.4]:
 cut(x,-8.0,64,.8,33,10)
 for y in np.arange(-22,7,5.8):details.append(box(x+(.4 if x<0 else -.4),float(y),63.9,.8,1.1,10.2))
 details.append(box(x+(.4 if x<0 else -.4),-8,68.5,.8,34.2,1.0))
# Top parapet/cutoff slab; full auditorium roof behind it is outside this section.
add(0,1,75,143,55,2.2)
solid=parts[0]
for a in parts[1:]:solid=solid+a
for a in cuts:solid=solid-a
for a in details:solid=solid+a
assert len(solid.decompose())==1
m=solid.simplify(.00001).to_mesh64();mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl');mesh.export(OUT/'model.obj');print(mesh.extents,mesh.is_watertight,len(mesh.faces))
