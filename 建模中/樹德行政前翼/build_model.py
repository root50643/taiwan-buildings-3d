"""Original Shute administrative forecourt wing, photo-derived printable approximation.
Units are millimetres. This is an explicitly partial wing, not a whole-building survey.
Reconstructs only the supported front fins/roof frame/corner/drum/tower; rear is a cut.
"""
from pathlib import Path
import json, argparse
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, OpType
R=Path(__file__).resolve().parent

def box(x0,x1,y0,y1,z0,z1):
    assert x1>x0 and y1>y0 and z1>z0
    return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def union(parts): return Manifold.batch_boolean(parts,OpType.Add)
def cyl(z0,z1,r0,r1,x=35,y=-17):
    return Manifold.cylinder(z1-z0,r0,r1,96).translate((x,y,z0))
def wedge(a0,a1,z0,z1,x=35,y=-17):
    a=np.radians(np.linspace(a0,a1,9)); pts=np.vstack([[0.,0.],np.column_stack([70*np.cos(a),70*np.sin(a)])])
    return CrossSection([pts]).extrude(z1-z0).translate((x,y,z0))
def make_model():
    parts=[box(-75,75,-51,36,0,3)]
    # Bounded front bar: the unobserved rear is a deliberately plain vertical cut.
    main=union([box(-63,12,-7,24,3,78),box(12,58,-17,24,3,78)])
    # Left courtyard windows: continuous glazing groups behind the six fins.
    for z0,z1 in [(7,15),(20,28),(34,43)]:
        main-=box(-59,10,-7.8,-5.4,z0,z1)
        # Broad continuous bands survive between the structural fins.
        parts.append(box(-59.3,10.2,-7.75,-5.0,z1,z1+1.3))
    # Upper fin field is predominantly opaque in the official aerial.
    # Only the leftmost source-visible glazed strip extends into the upper levels.
    for z0,z1 in [(49,57),(63,71)]:main-=box(-59,-50,-7.8,-6.2,z0,z1)
    # Deep open/recessed balcony above the two-level drum, with a solid back.
    main-=box(11.5,58.2,-18,-6.5,34.5,47.2)
    # Two upper storeys. Each has paired narrow ribbon panes and sunshade lines.
    # The local return at x=12 is a real stepped facade, not a new storey count.
    
    for lo,hi in [(50.5,57.0),(65.5,72.0)]:
        for z0,z1 in [(lo,lo+2.0),(lo+3.6,hi)]:
            main-=box(14.2,56.5,-17.3,-16.05,z0,z1)
            main-=box(11.9,12.85,-15.6,-7.3,z0,z1)
            # Backed vertical mullions only. They never float or rely on a hairline bridge.
            for x in np.arange(16,57,4.3):parts.append(box(x-.47,x+.47,-17.04,-15.9,z0-.05,z1+.05))
            for y in np.arange(-13,-7.3,4.3):parts.append(box(11.98,13.05,y-.47,y+.47,z0-.05,z1+.05))
        for z in [lo-1.1,lo+2.0,hi]:
            parts.append(box(11.5,57.6,-19.1,-15.8,z,z+1.2))
            parts.append(box(10.25,13.3,-19.1,-5.5,z,z+1.2))
    parts.append(main)
    # Balcony front-left pier, slab, and substantial low parapet behind the curved rim.
    parts.append(box(12.2,17.0,-20.2,-14.1,33.2,48))
    parts.append(box(11.5,58,-18.2,-6.1,33.5,35))
    back=box(16.2,57.9,-7.2,-6.1,35,46.8)
    for x in np.arange(18,56,4.5):back-=box(x,x+3.25,-7.3,-6.7,36.5,45.3)
    parts.append(back)
    # Distinct flared glazed entrance: top radius exceeds lower radius.
    zbot,ztop=3.,32.6
    rbot,rtop=22.5,27.
    r=lambda z:rbot+(rtop-rbot)*(z-zbot)/(ztop-zbot)
    drum=cyl(zbot,ztop,rbot,rtop) ^ box(7,63,-46,-15,2,34)
    # Pane pockets represent glass; continuous solid backing keeps this a printable solid.
    # All longitudinal and horizontal frame widths exceed 0.9 mm on the delivered mesh.
    for z0,z1 in [(4.5,11.2),(12.45,18.8),(20.05,30.9)]:
        ring=cyl(z0,z1,r(z0)+1.0,r(z1)+1.0)-cyl(z0-.1,z1+.1,r(z0)-.55-.1*(rtop-rbot)/(ztop-zbot),r(z1)-.55+.1*(rtop-rbot)/(ztop-zbot))
        for a in np.arange(180.,360.,12.):
            if z0<5 and a in [276.,288.,300.]:continue # preserve robust door jambs
            drum-=ring ^ wedge(a+1.3,a+10.7,z0-.02,z1+.02)
    # Entrance recess on the source-visible front-right quarter, never a blind internal void.
    door=(cyl(3.7,11.2,r(3.7)+1,r(11.2)+1)-cyl(3.6,11.3,r(3.6)-1.0,r(11.3)-1.0))
    drum-=door ^ wedge(283,305,3.65,11.25)
    parts.append(drum)
    # Balcony curved rim is a thick architectural simplification of the thin source rail.
    rim=(cyl(32.1,35.2,27.45,27.45)-cyl(31.9,35.4,25.9,25.9)) ^ box(6,64,-47,-15,31,36)
    parts.append(rim)
    # Source railing terminates into substantial side abutments, never knife tips.
    parts.append(box(7.4,12.7,-19.2,-14.6,31.8,35.2))
    parts.append(box(57.3,63.0,-19.2,-14.6,31.8,35.2))
    # Six giant concrete fins; full-height front blades with rearward roof beams.
    fin_x=[-47,-36,-25,-14,-3,8]
    for x in fin_x:
        parts.append(box(x-1.65,x+1.65,-11.8,-4.3,3,88.6))
        parts.append(box(x-1.65,x+1.65,-11.8,25,85.3,88.6))
    # High rear roof screen/framework visible in the official aerial, not a roof cap.
    screen=box(-63,58,21.0,25.0,77.5,91.5)
    for x0,x1 in [(-58,-49),(-45,-38),(-34,-27),(-23,-16),(-12,-5),(-1,6),(10,20),(24,34)]:
        screen-=box(x0,x1,20.8,25.2,81.5,88.2)
    parts.append(screen)
    # Pale tall sign/stair tower. A narrow side-glass strip is recessed in its right face.
    tower=box(57,69,-17.0,5.0,3,104)
    tower-=box(68.35,69.2,-14.9,2.6,5,84)
    for z in np.arange(7,84,5.2):parts.append(box(68.22,69.08,-15,2.7,z,z+1.05))
    parts.append(box(68.2,69.1,-6.9,-5.8,4.8,84.2))
    parts.append(tower)
    # Short rearward return ends plainly: sources do not resolve the full outer elevation.
    parts.append(box(57,65,4.5,24.5,3,78))
    # Broad, shallow entry paving plateau. No speculative landscape or auditorium.
    parts.append(box(5,69,-46.5,-15,2.7,3.5))
    final=union(parts)
    assert final.status().name=='NoError', final.status()
    mesh=final.to_mesh()
    t=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=False)
    return t

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'model.stl');a=p.parse_args()
    t=make_model();t.export(a.output)
    print(json.dumps({'faces':len(t.faces),'extents_mm':t.extents.tolist(),'watertight_construction_hint':bool(t.is_watertight),'output':str(a.output)}))
    if a.output.resolve()==(R/'model.stl').resolve():
        params={'school':'樹德科技大學','campus':'校本部（南校區）','building':'行政大樓弧形入口及前庭行政翼（局部）','units':'mm','base_dimensions_mm':[150,87,3],'model_extent_mm':t.extents.tolist(),'front':'negative Y','max_height_mm':104,'fins':6,'upper_occupied_window_bands':2,'lower_glazed_drum_levels':2,'scope':'photo-derived front wing; clean simplified rear cut; multifunction auditorium excluded','status':'author evidence candidate; independent review recorded separately','dimension_limitations':'No surveyed dimensions; independent model scale; wall/rail details enlarged for fabrication.'}
        (R/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
