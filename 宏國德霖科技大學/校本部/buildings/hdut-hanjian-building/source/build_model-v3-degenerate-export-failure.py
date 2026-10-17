"""HDUT Han-Jian Hall original exterior, scheme C. Dimensions in estimated metres, output mm."""
from pathlib import Path
import argparse,hashlib,json,os,struct,shutil
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).resolve().parent.parent

def require(v,m):
    if not v:raise RuntimeError(m)
def union(v):return Manifold.batch_boolean(v,OpType.Add)
def box(a,b,c,d,e,f):
    verts=np.round(np.array([[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]],np.float64),6)
    faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint64)
    return Manifold(Mesh64(verts,faces))
def ccw(pts):
    q=np.array(pts,dtype=float)
    if np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))<0:q=q[::-1]
    return q
def make_model(p):
    s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm'];parts=[];regions=[];features=[]
    Z=lambda z:base+s*z
    def B(a,b,c,d,e,f):return box(a*s,b*s,c*s,d*s,Z(e),Z(f))
    def add(o,n):
        require(str(o.status()).endswith('NoError'),n)
        mesh=o.to_mesh64();canonical=Manifold(Mesh64(np.array(np.round(mesh.vert_properties,6),dtype=np.float64,order="C",copy=True),np.array(mesh.tri_verts,dtype=np.uint64,order="C",copy=True)))
        require(str(canonical.status()).endswith('NoError'),'canonical primitive '+n)
        parts.append(canonical);features.append(n)
    def col(mat,a,b,c,d,e,f):regions.append({'material':mat,'bounds_mm':[a*s,b*s,c*s,d*s,Z(e),Z(f)]})
    def cb(mat,a,b,c,d,e,f,n):add(B(a,b,c,d,e,f),n);col(mat,a-.003,b+.003,c-.003,d+.003,e-.003,f+.003)
    def prism_xy(pts,lo,hi,n,mat='wall'):
        o=CrossSection([ccw(pts)*s]).extrude((hi-lo)*s).translate((0,0,Z(lo)));add(o,n)
        xs,ys=zip(*pts);col(mat,min(xs),max(xs),min(ys),max(ys),lo,hi)
    def prism_yz(pts,x0,x1,n,mat='wall'):
        # profile in (Y,Z), extruded along +X.
        q=np.array([[y*s,Z(z)] for y,z in pts]);o=CrossSection([ccw(q)]).extrude((x1-x0)*s).transform(np.array([[0,0,1,x0*s],[1,0,0,0],[0,1,0,0]]));add(o,n)
        ys,zs=zip(*pts);col(mat,x0,x1,min(ys),max(ys),min(zs),max(zs))
    def rounded_column(x,y,lo,hi,w=1.1,n='thickened rounded arcade column'):
        radius=.28 # millimetres; corners remain broad and printable
        q=CrossSection.square((w*s-2*radius,w*s-2*radius)).offset(radius,circular_segments=12).translate(((x-w/2)*s+radius,(y-w/2)*s+radius))
        add(q.extrude((hi-lo)*s).translate((0,0,Z(lo))),n);col('column',x-w/2,x+w/2,y-w/2,y+w/2,lo,hi)
    a,b,c,d=p['base_bounds_m'];add(box(a*s,b*s,c*s,d*s,0,base),'integral base, no neighbouring buildings');col('base',a,b,c,d,-base/s,0)
    cb('paving',-1.5,83.5,-21.0,24.0,-.04,.22,'plain apron; original landscape not reconstructed')
    # Main high classroom strip, rear surface conservative and intentionally unfenestrated.
    # Full interiors omitted; deep east exterior galleries remain open.
    main=B(11.7,66.7,-16.65,-4.35,.20,40.0)
    # Clear source-supported entry passages below the high gallery. No blind internal cavity.
    for a,b in [(33.7,42.8),(45.8,54.8),(57.0,65.4)]:main=main-B(a,b,-17.0,-4.0,.18,4.0)
    add(main,'main high strip with ground-level through entries');col('wall',11.7,66.7,-16.65,-4.35,.2,40)
    # Different end cores supported by the scheme C standard plan, not mirrored.
    cb('core',3.5,11.9,-13.35,-4.35,.18,41.1,'south stair core, recessed rear edge')
    cb('core',66.5,77.7,-16.65,-4.35,.18,41.1,'north toilet/service core, wider rear depth')
    cb('core',77.5,81.9,-13.35,-4.35,.18,40,'north end stair core, distinct projecting end')
    # Open east galleries / floor edges. Main core mass supports their rear roots.
    for i,z in enumerate(p['floor_levels_m_design_analysis'][1:]+[40.0]):
        cb('floor',3.5,81.9,-13.35,.5,z-.65,z,'full-root gallery floor '+str(i+2))
        # rear plate extends to classroom rear edge, not an invented western balcony.
        cb('floor',11.7,77.7,-16.65,-12.9,z-.65,z,'rear roof/floor edge '+str(i+2))
    for x in [11.7,22.7,33.7,44.7,55.7,66.7,77.7]:rounded_column(x,-.1,.18,40,w=1.15,n='east gallery grid column')
    # Continuous solid guard bands substitute for fine bars at print scale.
    for z in p['floor_levels_m_design_analysis'][1:]:
        cb('rail',7.2,77.9,-.05,.51,z-.2,z+1.0,'east gallery continuous thickened guard')
    # Two offset balcony groups seen in the built facade; not every floor duplicates the standard plan.
    for x,z in [(22.7,18.0),(22.7,22.4),(22.7,26.8),(22.7,31.2),(22.7,35.6),(55.7,18.0),(55.7,22.4)]:
        cb('floor',x,x+11,-.3,2.8,z-.65,z,'projecting balcony slab')
        # inclined front fascia with stout back/root; precise pitch is a photograph estimate
        prism_yz([(2.1,z-.25),(2.8,z-.25),(3.3,z+1.65),(2.6,z+1.65)],x,x+11,'sloped balcony fascia','wall')
        cb('rail',x-.04,x+.60,.0,2.97,z-.25,z+1.48,'balcony south return')
        cb('rail',x+10.40,x+11.04,.0,2.97,z-.25,z+1.48,'balcony north return')
    cb('floor',55.7,66.7,-.3,2.8,12.95,13.6,'north lowest plain terrace slab')
    cb('rail',55.7,66.7,2.25,2.85,13.4,14.6,'north lowest plain terrace guard')
    cb('rail',55.7,56.3,-.1,2.85,13.4,14.6,'north lowest plain terrace south return')
    cb('rail',66.1,66.7,-.1,2.85,13.4,14.6,'north lowest plain terrace north return')
    # Large east frame: tapered return panels, no solid plate across the open facade.
    prism_xy([(0,-4.7),(1.0,-4.7),(1.0,2.6),(7.8,-.8),(7.8,.3),(0,4.0)],.18,45,'south giant frame tapered return')
    prism_xy([(82.7,-4.7),(81.7,-4.7),(81.7,2.6),(76.4,-.8),(76.4,.3),(82.7,4.0)],.18,45,'north giant frame tapered return')
    # Higher outer lip slopes down to the main roof at the gallery edge.
    prism_yz([(-.6,39.5),(.2,39.5),(4.0,44.3),(4.0,45.0),(3.3,45.0),(-.6,40.1)],0,82.7,'giant frame sloped top return')
    # North short-side tall slot left open between front frame and end stair, as photographed.
    # Top roof has only basic plane + unequal end cores, no undated PV or equipment.
    # Low side masses and elevated eastern front corridor bound an open-air central court.
    south=B(-1,33.7,.1,22.0,.18,13.6)
    # Source-visible south/front vertical staircase opening and two coarse landings.
    south=south-B(12.0,18.0,16.5,22.2,.17,12.3)
    add(south,'south low wing, source-supported front stair opening');col('wall',-1,33.7,.1,22,.18,13.6)
    for z in [4.8,9.2]:cb('floor',11.7,18.3,16.7,22.2,z-.65,z,'south front stair landing, flights omitted at core stage')
    north=B(69.0,83.0,.1,22.0,.18,13.6)
    # North front portal opens under the elevated front block; width conservative estimate.
    north=north-B(69.0,77.7,16.7,22.2,.17,8.9)
    add(north,'north low wing with front entry portal');col('wall',69,83,.1,22,.18,13.6)
    # 3F lifted crossbar: lower two-storey arcade is genuinely empty between pillars.
    cb('wall',18.0,77.7,17.0,22.0,9.2,13.6,'raised front corridor, third storey')
    # Main long glazing is a shallow recess in the actual solid, later core source review.
    for x in [33.7,44.7,55.7,66.7]:
        rounded_column(x,21.3,.18,9.45,w=1.35,n='front arcade column')
        rounded_column(x,17.5,.18,9.45,w=1.35,n='court-side arcade column')
    # North connector floor/rail already rooted in low wing. Court bounds stay open to the sky.
    # B1 existence is recorded; hidden underground volume and fitout not reconstructed.
    result=union(parts);require(str(result.status()).endswith('NoError'),'final union status')
    # Map drawing-convenience front-positive coordinates into right-handed north/west/up.
    result=result.transform(np.array([[1,0,0,0],[0,-1,0,0],[0,0,1,0]]))
    for q in regions:
        a,b,c,d,e,f=q['bounds_mm'];q['bounds_mm']=[a,b,-d,-c,e,f]
    return result,regions,features

def save_stl(solid,path):
    mesh=solid.to_mesh();v=np.asarray(mesh.vert_properties[:,:3],np.float32);faces=np.asarray(mesh.tri_verts,np.int64)
    data=bytearray(b'HDUT Han-Jian Hall | scheme C / early completed exterior | estimated 1:400 mm'.ljust(80,b'\0')+struct.pack('<I',len(faces)))
    for q in v[faces]:
        normal=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(normal);require(L>0,'Degenerate raw STL export');normal/=L;data+=struct.pack('<12fH',*normal,*q.ravel(),0)
    path.write_bytes(data);return len(faces)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');a=ap.parse_args();require(not a.output_dir.exists(),'Refusing to overwrite a model revision');a.output_dir.mkdir(parents=True)
    p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);n=save_stl(m,a.output_dir/'model.stl')
    (a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n');shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
    r={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256((a.output_dir/'model.stl').read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'status':'CORE source review pending; not QA-passed or printable-certified'}
    (a.output_dir/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='features'},indent=2))
if __name__=='__main__':main()
