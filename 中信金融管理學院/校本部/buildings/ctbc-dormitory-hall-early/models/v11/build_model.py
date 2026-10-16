"""Source-constrained CTBC early exterior. No source imagery embedded."""
from pathlib import Path
import argparse,hashlib,json,math,os,struct,shutil
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,Mesh,CrossSection,OpType
R=Path(__file__).resolve().parent.parent

def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def union(parts):return Manifold.batch_boolean(parts,OpType.Add)
def box(a,b,c,d,e,f):return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def make_model(p):
    s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm'];g=p.get('south_axis_calibration',1.0);parts=[];regions=[];features=[]
    Z=lambda z:base+s*g*z
    X=lambda x:s*g*x
    def B(a,b,c,d,e,f):return box(X(a),X(b),c*s,d*s,Z(e),Z(f))
    def RB(a,b,c,d,e,f,r=.50):
        # Real print-scale vertical edge fillets, built before union/export.
        w,h=X(b)-X(a),(d-c)*s
        require(min(w,h)>2*r,'Rounded pillar smaller than fillet diameter')
        profile=CrossSection.square((w-2*r,h-2*r)).offset(r,circular_segments=16).translate((X(a)+r,c*s+r))
        return profile.extrude(Z(f)-Z(e)).translate((0,0,Z(e)))
    def add(q,name):require(str(q.status()).endswith('NoError'),name+': '+str(q.status()));parts.append(q);features.append(name)
    def col(mat,a,b,c,d,e,f):regions.append({'material':mat,'bounds_mm':[X(a),X(b),c*s,d*s,Z(e),Z(f)]})
    def cb(mat,a,b,c,d,e,f,name=None):add(B(a,b,c,d,e,f),name or mat);col(mat,a-.001,b+.001,c-.001,d+.001,e-.001,f+.001)
    def recess(o,side,face,u0,u1,z0,z1,depth=None,mat='glass'):
        dp=depth or p['window_recess_m']
        if side=='south':q=(u0,u1,face-.05,face+dp,z0,z1)
        elif side=='north':q=(u0,u1,face-dp,face+.05,z0,z1)
        elif side=='west':q=(face-.05,face+dp,u0,u1,z0,z1)
        else:q=(face-dp,face+.05,u0,u1,z0,z1)
        if side=='south': col(mat,u0,u1,face+dp-.02,face+dp+.02,z0,z1)
        elif side=='north': col(mat,u0,u1,face-dp-.02,face-dp+.02,z0,z1)
        elif side=='west': col(mat,face+dp-.02,face+dp+.02,u0,u1,z0,z1)
        else: col(mat,face-dp-.02,face-dp+.02,u0,u1,z0,z1)
        return o-B(*q)
    def arch_void(x0,x1,y0,y1,zbase,spring,rise):
        pts=[(X(x0),Z(zbase)),(X(x1),Z(zbase)),(X(x1),Z(spring))]
        pts += [(X(.5*(x0+x1)+.5*(x1-x0)*math.cos(t)),Z(spring+rise*math.sin(t))) for t in np.linspace(0,math.pi,25)[1:]]
        return CrossSection([np.array(pts)]).extrude((y1-y0)*s).transform(np.array([[1,0,0,0],[0,0,-1,y1*s],[0,1,0,0]]))
    a,b,c,d=p['base_bounds_m'];add(box(a*s,b*s,c*s,d*s,0,base),'integrated flat base');col('base',a/g,b/g,c,d,-base/(s*g),0)
    cb('paving',-3.5/g,73.5/g,-6.5,40.5,-.03,.15,'ground apron')
    # Southern high dormitory: source X grid calibrated to estimated 62 m; Y depth 16 m.
    a,b,c,d=p['south_bounds_m'];stepx=p['south_room_end_physical_m']/g
    body=union([B(a,stepx,c,d,0,p['south_height_m']),B(stepx,b,c,9,0,p['south_height_m'])])
    # Top opening is a through-going geometric void, not painted decoration.
    body=body-arch_void(54.0,66.0,-.1,18.1,21.56,22.4,1.5)
    # Photograph-led facade: broad upper loggias, narrower central lower bays,
    # wide lower end groups and a deep rear glazing plane rather than black holes.
    centers=[5.8+3.65*i for i in range(12)]
    def glazing(x,w,z0,z1,yfront=1.0,yback=1.6,columns=3):
        frame=B(x-w/2,x+w/2,yfront,yback,z0,z1)
        pw=w/columns
        for k in range(columns):
            a=x-w/2+k*pw+(.40 if k==0 else .20);b=x-w/2+(k+1)*pw-(.40 if k==columns-1 else .20)
            if b>a:frame=recess(frame,'south',yfront,a,b,z0+.4,z1-.4,.25)
        add(frame,'recessed solid-root window mullions');col('frame',x-w/2,x+w/2,yfront-.01,yfront+.01,z0,z1)
    for i,x in enumerate(centers):
        # Upper full-width bay pair with a real solid parapet and set-back glazing.
        for z0,z1 in [(14.2,17.2),(18.0,21.4)]:
            body=recess(body,'south',0,x-1.5,x+1.5,z0,z1,1.6,mat='wall')
            cb('spandrel',x-1.48,x+1.48,.62,1.72,z0,z0+.70,'upper loggia solid parapet')
            glazing(x,2.96,z0+.69,z1-.18,1.03,1.72,3)
        # Lower rows: central narrow punched recesses versus broader end groups.
        for z0,z1 in [(5.2,8.4),(9.6,12.8)]:
            w=2.15 if 1<=i<=8 else 3.0
            body=recess(body,'south',0,x-w/2,x+w/2,z0,z1,1.6,mat='wall')
            glazing(x,w-.04,z0+.60,z1-.20,1.03,1.72,2 if w<3 else 3)
            cb('trim',x-w/2-.05,x+w/2+.05,-.16,.3,z1,z1+.45,'lower window overhanging head rooted above the true opening')
        # Photographed base has wider louver-like recesses; simplified paired bars.
        body=recess(body,'south',0,x-1.5,x+1.5,1.25,3.95,1.0,mat='glass')
        for z in [1.8,2.7,3.6]:cb('steel',x-1.47,x+1.47,.45,1.12,z,z+.4,'base louver simplified stout bars')
        if 1<=i<=8:body=recess(body,'south',0,x-.25,x+.25,22.35,23.65,.6)
    for z in [1.7,6.1,10.5,14.9,19.0]:body=recess(body,'south',0,53.8,66.2,z,z+.8,.75)
    # The blank northern short-wing back is deliberately uninvented.
    for z in [2.1,6.5,10.9,15.3,19.1]:
        body=recess(body,'south',0,1.15,2.35,z,z+.8,.55)
        body=recess(body,'south',0,49.35,50.55,z,z+.8,.55)
    # Main long-wing courtyard face inferred from the second design elevation.
    for i,x in enumerate([4.7+3.5*i for i in range(12)]):
        for z0,z1 in [(5.5,8.0),(10.0,12.5),(14.5,17.0)]:body=recess(body,'north',16,x-.95,x+.95,z0,z1,.75)
        body=recess(body,'north',16,x-1.4,x+1.4,19.0,21.7,.75)
        body=recess(body,'north',16,x-1.4,x+1.4,1.5,4.1,.75)
    for z0,z1 in [(2.0,4.0),(6.0,8.4),(10.4,12.8),(14.8,17.2),(19.0,21.6)]:body=recess(body,'north',16,44/g,46.5/g,z0,z1,.75)

    for z in [4.6,9.0,13.4,17.8]:
        body=recess(body,'east',68,.7,8.3,z,z+.55,.55)
    body=recess(body,'east',68,.6,7.0,2.35,6.2,1.2)
    # Small recessed roof fields retain broad printable parapet rims.
    body=body-B(1/g,(p['south_room_end_physical_m']-1)/g,1.0,15.0,23.85,24.7)
    # Eastern arch block remains a simple flat roof: an unverified roof recess
    # would make the actual skin over the large opening too thin at this scale.

    add(body,'south high long wing with photo-led south recesses and design-inferred north face')
    for z in [17.35,21.4]:cb('trim',3.8,48.7,-.75,.16,z,z+.5,'south continuous projecting sill/header band')
    for i in range(1,9):
        x=3.975+3.65*i;cb('trim',x-.24,x+.24,-.48,.15,11.2,17.5,'long slender facade fin, manufacturing-thickened')
    # Broad white rim follows the recognizable flat-arched top opening.
    outer=arch_void(53.4,66.6,-.52,.12,20.3,22.6,1.8)
    inner=arch_void(54.0,66.0,-.62,.22,21.56,22.4,1.5)
    add(outer-inner,'white arched opening surround with physical relief')
    col('trim',53.39,66.61,-.53,-.01,20.29,24.5)
    for x in [57.8,62.2]:add(RB(x-.25,x+.25,4.2,4.75,21.45,24.1),'recessed arch internal upright with0.5mm vertical fillets')
    # Roof recesses only describe conservative flat parapets, not unverified equipment.

    # Low auditorium/connector remains visibly lower between the high wings.
    a,b,c,d=p['hall_bounds_m'];cb('wall',a,b,c,d,0,p['hall_height_m'],'lower lecture hall and connector')
    a,b,c,d=p['north_bounds_m'];north=B(a,b,c,d,6.9,p['north_height_m'])
    for x in [v/g for v in [49.45,53.37,57.29,61.21,65.13,69.05]]:
        for z0,z1 in [(9.0,11.7),(13.0,15.7),(17.0,20.3)]:north=recess(north,'south',24,x-1.45,x+1.45,z0,z1,.65)
    # Only the photographed eastern end receives broad dark recesses and
    # local parapet blocks; no invented pane inventory on the unknown north.
    for z0,z1 in [(8.4,11.6),(12.8,15.6),(16.8,20.4)]:
        north=recess(north,'east',b,25.3,37.2,z0,z1,.85)
        cb('spandrel',b-.92,b+.12,29.0,33.0,z0,z0+.9,'north east-end local solid parapet block')
    north=north-B(48.5/g,70/g,25,37,22.85,23.7)
    add(north,'north short high parallel wing; north rear intentionally simplified')
    for z in [7.1,11.8,15.8,20.6]:cb('trim',70.6/g,72.2/g,24,38,z,z+.48,'north wing east-end stacked plate')
    # West projecting window/end band is not mirrored at the east end.
    west=B(-1.25,.15,4.2,14.0,.8,20.8)
    for z0,z1 in [(1.4,4.2),(5.4,8.4),(9.8,12.8),(14.2,17.1),(18.1,20.4)]:west=recess(west,'west',-1.25,4.8,13.4,z0,z1,.55)
    add(west,'west glass end projection')
    for z in [4.4,8.6,13,17.3,20.8]:cb('trim',-1.8,.1,3.9,14.3,z,z+.5,'west horizontal end plate')
    # Six foreground arches are physically separated from the main facade.
    arcade=B(4.0,53.5,-4.7,-3.9,0,6.2)
    for i in range(6):
        lo=4.8+i*8.0;arcade=arcade-arch_void(lo,lo+6.9,-4.8,-3.8,-.1,4.7,.95)
    # Physical rounded/thickened pier edges reduce brittle corners. This is an
    # explicit manufactured part, not a repair of exported STL or a QA waiver.
    arcade=arcade.minkowski_sum(Manifold.cylinder(.10,.50,.50,16).translate((0,0,-.05)))
    add(arcade,'independent six-bay arcade with0.5mm XY rounding and0.05mm Z allowance')
    cb('steel',4.0,53.5,-5.0,-3.6,4.35,4.85,'exposed front beam simplified stout rectangular profile')
    for x in [4.0+8.0*i for i in range(7)]:cb('steel',x,x+.5,-4.3,.2,4.35,4.85,'cross tie beam joins arcade to main body')
    # Photographed eastern entry and solid stair apron.
    cb('trim',61.8/g,71.8/g,-3.5,7.4,6.3,6.9,'east photographed broad entry canopy')
    add(RB(71.0/g,71.6/g,-3.1,-2.5,.1,7.7),'east tall canopy support with0.5mm vertical fillets');col('trim',71.0/g,71.6/g,-3.1,-2.5,.1,7.7)
    add(RB(62.4/g,62.9/g,-3.1,-2.5,.1,6.6),'east inner canopy support with0.5mm vertical fillets');col('steel',62.4/g,62.9/g,-3.1,-2.5,.1,6.6)
    stairpoly=[(-6.5*s,Z(0)),(3.1*s,Z(0)),(3.1*s,Z(2.3))]
    for i in range(9,-1,-1):
        stairpoly.extend([((-6.5+i*.52)*s,Z(.23*(i+1))),((-6.5+i*.52)*s,Z(.23*i))])
    stairpoly=stairpoly[:-1]
    stair=CrossSection([np.array(stairpoly)]).extrude(9.3*s).transform(np.array([[0,0,1,62.5*s],[1,0,0,0],[0,1,0,0]]))
    add(stair,'east broad entrance continuous stair profile');col('stairs',62.49/g,71.81/g,-6.51,3.11,-.01,2.31)

    # Open northwest court and low quarter-circle stepped terrace.
    for i in range(5):
        r0=10.4+i*.85;r1=r0+.88
        pts=[((46.5+r0*math.cos(t))*s,(16+r0*math.sin(t))*s) for t in np.linspace(math.pi/2,math.pi+.06,35)]
        pts += [((46.5+r1*math.cos(t))*s,(16+r1*math.sin(t))*s) for t in np.linspace(math.pi+.06,math.pi/2,35)]
        step=CrossSection([np.array(pts[::-1])]).offset(-.50,circular_segments=16).offset(.50,circular_segments=16).extrude((.22+.21*i)*s*g).translate((0,0,Z(.1)))
        add(step,'northwest open court curved step with robust overlap into south wall');col('stairs',30/g,47/g,16,32,0,1.5)
    result=union(parts);require(str(result.status()).endswith('NoError'),str(result.status()))
    return result,regions,features

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],np.float32);f=np.asarray(m.tri_verts,np.int64);tri=v[f]
    data=bytearray(b'CTBC early dormitory + lecture hall | estimated 1:400 | mm'.ljust(80,b'\0')+struct.pack('<I',len(tri)))
    for q in tri:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(n);require(L>0,'Degenerate export');n/=L;data+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(data);return len(tri)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);file=a.output_dir/'model.stl';n=save_stl(m,file)
    (a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n');shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
    report={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'status':'Source-reviewed geometry candidate; strict original-mesh QA pending'}
    (a.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='features'},indent=2))
if __name__=='__main__':main()
