"""Original Tianmu Gymnasium A exterior reconstruction. Nominal 1:500.
Source constrained geometry. No source imagery, hidden repairs, or previous model geometry.
"""
from pathlib import Path
import argparse,hashlib,json,struct,os,math,shutil
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,Mesh,CrossSection,OpType
R=Path(__file__).resolve().parent.parent

def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def union(q):return Manifold.batch_boolean(q,OpType.Add)
def box(a,b,c,d,e,f):return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def wave_height(u,side):
    # Measured overall envelope, photograph-led asymmetrical span rhythm.
    # Piecewise smooth lobes, not an assertion of actual curved-panel equations.
    if side in ('west','east'):
        knots=[(-33.85,8.6),(-16.9,10.05),(16.9,10.05),(33.85,8.6)]
        crests=[11.9,13.28,11.9]  # 1.08mm minimum printed fascia at central crest.
    elif side=='south':
        knots=[(-43.05,9.0),(-2.0,8.1),(43.05,8.8)]
        crests=[13.0,12.6]
    else:
        # North only partially photographed: conservative continuous band;
        # far-west wave timing remains estimated, explicitly not mirrored south.
        knots=[(-43.05,9.0),(-1.5,9.0),(43.05,8.9)]
        crests=[12.1,12.8]
    for i,((a,za),(b,zb)) in enumerate(zip(knots,knots[1:])):
        if a-1e-8<=u<=b+1e-8:
            # Broad flat end returns avoid acute razor tips at the isolated corner reveal.
            # Their 0.8m exposed length is a 1.6mm print-scale manufacturing return.
            if i==0:
                a+=.95
                if u<=a:return za
            if i==len(crests)-1:
                b-=.95
                if u>=b:return zb
            t=(u-a)/(b-a)
            return za*(1-t)+zb*t+(crests[i]-(za+zb)/2)*math.sin(math.pi*t)
    return knots[0][1]

def make_model(p):
    s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm'];parts=[];regions=[];features=[]
    Z=lambda z:base+s*(z+.5)
    def B(a,b,c,d,e,f):return box(a*s,b*s,c*s,d*s,Z(e),Z(f))
    def add(q,name):
        require(str(q.status()).endswith('NoError'),name+': '+str(q.status()));parts.append(q);features.append(name)
    def color(mat,a,b,c,d,e,f):regions.append({'material':mat,'bounds_mm':[a*s,b*s,c*s,d*s,Z(e),Z(f)]})
    def cb(mat,a,b,c,d,e,f,name=None):add(B(a,b,c,d,e,f),name or mat);color(mat,a-.001,b+.001,c-.001,d+.001,e-.001,f+.001)
    def height_solid(bounds,ztop,bottom,nx,ny):
        a,b,c,d=bounds;vs=[];fs=[]
        for zfun in [ztop,bottom if callable(bottom) else lambda x,y:bottom]:
            for j in range(ny+1):
                y=c+(d-c)*j/ny
                for i in range(nx+1):
                    x=a+(b-a)*i/nx;vs.append((x*s,y*s,Z(zfun(x,y))))
        N=(nx+1)*(ny+1)
        for j in range(ny):
            for i in range(nx):
                q=j*(nx+1)+i;r=q+nx+1
                fs.extend([(q,q+1,r+1),(q,r+1,r),(q+N,r+1+N,q+1+N),(q+N,r+N,r+1+N)])
        boundary=[i for i in range(nx+1)]+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
        for a0,b0 in zip(boundary,boundary[1:]+boundary[:1]):fs.extend([(a0,b0+N,b0),(a0,a0+N,b0+N)])
        return Manifold(Mesh(np.array(vs,np.float32),np.array(fs,np.uint32)))
    def recess(o,side,face,u0,u1,z0,z1,depth=None,mat='glass'):
        dp=p['window_recess_m'] if depth is None else depth
        if side=='west':q=(face-.05,face+dp,u0,u1,z0,z1)
        elif side=='east':q=(face-dp,face+.05,u0,u1,z0,z1)
        elif side=='south':q=(u0,u1,face-.05,face+dp,z0,z1)
        else:q=(u0,u1,face-dp,face+.05,z0,z1)
        color(mat,*q);return o-B(*q)
    def windows(o,side,face,centres,width,z0,z1,ncols=3):
        # Mullions are the uncut original wall, full-root rather than fragile rods.
        for u in centres:
            u0=u-width/2;pw=width/ncols
            for k in range(ncols):
                a=u0+k*pw+.26;b=u0+(k+1)*pw-.26
                for lo,hi in [(z0,z0+(z1-z0)*.72-.26),(z0+(z1-z0)*.72+.26,z1)]:
                    o=recess(o,side,face,a,b,lo,hi)
        return o
    # Foundation/base is one solid. Outdoor paving only around the building.
    a,b,c,d=p['base_bounds_m'];add(box(a*s,b*s,c*s,d*s,0,base),'integrated flat base');color('base',a,b,c,d,-base/s-.5,-.5)
    cb('paving',-57,45.5,-36.5,36.5,-.52,-.42,'paved apron')
    a,b,c,d=p['body_bounds_m'];body=B(a,b,c,d,-.5,p['wall_top_m'])
    # West entry: a centred curtain wall and two genuinely recessed 2F door portals.
    for y in [-24.0,24.0]:
        body=recess(body,'west',a,y-2.5,y+2.5,4.0,7.4,2.1,'door')
    west_centres=[-29.6,-17.4,-11.0,11.0,17.4,29.6]
    for z0,z1 in [(.7,3.25),(5.25,7.0),(9.4,11.4)]:body=windows(body,'west',a,west_centres,5.0,z0,z1,3)
    for u in np.linspace(-4.5,4.5,7):
        for z in np.arange(3.8,12.2,1.35):body=recess(body,'west',a,u-.49,u+.49,z,z+.82)
    body=windows(body,'west',a,[0],10.4,.22,3.0,6)
    # Horizontal curtain-wall transoms have the same physical recess depth.
    # East services front: wider central window rhythm and small corner lights.
    east_centres=[-24,-18,-12,-6,0,6,12,18,24]
    for z0,z1 in [(.85,3.0),(5.1,7.0),(9.4,11.35)]:body=windows(body,'east',b,east_centres,4.65,z0,z1,3)
    for u in [-31,-28,28,31]:body=windows(body,'east',b,[u],.95,5.15,7.1,1)
    # South side: plan-guided bay rhythm, visible long-side photograph.
    south_centres=[-36.5,-30,-23.5,-17,-10.5,-4,2.5,9,15.5,22,28.5,35]
    for z0,z1 in [(.9,3.0),(5.1,7.0),(9.35,11.3)]:body=windows(body,'south',c,south_centres,5.1,z0,z1,3)
    # North is independently specified. Near B stair entrance and rolling shutter
    # have photographic evidence. Far-west bay details are plan-based estimates.
    north_centres=[-36.5,-30,-23.5,-17,-10.5,-4,2.5,9,15.5]
    for z0,z1 in [(.85,3.1),(5.1,7.0),(9.35,11.3)]:body=windows(body,'north',d,north_centres,5.1,z0,z1,3)
    for z0,z1 in [(5.1,7.0),(9.35,11.3)]:body=windows(body,'north',d,[22,28.5,35],5.1,z0,z1,3)
    body=recess(body,'north',d,30.4,35.8,.2,3.3,.6,'door')
    body=recess(body,'north',d,21.3,27.5,.15,3.1,.35,'shutter')
    add(body,'three-level exterior mass with facade-specific openings')
    # Pink low plinth, no source texture. A material subdivision on the same skin.
    color('pink',a-.01,b+.01,c-.01,d+.01,-.5,.62)
    # Photo-led vertical fascia. Lower edges are waves; main roof is not scalloped.
    relief=p['fascia_relief_m']
    for side,lo,hi,face in [('west',c,d,a),('east',c,d,b),('south',a,b,c),('north',a,b,d)]:
        lo+=.15;hi-=.15  # Wall-corner reveal prevents overlapping independent fascia returns.
        u=sorted(set([*map(float,np.linspace(lo,hi,81)),lo+.8,hi-.8]));poly=[(float(v)*s,Z(wave_height(float(v),side))) for v in u]
        poly += [(hi*s,Z(13.82)),(lo*s,Z(13.82))]
        slab=CrossSection([np.array(poly)]).extrude(s*(relief+.35))
        # local (u,z,w) to global (x,y,z); chosen transform has positive determinant.
        if side=='west':mat=[[0,0,1,(face-relief)*s],[1,0,0,0],[0,1,0,0]]
        elif side=='east':mat=[[0,0,1,(face-.35)*s],[1,0,0,0],[0,1,0,0]]
        elif side=='south':mat=[[1,0,0,0],[0,0,-1,(face+.35)*s],[0,1,0,0]]
        else:mat=[[1,0,0,0],[0,0,-1,(face+relief)*s],[0,1,0,0]]
        add(slab.transform(np.array(mat)),side+' pink wave fascia')
    # Roof: four low rectangular eaves and a double-curved central dome.
    nx,ny=p['roof_grid_segments'];aa,bb,cc,dd=p['main_roof_bounds_m'];hx=bb;hy=dd
    roof=lambda x,y:max(p['main_roof_eave_top_m']+min(1.2,.50*min(hx-abs(x),hy-abs(y))),p['main_roof_crown_m']-(p['main_roof_crown_m']-p['main_roof_eave_top_m'])*((x/hx)**2+(y/hy)**2))
    # Analytic ellipse-ring tessellation places the skirt junction on its actual
    # contour instead of a jagged cut across rectangular cells.
    N=128; nr=20; zrim=16.9; rr=math.sqrt((p['main_roof_crown_m']-zrim)/(p['main_roof_crown_m']-p['main_roof_eave_top_m']))
    verts=[(0,0,Z(p['main_roof_crown_m']))];faces=[]
    for j in range(1,nr+1):
        r=rr*j/nr
        for i in range(N):
            t=2*math.pi*i/N;x=hx*r*math.cos(t);y=hy*r*math.sin(t)
            verts.append((s*x,s*y,Z(p['main_roof_crown_m']-(p['main_roof_crown_m']-p['main_roof_eave_top_m'])*r*r)))
    for i in range(N):faces.append((0,1+i,1+(i+1)%N))
    def join_rings(start0,start1):
        for i in range(N):
            ni=(i+1)%N;faces.extend([(start0+i,start1+i,start1+ni),(start0+i,start1+ni,start0+ni)])
    for j in range(nr-1):join_rings(1+j*N,1+(j+1)*N)
    # Rounded vertical lip: top shoulder, outward nose, underside return.
    for factor,z in [(.987,16.25),(1.0,15.7),(.999,15.08),(.983,p['main_roof_underside_m'])]:
        prev=len(verts)-N;start=len(verts)
        for i in range(N):
            t=2*math.pi*i/N;cx,cy=math.cos(t),math.sin(t);v=1/max(abs(cx),abs(cy));verts.append((s*hx*factor*cx*v,s*hy*factor*cy*v,Z(z)))
        join_rings(prev,start)
    # Plane underside closes the roof without unseen internal trusses.
    center=len(verts);verts.append((0,0,Z(p['main_roof_underside_m'])))
    for i in range(N):faces.append((center,center-N+(i+1)%N,center-N+i))
    mainroof=Manifold(Mesh(np.asarray(verts,np.float32),np.asarray(faces,np.uint32)))
    add(mainroof,'double-curved main roof with low skirt and rounded lip')
    color('silver',aa-.01,bb+.01,cc-.01,dd+.01,p['main_roof_underside_m']-.01,p['main_roof_crown_m']+.01)
    # Rectangular clerestory is inset from all four cap eaves. Its lower boundary
    # intersects the primary dome, thus automatically follows curved roof skin.
    ca,cb_,cc,cd=p['cap_support_bounds_m']
    def capbottom(x,y):
        # A real full-width flat perimeter band spans at least the last radial
        # cell (1.89mm in the short direction), rather than a sampled clamp
        # whose first triangle accidentally climbs from the very rim.
        if abs(x)>=17.3 or abs(y)>=14.05:return 27.35
        return max(27.35,28.2-.9*((x/18.6)**2+(y/15.1)**2)+.2*(x/18.6)**2*(y/15.1)**2)
    add(height_solid(p['cap_support_bounds_m'],lambda x,y:capbottom(x,y)+.12,21.5,24,20),'inset curved-top clerestory')
    color('clerestory',ca-.01,cb_+.01,cc-.01,cd+.01,21.49,28.33)
    cap=lambda x,y:p['cap_crown_m']-2.4*((x/18.6)**2+(y/15.1)**2)+2.4*(x/18.6)**2*(y/15.1)**2
    def rounded_ray(t,hx,hy,r):
        ux,uy=abs(math.cos(t)),abs(math.sin(t));length=min(hx/max(ux,1e-15),hy/max(uy,1e-15))
        if length*ux>hx-r and length*uy>hy-r:
            dot=(hx-r)*ux+(hy-r)*uy
            length=dot+math.sqrt(max(0,dot*dot-((hx-r)**2+(hy-r)**2-r*r)))
        return math.copysign(length*ux,math.cos(t)),math.copysign(length*uy,math.sin(t))
    N=128;nr=16;cv=[];cf=[]
    # Direct rounded-boundary mesh avoids coplanar Boolean trimming slivers.
    for bottom in [False,True]:
        cv.append((0,0,Z(capbottom(0,0) if bottom else cap(0,0))))
        for j in range(1,nr+1):
            for i in range(N):
                x,y=rounded_ray(i*2*math.pi/N,18.6,15.1,.9);x*=j/nr;y*=j/nr
                # Flat outer soffit meets a full-width vertical blunt lip; no acute bevel.
                cv.append((x*s,y*s,Z(capbottom(x,y) if bottom else cap(x,y))))
    half=1+nr*N
    for off,rev in [(0,False),(half,True)]:
        for i in range(N):
            tri=(off,off+1+i,off+1+(i+1)%N);cf.append(tri[::-1] if rev else tri)
        for j in range(nr-1):
            a0=off+1+j*N;b0=a0+N
            for i in range(N):
                ni=(i+1)%N
                for tri in [(a0+i,b0+i,b0+ni),(a0+i,b0+ni,a0+ni)]:cf.append(tri[::-1] if rev else tri)
    a0=1+(nr-1)*N;b0=half+a0
    for i in range(N):
        ni=(i+1)%N;cf.extend([(a0+i,b0+i,b0+ni),(a0+i,b0+ni,a0+ni)])
    add(Manifold(Mesh(np.asarray(cv,np.float32),np.asarray(cf,np.uint32))),'independent raised curved silver cap with rounded plan corners')
    color('silver',-18.61,18.61,-15.11,15.11,26.49,p['cap_crown_m']+.01)
    # Deep gray fascia-to-roof joint is visible in exterior photographs.
    color('clerestory',-43.51,43.51,-34.31,34.31,13.82,14.66)
    # Two western straight stair runs, broad solid risers and landings.
    for y in [-24.,24.]:
        lo,hi=y-3.1,y+3.1
        for i in range(24):
            x=-55.9+i*.30
            cb('stairs',x,x+.32,lo,hi,-.43,-.5+(i+1)*4.5/24,'west stair riser')
        cb('stairs',-48.72,-42.95,lo,hi,-.43,4.0,'connected 2F landing')
        # Solid stringer/guard panels are a print-scale substitution for rail wire.
        for yy in [lo,hi-.6]:
            verts=np.array([[-55.9,yy,-.50],[-48.7,yy,-.50],[-48.7,yy,5.0],[-55.9,yy,.6],[-55.9,yy+.6,-.50],[-48.7,yy+.6,-.50],[-48.7,yy+.6,5.0],[-55.9,yy+.6,.6]])
            add(Manifold.hull_points(np.column_stack((verts[:,:2]*s,Z(verts[:,2])))),'stair guard full-root solid stringer for printing')
            cb('frame',-48.72,-43.0,yy,yy+.6,3.5,5.0,'landing guard')
        color('frame',-56,-43,lo-.01,hi+.01,-.4,5.01)
    # Ground-level central entry canopy and shallow approach steps.
    cb('frame',-45.25,-42.9,-7.0,7.0,3.0,3.65,'central entry canopy')
    for i in range(3):cb('stairs',-46.0+i*.55,-42.9,-7.0,7.0,-.43,-.4+(i+1)*.17,'central entry shallow step')
    # Northern photographed entrance platform and local shallow stairs.
    cb('stairs',29.0,37.2,33.7,35.2,-.43,.08,'north B-stair entrance platform')
    for i in range(3):cb('stairs',29.0,37.2,35.1,36.4-i*.4,-.43,-.43+(i+1)*.16,'north entrance step')
    cb('frame',29.0,37.1,33.7,35.3,3.3,3.95,'north B-stair entrance canopy')
    result=union(parts);require(str(result.status()).endswith('NoError'),str(result.status()))
    return result,regions,features

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],np.float32);f=np.asarray(m.tri_verts,np.int64);tri=v[f]
    data=bytearray(b'UTaipei Tianmu Gym A | estimated 1:500 | original exterior mm'.ljust(80,b'\0')+struct.pack('<I',len(tri)))
    for q in tri:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(n);require(L>0,'Degenerate export');n/=L;data+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(data);return len(tri)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);file=args.output_dir/'model.stl';n=save_stl(m,file)
    (args.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n')
    shutil.copy2(R/'parameters.json',args.output_dir/'parameters.json');shutil.copy2(__file__,args.output_dir/'build_model.py')
    report={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'status':'Appearance draft. No strict print-QA or appearance acceptance claim.'}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='features'},indent=2))
if __name__=='__main__':main()
