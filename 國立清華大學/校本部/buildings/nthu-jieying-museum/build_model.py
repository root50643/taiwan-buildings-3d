#!/usr/bin/env python3
"""Original proportional whole connected exterior. No images or network inputs.
All dimensions are representative model millimetres, not measured building dimensions.
"""
import argparse,json,pathlib,math
import numpy as np
import trimesh,manifold3d as mf
from shapely.geometry import Polygon,LineString
PALETTE=[
 {'id':'aggregate','name':'Grey green washed aggregate','hex':'#7D8986','evidence':'Built-shell photographs show grey to grey-green aggregate; uncalibrated restrained approximation'},
 {'id':'base_wall','name':'Darker lower aggregate','hex':'#555F60','evidence':'Observed dark lower irregular enclosures and retained wall forms; not all dark areas are solid walls'},
 {'id':'glass','name':'Opaque blue grey glazing','hex':'#364D59','evidence':'Observed reflective glazing, represented as opaque exterior surfaces; no interior claims'},
 {'id':'frame','name':'Dark neutral metal','hex':'#4D5555','evidence':'Actual window frames, terrace and stair railings; spacing simplified'},
 {'id':'buff','name':'Warm pale soffit and edge','hex':'#C3B999','evidence':'Actual pale warm buff soffits and edge trim; approximate colour'},
 {'id':'terrace','name':'Neutral terrace paving','hex':'#ABAFAA','evidence':'Visible pale terrace paving; fine tile pattern omitted'},
 {'id':'roof_recess','name':'Roof aperture recessed neutral closure','hex':'#374346','evidence':'Observed dark roof openings; depth simplified without inventing an interior'},
 {'id':'retained_roof','name':'Low retained form grey roof','hex':'#747B78','evidence':'Connected low gabled and retained wall forms under overhang, not detached old farmhouse'},
 {'id':'plinth','name':'Display-only neutral base','hex':'#BABCB5','evidence':'Authored supporting display base, not a reconstructed museum plinth or measured landscape'}]
def smooth_path(points,n=6,closed=False):
 """Centripetal-like restrained cubic interpolation; not a traced source image."""
 q=np.asarray(points,float);out=[]
 for i in range(len(q) if closed else len(q)-1):
  a=q[(i-1)%len(q)] if closed or i>0 else q[i]
  b=q[i];c=q[(i+1)%len(q)];d=q[(i+2)%len(q)] if closed or i+2<len(q) else c
  for t in np.linspace(0,1,n,endpoint=False):
   out.append((.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)).tolist())
 if not closed:out.append(q[-1].tolist())
 return out
def solid(poly,z0,z1):return mf.CrossSection([np.asarray(poly,float)],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def solid_shape(poly,z0,z1):
 if poly.geom_type=='MultiPolygon':return mf.Manifold.batch_boolean([solid_shape(q,z0,z1) for q in poly.geoms],mf.OpType.Add)
 loops=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in poly.interiors]
 return mf.CrossSection(loops,mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def box(x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={}
 def add(self,n,s,mat=0,evidence='Built-shell photographs plus current lower/site plan; proportional exterior simplification'):
  assert not s.is_empty(),n
  assert s.status()==mf.Error.NoError,(n,s.status())
  s=s.as_original();self.ids[int(s.original_id())]=mat;self.items.append(s);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(s.bounding_box())})
 def box(self,n,x,y,z,mat=0,evidence='Actual feature family; dimensions and small junctions approximate'):self.add(n,box(x,y,z),mat,evidence)
 def strip(self,n,path,width,z0,z1,mat=0):self.add(n,solid_shape(LineString(path).buffer(width/2,cap_style=2,join_style=2),z0,z1),mat)
 def column(self,n,x,y,z0,z1,r,mat=3):self.add(n,mf.Manifold.cylinder(z1-z0,r,r,12).translate([x,y,z0]),mat)
 def roofh(self,x,y):
  p=self.p['roof_height'];return p['valley']+p['front_peak_rise']*math.exp(-(y-p['front_peak_y'])**2/p['front_spread'])+p['rear_peak_rise']*math.exp(-(y-p['rear_peak_y'])**2/p['rear_spread'])+p['cross_wave']*math.cos((x-14)*math.pi/66)+4*math.exp(-((x-17)**2+(y-111)**2)/230)
 def bandz(self,x,y):return self.p['main_band_bottom']+self.p['main_band_end_rise']*(1-y/126)+2.5*math.sin(y*.055)+1.4*math.cos(x*.065)
 def warp_slab(self,poly,lower,upper,spacing=3):
  s=solid(poly,0,1).refine_to_length(spacing)
  return s.warp(lambda v:(v[0],v[1],lower(v[0],v[1])+(upper(v[0],v[1])-lower(v[0],v[1]))*v[2]))
 def upper_shell(self,poly):
  # One native solid with explicit vertical band boundaries prevents coincident colour skins.
  s=mf.CrossSection([poly],mf.FillRule.EvenOdd).extrude(3,2).refine_to_length(self.p['roof_mesh_spacing'])
  def warp(v):
   x,y,t=v;bottom=self.bandz(x,y);levels=[bottom-1.2,bottom,bottom+self.p['main_band_height'],self.roofh(x,y)]
   k=min(2,max(0,int(t)));u=t-k;return (x,y,levels[k]*(1-u)+levels[k+1]*u)
  return s.warp(warp)
 def railing(self,name,path,z,closed=False):
  p=self.p; line=LineString(path+([path[0]]if closed else []));h=p['rail_height'];w=p['rail_width']
  self.strip(name+' continuous top rail',list(line.coords),w,z+h-w,z+h,3)
  self.strip(name+' continuous lower rail',list(line.coords),w*.9,z+.7,z+1.5,3)
  count=max(2,int(line.length/3.2)+1)
  for j,d in enumerate(np.linspace(0,line.length,count)):
   pt=line.interpolate(float(d));self.column(name+' post '+str(j+1),pt.x,pt.y,z-.2,z+h-.25,.44,3)
 def build(self):
  p=self.p;g=p['ground_z'];bd=p['display_base'];self.box('Display-only supporting base',bd[:2],bd[2:4],bd[4:],8,'Authored support convention; not an actual building plinth or measured terrain')
  # Lower footprint consists of irregular rooms, not a filled extrusion of the main roof.
  lower=solid(p['lower_core'],g-.1,46)-box((62,112),(18,82),(17.4,120))-box((46,80),(63,82),(17.4,120))
  self.add('Irregular lower core and setbacks',lower,1)
  self.add('Northern glazed stair and core enclosure',solid(p['north_core'],g-.1,34),1)
  # Genuine open passage lies between main lower core (y <=75) and north enclosure (y >=92).
  self.column('Pale passage support',10,84,g-.1,self.bandz(10,84)+.5,1.65,4)
  # Low connected gabled enclosures sit under courtyard overhang; detached farmhouse excluded.
  for i,poly in enumerate([[[64,22],[86,22],[86,38],[65,42]],[[72,46],[99,41],[104,57],[85,64]],[[47,65],[73,65],[75,75],[51,80]]]):
   shape=Polygon(poly);cx,cy=shape.centroid.coords[0]
   self.add('Connected low retained-wall enclosure '+str(i+1),solid(poly,g-.05,17.5),1)
   top=lambda x,y,cx=cx:17.5+5.0*max(0,1-abs(x-cx)/13)
   self.add('Connected low gabled roof '+str(i+1),self.warp_slab(poly,lambda x,y:17.0,top,3),7)
   front=[poly[1],poly[2]];self.strip('Retained gabled enclosure edge '+str(i+1),front,1.0,17.3,18.2,1)
  # Long low gallery, continuous with northern main enclosure. Neutral rear: no mirrored glazing.
  front=smooth_path(p['gallery_front'],p['curve_segments']);gallery=front+p['gallery_back'];gp=Polygon(gallery);assert gp.is_valid
  self.add('Complete attached low gallery enclosure',solid(gallery,g-.1,p['gallery_body_top']),0)
  self.add('Continuous gallery warm soffit',solid_shape(gp.buffer(.65,join_style=2),25.1,26.1),4)
  self.add('Continuous gallery roof terrace slab',solid_shape(gp.buffer(.8,join_style=2),26.0,p['gallery_roof_z']),5)
  self.strip('Continuous curved courtyard gallery glazing',front,.65,g+.5,24.7,2)
  fl=LineString(front)
  for i,d in enumerate(np.linspace(0,fl.length,int(fl.length/5)+1)):
   pt=fl.interpolate(float(d));self.column('Gallery glazing division '+str(i+1),pt.x,pt.y,g+.3,25.1,p['mullion_width']/2,3)
  self.strip('Terminal glazed return',[front[-1],p['gallery_back'][0]],.75,g+.5,24.8,2)
  self.strip('Terminal concrete end wall',[p['gallery_back'][0],p['gallery_back'][1]],2.0,g-.05,31.5,0)
  # Glazed north-core courtyard face and passage face; do not close the adjacent through route.
  self.strip('Glazed stair core passage edge',p['north_core'][:3],.65,g+.6,31.7,2)
  line=LineString(p['north_core'][:3])
  for i,d in enumerate(np.linspace(0,line.length,9)):
   pt=line.interpolate(float(d));self.column('Stair core glazing division '+str(i),pt.x,pt.y,g+.4,32,.43,3)
  # Variable-height glazed band and lower ledge supporting sculpted main upper exterior.
  outline=list(Polygon(p['main_outline']).buffer(1.0,join_style=1,quad_segs=3).buffer(-1.0,join_style=1,quad_segs=3).exterior.coords)[:-1];main=Polygon(outline);assert main.is_valid
  # Main roof uses a smooth saddle/rising-end height field, with dark recessed apertures.
  roof=self.upper_shell(outline)
  ap=p['oval_aperture'];a,b=ap['radii'];cx,cy=ap['center'];rot=math.radians(ap['rotation_degrees']);oval=[]
  for t in np.linspace(0,2*math.pi,64,endpoint=False):
   u=a*math.cos(t);v=b*math.sin(t);oval.append((cx+u*math.cos(rot)-v*math.sin(rot),cy+u*math.sin(rot)+v*math.cos(rot)))
  roof=roof-solid(oval,ap['bottom_z'],120)
  for x,y,w,l,z in p['roof_slits']:roof=roof-box((x-w/2,x+w/2),(y-l/2,y+l/2),(z,120))
  # Actual tall end is set back behind a lower glass/roof edge, not an unbroken tall perimeter.
  shoulder=p['roof_front_shoulder'];roof=roof-box((-25,115),(-15,shoulder['max_y']),(shoulder['top_z'],125))
  terrace=p['main_stepped_terrace'];zone=main.intersection(Polygon([(-20,terrace['min_y']),(terrace['max_x'],terrace['min_y']),(terrace['max_x'],terrace['max_y']),(-20,terrace['max_y'])]))
  roof=roof-box((-20,terrace['max_x']),(terrace['min_y'],terrace['max_y']),(terrace['base_z'],125))
  low=p['main_lower_shoulder'];lowzone=main.intersection(Polygon([(-20,low['min_y']),(low['max_x'],low['min_y']),(low['max_x'],low['max_y']),(-20,low['max_y'])]));roof=roof-box((-20,low['max_x']),(low['min_y'],low['max_y']),(low['top_z'],125))
  self.add('Whole sculpted upper shell with integral glass and soffit bands',roof,0)
  self.main_surface_id=int(self.items[-1].original_id())
  self.add('Lower rear road-flank roof shoulder',solid_shape(lowzone.buffer(-.08),low['top_z']-.3,low['top_z']+.15),5)

  # Broad connected stepped roof sector on road flank, separate from gallery terminal stair.
  step_parts=[]
  for i in range(terrace['steps']):
   xa=terrace['min_x']+(terrace['max_x']-terrace['min_x'])*i/terrace['steps'];xb=terrace['min_x']+(terrace['max_x']-terrace['min_x'])*(i+1)/terrace['steps']
   part=zone.buffer(-.08).intersection(Polygon([(xa,terrace['min_y']),(xb,terrace['min_y']),(xb,terrace['max_y']),(xa,terrace['max_y'])]));zz=terrace['base_z']+terrace['rise']*(i+1)/terrace['steps']
   if not part.is_empty:step_parts.append(solid_shape(part,terrace['base_z']-.2,zz))
  self.add('Main roof terrace with inboard-rising broad steps',mf.Manifold.batch_boolean(step_parts,mf.OpType.Add).set_tolerance(.01).simplify(.01),5)
  self.strip('Lower street-end roof shoulder parapet',p['main_outline'][:4],1.4,shoulder['top_z']-.3,shoulder['top_z']+2.7,0)

  self.add('Oval opening deep neutral closure',solid_shape(Polygon(oval).buffer(-.05),ap['bottom_z']-.15,ap['bottom_z']+.12),6,'Observed roof aperture; closed shallow interior abstraction below the opening, not an invented room')
  for i,(x,y,w,l,z) in enumerate(p['roof_slits']):self.box('Roof slit dark bottom '+str(i),(x-w/2+.04,x+w/2-.04),(y-l/2+.04,y+l/2-.04),(z-.15,z+.05),6)
  # Upper window divisions: vary with the undulating sill, attached rather than free wires.
  per=LineString(outline+[outline[0]])
  for i,d in enumerate(np.linspace(0,per.length,int(per.length/5),endpoint=False)):
   pt=per.interpolate(float(d));z=self.bandz(pt.x,pt.y)
   if pt.x<12 and 24<pt.y<113:continue
   self.column('Main ribbon division '+str(i),pt.x,pt.y,z-.6,z+p['main_band_height']+1.0,.43,3)
  # Curved lower terrace/ledge fronts at the road end and flank; not flat rectangular box additions.
  for i,(poly,z) in enumerate([([[-1,15],[18,0],[55,-2],[79,6],[88,18],[80,26],[60,18],[31,16],[10,27]],23),([[-4,44],[-7,63],[-4,84],[3,92],[12,85],[11,58],[8,44]],41)]):
   path=smooth_path(poly,5,True);self.add('Stepped main terrace '+str(i+1),solid_shape(Polygon(path).buffer(.9,join_style=2),z-1.8,z),5)
   # Low aggregate edge is visible; deliberately robust parapet mass.
   self.strip('Main terrace curved edge '+str(i+1),path[:len(path)//2+2],1.35,z-.2,z+3.5,0)
  # Sculptural fins, skinny in plan and tapered in elevation, merge into actual roof.
  for i,(x,y,w,l,high) in enumerate([(3,36,3,22,78),(24,76,3,20,83),(17,105,3.5,15,91),(68,11,2.8,17,88)]):
   poly=[(x-w/2,y-l/2),(x+w/2,y-l/2),(x+w/2,y+l/2),(x-w/2,y+l/2)]
   self.add('Tapered projecting sculptural fin '+str(i+1),self.warp_slab(poly,lambda xx,yy:35,lambda xx,yy,y=y,l=l,high=high:high-15*((yy-y)/l+.5),2),0)
  # Tall narrow street-side blades project from low toe to high rear attachment, as in built views.
  for i,(yy,high,toe,back) in enumerate([(40,81,-8,10),(90,87,-10,12),(101,92,-2,24)]):
   # Extrude X/Z profile along Y using an orientation-preserving rotation.
   profile=[(toe,38),(back,high),(back+2.2,high),(toe+2.2,38)]
   blade=solid(profile,0,2.1).rotate([90,0,0]).translate([0,yy+1.05,0])
   self.add('Street sculptural blade '+str(i+1),blade,0)
  # Actual straight exterior stair follows the outside gallery edge to the far terrace.
  st=p['gallery_stair'];x0=st['x0'];x1=st['x1'];y0=st['y0'];w=st['width'];n=st['steps'];h=p['gallery_roof_z']-g
  for i in range(n):
   lo=x0+(x1-x0)*i/n;hi=x0+(x1-x0)*(i+1)/n+.03;top=g+h*(i+1)/n
   # Filled underside is a disclosed print simplification of the photographed structural stair.
   self.box('Exterior stair tread '+str(i+1),(lo,hi),(y0,y0+w),(g-.1,top),0)
  self.box('Exterior stair upper landing',(x1-.2,st['landing_x1']),(y0-1,y0+w),(g-.1,p['gallery_roof_z']),0)
  self.box('Stair terrace bridge',(x1-1,st['landing_x1']),(131,y0+.5),(25.5,p['gallery_roof_z']),5)
  for side,yy in [('outer',y0+w-.25),('inner',y0+.25)]:
   # Rectangular wedge rail generated as a thin warped slab follows the slope.
   poly=[(x0,yy-.45),(x1,yy-.45),(x1,yy+.45),(x0,yy+.45)]
   slope=lambda x,y:g+h*(x-x0)/(x1-x0)+p['rail_height']
   self.add('Stair '+side+' rising rail',self.warp_slab(poly,lambda x,y:slope(x,y)-.85,slope,3),3)
   for i,x in enumerate(np.linspace(x0,x1,24)):
    z=g+h*(x-x0)/(x1-x0);self.column('Stair '+side+' post '+str(i),float(x),yy,max(g-.1,z-1.3),z+p['rail_height']-.25,.44,3)
  # Gallery terrace perimeter and low circular feature are explicit photographic motifs.
  self.railing('Gallery courtyard terrace rail',[pt for pt in front if pt[0]>=69],p['gallery_roof_z'])
  self.railing('Gallery outer terrace rail',p['gallery_back'][1:]+[front[0]],p['gallery_roof_z'])
  ring=[(136+10.5*math.cos(t),121+9*math.sin(t))for t in np.linspace(0,2*math.pi,40,endpoint=False)]
  self.railing('Terrace circular feature',ring,p['gallery_roof_z'],True)
  # Ground entry door faces are limited to actually observed frontage families.
  self.strip('Lower core courtyard door recess',[(87,22),(87,31)],.7,g+.5,15.3,2)
  self.strip('Lower core street dark entry',[(24,1),(20,18)],.6,g+.5,16.3,2)
  return mf.Manifold.batch_boolean(self.items,mf.OpType.Add)
def split_colour_bands(vertices,faces,materials,main_faces,builder):
 """Conforming per-face colour boundaries; cuts are shared across incident triangles.
 Interpolate an authored band-height scalar over existing triangles, without adding skins.
 """
 vv=[np.asarray(x,dtype=np.float64) for x in vertices];qq=[float(z-builder.bandz(float(x),float(y))) for x,y,z in vertices]
 ff=[list(map(int,x)) for x in faces];mm=list(map(int,materials));flags=list(map(bool,main_faces))
 for level in [0.,float(builder.p['main_band_height'])]:
  qq=[level if abs(q-level)<.002 else q for q in qq];cache={};outf=[];outm=[];outflags=[]
  def cut(a,b):
   if qq[a]==level:return a
   if qq[b]==level:return b
   key=(min(a,b),max(a,b))
   if key not in cache:
    t=(level-qq[a])/(qq[b]-qq[a]);pos=(vv[a]+t*(vv[b]-vv[a])).astype(np.float32).astype(np.float64)
    cache[key]=len(vv);vv.append(pos);qq.append(level)
   return cache[key]
  def clip(poly,below):
   result=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    ina=qq[a]<=level if below else qq[a]>=level;inb=qq[b]<=level if below else qq[b]>=level
    if ina:result.append(a)
    if ina!=inb:result.append(cut(a,b))
   clean=[]
   for j in result:
    if not clean or j!=clean[-1]:clean.append(j)
   if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
   return clean
  for face,mat,flag in zip(ff,mm,flags):
   vals=[qq[i] for i in face]
   polys=[face] if min(vals)>=level or max(vals)<=level else [clip(face,True),clip(face,False)]
   for poly in polys:
    for j in range(1,len(poly)-1):outf.append([poly[0],poly[j],poly[j+1]]);outm.append(mat);outflags.append(flag)
  ff,mm,flags=outf,outm,outflags
 for i,(face,flag) in enumerate(zip(ff,flags)):
  if flag:
   x,y,z=np.mean([vv[j] for j in face],axis=0);q=np.mean([qq[j] for j in face]);opaque_street=(x<12 and 24<y<113)
   mm[i]=4 if q<-.001 else (2 if q<builder.p['main_band_height']-.001 and not opaque_street else 0)
 return np.asarray(vv,np.float32),np.asarray(ff,np.uint32),np.asarray(mm,np.int32)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().set_tolerance(.02).simplify(.02);assert s.status()==mf.Error.NoError,s.status();m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3].copy();f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32);main_faces=np.zeros(len(f),bool)
 for i,oid in enumerate(m.run_original_id):
  lo,hi=m.run_index[i]//3,m.run_index[i+1]//3;mi[lo:hi]=b.ids[int(oid)]
  if int(oid)==b.main_surface_id:main_faces[lo:hi]=True
 # Snap near-exact straight plan boundaries to a binary parameter grid before float32 STL.
 # This preserves their coplanarity under float export; max displacement is below 0.002 model mm.
 snap_max=0.0;snapped=0
 for boundary in [p['main_outline'],p['lower_core'],p['north_core']]:
  for aa,bb in zip(boundary,boundary[1:]+boundary[:1]):
   aa=np.asarray(aa,float);bb=np.asarray(bb,float);delta=bb-aa;den=float(delta@delta)
   tt=((v[:,:2]-aa)@delta)/den;proj=aa+tt[:,None]*delta
   mask=(tt>=0)&(tt<=1)&(np.linalg.norm(v[:,:2]-proj,axis=1)<1e-4)
   ids=np.where(mask)[0];ss=np.round(tt[ids]*p['straight_boundary_binary_snap_divisions'])/p['straight_boundary_binary_snap_divisions'];vv=aa+ss[:,None]*delta
   if len(ids):snap_max=max(snap_max,float(np.linalg.norm(v[ids,:2]-vv,axis=1).max()));snapped+=len(ids);v[ids,:2]=vv
 assert snap_max<.002
 v,f,mi=split_colour_bands(v,f,mi,main_faces,b)
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'nthu-jieying-museum.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  mm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(mm.vert_properties)[:,:3].tolist(),'faces':np.asarray(mm.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'export_straight_boundary_snap_max_mm':snap_max,'export_straight_boundary_snap_vertex_visits':snapped,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
