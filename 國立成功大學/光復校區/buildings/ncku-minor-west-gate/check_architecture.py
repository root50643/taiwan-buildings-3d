"""Raw STL sections verify asymmetric facade and hip-and-gable topology."""
from pathlib import Path
import json,hashlib,numpy as np,manifold3d as md
from shapely.geometry import Polygon,Point,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
def section(z):
 g=GeometryCollection()
 for p in m.slice(z).to_polygons():g=g.symmetric_difference(Polygon(p))
 return g
s=section(72)
assert not s.contains(Point(0,-9)) and s.contains(Point(0,24))
assert not s.contains(Point(18,-9)) and not s.contains(Point(-18,-9))
assert s.contains(Point(40,8)) and s.contains(Point(-40,8))
assert not s.contains(Point(40,-15))
assert not section(20).contains(Point(0,0)) and section(46).contains(Point(0,0))
lo=section(90).bounds;hi=section(100).bounds
assert lo[2]>33 and lo[0]<-33 and 27<hi[2]<29 and -29<hi[0]<-27
r=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Unhealed STL horizontal sections + exact point occupancy',front_door_and_two_windows_recessed=True,rear_upper_wall_continuous=True,annexes_rearward_front_platform_clear=True,arched_tunnel_clear_below_and_solid_above=True,lower_hip_section_z90_bounds=lo,upper_gable_section_z100_bounds=hi,estimated_not_measured=True)
(A/'qa/architecture-sections.json').write_text(json.dumps(r,indent=2)+'\n')
