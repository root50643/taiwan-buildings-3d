"""CNU J historical representative exterior. All output coordinates in millimetres.
Run with Python 3.13 + requirements.txt; no photographs are needed to rebuild.
Original constructive geometry; dimensions are photo estimates, never survey data.
"""
from pathlib import Path
import json, hashlib, math
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64

R=Path(__file__).resolve().parent
P=json.loads((R/'parameters.json').read_text(encoding='utf-8'))
X=P['frame_x_positions_mm']

def box(x1,x2,y1,y2,z1,z2):
    return Manifold.cube((x2-x1,y2-y1,z2-z1)).translate((x1,y1,z1))

def union(items):
    return Manifold.batch_boolean(items, __import__('manifold3d').OpType.Add)

def yz_prism(x1,x2,points):
    # Convex sloping cheek; exact planar sides, no unsupported decorative rail.
    return Manifold.hull_points([[x,y,z] for x in (x1,x2) for y,z in points])

def flat_beam(a,b,width,thickness=2.2):
    # A rounded-ended rectangular beam in the YZ plane. Width is the true
    # perpendicular in-plane caliper, rather than an axis-aligned guess.
    a=np.array(a,float);b=np.array(b,float)
    d=(b-a)/np.linalg.norm(b-a); n=np.array([-d[1],d[0]])
    pts=[a-d*width/2+n*width/2,a-d*width/2-n*width/2,
         b+d*width/2+n*width/2,b+d*width/2-n*width/2]
    return yz_prism(-thickness/2,thickness/2,pts)

def as_mesh(s):
    m=s.to_mesh64()
    out=trimesh.Trimesh(np.asarray(m.vert_properties)[:,:3],np.asarray(m.tri_verts),process=False)
    out.remove_unreferenced_vertices()
    return out

def orient(m,mode):
    m=m.copy()
    if mode=='roof_top_down':
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[1,0,0]))
    elif mode=='flat_side':
        m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,1,0]))
    m.apply_translation(-m.bounds[0])
    return m

def build():
    # Solid lower level and the genuinely two-storey rear envelope. The central
    # rear glazing is a shallow relief in this solid, never an invented room.
    b=[box(-107,107,-51,39,0,3),box(-90,90,-31,24,2.9,14),
       box(-90,90,12,24,13.9,26),box(-91,91,-36,-24,12.4,14)]
    # Ten broad bleacher rows. Their underside is filled for tabletop printing;
    # the stepped open-air seating above the lower storey remains fully visible.
    for i in range(10):
        y=-25+i*3.7
        b.append(box(-87.5,87.5,y,12.2,13.9,14+(i+1)*1.2))
    for side in [-1,1]:
        a,c=sorted([side*87.4,side*90.8])
        b.append(yz_prism(a,c,[(-27,13.9),(-27,15.2),(14,28),(14,13.9)]))
        # End terrace and the visible outer flight to the upper rear level.
        a,c=sorted([side*90,side*99])
        b.append(box(a,c,-29,25,2.9,14))
        a,c=sorted([side*92,side*99])
        for i in range(12):
            b.append(box(a,c,-26+i*3.5,16.5,13.9,14+(i+1)))
        # Lower external flight, returning from ground to the side terrace.
        a,c=sorted([side*101,side*105])
        for i in range(11):
            b.append(box(a,c,-25,13-i*3.3,2.9,4+i))
        # Low opaque cheek, shaped to the upper flight, replaces fine railing.
        a,c=sorted([side*99.2,side*101])
        b.append(box(a-.21,c+.01,-27,17,2.9,14))
        b.append(yz_prism(a,c,[(-27,13.8),(-27,15),(17,27),(17,13.8)]))
        # Two front stair flights descend outwards from the middle balcony.
        # Each has a horizontal landing; stairs run along X as in the photo.
        for i in range(11):
            inner=28+i*2.55; outer=28+(i+1)*2.55
            a,c=sorted([side*inner,side*outer])
            b.append(box(a-.03,c+.03,-44,-35.5,2.9,14-i))
        a,c=sorted([side*26,side*29])
        b.append(box(a,c,-44,-35.5,2.9,14))
    main=union(b)
    cuts=[]
    # The front photograph shows a broad central command podium interrupting
    # the side bleachers. Keep its flat floor and opaque front, not more seats.
    cuts.append(box(-25,25,-25.1,-8.9,14,28.1))
    # Central glazing panel on the back, spanning the two-level composition.
    cuts.append(box(-26,26,22.8,24.1,6,23.6))
    # Window groups flank the glass on the upper floor; recessed, closed backs.
    for sx in [-1,1]:
        for u in [38,54,70]:
            a,c=sorted([sx*(u-5.6),sx*(u+5.6)])
            cuts.append(box(a,c,22.8,24.1,16.1,23.1))
        # Shallow lower door/window groups; they do not create hidden cavities.
        for u in [38,60,80]:
            a,c=sorted([sx*(u-5),sx*(u+5)])
            cuts.append(box(a,c,23.0,24.1,4.8,12.8))
    # Front ground-level openings; simplified closed relief, not real rooms.
    for x in [-75,-56,-37,37,56,75]:
        cuts.append(box(x-6,x+6,-31.1,-29.8,5,11.8))
    cuts.append(box(-15,15,-31.1,-29.5,3.8,12.3))
    for x in X:
        cuts.append(box(x-1.6,x+1.6,12.6,17.4,23.5,26.1))
    main=main-union(cuts)
    # Broad glass mullions and floor band stay rooted to the recess back.
    details=[main,box(-25.1,25.1,-25,-8.9,13.9,20.3)]
    for x in [-25,-16.7,-8.35,0,8.35,16.7,25]:
        details.append(box(x-.65,x+.65,22.7,23.4,6,23.6))
    for z in [6.6,12.4,17.8,23]:
        details.append(box(-26,26,22.7,23.4,z-.65,z+.65))
    main=union(details)
    # Roof underside ribs are observed structural members, not hidden props.
    roof_bits=[box(-96,96,-30,30,35,37.4)]
    for x in X:
        roof_bits.append(box(x-2.8,x+2.8,-29,29,33.8,35.1))
    for y in [-26,24]:
        roof_bits.append(box(-95,95,y-.9,y+.9,34,35.1))
    roof=union(roof_bits)
    rc=[]
    for x in X:
        rc.append(box(x-1.6,x+1.6,12.6,17.4,33.7,34.6))
        for y in [-24,15,27]:
            rc.append(box(x-1.3,x+1.3,y-1.9,y+1.9,36.6,37.5))
    roof=roof-union(rc)
    # One reusable lower column. A 0.05 mm glue seat and 0.4 mm total XY
    # clearance keep assembled meshes disjoint and allow dry positioning.
    col=union([box(-1.4,1.4,12.2,17.8,26.05,33.75),
               box(-1.4,1.4,12.8,17.2,23.8,26.1),
               box(-1.4,1.4,12.8,17.2,33.7,34.45)])
    # Upper historical mast / two diagonal braces, one flat printable frame.
    # Flags, thin cables and mast finials are deliberately omitted.
    foot=37.45; top=53.4
    frame_bits=[box(-1.1,1.1,13.5,16.5,foot,top),
                flat_beam((-24,foot+1.15),(15,top-3),1.8),
                flat_beam((27,foot+1.15),(15,top-3),1.8)]
    for y in [-24,15,27]:
        frame_bits.append(box(-1.1,1.1,y-2.5,y+2.5,foot,foot+1.8))
        frame_bits.append(box(-1.1,1.1,y-1.7,y+1.7,36.75,foot+.05))
    frame=union(frame_bits)
    return {'main_body':main,'roof':roof,'column':col,'mast_brace_frame':frame}

def main():
    (R/'parts').mkdir(exist_ok=True)
    solids=build(); meshes={k:as_mesh(s) for k,s in solids.items()}
    assembly=[]; placements=[]
    for name in ['main_body','roof']:
        assembly.append(meshes[name]); placements.append({'part':name,'copy':1,'translation_mm':[0,0,0]})
    for name in ['column','mast_brace_frame']:
        for i,x in enumerate(X):
            m=meshes[name].copy();m.apply_translation([x,0,0]);assembly.append(m)
            placements.append({'part':name,'copy':i+1,'translation_mm':[x,0,0]})
    trimesh.util.concatenate(assembly).export(R/'model.stl')
    modes={'main_body':'upright','roof':'roof_top_down','column':'flat_side','mast_brace_frame':'flat_side'}
    inventory=[]
    for name,m in meshes.items():
        m.export(R/'parts'/f'{name}-assembly.stl')
        q=orient(m,modes[name]);q.export(R/'parts'/f'{name}-print.stl')
        inventory.append({'part':name,'quantity':1 if name in ['main_body','roof'] else len(X),
                          'print_orientation':modes[name],'assembly_bounds_mm':m.bounds.tolist(),
                          'print_bounds_mm':q.bounds.tolist(),'triangles':len(m.faces),
                          'volume_mm3':m.volume,'print_volume_mm3':q.volume})
    data={'units':'mm','assembly_is_for_overview_only':True,'physical_piece_count':2+2*len(X),
          'unique_part_count':4,'inventory':inventory,'placements':placements,
          'assembly_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),
          'reconstruction':'Each *-assembly.stl is at its design location (column and frame at x=0). Add X translations in placements. Each *-print.stl is independently bed-oriented, min bound 0.'}
    (R/'assembly.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data['inventory'],indent=2))

if __name__=='__main__':main()
