"""Directed checks for historically detected artificial construction microlips."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);S=2.5
rows=[]
def add(n,p,w):rows.append(dict(name=n,point_design=p,expected_solid=w))
# Keep exact formerly reported microface centroid coordinates, not new convenient samples.
add('former_ramp_end_microface_centroid_removed',[-12.5,-4.333372497558594,3.7999348958333337],False)
add('former_rail_post_microface_centroid_removed',[-16.642750549316407,-5.120078150431315,3.9924395243326822],False)
q=lambda x:round(x*1024)/1024
for x in [-12.7,-12.6,-12.51,-12.5,-12.49,-12.4]:
 top=q(3.8) if x>=-12.65 else q(1.88)+(x+28.5)/16*(q(3.8)-q(1.88))
 for y in [-5,-4.6,-4.15]:
  add('upper_ramp_landing_common_plane_floor',[x,y,top-.03],True);add('upper_ramp_landing_common_plane_head',[x,y,top+.03],False)
for x in [-22,-19,-17,-16.642750549316407,-14]:
 z=q(1.88+.75)+(x+28.5)/16*(q(3.8+.75)-q(1.88+.75))
 for dz in [-.035,0,.035]:
  add('rail_inner_side_same_post_plane_inside',[x,q(-5.12)-.01,z+dz],True)
  add('rail_inner_side_same_post_plane_outside',[x,q(-5.12)+.01,z+dz],False)
pts=np.asarray([r['point_design'] for r in rows])*S;got=m.contains(pts);fail=[]
for r,g in zip(rows,got):
 r['actual_solid']=bool(g)
 if r['expected_solid']!=g:fail.append(r)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),sample_count=len(rows),failed=fail,samples=rows,limits='Two historically artificial interface microfaces removed by generator co-registration, not removal of raw mesh faces; no global thickness guarantee.')
(A/'qa/interface-microlip-validation.json').write_text(json.dumps(report,indent=2));print('interface samples',len(rows),'failed',len(fail));assert not fail,fail
