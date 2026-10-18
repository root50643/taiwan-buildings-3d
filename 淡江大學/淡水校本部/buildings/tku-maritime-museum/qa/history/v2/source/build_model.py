from pathlib import Path
import argparse, hashlib, json
import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent.parent

def generate(p):
    pieces=[]; labels=[]
    def add(mesh,name):
        pieces.append(mesh); labels.append(name); return mesh
    def box(x0,x1,y0,y1,z0,z1,name):
        m=trimesh.creation.box([x1-x0,y1-y0,z1-z0]);m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return add(m,name)
    def prism_yz(x0,x1,points,name):
        m=trimesh.creation.extrude_polygon(Polygon(points),x1-x0,engine='manifold')
        # (u,v,w) -> (w,u,v), a cyclic, orientation-preserving permutation.
        m.vertices=m.vertices[:,[2,0,1]];m.apply_translation([x0,0,0]);return add(m,name)
    w=p['body_width']/2;l=p['body_length']/2;h=p['deck_height']
    # Chamfered RECTANGLE: no pointed prow, keel, underground hull or invented base.
    poly=Polygon([(-w+3,-l),(w-3,-l),(w,-l+3),(w,l),(-w,l),(-w,-l+3)])
    body=trimesh.creation.extrude_polygon(poly,h,engine='manifold');add(body,'near-rectangular main body / open deck')
    box(-44,44,0,68,h-0.5,62,'lower stepped superstructure')
    # Central faceted glass enclosure; the sloping roof and white side cheeks are visible in both aerials.
    prism_yz(-24,24,[(-17,h-0.5),(18,h-0.5),(18,66),(-5,66),(-17,59)],'angular glazing enclosure')
    for s in [-1,1]:
        a,b=sorted([s*24,s*40])
        prism_yz(a,b,[(-5,h-0.5),(29,h-0.5),(29,69),(17,69),(-5,50)],'white inclined cheek')
    box(-34,34,25,65,61.5,80,'upper bridge house')
    box(-35,35,24,66,79.8,81.4,'green upper flat roof')
    for s in [-1,1]:
        a,b=sorted([s*31,s*p['wing_outer_x']])
        box(a,b,34,54,p['wing_bottom'],p['wing_bottom']+p['wing_thickness'],'projecting bridge wing')
        # Print simplification v2: close only the 2 mm gap directly under the inner wing root.
        # The actual outer wing overhang remains open beyond x=44.1.
        a,b=sorted([s*31,s*44.1])
        box(a,b,34,54,61.5,61.5+p['inner_wing_root_fill_mm']+0.5,'filled inner wing root for accessible support')
        # Broad solid perimeter upstand, not a mesh of fragile railing rods.
        a,b=sorted([s*(p['wing_outer_x']-1.6),s*p['wing_outer_x']])
        box(a,b,34,54,66.8,70.2,'simplified solid wing edge')
    box(-17,1,45,60,80,101,'rectangular funnel-like upright')
    box(-17,1,45,60,99.2,101.4,'dark funnel cap')
    r=p['mast_diameter']/2
    m=trimesh.creation.cylinder(radius=r,height=p['mast_top']-80,sections=16);m.apply_translation([14,41,(p['mast_top']+80)/2]);add(m,'thickened mast')
    t=p['crossarm_thickness'];box(-1,29,41-t/2,41+t/2,109,109+t,'thickened crossarm')
    box(5,23,41-t/2,41+t/2,120,120+t,'thickened top crossarm')
    # Entry bridge is deliberately narrow, supported at its far end by visible-scale piers.
    box(p['entry_bridge_outer_x'],-51,-9,1,16.8,20,'narrow side entrance bridge')
    for y in [-7.4,-0.6]:box(-89,-86.2,y,y+2.8,0,17.2,'entry bridge pier')
    # Short stairs terminate at the SIDE DOOR, never at the roof deck.
    for i in range(8):box(-62,-51,-29+i*2.5,-9,0,(i+1)*2.5,'side door stair')
    union=trimesh.boolean.union(pieces,engine='manifold',check_volume=True)
    cuts=[]
    def cutbox(x0,x1,y0,y1,z0,z1):
        m=trimesh.creation.box([x1-x0,y1-y0,z1-z0]);m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);cuts.append(m)
    # Paired broad splayed recesses on both long sides, each divided by robust mullions.
    for s in [-1,1]:
        for a,b in [(-27,-8),(2,21)]:
            pts=[(a,31),(b,31),(b+2,37),(a-2,37)]
            m=trimesh.creation.extrude_polygon(Polygon(pts),1.7,engine='manifold');m.vertices=m.vertices[:,[2,0,1]]
            m.apply_translation([50.8 if s==1 else -52.5,0,0]);cuts.append(m)
        for y in [30,37,44,51,58]:cutbox(50.8 if s==1 else -52.5,52.5 if s==1 else -50.8,y,y+3.2,35,37.6)
        for y in [-32,-19,-6,7,20,33,46]:cutbox(50.8 if s==1 else -52.5,52.5 if s==1 else -50.8,y,y+7,13,18.5)
    cutbox(-52.5,-50.7,-10,2,20,30)
    # Glazing mullions are shallow incisions into a solid enclosure, never zero-thickness sheets.
    for x in [-19,-10,-1,8,17]:cutbox(x,x+1.1,-17.4,-16.4,44,p['front_glazing_groove_top_mm'])
    for x in [-26,-12,2,16]:cutbox(x,x+6,24.4,25.8,68.5,75.5)
    model=trimesh.boolean.difference([union,*cuts],engine='manifold',check_volume=True)
    model.remove_unreferenced_vertices()
    return model, [{'name':n,'bounds':m.bounds.tolist()} for n,m in zip(labels,pieces)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE);args=ap.parse_args()
    p=json.loads((HERE/'parameters.json').read_text(encoding='utf-8'))
    model,parts=generate(p);args.output.mkdir(parents=True,exist_ok=True)
    raw=model.export(file_type='stl');(args.output/'model.stl').write_bytes(raw)
    report={'generator':'source/build_model.py','units':'mm','parameters_sha256':hashlib.sha256((HERE/'parameters.json').read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256(raw).hexdigest(),'vertices':len(model.vertices),'triangles':len(model.faces),'bounds':model.bounds.tolist(),'volume_mm3':float(model.volume),'parts':parts}
    (args.output/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['stl_sha256','triangles','volume_mm3','bounds']}))
if __name__=='__main__':main()
