"""Original triangles: local backed relief and entry-corner axis first segments.
The first segment ends at the first air crossing; never sums later walls.
"""
from pathlib import Path
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent
exec((R/'check_local_corner_profiles.py').read_text().split('OLD=T.copy();result=')[0])
rows=[]
for fi,weights in [(16042,[.2,.6,.2]),(14622,[.6,.2,.2]),(62655,[1/3]*3),(3549,[1/3]*3)]:
 t=T[fi];p=np.array(weights)@t;inside=p-norm[fi]*1e-5;roots=[]
 for d in [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]:
  h=hits(inside,np.array(d));roots.append({'direction':d,'first_contiguous_exit_mm':h[0][0] if h else None,'all_intersections':h})
 rows.append({'face':fi,'surface_point_mm':p.tolist(),'inside_point_mm':inside.tolist(),'normal':norm[fi].tolist(),'axis_first_segments':roots})
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'samples':rows,'limitations':'Nominated original facets and axes only. A backed shallow relief can have a short side chord while a perpendicular back direction enters the wall; both are reported. Not an all-direction minimum wall guarantee.'}
(R/'local-back-roots.json').write_text(json.dumps(report,indent=2));print('local back root evidence written')
