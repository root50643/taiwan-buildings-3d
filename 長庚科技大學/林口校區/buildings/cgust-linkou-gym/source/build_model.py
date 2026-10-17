"""Original CGUST Linkou gym proportional exterior CSG in model mm.
No reference image, original drawing or texture is loaded by this generator.
A/B main roof height step and eccentric lower B roof remain actual geometry.
"""
from pathlib import Path
import os,argparse,json,hashlib,struct,shutil
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from manifold3d import Manifold,CrossSection,OpType,Mesh64
R=Path(__file__).resolve().parent.parent

def require(v,m):
 if not v:raise RuntimeError(m)
def union(parts):return Manifold.batch_boolean(parts,OpType.Add)
def ccw(v):
 q=np.array(v,dtype=float)
 if np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))<0:q=q[::-1]
 return q
def box(a,b,c,d,e,f):
 v=np.array([[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]],np.float64)
 faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint64)
 return Manifold(Mesh64(v,faces))
def make_model(p):
 parts=[];cuts=[];late=[];regions=[];features=[]
 def region(mat,bounds):regions.append({'material':mat,'bounds_mm':list(bounds)})
 def add(s,n,mat=None,bounds=None):
  require(str(s.status()).endswith('NoError'),n);parts.append(s);features.append(n)
  if mat:region(mat,bounds)
 def block(a,b,c,d,e,f,n,mat='wall'):
  add(box(a,b,c,d,e,f),n,mat,(a-.01,b+.01,c-.01,d+.01,e-.01,f+.01))
 def lateblock(*args,**kwargs):
  block(*args,**kwargs);late.append(parts.pop())
 def rounded_block(a,b,c,d,e,f,n,mat='wall'):
  # Original model-space rounded pillar, no post-export repair.
  q=CrossSection([ccw([(a,c),(b,c),(b,d),(a,d)])]).offset(-.5,circular_segments=16).offset(.5,circular_segments=16)
  add(q.extrude(f-e).translate((0,0,e)),n,mat,(a-.01,b+.01,c-.01,d+.01,e-.01,f+.01))
 def poly(pts,z0,z1,n,mat='annex'):
  q=np.array(pts);add(CrossSection([ccw(pts)]).extrude(z1-z0).translate((0,0,z0)),n,mat,(q[:,0].min()-.01,q[:,0].max()+.01,q[:,1].min()-.01,q[:,1].max()+.01,z0-.01,z1+.01))
 def roof(x0,x1,y0,y1,eave,rise,n):
  # Closed filled roof volume. Parabolic curve is a model-design estimate.
  xs=np.linspace(x0,x1,p['curve_segments']+1);zs=eave+rise*(1-((xs-(x0+x1)/2)/((x1-x0)/2))**2)
  profile=[(x0,eave-1),(x1,eave-1)]+list(zip(xs[::-1],zs[::-1]))
  # Rotate local extrusion +z to -world y, local profile y to world z.
  s=CrossSection([ccw(profile)]).extrude(y1-y0).rotate((90,0,0)).translate((0,y1,0))
  add(s,n,'roof',(x0-.01,x1+.01,y0-.01,y1+.01,eave-1.01,eave+rise+.01))
 a,b,c,d=p['base_bounds_mm'];block(a,b,c,d,0,p['base_thickness_mm'],'minimal model base, not a measured site boundary','base')
 poly([(-68,-22),(68,-22),(68,183),(62,190),(-42,190),(-68,182)],2.4,6.5,'minimal integral raised support; exposed B/T lower datum is estimated','paving')
 x0,x1,y0,y1=p['main_hall_bounds_mm'];split=p['main_low_roof_y_mm'][1]
 block(x0,x1,y0,split+.1,6.4,p['low_roof_eave_z_mm'],'A-side main hall below lower curved roof')
 block(x0,x1,split-.1,y1,6.4,p['high_roof_eave_z_mm'],'B-side main hall below higher curved roof')
 roof(x0-1,x1+1,0,split,p['low_roof_eave_z_mm'],p['main_roof_rise_mm'],'A lower broad curved main roof')
 roof(x0-1,x1+1,split,155.3,p['high_roof_eave_z_mm'],p['main_roof_rise_mm'],'B higher broad curved main roof; real vertical transverse step')
 # Front U footprint leaves central entry recessed; canopy bridges its mouth.
 poly([(-64,-20),(-24,-20),(-24,-9),(24,-9),(24,-20),(64,-20),(64,2),(-64,2)],6.4,25.5,'A low flat roof annex with central entrance recess')
 for a,b in [(-64,-24),(24,64)]:
  block(a,b,-20,-18.5,25.3,27.1,'A front parapet','annex')
 block(-64,-62.5,-20,2,25.3,27.1,'A S-side parapet','annex');block(62.5,64,-20,2,25.3,27.1,'A T-side parapet','annex')
 block(-26,26,-24,-7.5,21.5,23.5,'A shallow entrance canopy, thickened model estimate','canopy')
 # Rear annex differs in footprint, roof height, projections and observed vertical corner volume.
 poly([(-66,152),(-66,180),(-42,180),(-42,189),(-17,189),(-17,185),(45,185),(45,190),(63,190),(63,152)],2.4,29.5,'B irregular flat-roof annex with rear projections and recessed middle')
 block(-66,-64.4,153,180,29.3,31,'B S parapet','annex');block(-66,-42,178.4,180,29.3,31,'B rear S parapet','annex')
 block(-42,-17,187.4,189,29.3,31,'B projecting short parapet','annex');block(-17,45,183.4,185,29.3,31,'B recessed central parapet','annex')
 block(61.4,63,153,175,29.3,31,'B T parapet','annex')
 a,b,c,d=p['secondary_bounds_mm'];block(a,b,c,d,29.4,p['secondary_roof_eave_z_mm'],'B offset narrower upper room; lateral offset estimated','wall')
 roof(a-.7,b+.7,c,d,p['secondary_roof_eave_z_mm'],p['secondary_roof_rise_mm'],'B lower narrower secondary curved roof; unequal side platforms')
 block(45,63,172.5,190,2.4,42,'source-observed B/T corner vertical volume; function unknown','annex')
 block(44.4,63.6,172,190.5,41.7,43.3,'corner volume flat cap','annex')
 # Simple step hints only; no full terrain reconstruction.
 for z,depth in [(3.8,5),(5.2,3)]:block(-25,25,-24-depth,-19,z-1.6,z,'A short entrance approach step','paving')
 # Source-observed facade groups. Counts/spacing are intentionally coarsened.
 def recess(a,b,c,d,e,f,n):
  cuts.append(box(a,b,c,d,e,f));region('glass',(a-.02,b+.02,c-.02,d+.02,e-.02,f+.02));features.append(n)
 def beam(a,b,width,n):
  # Thick model-scale cap hull; no real structural-section claim.
  caps=[Manifold.cylinder(width,width/2,circular_segments=16).translate((v[0],v[1],v[2]-width/2)) for v in [a,b]]
  q=Manifold.batch_hull(caps);aa=np.array(a);bb=np.array(b);lo=np.minimum(aa,bb)-width;hi=np.maximum(aa,bb)+width
  add(q,n,'bracket',(lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]))
 def planar_beam(a,b,thickness,ywidth,n):
  # Rectangular XZ bar with a constant full Y width; planar end intersections
  # preserve the diagonal opening without round-cap tangency necks.
  ax,ay,az=a;bx,by,bz=b;require(ay==by,'planar bar endpoints share y')
  dx=bx-ax;dz=bz-az;length=(dx*dx+dz*dz)**.5;nx=-dz/length*thickness/2;nz=dx/length*thickness/2
  pts=[(ax+nx,az+nz),(bx+nx,bz+nz),(bx-nx,bz-nz),(ax-nx,az-nz)]
  shape=CrossSection([ccw(pts)]).extrude(ywidth).rotate((90,0,0)).translate((0,ay+ywidth/2,0))
  add(shape,n,'bracket',(min(x for x,z in pts)-.01,max(x for x,z in pts)+.01,ay-ywidth/2-.01,ay+ywidth/2+.01,min(z for x,z in pts)-.01,max(z for x,z in pts)+.01))
 def latebeam(*args,**kwargs):
  beam(*args,**kwargs);late.append(parts.pop())
 def arched_window_groups(x0,x1,yface,eave,rise,count,front):
  curve=lambda x:eave+rise*(1-((x-(x0+x1)/2)/((x1-x0)/2))**2)
  for i in range(count):
   a=x0+2+(x1-x0-4)*i/count+.65;b=x0+2+(x1-x0-4)*(i+1)/count-.65
   if not front and b>44.0:continue # Existing T corner volume obscures this group; do not drill into it.
   za=curve(a)-1.1;zb=curve(b)-1.1;pts=[(a,za-3.6),(b,zb-3.6),(b,zb),(a,za)]
   ya,yb=(yface-.2,yface+1.0) if front else (yface-1.0,yface+.5)
   q=CrossSection([ccw(pts)]).extrude(yb-ya).rotate((90,0,0)).translate((0,yb,0));cuts.append(q)
   region('glass',(a-.02,b+.02,ya-.02,yb+.02,min(za,zb)-3.62,max(za,zb)+.02))
  features.append(('A wide' if front else 'B narrow')+' arched end window band; model-estimated pane count')
 arched_window_groups(-62.5,62.5,0,p['low_roof_eave_z_mm'],p['main_roof_rise_mm'],18,True)
 a,b,c,d=p['secondary_bounds_mm'];arched_window_groups(a,b,d,p['secondary_roof_eave_z_mm'],p['secondary_roof_rise_mm'],10,False)
 for a,b in [(156,160.5),(162,166.5),(168,172.5)]:recess(-18.2,-17,a,b,30.4,33.0,'observed S-facing narrow roof room window group')
 # S: directly seen sports-field face, alternating large glazed groups and horizontal groups.
 for y in [5,29,53,77,101,125,149]:
  eave=p['low_roof_eave_z_mm'] if y<82 else p['high_roof_eave_z_mm']
  block(-64,-61.9,y-1.35,y+1.35,6.3,eave-.4,'S coarse grey vertical pier','annex')
  block(-70.6,-66.8,y-1.9,y+1.9,6.3,27,'S visible maroon outer post, thick model section','bracket')
  block(-69.6,-61.9,y-1.2,y+1.2,24.8,27,'S maroon cross member','bracket')
  planar_beam((-68.7,y,26),(-62.2,y,20.5),2.2,4.4,'S visible planar diagonal bracket, model-thickened Y section')
 for ya,yb in [(8,25),(32,49),(56,73),(80,97),(104,121),(128,145)]:recess(-62.7,-61.3,ya,yb,33,37,'S upper horizontal window group')
 for ya,yb in [(8,24),(56,72),(128,144)]:
  recess(-62.7,-61.3,ya,yb,19,31.2,'S broad vertically proportioned glazing')
  for y in [ya+5.2,ya+10.4]:lateblock(-63.0,-61.1,y-.65,y+.65,18.8,31.5,'S coarse vertical window subdivision','wall')
  for z in [23,27]:lateblock(-63.0,-61.1,ya-.1,yb+.1,z-.65,z+.65,'S coarse horizontal window subdivision','wall')
 for ya,yb in [(32,48),(80,96),(104,120)]:recess(-62.7,-61.3,ya,yb,24.5,30.5,'S shorter horizontal middle windows')
 for ya,yb in [(8,24),(56,72),(104,120)]:recess(-62.7,-61.3,ya,yb,6.8,15.3,'S partly sheltered entrance glazing')
 for y in [5,29,53,77,101,125]:block(-71,-61.9,y+1.5,y+22.5,16,18,'S source-visible segmented lower canopy, model thickening','canopy')
 # T: support and upper window hints directly visible above trees. No lower mirrored windows.
 for y in [8,40,72,104,136]:
  eave=p['low_roof_eave_z_mm'] if y<82 else p['high_roof_eave_z_mm']
  block(61.9,64,y-1.35,y+1.35,6.3,eave-.4,'T partly observed vertical pier','annex')
  block(66.8,70.6,y-1.9,y+1.9,6.3,27,'T photograph-supported maroon post','bracket')
  block(61.9,69.6,y-1.2,y+1.2,24.8,27,'T photograph-supported cross member','bracket')
  planar_beam((68.7,y,26),(62.2,y,20.5),2.2,4.4,'T photograph-supported planar diagonal, model-thickened Y section')
  block(61.9,71,y-2,y+18,16,18,'T canopy hint; tree-hidden lower wall left neutral','canopy')
 for ya,yb in [(12,31),(44,63),(76,95),(108,127)]:recess(61.3,62.7,ya,yb,33,37,'T limited upper window hint from official street photograph')
 # Low A wing doors and recessed central entrance, distinct from both curved end bands.
 for a,b in [(-60,-43),(-40,-28),(29,43),(47,60)]:recess(a,b,-20.2,-19,7,20.8,'A flat-wing coarse opening panel')
 for a,b in [(-22,-8),(-6,7),(9,22)]:recess(a,b,-9.2,-8,6.8,20.7,'A central recessed entrance glazing')
 # B front platforms remain open above this low facade; no invented roof equipment.
 for y,groups in [(180,[(-62,-47)]),(189,[(-39,-20)]),(185,[(-14,7),(12,37)])]:
  for a,b in groups:
   for lo,hi in [(7,16),(19,27)]:recess(a,b,y-1,y+.2,lo,hi,'B source-observed low annex grouped windows')
 for lo,hi in [(8,17),(21,29),(33,40)]:
  recess(47.5,60.5,189,190.2,lo,hi,'existing B/T corner vertical window group; function unknown')
  recess(62,63.2,175,188,lo,hi,'existing corner T-facing glazing group')
 recess(-66.2,-65,157,177,17,27,'B annex S-facing broad window group')
 block(-72.5,-65.8,157,178,12.5,14.5,'B annex side shallow canopy, model thickening','canopy')
 for y in [159,176]:
  latebeam((-65.5,y,23),(-71.5,y,13.5),2.2,'observed B side canopy coarse brace')
  lateblock(-68.5,-64.5,y-1.2,y+1.2,20,23.4,'B short wall-side manufacturing connection pad','bracket')
 m=union([union(parts)-union(cuts),*late]).as_original().set_tolerance(p['construction_simplify_tolerance_mm']).simplify(p['construction_simplify_tolerance_mm'])
 require(str(m.status()).endswith('NoError'),'final union');return m,regions,features

def save_stl(m,path):
 q=m.to_mesh();v=np.asarray(q.vert_properties[:,:3],np.float32);faces=np.asarray(q.tri_verts,np.int64)
 data=bytearray(b'CGUST Linkou gym | original proportional representative | model mm no metric scale'.ljust(80,b'\0')[:80]+struct.pack('<I',len(faces)))
 for t in v[faces]:
  n=np.cross(t[1].astype(float)-t[0],t[2].astype(float)-t[0]);L=np.linalg.norm(n);require(L>0,'degenerate raw STL');n/=L;data+=struct.pack('<12fH',*n,*t.ravel(),0)
 path.write_bytes(data);return len(faces)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();require(not a.output_dir.exists(),'Refuse overwrite');a.output_dir.mkdir(parents=True)
 p=json.loads((R/'parameters.json').read_bytes());shutil.copy2(R/'parameters.json',a.output_dir/'parameters.json');shutil.copy2(__file__,a.output_dir/'build_model.py');m,regions,features=make_model(p);n=save_stl(m,a.output_dir/'model.stl');(a.output_dir/'color-regions.json').write_text(json.dumps(regions,indent=2)+'\n');r={'revision':p['revision'],'triangles':n,'stl_sha256':hashlib.sha256((a.output_dir/'model.stl').read_bytes()).hexdigest(),'manifold_status':str(m.status()),'components':len(m.decompose()),'volume_mm3':m.volume(),'bounds_mm':m.bounding_box(),'features':features,'scope':'Macro prototype only, no manufacturing QA or print claim'};(a.output_dir/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='features'},indent=2))
if __name__=='__main__':main()
