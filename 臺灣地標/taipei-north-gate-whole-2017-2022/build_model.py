#!/usr/bin/env python3
"""Whole Taipei North Gate, original numeric approximation. No source-pixel inputs."""
import argparse,pathlib,json,math
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,Point,box as rect
PALETTE=[
 {'id':'stone_joint','name':'Pale warm stone joints','hex':'#A29D8E','evidence':'F01-F04 pale mortar seams; uncalibrated'},
 {'id':'stone_dark','name':'Weathered dark grey stone','hex':'#66655D','evidence':'F01-F04 lower stone body and G01 vault'},
 {'id':'stone_medium','name':'Weathered mid-grey stone','hex':'#7A786B','evidence':'F01-F04 variegated stone; procedural rhythm'},
 {'id':'stone_warm','name':'Warm grey-brown stone','hex':'#776E62','evidence':'F01-F04 variegated stone; not sampled pixels'},
 {'id':'red_plaster','name':'Muted brick-red plaster','hex':'#943C30','evidence':'F01-F04 all upper faces, R01 and A01; daylight approximation'},
 {'id':'terracotta','name':'Warm terracotta tiles','hex':'#A95A32','evidence':'R01/R02/A01 orange-brown tiled envelope; uncalibrated'},
 {'id':'ridge_grey','name':'Weathered raised grey roof bands','hex':'#565951','evidence':'R01/R02/A01 connected raised ridge and separator bands'},
 {'id':'eave_light','name':'Pale narrow eave trim','hex':'#C4BEAA','evidence':'F01-F04 narrow pale eave edge'},
 {'id':'brick','name':'Exposed opening brick','hex':'#995C46','evidence':'F01/F02/F04 brick reveals around rectangular/end openings'},
 {'id':'plaque','name':'Dark plaque field','hex':'#555247','evidence':'F01/F02 plaque only on front long face'},
 {'id':'plaque_accent','name':'Subdued ochre plaque accent','hex':'#BDA269','evidence':'F01 gold-toned lettering; simplified authored border, inscription not reproduced'}]
def union(parts):
 q=[x for x in parts if not x.is_empty()];return mf.Manifold.batch_boolean(q,mf.OpType.Add)if q else mf.Manifold()
def solid(poly,z0,z1):
 if poly.is_empty:return mf.Manifold()
 if poly.geom_type=='MultiPolygon':return union([solid(x,z0,z1)for x in poly.geoms])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(x.coords)[:-1]for x in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return solid(rect(x[0],y[0],x[1],y[1]),*z)
def arch(r,spring,bottom):
 return Polygon([(-r,bottom),(r,bottom),(r,spring)]+[(r*math.cos(t),spring+r*math.sin(t))for t in np.linspace(0,np.pi,33)[1:]]+[(-r,bottom)])
def along_y(poly,lo,hi):return solid(poly,lo,hi).rotate([90,0,0]).translate([0,lo+hi,0])
def along_x(poly,lo,hi):return along_y(poly,lo,hi).rotate([0,0,-90])
def height_solid(xs,ys,fn,bottom):
 v=[];f=[];nx=len(xs);ny=len(ys)
 for y in ys:
  for x in xs:v.append([float(x),float(y),float(fn(x,y))])
 for y in ys:
  for x in xs:v.append([float(x),float(y),bottom])
 N=nx*ny
 for j in range(ny-1):
  for i in range(nx-1):
   a=j*nx+i;b=a+1;d=(j+1)*nx+i;c=d+1;f.extend([[a,b,c],[a,c,d],[N+a,N+c,N+b],[N+a,N+d,N+c]])
 ring=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(N-2,N-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
 for a,b in zip(ring,ring[1:]+ring[:1]):f.extend([[a,N+a,N+b],[a,N+b,b]])
 return mf.Manifold(mf.Mesh(np.asarray(v,np.float32),np.asarray(f,np.uint32)))
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={}
 def add(self,name,m,mat,evidence):
  if m.is_empty():return
  assert m.status()==mf.Error.NoError,(name,m.status());m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':name,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(m.bounding_box())})
 def ridge_height(self,x):
  p=self.p;return p['side_ridge_mm']+(p['middle_ridge_mm']-p['side_ridge_mm'])*math.exp(-(abs(x)/p['separator_x_mm'])**10)
 def roof_z(self,x,y,tiles=True):
  p=self.p;u=abs(y)/p['roof_half_y_mm'];v=abs(x)/p['roof_half_x_mm'];z=p['eave_mid_mm']+(self.ridge_height(x)-p['eave_mid_mm'])*(1-u)**1.65+p['eave_corner_lift_mm']*v**5*u**4
  if tiles:z+=p['tile_relief_mm']*(.5+.5*math.cos(x*2*math.pi/p['tile_rhythm_mm']))*(.3+.7*u)
  return z
 def roof_body(self):
  p=self.p;X=p['roof_half_x_mm'];Y=p['roof_half_y_mm'];G=p['gable_x_mm'];xs=np.unique(np.r_[np.linspace(-X,X,p['roof_x_segments']+1),-G,G]);ys=np.linspace(-Y,Y,p['roof_y_segments']+1)
  def lower(x,y):
   cap=164 if abs(x)<=G else p['eave_mid_mm']+16*((X-abs(x))/(X-G))**1.55+p['eave_corner_lift_mm']*(abs(y)/Y)**4
   # Hip tiles run down the end rather than sideways; no photographic texture.
   return min(self.roof_z(x,y),cap+.35*(.5+.5*math.cos(y*2*math.pi/p['tile_rhythm_mm'])))
  low=height_solid(xs,ys,lower,140)
  upper=height_solid(np.unique(np.r_[np.linspace(-G,G,115),-38,38]),ys,self.roof_z,140)
  return low+upper
 def strip(self,coords,base,top,width,axis):
  poly=Polygon([(float(u),float(base(u)))for u in coords]+[(float(u),float(top(u)))for u in coords[::-1]])
  return along_y(poly,-width/2,width/2)if axis=='x'else along_x(poly,-width/2,width/2)
 def build(self):
  p=self.p;wx=p['wall_width_mm']/2;wy=p['wall_depth_mm']/2;st=p['stone_top_mm'];passage=along_y(arch(p['arch_radius_mm'],p['arch_spring_z_mm'],-2),-wy-8,wy+8)
  lower=box((-wx,wx),(-wy,wy),(0,st))-passage
  self.add('Lower continuous stone body with true through vault',lower,0,'F01/F03/G01 through-vault, F02/F04 same solid end; P01/G04 other end; D01 rectangular ground plan only')
  # Low projecting stone plinth is part of the gate, not the plaza interpretation.
  self.add('Low perimeter stone plinth',box((-wx-1.6,wx+1.6),(-wy-1.6,wy+1.6),(0,2.7))-passage,2,'F01-F04 low perimeter stone footing; no plaza walls or attached historical city wall')
  course=p['stone_course_height_mm'];bw=p['stone_block_width_mm'];rel=p['stone_relief_mm'];idx=0
  for row,z0 in enumerate(np.arange(2.8,st-.1,course)):
   z1=min(z0+course-.30,st-.15)
   for face,sgn in [('front',-1),('reverse',1)]:
    for col,x0 in enumerate(np.arange(-wx-bw+(row%2)*bw/2,wx,bw)):
     x1=min(x0+bw-.35,wx);x0=max(x0,-wx)
     if x1<=x0:continue
     q=box((x0,x1),(-wy-rel,-wy+.25)if sgn<0 else(wy-.25,wy+rel),(z0,z1))-passage
     self.add(f'Stone {face} course {row:02d} block {col:02d}',q,1+((row*73856093)^(col*19349663)^((sgn+2)*83492791))%3,'F01/F03 masonry appearance; reduced procedural course/block rhythm, not exact stones');idx+=1
   for face,sgn in [('same end',1),('other end',-1)]:
    for col,y0 in enumerate(np.arange(-wy-bw+(row%2)*bw/2,wy,bw)):
     y1=min(y0+bw-.35,wy);y0=max(y0,-wy)
     if y1<=y0:continue
     q=box((wx-.25,wx+rel)if sgn>0 else(-wx-rel,-wx+.25),(y0,y1),(z0,z1))
     self.add(f'Stone {face} course {row:02d} block {col:02d}',q,1+((row*73856093)^(col*19349663)^((sgn+2)*83492791))%3,'F02/F04 same end, P01/G04 other end; procedural masonry not copied texture')
  # Continuous actual curved barrel lining; no door or false blockage in passage.
  barrel=along_y(arch(29.7,p['arch_spring_z_mm'],0),-wy,wy)-passage
  self.add('Dark continuous vault lining',barrel,1,'G01 actual deep stone vault; no hidden interior-room or door reconstruction')
  for side,sgn in [('front',-1),('reverse',1)]:
   for i in range(17):
    aa=i*math.pi/17+.006;bb=(i+1)*math.pi/17-.006;pts=[(r*math.cos(t),p['arch_spring_z_mm']+r*math.sin(t))for r,ts in [(27,np.linspace(aa,bb,4)),(31,np.linspace(bb,aa,4))]for t in ts]
    self.add(f'{side} arch voussoir {i:02d}',along_y(Polygon(pts),-wy-.65,-wy+.35)if sgn<0 else along_y(Polygon(pts),wy-.35,wy+.65),1+i%3,'F01/F03 radial arch surround; approximate voussoir count')
  roof=self.roof_body();inner=box((-wx+p['upper_wall_thickness_mm'],wx-p['upper_wall_thickness_mm']),(-wy+p['upper_wall_thickness_mm'],wy-p['upper_wall_thickness_mm']),(st+2,205))
  upper=(box((-wx,wx),(-wy,wy),(st-.2,205))-inner)^roof.translate([0,0,-1.3])
  # The solid roof volume begins above wall base; retain lower upper-wall ring.
  upper=upper+(box((-wx,wx),(-wy,wy),(st-.2,141))-inner)
  openings=[]
  for x in [-p['square_window_x_mm'],p['square_window_x_mm']]:openings.append(box((x-8,x+8),(-wy-3,wy+3),(105,125)))
  openings.append(along_y(Point(0,p['round_window_z_mm']).buffer(p['round_window_radius_mm'],quad_segs=24),-wy-3,wy+3))
  endpoly=arch(p['end_arch_radius_mm'],p['end_arch_spring_mm'],p['end_arch_bottom_mm']);openings.append(along_x(endpoly,-wx-3,wx+3));cut=union(openings);upper=upper-cut
  self.add('Upper red four-face envelope and actual openings',upper,4,'F01/F03 square-round-square both long faces; F02/F04 same end and P01/G04/A01 other end arched upper opening. Interior wall thickness is schematic')
  # Brick reveals and lintels sit within the cut openings, preserving the voids.
  for sgn,label in [(-1,'front'),(1,'reverse')]:
   ya=(-wy-.35,-wy+8)if sgn<0 else(wy-8,wy+.35)
   for i,x in enumerate([-56,56]):
    ring=box((x-10,x+10),ya,(103.3,126.7))-box((x-8,x+8),(-wy-4,wy+4),(105,125))
    self.add(f'{label} square reveal {i}',ring,8,'F01/F03 exposed reddish brick reveals; openings remain real through-wall voids')
    for z in [103.3,125]:self.add(f'{label} square lintel {i} {z}',box((x-10,x+10),(-wy-.6,-wy+.4)if sgn<0 else(wy-.4,wy+.6),(z,z+1.5)),2,'F01/F03 pale grey lintel and sill')
  for sgn,label in [(1,'same end'),(-1,'other end')]:
   outer=arch(10.8,113,82.6);q=along_x(outer.difference(endpoly),wx-8,wx+.35)if sgn>0 else along_x(outer.difference(endpoly),-wx-.35,-wx+8)
   self.add(label+' tall arched brick reveal',q,8,'F02/F04 SAME end; P01/G04/A01 OTHER end, tall arched upper opening; independent source attribution')
  # One continuous roof shell and actual terminal gable/hip junctions.
  shell=roof-roof.translate([0,0,-p['roof_shell_mm']]);self.add('One connected terracotta tiled roof envelope',shell,5,'R01 both real slopes and terminal hip; R02 reverse and A01 front. Single connected envelope with authored tile ribs, not separate little roofs')
  for sgn,label in [(-1,'other'),(1,'same')]:
   x=sgn*p['gable_x_mm'];plate=box((x-1.15,x+1.15),(-56,56),(161,205))^roof
   self.add(label+' upper gable and lower hip join',plate,6,'R01 near terminal upper gable/lower hip, A01/P01 complementary end; simplified visible gable face, no hidden framing')
  for label,lo,hi in [('left',-98,-38),('middle',-38,38),('right',38,98)]:
   us=np.linspace(lo,hi,25);mid=(lo+hi)/2;half=(hi-lo)/2
   self.add(label+' longitudinal raised ridge span',self.strip(us,lambda x:self.roof_z(x,0)-.4,lambda x:self.roof_z(x,0)+3.0+(17 if label=='middle' else 7)*(abs(x-mid)/half)**6,2.5,'x'),6,'R01/R02/A01 three longitudinal ridge-height spans; approximate upturns without exact ornamental carving')
  for x in [-38,38,-98,98]:
   # Along_x reverses in-plane y when rotated: profile is symmetric in y.
   us=np.linspace(-62,62,49)
   band=self.strip(us,lambda y:self.roof_z(x,y)-1,lambda y:self.roof_z(x,y)+3.0+2.2*(abs(y)/62)**10,2.5,'y').translate([x,0,0])
   self.add(('Terminal'if abs(x)>90 else'Separator')+f' descending raised band {x}',band,6,'R01 actual joined descending bands on BOTH slopes, R02 reverse/A01 front; terminate within same tiled surface, not detached roofs')
  # Terminal diagonal joins continue into the same lower hipped return.
  for sx in [-1,1]:
   for sy in [-1,1]:
    pts=[]
    for t in np.linspace(0,1,13):
     x=sx*(98+26*t);y=sy*(62+16*t);z=self.roof_z(x,y)+.45+3.5*t**9;pts.append(np.array([x,y,z]))
    rods=[]
    for aa,bb in zip(pts[:-1],pts[1:]):
     zz=bb-aa;L=np.linalg.norm(zz);zz/=L;xx=np.cross([0.,0,1],zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
     rods.append(mf.Manifold.cylinder(L+.25,.95,.95,8).transform(np.column_stack([xx,yy,zz,aa-.125*zz])))
    self.add(f'Terminal hip seam {sx} {sy}',union(rods),6,'R01 and A01 terminal side-slope to lower-hip diagonal joins and lifted eave corners; simplified visible band, not hidden geometry')
  # Pale eave trim follows the real upturned perimeter.
  for sgn in [-1,1]:
   us=np.linspace(-124,124,81);band=self.strip(us,lambda x:self.roof_z(x,sgn*78)-2.1,lambda x:self.roof_z(x,sgn*78)-.75,1.1,'x').translate([0,sgn*77.65,0]);self.add(f'Long pale eave trim {sgn}',band,7,'F01-F04 curved continuous narrow pale eave edge')
   us=np.linspace(-78,78,51);band=self.strip(us,lambda y:148+7*(abs(y)/78)**4-1.7,lambda y:148+7*(abs(y)/78)**4-.2,1.1,'y').translate([sgn*123.65,0,0]);self.add(f'End pale eave trim {sgn}',band,7,'F02/F04 and P01/G04 other end curved pale edge')
  self.add('Front plaque field only',box((-21,21),(-wy-1.1,-wy+.2),(83,99)),9,'F01/F02 plaque only on front long face, absent from F03 reverse')
  frame=rect(-22,82.3,22,99.7).difference(rect(-20.5,83.8,20.5,98.2));self.add('Front plaque border',along_y(frame,-wy-1.2,-wy-.7),2,'Simplified stone plaque surround, no copied ornament or source pixels')
  # The inscription is not reconstructed: no pseudo-characters or copied calligraphy.
  inset=rect(-18.5,85,18.5,97).difference(rect(-18.05,85.45,18.05,96.55))
  self.add('Subdued plaque inner accent border',along_y(inset,-wy-1.3,-wy-.95),10,'F01 warm plaque accents only; inscription and fine ornament intentionally not reproduced')
  return union(self.items)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build();assert s.status()==mf.Error.NoError,s.status()
 s=s.set_tolerance(.003).simplify(.003);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):mi[mm.run_index[i]//3:mm.run_index[i+1]//3]=b.ids[int(oid)]
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,5),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.004).simplify(.004)
 cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts).copy()
 # Boolean float32 output can retain a zero-area sliver after a sub-tolerance
 # corner split. Collapse ONLY its shortest edge within the declared .004 mm;
 # no hole filling, broad vertex welding or validation tolerance relaxation.
 collapsed=0
 while True:
  tri=v[f].astype(float);area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5;bad=np.where(area<1e-9)[0]
  if not len(bad):break
  i=int(bad[0]);ff=f[i];lens=[np.linalg.norm(v[ff[(j+1)%3]].astype(float)-v[ff[j]])for j in range(3)];j=int(np.argmin(lens));assert lens[j]<=.004,(i,lens)
  keep=int(ff[j]);drop=int(ff[(j+1)%3]);f[f==drop]=keep;valid=(f[:,0]!=f[:,1])&(f[:,1]!=f[:,2])&(f[:,2]!=f[:,0]);f=f[valid];mi=mi[valid];collapsed+=1;assert collapsed<30
 used=np.unique(f);mapping=np.full(len(v),-1,dtype=int);mapping[used]=np.arange(len(used));v=v[used];f=mapping[f]
 t=trimesh.Trimesh(v,f,process=False);t.export(out/(p['model_id']+'.stl'));np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(m.vert_properties)[:,:3].tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'float_canonical_tolerance_mm':.004,'zero_area_short_edge_collapses':collapsed,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
