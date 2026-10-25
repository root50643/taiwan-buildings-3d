#!/usr/bin/env python3
"""Authored approximate whole Daxi Butokuden exterior, 2014 survey state.
Public-input-only construction: no image texture, copied linework, network or private path.
Published inner-face and RF dimension anchors are interpreted at approximate 1:100.
"""
import argparse,pathlib,json,math
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,LineString,Point,box as rect
from shapely.ops import unary_union
PALETTE=[
 {'id':'washed_stone','name':'Warm pale washed-stone walls and columns','hex':'#C2BFB2','evidence':'P01 pp3–4 report-era exterior photos; masonry/RC imitation timber profiles, not dark wood walls'},
 {'id':'base_stone','name':'Weathered grey foundation and steps','hex':'#999A90','evidence':'P01 p3 raised base and steps; approximate surface colour'},
 {'id':'roof_slate','name':'Muted grey-brown small roofing units','hex':'#6F716B','evidence':'P01 pp3–4; simplified authored roof courses, no image texture'},
 {'id':'copper_patina','name':'Subdued blue-green patinated copper ridge','hex':'#72948C','evidence':'P01 p4 copper-clad ridge, hips and chiwen detail'},
 {'id':'dark_timber','name':'Dark grey-brown doors and window frames','hex':'#51483C','evidence':'P01 pp3–4; solid approximate colour'},
 {'id':'glazing','name':'Muted dark glazing proxy','hex':'#3E504C','evidence':'P01 pp3–4; opaque display proxy, no copied photo or true transmission'},
 {'id':'gable_shadow','name':'Dark gable louvers and under-eave timber','hex':'#424139','evidence':'P01 pp3–4; distinct from pale washed-stone exterior walls'},
 {'id':'fine_trim','name':'Pale projecting trim and railing','hex':'#D2CEBF','evidence':'P01 p3 washed-stone ornamental rails and window surrounds'}]
def union(parts):
 p=[x for x in parts if not x.is_empty()]
 return mf.Manifold.batch_boolean(p,mf.OpType.Add) if p else mf.Manifold()
def solid(poly,z0,z1):
 if poly.is_empty:return mf.Manifold()
 if poly.geom_type in ('MultiPolygon','GeometryCollection'):return union([solid(q,z0,z1)for q in poly.geoms if q.geom_type in ('Polygon','MultiPolygon')])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(q.coords)[:-1]for q in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return solid(rect(x[0],y[0],x[1],y[1]),*z)
def oriented(poly,axis,depth0,depth1):
 m=solid(poly,depth0,depth1)
 # Polygon coordinates are horizontal facade position and vertical z.
 return m.transform(np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0]])) if axis=='y' else m.transform(np.array([[0,0,1,0],[1,0,0,0],[0,1,0,0]]))
def loft_rectangles(rings):
 # Each ring is x_min, y_min, x_max, y_max, z. Explicit planar quad bands.
 vertices=[]
 for x0,y0,x1,y1,z in rings:vertices.extend([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)])
 faces=[[0,2,1],[0,3,2]]
 for k in range(len(rings)-1):
  for i in range(4):
   a=4*k+i;b=4*k+(i+1)%4;c=4*(k+1)+(i+1)%4;d=4*(k+1)+i;faces.extend([[a,b,c],[a,c,d]])
 z=4*(len(rings)-1);faces.extend([[z,z+1,z+2],[z,z+2,z+3]])
 return mf.Manifold(mf.Mesh(np.asarray(vertices,np.float32),np.asarray(faces,np.uint32)))
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.wx=p['inner_wall_face_span_mm'][0]/2+p['wall_thickness_mm'];self.wy=p['inner_wall_face_span_mm'][1]/2+p['wall_thickness_mm'];self.rx=p['main_roof_span_mm'][0]/2;self.ry=p['main_roof_span_mm'][1]/2
 def add(self,name,m,mat=0,evidence='P03 A03/A08–A11, P01 p3; original approximate exterior component'):
  assert not m.is_empty(),name
  assert m.status()==mf.Error.NoError,(name,m.status())
  m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':name,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(m.bounding_box())})
 def surf(self,poly,lo,hi,edge=None):
  if poly.is_empty:return mf.Manifold()
  if poly.geom_type in ('MultiPolygon','GeometryCollection'):return union([self.surf(q,lo,hi,edge)for q in poly.geoms if q.geom_type=='Polygon'])
  s=solid(poly,0,1).refine_to_length(edge or self.p['surface_mesh_edge_mm'])
  def warp(v):
   q=np.array(v,copy=True);a=lo(q[:,:2]);b=hi(q[:,:2]);q[:,2]=a+(b-a)*q[:,2];return q
  return s.warp_batch(warp)
 def strip(self,path,w,z0,z1):return solid(LineString(path).buffer(w/2,cap_style=2,join_style=2),z0,z1)
 def beam(self,a,b,width,mat,name):
  a=np.array(a,float);b=np.array(b,float);v=b-a;l=np.linalg.norm(v);m=mf.Manifold.cylinder(l,width/2,width/2,6);zz=v/l;xx=np.cross([0,0,1.],zz)
  if np.linalg.norm(xx)<.01:xx=np.array([1.,0,0])
  xx/=np.linalg.norm(xx);yy=np.cross(zz,xx);self.add(name,m.transform(np.column_stack([xx,yy,zz,a])),mat)
 def h(self,xy):
  # Lower hipped skirt turns into upper gable planes at |x| = 77.8.
  y=np.abs(xy[:,1]);x=np.abs(xy[:,0]);gx=self.p['main_gable_half_length_mm'];gy=self.p['roof_break_half_depth_mm'];gz=self.p['roof_break_height_mm']
  skirt=np.minimum((self.rx-x)/(self.rx-gx),(self.ry-y)/(self.ry-gy));t=np.clip(skirt,0,1)
  lower=self.p['roof_eave_datum_mm']+1.15+(gz-self.p['roof_eave_datum_mm']-1.15)*(0.72*t+0.28*t*t)
  tupper=np.clip(1-y/gy,0,1);upper=gz+(self.p['main_ridge_datum_mm']-1.45-gz)*(0.91*tupper+0.09*tupper*tupper)
  return np.where((x<=gx+.0001)&(y<=gy),upper,lower)
 def lowerh(self,xy):
  gx=self.p['main_gable_half_length_mm'];gy=self.p['roof_break_half_depth_mm'];gz=self.p['roof_break_height_mm'];t=np.clip(np.minimum((self.rx-np.abs(xy[:,0]))/(self.rx-gx),(self.ry-np.abs(xy[:,1]))/(self.ry-gy)),0,1)
  return self.p['roof_eave_datum_mm']+1.15+(gz-self.p['roof_eave_datum_mm']-1.15)*(.72*t+.28*t*t)
 def rooflayer(self,poly,lo,hi):return self.surf(poly,lambda xy:self.h(xy)+lo,lambda xy:self.h(xy)+hi)
 def facade_box(self,name,axis,sign,center,width,z0,z1,out0,out1,mat=0,evidence='P03 A08–A11 and A16–A19; P01 p3'):
  d=(self.wy if axis=='y' else self.wx);aa,bb=sorted([sign*(d+out0),sign*(d+out1)])
  self.add(name,oriented(rect(center-width/2,z0,center+width/2,z1),axis,aa,bb),mat,evidence)
 def facade_rod(self,name,axis,sign,a,b,width,mat=4,out=.65):
  d=sign*((self.wy if axis=='y' else self.wx)+out)
  aa=[a[0],d,a[1]]if axis=='y'else[d,a[0],a[1]];bb=[b[0],d,b[1]]if axis=='y'else[d,b[0],b[1]]
  self.beam(aa,bb,width,mat,name)
 def diamonds(self,prefix,axis,sign,c,w,z0,z1,n):
  # Solid dark panel behind a raised pale/dark diamond transom lattice.
  self.facade_box(prefix+' transom glazing',axis,sign,c,w,z0,z1,-.25,.4,5)
  for z in [z0,z1]:self.facade_box(prefix+' transom horizontal %.1f'%z,axis,sign,c,w+.5,z-.26,z+.26,.2,1.0,4)
  for x in [c-w/2,c+w/2]:self.facade_box(prefix+' transom jamb %.1f'%x,axis,sign,x,.55,z0,z1,.2,1.0,4)
  pitch=w/n
  for i in range(n):
   x=c-w/2+(i+.5)*pitch;points=[(x-pitch/2,(z0+z1)/2),(x,z1),(x+pitch/2,(z0+z1)/2),(x,z0)]
   for j in range(4):self.facade_rod(prefix+' diamond %d %d'%(i,j),axis,sign,points[j],points[(j+1)%4],.42,7,.82)
 def window(self,prefix,axis,sign,c,w,sill):
  mainh=14.3;translo=sill+16.6;transhi=sill+22.7
  # Frame and muted opaque inset sit in a bounded facade recess proxy.
  self.facade_box(prefix+' pale surround',axis,sign,c,w+2.0,sill-.8,transhi+.8,-.2,.5,7)
  self.facade_box(prefix+' lower glazing',axis,sign,c,w,sill,sill+mainh,.15,.67,5)
  for z in [sill,sill+mainh]:self.facade_box(prefix+' sash horizontal %.1f'%z,axis,sign,c,w+.5,z-.35,z+.35,.45,1.04,4)
  for i in range(5):self.facade_box(prefix+' mullion %d'%i,axis,sign,c-w/2+i*w/4,.45 if i%2 else .65,sill,sill+mainh,.5,1.04,4)
  for i,t in enumerate([.16,.32,.72,.88]):self.facade_box(prefix+' glazing horizontal %d'%i,axis,sign,c,w,sill+mainh*t-.18,sill+mainh*t+.18,.58,1.04,4)
  self.diamonds(prefix,axis,sign,c,w,translo,transhi,4)
 def door(self,prefix,axis,sign,c,front=False):
  bottom=8.4;w=18.9;top=bottom+19.5
  self.facade_box(prefix+' pale surround',axis,sign,c,w+2.4,bottom-.4,top+6.8,-.2,.45,7)
  self.facade_box(prefix+' double leaf',axis,sign,c,w,bottom,top,.15,.7,4)
  for x in [c-w/2,c,c+w/2]:self.facade_box(prefix+' upright %.1f'%x,axis,sign,x,.65,bottom,top,.45,1.05,4)
  for signleaf in [-1,1]:
   lc=c+signleaf*w/4
   self.facade_box(prefix+' upper panel %d'%signleaf,axis,sign,lc,w/2-1.3,top-4.7,top-1.0,.65,1.05,4)
   for row in range(5):
    for col in range(3):
     pc=lc+(col-1)*2.4;z=bottom+1.4+row*2.5
     self.facade_box(prefix+' raised panel %d %d %d'%(signleaf,row,col),axis,sign,pc,1.7,z,z+1.7,.65,1.15,4)
  self.diamonds(prefix,axis,sign,c,w,top+.8,top+(4.6 if front else 5.87),4)
 def rail(self,prefix,path,z0,height=6.0,spacing=8.0,mat=7):
  w=self.p['rail_member_mm'];L=LineString(path)
  for k,z in enumerate([z0+1.8,z0+4.2,z0+height]):self.add(prefix+' horizontal %d'%k,self.strip(path,w,z-w/2,z+w/2),mat)
  # Endpoint and mid-post count are deliberately reduced, not exact miniature joinery.
  n=max(1,int(math.ceil(L.length/spacing)))
  for j,t in enumerate(np.linspace(0,1,n+1)):
   q=L.interpolate(t,normalized=True);self.add(prefix+' post %02d'%j,solid(q.buffer(.62,resolution=3),z0-.35,z0+height+.6),mat)
   self.add(prefix+' post cap %02d'%j,solid(q.buffer(.85,resolution=3),z0+height+.2,z0+height+.85),mat)
 def build(self):
  p=self.p;wx=self.wx;wy=self.wy;floor=p['floor_datum_mm'];body=rect(-wx,-wy,wx,wy);projection=rect(-19.8,wy-.3,19.8,wy+9.4);foot=body.union(projection)
  # Closed exterior display proxy; interior and inaccessible foundation are not reconstructed.
  self.add('Raised tapered main masonry base',self.surf(foot.buffer(.85,join_style=2),lambda xy:np.zeros(len(xy)),lambda xy:np.full(len(xy),floor-.1),5),1,'P03 A03/A08–A11: raised main hall; solid display enclosure, no hidden foundation claim')
  self.add('Whole main hall exterior enclosure',solid(body,7.8,43.85),0,'A03 inner-face 1780×1055 plus graphically bounded 42 cm wall thickness; no interior reconstruction')
  self.add('Blank shallow rear altar projection',solid(projection,7.8,43.85),0,'P03 A03/A09/A14; central shallow rear projection is blank, not an entry')
  for z,w,h in [(2.4,.45,.40),(5.1,.35,.40),(8.1,1.0,.9),(16.5,.75,1.1),(41.1,1.2,1.8)]:
   band=foot.buffer(w,join_style=2).difference(foot.buffer(-.3,join_style=2))
   if z==16.5:
    band=band.difference(rect(-10.8,-wy-2,10.8,-wy+2))
    for sign in [-1,1]:band=band.difference(rect(sign*wx-2,-10.8,sign*wx+2,10.8))
   self.add('Pale plinth or wall band %.1f'%z,solid(band,z,z+h),7 if z>=8 else 1)
  # Window bays from A03 extension-line anchors; not evenly redistributed generic bays.
  longcenters=[-63.75,-45.05,45.05,63.75]
  for sign,label in [(-1,'Front'),(1,'Rear')]:
   for i,c in enumerate(longcenters):self.window(label+' window %d'%i,'y',sign,c,14.3,17.153)
   # Courses terminate at actual window and center openings/projection, instead of crossing glass.
   gaps=[(-73.5,-35.8),(35.8,73.5)]+([(-11,11)]if sign<0 else [(-20,20)])
   for j,z in enumerate(np.arange(19.0,40.5,3.1)):
    face=LineString([(-wx,sign*(wy+.1)),(wx,sign*(wy+.1))]).buffer(.12,cap_style=2)
    for a,b in gaps:face=face.difference(rect(a,-wy-2,b,wy+2))
    self.add(label+' wall horizontal joint %d'%j,solid(face,z,z+.23),1)
   for c in [-wx+.9,-73.1,-54.4,-35.7,35.7,54.4,73.1,wx-.9]:
    if abs(c)<60 and abs(c)>40:continue
    self.facade_box(label+' pale pilaster %.1f'%c,'y',sign,c,2.35,8.0,42.0,-.1,.95,0)
  for j,z in enumerate(np.arange(19,40.6,3.1)):
   self.add('Rear projection course %d'%j,box((-19.8,19.8),(wy+9.35,wy+9.6),(z,z+.23)),1)
  self.door('Front entry','y',-1,0,True)
  for sign,label in [(-1,'Left'),(1,'Right')]:
   for i,c in enumerate([-27.05,27.05]):self.window(label+' side window %d'%i,'x',sign,c,17.3,16.4)
   self.door(label+' side door','x',sign,0)
   for c in [-wy+1,-37.7,-12.7,12.7,37.7,wy-1]:self.facade_box(label+' pale pilaster %.1f'%c,'x',sign,c,2.3,8.0,42.0,-.1,1.0,0)
   for j,z in enumerate(np.arange(19,40.6,3.1)):
    for k,(a,b)in enumerate([(-wy,-37),(37,wy)]):self.facade_box(label+' side wall joint %d %d'%(j,k),'x',sign,(a+b)/2,b-a,z,z+.23,0,.23,1)
  # Discrete shallow window ledges and rail groups: no continuous veranda.
  for sign,label in [(-1,'Front'),(1,'Rear')]:
   for side in [-1,1]:
    a,b=(-73.5,-35.8)if side<0 else(35.8,73.5);y0,y1=sorted([sign*(wy-.25),sign*(wy+4.6)])
    self.add(label+' window ledge %d'%side,box((a-.8,b+.8),(y0,y1),(15.3,16.2)),7)
    path=[(a,sign*(wy-.1)),(a,sign*(wy+4.05)),(b,sign*(wy+4.05)),(b,sign*(wy-.1))]
    self.rail(label+' window rail %d'%side,path,15.9,5.5,9)
    for k,x in enumerate([a+1,(a+b)/2,b-1]):self.add(label+' ledge bracket %d %d'%(side,k),box((x-.6,x+.6),(y0,y1),(14.45,15.7)),1)
  # Separate side-door decks with open supported undercrofts, not wraparound slabs.
  for sign,label in [(-1,'Left'),(1,'Right')]:
   x0,x1=sorted([sign*(wx-.2),sign*(wx+17.2)])
   self.add(label+' discrete door deck',box((x0,x1),(-37.0,37.0),(6.2,7.5)),1)
   self.add(label+' door deck pale edge',box((x0,x1),(-37.5,37.5),(7.1,7.9)),7)
   for k,y in enumerate([-35,35]):self.add(label+' deck outside support %d'%k,box(tuple(sorted([sign*(wx+14.7),sign*(wx+17.0)])),(y-1.05,y+1.05),(0,7.3)),1)
   # Rail is open at the central doorway on both sides; right has the outer stair.
   for side in [-1,1]:
    ya,yb=(-36.5,-14)if side<0 else(14,36.5)
    path=[(sign*(wx-.1),ya),(sign*(wx+16.1),ya),(sign*(wx+16.1),yb)]if side<0 else[(sign*(wx+16.1),ya),(sign*(wx+16.1),yb),(sign*(wx-.1),yb)]
    self.rail(label+' deck rail %d'%side,path,7.5,8.8,9)
   for y in [-14,14]:
    self.add(label+' central rail terminal %.0f'%y,solid(Point(sign*(wx+16.1),y).buffer(.95,resolution=4),7.2,20.5),7)
   self.add(label+' side doorway threshold',box(tuple(sorted([sign*(wx-.4),sign*(wx+2.0)])),(-10.5,10.5),(7.3,8.5)),7)
  for k in range(4):
   x=wx+17.0+(3-k)*2.4;self.add('Right-only outer stair tread %d'%k,box((x,x+2.45),(-14,14),(0,(k+1)*1.85)),1,'P03 A03/A09/A12; no mirrored free left staircase')
  # Front porch platform and independent short entry flight, attached to hall steps.
  self.add('Front porch low platform',box((-32.5,32.5),(-96.5,-wy+.2),(0,4.3)),1)
  self.add('Front porch thin pale floor edge',box((-33,33),(-97,-wy+.3),(3.7,4.5)),7)
  for k in range(3):
   y=-104.2+k*2.55;self.add('Front central approach step %d'%k,box((-14.4,14.4),(y,-96.4),(0,1.45*(k+1))),1)
  for sign in [-1,1]:self.add('Front step cheek %d'%sign,box(tuple(sorted([sign*14.6,sign*16.2])),(-104.2,-96.0),(0,4.9)),7)
  for k in range(3):self.add('Covered entry inner step %d'%k,box((-19.5,19.5),(-64.5+k*2.55,-wy+.3),(4.2,4.3+(k+1)*1.38)),1)
  for sign in [-1,1]:
   x=sign*18.2;self.add('Porch washed-stone column %d'%sign,box((x-1.05,x+1.05),(-84.15,-82.05),(4.25,34.3)),0)
   self.add('Porch column stone foot %d'%sign,box((x-1.5,x+1.5),(-84.6,-81.6),(4.0,5.5)),7)
   self.add('Porch column capital %d'%sign,box((x-1.55,x+1.55),(-84.65,-81.55),(32.5,35.6)),7)
   self.add('Porch depth structural beam %d'%sign,box((x-.9,x+.9),(-84.1,-wy+.3),(32.9,35.5)),6)
  self.add('Porch front pale crossbeam',box((-19.6,19.6),(-84.2,-82.1),(29.3,31.1)),0)
  # Entire main roof, explicit lower hips and upper curved gable slopes.
  gx=p['main_gable_half_length_mm'];gy=p['roof_break_half_depth_mm'];roof=rect(-self.rx,-self.ry,self.rx,self.ry)
  rings=[(-self.rx,-self.ry,self.rx,self.ry,43.25)]
  for t in np.linspace(0,1,17):
   xx=self.rx+(gx-self.rx)*t;yy=self.ry+(gy-self.ry)*t;zz=45.05+(p['roof_break_height_mm']-45.05)*(.72*t+.28*t*t)
   rings.append((-xx,-yy,xx,yy,zz))
  self.add('Main curved lower hipped roof',loft_rectangles(rings),2,'P03 A07–A11/A14; explicit rectangular loft rings follow the curved four-slope skirt, with no warped triangle fan')
  ys=sorted(set(list(np.linspace(-gy,gy,89))+[-gy,0,gy]));heights=self.h(np.c_[np.zeros(len(ys)),ys])
  upper=Polygon([(-gy,60.9),(gy,60.9)]+list(zip(ys[::-1],heights[::-1])))
  self.add('Main upper curved gable roof',oriented(upper,'x',-gx,gx),2,'P03 A07–A11/A14; explicit swept curved profile, vertical gable ends and full ridge length')
  # Dark under-eave fascia and regular exposed rafter tips, all attached to roof.
  self.add('Main continuous thin dark eave fascia',solid(roof.buffer(.15,join_style=2).difference(roof.buffer(-1.0)),42.9,44.7),6)
  for sign in [-1,1]:
   for j,x in enumerate(np.arange(-89,90,6.1)):self.add('Long eave rafter %d %02d'%(sign,j),box((x-.35,x+.35),tuple(sorted([sign*(wy-.4),sign*(self.ry-.6)])),(42.7,43.8)),6)
   for j,y in enumerate(np.arange(-50,51,6.1)):self.add('Side eave rafter %d %02d'%(sign,j),box(tuple(sorted([sign*(wx-.4),sign*(self.rx-.6)])),(y-.35,y+.35),(42.7,43.8)),6)
  # Shallow reduced roof-course relief, mathematical authored geometry rather than copied tile texture.
  courses=[]
  for y in np.arange(-self.ry+2,self.ry-1,p['roof_course_pitch_mm']):
   z=float(self.h(np.array([[0,y]]))[0]);courses.append(box((-gx+.7,gx-.7),(y-.13,y+.13),(z-.28,z+.17)))
  for sign in [-1,1]:
   for x in np.arange(gx+1,self.rx-1,p['roof_course_pitch_mm']):
    lim=self.ry-(self.rx-x)*(self.ry-gy)/(self.rx-gx);z=float(self.lowerh(np.array([[x,0]]))[0]);courses.append(box((sign*x-.13,sign*x+.13),(-lim+.9,lim-.9),(z-.28,z+.17)))
  self.add('Reduced main roof course relief',union(courses),2,'P01 p3 reduced roofing rhythm: constant-height shallow courses on explicit roof profiles, not exact tile counts or copied texture')
  # Copper horizontal main ridge, gable verges and lower hip corners.
  self.add('Main copper ridge cap',box((-gx-1.6,gx+1.6),(-1.35,1.35),(96.4,98.4)),3)
  for side in [-1,1]:
   x=side*gx
   self.add('Copper ridge end pedestal %d'%side,box((x-3.5,x+3.5),(-5.0,5.0),(92.9,98.4)),3,'P03 A08–A11 ridge-end square shoulders; P01 p4 copper detail')
   for sign in [-1,1]:
    for j,(ya,yb)in enumerate(zip(np.linspace(0,gy,11)[:-1],np.linspace(0,gy,11)[1:])):
     aa=np.array([[x,sign*ya],[x,sign*yb]]);zz=self.h(aa)+.35
     self.beam([x,sign*ya,zz[0]],[x,sign*yb,zz[1]],1.18,3,'Gable copper verge %d %d %02d'%(side,sign,j))
    pts=np.c_[np.linspace(x,side*self.rx,11),np.linspace(sign*gy,sign*self.ry,11)];zz=self.h(pts)+.35
    for j in range(10):self.beam([*pts[j],zz[j]],[*pts[j+1],zz[j+1]],1.0,3,'Lower copper hip %d %d %02d'%(side,sign,j))
   # Dark triangular upper gable: appears on each short side only.
   poly=Polygon([(-35.7,62.0),(0,92.8),(35.7,62.0)])
   da,db=sorted([x+side*.03,x+side*.75]);self.add('Dark gable louver field %d'%side,oriented(poly,'x',da,db),6)
   for j,y in enumerate(np.arange(-34,35,1.45)):
    ztop=92.8-abs(y)*30.8/35.7
    if ztop>62.5:self.add('Gable vertical louver %d %02d'%(side,j),oriented(rect(y-.21,62.0,y+.21,ztop),'x',*sorted([x+side*.65,x+side*1.0])),4)
   self.add('Gable pale lower cross trim %d'%side,oriented(rect(-37.2,60.3,37.2,62.2),'x',*sorted([x+side*.1,x+side*1.2])),7)
   # Stylized pendant outline; no claim to replicate carved motif.
   ped=Polygon([(-1.1,88.0),(-1.8,84.6),(-3,84),(-2.5,82.2),(-.6,83),(0,80.8),(.6,83),(2.5,82.2),(3,84),(1.8,84.6),(1.1,88)])
   self.add('Simplified gable pendant %d'%side,oriented(ped,'x',*sorted([x+side*.7,x+side*1.45])),7)
   # C-shaped chiwen ridge end, hooks inward along the long ridge.
   hook=[(-2,0),(-2,4),(-1.6,6.5),(-.8,8.4),(.5,9.8),(2.1,10.6),(4.1,10.85),(5.4,10.6),(5.3,9.5),(3.7,8.9),(2.7,7.9),(2.2,6.2),(2.1,3.1),(2.6,1.4),(4.8,1.4),(5.1,0)]
   hp=Polygon([(x-side*u,98.1+v)for u,v in hook]);hm=oriented(hp,'y',-1.15,1.15)
   def taper_hook(v):
    q=np.array(v,copy=True);q[:,1]*=(3.3-1.8*np.clip((q[:,2]-98.1)/10.85,0,1))/1.15;return q
   self.add('Copper chiwen inward hook %d'%side,hm.warp_batch(taper_hook),3,'P01 p4 closeup and A08/A09; bounded simplified silhouette, not exact carved/scaled detail')
  # Entry roof: lower side hips and front upper gable; back ridge meets the main slope.
  pyfront=-(self.ry+p['porch_projection_beyond_main_roof_mm']);pyback=-61.9;pg=-82.5;phw=32.5;pgw=21.5
  def porchh(xy):
   x=np.abs(xy[:,0]);y=xy[:,1];t=np.clip((phw-x)/(phw-pgw),0,1);tf=np.clip((y-pyfront)/(pg-pyfront),0,1);sk=np.minimum(t,tf);lower=35.5+5.1*(.75*sk+.25*sk*sk)
   u=np.clip(1-x/pgw,0,1);upper=40.6+10.0*(.85*u+.15*u*u)
   return np.where((x<=pgw)&(y>=pg),upper,lower)
  pp=rect(-phw,pyfront,phw,pyback)
  prings=[(-phw,pyfront,phw,pyback,34.8)]
  for t in np.linspace(0,1,13):
   xx=phw+(pgw-phw)*t;yf=pyfront+(pg-pyfront)*t;zz=35.5+5.1*(.75*t+.25*t*t);prings.append((-xx,yf,xx,pyback,zz))
  lower=loft_rectangles(prings)
  xs=np.linspace(-pgw,pgw,45);zs=porchh(np.c_[xs,np.full(len(xs),pg+.1)])
  prof=Polygon([(-pgw,40.35),(pgw,40.35)]+list(zip(xs[::-1],zs[::-1])))
  self.add('Connected curved entry roof',lower+oriented(prof,'y',pg,pyback),2,'P03 A07/A08/A10/A14, P01 p3; explicit lower-hip loft and upper profile, connected into main roof')
  self.add('Porch dark eave fascia',solid(pp.buffer(.15,join_style=2).difference(pp.buffer(-.75)),34.6,35.6),6)
  pr=[]
  for x in np.arange(-phw+1,phw-1,1.7):
   z=float(porchh(np.array([[x,pg+.1]]))[0]);ymin=pg if abs(x)<=pgw else pyfront+(pg-pyfront)*(phw-abs(x))/(phw-pgw)
   pr.append(box((x-.1,x+.1),(ymin+.7,pyback-.2),(z-.28,z+.14)))
  for y in np.arange(pyfront+1,pg-.2,1.7):
   t=(y-pyfront)/(pg-pyfront);lim=phw+(pgw-phw)*t;z=float(porchh(np.array([[0,y]]))[0]);pr.append(box((-lim+.8,lim-.8),(y-.1,y+.1),(z-.28,z+.14)))
  self.add('Reduced entry roof course relief',union(pr),2)
  self.add('Entry copper ridge',box((-0.8,.8),(pg-1,pyback+.3),(49.7,51.0)),3)
  for side in [-1,1]:
   pts=np.c_[np.linspace(0,side*phw,15),np.full(15,pg)];zz=porchh(pts)+.25
   for j in range(14):self.beam([*pts[j],zz[j]],[*pts[j+1],zz[j+1]],.8,3,'Entry copper verge %d %02d'%(side,j))
   pts=np.c_[np.linspace(side*pgw,side*phw,8),np.linspace(pg,pyfront,8)];zz=porchh(pts)+.25
   for j in range(7):self.beam([*pts[j],zz[j]],[*pts[j+1],zz[j+1]],.75,3,'Entry lower hip %d %02d'%(side,j))
  pgab=Polygon([(-17.3,40.1),(0,48.8),(17.3,40.1)]);self.add('Entry dark gable face',oriented(pgab,'y',pg-.6,pg-.02),6)
  for i,x in enumerate(np.arange(-16,17,1.3)):
   h=48.8-abs(x)*8.7/17.3
   if h>40.3:self.add('Entry gable louver %02d'%i,oriented(rect(x-.18,40.1,x+.18,h),'y',pg-.9,pg-.5),4)
  self.add('Entry pale gable lower trim',box((-19,19),(pg-.9,pg-.1),(39.5,40.6)),7)
  self.add('Entry small copper finial',solid(Point(0,pg).buffer(.65,resolution=4),50.4,52.5),3)
  return union(self.items)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build();assert s.status()==mf.Error.NoError,s.status()
 s=s.set_tolerance(.003).simplify(.003);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):mi[mm.run_index[i]//3:mm.run_index[i+1]//3]=b.ids[int(oid)]
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,5),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.004).simplify(.004)
 parts=canonical.decompose();filled=len([q for q in parts if q.volume()<=0]);canonical=union([q for q in parts if q.volume()>0]);cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts)
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'daxi-butokuden-main-hall-2014.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 partdata=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();partdata.append({'name':op['name'],'vertices':np.asarray(m.vert_properties)[:,:3].tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(partdata,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(partdata),'non_visible_closed_cavities_filled_for_exterior_display':filled,'float_canonical_tolerance_mm':.004,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
