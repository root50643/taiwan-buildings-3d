"""Original WFU Shengyou representative exterior CSG, output in model mm.
The building is a school-labeled 2014 aerial interpretation, not metric reconstruction.
The 2025 plans only constrain relative topology. No source image/vector is loaded.
"""
from pathlib import Path
import argparse,hashlib,json,os,struct,shutil,math
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).resolve().parent.parent

def require(v,m):
 if not v:raise RuntimeError(m)
def union(v):return Manifold.batch_boolean(v,OpType.Add)
def ccw(v):
 q=np.array(v,dtype=float)
 if np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))<0:q=q[::-1]
 return q

def box(a,b,c,d,e,f):
 v=np.array([[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]],np.float64)
 faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint64)
 return Manifold(Mesh64(v,faces))

def make_model(p):
 base=p['base_thickness_mm'];parts=[];regions=[];features=[];cuts=[]
 Z=lambda z:base+z
 s=p['relative_plan_point_to_model_mm'];ox,oy=p['plan_reference_origin']
 xy=lambda q:np.array([(q[0]-ox)*s,(q[1]-oy)*s])
 def region(mat,pts,lo,hi):
  pts=np.array(pts);regions.append({'material':mat,'bounds_mm':[float(pts[:,0].min())-.02,float(pts[:,0].max())+.02,float(pts[:,1].min())-.02,float(pts[:,1].max())+.02,Z(lo)-.02,Z(hi)+.02]})
 def add(q,n,mat=None,bounds=None):
  require(str(q.status()).endswith('NoError'),n)
  mesh=q.to_mesh64();q=Manifold(Mesh64(np.array(mesh.vert_properties,dtype=np.float64,order='C',copy=True),np.array(mesh.tri_verts,dtype=np.uint64,order='C',copy=True)))
  require(str(q.status()).endswith('NoError'),'canonical '+n);parts.append(q);features.append(n)
  if mat and bounds:region(mat,bounds[0],bounds[1],bounds[2])
 def cs(pts,r=.5):
  c=CrossSection([ccw(pts)])
  return c.offset(-r,circular_segments=16).offset(r,circular_segments=16) if r else c
 def P(pts,lo,hi,r=.5):return cs(pts,r).extrude(hi-lo).translate((0,0,Z(lo)))
 def poly(pts,lo,hi,n,mat='wall',r=.5):add(P(pts,lo,hi,r),n,mat,(pts,lo,hi))
 def plan(pts,lo,hi,n,mat='wall',r=.5):poly([xy(q) for q in pts],lo,hi,n,mat,r)
 def B(a,b,c,d,e,f):return box(a,b,c,d,Z(e),Z(f))
 def block(a,b,c,d,e,f,n,mat='wall',r=.5):poly([(a,c),(b,c),(b,d),(a,d)],e,f,n,mat,r)
 def strip(a,b,width,lo,hi,n,mat='wall'):
  a=np.array(a,dtype=float);b=np.array(b,dtype=float);t=b-a;t/=np.linalg.norm(t);d=np.array([-t[1],t[0]])*width/2
  poly([a+d,b+d,b-d,a-d],lo,hi,n,mat,r=.45)
 def beam(a,b,width,n,mat='roof'):
  # Original CSG hull of vertical rounded end volumes. Flat caps avoid vanishing
  # XY tip islands; visible long axis and open structural gaps remain unchanged.
  a=np.array(a,dtype=float);b=np.array(b,dtype=float)
  caps=[Manifold.cylinder(width,width/2,circular_segments=24).translate((v[0],v[1],Z(v[2]-width/2))) for v in [a,b]]
  q=Manifold.batch_hull(caps);add(q,n);region(mat,[a[:2]-width,b[:2]+width],min(a[2],b[2])-width,max(a[2],b[2])+width)
 def roof_panel(quad,thick,n,mat='roof',closed_interior=False):
  v=np.array(quad,dtype=float);v[:,2]+=base;bottom=v-[0,0,thick]
  if closed_interior:bottom[:,2]=Z(86.9)
  v=np.vstack([bottom,v]);faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],dtype=np.uint64)
  if np.dot(np.cross(v[1]-v[0],v[2]-v[0]),[0,0,1])<0:faces=faces[:,::-1]
  q=Manifold(Mesh64(v,faces))
  if closed_interior:q=q^P(np.array(quad)[:,:2],86.8,max(np.array(quad)[:,2])+.1,r=.6)
  add(q,n);region(mat,np.array(quad)[:,:2],min(np.array(quad)[:,2])-thick,max(np.array(quad)[:,2]))
 a,b,c,d=p['base_bounds_mm'];add(box(a,b,c,d,0,base),'integral model base, not a surveyed site boundary');region('base',[(a,c),(b,d)],-base,0)
 # Plan-derived low V arms, with the source's genuinely open three-storey apex.
 left_full=[(499,15),(80,426),(164,426),(499,99)]
 right_full=[(499,15),(910,426),(832,426),(499,99)]
 wing_cs=CrossSection([ccw([xy(q) for q in left_full])])+CrossSection([ccw([xy(q) for q in right_full])])
 wing_cs=wing_cs.offset(-.6,circular_segments=16).offset(.6,circular_segments=16)
 # The lower occupied wings stop before the entrance apex; upper two floors bridge it.
 lower_cs=wing_cs-CrossSection.square((230,(112-15)*s+20)).translate((-115,-20))
 lower_cs=lower_cs.offset(-.6,circular_segments=16).offset(.6,circular_segments=16)
 add(lower_cs.extrude(33.5).translate((0,0,Z(-.1))),'rounded lower wing entrance ends; large apex remains open')
 add(wing_cs.extrude(18.1).translate((0,0,Z(32.9))),'continuous upper 4F/5F entrance crossing')
 # Floor-specific rear masses: irregular lower footprint rather than uniform third wing.
 rear_levels=[
  (-.1,15,[(140,448),(893,448),(920,573),(597,675),(550,675),(499,697),(405,607),(291,607),(140,524)]),
  (15,24,[(140,448),(893,448),(920,573),(610,675),(554,675),(499,697),(404,607),(291,607),(140,524)]),
  (24,33,[(140,448),(893,448),(920,573),(610,675),(554,675),(499,697),(404,607),(291,607),(140,524)]),
  (33,42,[(140,448),(893,448),(920,573),(795,607),(594,607),(499,697),(405,607),(291,607),(140,524)]),
  (42,51,[(140,448),(893,448),(920,561),(792,607),(594,607),(499,697),(405,607),(291,607),(140,524)])
 ]
 for i,(lo,hi,pts) in enumerate(rear_levels):plan(pts,lo,hi,'irregular rear lower mass floor '+str(i+1))
 # Reconnected low-wing rear bands verified on p6. These are not courtyard voids.
 plan([(140,420),(230,420),(246,442),(246,450),(140,450)],-.1,51,'paper-left low-wing rear connecting body')
 plan([(766,420),(878,420),(878,450),(752,450),(752,442)],-.1,51,'paper-right low-wing rear connecting body')
 # The upper small triangle is separate; its two unobserved diagonal elevations stay plain.
 high=[(244.078,442.375),(753.662,442.375),(499,697.229)]
 plan(high,-.1,87,'smaller high body, 6F–9F only above low wings')
 # Source-visible inward galleries, open between floor slabs. These do not fill the court.
 left_gallery=[(499,94),(159,429),(230,429),(230,409),(499,137)]
 right_gallery=[(499,94),(837,429),(766,429),(766,409),(499,137)]
 for k,z in enumerate([6,15,24,33,42,51]):
  pts=[xy(q) for q in left_gallery+right_gallery]
  C=CrossSection([ccw([xy(q) for q in left_gallery])])+CrossSection([ccw([xy(q) for q in right_gallery])])
  if z<33:C=C^CrossSection.square((230,160)).translate((-115,(168-15)*s))
  C=C.offset(-.6,circular_segments=16).offset(.6,circular_segments=16)
  add(C.extrude(1.8).translate((0,0,Z(z-1.8))),'continuous paired inward gallery slab '+str(k+1),'floor',(pts,z-1.8,z))
  plan([(230,426),(766,426),(754,449),(244,449)],z-1.8,z,'high-body long inward terrace '+str(k+1),'floor')
 # Thickened gallery columns and source-observed tall portico piers.
 for side in [-1,1]:
  for u in [67,134,201,269]:
   pp=(499+side*u,137+u);q=xy(pp)
   block(q[0]-1.4,q[0]+1.4,q[1]-1.4,q[1]+1.4,-.1,51,'gallery column','column',.5)
 for pp in [(499,25),(433,88),(565,88)]:
  q=xy(pp);block(q[0]-1.7,q[0]+1.7,q[1]-1.7,q[1]+1.7,-.1,33.5,'three-storey entrance portico pier','wall',.55)
 # Entry terrace and steps; court ground is lower, not a uniform through-hole.
 plan([(499,1),(382,118),(452,192),(546,192),(616,118)],-.1,6,'entry raised landing with large portico above','paving',1.8)
 for z,w in [(1.5,4.5),(3,3),(4.5,1.5)]:
  C=cs([xy(q) for q in [(499,1),(382,118),(452,192),(546,192),(616,118)]],1.8).offset(w,circular_segments=16)
  C=C^CrossSection.square((100,42)).translate((-50,-10))
  add(C.extrude(z+.1).translate((0,0,Z(-.1))),'conservative shallow entrance approach step')
 plan([(466,191),(532,191),(532,352),(600,421),(600,448),(566,448),(499,380),(432,448),(398,448),(398,421),(466,352)],-.1,6,'lower courtyard Y walk; estimated relative level','paving',1)
 plan([(499,291),(620,424),(378,424)],6,15,'courtyard projecting upper terrace; lower garden remains open','paving',1)
 # Low-wing flat roofs, parapet lips and observed small end service masses.
 for a,b in [((499,15),(80,426)),((499,15),(910,426)),((499,137),(230,409)),((499,137),(766,409))]:strip(xy(a),xy(b),1.5,50.5,53,'low roof parapet','wall')
 for pts in [[(104,394),(140,360),(184,404),(166,426),(104,426)],[(892,394),(856,360),(812,404),(832,426),(892,426)]]:plan(pts,50.5,61,'low wing terminal raised service volume')
 # Four upper primary bands, physically recessed into the photographed face only.
 # Coarsened mullion spacing is an explicit print-scale estimate, not measured counts.
 for i,(lo,hi) in enumerate([(53,59),(62,68),(71,77),(81,85)]):
  for k in range(18):
   x0=-49+5.6*k;x1=min(x0+4.4,49)
   for za,zb in ([(lo,lo+4.1),(lo+5.1,hi)] if hi-lo>5 else [(lo,hi)]):
    cuts.append(B(x0,x1,101.8,103.8,za,zb));region('glass',[(x0,101.8),(x1,103.8)],za,zb)
  block(-49.4,49.4,101.3,103.4,lo-1.2,lo,'high horizontal sill '+str(i+1),'floor')
 # Visible lower part of the high courtyard face, separate from the four upper bands.
 for z in [6,15,24,33,42]:
  for x0,x1 in [(-49,-33),(-31,-15),(-13,3),(5,21),(23,39),(41,49)]:
   cuts.append(B(x0,x1,101.8,103.8,z+2,z+7));region('glass',[(x0,101.8),(x1,103.8)],z+2,z+7)
 # Low-wing outside bands and the inward gallery back-wall openings use different rhythms.
 def orientcut(a,b,u0,u1,v0,v1,lo,hi,mat='glass'):
  a=np.array(a);b=np.array(b);t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]])
  pts=[a+u*t+v*n for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
  cuts.append(P(pts,lo,hi,r=.25));region(mat,pts,lo,hi)
 for side,end in [(-1,(80,426)),(1,(910,426))]:
  a=xy((499,15));b=xy(end)
  # The left local normal points outside; the right local normal points inside.
  v0,v1=(-1.25,.4) if side==-1 else (-.4,1.25)
  for z in [6,15,24,33,42]:
   # Only paper-right has a clearly visible long exterior in 75/110 s.
   # Wider paired/multiple panes at the entrance, medium main bays, short tail bays.
   if side==1:
    groups=([(6,36,3),(41,60,2),(65,84,2),(89,107,2),(113,122,1),(127,134,1)] if z>=33 else [(41,57,2),(63,79,2),(85,101,2),(109,119,1),(125,134,1)])
   else:
    # Conservative broad recesses only: obscured wing has no invented repeated grid.
    groups=([(8,33,2),(49,68,1),(91,107,1)] if z>=33 else [(49,68,1),(91,107,1)])
   for u0,u1,count in groups:
    gap=1.5;w=(u1-u0-gap*(count-1))/count
    for k in range(count):orientcut(a,b,u0+k*(w+gap),u0+k*(w+gap)+w,v0,v1,z+2,z+7)
    t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]])
    outside=1 if side==-1 else -1
    pts=[a+u*t+v*n for u,v in [(u0-.5,-.8),(u1+.5,-.8),(u1+.5,.8),(u0-.5,.8)]]
    poly(pts,z+.9,z+2,'source-visible horizontal low-wing sill','floor',r=.45)
  # Classroom backs are recessed behind the open galleries; no repeated outside strips here.
  ia=xy((499,99));ib=xy((164,426) if side==-1 else (832,426))
  iv0,iv1=(-.4,1.25) if side==-1 else (-1.25,.4)
  for z in [6,15,24,33,42]:
   for u in [18,40,62,84]:
    if z<33 and u<26:continue
    orientcut(ia,ib,u,u+3.1,iv0,iv1,z+.3,z+7)
    orientcut(ia,ib,u+5.2,u+14.2,iv0,iv1,z+3,z+7)
  # Integral coarse gallery guards replace sub-print-size source rails.
  ga=xy((499,137));gb=xy((230,409) if side==-1 else (766,409));t=(gb-ga)/np.linalg.norm(gb-ga);n=np.array([-t[1],t[0]])*.75
  pts=[ga+n,gb+n,gb-n,ga-n]
  for z in [6,15,24,33,42]:
   C=CrossSection([ccw(pts)])
   if z<33:C=C^CrossSection.square((230,160)).translate((-115,(168-15)*s))
   C=C.offset(-.5,circular_segments=16).offset(.5,circular_segments=16)
   add(C.extrude(2.7).translate((0,0,Z(z-.3))),'thickened open-gallery guard', 'rail',(pts,z-.3,z+2.4))
 # Lower garden remains exposed beside the source-topology Y path and raised triangle.
 for a,b in [((499,291),(620,424)),((499,291),(378,424))]:strip(xy(a),xy(b),1.6,14.7,17.2,'coarse courtyard terrace edge guard','rail')
 # Distinctive high roof: solid deck below, OPEN perimeter framing above.
 # Central panels occupy only part of the triangular deck. Exact hidden roof shape is unknown.
 strip((-61,102.6),(61,102.6),2.3,86.5,90,'front roof parapet','wall')
 for x in [-61,61]:
  beam((x,102.6,89),(0,164,110),2.8,'open sloping perimeter roof beam')
  beam((x,102.6,87),(x,102.6,90),3.8,'roof front end wall reinforcement','wall')
 caps=[Manifold.cylinder(24.6,1.5,circular_segments=24).translate((0,y,Z(86.9))) for y in [159,164]]
 add(Manifold.batch_hull(caps),'rounded ridge support with continuous capsule cap; model simplification')
 roof_panel([(-30,104,89),(30,104,89),(37,115,96),(-37,115,96)],2,'sloping pale front skylight abstraction','skylight',closed_interior=True)
 roof_panel([(-37,115,96),(37,115,96),(22,141,104),(-22,141,104)],2,'central opaque sloping roof panel',closed_interior=True)
 roof_panel([(-13,145,105),(13,145,105),(.8,158,109),(-.8,158,109)],2,'upper pale roof segment separated by visible high gap','skylight')
 # Integral rounded frames sit 1.4 mm below every panel edge. This covers
 # otherwise acute printable panel edges without filling the large structural gaps.
 roof_edges=[((-30,104,89),(30,104,89)),((-30,104,89),(-37,115,96)),((30,104,89),(37,115,96)),((-37,115,96),(37,115,96)),((-22,141,104),(22,141,104)),((-13,145,105),(13,145,105)),((-37,115,96),(-22,141,104)),((37,115,96),(22,141,104)),((-13,145,105),(-.8,158,109)),((13,145,105),(.8,158,109)),((-.8,158,109),(.8,158,109)),((-.8,158,109),(0,164,110)),((.8,158,109),(0,164,110))]
 for a,b in roof_edges:beam((a[0],a[1],a[2]-1.4),(b[0],b[1],b[2]-1.4),2.8,'rounded integral panel-edge frame')
 for side in [-1,1]:beam((side*26,134,100),(side*31,134,100),4,'local integral roof junction collar; unverified manufacturing estimate')
 features.append('roof slope/ridge and hidden support positions are explicit model estimates; large side and near-ridge gaps retained')
 m=(union(parts)-union(cuts)).as_original().set_tolerance(p['construction_simplify_tolerance_mm']).simplify(p['construction_simplify_tolerance_mm'])
 require(str(m.status()).endswith('NoError'),'final union');return m,regions,features

def save_stl(solid,path):
 mesh=solid.to_mesh();v=np.asarray(mesh.vert_properties[:,:3],np.float32);faces=np.asarray(mesh.tri_verts,np.int64)
 data=bytearray(b'WFU Shengyou | 2014-label exterior representative | model mm, no metric scale'.ljust(80,b'\0')+struct.pack('<I',len(faces)))
 for q in v[faces]:
  normal=np.cross(q[1].astype(float)-q[0],q[2].astype(float)-q[0]);L=np.linalg.norm(normal);require(L>0,'Degenerate raw STL export');normal/=L;data+=struct.pack('<12fH',*normal,*q.ravel(),0)
 path.write_bytes(data);return len(faces)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=R/'models'/'v0');a=ap.parse_args();require(not a.output_dir.exists(),'Refusing overwrite');a.output_dir.mkdir(parents=True)
 shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py')
 p=json.loads((R/'parameters.json').read_text());m,regions,features=make_model(p);n=save_stl(m,a.output_dir/'model.stl')
 (a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n')
 r={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256((a.output_dir/'model.stl').read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'model_scope':'Original representative exterior in model millimetres; no metric building scale; no physical print claimed'}
 (a.output_dir/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='features'},indent=2))
if __name__=='__main__':main()
