"""玄奘圖資有界研究草稿，未核外觀/未完成QA。尺寸為NLSC屋頂投影初描，高度照片推估。"""
from pathlib import Path
import numpy as np,trimesh
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).parent;S=1.15;B=1.6;parts=[];cuts=[]
def box(x0,y0,x1,y1,z0,z1):return Manifold.cube(((x1-x0)*S,(y1-y0)*S,(z1-z0)*S)).translate((x0*S,y0*S,B+z0*S))
def add(*a):parts.append(box(*a))
def cut(*a):cuts.append(box(*a))
parts.append(Manifold.cube((150,140,B)).translate((-75,-70,0)))
# Local front faces -Y; roof projection 119m crossbar, 40m wide long stem.
# Feet are conservative insets; no measured wallbase or uniform exposed B1/B2 claim.
add(-57.8,-49,57.8,-34,-.03,27)
add(-18.6,-35,18.6,47,-.03,27)
# Visible low inner return roof; height is bounded hypothesis, not a measured storey.
add(19,-34,50,-17,-.03,9)
add(19,-18,24,12,-.03,9)
# Graded scene ground along library forecourt, not campus terrain survey.
add(-61,-54,38,-48,-.03,4.0)
pad=CrossSection([[(37.8*S,B-.03*S),(61*S,B-.03*S),(61*S,B+.25*S),(37.8*S,B+4*S)]]).extrude(6*S).transform(np.array([[1,0,0,0],[0,0,-1,-48*S],[0,1,0,0]],float));parts.append(pad)
# Broad five-row front facade, upper tall windows and lower shorter belt.
# Bay count initial photo reading; grouping awaits source overlay review.
for x in np.linspace(-55.8,55.8,28):
 for lo,hi in [(5.4,7.5),(9.4,12.9),(13.7,17.2),(18,21.5),(22.3,25.8)]:
  cut(x-1.65,-49.3,x+1.65,-48.88,lo,hi)
for z in [8.1,12.7,17.3,21.9,26.4]:add(-57.75,-49.04,57.75,-48.8,z,z+.24)
for x in np.linspace(-57.85,57.85,29):add(max(-57.75,x-.48),-49.12,min(57.75,x+.48),-48.8,-.02,26.9)
# Long side source has tall narrow openings, lower short openings, not front mirror.
# Candidate low-slope P2 end of crossbar: four tall + two short tiers.
for x in np.linspace(43.4,55.8,4):cut(x-1.5,-49.3,x+1.5,-48.88,2.6,4.0)
cut(57.4,-46.5,58.1,-36.0,.15,2.25)
# Side window arrays omitted until photograph-to-wing identity is independently closed.
# Rear end hidden by woodland: deliberately only mass, no invented window array.
# Original wide overhanging roof, separate from post-2022 solar canopy.
add(-59.5,-50,59.5,-32,26.7,27.6)
add(-20,-33,20,49,26.7,27.6)
# Solar shelter simplified as backed broad planes with shallow lane divisions.
add(-59,-49.5,59,-32.5,27.5,29.5)
for xa,xb in [(-19.5,-8),(-6.8,6.8),(8,19.5)]:add(xa,-32.8,xb,48.5,27.5,29.5)
# Finite central shallow skylight ridge discernible in official aerial.
p=[(-6*S,B+29.3*S),(6*S,B+29.3*S)]+[(6*S*np.cos(t),B+(29.3+1.8*np.sin(t))*S)for t in np.linspace(0,np.pi,33)]
barrel=CrossSection([p]).extrude(73*S).transform(np.array([[1,0,0,0],[0,0,-1,42*S],[0,1,0,0]],float))
parts.append(barrel)
add(-6,6,6,14,30,30.8)
# Rear roof stair/service mass, only observed large roof blocks.
add(-7,41,7,49,29.2,32)
add(-19,35,-14,43,29.3,30.5)
entry_start=len(parts)
# Main entrance porch above bounded +4m forecourt; exact terrain not measured.
# Main entrance porch: broad open opening, two large square stone piers.
add(4,-58,19,-48.5,-.03,4.3)
for x in [4.6,17.2]:add(x,-57.4,x+1.8,-48.5,4.1,13.0)
add(4.2,-57.5,19.4,-48.5,12.5,14)
# Rounded heavy cornice is backed to the porch, never an independent thin lip.
cap=Manifold.cylinder(15.2*S,1.05*S,1.05*S,32).rotate((0,90,0)).translate((4.2*S,-57.4*S,B+13.5*S))
parts.append(cap ^ box(3,-60,21,-48,8,14.2))
for i in range(4):add(3.7,-60+i*.6,19.8,-57.7,-.03,3.25+i*.28)
entry_parts=parts[entry_start:];parts=parts[:entry_start]
# Authored primitive grid before CSG; no exported STL repair.
def grid(p):
 m=p.to_mesh64();return Manifold(Mesh64(np.ascontiguousarray(np.round(m.vert_properties,4)),np.array(m.tri_verts,dtype=np.uint64,copy=True)))
solid=Manifold.batch_boolean([grid(p)for p in parts],OpType.Add)-Manifold.batch_boolean([grid(p)for p in cuts],OpType.Add)
solid+=Manifold.batch_boolean([grid(p)for p in entry_parts],OpType.Add)
assert solid.status().name=='NoError';m=solid.to_mesh64();mesh=trimesh.Trimesh(np.array(m.vert_properties[:,:3],dtype=np.float32),np.array(m.tri_verts),process=False);mesh.export(R/'model.stl');print(mesh.extents,len(mesh.faces),mesh.is_watertight,len(mesh.split(only_watertight=False)))
