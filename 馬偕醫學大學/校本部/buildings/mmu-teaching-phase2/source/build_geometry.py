#!/usr/bin/env python3
"""Source-proportional whole MMU second teaching/research D–G complex.
All geometric inputs are authored numbers; no source pixels or private data needed.
"""
import argparse,json,pathlib,math
import numpy as np, trimesh, manifold3d as mf
ROOT=pathlib.Path(__file__).resolve().parent
PALETTE=[
 {'id':'brick','name':'Published brick red, approximate','hex':'#A26550','evidence':'2014 architect gallery / 2016 publication; uncalibrated'},
 {'id':'concrete','name':'Light concrete frame and bands','hex':'#C9CAC5','evidence':'D/E front and road-side open frames; uncalibrated'},
 {'id':'glass','name':'Dark blue gray glazing/recess','hex':'#3C5059','evidence':'Published facades; opaque printing convention'},
 {'id':'metal','name':'Dark steel trellis and rails','hex':'#454C4B','evidence':'D branching screen; simplified thicker sections'},
 {'id':'roof','name':'Neutral roof surfaces, unverified finish','hex':'#A6A7A2','evidence':'Footprint/height supported; exact waterproofing color unknown'},
 {'id':'grade','name':'Neutral abstract support/grade','hex':'#B0B2AA','evidence':'Authored display aid, not measured terrain or basement'},
 {'id':'base','name':'Display plinth','hex':'#757D79','evidence':'Authored display aid only'},
 {'id':'window_light','name':'Light window subdivisions','hex':'#B4C1C1','evidence':'Broad window subdivision family, simplified'},
]
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.s=p['plan_to_model']['scale'];self.ox,self.oy=p['plan_to_model']['origin'];self.L=p['levels_model_mm'];self.S=p['structural_model_mm']
 def xy(self,x,y):return ((x-self.ox)*self.s,(self.oy-y)*self.s)
 def add(self,n,m,mat=0,certainty='source-proportional',source='official 3F–7F topology / published facade family'):
  assert m.status()==mf.Error.NoError,(n,m.status());m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'certainty':certainty,'source':source,'bounds_model_mm':list(m.bounding_box())})
 def rawbox(self,x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
 def box(self,n,x,y,z,mat=0,**kw):self.add(n,self.rawbox(x,y,z),mat,**kw)
 def planbox(self,n,x0,x1,y0,y1,z0,z1,mat=0,**kw):
  a,b=self.xy(x0,y1);c,d=self.xy(x1,y0);self.box(n,(a,c),(b,d),(z0,z1),mat,**kw)
 def beam(self,n,a,b,w,mat=1):
  a=np.array(a,float);b=np.array(b,float);delta=b-a;length=np.linalg.norm(delta);u=delta/length;t=np.array([0.,0.,1.])
  if abs(u@t)>.95:t=np.array([0.,1.,0.])
  v=np.cross(u,t);v/=np.linalg.norm(v);q=np.cross(u,v)
  # hull of a square-prism beam; ends extended for robust intersections.
  pts=[(p+sv*v*w/2+sq*q*w/2).tolist()for p in (a-.05*u,b+.05*u)for sv in(-1,1)for sq in(-1,1)]
  self.add(n,mf.Manifold.hull_points(pts),mat,source='Published structural language; section/count simplified')
 def frame(self,n,rect,z0,z1,bays=5,side='long'):
  x0,x1,y0,y1=rect;a,b=self.xy(x0,y1);c,d=self.xy(x1,y0);w=self.S['frame_width']
  for x in(a,c):self.box(n+' longitudinal open beam',(x-w/2,x+w/2),(b-w/2,d+w/2),(z1-w,z1),1)
  for y in(b,d):self.box(n+' transverse open beam',(a-w/2,c+w/2),(y-w/2,y+w/2),(z1-w,z1),1)
  for y in np.linspace(b,d,bays+1):
   for x in(a,c):self.box(n+' pier',(x-w/2,x+w/2),(y-w/2,y+w/2),(z0-.4,z1),1)
  # E has cross beams only. F/G perimeter remains a genuinely open rectangular frame.
  if n.startswith('E'):
   for y in np.linspace(b,d,bays+1)[1:-1]:self.box(n+' open cross beam',(a-w/2,c+w/2),(y-w/2,y+w/2),(z1-w,z1),1)
 def window_x(self,n,x,y,z,w,h,positive=True,mat=2):
  sign=1 if positive else -1;self.box(n,(x-.12,x+.26)if positive else(x-.26,x+.12),(y-w/2,y+w/2),(z,z+h),mat,source='Observed opening family; approximate bay spacing, opaque shallow relief')
  self.box(n+' mullion',(x+.05,x+.34)if positive else(x-.34,x-.05),(y-.18,y+.18),(z,z+h),7)
 def window_y(self,n,y,x,z,w,h,positive=True):
  self.box(n,(x-w/2,x+w/2),(y-.12,y+.26)if positive else(y-.26,y+.12),(z,z+h),2,source='Observed opening family; approximate bay spacing, opaque shallow relief')
  self.box(n+' mullion',(x-.18,x+.18),(y+.05,y+.34)if positive else(y-.34,y-.05),(z,z+h),7)
 def build(self):
  P=self.p;L=self.L;s=self.s;bottom=L['base'];lo=L['lower_grade_abstraction'];start=L['main_upper_start'];roof=L['main_roof'];frame=L['open_frame_top'];fw=self.S['floor_band']
  self.box('Display plinth — not site terrain',(-128,137),(-75,86),(0,bottom),6,certainty='display-only',source='Independent presentation aid; courtyard remains outside building volume')
  # G and F begin above the lower open level, unlike E; never seven full extrusions.
  for wing in ('G','F'):
   x0,x1,y0,y1=P['footprints'][wing]
   self.planbox(wing+' abstract grade support',x0,x1,y0,y1,bottom,lo,5,certainty='display abstraction',source='Slope-related lower exposure; not terrain, basement, or measured floor height')
   self.planbox(wing+' upper three-storey body',x0,x1,y0,y1,start,roof,0)
   # Real lower undercroft: core plus columns, not an extra full floor.
   self.planbox(wing+' lower recessed service core',x0+10,x1-25,y0+5,y0+53,lo,start+.2,5)
   for xx in (x0+4,x1-4):
    for yy in np.linspace(y0+4,y1-4,6):self.planbox(wing+' lower pier',xx-2,xx+2,yy-2,yy+2,lo-.2,start+.2,1)
   self.planbox(wing+' lower suspended plate',x0,x1,y0,y1,start-.9,start+.5,1)
   for z in (35,46,56.5):self.planbox(wing+' thin facade level band',x0-.7,x1+.7,y0-.7,y1+.7,z,z+fw,1)
   self.planbox(wing+' neutral terrace roof',x0,x1,y0,y1,roof-.15,roof+.45,4)
   self.planbox(wing+' inset flat roof',x0+14,x1-14,y0+20,y1-22,roof, L['inner_setback_roof'],4,source='7F and aerial: inset flat roof/terrace; exact coping simplified')
   self.frame(wing+' high open perimeter frame',[x0+1,x1-1,y0+1,y1-1],roof,frame,6 if wing=='G' else 4)
   # Coarse G brick return: broad brick with narrow tall glass, not mirrored front.
   for px in (x0,x1):
    X,_=self.xy(px,y0)
    for yy in np.linspace(y0+26,y1-20,8 if wing=='G' else 5):
     _,Y=self.xy(px,yy)
     for z in (26,37,48):self.window_x(wing+' courtyard/return narrow opening',X,Y,z,3.2,6.8,px==x1)
   _,Y=self.xy(x0,y1)
   for xx in np.linspace(x0+20,x1-20,4):
    X,_=self.xy(xx,y1)
    for z in(26,37,48):self.window_y(wing+' end-face narrow opening',Y,X,z,2.9,6.7,False)
  # E long unequal arm with five exposed bands, stepped local roof room, and no phase I.
  ex0,ex1,ey0,ey1=P['footprints']['E']
  self.planbox('E long five-band body including enclosed side circulation',ex0,522,ey0,ey1,bottom,roof,0)
  self.planbox('E neutral roof terrace',ex0,522,ey0,ey1,roof-.1,roof+.5,4)
  # Side gallery/circulation strip and phase-I boundary stub are deliberately narrow.
  for z in (2,13,24,35,46,57):self.planbox('E phase-boundary corridor plate',ex1-2,522,394,447,z,z+1,1)
  for yy in np.linspace(398,443,3):self.planbox('E corridor pier',518,522,yy-2,yy+2,bottom,roof+1,1)
  for z in (13,24,35,46,56.7):self.planbox('E brick floor course',ex0-.2,522.2,ey0,ey1,z,z+.3,0)
  # Front towards plan-right, regular narrow lower windows / wide upper band, per front photo.
  X,_=self.xy(522,ey0)
  for yy in np.linspace(ey0+19,ey1-18,11):
   _,Y=self.xy(522,yy)
   for z in (4,15,26,37):self.window_x('E front lower window',X,Y,z,5.0,4.1)
   self.window_x('E front broad upper window',X,Y,48,8.5,6.5)
  X,_=self.xy(ex0,ey0)
  for yy in np.linspace(154,ey1-18,7):
   _,Y=self.xy(ex0,yy)
   for z in(15,26,37,48):self.window_x('E inward court simplified opening',X,Y,z,5.6,5.2,False)
  self.frame('E open rooftop pergola',[406,504,213,395],roof+.3,frame,5)
  self.planbox('E localized upper enclosed room',404,506,50,132,roof, L['E_upper_room_top'],1,source='7F E upper room + early front photos/aerial: local white-windowed stage')
  for px in (404,506):
   X,_=self.xy(px,50)
   for yy in (64,88,114):
    _,Y=self.xy(px,yy);self.window_x('E upper room window',X,Y,59,5.9,6.4,px==506)
  for py in(50,132):
   _,Y=self.xy(404,py)
   for xx in(421,449,478):
    X,_=self.xy(xx,py);self.window_y('E upper room end window',Y,X,59,6.4,6.4,py==50)
  self.planbox('E further raised brick rooftop cap',423,490,57,113,L['E_upper_room_top']-.2,L['E_brick_cap_top'],0,source='Early front photos and 2016 aerial: second taller brick step, not full new storey')
  self.planbox('E cap neutral flat roof',423,490,57,113,L['E_brick_cap_top']-.2,L['E_brick_cap_top']+.55,4)
  # Continuous narrow upper back corridor joins G,F,E but leaves the inner light well and main court open.
  self.planbox('G–F–E narrow back corridor',128,404,36,58,start,roof,1)
  for z in(26,37,48):
   _,Y=self.xy(128,36)
   for xx in np.linspace(139,395,13):
    X,_=self.xy(xx,36);self.window_y('Road-side upper corridor glazed bay',Y,X,z,5.8,7.0,True)
  # Published road-side facades alternate broad brick piers and glazed concrete bays.
  for xx0,xx1 in ((190,222),(309,339),(370,396)):
   self.planbox('Road-side broad brick pier panel',xx0,xx1,35.1,37,start,roof,0,source='ad-12/ad-15: broad brick panels separating open/glazed concrete bays; spacing simplified')
  for xx in(28,60,96):
   X,Y=self.xy(xx,36)
   for z in(26,37,48):self.window_y('G road-side broad grouped opening',Y,X,z,6.8,6.5)
  for xx in(425,474):
   X,Y=self.xy(xx,36)
   for z in(26,37,48):self.window_y('E road-side grouped opening',Y,X,z,8.3,6.4)
  self.planbox('F–E narrow cross-link',350,406,132,148,start,roof,1)
  for z in(26,37,48):
   _,Y=self.xy(350,148)
   for xx in(364,389):
    X,_=self.xy(xx,148);self.window_y('F–E bridge window',Y,X,z,5.4,6.7,False)
  # One small higher corridor on the back edge, not a solid floor across F/G terraces.
  self.planbox('Upper back corridor low wall',55,399,36,47,roof,roof+3,0)
  for xx in np.linspace(55,399,16):self.planbox('Upper corridor frame pier',xx-1.8,xx+1.8,36,47,roof,frame,1)
  self.planbox('Upper back corridor open top beam',55,399,36,40,frame-1.2,frame,1)
  self.planbox('Upper back corridor inner top beam',55,399,43,47,frame-1.2,frame,1)
  # D uses its own rotated axes rather than a fourth orthogonal box.
  origin=np.array(self.xy(*P['footprints']['D_origin']));ang=math.radians(P['footprints']['D_rotation_degrees']);u=np.array([math.cos(ang),math.sin(ang)]);v=np.array([math.sin(ang),-math.cos(ang)]);du,dv=P['footprints']['D_size']
  def Dpt(uu,vv,z):return [*(origin+u*uu+v*vv),z]
  def Dbox(n,ur,vr,zr,mat=0,**kw):
   pts=[Dpt(uu,vv,z)for uu in ur for vv in vr for z in zr];self.add(n,mf.Manifold.hull_points(pts),mat,**kw)
  Dbox('D abstract grade support',(0,du),(0,dv),(bottom,lo),5,certainty='display abstraction',source='Slope-related lower grade, not measured terrain')
  Dbox('D recessed lower body',(0,du-9),(0,dv),(lo,start+.2),0)
  for vv in np.linspace(2,dv-2,7):Dbox('D undercroft pier',(du-2.4,du-.8),(vv-.7,vv+.7),(lo-.2,start+.4),0)
  Dbox('D upper three-band skewed body',(0,du),(0,dv),(start,roof),0)
  for z in(start,35,46,56.8):Dbox('D pale perimeter band',(-.25,du+.25),(-.25,dv+.25),(z,z+.85),1)
  Dbox('D neutral flat roof',(.9,du-.9),(.9,dv-.9),(roof,roof+.45),4)
  for ur,vr in [((0,1.2),(0,dv)),((du-1.2,du),(0,dv)),((0,du),(0,1.2)),((0,du),(dv-1.2,dv))]:Dbox('D flat-roof parapet',ur,vr,(roof-.3,roof+1.7),0)
  # Long screened elevation with recessed dark windows and balcony slabs.
  for z in(26,37,48):
   Dbox('D screened long window strip',(du-.05,du+.24),(5,dv-5),(z,z+6),2)
   for vv in np.linspace(5,dv-5,10):Dbox('D window subdivision',(du+.14,du+.32),(vv-.18,vv+.18),(z,z+6),7)
  for z in(24,35,46,57):Dbox('D slim balcony sill',(du-.3,du+2.3),(5,dv-5),(z,z+.85),1)
  # Distinct end face: smaller vertical openings and one low horizontal row.
  for z in(37,48):
   for uu in(8,18,31):Dbox('D end-face narrow window',(uu-1.4,uu+1.4),(dv-.1,dv+.27),(z,z+6.5),2)
  Dbox('D end-face low broad window',(12,du-3),(dv-.1,dv+.27),(26,30.5),2)
  for uu in np.linspace(14,du-5,7):Dbox('D low end-window subdivision',(uu-.16,uu+.16),(dv+.12,dv+.35),(26,30.5),7)
  # The opposite end is not a mirror: sparse grouped openings against large brick panels.
  for z in(26,37,48):
   for uu in(8,29):Dbox('D road-end grouped opening',(uu-2.4,uu+2.4),(-.28,.1),(z,z+6.2),2)
  # Open branching trellis remains actual holes; no arbitrary solid green plane.
  trellis_u=du+3.5;w=self.S['trellis'];vvlist=np.linspace(5,dv-5,8)
  for vv in vvlist:self.beam('D trellis vertical',Dpt(trellis_u,vv,23.7),Dpt(trellis_u,vv,64),w,3)
  for z in(24,35,46,57,64):self.beam('D trellis horizontal',Dpt(trellis_u,5,z),Dpt(trellis_u,dv-5,z),w,3)
  for vv in(15,35,50):
   self.beam('D trellis branching left',Dpt(trellis_u,vv,35),Dpt(trellis_u,max(5,vv-8),52),w,3)
   self.beam('D trellis branching right',Dpt(trellis_u,vv,35),Dpt(trellis_u,min(dv-5,vv+8),52),w,3)
  for z in(24,35,46,57):
   for vv in(5,20,35,dv-5):self.beam('D trellis attachment',Dpt(du-.1,vv,z+.3),Dpt(trellis_u,vv,z+.3),w,3)
  # D links follow their actual endpoints and enclose a second open recess.
  for label,y0,y1,xend in [('upper',36,48,598),('lower',121,135,610)]:
   for z in(start,35,46,57):self.planbox('E–D '+label+' narrow link deck',519,xend,y0,y1,z,z+1.1,1)
   for zz in(25.1,36.1,47.1):
    self.planbox('E–D '+label+' dark bridge band',520,xend-1,y0+1.5,y1-1.5,zz,zz+8.8,2)
   for yy in(y0,y1-2):
    for xx in np.linspace(521,xend-2,5):self.planbox('E–D bridge pier',xx,xx+2,yy,yy+2,start,roof+1,1)
  # Road-side projecting stair character, supported by corridor and simplified.
  xa,ya=self.xy(205,36);xb,yb=self.xy(333,36)
  for k,(z0,z1) in enumerate([(24,35),(35,46)]):
   n=15;left=xa if k==0 else xb;right=xb if k==0 else xa
   for i in range(n):
    x=left+(right-left)*i/n;xn=left+(right-left)*(i+1)/n
    self.box('Road-side external stair step',(min(x,xn)-.06,max(x,xn)+.06),(ya-.15,ya+3.5),(z0+i*(z1-z0)/n-.45,z0+(i+1)*(z1-z0)/n),1)
   self.beam('Road-side external stair solid rail',[left,ya+3.1,z0+2.5],[right,ya+3.1,z1+2.5],1.05,3)
   for i in(0,4,8,12,15):
    x=left+(right-left)*i/n;z=z0+i*(z1-z0)/n;self.beam('Road-side stair rail post',[x,ya+3.1,z-.1],[x,ya+3.1,z+2.5],1.0,3)
   self.box('Road-side stair landing',(right-2.2,right+2.2),(ya-.2,ya+4),(z1-.6,z1+.5),1)
  # E boundary stair core only on D–G side; no phase-I tower or C volume.
  self.planbox('E lower-end stair projection',423,491,395,421,bottom,roof,0)
  self.planbox('E lower-end stair roof',423,491,395,421,roof-.2,roof+1,4)
  # Make one connected union. Construction components are retained separately for editing.
  return mf.Manifold.batch_boolean(self.items,mf.OpType.Add)

def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);solid=b.build();assert solid.status()==mf.Error.NoError
 # Remove sub-micron nearly collinear slivers before binary-STL float32 quantization.
 solid=solid.simplify(0.0002)
 m=solid.to_mesh();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),dtype=np.int32)
 for k,oid in enumerate(m.run_original_id):mi[m.run_index[k]//3:m.run_index[k+1]//3]=b.ids[int(oid)]
 mesh=trimesh.Trimesh(v,f,process=False);mesh.export(out/'model.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'palette.json').write_text(json.dumps(PALETTE,ensure_ascii=False,indent=2)+'\n');(out/'parameters.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
 (out/'editable-parts.json').write_text(json.dumps({'units':'authored model mm, not measured scale','palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  pm=item.to_mesh();parts.append({'name':op['name'],'vertices':np.asarray(pm.vert_properties)[:,:3].tolist(),'faces':np.asarray(pm.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 report={'vertices':len(v),'triangles':len(f),'authored_components':len(parts),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'connected_shells':len(mesh.split(only_watertight=False)),'volume_model_mm3':float(mesh.volume),'bounds_model_mm':mesh.bounds.tolist(),'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=pathlib.Path,required=True);a.add_argument('--parameters',type=pathlib.Path,default=ROOT/'parameters.json');args=a.parse_args();run(args.out,args.parameters)
