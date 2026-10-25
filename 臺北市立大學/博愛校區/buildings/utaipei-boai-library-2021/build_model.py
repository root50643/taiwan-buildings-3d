#!/usr/bin/env python3
"""Original procedural exterior. No source pixels; dimensions are representative model mm."""
import argparse, json, pathlib
import numpy as np
import trimesh
import manifold3d as mf
PALETTE=[
 {'id':'stone','name':'Observed pale stone / concrete family','hex':'#CBCFCD','evidence':'Daylight east, north and south photographs; uncalibrated'},
 {'id':'frame','name':'Pale projecting frames','hex':'#E0E2DB','evidence':'Photographed eaves, frames and mullions; uncalibrated'},
 {'id':'glass','name':'Opaque blue-green glazing approximation','hex':'#527E85','evidence':'Observed glazing family, not transparent simulated glass'},
 {'id':'glass_shadow','name':'Dark glazing / recessed panels','hex':'#354F56','evidence':'Observed shadowed glazing family; no interior reconstruction'},
 {'id':'screen','name':'Orange-brown sunshade fins','hex':'#A9673D','evidence':'Daylight architect photographs; no exact coating specification'},
 {'id':'roof','name':'Neutral gray roof surface','hex':'#777B78','evidence':'Roof aerial, approximate material interpretation'},
 {'id':'central_dark','name':'Central dark visible top zone','hex':'#3D4243','evidence':'Aerial dark rectangle; covering type and depth unknown'},
 {'id':'west_neutral','name':'Unobserved west details: neutral closure','hex':'#B6BCBB','evidence':'Plan-supported envelope only; NOT verified west facade paint'},
 {'id':'plinth','name':'Authored display plinth','hex':'#929D9A','evidence':'Display-only; not surveyed terrain'},
 {'id':'approach','name':'Approximate entrance platform','hex':'#BBB9AE','evidence':'Entrance photographs, simplified steps'},
]
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={}
 def add(self,n,s,mat=0,evidence='guide outlines + photographs; proportions estimated'):
  s=s.as_original();self.ids[int(s.original_id())]=mat;self.items.append(s)
  self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_model_mm':list(s.bounding_box())})
 def box(self,n,x,y,z,mat=0,evidence='photographed feature family; size/count simplified'):
  assert min(x[1]-x[0],y[1]-y[0],z[1]-z[0])>0,(n,x,y,z)
  self.add(n,mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]]),mat,evidence)
 def prism(self,n,poly,z,mat=0,evidence='official guide outline, independently simplified; not measured'):
  self.add(n,mf.CrossSection([poly],mf.FillRule.EvenOdd).extrude(z[1]-z[0]).translate([0,0,z[0]]),mat,evidence)
 def grid_east(self,name,x,y,z,n,rows,mat=2):
  self.box(name+' glazing',(x-.18,x+.3),y,z,mat)
  for i,yy in enumerate(np.linspace(y[0],y[1],n+1)):
   self.box(name+f' vertical {i}',(x+.2,x+.85),(float(yy)-.325,float(yy)+.325),z,1)
  for i,zz in enumerate(rows):self.box(name+f' horizontal {i}',(x+.2,x+.85),y,(zz-.325,zz+.325),1)
 def grid_north(self,name,y,x,z,n,rows,mat=2):
  self.box(name+' glazing',x,(y-.18,y+.3),z,mat)
  for i,xx in enumerate(np.linspace(x[0],x[1],n+1)):
   self.box(name+f' vertical {i}',(float(xx)-.325,float(xx)+.325),(y+.2,y+.85),z,1)
  for i,zz in enumerate(rows):self.box(name+f' horizontal {i}',x,(y+.2,y+.85),(zz-.325,zz+.325),1)
 def grid_south(self,name,y,x,z,n,rows,mat=2):
  self.box(name+' glazing',x,(y-.3,y+.18),z,mat)
  for i,xx in enumerate(np.linspace(x[0],x[1],n+1)):
   self.box(name+f' vertical {i}',(float(xx)-.325,float(xx)+.325),(y-.85,y-.2),z,1)
  for i,zz in enumerate(rows):self.box(name+f' horizontal {i}',x,(y-.85,y-.2),(zz-.325,zz+.325),1)
 def build(self):
  p=self.p;b=p['display_base'];self.box('Display plinth, not surveyed site',b[:2],b[2:4],b[4:],8,'authored display aid only')
  # Six authored height zones, not six equal exterior window bands.
  self.prism('Raised occupied-envelope footing',p['lower_outline'],(3.9,8),0)
  self.prism('1F-2F lower envelope with northeast setback',p['lower_outline'],(8,50),7)
  self.prism('Northeast stair, chamfered outer corner',[(55,60),(80,60),(87,67),(87,82),(55,82)],(4,135),0)
  self.box('2F north linking bridge',(16,58),(60,82),(30,50),0)
  self.prism('3F-4F projecting middle envelope',p['main_outline'],(50,94),7)
  # 5F east recess; 6F southwest setback are distinct plan changes.
  mid=[(73 if x==76 else x,y) for x,y in p['main_outline']]
  self.prism('5F recessed east envelope',mid,(94,111),7)
  self.prism('6F upper asymmetric envelope',p['top_outline'],(111,129),7)
  # West keeps the outline, cores and setbacks; no mirrored windows or invented doors.
  self.prism('Southeast tall vertical core',[(21,-65),(54,-65),(54,-89),(32,-89),(28,-93),(21,-91)],(4,p['southeast_core_top']),0)
  self.prism('North projecting glazed core envelope',[(-56,79),(-29,79),(-29,97),(-56,91)],(29,134),0)
  self.box('Northwest stair cap',(-85,-56),(61,83),(128.8,132),0)
  self.prism('North core thin cap',[(-57,78),(-28,78),(-28,98),(-57,92)],(133.7,p['north_core_top']),1)
  # Main east opening is recessed from the broad stone portal.
  self.box('East north full-height portal pier',(73,85),(70,84),(4,135),0)
  self.box('East south full-height portal pier',(73,85),(-85,-69),(4,135),0)
  self.box('Large east overhanging canopy',(68,91),(-86,85),(131.3,p['east_eave_top']),1)
  self.box('East roof rear tying beam',(69,77),(-85,84),(128.5,132),0)
  self.box('East mid-level projecting ledge',(74,85),(-72,72),(93.8,97.3),1)
  self.grid_east('East upper two-storey glazing',73,(-68,69),(97.2,129),39,[105,114,122])
  for yy in (-23,23):self.box('East upper wide mullion '+str(yy),(73.15,75.6),(yy-1.25,yy+1.25),(97,129.2),0)
  self.grid_east('East middle shadowed glazing',76,(-68,69),(50,94),24,[62,74,85],3)
  for i,yy in enumerate(np.linspace(-68,69,p['east_fin_count'])):
   self.box(f'East orange-brown sunshade {i+1}',(76.1,80.4),(float(yy)-p['fin_width']/2,float(yy)+p['fin_width']/2),(50,94.2),4)
  self.grid_east('East lower southern entrance glazing',66,(-66,-12),(8,49.8),12,[18,29,40])
  self.grid_east('East lower projecting entrance glazing',77,(-11,14),(8,49.8),6,[18,29,40])
  self.grid_east('East lower northern entrance glazing',66,(14,25),(8,49.8),3,[18,29,40])
  # Deep pale entrance piers, independent from slim window mullions.
  for yy in (-47,-19,23):self.box('East entrance structural pier '+str(yy),(65.7,76.2),(yy-1.7,yy+1.7),(8,50.2),0)
  # North is NOT a mirror of south: recessed screen and two distinct glazed ends.
  self.grid_north('North recessed main glazing',74,(-28,17),(38,128.5),10,[50,70,91,111],3)
  for i,xx in enumerate(np.linspace(-27,16,p['north_fin_count'])):
   self.box(f'North recessed brown fin {i+1}',(float(xx)-.425,float(xx)+.425),(74.15,77.8),(38,129),4)
  self.grid_north('North eastern screen backing',82,(17,41),(39,128.5),6,[50,70,91,111],3)
  for i,xx in enumerate(np.linspace(18,40,10)):
   self.box(f'North eastern brown fin {i+1}',(float(xx)-.425,float(xx)+.425),(82.15,85.2),(39,129),4)
  self.grid_north('North east projecting glazed bay',82,(43,69),(62,127),8,[70,80,90,100,110,120])
  for xx in (41,70):self.box('North glazed bay side frame '+str(xx),(xx-1.25,xx+1.25),(81.8,87),(60,130),0)
  for zz in (60,129):self.box('North glazed bay horizontal frame '+str(zz),(40,71),(81.8,87),(zz,zz+2),0)
  self.grid_north('North western core glazing',94,(-53,-32),(38,132),5,[48,58,68,78,88,98,108,118,128])
  # Tiny glass prisms sit at the actual sloping north core face, not unsupported in space.
  self.box('North core glazing support',(-54,-31),(90,94.1),(37.8,132.2),0)
  self.grid_north('North western core glazing visible',94.1,(-53,-32),(38,132),5,[48,58,68,78,88,98,108,118,128])
  self.box('North screen lower ledge',(-29,42),(73.5,84.6),(36.8,39.2),0)
  self.box('North screen top cap',(-29,42),(73.5,85),(128.7,131),0)
  # South long screen and tall white core, with visible narrow turquoise stair strip.
  self.grid_south('South lower double-height glazing',-80,(-74,20),(8,49.5),20,[19,30,41])
  for xx in (-67,-24,17):self.box('South lower structural pier '+str(xx),(xx-1.5,xx+1.5),(-82,-79.6),(8,50.5),0)
  self.grid_south('South screen backing',-80,(-74,20),(50,111),22,[61,73,84,95,106],3)
  self.grid_south('South recessed upper glazing',-73,(-67,20),(111,124.5),19,[118],3)
  for i,xx in enumerate(np.linspace(-74,19,p['south_fin_count'])):
   # Over upper setback these fins remain connected by the top and lower ledges.
   self.box(f'South orange-brown sunshade {i+1}',(float(xx)-.425,float(xx)+.425),(-84,-79.8),(49.5,123),4)
  for zz in (49,72.5,93.8,122.8):self.box('South screen horizontal ledge '+str(zz),(-77,21),(-84.4,-79.7),(zz,zz+1.7),0)
  self.box('South upper rear beam',(-70,21),(-73.4,-71.5),(123,129),0)
  for xx in (-75,20):self.box('South pergola end post '+str(xx),(xx-.75,xx+.75),(-83.7,-72),(123,129),1)
  self.box('South pergola outer beam',(-76,21),(-85,-83.4),(127.5,129),1)
  for i,xx in enumerate(np.linspace(-74,19,27)):
   self.box(f'South open pergola rafter {i+1}',(float(xx)-.6,float(xx)+.6),(-85,-71.7),(127.5,129),1)
  self.box('Southeast narrow glazed projection backing',(22,31),(-93.4,-87.8),(8,132),0)
  self.grid_south('Southeast core tall narrow window',-93.4,(23,30),(9,130),2,[20,31,42,53,64,75,86,97,108,119])
  # Roof: real main rectangles and low caps, never an arbitrary seventh storey.
  self.prism('Main neutral roof surface',p['top_outline'],(128.9,129.35),5)
  self.box('West visible long low roof cap',(-83,-65),(16,58),(129,132.2),0)
  self.box('West cap neutral top',(-83,-65),(16,58),(132.1,132.5),5)
  self.box('Southwest visible roof rectangle',(-65,18),(-71,-38),(129.2,129.8),5)
  self.box('Southeast core dark top',(22,53),(-88,-66),(139.8,140.15),5)
  x0,x1,y0,y1=p['central_dark_zone']
  self.box('Central dark neutral top feature',(x0,x1),(y0,y1),(129.3,129.65),6,'aerial dark zone; NOT an open well or asserted glazed roof')
  for x in (x0,x1):self.box('Central visible top rim X '+str(x),(x-.55,x+.55),(y0-.55,y1+.55),(129.2,130.3),0)
  for y in (y0,y1):self.box('Central visible top rim Y '+str(y),(x0-.55,x1+.55),(y-.55,y+.55),(129.2,130.3),0)
  # Approach is limited to the photographed raised platform/steps; no underground volumes.
  self.box('Entrance raised platform',(65.5,98),(-68,29),(3.8,7.9),9)
  for i in range(5):self.box(f'Approximate entrance step {i+1}',(97-i*1.6,107-i*1.6),(-28,10),(4,4+(i+1)*.8),9)
  # A modeled neutral ramp-mouth surface; local depression is open above, not a basement.
  self.box('North entrance ramp side wall outer',(85,108),(87,89),(3.8,10),0)
  self.box('North entrance ramp side wall inner',(85,108),(75,77),(3.8,9),0)
  ramp=mf.Manifold.hull_points([[85,77,4],[108,77,4],[85,87,4],[108,87,4],[85,77,4.3],[108,77,8],[85,87,4.3],[108,87,8]])
  self.add('Approximate exposed ramp surface only',ramp,9,'entry ramp family only; connection to B1-B3 not reconstructed')
  return mf.Manifold.batch_boolean(self.items,mf.OpType.Add)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().simplify(1e-5);assert s.status()==mf.Error.NoError,s.status()
 m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=b.ids[int(oid)]
 t=trimesh.Trimesh(v,f,process=False)
 t.export(out/'utaipei-boai-library-2021.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  mm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(mm.vert_properties)[:,:3].tolist(),'faces':np.asarray(mm.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE) if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
