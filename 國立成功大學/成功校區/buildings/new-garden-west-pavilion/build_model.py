"""NCKU Da Hsin Yuan WEST Alumni Club, source-guided printable exterior.
Architectural X east, Y south; approximate metres are uniformly scaled to mm.
All geometry is newly constructed for the west pavilion. No post-export repair.
"""

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

from pathlib import Path
import argparse, hashlib, json, struct
import numpy as np
from manifold3d import Manifold, OpType
R = Path(__file__).resolve().parent

def box(x0,x1,y0,y1,z0,z1):
    require(x1>x0 and y1>y0 and z1>z0, (x0,x1,y0,y1,z0,z1))
    return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))

def union(parts):
    return Manifold.batch_boolean(parts,OpType.Add)

def make_model(p):
    s=p['scale_mm_per_m']; floor=p['plinth_top_mm']
    Z=lambda m:floor+s*m
    B=lambda a,b,c,d,z0,z1:box(s*a,s*b,s*c,s*d,Z(z0),Z(z1))
    x0,x1,y0,y1=p['base_bounds_mm']
    parts=[box(x0,x1,y0,y1,0,p['base_thickness_mm'])]
    # Source-visible pavilion plinth, simplified site grades. The east shoulder
    # is near flush; the west has two rising stair treads and a low wall.
    parts.append(box(0,21.35*s,0,24.35*s,p['base_thickness_mm']-.05,floor))
    parts.append(box(18*s,22.05*s,-.35*s,24.75*s,p['base_thickness_mm']-.05,floor-.3))
    for a,b,h in [(-1.25,0.05,floor-1.2),(-.65,.05,floor-.6)]:
        parts.append(box(a*s,b*s,16*s,18.3*s,p['base_thickness_mm']-.03,h))
    # The west low wall is on the outer edge of the plinth, separate from glazing.
    parts.append(B(0,.24,7.0,16.0,-.02,.85))
    # North-east low landscape edge is truncated at the pavilion, not a site model.
    parts.append(B(18.75,21.35,-.05,.22,-.02,.30))

    a,b,c,d=p['main_glazing_bounds_m']; fw=p['frame_width_mm']
    hall=B(a,b,c,d,-.02,p['main_roof_top_m'])
    # Glass and doors are backed recesses. Full-height bays retain the three
    # paired-door sets at different positions on north/east/west facades.
    lo,hi=Z(.10),Z(p['main_beam_bottom_m'])-.18
    def panel_cut(side,t0,t1,z0,z1,dep):
        if side=='west':return box(a*s-.02,a*s+dep,t0,t1,z0,z1)
        if side=='east':return box(b*s-dep,b*s+.02,t0,t1,z0,z1)
        if side=='north':return box(t0,t1,c*s-.02,c*s+dep,z0,z1)
        return box(t0,t1,d*s-dep,d*s+.02,z0,z1)
    door_ranges={'north':(7,13),'east':(7,13),'west':(5,11)}
    for side in ['north','east','west']:
        start,end=(c,d) if side in ['east','west'] else (a,b)
        dr0,dr1=door_ranges[side]
        for i,t in enumerate(np.arange(start,end,1.0)):
            t0=t*s+fw/2;t1=(t+1)*s-fw/2
            if t==start:t0=max(t0,start*s+1.6)
            if t+1==end:t1=min(t1,end*s-1.6)
            if dr0<=t<dr1:
                # Six door leaves, grouped into three pairs by wider pair posts.
                if int(t-dr0)%2==0:t0+=.15
                else:t1-=.15
                hall-=panel_cut(side,t0,t1,lo,Z(2.30)-fw/2,p['glazing_recess_mm']+.2)
                hall-=panel_cut(side,t0,t1,Z(2.30)+fw/2,hi,p['glazing_recess_mm'])
            else:
                hall-=panel_cut(side,t0,t1,lo,hi,p['glazing_recess_mm'])
    # South return glazing on either side of the recessed connecting neck.
    for t in [2,3,13,14,15]:
        t0=t*s+fw/2;t1=(t+1)*s-fw/2
        if t==2:t0=2*s+1.6
        if t==15:t1=16*s-1.6
        hall-=panel_cut('south',t0,t1,lo,hi,p['glazing_recess_mm'])
    # The uncut 1 mm wall land between leaf/transom is the door head.
    parts.append(hall)

    # Plan-traced recessed junction: x4.25..12.75 only. The 19 x 8 m low-roof
    # envelope is explicitly NOT a filled rectangular service-body block.
    ja,jb,jc,jd=p['junction_bounds_m']
    junction=B(ja,jb,jc-.02,jd+.02,-.02,p['service_roof_top_m']-.12)
    junction-=box(ja*s-.02,ja*s+.85,16.40*s,17.45*s,Z(.10),Z(2.30))
    junction-=box(jb*s-.85,jb*s+.02,16.4*s,17.45*s,Z(.10),Z(2.30))
    parts.append(junction)
    sa,sb,sc,sd=p['service_body_bounds_m']
    service=B(sa,sb,sc,sd,-.02,p['service_roof_top_m']-.1)
    # WEST: one tall window, followed northwards by the separate recessed door.
    service-=box(sa*s-.02,sa*s+p['service_opening_recess_mm'],19.05*s,20.85*s,Z(.55),Z(2.30))
    # EAST: tall ground-level entrance near the south end, not two high windows.
    service-=box(sb*s-p['service_opening_recess_mm'],sb*s+.02,21.80*s,23.60*s,Z(.08),Z(2.30))
    # SOUTH: broad cafe window, entrance, two small windows, reception window.
    # Positions read from west half of South Elevation, not the east service bay.
    for u,v,h0,h1 in [(3.3,6.3,1.35,2.55),(8.8,9.8,.08,2.55),
                       (10.8,12.0,1.35,2.55),(14.6,15.8,1.35,2.55),
                       (18.5,20.3,1.35,2.55)]:
        service-=box(u*s,v*s,sd*s-p['service_opening_recess_mm'],sd*s+.02,Z(h0),Z(h1))
    # The broad south window has two lights. Its mullion is backed by the wall.
    parts.append(box(4.8*s-fw/2,4.8*s+fw/2,sd*s-.9,sd*s+.04,Z(1.35),Z(2.55)))
    # Light, intentionally shallow concrete formwork joints. No tie-hole spikes.
    # Vertical and horizontal lines are grooves backed by the solid service wall.
    for h in [.85,1.70,2.55]:
        zz=Z(h)
        for q0,q1 in [(sa*s-.02,sa*s+.18),(sb*s-.18,sb*s+.02)]:
            service-=box(q0,q1,sc*s-.02,sd*s+.02,zz-.11,zz+.11)
        service-=box(sa*s-.02,sb*s+.02,sd*s-.18,sd*s+.02,zz-.11,zz+.11)
        service-=box(sa*s-.02,sb*s+.02,sc*s-.02,sc*s+.18,zz-.11,zz+.11)
    parts.append(service)
    ra,rb,rc,rd=p['service_roof_bounds_m']; rt=Z(p['service_roof_top_m'])
    parts.append(box(ra*s,rb*s,rc*s,rd*s,rt-p['service_roof_sheet_thickness_mm'],rt))

    # Main roof is square (18 x 18 m), with full deep overhang and timber grid.
    ra,rb,rc,rd=p['main_roof_bounds_m'];rt=Z(p['main_roof_top_m']);rbz=rt-p['main_roof_sheet_thickness_mm']
    parts.append(box(ra*s,rb*s,rc*s,rd*s,rbz,rt))
    w=p['beam_width_mm'];bz=Z(p['main_beam_bottom_m'])
    for t in np.arange(p['beam_pitch_m'],18,p['beam_pitch_m']):
        t=t*s
        parts.append(box(t-w/2,t+w/2,0,18*s,bz,rbz+.03))
        parts.append(box(0,18*s,t-w/2,t+w/2,bz,rbz+.03))
    # White rooftop rectangular enclosure is present in drawings AND photographs.
    a,b,c,d=p['rooftop_box_bounds_m'];unit=B(a,b,c,d,p['main_roof_top_m']-.02,p['rooftop_box_top_m'])
    # South short-face louvers only. Other faces remain plain as the photos show.
    for z in np.arange(Z(4.30),Z(5.25),1.35):
        unit-=box(a*s+1.0,b*s-1.0,d*s-p['louver_recess_mm'],d*s+.02,z,z+.5)
    parts.append(unit)
    result=union(parts)
    require(str(result.status()).endswith('NoError'), str(result.status()))
    require(len(result.decompose())==1, str([(q.bounding_box(),q.volume()) for q in result.decompose()]))
    return result

def save_stl(solid,path):
    # Exact CSG output to deterministic binary STL, with no repairs, merges,
    # rounded-coordinate welding, removed faces or STL post-processing.
    mesh=solid.to_mesh();vertices=np.asarray(mesh.vert_properties[:,:3],dtype=np.float32).copy()
    vertices[:,1]*=-1 # Exported right-handed axes: +X east, +Y north, +Z up.
    faces=np.asarray(mesh.tri_verts,dtype=np.int64)[:,[0,2,1]];tris=vertices[faces]
    data=bytearray(b'NCKU west Alumni Club | approximate exterior | millimetres'.ljust(80,b'\0')+struct.pack('<I',len(tris)))
    for t in tris:
        n=np.cross(t[1].astype(float)-t[0],t[2].astype(float)-t[0]);n/=np.linalg.norm(n)
        data+=struct.pack('<12fH',*n,*t.ravel(),0)
    path.write_bytes(data);return len(tris)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R);args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());solid=make_model(p)
    path=args.output_dir/'model.stl';count=save_stl(solid,path)
    report={'triangles':count,'stl_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'manifold_status':str(solid.status()),'components':len(solid.decompose()),
            'volume_mm3':solid.volume(),'csg_bounds_before_y_reflection_mm':solid.bounding_box(),
            'main_roof_parameter_mm':[(p['main_roof_bounds_m'][1]-p['main_roof_bounds_m'][0])*p['scale_mm_per_m'],(p['main_roof_bounds_m'][3]-p['main_roof_bounds_m'][2])*p['scale_mm_per_m']],
            'export_axes':'+X east, +Y north, +Z up',
            'notes':'Construction report only. Original-STL checks and independent review are separate.'}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
