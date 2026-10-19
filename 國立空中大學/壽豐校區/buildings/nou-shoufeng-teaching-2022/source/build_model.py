"""Original, parameterized photo interpretation. Coordinates and STL units: mm.
No source photographs are embedded. Run with numpy, trimesh, manifold3d, shapely.
"""
from pathlib import Path
import json, hashlib, math
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon
from shapely.ops import triangulate

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'models'
MODELS.mkdir(exist_ok=True)
L, H, W = 156., 126., 30.
SLAB, WALL, CAP = 1.6, 7.2, 1.2
PITCH = 10.

def box(x0,x1,y0,y1,z0,z1):
    m=tm.creation.box([x1-x0,y1-y0,z1-z0]); m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]); return m

def union(items): return tm.boolean.union(items, engine='manifold', check_volume=True)
def subtract(m, cuts): return tm.boolean.difference([m,union(cuts)], engine='manifold', check_volume=True) if cuts else m
def lslab(z0,z1): return union([box(0,L,0,W,z0,z1),box(0,W,0,H,z0,z1)])

def prism_xz(coords,y0,y1):
    p=Polygon(coords); tris=[t for t in triangulate(p) if p.covers(t.representative_point())]
    vertices=[]; faces=[]; lookup={}
    for t in tris:
        face=[]
        for xy in list(t.exterior.coords)[:3]:
            if xy not in lookup: lookup[xy]=len(vertices);vertices.append(xy)
            face.append(lookup[xy])
        faces.append(face)
    m=tm.creation.extrude_triangulation(np.asarray(vertices),np.asarray(faces),y1-y0)
    # local (x,z,depth) -> world (x,y,z)
    a=np.eye(4); a[:3,:3]=[[1,0,0],[0,0,1],[0,1,0]];a[1,3]=y0
    m.apply_transform(a);m.fix_normals();return m

def lower(floor):
    items=[lslab(0,SLAB),box(0,L,0,22,SLAB,8.8),box(0,22,0,H,SLAB,8.8)]
    # Terminal external walls, with open court-facing arcade.
    items += [box(L-1.6,L,22,28.4,SLAB,8.8),box(22,28.4,H-1.6,H,SLAB,8.8)]
    xs=list(np.arange(30,155,12))+[155.2]
    ys=list(np.arange(30,125,12))+[125.2]
    for x in xs: items.append(box(x-.8,x+.8,28.4,30,SLAB,8.8))
    for y in ys: items.append(box(28.4,30,y-.8,y+.8,SLAB,8.8))
    if floor>0:
        items += [box(30,L,28.5,30,SLAB,4.5),box(28.5,30,30,H,SLAB,4.5)]
    m=union(items); cuts=[]
    # Blind, shallow windows: visible corridor face; back rows deliberately estimated.
    for x in np.arange(34,150,12):
        for a,b in [(21.35,22.05),(-.05,.65)]: cuts.append(box(x,x+7,a,b,3.0,6.9))
    for y in np.arange(34,120,12):
        for a,b in [(21.35,22.05),(-.05,.65)]: cuts.append(box(a,b,y,y+7,3.0,6.9))
    if floor>0:
        for x in np.arange(32,153,3): cuts.append(box(x,x+.65,29.7,30.05,2.1,4.0))
        for y in np.arange(32,123,3): cuts.append(box(29.7,30.05,y,y+.65,2.1,4.0))
    return subtract(m,cuts)

def cap():
    # Flat ceiling plus two terminal arch soffits only. Printed inverted.
    items=[lslab(8.8,10)]
    x0,x1=138.8,149.2
    coords=[(x0,8.9),(x1,8.9)]
    for t in np.linspace(1,0,25):
        x=x0+(x1-x0)*t; z=6.8+1.2*math.sin(math.pi*t)
        coords.append((x,z))
    arch=prism_xz(coords,28.4,30)
    # Ends align with the last ordinary 12 mm bay (138..150).
    items.append(arch)
    coords2=[(114.8,8.9),(124.4,8.9)]+[(114.8+9.6*t,6.8+1.2*math.sin(math.pi*t)) for t in np.linspace(1,0,25)]
    arch2=prism_xz(coords2,28.4,30); a=np.eye(4);a[:3,:3]=[[0,1,0],[1,0,0],[0,0,1]]
    arch2.apply_transform(a);arch2.fix_normals();items.append(arch2)
    return union(items)

def roof():
    items=[lslab(0,1.2),box(0,L,0,1.2,1.2,3.4),box(0,1.2,0,H,1.2,3.4),
           box(28.8,L,28.8,30,1.2,3.4),box(28.8,30,28.8,H,1.2,3.4),
           box(L-1.2,L,0,30,1.2,3.4),box(0,30,H-1.2,H,1.2,3.4)]
    # Low terminal and inner-corner stair headhouses, not a fifth storey.
    for x,y,dx,dy in [(140,3,14,18),(3,108,18,16),(16,16,14,14)]:
        items.append(box(x,x+dx,y,y+dy,1.2,6.0))
    return union(items)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parts=[]; assembled=[]
    for i in range(4):
        lo=lower(i); a=np.eye(4);a[2,3]=2+i*10
        if i==0:
            lo.apply_translation([0,0,2]);lo=union([lo,lslab(0,2)]);a=np.eye(4)
        parts.append((f'{i*2+1:02d}-floor{i+1}-lower-upright',lo,a))
        ce=cap();ce.apply_transform(np.diag([1,-1,-1,1]));ce.apply_translation([0,W,10])
        # Inverted cap uses an actual proper rotation. x unchanged, y mirrored.
        a=np.diag([1,-1,-1,1]);a[1,3]=W;a[2,3]=12+i*10
        parts.append((f'{i*2+2:02d}-floor{i+1}-ceiling-inverted',ce,a))
    a=np.eye(4);a[2,3]=42
    parts.append(('09-roof-parapet-upright',roof(),a))
    manifest=[]
    for name,m,a in parts:
        m.merge_vertices();m.remove_unreferenced_vertices();m.fix_normals()
        p=MODELS/(name+'.stl');m.export(p)
        am=m.copy();am.apply_transform(a);assembled.append(am)
        manifest.append({'name':name,'stl':p.name,'sha256':sha(p),'print_bounds_mm':m.bounds.tolist(),
                         'assembly_transform_mm':a.tolist(),'assembly_bounds_mm':am.bounds.tolist(),
                         'print_orientation':'inverted ceiling; flip around X to assemble' if 'inverted' in name else 'upright'})
    full=union(assembled);full.export(MODELS/'assembly-reference-do-not-print.stl')
    data={'units':'mm','version':1,'parts':manifest,'assembly_bounds_mm':full.bounds.tolist(),
          'estimated_geometry':{'wing_envelope_mm':[L,H,W],'storeys':4,'storey_pitch_mm':10,'nominal_scale':'approximately 1:400; relative estimates, not measured',
          'min_structural_wall_mm':1.2,'min_grooved_rail_core_mm':1.2,'column_mm':1.6,'window_recess_mm':.65},
          'reference_stl_sha256':sha(MODELS/'assembly-reference-do-not-print.stl')}
    (ROOT/'parameters.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps({'parts':len(parts),'assembly_bounds_mm':full.bounds.tolist(),'volume_mm3':full.volume}))

if __name__=='__main__':main()
