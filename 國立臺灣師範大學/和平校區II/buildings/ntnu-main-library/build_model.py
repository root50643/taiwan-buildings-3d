#!/usr/bin/env python3
"""Original whole exterior approximation; no photographic textures or surveyed dimensions."""
import argparse,json,pathlib
import numpy as np
import trimesh
import manifold3d as mf
PALETTE=[
 {'id':'brick','name':'Warm muted brick family','hex':'#B07864','evidence':'2025 official repaired north facade and 2025 south photographs; approximate uncalibrated colour'},
 {'id':'brick_edge','name':'Brick ledges and returns','hex':'#956552','evidence':'Observed horizontal brick edge articulation; approximate colour'},
 {'id':'glazing','name':'Opaque dark grey glazing','hex':'#3D4A50','evidence':'Observed dark horizontal glazing; opaque exterior representation, not interior glass simulation'},
 {'id':'mullions','name':'Neutral metal window divisions','hex':'#7A807D','evidence':'Photographed window divisions; spacing and count simplified'},
 {'id':'roof','name':'Neutral weatherproof roof','hex':'#656969','evidence':'Roof mosaic and high-angle photograph; not calibrated roof coating'},
 {'id':'skylight','name':'Pale roof caps','hex':'#D9D0B7','evidence':'Covered atrium cap array in aerial and high-angle images; exact count and profiles simplified'},
 {'id':'wood','name':'Eastern bookstore gate timber family','hex':'#6B4B38','evidence':'NLPI photograph supplied by NTNU Press; simplified gate only at east lower pocket'},
 {'id':'west_backing','name':'West pocket neutral backed closure','hex':'#555552','evidence':'Diagram-bounded west pocket; exact hidden closure material and glazing plane unknown'},
 {'id':'soffit','name':'Pale lower-entry soffit','hex':'#D3C9B4','evidence':'Official 2025 north lower-entry view; approximate colour'},
 {'id':'plinth','name':'Authored neutral display plinth','hex':'#B5B6AD','evidence':'Display-only aid, not surveyed pavement or terrain'},
]
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={}
 def add(self,n,s,mat=0,evidence='Source-grounded form, independently simplified proportions'):
  s=s.as_original();self.ids[int(s.original_id())]=mat;self.items.append(s);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(s.bounding_box())})
 def box(self,n,x,y,z,mat=0,evidence='Photographed feature family; dimensions and details approximate'):
  self.add(n,mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]]),mat,evidence)
 def prism(self,n,poly,z,mat=0,evidence='Nonmetric diagrams plus actual exterior photographs; not an as-built outline'):
  self.add(n,mf.CrossSection([poly],mf.FillRule.EvenOdd).extrude(z[1]-z[0]).translate([0,0,z[0]]),mat,evidence)
 def arc(self,r,a=0,b=180,cy=None,n=None):
  if cy is None:cy=self.p['arc_center_y']
  if n is None:
   degrees=np.unique(np.r_[a,np.linspace(0,180,self.p['curve_segments']+1),b]);degrees=degrees[(degrees>=a)&(degrees<=b)]
  else:degrees=np.linspace(a,b,n+1)
  return [(float(r*np.cos(t)),float(cy+r*np.sin(t)))for t in np.deg2rad(degrees)]
 def band(self,n,rin,rout,z,mat,a=0,b=180,cy=None):self.prism(n,self.arc(rout,a,b,cy)+list(reversed(self.arc(rin,a,b,cy))),z,mat)
 def footprint(self,lower=False):
  p=self.p;r=p['radius'];a,b=p['lower_north_recess_degrees'];c=self.arc(r,0,a)+self.arc(p['lower_north_radius'],a,b)+self.arc(r,b,180)if lower else self.arc(r)
  return c+[(-r,p['south_y']),(r,p['south_y'])]
 def build(self):
  p=self.p;r=p['radius'];g=p['ground_z'];z2=p['second_floor_z'];zu=p['upper_body_z'];roof=p['roof_z']
  base=p['display_base'];self.box('Display-only plinth',base[:2],base[2:4],base[4:],9,'Authored display base, not building footprint or surveyed site')
  low=mf.CrossSection([self.footprint(True)],mf.FillRule.EvenOdd).extrude(z2-g).translate([0,0,g])
  for key in ['west_pocket','east_pocket']:
   x0,x1,y0,y1,z0,z1=p[key];cut=mf.Manifold.cube([x1-x0,y1-y0+.5,z1-z0+.2]).translate([x0,y0-.5,z0-.1]);low=low-cut
  self.add('1F whole lower mass with two separate south backed recesses',low,0,'1F current and 2020 reverse axonometrics constrain closed pockets; actual 2025 south shell establishes relation to upper bar')
  self.prism('2F continuous south bar and recessed north entry envelope',self.footprint(True),(z2-.1,zu+.1),0)
  self.prism('3F-8F complete D-shaped upper exterior',self.footprint(),(zu,roof),0)
  # The tall terminal masses are part of the whole D-shaped building, not nearby buildings.
  for side,x in [('East',(79,100)),('West',(-100,-79))]:
   self.box(side+' full-height terminal core pier',x,(-44,4),(g-.1,p['end_pier_top_z']),0)
   self.box(side+' narrow raised edge pier',(x[0],x[0]+3)if side=='East'else(x[1]-3,x[1]),(-44,8),(g-.1,p['end_pier_top_z']+.5),0)
   self.box(side+' terminal roof surface',x,(-44,4),(p['end_pier_top_z']-.1,p['end_pier_top_z']+.25),4)
  # Six upper window ribbons above the low two-storey entry composition.
  for k,(z0,z1)in enumerate(p['upper_windows'],3):
   self.band(f'North curved floor {k} glazing',r-.15,r+.22,(z0,z1),2,5,175)
   self.band(f'North floor {k} lower brick ledge',r-.1,r+.65,(z0-.9,z0),1,5,175)
   for j,deg in enumerate(np.linspace(6,174,p['curved_mullion_count']+1)):
    # Fixed angle sectors share the exact polygonization of each feature; union resolves attachment.
    self.band(f'North floor {k} mullion {j+1}',r+.12,r+.48,(z0,z1),3,float(deg-.11),float(deg+.11))
   self.box(f'South floor {k} glazing',(-77,77),(-42.24,-41.85),(z0,z1),2)
   self.box(f'South floor {k} lower brick ledge',(-78,78),(-42.6,-41.85),(z0-.9,z0),1)
   for j,x in enumerate(np.linspace(-76,76,p['rear_mullion_count']+1)):
    self.box(f'South floor {k} mullion {j+1}',(x-.22,x+.22),(-42.49,-42.13),(z0,z1),3)
  # Low north entrance: central recess and returns, never a punched through exterior tunnel.
  a,b=p['lower_north_recess_degrees'];rr=p['lower_north_radius']
  self.band('North central second-floor set-back glazing',rr-.15,rr+.2,(23,34.7),2,a+.5,b-.5)
  self.band('North recessed lower entrance doors and side glazing',rr-.15,rr+.2,(5,16),2,69,111)
  for j,deg in enumerate(np.linspace(a+1,b-1,17)):
   self.band(f'North lower-entry mullion {j+1}',rr+.12,rr+.45,(23,34.7),3,float(deg-.13),float(deg+.13))
  for j,deg in enumerate(np.linspace(70,110,9)):
   self.band(f'North ground-entry door division {j+1}',rr+.1,rr+.42,(5,16),3,float(deg-.13),float(deg+.13))
  for side,aa,bb in [('East',6,a-.5),('West',b+.5,174)]:
   self.band(side+' northern second-floor wing glazing',r-.15,r+.2,(23,34.7),2,aa,bb)
   for j,deg in enumerate(np.linspace(aa+1,bb-1,10)):
    self.band(f'{side} second-floor mullion {j}',r+.12,r+.42,(23,34.7),3,float(deg-.13),float(deg+.13))
  self.band('North pale recess soffit underside',rr-.1,r+.05,(35.8,36.15),8,a+.2,b-.2)
  # Both rear pockets terminate in backing, below the continuous 2F bar.
  x0,x1,y0,y1,z0,z1=p['west_pocket'];self.box('West lower pocket neutral backed boundary',(x0+.05,x1-.05),(y1-.2,y1+.2),(g+.05,z2-.05),7,'Coarse bounded neutral closure; not an assertion of observed brick or exact glazing')
  x0,x1,y0,y1,z0,z1=p['east_pocket'];self.box('East bookstore set-back glazed closure',(x0+.15,x1-.15),(y1-.22,y1+.18),(g+.3,z2-.7),2)
  for x in [x0+2,(x0+x1)/2,x1-2]:self.box('East bookstore closure mullion '+str(x),(x-.35,x+.35),(y1-.48,y1+.1),(g+.3,z2-.6),3)
  # Gate is seen only at east. Its coarse rails overlap pocket side returns and upper bar.
  for x in [x0+.2,x1-.2]:self.box('East timber gate jamb '+str(x),(x-1.1,x+1.1),(y0-.55,y0+1.4),(g-.1,z2-.2),6)
  self.box('East timber gate header',(x0-1,x1+1),(y0-.9,y0+1.4),(z2-2.4,z2+.2),6)
  for xx in [(x0+.3,x0+9),(x1-9,x1-.3)]:self.box('East timber gate side screen '+str(xx),xx,(y0-.35,y0+.65),(g+.4,z2-2.2),6)
  # Topology: a closed roof-level atrium lid, never an open exterior court or deep dropped roof.
  self.prism('Whole D-shaped neutral roof surface',self.footprint(),(roof-.15,roof+.12),4)
  self.band('Outer curved brick roof parapet',r-2.2,r+.1,(roof-.1,roof+2.4),0)
  self.box('South upper bar brick roof edge',(-80,80),(-42.1,-39.9),(roof-.1,roof+2.4),0)
  ar=p['covered_atrium_radius'];acy=p['covered_atrium_center_y'];az=p['covered_atrium_roof_z']
  # A shallow added lid remains at roof level; body below is intentionally solid exterior abstraction.
  self.prism('Covered atrium closed semicircular roof',self.arc(ar,0,180,acy)+[(ar,acy)],(roof-.05,az),4,'Aerial, high-angle and interior roof corroboration; roof heights qualitative')
  self.band('Covered atrium low roof rim',ar-1,ar+1,(az-.35,az+.65),1,0,180,acy)
  self.box('Covered atrium straight rim',(-ar,ar),(acy-.8,acy+.8),(az-.35,az+.65),1)
  caps=0
  for radius,count in zip(p['skylight_ring_radii'],p['skylight_ring_counts']):
   for deg in np.linspace(8,172,count):
    x=float(radius*np.cos(np.deg2rad(deg)));y=float(acy+radius*np.sin(np.deg2rad(deg)));cr=p['skylight_radius'];h=p['skylight_height']
    profile=[(0,0),(cr,0)]+[(float(cr*np.cos(t)),float(.3+(h-.3)*np.sin(t)))for t in np.linspace(0,np.pi/2,7)];cap=mf.CrossSection([profile],mf.FillRule.EvenOdd).revolve(16).translate([x,y,az-.15]);self.add(f'Covered atrium pale cap {caps+1}',cap,5,'Observed roof cap array; count, spacing and profile representative');caps+=1
  # Coarse low mechanical blocks only on the library roof, separated from neighbouring PV roof.
  for k,(x,y,w,d)in enumerate([(-43,-29,15,7),(0,-29,17,8),(40,-29,15,7),(68,14,8,11)]):
   self.box(f'Roof low service block {k+1}',(x-w/2,x+w/2),(y-d/2,y+d/2),(roof-.1,roof+3.2),4)
   for j in range(4):self.box(f'Roof service block {k+1} top slat {j+1}',(x-w/2+.5,x+w/2-.5),(y-d/2+.7+j*(d-1.4)/4,y-d/2+1+j*(d-1.4)/4),(roof+3.1,roof+3.4),3)
  # Modest entrance threshold is authored, not a site reconstruction.
  self.box('North entry threshold',(-26,26),(60,71),(3.9,5),8)
  return mf.Manifold.batch_boolean(self.items,mf.OpType.Add)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().simplify(0.001);assert s.status()==mf.Error.NoError,s.status();m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=b.ids[int(oid)]
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'ntnu-main-library.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  mm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(mm.vert_properties)[:,:3].tolist(),'faces':np.asarray(mm.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
