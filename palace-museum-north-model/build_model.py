"""國立故宮博物院北部院區正館 — photo-interpreted 150 mm FDM miniature.
Units: millimeters. Front is -Y. No interior, security features or underground
spaces. Proportions, unseen rear and reduced ornament are explicitly inferred.
Run with the pinned versions in requirements.txt.
"""
from pathlib import Path
import argparse, json, hashlib
import numpy as np
import trimesh
import manifold3d as m
P=Path(__file__).resolve().parent
parts=[];cuts=[]
def box(x,y,z,w,d,h):
    return m.Manifold.cube((w,d,h),True).translate((x,y,z))
def block(x,y,z0,z1,w,d): return box(x,y,(z0+z1)/2,w,d,z1-z0)
def roof(x,y,z,w,d,h,topw,topd):
    """Solid chamfered eave and concave-rise truncated hip; mild corner uplift."""
    # Bottom tuck permits >0.8-mm overlap with supporting wall. The short
    # bevel enlarges eaves gradually; all roofs are full solids, never shells.
    rings=[(w-3,d-3,z-1.15,0),(w,d,z+.1,.55),
           (w-.9,d-.9,z+.55,.4),
           (w*.75+topw*.25,d*.75+topd*.25,z+h*.22,.20),
           (w*.42+topw*.58,d*.42+topd*.58,z+h*.54,.1),
           (topw,topd,z+h,0)]
    verts=[]
    for ww,dd,zz,lift in rings:
        for k,(xx,yy) in enumerate([(-ww/2,-dd/2),(0,-dd/2),(ww/2,-dd/2),(ww/2,0),(ww/2,dd/2),(0,dd/2),(-ww/2,dd/2),(-ww/2,0)]):
            verts.append((x+xx,y+yy,zz+(lift if k%2==0 else 0)))
    faces=[]
    for r in range(len(rings)-1):
        for i in range(8):
            a=r*8+i;b=r*8+(i+1)%8;c=(r+1)*8+(i+1)%8;dd=(r+1)*8+i
            faces.extend([(a,b,c),(a,c,dd)])
    for i in range(1,7):faces.append((0,i+1,i))
    off=(len(rings)-1)*8
    for i in range(1,7):faces.append((off,off+i,off+i+1))
    t=trimesh.Trimesh(vertices=verts,faces=faces,process=True);t.fix_normals()
    return m.Manifold(m.Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
def roof_ridge(x,y,z,w,d,h,tw,td):
    parts.append(roof(x,y,z,w,d,h,tw,td))
    # Broad flat rim expresses the photographed 盝頂 without fragile ornaments.
    for xx in [x-tw/2,x+tw/2]:parts.append(block(xx,y,z+h-.15,z+h+.65,.85,td+1))
    for yy in [y-td/2,y+td/2]:parts.append(block(x,yy,z+h-.15,z+h+.65,tw+.8,.85))
    for xx in [x-tw/2,x+tw/2]:
        for yy in [y-td/2,y+td/2]:parts.append(block(xx,yy,z+h-.15,z+h+1.5,1.15,1.15))
def rail(x,y,z,w,d):
    # Solid low parapet with robust relief piers, not a free-standing lattice.
    parts.append(block(x,y,z-.2,z+1.45,w,d))
    n=max(1,int(w/3.8))
    for xx in np.linspace(x-w/2+.55,x+w/2-.55,n+1):parts.append(block(float(xx),y,z-.2,z+2.1,1.05,max(1.05,d)))
def front_windows(x,y,z,w,h,n,depth=.5):
    for xx in np.linspace(x-w/2+w/(2*n),x+w/2-w/(2*n),n):
        cuts.append(box(float(xx),y,z,w/n*.62,depth,h))
# A short approach plaza, main raised terrace and solid connecting museum mass.
parts += [block(0,0,0,2.4,150,91),block(0,12,2.2,12.4,140,53)]
# Rear principal gallery wall and the forward-protruding terminal pavilions.
parts += [block(0,20,12,29.1,134,27),block(-60.5,1.5,2.2,18.8,20,50),block(60.5,1.5,2.2,18.8,20,50)]
# Two shallow facade projections that flank the center and carry pale relief.
for x in [-24,24]:parts.append(block(x,5.3,12,30.3,14,7))
# Green-tile apron around the flat gallery roof, with a raised central terrace.
parts.append(roof(0,20,28.7,138,31,2.0,131,24))
for x in [-24,24]:parts.append(roof(x,5.2,30,17,9,1.6,12,4))
# Center pavilion: high broad flat-topped Chinese hip roof (盝頂), photo-based.
parts += [block(0,18.5,29,38.5,25,20),block(0,18.5,29.5,30.5,28,22.5)]
roof_ridge(0,18.5,38.2,32,26,6.1,15.8,9.8)
# Small pointed square pavilions behind the two projecting facade bays.
for x in [-33.5,33.5]:
    parts.append(block(x,24,30,37.1,9.5,9.5))
    front_windows(x,19.1,34.2,8.6,4.1,3,depth=.55)
    parts.append(roof(x,24,36.8,14.5,14.5,4.5,1.8,1.8))
    parts.append(m.Manifold.cylinder(1.8,.7,.45,20).translate((x,24,41.1)))
# The front terminal towers step forward, their roofs lower than central roof.
for x in [-60.5,60.5]:
    parts.append(roof(x,-6,18.5,24,22,1.7,18,16))
    parts.append(block(x,-6,19.7,26,16.5,15))
    roof_ridge(x,-6,25.8,23.5,21.5,4.4,10.5,8.5)
    # Wall belt, simplified balcony and engaged pilasters.
    parts.append(block(x,-6,18.1,19.1,21.7,19))
    rail(x,-15.25,19,20,1.0)
    for xx in [x-7.0,x-3.5,x,x+3.5,x+7.0]:parts.append(block(xx,-13.5,20,25.8,.9,.8))
    front_windows(x,-13.65,23.3,15,3.5,5)
    front_windows(x,-23.42,6.4,16,5.8,4)
# Lower gallery frontage, terrace rim, and simplified doorway rhythm.
parts.append(block(0,-14.5,2.3,12.4,112,4))
for side in [-1,1]:
    rail(side*39.5,-15.5,12.35,42,1.1)
    front_windows(side*38.5,-16.58,6.2,24,5.7,6,depth=.58)
# Twin visible stair flights flanking the sloped central glass canopy.
# 14 enlarged risers; these do NOT claim the real stair count.
for side in [-1,1]:
    x=side*18.9
    for k in range(14):
        y0=-34+k*1.3;top=2.4+(k+1)*(10/14)
        parts.append(block(x,(y0-14.2)/2,2.25,top,8.7,-14.2-y0+.15))
    # Sloped parapets are solid wedges connected to every step.
    for xx in [x-4.75,x+4.75]:
        pts=[(xx+dx,yy,zz) for dx in [-.62,.62] for yy,zz in [(-34.4,2.3),(-34.4,4.5),(-14.3,14.5),(-14.3,2.3)]]
        parts.append(m.Manifold.hull_points(pts))
        for k in range(0,14,2):
            yy=-33+k*1.3;zz=4.5+(yy+34.4)*(10/20.1)
            parts.append(block(xx,yy,zz-.5,zz+.8,1.1,1.1))
# Central inclined canopy represented as a solid wedge with thick ribs.
# No glass, inscriptions, unseen interior or access details are reproduced.
canopy=m.Manifold.hull_points([(x,y,z) for x in [-13,13] for y,z in [(-33,2.3),(-33,3.7),(-14.3,12.4),(-14.3,2.3)]])
parts.append(canopy)
for x in np.linspace(-12.7,12.7,9):
    parts.append(m.Manifold.hull_points([(float(x)+dx,y,z) for dx in [-.26,.26] for y,z in [(-32.8,3.4),(-32.8,4.1),(-14.4,12.0),(-14.4,12.8)]]))
rail(0,-13.9,12.35,26.5,1.15)
# Main hall windows, engaged narrow mullions and a simple pale title plaque.
front_windows(0,8.43,34.1,24,5.2,7,depth=.64)
for x in np.linspace(-11.5,11.5,8):parts.append(block(float(x),8.25,30.5,38,.8,.7))
parts.append(block(0,6.08,23.1,24.8,9,.9))
# Central front door is a shallow arched mark only.
cutdoor=block(0,6.5,12.2,17.5,2.8,1.1)+m.Manifold.cylinder(1.1,1.4,1.4,40).rotate((90,0,0)).translate((0,7.05,17.4))
cuts.append(cutdoor)
# Pale front ornament plaques are large, solid simplified relief.
for x in [-24,24]:
    parts += [block(x,1.58,20,28.6,2.2,.65),block(x,1.43,19.6,20.6,4.3,.85)]
# Continuous rear remains intentionally plain with just a structural belt.
parts.append(block(0,33.65,12.1,13.1,134,.65))
# All positive parts overlap. Recesses are blind and open to the exterior.
body=m.Manifold.batch_boolean(parts,m.OpType.Add)
body=body-m.Manifold.batch_boolean(cuts,m.OpType.Add)
assert str(body.status()).endswith('NoError'), body.status()
mesh=body.to_mesh();tm=trimesh.Trimesh(vertices=mesh.vert_properties[:,:3],faces=mesh.tri_verts,process=True)
assert tm.is_watertight and tm.is_winding_consistent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'model.stl');args=ap.parse_args()
tm.export(args.output)
print(json.dumps({'stl':str(args.output),'dimensions_mm':tm.extents.tolist(),'faces':len(tm.faces),'volume_mm3':float(tm.volume),'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()},indent=2))
