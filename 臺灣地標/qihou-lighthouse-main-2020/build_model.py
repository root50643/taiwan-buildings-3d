#!/usr/bin/env python3
"""Original parameterized whole Qihou Lighthouse circa-2020 exterior; no source pixels."""
import argparse,pathlib,json,math
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,Point,box as rect
from shapely.ops import unary_union
PALETTE=[
 {'id':'white_wall','name':'White masonry','hex':'#E9EBE6','evidence':'P01 PDF3/4/8/9 completed white exterior; no calibrated sampling'},
 {'id':'white_trim','name':'Light painted trim','hex':'#F2F3EE','evidence':'P01 A11/A12 white architectural trim; PDF3 lower completed 2020-08-03 photo pale lantern lattice and upper rim'},
 {'id':'white_roof','name':'Light waterproof roof','hex':'#DDE1DB','evidence':'P01 PDF119 photographs5-146/147 completed wing roof coating'},
 {'id':'dark_metal','name':'Dark dome and selected metalwork','hex':'#333B40','evidence':'P01 PDF6 dark dome/railing; PDF3 lower completed photo dark lower lantern band; not a generic metal color'},
 {'id':'grey_frame','name':'Restrained gray frames','hex':'#7A858A','evidence':'P01 PDF3/4 front frames gray; hidden finishes simplified, not uniformly established'},
 {'id':'glazing','name':'Opaque blue-gray glazing approximation','hex':'#52646C','evidence':'Authored opaque glazing representation, not measured glass transmission or interiors'},
 {'id':'balcony_deck','name':'Muted balcony deck','hex':'#77786D','evidence':'P01 PDF6 overhead deck distinct from white wing roof; uncalibrated'},
 {'id':'base_band','name':'Dark lower plinth band','hex':'#4C5355','evidence':'P01 PDF4 visible dark band below front white walls; extent simplified'}]
def union(parts):
 q=[x for x in parts if not x.is_empty()];return mf.Manifold.batch_boolean(q,mf.OpType.Add)if q else mf.Manifold()
def solid(poly,z0,z1):
 if poly.is_empty:return mf.Manifold()
 if poly.geom_type=='MultiPolygon':return union([solid(x,z0,z1)for x in poly.geoms])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(x.coords)[:-1]for x in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return solid(rect(x[0],y[0],x[1],y[1]),*z)
def along_y(poly,lo,hi):return solid(poly,lo,hi).rotate([90,0,0]).translate([0,lo+hi,0])
def along_x(poly,lo,hi):return along_y(poly,lo,hi).rotate([0,0,-90])
def arch(r,spring,bottom):
 return Polygon([(-r,bottom),(r,bottom),(r,spring)]+[(r*math.cos(t),spring+r*math.sin(t))for t in np.linspace(0,np.pi,33)[1:]]+[(-r,bottom)])
def octagon(flat):
 h=flat/2;k=h*(math.sqrt(2)-1)
 return Polygon([(-k,-h),(k,-h),(h,-k),(h,k),(k,h),(-k,h),(-h,k),(-h,-k)])
def rod(a,b,r=.5,segments=8):
 aa=np.asarray(a,float);bb=np.asarray(b,float);zz=bb-aa;L=np.linalg.norm(zz);zz/=L;ref=np.array([0.,0,1])if abs(zz[2])<.95 else np.array([1.,0,0]);xx=np.cross(ref,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return mf.Manifold.cylinder(L+.08,r,r,segments).transform(np.column_stack([xx,yy,zz,aa-.04*zz]))
def cyl(r,z0,z1,n=96):return mf.Manifold.cylinder(z1-z0,r,r,n).translate([0,0,z0])
def ring(r,w,z0,z1,n=96):return cyl(r+w/2,z0,z1,n)-cyl(r-w/2,z0-1,z1+1,n)
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.owner_ids={}
 def add(self,name,m,mat,evidence):
  if m.is_empty():return
  override=self.p.get('component_material_overrides',{}).get(name)
  if override is not None:
   mat=next(i for i,q in enumerate(PALETTE)if q['id']==override)
   evidence+='; P01 PDF3 lower completed photo 2020-08-03: exact component material correction to '+override
  assert m.status()==mf.Error.NoError,(name,m.status());m=m.as_original();self.ids[int(m.original_id())]=mat;self.owner_ids[int(m.original_id())]=len(self.items);self.items.append(m);self.ops.append({'name':name,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(m.bounding_box())})
 def local(self,m):return m.translate([0,self.p['tower_y_mm'],0])
 def frame(self,name,x,face_y,z0,z1,width,front=True):
  # Recessed glazing is opaque and attached to the solid exterior; no invented interiors.
  sign=-1 if front else 1;surface=face_y
  def depth(a,b):return (surface+min(sign*a,sign*b),surface+max(sign*a,sign*b))
  self.add(name+' opaque inset glass',box((x-width/2,x+width/2),depth(-3.3,-1.4),(z0,z1)),5,'P01 A09/A11/A12 opening position; opaque recessed glazing is a modeling convention')
  outer=rect(x-width/2-.65,z0-.65,x+width/2+.65,z1+.65);inner=rect(x-width/2+.6,z0+.6,x+width/2-.6,z1-.6)
  bars=along_y(outer.difference(inner),*depth(-1.65,.30))
  for xx in [x]:bars+=box((xx-.4,xx+.4),depth(-1.65,.35),(z0,z1))
  for zz in np.linspace(z0,z1,7)[1:-1]:bars+=box((x-width/2,x+width/2),depth(-1.65,.35),(zz-.35,zz+.35))
  self.add(name+' gray sash and crossbars',bars,4,'P01 A11/A12 tall narrow sash rhythm; PDF3/4 front gray framing, other frames simplified')
  surround=outer.buffer(.9,join_style=2).difference(outer)
  self.add(name+' white surround and sill',along_y(surround,*depth(-.25,.65))+box((x-width/2-2,x+width/2+2),depth(-.2,1.5),(z0-1.6,z0-.5)),1,'P01 A11/A12 thin white surrounds and projecting sill')
 def build(self):
  p=self.p;front=-p['wing_depth_mm']/2;rear=-front;wf=p['wing_front_width_mm']/2;wr=p['wing_rear_width_mm']/2;cy=p['tower_y_mm'];floor=p['floor_z_mm'];eave=p['eave_z_mm'];shaft=octagon(p['tower_across_flats_mm']);towerpoly=Polygon([(x,y+cy)for x,y in shaft.exterior.coords]);wing=Polygon([(-wf,front),(wf,front),(wr,rear),(-wr,rear)]);neck=rect(-p['neck_width_mm']/2,rear-1,p['neck_width_mm']/2,cy-15);foot=unary_union([wing,neck,towerpoly])
  self.add('Connected building foundation footprint',solid(foot.buffer(2,join_style=2),0,3.0),1,'P01 A09 full wing, short neck and octagonal tower; not whole precinct, open reentrant sides')
  self.add('Low plinth band',solid(foot,2.9,floor+.15),7,'P01 PDF4 visible dark base band, reduced approximation; no site walls')
  winz=(p['window_bottom_z_mm'],p['window_top_z_mm']);ww=p['window_width_mm'];cuts=[]
  for x in p['front_window_centers_mm']:cuts.append(box((x-ww/2,x+ww/2),(front-7,front+3),winz))
  for x in p['rear_window_centers_mm']:cuts.append(box((x-ww/2,x+ww/2),(rear-3,rear+7),winz))
  entrance=along_y(arch(12.5,65.0,floor-.1),front-9,front+3)
  sidecut=box((wr-3,wr+6),(-9.4,9.4),(floor-.1,55.4))
  wingbody=(solid(wing,floor-.1,eave-1.5)+box((-36.4,36.4),(front-3.0,front+.3),(floor-.1,eave-1.5)))-union(cuts+[entrance,sidecut])
  self.add('Whole wing with recessed openings',wingbody,0,'P01 A09/A11/A12 entire office/exhibition wing; front four windows and central arch, rear four windows, SW side door, NE blind side. Solid exterior, not full interior reconstruction')
  self.add('Short physically connected neck',solid(neck,floor-.1,eave),0,'P01 A09 and A13 roof and neck attach to tower; open exterior reentrant spaces on both sides')
  # Tower window heights deliberately differ: high NW/rear, low NE/left facet.
  twrear=box((-5.5,5.5),(cy+29.6,cy+35),(106,125.5));twleft=box((-35,-29.6),(cy-5.5,cy+5.5),(41,61))
  self.add('Eight faceted tower shaft',solid(towerpoly,floor-.1,143.0)-twrear-twleft,0,'P01 A09/A10 octagonal tower, A12 unequal tower opening heights; not a round generic shaft')
  self.frame('Tower high NW window',0,cy+32.8,106,125.5,11,False)
  # Rotate a local front-style window onto the NE side of the tower.
  before=len(self.items);self.frame('Tower low NE window',0,-32.8,41,61,11,True)
  for j in range(before,len(self.items)):
   self.items[j]=self.items[j].rotate([0,0,-90]).translate([0,cy,0]);self.ops[j]['bounds_model_mm']=list(self.items[j].bounding_box())
  for face,xs,y in [('SE',p['front_window_centers_mm'],front),('NW',p['rear_window_centers_mm'],rear)]:
   for i,x in enumerate(xs):self.frame(f'Wing {face} window {i+1}',x,y,*winz,ww,face=='SE')
  # Central arched double door and a reduced radial/diagonal fanlight, not copied ornament.
  self.add('Front opaque arched entry recess',along_y(arch(12.5,65.0,floor),front+1.4,front+3.3),5,'P01 A11 arched entry; opaque closed-leaf representation avoids inventing interior')
  surround=arch(15.0,65.0,floor-.1).difference(arch(13.1,65.0,floor-.1));self.add('Front white arched entry surround',along_y(surround,front-3.5,front+.4),1,'P01 A11 white arched surround')
  door=box((-11.8,11.8),(front-1.0,front+1.8),(floor,59.7))
  self.add('Front gray double door leaves',door,4,'P01 A11 double-leaf entry, PDF4 gray front door; reduced panel detail')
  panels=[]
  for xx in [-6,6]:
   for z0,z1 in [(floor+3,floor+20),(floor+23,floor+37),(floor+40,57.8)]:
    q=rect(xx-4.3,z0,xx+4.3,z1).difference(rect(xx-3.7,z0+.6,xx+3.7,z1-.6));panels.append(along_y(q,front-1.45,front-.7))
  panels.append(box((-.42,.42),(front-1.55,front-.7),(floor,60)))
  self.add('Front door authored panel moldings',union(panels),1,'P01 A11 six rectangular leaf panels; reduced original profile without inscriptions')
  fan=arch(11.8,65,60.5);bars=[]
  for xx in [-8,-4,0,4,8]:bars.append(along_y(rect(xx-.3,60.4,xx+.3,78),front-.9,front+1.6)^along_y(fan,front-2,front+3))
  for zz in [60.5,65,69.5,74]:bars.append(along_y(rect(-13,zz-.3,13,zz+.3),front-.9,front+1.6)^along_y(fan,front-2,front+3))
  for x in [-8,0,8]:
   for sg in [-1,1]:bars.append(rod([x,front-.4,61],[x+sg*10,front-.4,73],.32)^along_y(fan,front-2,front+3))
  self.add('Front fanlight reduced geometric lattice',union(bars),4,'P01 A11 fanlight geometric pattern, simplified authored lattice not exact ornamental tracing')
  # Side door on SW/+X only. NE/-X remains deliberately blind.
  self.add('SW opaque side doorway',box((wr-3.3,wr-1.5),(-9.4,9.4),(floor,55.4)),5,'P01 A11 SW single doorway; no mirrored NE door')
  sideframe=rect(-10.2,floor,10.2,56.2).difference(rect(-8.5,floor+.9,8.5,54.5));sf=along_x(sideframe,wr-1.9,wr+.3)
  for z in [24,40]:sf+=box((wr-1.8,wr+.2),(-9,9),(z-.5,z+.5))
  sf+=box((wr-1.8,wr+.2),(-.45,.45),(floor,55.4));self.add('SW gray door frame',sf,4,'P01 A11 side door rectangular panels; restrained uncalibrated gray')
  self.add('SW door canopy and brackets',box((wr-.3,wr+5),(-13.5,13.5),(58,59.3))+box((wr-.3,wr+3),(-10.5,-9),(56.2,58.2))+box((wr-.3,wr+3),(9,10.5),(56.2,58.2)),1,'P01 A11 small side-door projection and pair of brackets')
  self.add('SW attached doorstep',box((wr-1,wr+7),(-11,11),(0,3))+box((wr-1,wr+5),(-10.5,10.5),(2.9,6))+box((wr-1,wr+3),(-10,10),(5.9,9)),1,'P01 A09/A11 side entrance low attached steps, approximate risers')
  # Shallow facade relief panels and pilasters preserve four-face asymmetry.
  for sg in [-1,1]:
   self.add(f'SE pilaster {sg}',box((sg*36.4-2,sg*36.4+2),(front-3.7,front+.3),(floor,eave-2)),1,'P01 A11 central pediment bay pilasters')
   self.add(f'SE outer corner pilaster {sg}',box((sg*118.7-1.8,sg*118.7+1.8),(front-1.2,front+.4),(floor,eave-2)),1,'P01 A11 front outer corner relief')
  panelborder=rect(-35,10,35,70.5).difference(rect(-34.4,10.6,34.4,69.9))
  self.add('NE blind wall recessed-panel border',along_x(panelborder,-wf-.35,-wf+.4),1,'P01 A12 NE blank rectangular wall panel; explicitly not a door')
  swpanel=along_x(panelborder,wr-.4,wr+.35)-sidecut
  self.add('SW wall panel border',swpanel,1,'P01 A11 side relief panel surrounding side door')
  # Front entry has only the building-attached stair, not the long precinct stair.
  steps=[]
  for k in range(6):
   yy=front-29+4.5*k;steps.append(box((-14.7,14.7),(yy,front+1),(0,(k+1)*1.5)))
  self.add('Attached front six-step entrance',union(steps),6,'P01 A09/A11 attached entrance steps only; reduced approximate risers, excludes hill approach')
  for sg in [-1,1]:
   side=Polygon([(front-30,0),(front-30,3),(front-1,15),(front+1,15),(front+1,0)])
   # Profile uses y as horizontal coordinate; along_x reverses y.
   self.add(f'Front stair cheek {sg}',along_x(side,sg*16-1.5,sg*16+1.5).rotate([0,0,180]),1,'P01 A11/PDF4 white low cheek walls attached to front steps; approximate incline')
  # Flat draining roof behind a narrow front pediment; no pitched wing roof.
  roofpoly=unary_union([rect(-p['roof_width_mm']/2,-p['roof_depth_mm']/2,p['roof_width_mm']/2,p['roof_depth_mm']/2),rect(-32.8,rear-1,32.8,cy)])
  self.add('Whole low wing and neck roof slab',solid(roofpoly,eave-2.0,eave+.5),2,'P01 A09 RF and PDF119 flat/slightly draining white roof meets the tower; no occupied second floor')
  self.add('Wing white projecting cornice',solid(roofpoly.buffer(1.0,join_style=2),eave-1.8,eave-.3),1,'P01 A11/A12 continuous projecting white cornice')
  parapetouter=unary_union([rect(-125.0,-55.4,125.0,55.4),rect(-28.6,51,28.6,cy)])
  parapet=parapetouter.difference(parapetouter.buffer(-4,join_style=2)).difference(towerpoly.buffer(.02,join_style=2))
  self.add('Low continuous roof parapet',solid(parapet,eave-.1,p['parapet_z_mm']),0,'P01 A09 RF/PDF119 low perimeter parapet; connector touches tower, no enclosed courtyard')
  ped=Polygon([(-36.4,eave-1),(36.4,eave-1),(0,p['pediment_peak_z_mm'])]);self.add('Central front pediment only',along_y(ped,front-8.9,front-1.4),0,'P01 A11 triangular central entrance pediment, not a full pitched roof')
  trim=Polygon([(-38,eave-1.3),(0,p['pediment_peak_z_mm']+1.3),(38,eave-1.3),(35.4,eave-1.3),(0,p['pediment_peak_z_mm']-1.2),(-35.4,eave-1.3)])
  self.add('Pediment raised sloping cornice',along_y(trim,front-9.7,front-7.8),1,'P01 A11 paired sloping pediment molding; reduced section')
  # Four small drainage openings are source-backed; no rooftop lamp bases remain.
  for i,x in enumerate([-100,-43,43,100]):
   self.add(f'Front roof rainwater pipe {i+1}',cyl(.65,floor+.5,eave,12).translate([x,front-1,0])+box((x-1.2,x+1.2),(front-2.3,front+.6),(floor+.5,floor+3)),4,'P01 A08 four wing roof drains/A11 slim vertical pipes; simplified routing and gray finish')
  self.add('Octagonal shaft cornice band',self.local(solid(octagon(71),140.0,144.5)),1,'P01 A11/A12 octagonal tower transition below balcony')
  brackets=[]
  for i in range(24):
   angle=i*15+7.5
   for r0,r1,z0,z1 in [(31,39,141,148.2),(37,45,143,148.2),(43,51.5,145,148.2)]:brackets.append(box((r0,r1),(-1.3,1.3),(z0,z1)).rotate([0,0,angle]))
  self.add('Twenty-four reduced stepped corbels',self.local(union(brackets)),1,'P01 A11/A12 stepped balcony support rhythm; reduced count/detail, not exact carving')
  self.add('Octagonal balcony slab',self.local(solid(octagon(p['balcony_across_flats_mm']),p['balcony_bottom_z_mm'],p['balcony_top_z_mm'])),1,'P01 A10 eight-sided balcony outline, not circular deck')
  self.add('Octagonal muted balcony walking surface',self.local(solid(octagon(p['balcony_across_flats_mm']-1.2),p['balcony_top_z_mm']-.3,p['balcony_top_z_mm']+.35)),6,'P01 PDF6 deck muted/dark compared with brilliant white wing coating')
  pedestal=cyl(p['pedestal_radius_mm'],p['balcony_top_z_mm']-.3,p['lantern_bottom_z_mm'],96)
  pedcut=box((-7,7),(-32,-27),(p['balcony_top_z_mm'],177.4));pedestal-=pedcut
  self.add('Circular lantern pedestal',self.local(pedestal),0,'P01 A10/A11 round lantern base above independent octagonal shaft and deck')
  self.add('Front balcony doorway inset',self.local(box((-7,7),(-28.2,-26.5),(p['balcony_top_z_mm'],177.4))),4,'P01 A11 door in front of circular lantern pedestal; opaque simplified leaf')
  doorring=rect(-8,p['balcony_top_z_mm'],8,178.4).difference(rect(-6.3,p['balcony_top_z_mm']+.8,6.3,176.6))
  self.add('Front balcony doorway white surround',self.local(along_y(doorring,-30.8,-27.4)),1,'P01 A11 balcony doorway surround')
  for z,r in [(p['balcony_top_z_mm']+1,31.3),(p['lantern_bottom_z_mm']-2.2,31.5)]:self.add(f'Lantern base cornice {z}',self.local(cyl(r,z,z+1.3)),1,'P01 A11/A12 circular pedestal bands')
  rail=[];zb=p['balcony_top_z_mm'];rt=p['railing_radius_mm']
  for i in range(p['railing_pickets']):
   t=2*math.pi*i/p['railing_pickets'];rail.append(cyl(p['railing_bar_radius_mm'],zb-.5,zb+p['railing_height_mm'],8).translate([rt*math.cos(t),rt*math.sin(t),0]))
  for z in [zb+1.8,zb+18.2,zb+p['railing_height_mm']-.4]:rail.append(ring(rt,1.15,z,z+.8,128))
  self.add('Circular open balcony railing',self.local(union(rail)),3,'P01 A10/PDF6 circular dark railing inside octagonal balcony; 64 reduced pickets, open gaps retained')
  # Opaque glass cylinder with source-specific two-tier diagonal lantern lattice.
  self.add('Opaque lantern glazing body',self.local(cyl(p['lantern_radius_mm']-.75,p['lantern_bottom_z_mm']-.3,p['lantern_top_z_mm']+.3,96)),5,'P01 A10/A11 circular glazing; opaque material preserves exterior without invented optics/interior')
  lattice=[];rb=p['lantern_radius_mm'];z0=p['lantern_bottom_z_mm'];z1=p['lantern_top_z_mm'];zm=(z0+z1)/2;N=p['lantern_bays']
  for z in [z0,zm,z1-.6]:lattice.append(ring(rb,1.6,z-.2,z+.8,96))
  for i in range(N):
   aa=2*math.pi*i/N;bb=2*math.pi*(i+1)/N
   for za,zz in [(z0,zm),(zm,z1)]:
    lattice.append(rod([rb*math.cos(aa),rb*math.sin(aa),za],[rb*math.cos(bb),rb*math.sin(bb),zz],.66,10));lattice.append(rod([rb*math.cos(bb),rb*math.sin(bb),za],[rb*math.cos(aa),rb*math.sin(aa),zz],.66,10))
  self.add('Two tier diagonal lantern frame',self.local(union(lattice)),3,'P01 A11/A12 diagonal rhomboid/triangular lantern framing; reduced 12-bay layout')
  self.add('Dome lower projecting rim',self.local(cyl(30.1,p['lantern_top_z_mm']-.6,p['lantern_top_z_mm']+.9)),3,'P01 A10/A11 circular projecting dome rim; PDF3 completed photo establishes pale finish')
  dome=mf.Manifold.sphere(p['dome_radius_mm'],96).translate([0,0,p['lantern_top_z_mm']])^box((-40,40),(-40,40),(p['lantern_top_z_mm']-.2,260))
  self.add('Dark hemispherical dome',self.local(dome),3,'P01 PDF6/PDF103 dark dome; A10 circular dome profile, no copied photographic texture')
  # Crown/orb/vane dimensions are bounded simplifications of A11/A12 silhouette.
  crown=cyl(7.0,246.3,251.3,64)+mf.Manifold.cylinder(2.2,9.3,6.6,64).translate([0,0,250.7])+cyl(2.7,252.7,256.2,32)+mf.Manifold.sphere(5.6,48).translate([0,0,261.0])
  self.add('Dome crown and finial orb',self.local(crown),3,'P01 A11/A12 crown and orb silhouette; exact small finial geometry unresolved')
  fin=cyl(.58,266,284,12)
  for z,length in [(274,8),(278.5,6)]:fin+=rod([-length/2,0,z],[length/2,0,z],.45,8)
  fin+=rod([0,0,282],[2.1,0,283.5],.45,8)+rod([0,0,282],[-1.7,0,284],.45,8)
  self.add('Reduced finial and weather vane',self.local(fin),3,'P01 A11/A12 reduced connected vane, no exact symbols or inscription; thin-feature print caution')
  # Completed ladder is pale, not red primer from construction-stage photograph.
  ladder=[];x=22.5;yy=-20.5
  for dx in [-2.0,2.0]:ladder.append(rod([x+dx,yy,174],[x+dx,yy,223.0],.58,10))
  for z in np.arange(176,222,4):ladder.append(rod([x-2.0,yy,z],[x+2.0,yy,z],.52,10))
  for z in [178,191,214]:ladder.append(rod([x,yy,z],[x*.91,yy*.91,z],.7,10))
  self.add('Pale exterior lantern access ladder',self.local(union(ladder)),1,'P01 A11 ladder location and PDF6 completed pale ladder; red primer stage explicitly not final material')
  return union(self.items)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build();assert s.status()==mf.Error.NoError,s.status()
 s=s.set_tolerance(.003).simplify(.003);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32);owner=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):
  sl=slice(mm.run_index[i]//3,mm.run_index[i+1]//3);mi[sl]=b.ids[int(oid)];owner[sl]=b.owner_ids[int(oid)]
 assert set(p.get('component_material_overrides',{}))<=set(x['name']for x in b.ops),'Unmatched component material override'
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,5),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.004).simplify(.004)
 cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];owner=owner[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts).copy()
 # Boolean float32 output can retain a zero-area sliver after a sub-tolerance
 # corner split. Collapse ONLY its shortest edge within the declared .004 mm;
 # no hole filling, broad vertex welding or validation tolerance relaxation.
 collapsed=0
 while True:
  tri=v[f].astype(float);area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5;bad=np.where(area<1e-9)[0]
  if not len(bad):break
  i=int(bad[0]);ff=f[i];lens=[np.linalg.norm(v[ff[(j+1)%3]].astype(float)-v[ff[j]])for j in range(3)];j=int(np.argmin(lens));assert lens[j]<=.004,(i,lens)
  keep=int(ff[j]);drop=int(ff[(j+1)%3]);f[f==drop]=keep;valid=(f[:,0]!=f[:,1])&(f[:,1]!=f[:,2])&(f[:,2]!=f[:,0]);f=f[valid];mi=mi[valid];owner=owner[valid];collapsed+=1;assert collapsed<30
 used=np.unique(f);mapping=np.full(len(v),-1,dtype=int);mapping[used]=np.arange(len(used));v=v[used];f=mapping[f]
 t=trimesh.Trimesh(v,f,process=False);t.export(out/(p['model_id']+'.stl'));np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi,component_ids=owner)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(m.vert_properties)[:,:3].tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'float_canonical_tolerance_mm':.004,'zero_area_short_edge_collapses':collapsed,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
