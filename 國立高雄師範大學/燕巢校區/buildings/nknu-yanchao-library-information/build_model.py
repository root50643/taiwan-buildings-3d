#!/usr/bin/env python3
"""Original parametric above-ground exterior. Public numerical inputs only; no image/network dependency.
Architectural-metre-equivalent parameters are proportional estimates, not survey data.
"""
import argparse,json,pathlib,math
import numpy as np
import trimesh,manifold3d as mf
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
PALETTE=[
 {'id':'warm_cladding','name':'Warm beige exterior cladding','hex':'#C9B69A','evidence':'Actual 2011–2012 completion photographs, uncalibrated beige finish'},
 {'id':'glazing','name':'Opaque dark green grey glazing','hex':'#40555B','evidence':'Recessed reflective glass in actual completion photographs; opaque exterior model convention'},
 {'id':'pale_frame','name':'Pale metal and structural accents','hex':'#E0E2D9','evidence':'Roof posts, circular rooflight ribs, rear columns and glazing divisions in completion photos'},
 {'id':'roof','name':'Neutral grey roofs and canopy edges','hex':'#858B8C','evidence':'Actual elevated whole-roof photograph; exact waterproofing and fine services unresolved'},
 {'id':'terrace','name':'Grey paving and deck edges','hex':'#A8ADAA','evidence':'Visible entrance deck and rear curved terrace; paving joints generalized'},
 {'id':'panel_joint','name':'Recessed neutral panel joints','hex':'#AB9D88','evidence':'Photographic cladding panel divisions; exact joint dimensions approximate'},
 {'id':'display_base','name':'Nonarchitectural display support','hex':'#CDD0C8','evidence':'Authored support closure, not B1, foundation, measured terrain or building plinth'}]
def box(x,y,z):return mf.Manifold.cube([x[1]-x[0],y[1]-y[0],z[1]-z[0]]).translate([x[0],y[0],z[0]])
def solid(poly,z0,z1):
 if hasattr(poly,'geom_type'):
  if poly.geom_type=='MultiPolygon':return mf.Manifold.batch_boolean([solid(q,z0,z1)for q in poly.geoms],mf.OpType.Add)
  loops=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1]for r in poly.interiors]
 else:loops=[poly]
 return mf.CrossSection(loops,mf.FillRule.EvenOdd).extrude(z1-z0).translate([0,0,z0])
def arc(r,a,b,n=48):return [(r*math.cos(t),r*math.sin(t))for t in np.linspace(math.radians(a),math.radians(b),n)]
def union(parts):return mf.Manifold.batch_boolean(parts,mf.OpType.Add)
class Builder:
 def __init__(self,p):self.p=p;self.items=[];self.ops=[];self.ids={};self.s=p['model_mm_per_m']
 def add(self,n,m,mat=0,evidence='Actual completion photos and official whole floor plans; dimensions proportional'):
  assert not m.is_empty(),n
  assert m.status()==mf.Error.NoError,(n,m.status())
  m=m.as_original();self.ids[int(m.original_id())]=mat;self.items.append(m);self.ops.append({'name':n,'material':PALETTE[mat]['id'],'evidence':evidence,'bounds_architectural_m_equivalent':list(m.bounding_box())})
 def box(self,n,x,y,z,mat=0):self.add(n,box(x,y,z),mat)
 def strip(self,n,path,w,z0,z1,mat=0):self.add(n,solid(LineString(path).buffer(w/2,cap_style=2,join_style=2),z0,z1),mat)
 def col(self,n,x,y,z0,z1,r=.15,mat=2):self.add(n,mf.Manifold.cylinder(z1-z0,r,r,12).translate([x,y,z0]),mat)
 def beam(self,n,a,b,r=.14,mat=2):
  aa=np.array(a,float);bb=np.array(b,float);d=bb-aa;length=np.linalg.norm(d);u=d/length;v=np.cross(u,[0,0,1]);
  if np.linalg.norm(v)<.1:v=np.cross(u,[0,1,0])
  v/=np.linalg.norm(v);w=np.cross(u,v);matrix=np.column_stack([v,w,u,aa]);self.add(n,mf.Manifold.cylinder(length,r,r,12).transform(matrix.tolist()),mat)
 def stair(self,name,start,end,width,z0,z1,n,mat=4):
  a=np.array(start,float);b=np.array(end,float);d=b-a;l=np.linalg.norm(d);u=d/l;v=np.array([-u[1],u[0]])
  for i in range(n):
   lo=a+d*i/n;hi=a+d*(i+1)/n+u*.02;poly=[lo-v*width/2,hi-v*width/2,hi+v*width/2,lo+v*width/2];self.add(name+' tread '+str(i+1),solid(np.array(poly).tolist(),z0-.04,z0+(z1-z0)*(i+1)/n),mat,'Stair position/direction constrained by plans; exact riser count and solid underside approximate')
  for sign in [-1,1]:
   aa=a+v*sign*(width/2-.08);bb=b+v*sign*(width/2-.08)
   self.beam(name+' handrail '+str(sign),[*aa,z0+1.0],[*bb,z1+1.0],.12,2)
   for j,t in enumerate(np.linspace(0,1,7)):
    q=aa+(bb-aa)*t;z=z0+(z1-z0)*t;self.col(name+' rail post '+str(sign)+' '+str(j),*q,max(z0-.04,z-.2),z+1.0,.12,2)
 def wing(self,name,origin,rotation,left=False):
  p=self.p;w,l=p['wing_outer_wall_size_m'];g=p['ground_visible_contact_z_m'];h=p['wing_roof_z_m']
  def xf(m):return m.rotate([0,0,rotation]).translate([origin[0],origin[1],0])
  def add(n,m,mat=0):self.add(name+' '+n,xf(m),mat)
  # No exposed B1 is inferred; the wing envelope stops at the visible grade convention.
  core=box((0,w),(0,l),(g-.05,h));cuts=[];glass=[];mullions=[]
  # Local faces are separately sampled, not mirrored copies of a single façade.
  for face,length in [('front',w),('rear',w),('outer',l),('inner',l)]:
   count=max(8,round(length/2.05));spacing=length/count
   for row,(z0,z1) in enumerate(p['facade_bands_m']):
    for i in range(count):
     t=(i+.5)*spacing
     # Central wing joins legitimately mask part of the inner elevations.
     if face=='inner' and 0<t<l*.80:continue
     wid=p['window_width_m'];segments=[(z0,z1)] if row==2 else ([(z0,z0+1.55),(z0+1.9,z1)]if i%3==0 else [(z0+.05,z0+1.65)]if i%2 else [(z0+1.83,z1)])
     if row==2 and (i+int(left))%11==5:continue
     for j,(a,b) in enumerate(segments):
      if face=='front':cut=box((t-wid/2,t+wid/2),(-.02,.34),(a,b));pane=box((t-wid/2+.05,t+wid/2-.05),(.285,.36),(a+.05,b-.05));bar=box((t-wid/2+.04,t+wid/2-.04),(.26,.37),((a+b)/2-.06,(a+b)/2+.06))
      elif face=='rear':cut=box((t-wid/2,t+wid/2),(l-.34,l+.02),(a,b));pane=box((t-wid/2+.05,t+wid/2-.05),(l-.36,l-.285),(a+.05,b-.05));bar=box((t-wid/2+.04,t+wid/2-.04),(l-.37,l-.26),((a+b)/2-.06,(a+b)/2+.06))
      else:
       xx=w if face=='inner' and left or face=='outer' and not left else 0
       xr=(xx-.34,xx+.02)if xx else(-.02,.34);pr=(xx-.36,xx-.285)if xx else(.285,.36);br=(xx-.37,xx-.26)if xx else(.26,.37)
       cut=box(xr,(t-wid/2,t+wid/2),(a,b));pane=box(pr,(t-wid/2+.05,t+wid/2-.05),(a+.05,b-.05));bar=box(br,(t-wid/2+.04,t+wid/2-.04),((a+b)/2-.06,(a+b)/2+.06))
      cuts.append(cut);glass.append(pane);mullions.append(bar)
  add('complete visible wing envelope with recessed openings',core-union(cuts),0);add('recessed glazing',union(glass),1);add('recessed glazing horizontal frames',union(mullions),2)
  # The horizontal macro bands do not signify three storeys.
  for j,z in enumerate([4.65,9.35,12.65]):
   ring=Polygon([(-.04,-.04),(w+.04,-.04),(w+.04,l+.04),(-.04,l+.04)]).difference(Polygon([(.10,.10),(w-.10,.10),(w-.10,l-.10),(.10,l-.10)]));add('fine continuous cladding band '+str(j),solid(ring,z,z+.085),5)
  # Whole broad roof field, low rim, open raised canopy band and repeated posts.
  add('complete flat roof field',box((-.20,w+.2),(-.2,l+.2),(h-.08,h+.22)),3)
  rim=Polygon([(-.2,-.2),(w+.2,-.2),(w+.2,l+.2),(-.2,l+.2)]).difference(Polygon([(.12,.12),(w-.12,.12),(w-.12,l-.12),(.12,l-.12)]));add('low roof perimeter edge',solid(rim,h+.15,h+.48),3)
  ring=Polygon([(-.85,-.85),(w+.85,-.85),(w+.85,l+.85),(-.85,l+.85)]).difference(Polygon([(.62,.62),(w-.62,.62),(w-.62,l-.62),(.62,l-.62)]));add('raised thin perimeter canopy band',solid(ring,p['canopy_top_z_m']-.18,p['canopy_top_z_m']),3)
  for edge in range(4):
   length=w if edge<2 else l
   for j,t in enumerate(np.linspace(.5,length-.5,max(3,round(length/2.35)))):
    x,y=(t,.1)if edge==0 else(t,l-.1)if edge==1 else(.1,t)if edge==2 else(w-.1,t)
    add('canopy support '+str(edge)+' '+str(j),box((x-.12,x+.12),(y-.12,y+.12),(h+.15,p['canopy_top_z_m']-.12)),2)
  # Roof housings only where actual elevated completion photo shows them.
  if left:houses=[(w-10,4.8,7.6,4.5,1.25),(9,27,3.3,3.2,.8)]
  else:houses=[(3.7,4.7,9.0,5.0,2.1),(24,32,3.0,3.4,.8)]
  for i,(x,y,ww,ll,hh) in enumerate(houses):
   add('visible roof housing '+str(i),box((x,x+ww),(y,y+ll),(h+.15,h+hh)),0);add('housing grey flat cap '+str(i),box((x-.2,x+ww+.2),(y-.2,y+ll+.2),(h+hh-.08,h+hh+.17)),3)
   add('housing dark service face '+str(i),box((x+.5,x+ww-.5),(y-.015,y+.07),(h+.48,h+hh-.2)),1)
  # Plan-supported exterior evacuation stair positions, not invented basement stairs.
  if not left:
   for i,(a,b,wi) in enumerate([((w+1.0,13),(w+1.0,3.2),1.75),((24,l+1.25),(12,l+1.25),1.8)]):
    c=math.cos(math.radians(rotation));ss=math.sin(math.radians(rotation));f=lambda q:(origin[0]+q[0]*c-q[1]*ss,origin[1]+q[0]*ss+q[1]*c)
    self.stair(name+' exterior escape stair '+str(i),f(a),f(b),wi,g,5.2,26)
    add('escape upper landing '+str(i),box((w-.1,w+2.0),(2.4,4),(4.8,5.2)) if i==0 else box((10.5,13.5),(l-.1,l+2.2),(4.8,5.2)),4)
  else:
   for j in range(3):
    add('outer flank evacuation shallow step '+str(j),box((-2.2+j*.55,.20),(l-6,l-3),(g-.05,g+.12*(j+1))),4)
    add('rear evacuation shallow step '+str(j),box((w-4,w-1.2),(l-.20,l+2.1-j*.55),(g-.05,g+.12*(j+1))),4)
 def build(self):
  p=self.p;g=p['ground_visible_contact_z_m'];h=p['wing_roof_z_m'];base=p['display_base_m']
  self.add('Nonarchitectural support closure — not B1 or terrain',box(base[:2],base[2:],(-p['display_base_thickness_m'],g)),6,'Fabrication/display support only; no basement, foundation or survey inference')
  self.wing('Right information wing',p['right_wing_origin_m'],0,False)
  # Left wing x increases inward. Its independently oriented whole envelope matches the skewed official plan.
  ang=p['left_wing_rotation_degrees'];w,l=p['wing_outer_wall_size_m'];v=np.array([math.cos(math.radians(ang)),math.sin(math.radians(ang))]);inner=np.array(p['left_wing_inner_front_m']);origin=inner-v*w
  self.wing('Left library wing',origin.tolist(),ang,True)
  a,b=p['rear_arc_degrees'];r=p['central_rear_radius_m'];rear=arc(r,a,b,64);frontL=p['left_wing_inner_front_m'];frontR=p['right_wing_origin_m'];central=Polygon([frontL,frontR,rear[0]]+rear[1:]).buffer(.035,join_style=2);assert central.is_valid
  # Central enclosure joins both wings; actual convex front is not an open courtyard.
  body=solid(central,g-.05,h-.1)
  band=LineString(rear).buffer(.35,cap_style=2,join_style=2)
  for z0,z1 in [(g+.15,3.75),(4.5,9.5)]:body=body-solid(band,z0,z1)
  # Small upper windows are genuine recesses, not a third-storey assertion.
  for i,t in enumerate(np.linspace(math.radians(a+4),math.radians(b-4),12)):
   cx,cy=r*math.cos(t),r*math.sin(t);cut=box((-.43,.43),(-.4,.4),(10.7,11.75)).rotate([0,0,math.degrees(t)-90]).translate([cx,cy,0]);body=body-cut
   pane=box((-.36,.36),(-.26,.08),(10.76,11.69)).rotate([0,0,math.degrees(t)-90]).translate([(r-.25)*math.cos(t),(r-.25)*math.sin(t),0]);self.add('Curved upper band small window '+str(i),pane,1)
  self.add('Central enclosed hall convex upper band and joining body',body,0)
  for j,(rr,z0,z1) in enumerate([(r-.26,g+.14,3.76),(r-.26,4.49,9.51)]):self.strip('Curved hall dark glazed band '+str(j),arc(rr,a,b,64),.22,z0,z1,1)
  for j,z in enumerate([3.80,4.35,9.6,12.7]):self.strip('Curved hall pale horizontal edge '+str(j),arc(r+.06,a,b,64),.48,z,z+.20,2)
  for i,t in enumerate(np.linspace(math.radians(a),math.radians(b),20)):
   x,y=(r-.07)*math.cos(t),(r-.07)*math.sin(t)
   for j,(z0,z1) in enumerate([(g,3.85),(4.35,9.75)]):self.col('Rear glazing mullion '+str(i)+' '+str(j),x,y,z0,z1,.12,2)
  self.strip('Rear glass mid transom',arc(r-.05,a,b,64),.25,6.9,7.05,2)
  # Pale supports sit outside lower glazing and support curved intermediate projection.
  for i,t in enumerate(np.linspace(math.radians(a+8),math.radians(b-8),5)):
   x,y=(r+.65)*math.cos(t),(r+.65)*math.sin(t);self.col('Rear terrace pale support '+str(i),x,y,g-.02,4.6,.24,2)
  self.strip('Rear projecting curved canopy',arc(r+.35,a,b,64),1.5,4.15,4.45,3)
  roof=solid(central,h-.18,h+.22)-mf.Manifold.cylinder(4,6.35,6.35,72).translate([0,0,h-.5]);self.add('Central joining roof with circular light well',roof,3)
  # Recessed glazed closure + hollow tapered lightwell + raised open radial frame.
  # This is not a dome or a fabricated solid cylindrical roof block.
  self.add('Circular rooflight recessed glazed cover',mf.Manifold.cylinder(.23,6.45,6.45,72).translate([0,0,h-.18]),1)
  frustum=mf.Manifold.cylinder(1.75,6.3,8.8,72).translate([0,0,h+.02])-mf.Manifold.cylinder(1.85,6.03,8.53,72).translate([0,0,h-.02]);self.add('Tapered annular rooflight glazing',frustum,1)
  for j,(rr,zz) in enumerate([(6.35,h+.05),(8.85,h+1.73),(9.0,h+2.3)]):self.strip('Circular rooflight pale perimeter ring '+str(j),arc(rr,0,360,97),.24,zz,zz+.16,2)
  for i,t in enumerate(np.linspace(0,2*math.pi,28,endpoint=False)):
   self.beam('Rooflight outward inclined pale rib '+str(i),[6.28*math.cos(t),6.28*math.sin(t),h-.05],[9.2*math.cos(t),9.2*math.sin(t),p['rooflight_top_z_m']],.13,2)
  # Actual front upper deck has an open underside. A surrounding slab does not become a solid podium.
  deck=Polygon(p['front_terrace_polygon_m']).buffer(.08,join_style=2);zz=p['estimated_2F_z_m'];self.add('Front upper terrace slab with clear underpass',solid(deck,zz-.38,zz),4)
  for i,xy in enumerate([(-.3,-30.0),(8.7,-29.4),(1.2,-37.5),(12.9,-35.5)]):self.col('Entrance terrace undercroft support '+str(i),*xy,g-.02,zz,.23,4)
  # Recessed entrance is at the back of this upper terrace, aligned with visible front glazing.
  self.strip('Main entrance recessed glazed doors',[frontL,frontR],.23,zz+.02,8.8,1)
  for i,t in enumerate(np.linspace(0,1,6)):
   xy=np.array(frontL)*(1-t)+np.array(frontR)*t;self.col('Entrance glazing division '+str(i),*xy,zz,8.9,.12,2)
  self.strip('Front horizontal monumental lintel',[[-3.0,-25.4],[20.0,-23.5]],.8,9.0,12.35,0)
  # Distinct tall thin blades and low parapet cheeks frame, rather than fill, the terrace.
  sides=[[p['front_terrace_polygon_m'][0],p['front_terrace_polygon_m'][-1]],[p['front_terrace_polygon_m'][1],p['front_terrace_polygon_m'][2]]]
  for i,side in enumerate(sides):
   self.strip('Entrance terrace grey parapet '+str(i),side,.32,zz-.22,zz+1.05,4)
   q=np.array(side[-1]);d=np.array(side[0])-q;d/=np.linalg.norm(d);self.strip('Tall entrance end fin '+str(i),[q.tolist(),(q+d*2.1).tolist()],.55,g-.02,14.2,0)
  # The outer front arc is labelled flowerbeds and ramps in the actual 2F plan,
  # NOT enclosed rooms. Low landscape retaining forms are kept distinct from the building.
  outer=Polygon(p['front_outer_arc_polygon_m']).buffer(.10,join_style=2)
  for stair_spec in p['entrance_stairs']:outer=outer.difference(LineString([stair_spec['start_m'],stair_spec['end_m']]).buffer(stair_spec['width_m']*.58,cap_style=2))
  self.add('Front curved landscape contact and retaining edge',solid(outer,g-.03,zz-.12),4,'Plan labels flowerbeds/ramps; immediate grade contact is schematic, not a surveyed terrain or room volume')
  self.add('Front curved paved landscape strip',solid(outer.buffer(.08,join_style=2),zz-.14,zz+.03),4)
  # Three shallow planter ribbons; no invented raised gallery or roof across this arc.
  for i,t in enumerate([0.24,0.57,0.90]):
   innerline=np.array(p['front_outer_arc_polygon_m'][:5]);outerline=np.array(p['front_outer_arc_polygon_m'][5:][::-1]);line=(innerline*(1-t)+outerline*t).tolist()
   self.add('Front low curved planter edge '+str(i),solid(LineString(line).buffer(.11,cap_style=2).intersection(outer),zz-.02,zz+.33),4)
  for d in p['entrance_stairs']:self.stair('Paired entrance stair '+d['name'],d['start_m'],d['end_m'],d['width_m'],g,zz,d['steps'])
  # Rear shallow terrace is a crescent between wings, with three distinct rounded steps.
  ar=arc(22.6,66.8,134.5,64);inner=arc(r+.1,b,a,64);terr=Polygon(ar+inner);assert terr.is_valid
  for j in range(3):self.add('Rear curved terrace shallow step '+str(j+1),solid(terr.buffer(-j*.32,join_style=1),g-.03,g+.12*(j+1)),4)
  # Neutral immediate contact strips, no invented terrain survey or below-grade mass.
  self.strip('Rear terrace curb',ar,.3,g-.01,g+.3,4)
  return union(self.items)
def run(out,params):
 out.mkdir(parents=True,exist_ok=True);p=json.loads(params.read_text());b=Builder(p);s=b.build().set_tolerance(.002).simplify(.002);assert s.status()==mf.Error.NoError,s.status();mm=s.scale([p['model_mm_per_m']]*3).to_mesh();s=mf.Manifold(mm).set_tolerance(.005).simplify(.005); closed=s.decompose();filled_internal=len([q for q in closed if q.volume()<=0]);s=union([q for q in closed if q.volume()>0]);s=mf.Manifold(s.to_mesh()).set_tolerance(.006).simplify(.006);mm=s.to_mesh();v=np.asarray(mm.vert_properties)[:,:3].copy();f=np.asarray(mm.tri_verts);mi=np.zeros(len(f),np.int32)
 for i,oid in enumerate(mm.run_original_id):mi[mm.run_index[i]//3:mm.run_index[i+1]//3]=b.ids[int(oid)]
 # Float32 roundtrip canonicalization with explicit original-face correspondence keeps
 # every colour boundary while resolving export-collapsed zero-area facets.
 canonical=mf.Manifold(mf.Mesh(np.ascontiguousarray(v,dtype=np.float32),np.ascontiguousarray(f,dtype=np.uint32),face_id=np.arange(len(f),dtype=np.uint32))).set_tolerance(.002).simplify(.002)
 cm=canonical.to_mesh();mi=mi[np.asarray(cm.face_id,dtype=int)];v=np.asarray(cm.vert_properties)[:,:3].copy();f=np.asarray(cm.tri_verts)
 t=trimesh.Trimesh(v,f,process=False);t.export(out/'nknu-yanchao-library-information.stl');np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 (out/'editable-parts.json').write_text(json.dumps({'units':p['units'],'palette':PALETTE,'features':b.ops},ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for op,item in zip(b.ops,b.items):
  m=item.to_mesh();parts.append({'name':op['name'],'vertices':(np.asarray(m.vert_properties)[:,:3]*p['model_mm_per_m']).tolist(),'faces':np.asarray(m.tri_verts).tolist(),'material':next(i for i,d in enumerate(PALETTE)if d['id']==op['material'])})
 (out/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 r={'vertices':len(v),'triangles':len(f),'volume_model_mm3':float(t.volume),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'bounds_model_mm':t.bounds.tolist(),'components':len(t.split(only_watertight=False)),'authored_parts':len(parts),'non_visible_closed_cavities_filled_for_exterior_print':filled_internal,'float_export_resimplification_tolerances_mm':[0.005,0.006],'material_triangles':{d['id']:int((mi==i).sum())for i,d in enumerate(PALETTE)}}
 (out/'build-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--params',type=pathlib.Path,default=pathlib.Path(__file__).with_name('parameters.json'));a=ap.parse_args();run(a.out,a.params)
