"""KMU Library II early completed exterior, finite original solid geometry in millimetres."""
from pathlib import Path
import argparse,hashlib,json,math,os,struct,shutil
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,CrossSection,OpType
R=Path(__file__).resolve().parent.parent

def require(x,s):
    if not x:raise RuntimeError(s)
def union(x):return Manifold.batch_boolean(x,OpType.Add)
def box(a,b,c,d,e,f):return Manifold.cube((b-a,d-c,f-e)).translate((a,c,e))
def make_model(p):
    s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm'];parts=[];regions=[];features=[]
    Z=lambda z:base+s*z
    def B(a,b,c,d,e,f):return box(a*s,b*s,c*s,d*s,Z(e),Z(f))
    def add(o,name):require(str(o.status()).endswith('NoError'),name);parts.append(o);features.append(name)
    def col(mat,a,b,c,d,e,f):regions.append({'material':mat,'bounds_mm':[a*s,b*s,c*s,d*s,Z(e),Z(f)]})
    def cb(mat,a,b,c,d,e,f,name):add(B(a,b,c,d,e,f),name);col(mat,a-.002,b+.002,c-.002,d+.002,e-.002,f+.002)
    def cyl_between(a,b,r,name):
        av=np.array([a[0]*s,a[1]*s,Z(a[2])]);bv=np.array([b[0]*s,b[1]*s,Z(b[2])]);v=bv-av;L=np.linalg.norm(v);v=v/L
        u=np.cross(v,[0,1,0]);u/=np.linalg.norm(u);w=np.cross(v,u);mat=np.column_stack([u,w,v,av]);o=Manifold.cylinder(L,r*s,circular_segments=12).transform(mat);add(o,name)
    # Integral base: no neighbouring architecture.
    a,b,c,d=p['base_bounds_m'];add(box(a*s,b*s,c*s,d*s,0,base),'integral base');col('base',a,b,c,d,-base/s,0)
    cb('paving',-.7,21.1,-4.4,20.1,-.03,.18,'plain footprint apron')
    # Full-height glazing skin: all material assignment remains on actual STL faces.
    north=B(0,20.4,18.6,18.9,.15,18.0)-B(8.2,12.2,18.5,19.1,.17,2.8)
    add(north,'north glass skin with open real central entry');col('glass',-.01,20.41,18.59,18.91,.14,18.01)
    cb('glass',0,.30,0,18.9,.15,18,'west glazing substrate')
    cb('glass',20.1,20.4,0,18.9,.15,18,'east glazing substrate')
    # Higher grey service band: toilets/elevator and second enclosed stair, exterior mass only.
    core=B(.5,19.9,-4,0.35,.15,20.0)
    # Evinced small south windows retained very sparingly; not a mirrored north facade.
    for x in [3.2,6.7]:
        for z in [5.7,10.1,14.5]:
            core=core-B(x,x+.75,-4.1,-3.65,z,z+.65)
            col('dark',x,x+.75,-3.67,-3.63,z,z+.65)
    add(core,'opaque southern service core includes second enclosed stair');col('core',.49,19.91,-4.01,.36,.14,20.01)
    cb('core',8.0,12.0,-4.9,-3.7,.15,17.5,'low-detail central south connection return; adjoining old library excluded')
    # Main floor plates contain a shared north-west stair opening connected through all storeys.
    for z in [4.2,8.6,13.0]:
        slab=B(0,20.4,0,18.9,z-.34,z)
        slab=slab-union([B(.30,6.4,16.4,18.6,z-.5,z+.1),B(.30,2.4,12.0,18.6,z-.5,z+.1)])
        add(slab,'floor plate with NW L stair well');col('floor',0,20.4,0,18.9,z-.35,z+.01)
    cb('roof',-.20,20.60,-.08,19.09,17.66,18.0,'plain flat main roof, no garden or equipment')
    # Only necessary exterior-visible tree structure; no full interior replica or fitout.
    for x,y in [(5.0,5.0),(15.0,5.0),(5.0,14.0),(15.0,14.0)]:
        cyl_between((x,y,.05),(x,y,4.18),.36,'ground floor tree trunk')
        for lo,hi in [(4.05,8.50),(8.45,12.90),(12.85,17.80)]:
            for dx in [-1.25,1.25]:cyl_between((x+(.55 if dx>0 else -.55),y,lo),(x+dx,y,hi),.28,'simplified visible tree branch; not exact 4/8/16/32 system')
    col('column',.8,19.4,.8,18.2,.14,17.85)
    # West and east solid metal panels with circular glazing windows; whole upper storeys retained.
    # East pattern is lower-confidence schematic, independently spaced rather than a mirrored west face.
    for side,groups in [('west',[(1.5,8.8,[2.5,4.3,6.1,7.9]),(10.7,13.9,[11.5,13.0]),(15.0,16.6,[15.8])]),('east',[(2.1,8.7,[3.2,5.4,7.6]),(10.9,14.0,[12.2])])]:
        a,b=(-.12,.34) if side=='west' else (20.06,20.52)
        for y0,y1,centres in groups:
            panel=B(a,b,y0,y1,.2,17.72)
            for z in [1.5,5.8,10.2,14.6]:
                for y in centres:
                    hole=Manifold.cylinder((b-a+.4)*s,.64*s,circular_segments=32).rotate((0,90,0)).translate(((a-.2)*s,y*s,Z(z)))
                    panel=panel-hole
                    regions.append({'material':'glass','cylinder_x':[(a-.02)*s,(b+.02)*s,y*s,Z(z),.65*s]})
            add(panel,side+' opaque cladding with circle rhythm');col('metal',a-.01,b+.01,y0,y1,.2,17.72)
            # Mark window disks again after broad panel material region.
            for z in [1.5,5.8,10.2,14.6]:
                for y in centres:regions.append({'material':'glass','cylinder_x':[(a-.05)*s,(b+.05)*s,y*s,Z(z),.65*s]})
    # Primary north face: opaque central sign panel suspended above entry.
    cb('metal',7.0,13.4,18.52,19.05,2.8,18.0,'north central vertical sign panel')
    # Broad floor-edge and top spandrel strips, physical geometry with robust roots.
    for z in [4.2,8.6,13.0,17.0]:
        cb('frame',-.16,20.56,18.45,19.03,z-.28,z+.13,'north horizontal frame')
        cb('frame',-.16,.60,-.08,19.03,z-.28,z+.13,'west horizontal frame')
        cb('frame',19.80,20.56,-.08,19.03,z-.28,z+.13,'east horizontal frame')
    # Rounded plan profiles avoid fragile sharp exposed mullion roots.
    def mullion(a,b,c,d):
        r=.25;w,h=(b-a)*s,(d-c)*s
        prof=CrossSection.square((w-2*r,h-2*r)).offset(r,circular_segments=12).translate((a*s+r,c*s+r))
        add(prof.extrude(17.70*s).translate((0,0,Z(.1))), 'rounded thickened curtain-wall mullion')
        col('frame',a-.01,b+.01,c-.01,d+.01,.09,18.01)
    for x in [0,1.55,3.1,4.65,6.2,7,13.4,14.95,16.5,18.05,19.6,20.25]:mullion(x-.15,x+.15,18.38,19.05)
    for y in [.3,1.5,8.8,10.7,13.9,15.0,16.6,18.75]:mullion(-.16,.48,y-.15,y+.15)
    for y in [.3,2.1,8.7,10.9,14,16.1,18.75]:mullion(19.92,20.56,y-.15,y+.15)
    # Northwest open L stair, stout solid flights and landings rather than fragile individual treads.
    for lo,hi in [(0.18,4.2),(4.2,8.6),(8.6,13.0)]:
        mid=(lo+hi)/2
        pts=np.array([[1.2*s,Z(mid-.4)],[6.9*s,Z(lo-.28)],[6.9*s,Z(lo-.07)],[1.2*s,Z(mid+.25)]])
        ramp=CrossSection([pts]).extrude(1.65*s).transform(np.array([[1,0,0,0],[0,0,-1,18.3*s],[0,1,0,0]]));add(ramp,'north stair flight, thickened solid ramp')
        pts=np.array([[11.65*s,Z(hi-.34)],[17.5*s,Z(mid-.4)],[17.5*s,Z(mid+.25)],[11.65*s,Z(hi-.08)]])
        ramp=CrossSection([pts]).extrude(1.65*s).transform(np.array([[0,0,1,.55*s],[1,0,0,0],[0,1,0,0]]));add(ramp,'west return stair flight, thickened solid ramp')
        cb('stairs',.3,2.55,16.0,18.6,mid-.55,mid+.40,'NW corner intermediate landing')
    col('stairs',.31,6.95,11.6,18.55,.15,13.25)
    # Door reveals and low entry platform are physical source-supported frontage cues.
    cb('frame',7.9,8.35,18.25,19.1,.15,3.1,'entry east jamb')
    cb('frame',12.05,12.5,18.25,19.1,.15,3.1,'entry west jamb')
    cb('paving',7.7,12.7,18.7,20.0,.12,.36,'north entrance low platform')
    result=union(parts);require(str(result.status()).endswith('NoError'),'union failed');return result,regions,features

def save_stl(solid,path):
    m=solid.to_mesh();v=np.asarray(m.vert_properties[:,:3],np.float32);f=np.asarray(m.tri_verts,np.int64);tri=v[f]
    data=bytearray(b'KMU Library II | early exterior | estimated 1:200 | mm'.ljust(80,b'\0')+struct.pack('<I',len(tri)))
    for q in tri:
        n=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(n);require(L>0,'Degenerate export');n/=L;data+=struct.pack('<12fH',*n,*q.ravel(),0)
    path.write_bytes(data);return len(tri)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);file=a.output_dir/'model.stl';n=save_stl(m,file)
    (a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n');shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
    report={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'status':'Core source review, no strict QA yet'}
    (a.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='features'},indent=2))
if __name__=='__main__':main()
