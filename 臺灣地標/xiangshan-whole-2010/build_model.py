#!/usr/bin/env python3
"""Own normalized geometry. No network, image tracing, textures or source-pixel inputs.
Coordinates are desktop millimetres, not surveyed building dimensions.
"""
import argparse, pathlib, json, math
import numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Polygon, LineString, Point, box as rect
from shapely.ops import unary_union
PALETTE=[
 {'id':'natural_concrete','name':'Muted natural concrete','hex':'#BBBDB5','evidence':'Architect A01/A03/A04 daylight photographs; approximate material family'},
 {'id':'recessed_glazing','name':'Opaque dark blue-grey glazing','hex':'#405963','evidence':'Architect A01/A03/A04; no source reflections or textures'},
 {'id':'roof_planting','name':'Muted green roof vegetation','hex':'#79865B','evidence':'Architect A01; grass season/dryness not fixed paint'},
 {'id':'paving','name':'Pale roof and pedestrian paving','hex':'#CAC9BD','evidence':'Architect A01/A04; roof paving and ground pedestrian paths'},
 {'id':'basin_water','name':'Restrained reflecting basin','hex':'#688989','evidence':'Architect A01/A04; simplified shallow basin, no photographic reflection'},
 {'id':'ground_planting','name':'Central planted court and inland grade','hex':'#8C986C','evidence':'Architect A01 and A07/A09 plan relationships'},
 {'id':'recess_shadow','name':'Dark doorway and slit backing','hex':'#444B4C','evidence':'Architect A03/A04 and A10; actual geometric recess backing, not painted cast shadow'},
 {'id':'neutral_base','name':'Thin contextual model closure','hex':'#AAA99D','evidence':'Authored thin closure beneath local ground; not a giant architectural podium'}]
def union(parts):
 parts=[x for x in parts if not x.is_empty()]
 return mf.Manifold.batch_boolean(parts,mf.OpType.Add) if parts else mf.Manifold()
def solid(poly,z0,z1):
 if poly.is_empty:return mf.Manifold()
 if poly.geom_type in ('MultiPolygon','GeometryCollection'):return union([solid(q,z0,z1)for q in poly.geoms if q.geom_type in ('Polygon','MultiPolygon')])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1]for r in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return solid(rect(x[0],y[0],x[1],y[1]),*z)
def curve(start,segments):
 pts=[np.array(start,float)]
 for seg in segments:
  if len(seg)==2:pts.append(np.array(seg,float));continue
  c1,c2,end=[np.array(v,float)for v in seg];p0=pts[-1].copy()
  for t in np.linspace(0,1,17)[1:]:pts.append((1-t)**3*p0+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*end)
 return Polygon(pts).buffer(0)
def shells():
 # Independently authored complete wing boundaries, not a mirrored pair.
 admin=curve((-103,93),[(50,93),(54,94),(66,94),(120,90),(120,86),(-39,47),[(-46,45),(-50,40),(-49,31)],(-40,-25),[(-39,-29),(-41,-31),(-46,-31)],(-63,-31),[(-69,-31),(-72,-28),(-74,-22)],(-109,81),[(-112,87),(-109,92),(-103,93)]])
 visitor=curve((-122,39),[(-107,39),[(-103,39),(-101,36),(-100,31)],(-88,-26),[(-84,-42),(-77,-50),(-63,-54)],(60,-75),[(60,-83),(42,-99),(18,-100)],(-112,-89),[(-122,-88),(-124,-80),(-124,-71)],(-124,36),[(-124,38),(-123,39),(-122,39)]])
 return admin,visitor
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.ap,self.vp=shells()
 def add(self,n,m,mat=0,evidence='Architect A09 plan, A01 completed roof and A10 projections; normalized bounded approximation'):
  assert not m.is_empty(),n
  assert m.status()==mf.Error.NoError,(n,m.status())
  m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_normalized_units':list(m.bounding_box())})
 def height(self,xy,wing):
  p=self.p;x=xy[:,0];tag='admin' if wing=='A' else 'visitor';hi=p['roof_peak_'+tag+'_mm'];a=p[tag+'_roof_descent_start_x'];b=p[tag+'_roof_descent_end_x'];t=np.clip((x-a)/(b-a),0,1)
  # Smooth high crown to long continuous inland grade approach, not a flat slab cap.
  h=p['roof_min_mm']+(hi-p['roof_min_mm'])*np.cos(t*np.pi/2)**1.35
  crown=.32*np.exp(-((x-(a-30))/35)**2)
  return h+crown
 def surface(self,poly,wing,bottom,top):
  if poly.is_empty:return mf.Manifold()
  if poly.geom_type in ('MultiPolygon','GeometryCollection'):return union([self.surface(q,wing,bottom,top)for q in poly.geoms if q.geom_type=='Polygon'])
  m=solid(poly,0,1).refine_to_length(self.p['surface_mesh_edge_mm'])
  def warp(v):
   q=np.array(v,copy=True);lo=bottom(q[:,:2]);hi=top(q[:,:2]);q[:,2]=lo+(hi-lo)*q[:,2];return q
  return m.warp_batch(warp)
 def layer(self,poly,wing,lo,hi):return self.surface(poly,wing,lambda xy:self.height(xy,wing)+lo,lambda xy:self.height(xy,wing)+hi)
 def body(self,poly,wing,offset=-.8):return self.surface(poly,wing,lambda xy:np.zeros(len(xy))-.05,lambda xy:np.maximum(.22,self.height(xy,wing)+offset))
 def strip(self,n,path,w,z0,z1,mat=0):self.add(n,solid(LineString(path).buffer(w/2,cap_style=2,join_style=2),z0,z1),mat)
 def build(self):
  ap,vp=self.ap,self.vp;p=self.p
  land=curve((-139,103),[(-109,107),(120,107),(135,90),(101,-72),[(98,-85),(79,-106),(48,-111)],(-120,-104),[(-137,-103),(-142,-92),(-143,-79)],(-146,83),[(-146,94),(-143,100),(-139,103)]])
  self.add('Thin local ground closure',solid(land,-p['base_thickness_mm'],0),7,'Display closure beneath the basin, paths and local grade, only 1.1 mm thick; not an exposed building podium')
  self.add('Inland ground and planted court field',solid(land.buffer(-1),-.02,.18),5)
  # Broad lakeward basin connects the nested canopy bays; crossed only by narrow paths.
  basin=curve((-137,91),[(-105,94),(-83,31),(-31,33),(-30,-39),(-97,-38),(-105,-66),(-56,-91),(-56,-100),(-122,-96),[(-134,-94),(-139,-90),(-140,-80)],(-143,79),[(-143,87),(-141,90),(-137,91)]])
  self.add('Curved reflecting basin water surface',solid(basin,.16,.30),4)
  self.add('Low basin retaining perimeter',solid(basin.buffer(.7).difference(basin.buffer(-.40)),.04,.60),0)
  # Two actual pedestrian axes across water and into the inland planted court.
  self.strip('Central inland to lake narrow pedestrian crossing',[(-141,8),(-27,8)],3.6,.27,.68,3)
  self.strip('Administration inland approach',[(-40,38),(15,50),(44,59)],4.0,.16,.50,3)
  self.strip('Visitor diagonal inland approach',[(-26,-67),(12,-40),(46,-25)],4.2,.16,.50,3)
  court=curve((-26,26),[(36,38),(35,-36),[(35,-42),(32,-46),(28,-44)],(-11,-27),[(-25,-21),(-28,-5),(-26,26)]])
  self.add('Central court pale enclosing pedestrian walk',solid(court.buffer(2.7),.16,.46),3)
  self.add('Separate inland central planted court',solid(court,.40,.64),5)
  # Paved ramps/trenches remain recessed rather than becoming roof through-holes.
  ar=curve((-27,44),[(38,63),(38,69),(62,74),(61,77),(40,78),(-18,86),(-20,84),(38,73),(37,70),(-28,48)])
  vr=curve((-107,-20),[(-103,-37),[(-97,-59),(-83,-71),(-58,-78)],(-56,-79),[(-54,-80),(-55,-81),(-58,-81)],(-76,-80),[(-95,-77),(-105,-65),(-111,-45)],(-114,-21),[(-114,-18),(-109,-17),(-107,-20)]])
  self.recesses={'A':ar,'V':vr}
  for wing,poly in [('A',ap),('V',vp)]:
   name='Administration' if wing=='A' else 'Visitor';r=self.recesses[wing];depth=p['admin_recess_mm'] if wing=='A' else p['visitor_recess_mm']
   def soffit(xy):
    y=xy[:,1];h=self.height(xy,wing);normal=h-p['roof_shell_mm']
    if wing=='A':extra=8*np.exp(-((y+25)/7.0)**2)+6*np.exp(-((y-39)/6.0)**2)
    else:extra=7*np.exp(-((y-35)/6.0)**2)+5*np.exp(-((y+21)/7.0)**2)
    # Only canopy legs use these smooth deepening soffits; occupied inland arms stay thin.
    extra*=1/(1+np.exp(np.clip((xy[:,0]+35)/3,-60,60)))
    return np.maximum(.12,normal-extra)
   shell=self.surface(poly,wing,soffit,lambda xy:self.height(xy,wing))
   trench=self.surface(r.intersection(poly),wing,lambda xy:np.maximum(.26,self.height(xy,wing)-depth),lambda xy:self.height(xy,wing)+3)
   shell=shell-trench
   self.add(name+' whole curved concrete roof shell',shell,0)
   # Recess floor: genuine lower surface with continuous concrete side walls left by subtraction.
   self.add(name+' long recessed access return floor',self.surface(r.buffer(.18).intersection(poly),wing,lambda xy:np.maximum(.22,self.height(xy,wing)-depth-.35),lambda xy:np.maximum(.25,self.height(xy,wing)-depth+.05)),3)
   rim=poly.difference(poly.buffer(-.52));self.add(name+' thin pale perimeter roof edge',self.layer(rim,wing,-.1,.38),0)
  # A09 RF also shows the lower outboard continuation of the administration
  # diagonal return beyond the high roof edge. It is a genuinely inclined plate,
  # not a painted line on the ground or an extension of the whole high roof cap.
  outboard=ar.difference(ap.buffer(-.45))
  self.add('Administration lower outboard inclined access return',self.surface(outboard,'A',lambda xy:self.height(xy,'A')-p['admin_recess_mm']-.48,lambda xy:self.height(xy,'A')-p['admin_recess_mm']+.05),3,'A09 RF long narrow outboard return; A01 deep roof access and A10 administration west. Exact slope is normalized, not a surveyed stair or accessibility design.')
  edge=ar.boundary.buffer(.27,cap_style=2,join_style=2).difference(ap.buffer(-.30))
  self.add('Administration outboard return low concrete parapet',self.surface(edge,'A',lambda xy:self.height(xy,'A')-p['admin_recess_mm']-.50,lambda xy:self.height(xy,'A')-p['admin_recess_mm']+.62),0)
  # Distinct planting/paved RF fields including narrow fingers/returns.
  ag=curve((-92,83),[(-62,71),(-21,78),(38,71),(38,69),(-38,49),[(-47,47),(-50,40),(-48,32)],(-45,-20),[(-45,-22),(-46,-22),(-48,-22)],(-64,-22),(-70,-1),(-72,17),(-77,35),(-90,65),(-92,83)])
  ag=ag.difference(rect(-61,-7,-55,8).union(rect(-55,-2,-42,9)))
  ag=ag.union(Polygon([(-96,91),(-23,88),(-62,77)])).union(Polygon([(-17,87),(3,82),(39,91),(49,91),(54,92),(66,92),(117,89),(117,87),(48,70),(42,75)]).buffer(0))
  vg=vp.buffer(-1.15)
  vpave=curve((-117,29),[(-108,29),[(-106,29),(-105,27),(-104,25)],(-90,-40),(-95,-41),(-100,-34),(-104,-21),[(-104,-18),(-107,-18),(-108,-20)],(-104,-36),[(-98,-61),(-83,-72),(-57,-77)],(-56,-80),(-63,-80),(-109,-75),[(-111,-75),(-111,-74),(-111,-71)],(-111,-39),(-119,-9),(-119,26),[(-119,28),(-118,29),(-117,29)]])
  vg=vg.difference(vpave)
  for name,poly,grass,r,wing in [('Administration',ap,ag,ar,'A'),('Visitor',vp,vg,vr,'V')]:
   grass=grass.intersection(poly.buffer(-.6)).difference(r.buffer(.12))
   pave=poly.buffer(-.55).difference(grass.buffer(-.18)).difference(r.buffer(.1))
   self.add(name+' complete muted planted roof fields',self.layer(grass,wing,-.20,.20),2)
   self.add(name+' perimeter and return roof paving',self.layer(pave,wing,-.20,.10),3)
   # Reduced roof paving joints on the actual broad lakeward promenade, not photographic textures.
   lines=[]
   if wing=='A':
    for y in np.arange(-17,81,6):lines.append(LineString([(-120,y),(-20,y-12)]).buffer(.055,cap_style=2))
   else:
    for y in np.arange(-69,27,6):lines.append(LineString([(-126,y),(-82,y+1)]).buffer(.05,cap_style=2))
   joints=unary_union(lines).intersection(pave.buffer(-.22))
   if not joints.is_empty:self.add(name+' reduced paved promenade joints',self.layer(joints,wing,-.15,.12),0)
  # Administration occupied floors differ in extent. Front and long side remain recessed glazing.
  a1=ap.buffer(-5.5).intersection(Polygon([(-115,96),(35,96),(35,65),(-88,33),(-96,40)]))
  a2=ap.buffer(-5.5).intersection(Polygon([(-115,96),(-7,96),(-7,58),(-88,34),(-96,40)]))
  self.add('Administration ground enclosure',self.body(a1,'A',-1.2)^box((-150,150),(-150,150),(-.1,7.2)),1)
  self.add('Administration upper enclosure shorter extent',self.surface(a2,'A',lambda xy:np.full(len(xy),7.2),lambda xy:np.maximum(7.5,self.height(xy,'A')-1.3)),1)
  self.add('Administration solid inland descending roof approach',self.body(ap.intersection(rect(35,-120,130,110)),'A',-.55),0)
  self.add('Administration upper inland roof wedge over lower floor',self.surface(ap.intersection(rect(-7,-120,35,110)),'A',lambda xy:np.full(len(xy),7.2),lambda xy:self.height(xy,'A')-.55),0)
  self.add('Administration intermediate projecting floor band',solid(a1.buffer(5.5).intersection(ap),7.0,7.55),0)
  self.add('Administration ground projecting threshold',solid(a1.buffer(5.5).intersection(ap),.27,.75),0)
  # Concrete inner-side spine does not turn the open canopy into a continuous filled wing.
  spine=a1.buffer(.30).difference(a1.buffer(-2.4)).intersection(rect(-89,-100,36,80))
  self.add('Administration inner concrete service spine',self.body(spine,'A',-1.0),0)
  for i,x in enumerate(np.arange(-98,29,5.8)):
   top=min(float(self.height(np.array([[x,91.5]]),'A')[0])-.8,15.7)
   self.add('Administration outer column %02d'%i,box((x-.28,x+.28),(90.7,92.0),(.30,top)),0)
  for i,y in enumerate(np.arange(42,80,5.8)):
   x=-109+(81-y)*.34+1.0
   self.add('Administration lake edge column %02d'%i,box((x-.3,x+.7),(y-.3,y+.3),(.3,15.7)),0)
  # Complete visitor enclosure is predominantly one storey, never a whole second floor.
  vbody=curve((-110,-18),[(-98,-20),(-94,-38),[(-92,-48),(-85,-54),(-72,-60)],(-36,-67),(35,-83),[(39,-88),(33,-95),(18,-98)],(-91,-85),[(-105,-83),(-110,-80),(-110,-75)],(-110,-18)]).intersection(vp.buffer(-.6))
  self.add('Visitor one storey glazed enclosure',self.body(vbody.intersection(rect(-140,-120,-38,-15)),'V',-1.0),1)
  self.add('Visitor long solid inland roof descent',self.body(vbody.intersection(rect(-38,-120,90,-15)),'V',-.55),0)
  vinner=vbody.buffer(.30).difference(vbody.buffer(-2.3)).intersection(Polygon([(-107,-14),(70,-14),(70,-85),(-30,-78),(-84,-71),(-107,-39)]))
  self.add('Visitor curved inland concrete enclosure edge',self.body(vinner,'V',-.85),0)
  self.add('Visitor low continuous threshold',solid(vbody.buffer(.3).intersection(vp),.28,.65),0)
  for i,y in enumerate(np.arange(-72,-20,6)):
   self.add('Visitor lake glass division %02d'%i,box((-111.0,-109.5),(y-.13,y+.13),(.3,11.8)),0)
  for i,x in enumerate(np.arange(-88,-37,6)):
   y=-85-(x+91)*13/109+.15;hi=float(self.height(np.array([[x,y]]),'V')[0])-.75
   self.add('Visitor outer long glass division %02d'%i,box((x-.13,x+.13),(y-.28,y+.28),(.35,hi)),0)
  # Solid upper ends and tapered arch supports, deliberately unequal.
  atip=ap.intersection(rect(-100,-50,-30,-19))
  vtip=vp.intersection(rect(-140,30,-90,50))
  self.add('Administration closed curved canopy end support',self.body(atip,'A',-.4),0)
  self.add('Visitor distinct smaller closed canopy end support',self.body(vtip,'V',-.4),0)
  # Registered inward diagonal visitor access break, depressed to grade with one deep wall.
  notch=Polygon([(-25,-61),(-17,-64),(-12,-61),(-5,-64),(-14,-72),(-25,-69)])
  # This local cut is applied to already authored roof surfaces only; it opens inward, not a random roof hole.
  cut=solid(notch,.45,30)
  for i,(op,item)in enumerate(zip(self.ops,self.items)):
   if op['name'].startswith('Visitor') and any(s in op['name']for s in ['roof shell','roof edge','roof fields','roof paving','promenade joints','enclosure']):
    q=item-cut
    if not q.is_empty():
     q=q.as_original();self.ids[int(q.original_id())]=next(j for j,d in enumerate(PALETTE)if d['id']==op['material']);self.items[i]=q;op['bounds_normalized_units']=list(q.bounding_box())
  self.add('Visitor inward diagonal access cut floor',solid(notch,.15,.50),3,'A09 RF inward diagonal break and A01 approach; exact stairs generalized as miniature ramp landing')
  # Administration inward long slit: A10 west and the A09 diagonal inner flank.
  slitpoly=LineString([(-24,56.6),(31,69.9)]).buffer(1.7,cap_style=2)
  slit=solid(slitpoly,3.6,4.7)
  for i,op in enumerate(self.ops):
   if op['name'].startswith('Administration') and any(k in op['name']for k in ['enclosure','service spine','descending roof approach']):
    q=(self.items[i]-slit).as_original();self.ids[int(q.original_id())]=next(j for j,d in enumerate(PALETTE)if d['id']==op['material']);self.items[i]=q
  self.add('Administration recessed inward long slit backing',solid(LineString([(-24,58.3),(31,71.6)]).buffer(.45,cap_style=2),3.7,4.6),6,'A10 administration west long slit aligned to A09 inner diagonal flank; low-resolution position and exact width generalized')
  # Dark geometrically inset end doorway in the administration solid support, from A04.
  door=box((-58,-54),(-31.5,-28.8),(.55,5.4))
  for i,op in enumerate(self.ops):
   if op['name']=='Administration closed curved canopy end support':
    q=(self.items[i]-door).as_original();self.ids[int(q.original_id())]=0;self.items[i]=q
  self.add('Administration recessed canopy end doorway',box((-57.8,-54.2),(-29.0,-28.7),(.65,5.25)),6,'A04 canopy solid end recess, registered at narrow administration end; fine door hardware omitted')
  # Recesses must cut the occupied/ramp volumes too, not expose a false glass floor.
  for tag,wing,poly in [('Administration','A',ap),('Visitor','V',vp)]:
   r=self.recesses[wing].intersection(poly);depth=p['admin_recess_mm'] if wing=='A' else p['visitor_recess_mm']
   cutter=self.surface(r,wing,lambda xy:np.maximum(.26,self.height(xy,wing)-depth),lambda xy:self.height(xy,wing)+3)
   for i,op in enumerate(self.ops):
    if op['name'].startswith(tag) and not any(t in op['name']for t in ['access return floor','doorway','outboard']):
     q=self.items[i]-cutter
     if not q.is_empty():
      q=q.as_original();self.ids[int(q.original_id())]=next(j for j,d in enumerate(PALETTE)if d['id']==op['material']);self.items[i]=q
   side=r.buffer(.45).difference(r.buffer(-.25)).intersection(poly)
   self.add(tag+' recessed route concrete sidewalls',self.surface(side,wing,lambda xy:np.maximum(.20,self.height(xy,wing)-depth-.30),lambda xy:self.height(xy,wing)+.12),0)
  return union(self.items)

def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().set_tolerance(.002).simplify(.002);assert s.status()==mf.Error.NoError,s.status()
 mm=s.to_mesh();s=mf.Manifold(mm).set_tolerance(.004).simplify(.004);closed=s.decompose();filled=len([q for q in closed if q.volume()<=0]);s=union([q for q in closed if q.volume()>0]);s=mf.Manifold(s.to_mesh()).set_tolerance(.005).simplify(.005);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32);groups=np.zeros(len(f),np.int32);group_ids={int(item.original_id()):(1 if op['name'].startswith('Administration') else 2 if op['name'].startswith('Visitor') else 0)for op,item in zip(b.ops,b.items)}
 for i,oid in enumerate(mm.run_original_id):
  sl=slice(mm.run_index[i]//3,mm.run_index[i+1]//3);mi[sl]=b.ids[int(oid)];groups[sl]=group_ids[int(oid)]
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,4),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.asarray(mi+len(PALETTE)*groups,dtype=np.uint32))).set_tolerance(.001).simplify(.001);canonical_parts=canonical.decompose();filled+=len([q for q in canonical_parts if q.volume()<=0]);canonical=union([q for q in canonical_parts if q.volume()>0]);cm=canonical.to_mesh();groups=np.asarray(cm.face_id,dtype=int)//len(PALETTE);mi=np.asarray(cm.face_id,dtype=int)%len(PALETTE);v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts)
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'xiangshan-whole-2010.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi,groups=groups)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(m.vert_properties)[:,:3].tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'non_visible_closed_cavities_filled_for_exterior_print':filled,'float_export_resimplification_tolerances_mm':[.004,.005,.001],'float_vertex_quantization_mm':.0001,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
