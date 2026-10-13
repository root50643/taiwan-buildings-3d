"""國立澎湖科技大學圖書資訊大樓圓弧入口前段。自建照片近似，毫米。
只製作有實拍及樓層圖支持的圓弧前段；y=0是人为截斷面，不是實際背立面。
Python + manifold3d boolean solids; no downloaded mesh.
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from manifold3d import Manifold
OUT=Path(__file__).resolve().parent
R=54; SEG=144

def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def cyl(r,z,h):return Manifold.cylinder(h,r,r,circular_segments=SEG).translate((0,0,z))
def half(s):return s ^ box(0,-75,0,200,150,160) # y <= 0, explicit crop plane

def radial_box(a,r,z,w,d,h):
 # Local x is tangential; local y runs radial inward at front azimuth -90.
 return box(0,-r,z,w,d,h).rotate((0,0,a+90))

parts=[box(0,-25,0,150,90,3)]
# Main curved drum; lower ground/first-level arcade is recessed 17 mm.
parts += [half(cyl(37,2.8,44.2)),half(cyl(R,46.5,53.5))]
# Solid rear cut face: explicitly a crop, no inferred side wings or unseen windows.
parts += [box(0,-2,2.8,108,4,97.2)]
# Curved two-level floor slab and upper continuous floor/awning line.
parts += [half(cyl(R,22.5,2.5)),half(cyl(R+1.4,45,2.4))]
# Six front piers, one per 30-degree bay boundary, matching ring plan.
for a in [-165,-135,-105,-75,-45,-15]:
 parts.append(radial_box(a,50,2.8,10.8,8.4,44.5))
 # Substantial base and capital, fused, never separate trim fragments.
 parts.append(radial_box(a,50,2.8,11.6,9.2,8.5))
# No invented end piers: the rear cut plane is at the diameter, y=0.
# Open upper crown is a hollow ring above a recessed roof, not an invented atrium.
parts.append(half(cyl(R,99.5,20.5)-cyl(R-4.0,99.4,21)))
parts.append(half(cyl(R+1.4,119,3)-cyl(R-4.0,118.9,3.3)))
# Light wall belt between the two glazed window rows.
parts.append(half(cyl(R+.65,71.8,1.5)))
solid=parts[0]
for p in parts[1:]:solid=solid+p
# Seven visible front arc window centers; ends are partial bays at crop.
# Photos: two glazed rows; roof crown is open sky and has NO fabricated glazing.
for a in [-180,-150,-120,-90,-60,-30,0]:
 for z in [52,76]:
  # Shallow recess represents glazing; minimum backing is large solid mass.
  solid-=radial_box(a,53.8,z,12.5,4.6,13.2)
  # robust mullion relief inside recess, backed and connected at each end.
  solid+=radial_box(a,51.3,z-.3,1.2,4.0,13.8)
  solid+=radial_box(a,51.3,z+6.1,14.5,4.0,1.2)
 # crown openings are full depth, preserving the open upper ring.
 solid-=radial_box(a,52,103,12.5,12,13)
# Recessed entrance doors on the curved core, visible behind piers.
for a in [-150,-120,-90,-60,-30]:
 solid-=radial_box(a,36.9,5,9.5,2.5,14.5)
# All details clipped at the declared rear plane. Base retained.
solid=half(solid)+box(0,-25,0,150,90,3)
assert len(solid.decompose())==1
m=solid.simplify(.000001).to_mesh64()
mesh=trimesh.Trimesh(np.asarray(m.vert_properties,dtype=np.float32)[:,:3],np.asarray(m.tri_verts),process=True)
mesh.export(OUT/'model.stl')
print(mesh.extents,mesh.is_watertight,len(mesh.faces))
