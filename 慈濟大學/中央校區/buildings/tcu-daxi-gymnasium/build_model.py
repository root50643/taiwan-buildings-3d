#!/usr/bin/env python3
"""Original whole pre-PV exterior. Procedural colours; no copied photo pixels."""
import argparse,json,pathlib
import numpy as np
import trimesh
import manifold3d as mf
PALETTE=[
 {'id':'wall','name':'Light warm-neutral architectural body','hex':'#CDCBC1','evidence':'Architect exterior and university S1; approximate, not calibrated stone specification'},
 {'id':'ledge','name':'Neutral grey trim and recessed backing','hex':'#AFB2AE','evidence':'Photographed ledges and recesses; shadows computed by lighting'},
 {'id':'glass','name':'Restrained grey-blue opaque glazing','hex':'#52656B','evidence':'Glazed windows, including road-side arched windows; opaque printable exterior representation'},
 {'id':'frame','name':'Pale window frames and slim metal supports','hex':'#C9D0CE','evidence':'Photographed pale frames; exact sections and divisions simplified'},
 {'id':'roof','name':'Pale silver roof and entrance canopy','hex':'#E4E6E1','evidence':'Early bare roof and architect entrance canopy, uncalibrated'},
 {'id':'rooflight','name':'Neutral rooflight side glazing','hex':'#8B9EA1','evidence':'S1 and interior roof view, raised longitudinal narrow rooflight'},
 {'id':'paving','name':'Authored light-grey base and steps','hex':'#B8BAB4','evidence':'Manufacturing/presentation base; not reconstructed terrain'},
 {'id':'roof_surface','name':'Muted roof terrace surface','hex':'#A1A6A1','evidence':'Broad low-wing roof terraces, little equipment deliberately omitted'},
]
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.low_wing_phase=False
 def add(self,n,s,mat=0,evidence='Photo-grounded feature family; independently estimated proportions'):
  if self.low_wing_phase:s=s.translate([0,-40,0]).scale([1,self.p['low_wing_fitted_depth']/self.p['low_wing_reference_depth'],1]).translate([0,40,0])
  s=s.as_original();self.ids[int(s.original_id())]=mat;self.items.append(s);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(s.bounding_box())})
 def cube(self,x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
 def box(self,n,x,y,z,mat=0,evidence='Photographed feature family; dimensions approximate'):self.add(n,self.cube(x,y,z),mat,evidence)
 def xsolid(self,poly,x):
  # Cross-section coordinates are (longitudinal Y, vertical Z), extruded along X.
  return mf.CrossSection([poly],mf.FillRule.EvenOdd).extrude(x[1]-x[0]).rotate([90,0,90]).translate([x[0],0,0])
 def ysolid(self,poly,y):
  # Cross-section coordinates are (X,Z); flip extrusion to +Y without mirroring X.
  return mf.CrossSection([poly],mf.FillRule.EvenOdd).extrude(y[1]-y[0]).rotate([90,0,0]).translate([0,y[1],0])
 def archpoly(self,c,base,spring,r,rise=None):
  if rise is None:rise=r
  return [(c-r,base),(c+r,base)]+[(float(c+r*np.cos(t)),float(spring+rise*np.sin(t)))for t in np.linspace(0,np.pi,21)]
 def column(self,n,x,y,z,r,mat=0):self.add(n,mf.Manifold.cylinder(z[1]-z[0],r,r,24).translate([x,y,z[0]]),mat)
 def sidewindow(self,n,side,y,z,w=6.7,base_x=None,arch=False):
  x=base_x if base_x is not None else side*38
  xr=(x-.14,x+.26)if side>0 else(x-.26,x+.14)
  if arch:self.add(n,self.xsolid(self.archpoly(y,z[0],z[1]-w*.27,w/2,w*.27),xr),2)
  else:self.box(n,xr,(y-w/2,y+w/2),z,2)
  # Attached frame relief, not freestanding sub-nozzle walls.
  front=x+.3*side;self.box(n+' centre mullion',(min(x,front)-.05,max(x,front)+.05),(y-.22,y+.22),(z[0],z[1]-.1),3)
  if arch:self.box(n+' arched transom',(min(x,front)-.05,max(x,front)+.05),(y-w/2,y+w/2),(z[1]-w*.27-.18,z[1]-w*.27+.18),3)
  if z[1]-z[0]>6:self.box(n+' body transom',(min(x,front)-.05,max(x,front)+.05),(y-w/2,y+w/2),(z[0]+(z[1]-z[0])*.42-.18,z[0]+(z[1]-z[0])*.42+.18),3)
  self.box(n+' lower sill',(min(x,front)-.10,max(x,front)+.10),(y-w/2-.25,y+w/2+.25),(z[0]-.4,z[0]),1)
 def build(self):
  p=self.p;b=p['display_base'];self.box('Display-only base',b[:2],b[2:4],b[4:],6,'Original presentation/manufacturing aid, no surveyed ground claim')
  # Hall silhouette; a neutral solid interior is a manufacturing closure, not a room model.
  self.box('Whole high hall lower body',(-31,38),(-100,40),(2.9,28),0)
  self.box('High hall core behind upper galleries',(-31,31),(-100,40),(27.9,44.2),0)
  self.box('High hall complete upper wall band',(-38,38),(-100,40),(44,61.2),0)
  for side in [-1,1]:
   x=(-38,-30.9)if side<0 else(30.9,38)
   for yy in [(-100,-90),(19,40)]:self.box(f'{side} gallery solid end return {yy}',x,yy,(27.8,44.2),0)
  # Track-side lower arcade: perforated actual wall in front of a set-back closed interior.
  front=self.cube((-38,-30.8),(-100,40),(6.7,27.9))
  for cy in p['arcade_centers_y']:
   front=front-self.xsolid(self.archpoly(cy,6.6,p['arcade_spring_z'],p['arcade_opening_half_width']),(-38.2,-30.6))
  self.add('Track-side real open arched arcade wall',front,0,'Architect 009/011 show real open bays, with recessed backing; not a painted dark wall')
  self.box('Track arcade raised apron',(-40.5,-30.5),(-100.5,40.5),(2.9,7),6)
  for i in range(4):self.box(f'Track apron step {i+1}',(-44+i,-40+i*.05),(-97,32),(2.9,3.8+i*.8),6)
  # Differing ground zones: road lower windows stay exposed behind low roofs.
  for cy in p['arcade_centers_y']:
   self.sidewindow(f'Road arched CLOSED glazing {cy}',1,cy,(14,25),w=7,arch=True)
   self.sidewindow(f'Road low rectangular CLOSED glazing {cy}',1,cy,(5.5,10.1),w=7.5)
   self.sidewindow(f'Track arcade recessed rear window {cy}',-1,cy,(8,16.8),w=5.8,base_x=-31)
  for cy in [22,27,32,37]:
   for side in [-1,1]:
    self.sidewindow(f'NE hall projection large rectangular glazing {side} {cy}',side,cy,(15,25.3),w=3.8)
    self.sidewindow(f'NE hall projection low rectangular glazing {side} {cy}',side,cy,(5.5,10.1),w=3.8)
    self.sidewindow(f'NE hall projection tall upper glazing {side} {cy}',side,cy,(33,51.5),w=3.1)
  # Open upper recessed galleries with real round columns; both sides evidenced.
  for side in [-1,1]:
   xr=(-39,-30.5)if side<0 else(30.5,39)
   self.box(f'{side} upper gallery floor ledge',xr,(-99.8,39.8),(27,29),1)
   self.box(f'{side} upper gallery low solid parapet',(-38.3,-37.3)if side<0 else(37.3,38.3),(-90,19),(28.8,30.0),0)
   for cy in p['upper_column_y']:
    self.column(f'{side} upper round gallery column {cy}',side*36.5,cy,(28.9,44.2),1.25)
    self.column(f'{side} upper column capital {cy}',side*36.5,cy,(43.4,44.2),1.6,1)
   for cy in np.arange(-84,18,9):self.sidewindow(f'{side} set-back upper gallery arched window {cy}',side,float(cy),(31.5,39.7),w=5.6,base_x=side*31,arch=True)
   for cy in np.arange(-82,17,16):self.sidewindow(f'{side} upper short horizontal window {cy}',side,float(cy),(48.5,52.5),w=13.3)
   self.box(f'{side} deep eave glazed ventilation ribbon',(-38.2,-37.85)if side<0 else(37.85,38.2),(-97,37),(57.5,61.2),2)
   for cy in np.arange(-96,38,6):self.box(f'{side} eave ribbon mullion {cy}',(-38.35,-37.8)if side<0 else(37.8,38.35),(cy-.2,cy+.2),(57.5,61.2),3)
   self.box(f'{side} eave ribbon lower ledge',(-39,-37.8)if side<0 else(37.8,39),(-100.4,40.4),(56.8,57.6),1)
  # Central track entrance canopy interrupts the arcade rather than the entire facade.
  self.box('Track central low entrance canopy',(-46.5,-30.7),(-41,-16),(22.4,24.2),0)
  for cy in [-39,-18]:self.column(f'Track entrance canopy column {cy}',-44.5,cy,(6.7,22.6),.9,1)
  # Southwest end remains mostly solid, sparse window groups and tall corner glazing.
  for x in [-11,-3,5]:
   for zz in [(20,25.5),(39,44.5)]:self.box(f'SW sparse end glazing {x} {zz}',(x-2.5,x+2.5),(-100.25,-99.8),zz,2)
  for side in [-1,1]:
   xr=(-38.26,-37.8)if side<0 else(37.8,38.26)
   self.box(f'SW {side} long-facade tall glazed corner strip',xr,(-99.3,-93.3),(7.5,58),2,'Architect southwest corner and 2013 roadside southwest capture; tall glazed corner rather than mirrored arcade')
   for z in np.arange(9,58,4):self.box(f'SW {side} corner strip transom {z}',(-38.45,-37.8)if side<0 else(37.8,38.45),(-99.4,-93.2),(z,z+.35),3)
  # Broad main roof is separate from the NARROW longitudinal curved rooflight.
  ys=np.linspace(-102,42,49);shape=[(float(y),float(p['hall_roof_z']+p['hall_roof_rise']*(1-((y+30)/72)**2)))for y in ys]
  self.add('Broad shallow main roof envelope',self.xsolid([(-102,61), (42,61)]+list(reversed(shape)),(-40.5,40.5)),4,'Broad roof/eave rectangle, shallow photo-fit rise; NOT a full-width barrel vault')
  y0,y1=p['rooflight_y'];ys=np.linspace(y0,y1,65);mid=(y0+y1)/2;half=(y1-y0)/2
  curve=[(float(y),float(p['rooflight_end_z']+p['rooflight_rise']*(1-((y-mid)/half)**2)))for y in ys];rw=p['rooflight_half_width']
  self.add('Narrow raised longitudinal rooflight glazed body',self.xsolid([(y0,63.9),(y1,63.9)]+[(y,z-p['rooflight_thickness']+.15)for y,z in reversed(curve)],(-rw+.6,rw-.6)),5,'Long narrow central rooflight; side profile curvature estimated from S1 and bare roof')
  self.add('Narrow raised pale curved rooflight cap',self.xsolid([(y,z-p['rooflight_thickness'])for y,z in curve]+list(reversed(curve)),(-rw,rw)),4)
  for cy in np.linspace(y0+3,y1-3,22):
   top=p['rooflight_end_z']+p['rooflight_rise']*(1-((cy-mid)/half)**2)
   for side in [-1,1]:self.box(f'Rooflight attached side mullion {side} {cy:.3f}',(side*(rw-.6)-.20,side*(rw-.6)+.20),(cy-.24,cy+.24),(64.3,top-.3),3)
  # Joined low northeast wing. Two floors, deep OPEN entrance portico, stepped roof masses.
  self.low_wing_phase=True
  self.box('Joined low entrance wing ground core',(-38,38),(39.9,84),(2.9,25),0)
  self.box('Low wing upper floor and facade',(-38,38),(39.9,95),(24.7,37.5),0)
  self.box('Low wing front portico raised platform',(-39,39),(83.5,96),(2.9,7),6)
  for x in [-33,-13,13,33]:
   self.column(f'Entrance deep portico round column {x}',x,92,(6.9,25.1),1.35)
   self.column(f'Entrance portico capital {x}',x,92,(24,25.3),1.7,1)
  for x in [-29,-20,20,29]:
   self.box(f'Entrance recessed ground window {x}',(x-3,x+3),(83.8,84.3),(9,17.5),2)
   self.box(f'Entrance ground window transom {x}',(x-3,x+3),(84.2,84.55),(13,13.45),3)
  self.box('Entrance recessed central doors',(-11,11),(83.8,84.3),(7,22.2),2)
  for x in [-8,-4,0,4,8]:self.box(f'Entrance door division {x}',(x-.18,x+.18),(84.1,84.65),(7,22.3),3)
  for x in [-31,-25,25,31]:
   self.box(f'Front upper rectangular glazing {x}',(x-2.4,x+2.4),(94.8,95.2),(28,33.4),2)
   self.box(f'Front upper glazing transom {x}',(x-2.45,x+2.45),(95.1,95.4),(29.5,29.9),3)
  for side in [-1,1]:
   for cy in [46,57,68,79,88]:
    self.sidewindow(f'Low wing upper side window {side} {cy}',side,cy,(28,33.4),w=7)
    if cy<82:self.sidewindow(f'Low wing lower side window {side} {cy}',side,cy,(9,18),w=7)
  # Tiered roof terraces have a roof-level set-back mass, not an open ground-depth court.
  self.box('Low wing perimeter roof fascia',(-39.5,39.5),(39,96),(37.2,38.8),1)
  self.box('Low wing perimeter roof surface',(-38.8,38.8),(39.8,95.3),(38.6,38.9),7)
  self.box('Low wing central higher roof-level mass',(-24,24),(51,84),(38.7,44),0)
  self.box('Low wing higher roof pale cornice',(-25.5,25.5),(49.8,85.3),(43.5,44.9),4)
  self.box('Low wing higher roof neutral flat surface',(-24.5,24.5),(50.8,84.3),(44.8,45.1),7)
  # Curved name canopy is original geometry; fine sign text intentionally omitted.
  xx=np.linspace(-21.5,21.5,49);tops=[(float(x),float(28.3+6.4*(1-(x/21.5)**2)))for x in xx]
  self.add('Entrance curved pale name canopy',self.ysolid([(-21.5,26.6),(21.5,26.6)]+list(reversed(tops)),(94.7,99)),4,'Architect 008/010; sign text omitted rather than copying source pixels; shallow solid backing is a print adaptation')
  for i in range(8):self.box(f'Central entrance step {i+1}',(-15,15),(95.8,106-i*1.25),(2.9,3.5+(i+1)*.44),6)
  self.add('Side entrance rising ramp',self.ysolid([(-16,3),(-47,3),(-47,3.7),(-16,7)],(97,103)),6)
  self.add('Side entrance ramp thickened parapet',self.ysolid([(-16,6.5),(-47,3.25),(-47,5.1),(-16,8.4)],(102.2,103.1)),0)
  # External track-side stair at the real joining zone; preserve daylight beneath flight.
  # Y=37 is upper landing, Y=66 lower; 24 treads on a thin inclined slab.
  self.add('Track joining external stair inclined slab',self.xsolid([(37,23),(66,5.5),(66,7),(37,24.5)],(-47,-40)),1)
  for i in range(24):
   yy=37+i*29/24;top=24.5-i*17.5/24
   self.box(f'Track joining stair tread {i+1}',(-47.2,-39.8),(yy,yy+29/24+.02),(top-1.5,top+.18),6)
  self.box('Track stair upper landing connected to joined wing',(-47.2,-30.8),(34,39),(23.5,25),6)
  self.column('Track stair landing support',-44,36,(3,24),.9,1)
  for x in [-47,-40]:self.add(f'Track stair thickened parapet {x}',self.xsolid([(37,24),(66,6.5),(66,9),(37,26.5)],(x-.45,x+.45)),0,'Stair edge railing simplified as low solid ribbon for small-scale printing')
  # Open roadside double parking shelter, integral part of the bounded exterior scope.
  self.low_wing_phase=False
  z=p['canopy_roof_z'];y0,y1=p['canopy_y']
  for n,xr in [('inner',p['canopy_inner_x']),('outer',p['canopy_outer_x'])]:
   self.box(f'Road {n} thin parking canopy roof',xr,(y0,y1),(z,z+p['canopy_roof_thickness']),4,'Two source-confirmed low OPEN roof strips; no enclosed annex. Near-wall connection is a print simplification, not asserted fastening')
   for x in ([45.2]if n=='inner'else[51.8,59.2]):
    for cy in np.linspace(y0+1,y1-1,10):self.column(f'Road {n} slender canopy support {x} {cy:.3f}',x,float(cy),(2.9,z+.1),p['canopy_post_radius'],3)
   # Beam edge under roof; the whole under-roof interval is otherwise free air.
   self.box(f'Road {n} canopy slender longitudinal edge beam',(xr[1]-.8,xr[1]),(y0,y1),(z-.8,z+.1),3)
  return mf.Manifold.batch_boolean(self.items,mf.OpType.Add)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().simplify(.001);assert s.status()==mf.Error.NoError,s.status();m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=b.ids[int(oid)]
 # Resolve exact float32-coordinate coincidences introduced at coplanar colour seams.
 # This changes no vertex coordinate; zero-area collapsed facets carry no surface.
 original_v=len(v);original_f=len(f);v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
 keep=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>2e-9;f=f[keep];mi=mi[keep]
 t=trimesh.Trimesh(v,f,process=False);assert t.is_watertight and t.is_winding_consistent;t.export(out/'tcu-daxi-gymnasium.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  mm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(mm.vert_properties)[:,:3].tolist(),'faces':np.asarray(mm.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'exact_coordinate_welds':original_v-len(v),'zero_area_seam_facets_removed':original_f-len(f),'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
