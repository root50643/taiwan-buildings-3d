"""USC M gym + N library + central court; evidence-guided exterior approximation.
Construction uses estimated metres scaled to display millimetres. No mesh repair.
"""
from pathlib import Path
import argparse, hashlib, json, struct, os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold, CrossSection, OpType
R=Path(__file__).resolve().parent

def require(v,m):
    if not v: raise RuntimeError(m)
def box(a,b,c,d,e,f):
    require(b>a and d>c and f>e,f'Invalid box {a,b,c,d,e,f}')
    return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def union(parts):return Manifold.batch_boolean(parts,OpType.Add)

def make_model(p):
    s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm'];colors=[];features=[]
    Z=lambda z:base+s*z
    B=lambda a,b,c,d,e,f:box(s*a,s*b,s*c,s*d,Z(e),Z(f))
    def C(name,a,b,c,d,e,f):colors.append(dict(material=name,bounds_mm=[s*a,s*b,s*c,s*d,Z(e),Z(f)]))
    def P(points,z0,z1,fillet=.0):
        cs=CrossSection([np.array(points)*s])
        if fillet:cs=cs.offset(-fillet).offset(fillet,circular_segments=16)
        return cs.extrude(s*(z1-z0)).translate((0,0,Z(z0)))
    def RB(a,b,c,d,e,f):return P([(a,c),(b,c),(b,d),(a,d)],e,f,.42)
    def column(x,y,r,z0,z1):return Manifold.cylinder(s*(z1-z0),s*r,s*r,20).translate((s*x,s*y,Z(z0)))
    def beam(a,b,r):
        a=np.array([s*a[0],s*a[1],Z(a[2])]);b=np.array([s*b[0],s*b[1],Z(b[2])]);d=b-a;L=np.linalg.norm(d);w=d/L
        helper=np.array([0,0,1]) if abs(w[2])<.9 else np.array([1,0,0]);u=np.cross(helper,w);u/=np.linalg.norm(u);v=np.cross(w,u)
        mat=np.column_stack([u,v,w,a]);return Manifold.cylinder(L,s*r,s*r,20).transform(mat)
    def recess(o,side,face,u0,u1,z0,z1,depth=.25,material='glass'):
        if side=='west':q=(face-.02,face+depth,u0,u1,z0,z1)
        elif side=='east':q=(face-depth,face+.02,u0,u1,z0,z1)
        elif side=='south':q=(u0,u1,face-.02,face+depth,z0,z1)
        else:q=(u0,u1,face-depth,face+.02,z0,z1)
        C(material,*q);return o-B(*q)
    def grid(o,side,face,u0,u1,levels,pitch,depth=.25,skip=None,material='screen'):
        for u in np.arange(u0,u1-.2,pitch):
            aa=max(u+.45,u0+.75);bb=min(u+pitch-.45,u1-.75)
            for z0,z1 in zip(levels[:-1],levels[1:]):
                lo=z0+.75;hi=z1-.75
                if skip and skip(aa,bb,lo,hi):continue
                if bb>aa and hi>lo:o=recess(o,side,face,aa,bb,lo,hi,depth,material)
        return o
    a,b,c,d=p['base_bounds_mm'];parts=[box(a,b,c,d,0,base)]
    colors.append(dict(material='base',bounds_mm=[a,b,c,d,0,base+.001]))
    # West-court descending access: display relief 1.0 mm below grade, not a scale B1 room.
    parts[0]-=B(38.6,43.6,7.5,13.7,-.83,.03)
    for i in range(4):parts.append(RB(38.7,43.5,7.5+i*1.0,8.52+i*1.0,-.85,-.62+i*.205))
    # Raised turf covers the below-ground connection; only exterior levels are modelled.
    court=P([(40,14),(105,14),(109,18),(109,56),(40,56)],-.03,.50,.40)
    parts.append(court);C('lawn',39.8,109.2,13.8,56.2,.49,.51)
    # North path and edge bars are broad full-root solids, no thin rail wires.
    parts.append(B(40,109,56.3,58.9,-.02,.25));C('walk',40,109,56.3,58.9,.24,.26)
    for x0,x1 in [(40,52),(58,75),(82,96),(101,109)]:parts.append(B(x0,x1,59.5,60.7,-.02,.8))
    # M: main long metal hall with an open, recessed lower courtyard frontage.
    a,b,c,d=p['M_main_bounds_m'];H=p['M_estimated_main_roof_m']
    m=B(a,b,c,d,-.03,H-.9)
    C('metal',a-.01,b+.01,c-.01,d+.01,8,H-.89)
    m-=B(26.5,b+.1,7,59.5,-.02,8.0)
    # A lower glazed wall behind the open colonnade; the north concrete bay remains solid.
    m=grid(m,'east',26.5,8,58,[0,3.8,8.0],5.3,.32,material='glass')
    m=grid(m,'east',b,c,d,[8.0,11.4],4.2,.35,material='glass')
    m=grid(m,'east',b,c,d,[11.4,17.8,H-.9],4.2,.25,material='screen')
    m=grid(m,'west',a,c,d,[1.0,8.0,17.8,H-.9],4.2,.25,material='screen')
    m=grid(m,'north',d,a,b,[8.0,17.8,H-.9],4.3,.25,material='screen')
    m=grid(m,'south',c,a,b,[8.0,17.8,H-.9],4.3,.25,material='screen')
    parts.append(m)
    # Very shallow crown flattened for print robustness; continuous thick metal cap.
    roof=B(a-.3,b+.3,c-.3,d+.3,H-1,H+.10)
    for yy in np.arange(c+1.973,d-1.0,2.6):roof-=B(a-.4,b+.4,yy,yy+.65,H-.12,H+.3)
    parts.append(roof);C('metal',a-.31,b+.31,c-.31,d+.31,H-1.01,H+.11)
    # Low frontage columns, plus the distinctive V under the north landing.
    for yy in [10,20,30,40,58]:parts.append(column(34.5,yy,.66,-.05,8.1))
    parts.append(B(34.6,41.5,43.0,58.0,7.0,8.15));C('concrete',34.6,41.5,43,58,7,8.15)
    for yy in [43.5,56.7]:parts.append(beam((39.4,50.1,-.06),(39.4,yy,7.3),.75))
    # Blunt low print gusset keeps the V branch junction rooted above the base.
    parts.append(RB(38.4,40.4,47.7,52.5,-.03,1.6))
    # Exterior stair rises northward to the landing; solid stepped underside is a print simplification.
    for i in range(20):
        y=20+i*1.15;parts.append(RB(36.1,39.1,y,y+1.2,-.04,(i+1)*.35+.017*((i+1)/20)**2))
    # M southern low wing and stair tower visible outside the long metal roof.
    low=B(6,34,-14.2,.3,-.03,8.4)
    low=grid(low,'south',-14.2,7,33,[.5,4.1,8.3],5.2,.30,material='glass')
    low=grid(low,'east',34,-13.8,-2,[.5,4.1,8.3],5.2,.30,material='glass')
    parts.append(low);parts.append(B(6.8,13,-18,-10.5,-.03,13.6))
    tower=parts.pop();tower=grid(tower,'south',-18,7,12.8,[.5,4.7,9,13.5],5.8,.32,material='glass');parts.append(tower)
    # N plan: western bar + northern arm, southeast volume, and recessed roof slot.
    NH=p['N_estimated_main_roof_m'];SH=p['N_estimated_southeast_roof_m']
    n=union([B(113,125.0,24,69,5.4,NH),B(124.8,138.8,61.6,69,5.4,NH),B(124.8,150.3,27.7,58.5,5.4,SH),B(124.8,130,24,28,5.4,NH)])
    # Open double-height north-half court-facing aperture. Cut through west bar to the slot.
    n-=B(112.9,126.0,40.5,58.9,10.35,19.75)
    # Visible façade screen bands. They are not asserted to be six usable floors.
    skip=lambda aa,bb,zz,zt: (aa<59.4 and bb>40.0 and zz<20.2 and zt>10.0) or (bb>52.3 and zz<10.3)
    n=grid(n,'west',113,24,60.8,[5.4,10.3,15.0,19.8,24.4,29],5.5,.25,skip,'screen')
    # Continuous north-end concrete strip and sparse short slots seen in 06-r.
    for zz in [8.0,12.8,17.6,22.4]:n=recess(n,'west',113,62.0,64.1,zz,zz+.62,.24,'glass')
    # North short facade is mostly concrete with a grouped window zone, not a curtain-wall invention.
    n=grid(n,'north',69,115.5,121.7,[7.15,11.65,16.15,20.65],3.1,.25,material='glass')
    for zz in [9.0,17.5,25.0]:n=recess(n,'north',69,124.5,126.4,zz,zz+.65,.24,'glass')
    n=grid(n,'east',150.3,27.7,58.5,[5.4,10.3,15.0,19.8,24.4,SH],5.1,.25,material='glass')
    n=grid(n,'south',24,113,130,[5.4,10.3,15.0,19.8,24.4,29],4.25,.25,material='glass')
    # Lower inset roof surfaces express parapets, maintaining thick roots.
    n-=B(114.1,123.9,25.1,67.9,NH-.65,NH+.1)
    n-=B(125.0,137.7,62.7,67.9,NH-.65,NH+.1)
    n-=B(128,149.2,28.8,57.4,SH-.65,SH+.1)
    C('roof',114,124,25,68,NH-.66,NH-.64);C('roof',125,138,62,68,NH-.66,NH-.64);C('roof',128,149.3,28.7,57.5,SH-.66,SH-.64)
    parts.append(n)
    # Ground-floor glass/core at north; a recessed east-side receiving building.
    core=B(114.0,124.6,61.2,68.4,-.03,5.5);core=grid(core,'west',114,61.2,68.4,[0,5.4],3.6,.28,material='glass');parts.append(core)
    ground=B(124.2,149.6,28.2,58.0,-.03,5.5);ground=grid(ground,'west',124.2,28.2,58,[0,5.4],5,.30,material='glass');parts.append(ground)
    for yy in [25.2,32.2,39.2,46.2,53.2,60.2]:parts.append(RB(113.2,114.6,yy-.64,yy+.64,-.04,5.52))
    # Middle stair and landing visible within the actual upper void.
    parts.append(RB(113.1,121.5,52.1,53.5,10.1,20.0))
    parts.append(B(113.05,125.1,40.45,52.3,14.85,15.60))
    # The horizontal walk intentionally stops behind the front edge leaving the opening legible.
    for i in range(7):parts.append(RB(118.3,121.0,53.2+i*.77,55.20+i*.77,10.15,10.35+(i+1)*.75))
    # Lower middle exterior stair, plus side stair by south end, coarse full-root steps.
    for i in range(9):parts.append(RB(118.5,121.3,51.0+i*.8,52.55+i*.8,-.03,(i+1)*.62+.013*((i+1)/9)**2))
    for i in range(7):parts.append(RB(113.2,120.0,19.0+i*.75,19.82+i*.75,-.03,(i+1)*(5.4/7)))
    # Roof slot: shallow glass gutter, kept visibly lower than neighbouring roofs.
    parts.append(B(125.0,127.5,29.0,61.7,24.9,26.2));C('glass',125,127.5,29,61.7,26.19,26.21)
    # Major rooftop service block only, height estimated; no invented rooftop machine inventory.
    parts.append(B(129.5,137.5,63.2,67.5,NH-.7,NH+1.0));C('metal',129.5,137.5,63.2,67.5,NH-.7,NH+1.0)
    # Shallow sunk access strips at west/east edges of court, expressed as depressions in podium.
    # Because underground floors are omitted, these are external relief, not full B1/B2 interiors.
    # Six uniquely shaped, blunt sloped skylights at traced as-built centres.
    footprints=[ [(-2.8,-.8),(1.9,-1.1),(2.6,.5),(-1.7,1.2)], [(-2.6,-.8),(2.0,-.8),(2.6,.6),(-1.7,1.0)], [(-2.1,.6),(.3,-1.2),(2.1,.7),(.1,1.0)], [(-2.6,-.9),(1.8,-1.0),(2.4,1),(-2.2,1.2)], [(-2.0,.9),(.2,-1.0),(2.2,.5),(1.8,1.0)], [(-2.5,-.8),(2.4,-.7),(2.4,.8),(-1.8,1.1)] ]
    for i,(px,py) in enumerate(p['skylight_centres_orthophoto_px']):
        x=(px-50)*p['orthophoto_resolution_m_per_px'];y=(520-py)*p['orthophoto_resolution_m_per_px']
        pts=[(x+dx,y+dy) for dx,dy in footprints[i]]
        # Convex hull of 1.1 mm diameter spheres gives genuinely rounded 3D edges.
        # Both base and sloping top are rooted; no acute triangular glass tips.
        slope=.22 if i%2==0 else -.18
        spheres=[]
        for xx,yy in pts:
            for zz in [-.12,1.10+slope*(yy-y)]:
                spheres.append(Manifold.sphere(.55,16).translate((xx*s,yy*s,Z(zz))))
        q=Manifold.batch_hull(spheres)
        # A flat blunt crest truncates the last 0.45 mm spherical cap, so top XY slices retain width.
        top=max(Z(1.10+slope*(yy-y)) for xx,yy in pts)+.10
        q=q-box((x-6)*s,(x+6)*s,(y-5)*s,(y+5)*s,top,top+10)
        parts.append(q);C('skylight',x-3,x+3,y-1.5,y+1.5,.51,2.5)
    # N front long low glazed light well is distinct from the six lawn hoods.
    parts.append(RB(107.0,111.5,43.0,54.5,-.03,1.0));C('skylight',106.7,111.6,41.9,55.6,.7,1.01)
    # Low rectangular vent/light wells shown in official photos next to both buildings.
    for aa,bb,cc,dd in [(40,51,42,47),(40,51,18,24),(105,110,34,42),(105,110,55,61)]:
        parts.append(B(aa,bb,cc,dd,-.03,.85));C('metal',aa,bb,cc,dd,.80,.86)
    result=union(parts)
    require(str(result.status()).endswith('NoError'),str(result.status()))
    require(len(result.decompose())==1,f'{len(result.decompose())} separate solids')
    return result,colors

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],dtype=np.float32);f=np.asarray(m.tri_verts,dtype=np.int64);t=v[f]
    raw=bytearray(b'USC M+N+court | source-guided exterior display | mm'.ljust(80,b'\0')+struct.pack('<I',len(t)))
    for q in t:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(n);require(L>0,'Degenerate export');n/=L
        raw+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(raw);return len(t)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R);args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,colors=make_model(p);f=args.output_dir/'model.stl';n=save_stl(m,f)
    (args.output_dir/'color-regions.json').write_text(json.dumps(colors,indent=2)+'\n')
    report={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'export_axes':'+X east, +Y north, +Z up','notes':'Construction only. Original-STL validation and independent appearance review are separate.'}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
