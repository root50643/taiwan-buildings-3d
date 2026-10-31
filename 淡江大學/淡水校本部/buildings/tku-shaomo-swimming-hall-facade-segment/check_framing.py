"""Quantitative orthographic framing of actual mesh; 1200x900 aspect ratio."""
from pathlib import Path
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent
v=np.load(p/'mesh-data.npz')['vertices'];views=json.loads((p/'render-manifest.json').read_text())['views'];rows=[]
for q in views:
 loc=np.array(q['camera'],float);target=np.array(q['target'],float);forward=target-loc;forward/=np.linalg.norm(forward)
 ref=np.array([0,0,1.])
 if abs(forward@ref)>.99:ref=np.array([0,1.,0])
 right=np.cross(forward,ref);right/=np.linalg.norm(right);up=np.cross(right,forward);z=v-target
 xy=np.column_stack((.5+z@right/q['ortho_scale'],.5+z@up/(q['ortho_scale']*.75)))
 bounds=[*xy.min(axis=0).tolist(),*xy.max(axis=0).tolist()];margin=float(min(xy.min(),1-xy.max()));detail=q['name']=='entry_detail';rows.append({'view':q['name'],'normalized_bounds':bounds,'minimum_margin_fraction':margin,'required_margin':None if detail else .01,'passed':True if detail else margin>=.01,'scope':'detail allowed crop' if detail else 'whole retained facade including base'})
r={'passed':all(q['passed']for q in rows),'image_size':[1200,900],'mesh_sha256':hashlib.sha256((p/'mesh-data.npz').read_bytes()).hexdigest(),'views':rows};(p/'FRAMING-QA.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['passed']
