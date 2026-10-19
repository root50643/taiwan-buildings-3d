"""Preserve the fixed original A1 STL; partition only its existing material volume.
All dimensions and selectors are in millimeters. Edit semantic selectors here;
geometry is never regenerated from photos or the old parametric source.
Run with Python + numpy/trimesh/manifold3d; see requirements.txt.
"""
from pathlib import Path
import json, hashlib, itertools
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64, OpType

P=Path(__file__).resolve().parents[2]
OUT=P/'multicolor'
OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
if sha((P/'model.stl').read_bytes())!='f25654284af62f9f454421da0dbb1a21bcd9b0645bbfc7c6deb2df3f327f0023':
    raise RuntimeError('The fixed original STL changed; refuse to partition another geometry.')
src=trimesh.load(P/'model.stl',force='mesh',process=True)
A=Manifold(Mesh64(np.asarray(src.vertices),np.asarray(src.faces,dtype=np.uint64)))
assert A.status().name=='NoError'
def box(x0,x1,y0,y1,z0,z1):
    # Match the source STL coordinate precision before CSG. This avoids tiny
    # material-only slivers between decimal selectors and existing f32 edges.
    x0,x1,y0,y1,z0,z1=map(lambda v:float(np.float32(v)),(x0,x1,y0,y1,z0,z1))
    return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def union(ms):return Manifold.batch_boolean(ms,OpType.Add) if ms else Manifold()
def f(x):return float(np.float32(x))
roles={k:[] for k in ['roof','pv','dark_facade','plinth','brick','glass','light_frames']}
def add(role,*coords):roles[role].append(box(*coords))
def grow(shape,margin=.02):
    v=np.asarray(shape.to_mesh64().vert_properties)[:,:3]
    offsets=np.asarray(list(itertools.product([-margin,margin],repeat=3)))
    return Manifold.hull_points((v[:,None,:]+offsets[None,:,:]).reshape(-1,3))
def gable(x,y,z,w,d,r,axis='y'):
    pts=[[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]
    pts+=([[x,y-d/2,z+r],[x,y+d/2,z+r]] if axis=='y' else [[x-w/2,y,z+r],[x+w/2,y,z+r]])
    roles['roof'].append(grow(Manifold.hull_points(pts)))
def hip(x,y,z,w,d,r):
    roles['roof'].append(grow(Manifold.hull_points([[x+sx*w/2,y+sy*d/2,z] for sx in [-1,1] for sy in [-1,1]]+[[x,y,z+r]])))
# Broad bounded selectors: split through interior, not nearly-coincident source solids.
for x in [-52.5,52.5]:
    gable(x,10,45,28.4,77,4.5)
    hip(x,-59,34,27.5,19,3)
    add('roof',x-14.4,x+14.4,-28.7,48.7,44.8,45.5)
    for yy in [-10,25]:
        roles['roof'].append(grow(box(x-4.5,x+4.5,yy-9.5,yy+9.5,48.5,50.1)))
        gable(x,yy,50,10,20,1.6)
    for xx in [x-8,x+8]:roles['pv'].append(grow(box(xx-4,xx+4,-23.5,43.5,47.2,48)))
    add('dark_facade',x-13.8,x+13.8,-69,-49.7,2.8,16.7)
    add('dark_facade',x-7.1,x+7.1,-69.2,-67.4,17.0,18.4)
    add('brick',x-13.8,x+13.8,-69,-49.7,16.7,21.0)
gable(0,51,46,133.4,26.4,4,'x')
add('roof',-66.9,66.9,37.6,64.4,45.8,46.5)
for x in [-35,35]:
    roles['roof'].append(grow(box(x-13.5,x+13.5,47.5,54.5,49.4,51.2)))
    gable(x,51,51,28,8,1.4,'x')
    roles['pv'].append(grow(box(x-15.5,x+15.5,41.2,48.2,48.5,49.4)))
roles['roof'].append(grow(box(-8,8,36.3,63.3,46,51)))
gable(0,49.8,50.8,17,28,2,'x')
for x in [-61,61]:hip(x,54,54,10,10,3.1)
gable(-9,-54,30,42,26,5,'x')
hip(15,-51,37,9,9,2.4)
for x,w in [(-36,12),(36,33)]:gable(x,-50,7.1,w+1,5,1,'x')
add('plinth',-80,80,-80,80,-1,3.0)
# Inner U facades: broad red lower wall fields interrupted by grey structural bands.
for side in [-1,1]:
    x=side*39
    lo,hi=(x-1.5,x+.1) if side<0 else (x-.1,x+1.5)
    add('brick',lo,hi,-31.7,37.5,3.0,30.0)
    for y in np.arange(-32.5,39,7):add('dark_facade',lo-.1,hi+.1,y-.8,y+.8,3.0,44.6)
    for z in [11.0,18.5,26.0]:add('dark_facade',lo-.1,hi+.1,-32,38,z,z+2.2)
# Rear wing courtyard face and central projection.
add('brick',-59,59,38.0,39.8,3.0,31.0)
for x in np.arange(-60.5,62,7):add('dark_facade',x-.8,x+.8,37.9,40.0,3.0,44.7)
for z in [12.0,19.5,27.0]:add('dark_facade',-60,60,37.9,40.0,z,z+2.2)
add('dark_facade',-21.6,21.6,25.0,40.1,3.0,15.2)
add('brick',-21.6,21.6,25.0,28.9,15.2,21.8)
# Offset front block: source-visible brick infill fields on the right, light entry on left.
for z in [4.2,11.2,18.2]:add('brick',-5.6,11.1,-66.2,-64.4,z,z+5.8)
for x in [-5.5,0,5.5,11.0]:add('dark_facade',x-.6,x+.6,-66.3,-64.2,3.0,29.6)
add('dark_facade',11.1,19.1,-61.5,-59.6,3.0,33.0)

# Green glazing inserts extend >=0.9 mm behind the existing 0.6mm shallow window recess.
# Their aperture edges are read at the same float32 positions as the original STL.
def wy(xs,y,zs,w=3.3,h=3):
    for x in xs:
        for z in zs:add('glass',f(x-w/2),f(x+w/2),y-1.5,y+1.5,f(z),f(z+h))
def wx(x,ys,zs,w=3.3,h=3):
    for y in ys:
        for z in zs:add('glass',x-1.5,x+1.5,f(y-w/2),f(y+w/2),f(z),f(z+h))
for x in [-52.5,52.5]:
    for dx in [-4,0,4]:add('light_frames',f(x+dx-.45),f(x+dx+.45),-69,-66.1,4.8,17.0)
    for z0,z1 in [(8.075,8.925),(9.75,10.65),(11.775,12.625)]:add('light_frames',f(x-6.2),f(x+6.2),-69,-66.1,f(z0),f(z1))
    for xx in [x-13.5,x+13.5]:wx(xx,np.arange(-29,36,7),[7,14.5,22,29.5,37],4.2,3.6)
    wy([x-5,x,x+5],-68,[20,27],3.4,4)
    # Large front panes: leave the original 0.85/0.9mm mullions as wall material.
    spans=[(-6,-4.45),(-3.55,-.45),(.45,3.55),(4.45,6)]
    zs=[(5,8.075),(8.925,9.75),(10.65,11.775),(12.625,16.5)]
    for a,b in spans:
        for z0,z1 in zs:add('glass',f(x+a),f(x+b),-69,-66.1,f(z0),f(z1))
wy(np.arange(-57,61,7),64,[8,15.5,23,30.5,38],4.2,3.6)
wy([-33,-26,26,33],38.5,[8,15.5,23,30.5,38],4.2,3.6)
wy([-19,-12,-5,2,9,16],38.5,[38],4.2,3.6)
wy([-17,-12,12,17],28,[11,18,25],2.5,3.8)
wy([-5,0,5],26,[8,16,22],3.2,3.3)
wy(np.arange(-25,10,5.5),-66,[6,13,21],3.2,3.8)
wy(np.arange(-25,10,5.5),-42,[7,14,22],3.2,3.8)
# The narrow tower glazing has existing crossbars; keep those uncoloured.
for z0,z1 in [(5,9),(9.9,16),(16.9,23),(23.9,29)]:add('glass',f(13),f(17),-62,-59.5,f(z0),f(z1))
for z in [9,16,23]:add('light_frames',f(12.9),f(17.1),-62,-59.5,f(z),f(z+.85))

masks={k:union(v) for k,v in roles.items()}
remaining=A
fine={}
toolmap={'light_frames':1,'glass':4,'pv':3,'roof':3,'dark_facade':3,'plinth':3,'brick':2,'wall':1}
for name in ['light_frames','glass','pv','roof','dark_facade','plinth','brick']:
    mask=masks[name]
    fine[name]=remaining^mask
    remaining=remaining-mask
fine['wall']=remaining
names={1:'01-light-wall',2:'02-brick',3:'03-slate',4:'04-glazing'}
groups={names[k]:union([v for n,v in fine.items() if toolmap[n]==k]) for k in names}
def tm(m):
    a=m.to_mesh64();return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=False)
(OUT/'qa').mkdir(exist_ok=True)
report={'source_sha256':sha((P/'model.stl').read_bytes()),'source_volume_mm3':A.volume(),'source_bounds':src.bounds.tolist(),'parts':{},'overlap_mm3':{}}
report['fine_parts']={}
for name,m in fine.items():
    t=tm(m); comps=m.decompose()
    report['fine_parts'][name]={'tool':toolmap[name],'volume':m.volume(),'closed':bool(t.is_watertight),'components':len(comps),'min_component_volume':min(c.volume() for c in comps),'min_bbox_dimension_mm':min(float(tm(c).extents.min()) for c in comps)}
    print('FINE',name,report['fine_parts'][name],flush=True)
for name,m in groups.items():
    a=tm(m);cs=m.decompose();vols=sorted(c.volume() for c in cs)
    report['parts'][name]={'status':m.status().name,'volume_mm3':m.volume(),'facets':len(a.faces),'watertight':bool(a.is_watertight),'winding_consistent':bool(a.is_winding_consistent),'components':len(cs),'smallest_component_mm3':vols[:15],'bounds':a.bounds.tolist(),'small_components':[{'volume':c.volume(),'bounds':tm(c).bounds.tolist(),'extents':tm(c).extents.tolist()} for c in cs if c.volume()<2]}
    print(name,report['parts'][name],flush=True)
for (an,a),(bn,b) in itertools.combinations(groups.items(),2):report['overlap_mm3'][an+'__'+bn]=(a^b).volume()
u=union(list(groups.values()))
report['union_missing_mm3']=(A-u).volume();report['union_extra_mm3']=(u-A).volume();report['volume_sum_error_mm3']=sum(m.volume() for m in groups.values())-A.volume()
report['union_bounds']=tm(u).bounds.tolist()
(OUT/'qa'/'partition-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')

from three_mf_io import write_outputs
manifest=write_outputs(OUT,fine,toolmap,groups,A,report,{k:len(v) for k,v in roles.items()})
print(json.dumps(report,indent=2),flush=True)
