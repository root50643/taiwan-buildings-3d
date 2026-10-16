"""BWBC Zongde Hall. Source-constrained 2024 exterior, nominal 1:400.
All work is independently constructed for this building. No mesh repair.
Public architectural facts and estimated dimensions; photos never used as textures.
"""
from pathlib import Path
import argparse, hashlib, json, struct, os, math
os.environ['OMP_NUM_THREADS']='1'; os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold, CrossSection, OpType
R=Path(__file__).resolve().parent.parent

def require(v,m):
    if not v: raise RuntimeError(m)
def box(a,b,c,d,e,f):
    require(b>a and d>c and f>e, str((a,b,c,d,e,f)))
    return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def union(parts):return Manifold.batch_boolean(parts,OpType.Add)

def make_model(p):
    s=p['scale_mm_per_estimated_m']; base=p['base_thickness_mm']; regions=[];parts=[];features=[]
    Z=lambda z:base+s*z
    def C(mat,a,b,c,d,e,f,**extra):regions.append(dict(material=mat,bounds_mm=[a*s,b*s,c*s,d*s,Z(e),Z(f)],**extra))
    def B(a,b,c,d,e,f):return box(a*s,b*s,c*s,d*s,Z(e),Z(f))
    def P(poly,z0,z1,r=0):
        cs=CrossSection([np.array(poly)*s])
        if r:cs=cs.offset(-r).offset(r,circular_segments=16)
        return cs.extrude(s*(z1-z0)).translate((0,0,Z(z0)))
    def RB(a,b,c,d,e,f,r=None):return P([(a,c),(b,c),(b,d),(a,d)],e,f,p['minimum_radius_mm'] if r is None else r)
    def add(q,name=None):
        require(str(q.status()).endswith('NoError'),'Bad part '+str(name));parts.append(q)
        if name:features.append(name)
    def cb(name,a,b,c,d,e,f,rounded=False):
        add(RB(a,b,c,d,e,f) if rounded else B(a,b,c,d,e,f));C(name,a-.001,b+.001,c-.001,d+.001,e-.001,f+.001)
    def col(x,y,z0,z1,w=None):
        w=w or p['column_width_m'];add(RB(x-w/2,x+w/2,y-w/2,y+w/2,z0,z1))
    def recess(o,side,face,u0,u1,z0,z1,depth=.25):
        if side=='-x':q=(face-.03,face+depth,u0,u1,z0,z1)
        elif side=='+x':q=(face-depth,face+.03,u0,u1,z0,z1)
        elif side=='-y':q=(u0,u1,face-.03,face+depth,z0,z1)
        else:q=(u0,u1,face-depth,face+.03,z0,z1)
        C('glass',*q);return o-B(*q)
    def windows(o,side,face,lo,hi,z0,z1,pitch=7.2,skip=None):
        for u in np.arange(lo,hi-.6,pitch):
            a=u+.65;b=min(u+pitch-.65,hi-.45)
            if b-a<1:continue
            if skip and skip(a,b):continue
            o=recess(o,side,face,a,b,z0,z1)
            # Raised mullions are geometry, original surface retained between recesses.
            for v in np.arange(a+1.8,b-1,1.8):
                if side=='-x':cb('concrete',face,face+.28,v-.26,v+.26,z0,z1)
                elif side=='+x':cb('concrete',face-.28,face,v-.26,v+.26,z0,z1)
                elif side=='-y':cb('concrete',v-.26,v+.26,face,face+.28,z0,z1)
                else:cb('concrete',v-.26,v+.26,face-.28,face,z0,z1)
        return o
    # Root base and a thin integrated courtyard surface. No surrounding campus massing.
    a,b,c,d=p['base_bounds_m'];add(box(a*s,b*s,c*s,d*s,0,base));C('base',a,b,c,d,-base/s,0)
    cb('walk',-1,59,-.5,57,-.025,.15)
    cb('lawn',13.5,42.0,18.2,43.2,.13,.32)
    cb('walk',19.0,35,-8.0,4.0,-.01,.17)
    # Four outward-stepping high floors. Top-floor library absorbs the inner corridor.
    levels=p['floor_levels_m']; high_top=16.50
    fin_data=json.loads((R/'source/upper_wing_fin_positions.json').read_text())
    fin_positions=fin_data['centres_local_x_m_by_floor'];left_fin_positions=fin_data['centres_local_y_m_by_floor']
    for n,z in enumerate(levels):
        exp=n*p['per_floor_outer_expansion_m'];a=-exp;b=65.42+exp;c=-exp;d=56.42+exp
        top=levels[n+1] if n<3 else high_top
        innerx=9.5 if n<3 else 13.15;innery=47.0 if n<3 else 43.65
        inset=.25 if n==0 else 1.10
        # Room boxes are exterior solids; interiors are deliberately omitted.
        left=B(a+inset,innerx,c+inset,d-inset,z-.12,top-.24)
        upper=B(innerx-.05,b-inset,innery,d-inset,z-.12,top-.24)
        lowwin=z+.9;hiwin=top-.95
        left=windows(left,'-x',a+inset,c+.4,d-.4,lowwin,hiwin,6.7)
        left=windows(left,'-y',c+inset,a+.45,innerx-.2,lowwin,hiwin,6.8)
        left=windows(left,'+y',d-inset,a+.45,innerx-.2,lowwin,hiwin,6.8)
        upper=windows(upper,'+y',d-inset,innerx,b-.35,lowwin,hiwin,7.0,lambda aa,bb:aa<45.5 and bb>34.5)
        upper=windows(upper,'+x',b-inset,innery,d-.5,lowwin,hiwin,6.8)
        # Inward windows face open galleries; top library has a continuous band.
        left=windows(left,'+x',innerx,max(c+.5,11),43.5,z+1.1 if n==3 else lowwin,z+2.45 if n==3 else hiwin,6.5)
        upper=windows(upper,'-y',innery,13.4,b-.4,z+1.1 if n==3 else lowwin,z+2.45 if n==3 else hiwin,7.2)
        # The publicly visible central staircase is expressed as recessed vertical bays.
        upper=recess(upper,'+y',d-inset,35.3,38.8,z+.48,top-.50,depth=1.1)
        upper=recess(upper,'+y',d-inset,39.5,44.4,top-1.20,top-.55,depth=.28)
        add(left);add(upper)
        # L floor, including 3.5m inward gallery and the projecting high-wing ends.
        slab=union([B(a,b,43.5,d,z-.42,z+.12),B(a,13.2,c,43.6,z-.42,z+.12)])
        add(slab,'high_floor_'+str(n+1));C('concrete',a,b,c,d,z-.421,z+.121)
        # Source-led vertical screen fins: more densely packed at the upper floor.
        if n>0:
            t=p['fin_thickness_m'];pitch=2.45 if n<3 else 1.85;fw=1.25
            for y in left_fin_positions[str(n+1)]:
                yy=max(c+.04,min(y-fw/2,d-fw-.04))
                cb('bamboo',a+.40,a+.40+t,yy,yy+fw,z+.08,top-.20,True)
            top_centres = fin_positions[str(n+1)]
            for x in top_centres:
                xx=max(a+.04,min(x-t/2,b-t-.04))
                if xx<a+inset:continue  # Corner symbol belongs to the -X return, not a narrow duplicate.
                cb('bamboo',xx,xx+t,d-.4-fw,d-.4,z+.08,top-.20,True)
            for x in np.arange(a+.7,innerx-.3,pitch):cb('bamboo',x,x+fw,c+.4,c+.4+t,z+.08,top-.20,True)
            for y in np.arange(innery+.5,d-.5,pitch):
                if y+fw>d-.4-fw:continue  # +Y corner blade already represents this return.
                cb('bamboo',b-.4-t,b-.4,y,y+fw,z+.08,top-.20,True)
    # Lower gallery colonnades, open between the room fronts and court-side beam line.
    for x,y in [(13.0,yy) for yy in [14.6,23.6,32.6,43.5]]+[(xx,43.5) for xx in [13,23.8,34.6,45.4]]:
        col(x,y,.13,12.4)
    # Two-floor low wings and deeply open entry. The court-facing bridge stays across entry.
    for n,z in enumerate(levels[:2]):
        top=levels[n+1];outer=58.0+.30*n;front=3.6-.30*n
        lowright=B(49,outer,11.0,43.65,z-.1,top-.25)
        if n==0:
            lowright-=B(48.9,outer+.1,25.5,44.0,z-.2,top-.20)
            # p1 room13: keep x49..52 corridor, preparation room connects to high wing.
            preparation=B(52.0,58.0,43.5,47.40,z-.1,top-.25)
            preparation=recess(preparation,'-y',43.5,54.0,55.2,z+.05,z+2.5)
            add(preparation)
        lowright=windows(lowright,'+x',outer,11.2,43.3,z+1.05 if n==1 else z+.85,top-1.40 if n==1 else top-.95,6.2,lambda aa,bb:n==0 and aa<43.6 and bb>25.5)
        lowright=windows(lowright,'-x',49,11.2,43.3,z+1.05 if n==1 else z+.85,top-1.40 if n==1 else top-.95,6.2,lambda aa,bb:n==0 and aa<43.6 and bb>25.5)
        lowbottom=B(34.6,outer,front,11.05,z-.1,top-.25)
        lowbottom=windows(lowbottom,'-y',front,34.6,outer-.2,z+1.05 if n==1 else z+.85,top-1.40 if n==1 else top-.95,6.6)
        lowbottom=windows(lowbottom,'+y',11.05,34.6,48.8,z+1.05 if n==1 else z+.85,top-1.40 if n==1 else top-.95,6.6)
        add(lowright);add(lowbottom)
        add(union([B(45.2,outer+.55,10.8,43.7,z-.42,z+.12),B(13.0,outer+.55,front-.55,14.75,z-.42,z+.12)])-B(13.3,34.5,front-.6,10.8,z-.5,z+.2) if n==1 else union([B(45.2,outer+.55,10.8,43.7,z-.42,z+.12),B(13.0,outer+.55,front-.55,14.75,z-.42,z+.12)]))
    # Small outdoor platform p1 space15, exterior outline retained. Height estimated.
    cb('walk',57.70,65.8,37.0,43.65,-.02,.62)
    cb('walk',65.6,66.4,37.0,43.5,-.02,.40)
    cb('walk',66.2,67.0,37.0,43.5,-.02,.25)
    # Roof garden slab: continuous L cap over low wings, no third storey wall.
    z=levels[2]
    add(union([B(45.2,60.0,2.3,43.7,z-.50,z+.10),B(13.0,60.0,2.3,14.75,z-.50,z+.10)]),'low_roof_garden')
    # All visible low wing/gallery columns remain full-root solids.
    for x,y in [(xx,14.6) for xx in [13,23.8,34.6,45.4]]+[(45.6,yy) for yy in [14.6,23.6,32.6,43.5]]+[(13,3.6),(23.8,3.6),(34.6,3.6),(49,25.7),(58,25.7),(49,37.3),(58,37.3)]:col(x,y,.13,8.58)
    # Long parapets / mesh-rail simplifications are rounded, integrated guard panels.
    t=p['rail_thickness_m']
    for z,arms in [(4.63,True),(8.47,True),(12.31,False)]:
        if z<12:
            cb('rail',12.75,13.25,15.0,43.1,z+.05,z+1.13,True)
            cb('rail',12.8,45.7,43.25,43.75,z+.05,z+1.13,True)
        if arms:
            cb('rail',45.15,45.85,14.7,43.7,z+.05,z+1.13,True)
            cb('rail',12.8,45.7,14.35,14.85,z+.05,z+1.13,True)
    # Outer low-roof guard and garden beds. Broad raised beds, no arbitrary trees.
    add(P([(12.8,2.55),(59.95,2.55),(59.95,43.3),(59.45,43.3),(59.45,3.05),(12.8,3.05)],8.50,9.55,p['minimum_radius_mm']))
    C('rail',12.79,59.96,2.54,43.31,8.49,9.56)
    cb('garden',52.1,58.4,5.0,38.8,8.50,8.90,True)
    cb('garden',19.0,51.9,4.8,8.5,8.50,8.90,True)
    # Low rooftop utility pockets seen in p3 and bird's-eye photography.
    cb('concrete',50.8,57.6,34.4,43.2,8.52,9.8)
    cb('concrete',13.2,22.4,4.0,8.7,8.52,9.5)
    # L photovoltaic canopy. Inner edge reaches 6m into the courtyard; not a filled courtyard.
    # Canopy inclination is not measured; merged level plates are a documented approximation.
    canz=11.65
    canopy=union([B(39.5,50.9,10.5,43.55,canz,canz+.50),B(13.1,50.9,10.5,21.0,canz,canz+.50)])
    add(canopy,'L_photovoltaic_canopy');C('solar',13.0,51.0,10.4,43.6,canz-.001,canz+.501)
    # Outer open frame extensions are visible in p4 and photo017.
    for y in np.arange(11.0,43.0,3.3):cb('steel',50.5,52.0,y,y+.50,canz-.02,canz+.50,True)
    cb('steel',51.5,52.0,10.5,43.55,canz-.02,canz+.50,True)
    for x in np.arange(13.6,50.0,3.3):cb('steel',x,x+.50,9.3,10.9,canz-.02,canz+.50,True)
    cb('steel',13.1,52.0,9.3,9.8,canz-.02,canz+.50,True)
    # Module grid is rendered procedurally, not a measured module inventory.
    # Open edge framing does not extend over or enclose the clear central court.
    for x,y in [(41.8,yy) for yy in [18.2,24.3,30.4,36.5,42.6]]+[(xx,18.2) for xx in [16.7,23.0,29.3,35.6]]:
        r=p['canopy_column_diameter_m']/2
        q=Manifold.cylinder(s*(canz+.10-.13),s*r,s*r,16).translate((s*x,s*y,Z(.13)));add(q)
        C('steel',x-r-.001,x+r+.001,y-r-.001,y+r+.001,.12,canz+.12)
    # Edge frames and their obvious supports on the roof garden side.
    for y in [15,24,33,42]:col(50.6,y,8.50,canz+.1,.60)
    for x in [17,26,35,44]:col(x,10.8,8.50,canz+.1,.60)
    # Entrance broad stairs, rise to intermediate and second-floor landing.
    for i in range(14):add(B(16.6,23.2,3.7+i*.49,4.23+i*.49,.14,.15+(i+1)*.32))
    cb('concrete',16.6,23.3,9.9,11.35,3.70,4.72)
    # In-court exposed stair flights. Solid stepped undersides are print-only simplification.
    for i in range(12):add(B(42.5,44.85,22.5+i*.55,23.10+i*.55,.14,.18+(i+1)*.37))
    cb('concrete',42.5,45.7,28.8,30.2,4.18,4.77)
    for i in range(11):add(B(16.2+i*.67,16.94+i*.67,14.65,16.9,4.52,4.72+(i+1)*.34))
    cb('concrete',23.3,25.0,14.65,17.0,8.00,8.57)
    # Printed mesh-rail substitutes: continuous sloping guard panels rooted into steps.
    # They preserve both direction and landing without claiming mesh-wire fidelity.
    def stair_guard(axis,lo,hi,a,b,z0,z1,floor):
        pts=[]
        for w in [lo,hi]:
            angle=math.atan2(z1-z0,b-a);du=-1.05*math.sin(angle);dz=1.05*math.cos(angle)
            # Keep the visible top line, extend bottom normally into every step.
            rootu=.52*math.sin(angle);rootz=-.52*math.cos(angle)
            for u,z in [(a+rootu,z0+rootz),(b+rootu,z1+rootz),(b+du,z1+dz),(a+du,z0+dz)]:
                pts.append((w,u,z) if axis=='y' else (u,w,z))
        # Genuine longitudinal edge rounds: constant rounded profile extruded
        # along the flight. The .45mm radius is geometric, not a QA exemption.
        cs=CrossSection([np.array([(lo,-.52),(hi,-.52),(hi,1.05),(lo,1.05)])*s])
        cs=cs.offset(-p['minimum_radius_mm']).offset(p['minimum_radius_mm'],circular_segments=16)
        q=cs.extrude(math.hypot(b-a,z1-z0)*s)
        sn,co=math.sin(angle),math.cos(angle)
        matrix=([[1,0,0,0],[0,-sn,co,a*s],[0,co,sn,Z(z0)]] if axis=='y' else
                [[0,-sn,co,a*s],[1,0,0,0],[0,co,sn,Z(z0)]])
        q=q.transform(np.array(matrix))
        bb=np.array(pts)
        if bb[:,2].min()<floor:q-=B(bb[:,0].min()-.1,bb[:,0].max()+.1,bb[:,1].min()-.1,bb[:,1].max()+.1,floor-5,floor)
        add(q)
        # Full-root, flat-topped end posts prevent free pointed layer islands.
        for u,zb,zt in [(a+du/2,max(floor,z0-.8),z0+dz+.10),(b+du/2,max(floor,z1-.8),z1+dz+.10)]:
            if axis=='y':cb('rail',lo,hi,u-.70,u+.70,zb,zt,True)
            else:cb('rail',u-.70,u+.70,lo,hi,zb,zt,True)
        C('rail',bb[:,0].min(),bb[:,0].max(),bb[:,1].min(),bb[:,1].max(),bb[:,2].min(),bb[:,2].max())
    for xx in [16.6,22.72]:stair_guard('y',xx,xx+.48,3.8,10.25,.35,4.55,.14)
    for xx in [42.5,44.37]:stair_guard('y',xx,xx+.48,22.65,28.90,.40,4.60,.14)
    for yy in [14.65,16.42]:stair_guard('x',yy,yy+.48,16.35,23.45,4.70,8.38,4.52)

    # Main L hipped roof. Two unioned equal-pitch rectangles produce the inward valley.
    a,b,c,d=p['main_eave_bounds_m'];w=p['main_roof_leg_width_m'];e=p['main_eave_height_m'];h=.25*w/2
    def hip(a,b,c,d,axis):
        pts=[(x,y,e-.50) for x in [a,b] for y in [c,d]]+[(x,y,e) for x in [a,b] for y in [c,d]]
        if axis=='y':
            xc=(a+b)/2;pts += [(xc,c+w/2,e+h),(xc,d-w/2,e+h)]
        else:
            yc=(c+d)/2;pts += [(a+w/2,yc,e+h),(b-w/2,yc,e+h)]
        q=Manifold.hull_points(np.array([(x*s,y*s,Z(z)) for x,y,z in pts]))
        # Blunt 0.48m-wide ridge: caps the highest .06m, retaining 2.5:10 pitch elsewhere.
        return q-B(a-1,b+1,c-1,d+1,e+h-.06,e+h+2)
    roof=union([hip(a,a+w,c,d,'y'),hip(a,b,d-w,d,'x')])
    # Source-audited equipment screen over the long wing. The local, closed-bottom
    # continuous foot groove are declared manufacturing details, not source features. They
    # locally remove roof material while retaining the ridge, eaves and slopes
    # outside the groove, as well as the open screen gaps.
    xa,xb,ya,yb=36.75,44.88,47.14,56.09
    slats=[]
    for x in np.arange(xa,xb-.2,1.0):
        for y in [ya,yb-.50]:slats.append((x,min(x+.50,xb),y,y+.50))
    for y in np.arange(ya+.7,yb-.7,1.0):
        for x in [xa,xb-.50]:slats.append((x,x+.50,y,y+.50))
    pocket_gap=.48; groove_floor=17.15
    # Smooth closed-bottom ring with walls perpendicular to each roof slope.
    # Vertical cutters leave acute thin roof lips. These genuine inclined walls
    # preserve finite roof thickness at the lip; no ray samples are changed.
    def roof_normal_socket(x0,x1,y0,y1):
        def ys(y,z,north):
            zr=e+.25*((d-y) if north else (y-(d-w)))
            return y+(-1 if north else 1)*.25*(zr-z)
        pts=[(x*s,ys(y,z,north)*s,Z(z)) for z in [groove_floor,20.0]
             for x in [x0,x1] for y,north in [(y0,False),(y1,True)]]
        return Manifold.hull_points(np.array(pts))
    outer=roof_normal_socket(xa-pocket_gap,xb+pocket_gap,ya-pocket_gap,yb+pocket_gap)
    inner=roof_normal_socket(xa+.50+pocket_gap,xb-.50-pocket_gap,ya+.50+pocket_gap,yb-.50-pocket_gap)
    roof-=outer-inner
    add(roof,'L_equal_pitch_hip_roof');C('roof',a-.01,b+.01,c-.01,d+.01,e-.51,e+h+.01)
    for x0,x1,y0,y1 in slats:
        cb('bamboo',x0,x1,y0,y1,groove_floor-.35,20.60,True)
    # Two compact ridge-side saddles maintain a broad material route across the
    # foot groove. Their tops sit only .135m above the blunt ridge, not a skirt.
    for x0,x1 in [(36.15,37.85),(43.78,45.48)]:
        cb('roof',x0,x1,50.65,52.55,17.0,19.05,True)
    for x0,x1,y0,y1 in [(xa,xb,ya,ya+.5),(xa,xb,yb-.5,yb),(xa,xa+.5,ya,yb),(xb-.5,xb,ya,yb)]:
        cb('bamboo',x0,x1,y0,y1,20.10,20.65,False)
    result=union(parts)
    require(str(result.status()).endswith('NoError'),str(result.status()))
    return result,regions,features

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],dtype=np.float32);f=np.asarray(m.tri_verts,dtype=np.int64);tri=v[f]
    raw=bytearray(b'BWBC Zongde Hall | source-led exterior | local XY | mm'.ljust(80,b'\0')+struct.pack('<I',len(tri)))
    for q in tri:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(n);require(L>0,'Degenerate export');n/=L
        raw+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(raw);return len(tri)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);file=args.output_dir/'model.stl';n=save_stl(m,file)
    (args.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n')
    report=dict(revision=p['revision'],triangles=n,stl_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),manifold_status=str(m.status()),components=len(m.decompose()),volume_mm3=m.volume(),bounds_mm=m.bounding_box(),features=features,axes=p['local_axes'],status='Appearance draft. No strict geometry/print QA claim.')
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
