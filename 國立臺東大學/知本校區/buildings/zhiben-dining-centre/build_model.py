"""Public-exterior miniature in millimeters. Rebuild: python build_model.py.
Photo-interpreted, independent scale. No interior or security systems represented.
"""
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
OUT=Path(__file__).resolve().parent
parts=[];cuts=[];details=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def add(x,y,z,w,d,h):parts.append(box(x,y,z,w,d,h))
def detail(x,y,z,w,d,h):details.append(box(x,y,z,w,d,h))
def cut(x,y,z,w,d,h):cuts.append(box(x,y,z,w,d,h))
def poly(points,z,h):return CrossSection([points]).extrude(h).translate((0,0,z))
def yz(points,x,w):return CrossSection([points]).extrude(w).rotate((90,0,0)).rotate((0,0,90)).translate((x,0,0))
def roof(x,y,w,d,z,rise):
 add(x,y,z-.2,w,d,.75)
 parts.append(yz([(y-d/2,z),(y+d/2,z),(y,z+rise)],x-w/2,w))
def windows(x0,x1,y,zs,w=2.3,h=4.1,step=6):
 for x in np.arange(x0,x1+.01,step):
  for z in zs:cut(float(x),y,z,w,1.4,h)


def bar(p,q,r=.65):
 return Manifold.batch_hull([box(*p,2*r,2*r,2*r),box(*q,2*r,2*r,2*r)])
add(0,0,0,150,110,2.4)
# Independent dining-centre building next to second dorm, not dorm ground-floor wing.
add(0,0,2.3,126,76,22)
# Main roof is a low broad transverse barrel with clerestory along the top.
pts=[(-41,23.9),(41,23.9)]+[(float(41*np.cos(t)),float(24+9*np.sin(t))) for t in np.linspace(0,np.pi,41)]
parts.append(yz(pts,-66,132))
# Central raised strip seen in the school photograph and aerial.
add(0,0,30.4,105,15,9.7)
# Narrow clerestory panes simplified to shallow recesses.
for x in np.arange(-49,50,6):
 cut(float(x),-7.5,34.5,4,1.5,3.7)
 cut(float(x),7.5,34.5,4,1.5,3.7)
# Shallow curved floating cap, joined to clerestory, faceted for printing.
pts2=[(-13,39.5),(13,39.5)]+[(float(13*np.cos(t)),float(39.7+1.8*np.sin(t))) for t in np.linspace(0,np.pi,21)]
parts.append(yz(pts2,-55,110))
# Front glazed band under roof edge and substantial side piers.
for x in np.arange(-27,59,10):
 cut(float(x),-38,14.5,7.8,3.2,6.6)
 detail(float(x)-4.5,-38.2,3,1.5,1.7,20.8)
 # Tree-obscured lower frontage reduced to fewer simple exterior openings.
 cut(float(x),-38,4.5,6.5,2,6.4)
# Front left solid parapet block visible with the dining-centre sign, lettering omitted.
add(-52,-33,2.3,22,16,26)
# Entrance recess and low external platform, no interior arrangement.
cut(10,-38,2.4,19,5,12)
for i in range(3):add(10,-41.5-i*1.2,2.3,35,1.4,2.4-i*.6)
# Arc-shaped open recess below the exposed left roof edge, retained as a shallow exterior recess.
cut(-64,0,24,6,66,5.5)
for y in [-19,0,19]:cut(-63,y,15,2.2,13,6)
# Observed side upper window ribbon; unobserved rear kept plain.
for y in [-24,-12,0,12,24]:cut(63,y,15,1.8,8,6)
result=Manifold.batch_boolean(parts,OpType.Add)
if cuts:result=result-Manifold.batch_boolean(cuts,OpType.Add)
if details:result=result+Manifold.batch_boolean(details,OpType.Add)
assert result.status().name=='NoError'
m=result.to_mesh();mesh=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=True)
assert mesh.is_watertight and mesh.volume>0
mesh.export(OUT/'model.stl');print(OUT.name,mesh.extents,len(mesh.faces))
