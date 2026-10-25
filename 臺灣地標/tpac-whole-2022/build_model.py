#!/usr/bin/env python3
"""Original normalized exterior interpretation; no source-image, tracing or network dependency.
All 'm' suffixes denote architectural-proportion units, not surveyed metres.
"""
import argparse,json,pathlib,math
import numpy as np
import trimesh,manifold3d as mf
from shapely.geometry import Polygon,LineString,Point,box as polybox
PALETTE=[
 {'id':'silver_metal','name':'Approximate silver metal','hex':'#BFC5C7','evidence':'OMA exterior photos 01,04,05,09,10,14; material family, not calibrated metal/paint specification'},
 {'id':'blue_grey_glass','name':'Opaque blue-grey corrugated glazing','hex':'#324C59','evidence':'OMA photos 01,04,05,10; opaque miniature convention, no photographic reflections'},
 {'id':'pale_frame','name':'Pale metal bands and supports','hex':'#D1D7D6','evidence':'OMA photos 01,04,05,10,14'},
 {'id':'charcoal_screen','name':'Charcoal rear service screens','hex':'#29323D','evidence':'OMA photos 03,05,06; not shadow-painted silver'},
 {'id':'roof_planting','name':'Muted roof planting','hex':'#71815A','evidence':'OMA photos 01,05,06,09; approximate garden areas'},
 {'id':'paving','name':'Pale roof paving and attached platforms','hex':'#B4B6AD','evidence':'OMA photos 01,05,06,09'},
 {'id':'blue_inset','name':'Grand Theater blue recessed opening','hex':'#245972','evidence':'OMA photos 03,04'},
 {'id':'mesh_stair','name':'Simplified neutral stair enclosure','hex':'#858C8C','evidence':'OMA photos 04,14; opaque miniature mesh approximation, no invented internal equipment'},
 {'id':'panel_seam','name':'Subtle metallic seams','hex':'#929DA2','evidence':'OMA photos 09,10,14; major visible panel organization generalized'},
 {'id':'display_base','name':'Neutral display support','hex':'#D3D2C9','evidence':'Authored neutral support, not terrain, road or architectural plinth'}]
def box(x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
def union(parts):return mf.Manifold.batch_boolean(parts,mf.OpType.Add)
def solid(poly,z0,z1):
 if poly.geom_type=='MultiPolygon':return union([solid(q,z0,z1)for q in poly.geoms])
 return mf.CrossSection([list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1]for r in poly.interiors],mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def hull(verts):
 t=trimesh.convex.convex_hull(verts);return mf.Manifold(mf.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32)))
def arc(cx,cy,rx,ry,a,b,n=81):return [(cx+rx*math.cos(t),cy+ry*math.sin(t))for t in np.linspace(math.radians(a),math.radians(b),n)]
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={}
 def add(self,n,m,mat=0,evidence='Actual exterior photos and 2022 official plan topology; normalized, approximate dimensions'):
  assert not m.is_empty(),n
  assert m.status()==mf.Error.NoError,(n,m.status())
  m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_normalized_units':list(m.bounding_box())})
 def box(self,n,x,y,z,mat=0):self.add(n,box(x,y,z),mat)
 def strip(self,n,path,w,z0,z1,mat=0):self.add(n,solid(LineString(path).buffer(w/2,cap_style=2,join_style=2),z0,z1),mat)
 def col(self,n,x,y,z0,z1,r=.38,mat=2):self.add(n,mf.Manifold.cylinder(z1-z0,r,r,16).translate([x,y,z0]),mat)
 def beam(self,n,a,b,r=.4,mat=2):
  aa=np.array(a,float);bb=np.array(b,float);d=bb-aa;length=np.linalg.norm(d);u=d/length;v=np.cross(u,[0,0,1])
  if np.linalg.norm(v)<.1:v=np.cross(u,[0,1,0])
  v/=np.linalg.norm(v);w=np.cross(u,v);matrix=np.column_stack([v,w,u,aa]);self.add(n,mf.Manifold.cylinder(length,r,r,16).transform(matrix.tolist()),mat)
 def ramp(self,name,cx,cy,rx,ry,a,b,z0,z1,width=3.0):
  pts=arc(cx,cy,rx,ry,a,b,65);zs=np.linspace(z0,z1,len(pts));segments=[];rails=[]
  for i in range(len(pts)-1):
   aa=np.array(pts[i]);bb=np.array(pts[i+1]);d=bb-aa;u=d/np.linalg.norm(d);v=np.array([-u[1],u[0]])
   # Small overlaps remove coincident seams between neighboring wedge solids.
   aa-=u*.025;bb+=u*.025
   verts=[]
   for q,z in [(aa,zs[i]),(bb,zs[i+1])]:
    for side in [-1,1]:
     xy=q+v*side*width/2
     verts.extend([[*xy,z-.5],[*xy,z]])
   segments.append(hull(verts))
   for side in [-1,1]:
    xy1=aa+v*side*(width/2-.12);xy2=bb+v*side*(width/2-.12)
    vv=[]
    for q,z in [(xy1,zs[i]),(xy2,zs[i+1])]:
     for w in [-.12,.12]:vv.extend([[*(q+v*w),z-.1],[*(q+v*w),z+.8]])
    rails.append(hull(vv))
  self.add(name+' curved descending deck',union(segments),5,'2022 2F plan + actual photos 05/06; ramp trajectory and height generalized, no accessibility compliance claim')
  self.add(name+' low parapet edges',union(rails),5)
  for i in [3,12,24,36,48,59]:
   if zs[i]>.8:self.col(name+' support '+str(i),*pts[i],-.04,zs[i]-.25,.28,5)
 def build(self):
  p=self.p;x0,x1,y0,y1=p['central_cube_xy'];z0,z1=p['central_envelope_z'];base=p['display_base_xy']
  self.add('Nonarchitectural neutral display support',box(base[:2],base[2:],(-p['display_base_thickness'],0)),9,'Display closure only. Not terrain, foundation, basement, roads or measured architectural plinth.')
  lobby=p['ground_lobby_xy'];self.box('Recessed ground lobby within open perimeter undercroft',lobby[:2],lobby[2:],(-.03,z0+.1),1)
  # The roof slot is genuinely recessed and open, not a dark painted rectangle.
  slot=p['roof_slot_xy'];core=box((x0,x1),(y0,y1),(z0,z1)) - box(slot[:2],slot[2:],(p['roof_slot_floor_z'],z1+2))
  self.add('Central raised corrugated-glass cube envelope with open roof slot',core,1)
  for i,z in enumerate(p['facade_bands_z']):
   ring=polybox(x0-.28,y0-.28,x1+.28,y1+.28).difference(polybox(x0+.15,y0+.15,x1-.15,y1-.15))
   self.add('Central pale horizontal facade band '+str(i),solid(ring,z-.12,z+.13),2)
  # Shallow attached semicylinders approximate waves; repetitions are reduced for miniature robustness.
  ribs=[]
  for t in np.arange(-24.5,24.51,1.05):
   for xx,yy in [(t,y0),(t,y1),(x0,t),(x1,t)]:ribs.append(mf.Manifold.cylinder(z1-z0,.22,.22,10).translate([xx,yy,z0]))
  self.add('Reduced repeating vertical corrugated glass wave relief',union(ribs),1,'Actual corrugated glass in photo 10; count and wave depth simplified')
  for i,(x,y)in enumerate([(-23,-23),(23,-23),(-23,7),(23,7),(-22,23),(22,23)]):self.col('Central undercroft visible support '+str(i),x,y,-.04,z0+.2,.46)
  # Globe retained as one connected truncated ellipsoid; the rear is swallowed by the cube.
  center=p['globe_center'];r=p['globe_radii'];ball=mf.Manifold.sphere(1,80).scale(r).translate(center)
  ball=ball ^ box((-30,30),(-60,-24.7),(0,60));self.add('Globe Playhouse intersecting ellipsoidal silver shell',ball,0,'Official 7F outline and actual photos 01/04/09/10; ellipsoid is a proportional exterior approximation, not measured shell')
  # Thin major seam ribbons lie on the connected outer shell; they are not source-image textures.
  shell=mf.Manifold.sphere(1,80).scale([q+.025 for q in r]).translate(center)-mf.Manifold.sphere(1,80).scale([q-.06 for q in r]).translate(center)
  seams=[]
  for rot in [(0,0,0),(0,0,60),(0,0,-60),(52,0,0),(-52,0,0)]:
   plane=box((-.055,.055),(-25,25),(-25,25)).rotate(rot).translate(center);seams.append(shell^plane^box((-30,30),(-60,-24.65),(0,60)))
  self.add('Globe generalized major metallic panel seams',union(seams),8)
  for i,s in enumerate([-1,1]):self.beam('Globe inclined support '+str(i),[s*13,-42,-.06],[s*10,-34,17],.67,2)
  # Grand Theater: asymmetric footprint, independently higher roof and sloping/faceted soffit.
  verts=[[*xy,z]for xy,z in zip(p['grand_xy'],p['grand_bottom_z'])]+[[*xy,p['grand_top_z']]for xy in p['grand_xy']]
  grand=hull(verts);cut=box((-59.2,-57.7),(-10,16.5),(20.0,23.2));grand=grand-cut;self.add('Grand Theater flared polygon with sloping soffit',grand,0)
  self.box('Grand Theater long deep blue recessed opening',(-57.85,-57.65),(-9.7,16.2),(20.18,23.03),6)
  # Darker narrow opening back and pale inside sill remain actual 3D recess.
  self.box('Grand Theater inset sill',(-58.2,-57.6),(-9.8,16.3),(20.05,20.25),2)
  for y in [-9,-4,1,6,11,16]:self.box('Grand inset window division '+str(y),(-57.9,-57.6),(y-.07,y+.07),(20.15,23.1),2)
  for i,y in enumerate([-8,15]):self.beam('Grand Theater inclined ground support '+str(i),[-48,y,-.06],[-42,y,13],.75,2)
  # Mesh-clad stair volume seen in photograph 14: solid stylized enclosure with external rhythm.
  stair=hull([[-57,-13,-.05],[-51,-13,-.05],[-51,-8,-.05],[-57,-8,-.05],[-49,-13,18],[-43,-13,18],[-43,-8,18],[-49,-8,18]])
  self.add('Grand Theater inclined mesh stair enclosure',stair,7,'Actual low-angle photo 14; exterior mesh represented opaquely, hidden internal stairs not reconstructed')
  for i in range(7):
   z=1+i*2.6;x=-56+8*z/18;self.strip('Grand stair visible pale diagonal rhythm '+str(i),[(x,-13.02),(x+4.8,-13.02)],.16,z,z+.2,2)
  # Blue Box is intentionally neither a copy nor a mirror of Grand Theater.
  bb=p['blue_xy'];bz=p['blue_z'];self.box('Blue Box distinct rectangular metallic theater',bb[:2],bb[2:],bz,0)
  connector=hull([[25,17,11],[34,17,12],[34,25.2,10],[25,25.2,9],[25,17,18],[34,17,18],[34,25.2,15],[25,25.2,19]])
  self.add('Blue Box faceted rear connector extrusion',connector,0,'Photos 05/06 irregular projection beside rear dark screen')
  for i,(x,y) in enumerate([(43,-2),(43,17)]):self.col('Blue Box ground support '+str(i),x,y,-.05,8.4,.68,2)
  # Lower garden terrace: paved circular spaces on planted field, low parapet and three inset plates.
  self.roof_garden('Blue Box lower roof terrace',(25.2,52.7,-7.7,22.7),28.5,lower=True)
  # Central planted roof with visible braced slot and open railing/parapet boundary.
  roofpoly=polybox(-24.65,-24.65,24.65,24.65).difference(polybox(*[slot[0],slot[2],slot[1],slot[3]]))
  self.add('Central roof pale paved field around open slot',solid(roofpoly,51.94,52.13),5)
  self.roof_garden('Central main roof',(-12.3,24.2,-24.2,24.2),52,lower=False)
  self.box('Open roof slot recessed visible floor',slot[:2],slot[2:],(43.65,43.85),7)
  self.beam('Open roof slot long diagonal brace A',[-22.7,-22,51.7],[-13.3,22.5,51.7],.35,2)
  self.beam('Open roof slot long diagonal brace B',[-22.7,22.5,51.7],[-13.3,-22,51.7],.35,2)
  for x in [-23.3,-12.7]:self.strip('Roof slot pale upper edge '+str(x),[(x,-23),(x,23.4)],.28,51.9,52.3,2)
  # Rear two open-topped tall screens, central connecting face at three distinct setbacks/heights.
  sy=p['rear_screen_y'];sz=p['rear_screen_z']
  for i,sx in enumerate(p['rear_screen_x']):
   tower=box(sx,sy,sz)-box((sx[0]+1.0,sx[1]-1.0),(sy[0]+1.0,sy[1]-1.0),(51.7,sz[1]+.1))
   self.add('Rear screen tall open-top end tower '+str(i),tower,3)
   # Sparse relief represents screen rhythm, not false exact perforation counts.
   for j,x in enumerate(np.arange(sx[0]+.5,sx[1]-.3,.85)):
    self.box('Rear tower subtle vertical screen rib '+str(i)+' '+str(j),(x-.055,x+.055),(37.45,37.62),(5,54.9),3)
  self.box('Rear recessed upper central service connector',(-8.7,8.7),(24.5,31.4),(4,52.2),3)
  self.box('Rear stepped mid-level connecting screen',(-8.7,8.7),(31.0,35.4),(4,35.5),3)
  self.box('Rear low projecting central screen',(-8.7,8.7),(35.0,37.5),(4,18.5),3)
  for i,x in enumerate([-21,-12,12,21]):self.box('Rear service support '+str(i),(x-.45,x+.45),(29,30),(-.03,4.2),3)
  # Attached raised platform with two curved end ramps. A neutral thin base does not fill gaps.
  self.box('Rear attached raised platform',(-58,55),(37.0,44.5),(3.1,3.6),5)
  for i,x in enumerate(np.arange(-55,55,7)):
   self.col('Rear platform ground support '+str(i),float(x),42,-.04,3.4,.31,5)
  # Straight short side connections join the loop tops to the platform.
  self.ramp('Grand side attached curved ramp',-49,26,12,10,90,415,3.6,.18,3.0)
  self.ramp('Blue side attached curved ramp',44,26,12,11,90,-235,3.6,.18,3.0)
  return union(self.items)
 def roof_garden(self,name,rect,z,lower=False):
  xa,xb,ya,yb=rect
  if lower:self.box(name+' complete paved roof field',(xa,xb),(ya,yb),(z-.06,z+.13),5)
  field=polybox(xa+.5,ya+.5,xb-.5,yb-.5)
  if lower:
   circles=[(40,9,7.2),(30.5,-3,3.2),(49,18,3.0)];paths=[[(28,21),(40,9),(31,-3)],[(40,9),(51,-4)]]
  else:
   circles=[(8,-15,5.4),(16,12,5.1),(-5,16,4.5)];paths=[[(8,-15),(16,12),(-5,16)],[(-10,-22),(8,-15),(-4,23)],[(8,-15),(23,-23)]]
  paved=union([]) if False else None
  cut=Point(circles[0][0],circles[0][1]).buffer(circles[0][2],quad_segs=32)
  for x,y,r in circles[1:]:cut=cut.union(Point(x,y).buffer(r,quad_segs=32))
  for line in paths:cut=cut.union(LineString(line).buffer(.62,cap_style=2,join_style=2))
  garden=field.difference(cut);self.add(name+' planted field',solid(garden,z+.03,z+.32),4,'Actual roof photos 01/05/06/09; simplified visible planted/paved topology, no hidden roof services')
  self.add(name+' circular paving and connecting paths',solid(cut.intersection(field),z+.02,z+.20),5)
  # Exact miniature parapet instead of unsupported thin handrail objects.
  rim=polybox(xa,ya,xb,yb).difference(polybox(xa+.28,ya+.28,xb-.28,yb-.28))
  self.add(name+' low perimeter parapet',solid(rim,z-.06,z+.8),2)
  if lower:
   for i in range(3):self.box(name+' visible inset plate '+str(i),(48,50),(-4+i*4,-1.5+i*4),(z+.21,z+.36),7)

def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().set_tolerance(.002).simplify(.002);assert s.status()==mf.Error.NoError,s.status()
 mm=s.scale([p['model_mm_per_m']]*3).to_mesh();s=mf.Manifold(mm).set_tolerance(.004).simplify(.004);closed=s.decompose();filled=len([q for q in closed if q.volume()<=0]);s=union([q for q in closed if q.volume()>0]);s=mf.Manifold(s.to_mesh()).set_tolerance(.005).simplify(.005);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):mi[mm.run_index[i]//3:mm.run_index[i+1]//3]=b.ids[int(oid)]
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(np.round(v,4),dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.009).simplify(.009);cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts)
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'tpac-whole-2022.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();parts.append({'name':op['name'],'vertices':(np.asarray(m.vert_properties)[:,:3]*p['model_mm_per_m']).tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'non_visible_closed_cavities_filled_for_exterior_print':filled,'float_export_resimplification_tolerances_mm':[.004,.005,.009],'float_vertex_quantization_mm':.0001,'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
