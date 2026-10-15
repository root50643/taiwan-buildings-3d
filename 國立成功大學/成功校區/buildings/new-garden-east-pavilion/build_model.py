"""NCKU Da Hsin Yuan east Student Salon: source-guided printable exterior.
Architectural X points east, Y south. Dimensions are approximate; no surveyed claim.
The output is a single solid with backed recessed glazing. No post-export repair.
"""

import sys
sys.dont_write_bytecode=True
def require(condition, message='Required check failed'):
    if not bool(condition): raise RuntimeError(message)
from pathlib import Path
import argparse, hashlib, json, struct
import numpy as np
from manifold3d import Manifold, OpType

R = Path(__file__).resolve().parent

def box(x0, x1, y0, y1, z0, z1):
    require((x1 > x0 and y1 > y0 and z1 > z0), ('Required check failed'))
    return Manifold.cube((x1-x0, y1-y0, z1-z0)).translate((x0,y0,z0))

def union(parts):
    return Manifold.batch_boolean(parts, OpType.Add)

def make_model(p):
    s = p['scale_mm_per_m']; floor = p['plinth_top_mm']
    Z = lambda m: floor + s*m
    B = lambda a,b,c,d,z0,z1: box(s*a,s*b,s*c,s*d,Z(z0),Z(z1))
    x0,x1,y0,y1 = p['base_bounds_mm']
    parts = [box(x0,x1,y0,y1,0,p['base_thickness_mm'])]
    # Two shallow, continuous source-supported ground levels; no site landscaping.
    parts += [box(-2,82,-2,132,p['base_thickness_mm']-.05,floor),
              box(-5,85,-5,135,p['base_thickness_mm']-.05,p['base_thickness_mm']+.6)]
    a,b,c,d = p['main_glazing_bounds_m']
    hall = B(a,b,c,d,-.02,p['main_roof_top_m'])
    # Fill hidden ceiling cells: interior structure is intentionally solidified.
    # External eave grid stays visible; no sealed internal shells are exported.
    # Glass is deliberately backed with solid material. The 0.9 mm frame lands
    # are part of the same solid, not unattached fine pieces.
    frame=p['frame_width_mm']; depth=p['glazing_recess_mm']
    lo,hi=Z(.12),Z(p['main_beam_bottom_m'])-.25
    def pane_cut(side,t0,t1,z0,z1,dep=depth):
        if side=='west': return box(a*s-.02,a*s+dep,t0,t1,z0,z1)
        if side=='east': return box(b*s-dep,b*s+.02,t0,t1,z0,z1)
        if side=='north': return box(t0,t1,c*s-.02,c*s+dep,z0,z1)
        return box(t0,t1,d*s-dep,d*s+.02,z0,z1)
    for side in ['west','east','north','south']:
        start,end=(c*s,d*s) if side in ['west','east'] else (a*s,b*s)
        for i in range(12):
            t0=start+(end-start)*i/12+frame/2
            t1=start+(end-start)*(i+1)/12-frame/2
            # Keep 1.5 mm corner lands so perpendicular pockets never meet.
            if i==0: t0=max(t0,start+1.5)
            if i==11: t1=min(t1,end-1.5)
            hall-=pane_cut(side,t0,t1,lo,hi)
    # Different four-leaf door positions in the three source-visible facades.
    # The wider upper bar distinguishes doors from full-height glass bays.
    for side,m0,m1 in [('north',4.0,8.0),('east',4.0,8.0),('west',8.0,12.0)]:
        for k in range(4):
            t0=s*(m0+(m1-m0)*k/4)+frame/2
            t1=s*(m0+(m1-m0)*(k+1)/4)-frame/2
            hall-=pane_cut(side,t0,t1,Z(.12),Z(2.3)-frame/2,depth+.25)
            hall-=pane_cut(side,t0,t1,Z(2.3)+frame/2,hi,depth)
        # Backed door-head relief, with positive roots into the underlying wall.
        if side=='west': parts.append(box(a*s-.12,a*s+.6,s*m0,s*m1,Z(2.3)-frame/2,Z(2.3)+frame/2))
        elif side=='east': parts.append(box(b*s-.6,b*s+.12,s*m0,s*m1,Z(2.3)-frame/2,Z(2.3)+frame/2))
        else: parts.append(box(s*m0,s*m1,c*s-.12,c*s+.6,Z(2.3)-frame/2,Z(2.3)+frame/2))
    parts.append(hall)
    # Service tail is offset east, with a real recessed junction below the main
    # eave. It is not a full-width generic block behind the hall.
    sa,sb,sc,sd=p['service_body_bounds_m']
    service=B(sa,sb,sc,sd,-.02,p['service_roof_top_m']-.2)
    # Narrow north connector: side-door set back from the concrete east facade.
    connector=B(6.3,14.1,13.8,16.2,-.02,3.0)
    # East: broad south window, small north window, separate recessed junction door.
    for q0,q1,h0,h1 in [(22.7,24.4,1.05,2.3),(17.7,18.6,1.05,2.3)]:
        service-=box(sb*s-p['service_opening_recess_mm'],sb*s+.02,q0*s,q1*s,Z(h0),Z(h1))
    connector-=box(14.1*s-.8,14.1*s+.02,14.4*s,15.35*s,Z(.12),Z(2.25))
    # West: one small square window plus vertically stacked service louvers.
    service-=box(sa*s-.02,sa*s+.8,17.3*s,18.2*s,Z(1.35),Z(2.3))
    for q0,q1,h0,h1 in [(21.1,21.9,1.55,2.35),(20.0,21.9,.22,1.18)]:
        service-=box(sa*s-.02,sa*s+.8,q0*s,q1*s,Z(h0),Z(h1))
        for z in np.arange(Z(h0)+.55,Z(h1)-.2,1.1):
            parts.append(box(sa*s-.08,sa*s+.85,q0*s,q1*s,z,z+.55))
    # South: paired west equipment bay recess, east window wrapping the corner.
    # The machinery itself is omitted because public sources show differing states.
    service-=box(4.65*s,9.25*s,25.1*s,26.42*s,Z(.15),Z(2.8))
    parts.append(B(6.9,7.12,25.0,26.4,.0,2.85))
    # A backed short louver on the left of the equipment bay; no open machine mesh.
    for z in np.arange(Z(.3),Z(1.25),1.1):
        parts.append(box(4.7*s,5.8*s,25.08*s,25.25*s,z,z+.55))
    service-=box(14.1*s,15.9*s,26.4*s-.8,26.4*s+.02,Z(1.05),Z(2.3))
    parts += [service,connector]
    ra,rb,rc,rd=p['service_roof_bounds_m']
    parts.append(box(ra*s,rb*s,rc*s,rd*s,Z(p['service_roof_top_m'])-p['service_roof_sheet_thickness_mm'],Z(p['service_roof_top_m'])))
    # Thin horizontal main roof, deep cantilever and orthogonal timber grid.
    ra,rb,rc,rd=p['main_roof_bounds_m']
    rt=Z(p['main_roof_top_m']); rbz=rt-p['main_roof_sheet_thickness_mm']
    parts.append(box(ra*s,rb*s,rc*s,rd*s,rbz,rt))
    w=p['beam_width_mm']; bz=Z(p['main_beam_bottom_m'])
    for t in np.arange(p['beam_pitch_m'],16,p['beam_pitch_m']):
        t=max(w/2,min(16*s-w/2,t*s))
        parts.append(box(t-w/2,t+w/2,0,16*s,bz,rbz+.02))
        parts.append(box(0,16*s,t-w/2,t+w/2,bz,rbz+.02))
    # Source-visible major white rectangular rooftop louver box, never omitted.
    a,b,c,d=p['rooftop_box_bounds_m']
    unit=B(a,b,c,d,p['main_roof_top_m']-.02,p['rooftop_box_top_m'])
    for z in np.arange(Z(4.18),Z(5.3),1.4):
        for y0,y1 in [(c*s-.02,c*s+p['louver_recess_mm']),
                      (d*s-p['louver_recess_mm'],d*s+.02)]:
            unit-=box(a*s+1.2,b*s-1.2,y0,y1,z,z+.6)
    parts.append(unit)
    result=union(parts)
    require((str(result.status()).endswith('NoError')), (str(result.status())))
    require((len(result.decompose())==1), (str([(q.bounding_box(),q.volume()) for q in result.decompose()])))
    return result

def save_stl(solid,path):
    # Deterministic binary STL. Triangles are directly from the exact CSG result;
    # no mesh library is permitted to repair, merge, simplify or discard faces.
    mesh=solid.to_mesh(); vertices=np.asarray(mesh.vert_properties[:,:3],dtype=np.float32).copy()
    # Architectural drawing Y increases south. Map to a right-handed exported
    # system (+X east, +Y north, +Z up); reverse face winding with the reflection.
    vertices[:,1] *= -1
    faces=np.asarray(mesh.tri_verts,dtype=np.int64)[:,[0,2,1]]; tris=vertices[faces]
    header=b'NCKU east Student Salon | approximate exterior | millimetres'
    data=bytearray(header.ljust(80,b'\0')+struct.pack('<I',len(tris)))
    for t in tris:
        normal=np.cross(t[1].astype(float)-t[0],t[2].astype(float)-t[0]); normal/=np.linalg.norm(normal)
        data+=struct.pack('<12fH',*normal,*t.ravel(),0)
    path.write_bytes(data)
    return len(tris)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,default=R)
    args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text()); solid=make_model(p)
    path=args.output_dir/'model.stl'; count=save_stl(solid,path)
    report={'triangles':count,'stl_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'manifold_status':str(solid.status()),'components':len(solid.decompose()),
            'volume_mm3':solid.volume(),'csg_bounds_before_y_reflection_mm':solid.bounding_box(),
            'export_axes':'+X east, +Y north, +Z up',
            'notes':'Construction report only. Raw-STL checks and external review are separate.'}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
