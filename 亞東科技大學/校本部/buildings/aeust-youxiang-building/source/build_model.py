"""AEUST Youxiang early representative exterior. All geometry in output millimetres.
Original CSG; no repairs or meshes from third-party sources. No measured scale claimed.
"""
from pathlib import Path
import argparse,hashlib,json,os,struct,shutil,math
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).resolve().parent.parent

def require(v,m):
 if not v: raise RuntimeError(m)
def union(v): return Manifold.batch_boolean(v,OpType.Add)
def ccw(v):
 q=np.array(v,dtype=float)
 if np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))<0:q=q[::-1]
 return q

def box(a,b,c,d,e,f):
 v=np.array([[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]],np.float64)
 faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint64)
 return Manifold(Mesh64(v,faces))
def make_model(p):
 base=p['base_thickness_mm']; parts=[]; regions=[]; features=[]; cuts=[]; glazing=[]
 Z=lambda z:base+z
 def add(o,n):
  require(str(o.status()).endswith('NoError'),n)
  mesh=o.to_mesh64();q=Manifold(Mesh64(np.array(mesh.vert_properties,dtype=np.float64,order='C',copy=True),np.array(mesh.tri_verts,dtype=np.uint64,order='C',copy=True)))
  require(str(q.status()).endswith('NoError'),'canonical '+n);parts.append(q);features.append(n)
 def col(mat,a,b,c,d,e,f):regions.append({'material':mat,'bounds_mm':[a,b,c,d,Z(e),Z(f)]})
 def B(a,b,c,d,e,f):return box(a,b,c,d,Z(e),Z(f))
 def cb(mat,a,b,c,d,e,f,n):
  shape=rr(a,b,c,d,.45).extrude(f-e).translate((0,0,Z(e))) if mat=='column' else B(a,b,c,d,e,f)
  add(shape,n);col(mat,a-.01,b+.01,c-.01,d+.01,e-.01,f+.01)
 def rounded(cs,r):return cs.offset(-r,circular_segments=24).offset(r,circular_segments=24)
 def P(pts,lo,hi,r=0):
  cs=CrossSection([ccw(pts)]);cs=rounded(cs,r) if r else cs
  return cs.extrude(hi-lo).translate((0,0,Z(lo)))
 def poly(pts,lo,hi,n,mat='wall',r=0):
  add(P(pts,lo,hi,r),n);x,y=zip(*pts);col(mat,min(x),max(x),min(y),max(y),lo,hi)
 def rr(a,b,c,d,r):
  return CrossSection.square((b-a-2*r,d-c-2*r)).offset(r,circular_segments=24).translate((a+r,c+r))
 def roundmass(a,b,c,d,r,lo,hi,n,mat='wall'):
  add(rr(a,b,c,d,r).extrude(hi-lo).translate((0,0,Z(lo))),n);col(mat,a,b,c,d,lo,hi)
 def line_prism(a,b,width,lo,hi,n,mat='wall'):
  a=np.array(a);b=np.array(b);t=b-a;t=t/np.linalg.norm(t);nrm=np.array([-t[1],t[0]])*width/2
  poly([a+nrm,b+nrm,b-nrm,a-nrm],lo,hi,n,mat)
 def orientbox(origin,tangent,u0,u1,v0,v1,z0,z1):
  o=np.array(origin,dtype=float);t=np.array(tangent,dtype=float);t=t/np.linalg.norm(t);n=np.array([t[1],-t[0]])
  pts=[o+u*t+v*n for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
  return P(pts,z0,z1),pts
 def window(o,bounds):cuts.append(o);glazing.append(bounds)
 # integral base, not a representation of measured land boundary
 a,b,c,d=p['base_bounds_mm'];add(box(a,b,c,d,0,base),'integral 3 mm model base');col('base',a,b,c,d,-base,0)
 # Long A classroom mass. Courtyard and campus galleries in front are distinct from this solid.
 A=[(4.2,0),(203.2,0),(208.2,-2.5),(205,-16.7),(11,-16.7),(0,-5.5),(0,-2.8)]
 poly(A,-.1,106,'A long wing main body; rear details pending source comparison')
 # B diagonal classroom body, nonparallel with A. End lowered beneath its own roof crown.
 Bp=[(96.5,-62),(189.8,-38.0),(196.3,-60.3),(103.3,-84.6)]
 poly(Bp,-.1,106,'B shorter diagonal wing; unequal to A',r=.8)
 # D separate campus end core, rounded only on its observed end and below overhanging glass box.
 D=rr(70.8,92.8,-90.0,-63.0,3.0).extrude(82.1).translate((0,0,Z(-.1)))
 D=D-B(74.0,88.8,-91.0,-64.0,-.2,10.0)
 add(D,'D narrower lower rounded end with genuine ground entry opening');col('wall',70.8,92.8,-90,-63,-.1,82)
 # Recess entry below the cantilever is kept genuinely open in the foreground.
 # Narrow tall solid back wall extends above glass box as in 2007/2008 photos.
 poly([(90.0,-63.5),(99.5,-61.2),(105.5,-86.2),(96.2,-88.6)],-.1,116,'D tall offset solid core behind upper glass box','core',r=.8)
 roundmass(60.7,96.0,-96.0,-60.0,1.3,82,108,'D cantilever upper green glass box, broader than lower end','glass')
 # A projecting campus glass stair at paper-left return; independent from D box.
 roundmass(20,30,-33.5,-14.0,.9,-.1,112,'A campus-side vertical glass stair','glass')
 # Repeated gallery slabs along A's courtyard/campus edge.
 # Inner A edge at y=-22.2: slabs reach main solid by >1mm overlap.
 levels=p['representative_floor_levels_mm'][1:]
 for i,z in enumerate(levels):
  cb('floor',8,194.5,-22.3,-15.6,z-1.4,z,'A inward gallery slab '+str(i+2))
  # B inward gallery, broad root into its diagonal classroom body.
  poly([(96.3,-58.4),(192.9,-35.1),(191.4,-41.4),(97.4,-65.1)],z-1.4,z,'B inward gallery slab '+str(i+2),'floor',r=.65)
  # campus crosslink (paper x675–760), separated horizontal floors
  cb('floor',84.0,97.2,-65.0,-15.8,z-1.5,z,'campus A–D crosslink floor '+str(i+2))
  # intermediate bridge separates the large courtyard from the small end void
  cb('floor',159.1,172.5,-44.7,-15.8,z-1.5,z,'intermediate A–B crosslink floor '+str(i+2))
 # thickened gallery/crosslink edge columns (no delicate railing at blockout)
 for x in [8,30,51,72,84,97,118,139,159,172,194]:
  cb('column',x-.9,197.2 if x==194 else x+.9,-22.3,-15.8 if x==194 else -19.8,-.1,106,'A inward structural rhythm; last pier rooted to main wing')
 for x in [97,118,139,159,172,191]:
  y=-58.4+(x-96.3)*23.3/96.6
  cb('column',x-.9,x+.9,-46.2 if x==191 else y-1.7,y+.3,-.1,106,'B inward structural rhythm; last pier rooted into wing')
 # Campus and intermediate crosslink sides; slab space is open, not an extruded solid rectangle.
 for x,y in [(84,-45),(97,-45),(159,-35),(172,-35)]:cb('column',x-.9,x+.9,y-.9,y+.9,-.1,106,'crosslink column')
 # Photographed upper crossbar hides two highest gallery levels, not the entire court.
 E=B(84,97.2,-64,-16,94,106)
 for y in [-58,-50,-42,-34,-26]:E=E-B(83.5,97.7,y,y+3.0,100.0,103.5)
 for y in [-60,-55,-50,-45,-40,-35,-30,-25]:E=E-B(83.5,97.7,y,y+2.0,95.5,98.0)
 add(E,'campus upper crossbar with local perforations, without cutting adjoining wings');col('wall',84,97.2,-64,-16,94,106)
 cb('wall',159.1,172.5,-44,-16,98,106,'intermediate top connector')
 # C street-side giant frame. Slanted segment is aligned to paper end, not orthogonalised.
 # C's source-plan sides are almost parallel. A common local strip axis removes
 # incidental sub-micron mismatches between separately filleted elevation bands.
 # The unfilleted common-axis corners shift <0.3 mm; 0.65 mm fillets are additional.
 ca=np.array([203.45,-1.75]);ct=np.array([-11.8,-57.4]);cl=float(np.linalg.norm(ct));ct/=cl;cn=np.array([-ct[1],ct[0]])
 c_transform=np.array([[cn[0],ct[0],ca[0]],[cn[1],ct[1],ca[1]]])
 def c_interval(y0,y1):return sorted([(y0-ca[1])/ct[1],(y1-ca[1])/ct[1]])
 street_parts=[];c_levels=[-.1,10,11,26,27,94,95.5,98,99.5,103,106]
 for lo,hi in zip(c_levels,c_levels[1:]):
  mid=(lo+hi)/2;holes=[]
  if mid<10:holes.append(c_interval(-49,-23))
  if 11<mid<26 or 27<mid<94:holes.append(c_interval(-49,-20.5))
  if 95.5<mid<98:holes.extend(c_interval(y,y+1.8) for y in [-48,-44,-40,-36,-32,-28,-24])
  if 99.5<mid<103:holes.extend(c_interval(y,y+3) for y in [-46,-39,-32,-25])
  cursor=0;segments=[]
  for u0,u1 in sorted(holes):
   if u0>cursor:segments.append((cursor,u0))
   cursor=max(cursor,u1)
  if cursor<cl:segments.append((cursor,cl))
  for u0,u1 in segments:
   require(u1-u0>1.3,'C local segment too short for designed corner radius')
   cs=rr(-4.8,4.8,u0,u1,.65).transform(c_transform)
   street_parts.append(cs.extrude(hi-lo).translate((0,0,Z(lo))))
 add(union(street_parts),'C giant street frame with common-axis rounded aperture returns');col('wall',183,209,-61,0,-.1,106)
 # Rounded A/C corner tower distinct from campus D tower.
 roundmass(194.0,208.7,-20.5,.15,4.3,18,98,'street A/C rounded corner tower ten green intervals','glass')
 roundmass(193.4,209.3,-21.1,.75,4.6,10,18,'street rounded lower white body','wall')
 roundmass(193.4,209.3,-21.1,.75,4.6,98,106,'street rounded upper white body','wall')
 # Glazed low horizontal street podium is a solid recessed representative panel, not transparent topology.
 line_prism((198.0,-17.2),(190.0,-54.5),3.0,10,27,'street lower horizontal glazing band','glass')
 # Tall glass plane inset behind street frame visible in source; leaves actual aperture.
 line_prism((186,-48),(190,-30),2.0,27,94,'street inset vertical glass strip','glass')
 # Simple roof blocks only where early photos show raised mass; no equipment invented.
 cb('roof',189,204,-16,-3,105.5,116,'street roof raised solid crown')
 cb('roof',3,16,-13,-2,105.5,111,'A far end conservative stepped crown')
 # Conservative low entry landings: no inferred site paving or adjacent buildings.
 cb('paving',65,84,-96,-75,.0,1.3,'campus entrance simplified landing')
 # Upper perforations are local to E/C solids; adjacent wing geometry is never cut through.
 # A outer street long facade: paired small recesses with unequal end strips.
 # Window counts, dimensions and recess depths are print-scale approximations.
 for z in levels[:-1]:
  for x in [22.0+9.0*i for i in range(19)]:
   for a,b in [(x,x+2.6),(x+3.6,x+6.2)]:
    if a<83.6 and b>79.6:continue # preserve root of the independently observed vertical glazing strip
    window(B(a,b,-1.2,.3,z+2.0,z+5.8),(a,b,-1.21,.31,z+1.99,z+5.81))
 # Coarse vertical facade piers and one photograph-visible outer vertical glass strip.
 for x in [20.0+9*i for i in range(20)]:cb('wall',x,x+1.3,-.5,.8,10,106,'A outer vertical facade pier')
 for x,hi in [(80,109.5)]:
  roundmass(x,x+3.2,-.7,1.25,.45,10,hi,'A outer narrow glazing vertical, estimated placement','glass')
 # A visible inward gallery wall: broad openings, different from A's paired street windows.
 for z in levels[:-1]:
  for x in [32.0,53.0,74.0,100.0,121.0,142.0,175.0]:
   window(B(x,x+14.0,-17.1,-15.7,z+2.0,z+5.9),(x,x+14,-17.11,-15.69,z+1.99,z+5.91))
 # Broad gallery guard bands are thickened replacements for fine original rails.
 for z in levels[:-1]:
  cb('rail',8,194.3,-22.3,-21.1,z-.15,z+1.25,'A coarse integral gallery guard')
  poly([(96.3,-58.4),(192.9,-35.1),(193.2,-36.3),(96.6,-59.6)],z-.15,z+1.25,'B coarse integral gallery guard','rail',r=.45)
  cb('rail',84.0,85.3,-64,-22,z-.15,z+1.25,'E campus-facing coarse guard')
  cb('rail',159.1,160.4,-44,-22,z-.15,z+1.25,'F courtyard-facing coarse guard')
 # B outer diagonal facade uses its own orientation and broad openings.
 bo=(103.3,-84.6);bt=(93.0,24.3)
 for z in levels[:-1]:
  for u in [6.5+11.0*i for i in range(8)]:
   q,pts=orientbox(bo,bt,u,u+8.0,-1.2,.25,z+2.0,z+5.9)
   xs,ys=zip(*pts);window(q,(min(xs)-.01,max(xs)+.01,min(ys)-.01,max(ys)+.01,z+1.99,z+5.91))
 # Subtle inner B recesses visible in the deep courtyard, no fitout or door replication.
 bio=(96.5,-62.0);bit=(93.3,24.0)
 for z in levels[:-1]:
  for u in [7,28,49,70]:
   q,pts=orientbox(bio,bit,u,u+14,-.25,1.15,z+2,z+5.7)
   xs,ys=zip(*pts);window(q,(min(xs)-.01,max(xs)+.01,min(ys)-.01,max(ys)+.01,z+1.99,z+5.71))
 # D local rounded window strips only on the photographed campus-facing corner.
 d_outer=rr(70.6,93.0,-90.2,-62.8,3.2)
 d_inner=rr(72.0,91.6,-88.8,-64.2,1.8)
 clip=CrossSection([ccw([(69,-92),(87,-92),(87,-85.4),(75.5,-85.4),(75.5,-69),(69,-69)])])
 d_cut=(d_outer-d_inner)^clip
 for z in [26,34,42,50,58,66,74]:
  cuts.append(d_cut.extrude(4.5).translate((0,0,Z(z+1.4))))
  glazing.extend([(70.5,87.1,-90.3,-85.3,z+1.39,z+5.91),(70.5,75.6,-85.5,-68.9,z+1.39,z+5.91)])
 # Lower two-storey glazed band above the ground entry, kept recessed in the solid.
 cuts.append(d_cut.extrude(13.6).translate((0,0,Z(11.2))))
 glazing.extend([(70.5,87.1,-90.3,-85.3,11.19,24.81),(70.5,75.6,-85.5,-68.9,11.19,24.81)])
 # D high white core has a sparse observed single vertical window stack.
 for z in [18,26,34,42,50,58,66,74,82,90,98,106]:
  q,pts=orientbox((96.2,-88.6),(9.3,2.4),2.5,5.5,-1.2,.3,z+2,z+4.8)
  xs,ys=zip(*pts);window(q,(min(xs)-.01,max(xs)+.01,min(ys)-.01,max(ys)+.01,z+1.99,z+4.81))
 # Green box coarse mullion grooves. Only exposed campus/front/side surfaces are marked.
 for x in [64.5+4.4*i for i in range(7)]:cuts.append(B(x,x+.65,-96.2,-95.1,82,108.2))
 for y in [-92.0+4.4*i for i in range(7)]:cuts.append(B(60.5,61.6,y,y+.65,82,108.2))
 for z in [85.5,89.7,93.9,98.1,102.3,106.5]:
  cuts.append(B(60.5,96.2,-96.2,-95.1,z,z+.65));cuts.append(B(60.5,61.6,-96.2,-59.8,z,z+.65))
 # Street A/C corner bands are geometry, not a solid colour tube.
 for z in [26,34,42,50,58,66,74,82,90]:
  roundmass(193.4,209.3,-21.1,.75,4.6,z-1.8,z+.3,'C broad rounded horizontal wall band','floor')
 # One source-visible A-side square window in the upper white A/C corner body.
 window(B(199,202,-.6,1.1,100,103),(198.99,202.01,-.61,1.11,99.99,103.01))
 # Street lower glazing is outward at the source-observed two-storey podium height.
 # Keep its high giant opening empty: no flat dark/green fill plane.
 for bounds in glazing:col('glass',*bounds)
 # Recessed B-end wall behind C's high aperture: material only on its existing outward plane.
 # Original triangles already delimit the tall 27..94 mm patch; no void-spanning new solid.
 bn=np.array([22.3,6.5,0.0]);bn/=np.linalg.norm(bn)
 regions.append({'material':'glass','plane_band':{'point_mm':[189.8,-38.0,Z(27)],'outward_normal':bn.tolist(),'plane_tolerance_mm':.001,'minimum_normal_dot':.999,'z_bounds_mm':[Z(27),Z(94)]}})
 # The rooted B terminal pier shares this recessed representative glazed zone.
 regions.append({'material':'glass','plane_band':{'point_mm':[191.9,-40.0,Z(27)],'outward_normal':[1.0,0.0,0.0],'plane_tolerance_mm':.001,'minimum_normal_dot':.999,'z_bounds_mm':[Z(27),Z(94)],'y_bounds_mm':[-45.21,-35.70]}})
 col('dark',60.7,96,-96,-60,81.99,82.01)
 features.append('source-supported facade recesses and thickened guard bands; unknown paper-left short end stays plain')
 result=(union(parts)-union(cuts)).as_original().set_tolerance(p['construction_simplify_tolerance_mm']).simplify(p['construction_simplify_tolerance_mm']);require(str(result.status()).endswith('NoError'),'final union')
 return result,regions,features

def save_stl(solid,path):
 mesh=solid.to_mesh();v=np.asarray(mesh.vert_properties[:,:3],np.float32);faces=np.asarray(mesh.tri_verts,np.int64)
 data=bytearray(b'AEUST Youxiang | early representative exterior | relative estimates, no scale'.ljust(80,b'\0')+struct.pack('<I',len(faces)))
 for q in v[faces]:
  normal=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(normal);require(L>0,'Degenerate raw STL export');normal/=L;data+=struct.pack('<12fH',*normal,*q.ravel(),0)
 path.write_bytes(data);return len(faces)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');a=ap.parse_args();require(not a.output_dir.exists(),'Refusing overwrite');a.output_dir.mkdir(parents=True)
 shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
 p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);n=save_stl(m,a.output_dir/'model.stl')
 (a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n');shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
 r={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256((a.output_dir/'model.stl').read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'status':'source-supported facade candidate; final appearance and digital verification pending, no physical print'}
 (a.output_dir/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='features'},indent=2))
if __name__=='__main__':main()
