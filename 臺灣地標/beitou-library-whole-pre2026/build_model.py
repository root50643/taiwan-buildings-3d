#!/usr/bin/env python3
"""Independent whole historical exterior geometry; no source images/network required.
Proportional desktop millimetres, not surveyed architecture or certified print data.
"""
import argparse,pathlib,json,math
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,LineString,Point,box as rect
from shapely.ops import unary_union
PALETTE=[
 {'id':'warm_timber','name':'Warm amber timber frame and soffit','hex':'#A96F3C','evidence':'A03/A04/A07; approximate visible material family, no calibrated RGB'},
 {'id':'weathered_wood','name':'Weathered dark wood decks and rails','hex':'#61584A','evidence':'A01/A04/A07 horizontal balcony and deck bands'},
 {'id':'service_masonry','name':'Grey service masonry cladding','hex':'#8F9189','evidence':'A01/A05 rectangular service mass, not mirrored timber facade'},
 {'id':'glazing','name':'Muted dark green blue glazing','hex':'#365C59','evidence':'A03/A04/A07; opaque model proxy, not real light transmission'},
 {'id':'roof_green','name':'Muted planted roof field','hex':'#7C8D54','evidence':'A01 roof and P01 RF; season-dependent planting'},
 {'id':'pv_bluegrey','name':'Blue grey photovoltaic panel field','hex':'#536278','evidence':'A01 roof photograph; separate panel and planting regions'},
 {'id':'pale_trim','name':'Pale roof edge and masonry courses','hex':'#BEBBAA','evidence':'A01/A05 pale eaves, panel grid and service courses'},
 {'id':'local_ground','name':'Immediate sloping planted ground','hex':'#8B956E','evidence':'A01/P01 section grade relation only; distant park and creek omitted'},
 {'id':'retaining_stone','name':'Low grey retaining transition','hex':'#797B70','evidence':'A01 creek-side retaining interface; no copied stone texture'},
 {'id':'roof_equipment','name':'Simplified light equipment volumes','hex':'#B5B7AD','evidence':'A01 visible inside open rooftop screen; minor apparatus generalized'}]
def union(parts):
 p=[x for x in parts if not x.is_empty()]
 return mf.Manifold.batch_boolean(p,mf.OpType.Add) if p else mf.Manifold()
def solid(poly,z0,z1):
 if poly.is_empty:return mf.Manifold()
 if poly.geom_type in ('MultiPolygon','GeometryCollection'):return union([solid(q,z0,z1)for q in poly.geoms if q.geom_type in ('Polygon','MultiPolygon')])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(q.coords)[:-1]for q in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return solid(rect(x[0],y[0],x[1],y[1]),*z)
def north(x):return (x+90)*140/180-40
ROOF=Polygon([(-96,-43),(92,104),(92,-43)])
BODY=Polygon([(-69,-33),(-62,-22),(-50,-18),(-46,-16),(84,85),(84,-33)])
TOWER=rect(-54,-43,10,-17)
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={}
 def add(self,name,m,mat=0,evidence='P01 full 1F/RF and section, A01/A03/A04/A05; proportionally bounded original-design exterior'):
  assert not m.is_empty(),name
  assert m.status()==mf.Error.NoError,(name,m.status())
  m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':name,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(m.bounding_box())})
 def h(self,xy):
  x=xy[:,0];p=self.p
  return np.interp(x,[-96,p['roof_break_x_mm'],92],[p['roof_low_mm'],p['roof_break_mm'],p['roof_high_mm']])
 def surf(self,poly,lo,hi):
  if poly.is_empty:return mf.Manifold()
  if poly.geom_type in ('MultiPolygon','GeometryCollection'):return union([self.surf(q,lo,hi)for q in poly.geoms if q.geom_type=='Polygon'])
  s=solid(poly,0,1).refine_to_length(self.p['surface_mesh_edge_mm'])
  def warp(v):
   q=np.array(v,copy=True);a=lo(q[:,:2]);b=hi(q[:,:2]);q[:,2]=a+(b-a)*q[:,2];return q
  return s.warp_batch(warp)
 def layer(self,poly,lo,hi):return self.surf(poly,lambda xy:self.h(xy)+lo,lambda xy:self.h(xy)+hi)
 def strip(self,path,w,z0,z1):return solid(LineString(path).buffer(w/2,cap_style=2,join_style=2),z0,z1)
 def roofstrip(self,path,w,lo,hi):return self.layer(LineString(path).buffer(w/2,cap_style=2,join_style=2),lo,hi)
 def beam(self,a,b,width,mat,name):
  # Axis-aligned cross-section rod with actual connected endpoints.
  a=np.array(a,float);b=np.array(b,float);v=b-a;l=np.linalg.norm(v);m=mf.Manifold.cylinder(l,width/2,width/2,6)
  z=v/l;up=np.array([0,0,1.])
  x=np.cross(up,z)
  if np.linalg.norm(x)<.01:x=np.array([1.,0,0])
  x/=np.linalg.norm(x);y=np.cross(z,x);tr=np.column_stack([x,y,z,a]);self.add(name,m.transform(tr),mat)
 def build(self):
  p=self.p;r=p['rail_member_mm'];land=ROOF.buffer(11,join_style=2)
  self.add('Thin local ground closure',solid(land,-p['base_thickness_mm'],0.4),8,'Authored local closure only, not an architectural podium')
  self.add('Low creek-side immediate ground',solid(land.buffer(-.7),.2,1.0),7)
  # Higher park terrace south of the body. North-side basement remains exposed.
  park=land.intersection(rect(-110,-65,105,-33.15))
  self.add('Higher park-side grade',solid(park,.7,p['park_grade_mm']),7,'P01 long section and A01: two above ground floors, creek-side exposed basement')
  self.add('Park-side narrow paving',solid(park.intersection(rect(-75,-46,100,-33.1)),16.8,17.3),6)
  self.add('Park retaining edge',solid(park.boundary.buffer(.65).intersection(land),.6,17.3),8)
  east_grade=land.intersection(rect(83.8,-54,104,63))
  self.add('East park to creek descending grade',self.surf(east_grade,lambda xy:np.full(len(xy),.5),lambda xy:np.where(xy[:,1]<43,17.0,17.0-(xy[:,1]-43)*.79)),7,'P01 section and A03 high park-side ground, A01 creek exposure; simplified terrain transition')
  # Building enclosure retained as a solid printable exterior; balconies are separate real recesses.
  self.add('Whole wedge enclosed library body',self.surf(BODY.difference(rect(-72,-40,-46,20)),lambda xy:np.full(len(xy),.7),lambda xy:self.h(xy)-1.0),3)
  # Three creek-visible floor levels and actual terrace returns at high end.
  outer=Polygon([(-54,north(-54)-10.5),(-54,north(-54)-2.6),(84,north(84)-2.6),(91,91),(91,62),(83.4,62),(83.4,north(83.4)-10.5)])
  terrace=outer.buffer(.01).difference(BODY.buffer(-.35))
  self.terrace=terrace
  for k,z in enumerate(p['floor_levels_mm']):
   usable=terrace.intersection(rect(-54 if k<2 else -40,-70,100,110))
   self.add('Level %d projecting balcony deck'%k,solid(usable,z-.65,z+.45),1)
   # Front beam remains behind the rail and overlaps each deck.
   a=(-50 if k<2 else -37);end=84
   path=[(a,north(a)-3.0),(end,north(end)-3.0),(89,87),(89,65)]
   self.add('Level %d outer balcony fascia'%k,self.strip(path,1.2,z-.8,z+.5),1)
   if k>0:
    for h in [-2.7,-1.6,-.5]:self.add('Level %d lower slatted fascia %.1f'%(k,h),self.strip(path,1.0,z+h,z+h+.65),1)
   for h in [1.5,2.9,4.3]:self.add('Level %d railing horizontal %.1f'%(k,h),self.strip(path,r,z+h,z+h+r),1)
   L=LineString(path)
   for j,d in enumerate(np.arange(0,L.length+1,10)):
    pt=L.interpolate(min(d,L.length));self.add('Level %d rail post %02d'%(k,j),solid(pt.buffer(r*.6,resolution=2),z-(3.0 if k>0 else .3),z+5.1),6)
  # Timber frame along diagonal glazing line. Broad supports with secondary window mullions.
  for i,x in enumerate(np.arange(-49,84,12)):
   y=north(x)-10.2;top=float(self.h(np.array([[x,y]]))[0])-1.0
   self.add('Creek facade timber post %02d'%i,solid(Point(x,y).buffer(1.0,resolution=2),.6,top+.2),0)
   for z in [17.4,33.4]:self.add('Timber post beam tie %02d %.1f'%(i,z),self.strip([(x,y),(x,y+7.1)],1.4,z-.5,z+.6),0)
  glassline=[(-50,north(-50)-9.9),(83,north(83)-9.9)]
  for i,z in enumerate([5.0,13.6,21.0,29.7,37.0,45.0]):
   part=self.strip(glassline,.75,z,z+.8)^self.layer(BODY.buffer(.1),-70,-.7)
   if not part.is_empty():self.add('Creek window horizontal frame %02d'%i,part,0)
  for i,x in enumerate(np.arange(-42,83,6)):
   y=north(x)-10.25;top=float(self.h(np.array([[x,y]]))[0])-1.2
   self.add('Creek secondary mullion %02d'%i,self.strip([(x,y-1),(x+.1,y+.6)],.55,1.0,top),0)
  # Separate upper balcony canopy: band visible beneath main high roof, not a fourth floor.
  canopy=terrace.buffer(1.25).intersection(rect(2,-60,92,107))
  self.add('Upper terrace independent deep canopy',solid(canopy,47.0,48.1),1)
  for x in np.arange(6,82,12):
   y=north(x)-4;hi=float(self.h(np.array([[x,y]]))[0])-.3
   self.add('Upper canopy support %.0f'%x,solid(Point(x,y).buffer(.85,resolution=2),33.5,max(48.0,hi)),0)
  # High eastern glazing and a distinct opaque board portion, with actual broad roof overhang.
  for i,y in enumerate(np.arange(-29,89,12)):
   self.add('East tall timber frame %02d'%i,box((83.45,85.0),(y-.65,y+.65),(17.0,60.1)),0)
  for z in [17.4,25.2,33.4,43.7,53.5]:self.add('East glass transom %.1f'%z,box((83.5,85.05),(-32,90),(z-.45,z+.45)),0)
  self.add('East opaque board side portion',box((83.5,85.2),(-31.8,-8.0),(17.0,42.0)),0)
  for z in np.arange(18,41,1.8):self.add('East board joint %.1f'%z,box((85.1,85.32),(-31.8,-8),(z,z+.35)),1)
  # South park face transitions from service masonry to distinct timber/glazing.
  self.add('South timber opaque lower spandrel',box((10,83.7),(-34.1,-32.7),(31.0,35.5)),0)
  for i,x in enumerate(np.arange(15,84,10)):
   self.add('South facade timber frame %02d'%i,box((x-.7,x+.7),(-34.1,-32.5),(16.7,float(self.h(np.array([[x,-33]]))[0])-.5)),0)
  self.add('South intermediate projecting shade',box((8,85),(-38,-31.8),(32.8,34.1)),1)
  for i,x in enumerate(np.arange(10,86,3)):
   self.add('South shade trellis end %02d'%i,box((x-.35,x+.35),(-40,-32.5),(33.2,33.9)),0)
  # Low west opaque service end follows lower bent roof.
  west=BODY.intersection(rect(-72,-40,-46,20))
  self.add('Low west opaque end body',self.surf(west,lambda xy:np.full(len(xy),.7),lambda xy:self.h(xy)-.5),0)
  for i,x in enumerate([-61,-52]):
   self.add('Low west small window %02d'%i,box((x-1.3,x+1.3),(-33.35,-32.75),(22.0,26.2)),3)
  # Main roof is bent along its length; slope not a generic triangle plane.
  roof_without_tower=ROOF.difference(TOWER.buffer(-.25))
  self.add('Whole nonuniform bent roof shell',self.layer(roof_without_tower,-p['roof_shell_mm'],0),0)
  rim=ROOF.difference(ROOF.buffer(-.8));self.add('Pale continuous roof eave edge',self.layer(rim,-1.1,.35),6)
  # PV band follows the long creek edge; green field is a separate southern triangle.
  pv=Polygon([(-28,north(-28)-4),(85,north(85)-4),(85,north(85)-25),(-28,north(-28)-25)]).intersection(ROOF.buffer(-1))
  green=Polygon([(14,-34),(85,-34),(85,north(85)-33),(14,north(14)-33)])
  self.add('Separate triangular planted roof',self.layer(green,-.1,.55),4)
  self.add('Long photovoltaic panel field',self.layer(pv,-.1,.55),5)
  grid=[]
  for x in np.arange(-26,87,7):grid.append(LineString([(x,north(x)-27),(x,north(x)-2)]).buffer(.18,cap_style=2))
  for d in [4,11,18,25]:grid.append(LineString([(-30,north(-30)-d),(86,north(86)-d)]).buffer(.18,cap_style=2))
  self.add('Reduced real PV panel frame grid',self.layer(unary_union(grid).intersection(pv.buffer(-.6)),.20,.77),6)
  walkpath=[(8,-15),(8,north(8)-29),(85,north(85)-29)]
  walkway=LineString(walkpath).buffer(1.8,join_style=2,cap_style=2)
  self.add('Roof access walk dividing PV and planting',self.layer(walkway,-.1,.65),1)
  # Roof slat areas are geometry in source-visible unplanted parts, not extracted texture.
  bare=ROOF.buffer(-1.4).difference(pv.buffer(.7)).difference(green.buffer(.7)).difference(TOWER.buffer(1)).difference(walkway.buffer(1.0)).buffer(-.45)
  ribs=[]
  for y in np.arange(-42,101,2.4):ribs.append(LineString([(-100,y),(94,y)]).buffer(.22,cap_style=2))
  self.add('Reduced roof deck slat rhythm',self.layer(unary_union(ribs).intersection(bare),-.35,.30),1)
  # Roof walk rails have open gaps, plus perimeter green-field edge rail.
  railpaths=[[(12,north(12)-26.5),(85,north(85)-26.5)],[(12,north(12)-31.5),(85,north(85)-31.5)],[(14,-34),(85,-34),(85,north(85)-33)]]
  for k,path in enumerate(railpaths):
   for h in [2.0,4.2]:self.add('Roof rail %d horizontal %.1f'%(k,h),self.roofstrip(path,r,h,h+r),1)
   L=LineString(path)
   for j,d in enumerate(np.arange(0,L.length+.1,9)):
    q=L.interpolate(min(d,L.length));h=float(self.h(np.array([[q.x,q.y]]))[0]);self.add('Roof rail %d post %02d'%(k,j),solid(q.buffer(r*.6,resolution=2),h-.3,h+5.0),1)
  # Single observed small skylight in green field, not multiple guessed plan symbols.
  sky=rect(49,-5,56,2);self.add('Single observed small skylight frame',self.layer(sky,-.1,1.5),6);self.add('Single skylight dark inset',self.layer(sky.buffer(-.65),1.3,1.65),3)
  # Service tower lower mass and OPEN rooftop equipment enclosure, not an added solid storey.
  self.add('Attached service tower masonry body',solid(TOWER,.7,50.3),2)
  for z in np.arange(4,50,5.2):
   rim=TOWER.buffer(.18).difference(TOWER.buffer(-.3));self.add('Service tower pale course %.1f'%z,solid(rim,z,z+.40),6)
  for i,x in enumerate([-43,-20,1]):
   for z in [23,38]:self.add('South service small opening %d %d'%(i,z),box((x-2,x+2),(-43.28,-42.75),(z,z+4.5)),3)
  self.add('Open screen equipment floor',solid(TOWER.buffer(-.4),50.0,50.7),6)
  for z in np.arange(51.2,62,1.5):
   rim=TOWER.difference(TOWER.buffer(-.75));self.add('Open tower perimeter slat %.1f'%z,solid(rim,z,z+.68),1)
  for i,(x,y)in enumerate([(-53.5,-42.5),(-53.5,-17.5),(9.5,-42.5),(9.5,-17.5),(-22,-42.5),(-22,-17.5)]):
   self.add('Tower open screen post %d'%i,box((x-.55,x+.55),(y-.55,y+.55),(49.7,62.2)),1)
  for i,x in enumerate([-44,-22,-1]):self.add('Simplified visible roof equipment %d'%i,box((x-5,x+5),(-36,-24),(50.4,53.7)),9)
  # Attached eastern exterior stairs connect exposed lower terrace to upper grade.
  for k in range(14):
   y=64+k*1.5;z=1.4+(k+1)*16/14
   self.add('East exterior stair tread %02d'%k,box((85.0,92.0),(y,y+1.65),(0.8,z)),1)
  # Every stair rail is supported at both ends, not floating ornaments.
  self.beam([92,64,5.5],[92,85,21.5],.8,1,'East exterior stair inclined handrail')
  for j,t in enumerate([0,.25,.5,.75,1]):
   y=64+21*t;z=1.4+16*t;self.add('East stair handrail post %d'%j,box((91.65,92.35),(y-.35,y+.35),(z-.2,z+4.7)),1)
  # Low contextual creek retaining line stays narrow and follows whole frontage.
  wallpath=[(-72,-24),(-55,-8),(88,104),(99,99)]
  self.add('Creek-side defining retaining strip',self.strip(wallpath,1.5,.1,3.2),8)
  return union(self.items)

def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build();assert s.status()==mf.Error.NoError,s.status()
 s=s.set_tolerance(.003).simplify(.003);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):mi[mm.run_index[i]//3:mm.run_index[i+1]//3]=b.ids[int(oid)]
 # Canonical float32 STL representation is checked, not just the higher precision construction.
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,5),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.004).simplify(.004)
 parts=canonical.decompose();filled=len([q for q in parts if q.volume()<=0]);canonical=union([q for q in parts if q.volume()>0]);cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts)
 v[:,1]*=p['plan_cross_axis_proportion']
 for op in b.ops:
  op['bounds_model_mm'][1]*=p['plan_cross_axis_proportion'];op['bounds_model_mm'][4]*=p['plan_cross_axis_proportion']
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'beitou-library-whole-pre2026.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  m=item.scale([1.0,p['plan_cross_axis_proportion'],1.0]).to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(m.vert_properties)[:,:3].tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'non_visible_closed_cavities_filled_for_exterior_print':filled,'float_canonical_tolerance_mm':.004,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
