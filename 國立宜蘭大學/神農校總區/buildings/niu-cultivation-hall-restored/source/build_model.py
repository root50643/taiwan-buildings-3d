"""Original parametric exterior approximation; no third-party mesh or image input."""
from pathlib import Path
import json, hashlib, time
import numpy as np
import manifold3d as mf
import trimesh

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'parameters.json').read_text(encoding='utf8'))
OUT=ROOT/'models/v1'
def box(lo,hi):return mf.Manifold.cube(np.subtract(hi,lo).tolist()).translate(lo)
def hull(points):return mf.Manifold.hull_points(np.array(points,dtype=np.float64))
def layers(rings):return hull([p for r in rings for p in r])
def rectring(x,y,z):return [[-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]]
def front_prism(poly,yfront,yback,bevel=0):
    zmax=max(z for x,z in poly)
    return hull([[x,yfront,z] for x,z in poly]+[[x,yback,z-min(bevel,max(0,z-(zmax-bevel)))] for x,z in poly])
def rect(x,z,w,h):return [[x-w/2,z],[x+w/2,z],[x+w/2,z+h],[x-w/2,z+h]]
def arch(x,z,w,h):
    r=w/2; spring=z+h-r
    return [[x-r,z],[x+r,z]]+[[x+r*np.cos(a),spring+r*np.sin(a)] for a in np.linspace(0,np.pi,17)]
def regular(cx,cz,r,n,angle=0):return [[cx+r*np.cos(a),cz+r*np.sin(a)] for a in np.linspace(angle,angle+2*np.pi,n,endpoint=False)]
def end_prism(poly,xfront,xback):return hull([[x,y,z] for x in [xfront,xback] for y,z in poly])
z0=P['main']['base_thickness']; wall=z0+P['main']['wall_height']; ew=z0+P['entry']['wall_height']
base=box([-83,-67,0],[83,44,z0])
body=box([-75,-37.5,z0],[75,37.5,wall])
entry=box([-24,-59.5,z0],[24,-37,ew])
# Bevelled undersides grow outward at 45 degrees; upper main surface has four hips.
roof=layers([rectring(75,37.5,wall-0.5),rectring(78,40.5,wall+2.5),[[x,y,wall+18] for x in [-37.5,37.5] for y in [-0.6,0.6]]])
# Solid front gable volume, with independent ridge that joins the main hip naturally.
entry_roof=layers([[[x,y,ew-0.4] for x in [-24,24] for y in [-59.5,-18]],[[x,y,ew+2] for x in [-26.4,26.4] for y in [-61.9,-18]],[[x,y,ew+14.6] for x in [-0.6,0.6] for y in [-61.9,-18]]])
m=base+body+entry+roof+entry_roof
cuts=[]; inserts=[]; features=[]
def window(x,w,h,z,kind='rect'):
    profile=arch(x,z,w,h) if kind=='arch' else rect(x,z,w,h)
    cuts.append(front_prism(profile,-37.55,-36.7,0.8))
    # Mullions anchored to recess backing; minimum width 0.9mm, no loose islands.
    inserts.append(box([x-0.45,-37.55,z],[x+0.45,-36.5,z+h-(w/2 if kind=='arch' else 0)]))
    for zz in [z+h*0.32,z+h*0.64]:
        inserts.append(box([x-w/2,-37.55,zz-0.45],[x+w/2,-36.5,zz+0.45]))
    # Integral broad sill, under-bevel limits its outward cantilever.
    sill=hull([[a,b,c] for a in [x-w/2-0.9,x+w/2+0.9] for b,c in [(-37.4,z-1.2),(-37.4,z),(-38.2,z),(-38.2,z-0.4)]])
    inserts.append(sill)
    features.append({'type':kind,'front_x':x,'width':w,'height':h,'bottom_z':z,'evidence':'restored official photos; approximate positioning'})
for x in [-35.5,35.5]:window(x,16,22,8)
for x in [-63,-53,53,63]:window(x,6.5,23,7,'arch')
# Door recess stands for the open porch; no closed room or hidden support trap.
cuts.append(front_prism(rect(0,z0,35,26),-59.55,-58.6,0.9))
inserts.append(box([-0.6,-59.55,z0],[0.6,-58.4,z0+25]))
inserts.append(box([-17.5,-59.55,22.5],[17.5,-58.4,23.5]))
for x in [-8.5,8.5]:inserts.append(box([x-0.5,-59.55,z0],[x+0.5,-58.4,22.5]))
# Only the photo-confirmed left side of the projecting entrance receives a hexagonal recess.
hp=regular(-49,18,4.5,6)
cuts.append(end_prism(hp,-24.05,-23.2))
features.append({'type':'hexagonal','plane':'entry left wall x=-24','centre_yz':[-49,18],'radius':4.5,'depth':0.8})
# Small circular ventilation recess on front gable, printed as a blind recess.
cuts.append(front_prism(regular(0,39,2.8,32),-61.95,-61.1,0.8))
for zz in [38.5,39.7]:inserts.append(box([-2.2,-61.95,zz-0.4],[2.2,-60.9,zz+0.4]))
# Partially observed left end: two visible vertical wood window bays only.
# Do not invent a complete repeated end/rear facade.
for yy in [-18,-5]:
    pr=rect(yy,8,7.5,22)
    cuts.append(end_prism(pr,-75.05,-74.2))
    inserts.append(box([-75.05,yy-0.45,8],[-74,yy+0.45,30]))
    for zz in [15,22]:inserts.append(box([-75.05,yy-3.75,zz-0.45],[-74,yy+3.75,zz+0.45]))
    features.append({'type':'partial left-end rectangular','centre_y':yy,'policy':'two visible bays retained; obscured count not claimed complete'})
for c in cuts:m=m-c
for a in inserts:m=m+a
# Coarse tile-course cues are broad shallow grooves, not fragile individual tiles.
# Front/rear main roof only, leaving the hips smooth and avoiding the projecting entry.
for y in [9,15,21,27,33]:
    z=wall+18-(y-0.6)*(15.5/39.9)
    for s in [-1,1]:
        yy=s*y
        # A horizontal rectangular cutter only nicks the sloping top by 0.25mm.
        if s<0:
            for lo,hi in [(-69,-29),(29,69)]:m=m-box([lo,yy-0.3,z-0.08],[hi,yy+0.3,z+0.5])
        else:m=m-box([-69,yy-0.3,z-0.08],[69,yy+0.3,z+0.5])
mesh=m.to_mesh64()
t=trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:,:3],faces=np.asarray(mesh.tri_verts),process=False)
t.export(OUT/'model.stl');t.export(OUT/'model.obj')
report={'revision':'v1-candidate','parameters_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest(),'boolean_status':str(m.status()),'vertices':len(t.vertices),'faces':len(t.faces),'bounds_mm':t.bounds.tolist(),'volume_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(t.split()),'features':features,'method':'Manifold boolean union/difference; original convex primitives. STL is the single printable solid; no auxiliary preview mesh.'}
(OUT/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='features'},indent=2))
