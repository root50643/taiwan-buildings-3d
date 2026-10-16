"""Source-constrained TMU Teaching Building; authored finite exterior, no image textures."""
from pathlib import Path
import argparse, hashlib, json, math, os, struct, shutil
os.environ['OMP_NUM_THREADS']='1'; os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold, CrossSection, OpType
R=Path(__file__).resolve().parent.parent

def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def union(parts): return Manifold.batch_boolean(parts,OpType.Add)
def box(a,b,c,d,e,f): return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def make_model(p):
    s=p['scale_mm_per_estimated_m']; base=p['base_thickness_mm']; parts=[]; regions=[]; features=[]
    Z=lambda z:base+s*z
    def B(a,b,c,d,e,f): return box(a*s,b*s,c*s,d*s,Z(e),Z(f))
    def RB(a,b,c,d,e,f,r=.50):
        w,h=(b-a)*s,(d-c)*s
        require(min(w,h)>2*r,'Profile too small for authored fillet')
        profile=CrossSection.square((w-2*r,h-2*r)).offset(r,circular_segments=16).translate((a*s+r,c*s+r))
        return profile.extrude(Z(f)-Z(e)).translate((0,0,Z(e)))
    def rcb(mat,a,b,c,d,e,f,name):
        add(RB(a,b,c,d,e,f),name);col(mat,a-.001,b+.001,c-.001,d+.001,e-.001,f+.001)
    def add(o,name): require(str(o.status()).endswith('NoError'),name+': '+str(o.status()));parts.append(o);features.append(name)
    def col(mat,a,b,c,d,e,f): regions.append({'material':mat,'bounds_mm':[a*s,b*s,c*s,d*s,Z(e),Z(f)]})
    def cb(mat,a,b,c,d,e,f,name=None): add(B(a,b,c,d,e,f),name or mat);col(mat,a-.001,b+.001,c-.001,d+.001,e-.001,f+.001)
    def arch_void(a,b,c,d,z0,spring,rise):
        pts=[(a*s,Z(z0)),(b*s,Z(z0)),(b*s,Z(spring))]
        pts += [((.5*(a+b)+.5*(b-a)*math.cos(t))*s,Z(spring+rise*math.sin(t))) for t in np.linspace(0,math.pi,25)[1:]]
        return CrossSection([np.array(pts)]).extrude((d-c)*s).transform(np.array([[1,0,0,0],[0,0,-1,d*s],[0,1,0,0]]))
    def recess(o,side,face,a,b,z0,z1,depth=.55,mat='glass'):
        if side=='front': q=(a,b,face-.05,face+depth,z0,z1);r=(a,b,face+depth-.02,face+depth+.02,z0,z1)
        elif side=='rear':q=(a,b,face-depth,face+.05,z0,z1);r=(a,b,face-depth-.02,face-depth+.02,z0,z1)
        elif side=='nw':q=(face-depth,face+.05,a,b,z0,z1);r=(face-depth-.02,face-depth+.02,a,b,z0,z1)
        else:q=(face-.05,face+depth,a,b,z0,z1);r=(face+depth-.02,face+depth+.02,a,b,z0,z1)
        col(mat,*r);return o-B(*q)
    # Integral base and apron. Source metres describe estimated building coordinates.
    a,b,c,d=p['base_bounds_m'];add(box(a*s,b*s,c*s,d*s,0,base),'integrated flat base');col('base',a,b,c,d,-base/s,0)
    cb('paving',-2,84,-3,23,-.03,.15,'plain apron, no invented surrounding buildings')
    # Solid classroom masses preserve 1F 4 rooms + 2F/3F 5 rooms. Central 1F passage is real.
    body=union([B(0,82,.55,12.1,0,13.5),B(0,11.9,11.9,16,0,13.5),B(70.2,82,11.9,16,0,13.5)])
    body=body-B(33.3,48.7,-.2,16.2,.15,4.05)
    # Two U-stair/service bands are open only toward the corridor; no separate stair towers.
    for x in [13.0,63.4]: body=body-B(x,x+5.6,8.2,16.2,.15,13.0)
    # NE windows recessed behind continuous fins; 1F terminal areas use straight-column glazing.
    for a,b in [(12.6,18.5),(19.8,32.6),(34,48),(49.4,62.4),(63.7,69.5)]:
        for lo,hi in [(5.65,8.45),(10.15,12.95)]:body=recess(body,'front',.55,a,b,lo,hi,.55)
    for a,b in [(12.6,15.2),(15.8,18.5),(63.7,66.3),(66.9,69.5)]:body=recess(body,'front',.55,a,b,.75,3.95,.55)
    # Behind arcade openings, finite shallow dark window fields; central passage remains unfilled.
    for a,b in [(12.6,18.5),(19.8,25.5),(26.2,32.6),(49.4,55.4),(56.1,62.4),(63.7,69.5)]:body=recess(body,'front',.55,a,b,.65,3.75,.55)
    # SW corridor background openings, grouped by classroom; no mirrored NE fins.
    for a,b in [(20,25.2),(26,32.2),(34.1,40.2),(41,47.8),(50,55.2),(56,62.1)]:
        for lo,hi in [(1.0,3.7),(5.5,8.2),(10,12.7)]:body=recess(body,'rear',12.1,a,b,lo,hi,.55)
    # Photograph-supported NW end deep recessed window groups. SE end remains low detail.
    for lo,hi in [(1.0,3.8),(5.5,8.3),(10,12.8)]:
        for a,b in [(1.0,4.0),(4.6,7.6),(8.2,11.2),(11.8,14.8)]:body=recess(body,'nw',82,a,b,lo,hi,.85)
    add(body,'three-storey classroom and service solid with only 1F central through passage')
    # Upper floor/roof plates cover the passage and corridor, preserving continuous flat roof.
    for z in [4.0,8.5,13.0]:
        cb('concrete',0,82,.55,16,z,z+.55,'continuous structural floor/roof plate')
        cb('concrete',11.9,70.2,-.65,16,z,z+.55,'central projected structural floor/roof and shade plate')
    # Dense 2F/3F NE vertical fins, merged and thickened for manufacture. Roots overlap plates.
    count=p['fin_count_manufacturing_simplification'];w=p['fin_width_m_manufactured']
    for i in range(count):
        x=12.25+i*57.6/(count-1);rcb('concrete',x-w/2,x+w/2,-.65,1.4,4.0,13.5,'NE manufactured fin with rounded corners and solid root')
    cb('concrete',11.9,70.2,-.68,.85,12.5,14.0,'NE photo-proportioned deep continuous roof fascia')
    # SW open horizontal corridors, solid parapets and structural columns.
    for z in [4.5,9.0]:cb('concrete',11.65,70.45,15.45,16.0,z-.05,z+1.05,'SW corridor solid horizontal parapet')
    for x in [11.9,19.2,25.0,31.1,37.2,43.3,49.4,55.5,61.6,70.2]:rcb('concrete',x-.26,x+.26,15.35,16.0,.1,13.5,'SW corridor thickened rounded column')
    # End-room SW brick faces are blank source-supported terminal masses, not extra openings.
    cb('brick',0,11.9,15.42,16.06,.15,14.0,'SE end-room SW brick wall')
    cb('brick',70.2,82,15.42,16.06,.15,14.0,'NW end-room SW brick wall')
    cb('brick',0,11.9,-.10,1.2,.15,14.5,'SE end-room broad NE brick wall')
    cb('brick',70.2,82,-.10,1.2,.15,14.5,'NW end-room broad NE brick wall')
    # Short-end deep shade shelves differ from the long sides; NW window count is simplified.
    for z in [3.0,7.5,12.0]:cb('concrete',81.6,82.7,.25,15.75,z,z+1.55,'NW photograph-proportioned deep shade fascia')
    for y in [.5,4.3,7.9,11.5,15.4]:cb('concrete',81.5,82.55,y-.26,y+.26,.15,13.55,'NW thick end-frame divider')
    rcb('brick',81.5,82.15,-.5,.25,.15,14.5,'NW NE brick wingwall')
    rcb('brick',81.5,82.15,15.75,16.5,.15,14.5,'NW SW brick wingwall')
    # Unknown SE end: only broad recess and depth hierarchy; exact pane inventory omitted.
    for lo,hi in [(1.0,3.8),(5.5,8.3),(10,12.8)]:
        # A solid face already exists here. No invented detailed glazing array.
        pass
    for z in [4.0,8.5,13.0]:cb('concrete',-.6,.4,.25,15.75,z,z+.55,'SE conservative horizontal end depth')
    rcb('brick',-.15,.5,-.5,.25,.15,14.5,'SE NE brick wingwall estimated')
    rcb('brick',-.15,.5,15.75,16.5,.15,14.5,'SE SW brick wingwall estimated')
    # Repaired stone arcade only across central evidenced segment; terminal zones stay straight.
    arcade=B(18.7,63.4,-.95,1.40,.15,4.55)
    openings=[(19.8,23.1,2.8,.65),(24.3,27.6,2.8,.65),(28.8,32.1,2.8,.65),(34.0,48.0,2.5,1.0),(49.9,53.2,2.8,.65),(54.4,57.7,2.8,.65),(58.9,62.2,2.8,.65)]
    for a,b,spring,rise in openings:arcade=arcade-arch_void(a,b,-1.05,1.50,.1,spring,rise)
    add(arcade,'central NE restored stone arcade only, simplified seven-opening rhythm');col('stone',18.69,63.41,-.96,1.41,.14,4.56)
    # Plain shallow entry steps, not the historical giant bare canopy.
    for i in range(3):cb('paving',37.6,44.4,-2.7+i*.75,.4,.12,.12+(i+1)*.18,'central NE solid shallow entrance steps')
    # One SW elevator near NW quarter, with 3 short bridges. Clock tower expressly absent.
    cb('metal',59.1,62.7,18.0,21.5,.1,14.5,'single estimated grey-metal elevator volume')
    for z in [0.15,4.5,9.0]:
        cb('concrete',59.3,62.5,15.65,18.3,z-.1,z+.5,'short elevator bridge slab')
        for x in [59.3,62.0]:cb('metal',x,x+.5,15.65,18.3,z+.35,z+1.3,'stout bridge edge rail as manufactured solid')
    # Two U-shaped stairs: each pair of ramps joins 1F–2F and 2F–3F; roof access unknown.
    for x in [13.0,63.4]:
        for z in [.15,4.5]:
            for a,b,reverse in [(x+.1,x+2.35,False),(x+3.25,x+5.5,True)]:
                y0,y1=8.25,14.9
                if not reverse:pts=[(y0*s,Z(z)),(y1*s,Z(z)),(y1*s,Z(z+2.25)),(y0*s,Z(z+.65))]
                else:pts=[(y0*s,Z(z+3.75)),(y1*s,Z(z+2.25)),(y1*s,Z(z+2.90)),(y0*s,Z(z+4.35))]
                ramp=CrossSection([np.array(pts)]).extrude((b-a)*s).transform(np.array([[0,0,1,a*s],[1,0,0,0],[0,1,0,0]]));add(ramp,'U-stair manufactured solid ramp');col('stairs',a,b,y0,y1,z,z+4.5)
            cb('stairs',x+.1,x+5.5,14.25,15.4,z+1.80,z+3.05,'U-stair intermediate landing with robust ramp overlap')
    # Flat roof is uninterrupted over central classroom. Rails indicate finite activity zones.
    for a,b in [(1.1,10.8),(71.3,80.9)]:
        cb('roof',a,b,1.1,14.8,13.5,13.65,'approximate flat roof activity surface')
        for y in [1.1,14.3]:cb('metal',a,b,y,y+.5,13.55,14.35,'manufacturing-merged roof rail')
        for x in [a,b-.5]:cb('metal',x,x+.5,1.1,14.8,13.55,14.35,'manufacturing-merged roof rail')
    cb('concrete',11.9,70.2,15.4,16.0,13.5,14.0,'SW low roof parapet')
    result=union(parts);require(str(result.status()).endswith('NoError'),str(result.status()));return result,regions,features

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],np.float32);f=np.asarray(m.tri_verts,np.int64);tri=v[f]
    data=bytearray(b'TMU Teaching Building restored exterior | estimated nominal 1:400 | mm'.ljust(80,b'\0')+struct.pack('<I',len(tri)))
    for q in tri:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(n);require(L>0,'Degenerate export');n/=L;data+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(data);return len(tri)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);file=a.output_dir/'model.stl';n=save_stl(m,file)
    (a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n');shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
    report={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'status':'Source-review core candidate; no strict mesh QA yet'}
    (a.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='features'},indent=2))
if __name__=='__main__':main()
