"""NYCU Engineering VI / South Gate 2020 landscape bus shelter.
Source-plan and photo approximation; all delivered dimensions are display millimetres.
Front is -Y. Source roof-plan pixel tracing is an openly approximate design input.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Polygon,Point,box as rect
from shapely.geometry.polygon import orient
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
S=.78
P=lambda x,y:((x-222)*S,(138-y)*S)
poly=lambda pts:Polygon([P(*p) for p in pts])
def cross(p):
 ps=list(p.geoms) if p.geom_type=='MultiPolygon' else [p];loops=[]
 for q in ps:
  if q.is_empty:continue
  q=orient(q,sign=1);loops.append(np.array(q.exterior.coords[:-1]));loops.extend(np.array(a.coords[:-1]) for a in q.interiors)
 return CrossSection(loops)
def slab(p,z,h):return cross(p).extrude(h).translate((0,0,z))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def cyl(x,y,z,h,r,n=16):return Manifold.cylinder(h,r,circular_segments=n).translate((x,y,z))
def rod(a,b,r=.45,n=10):
 a=np.array(a);b=np.array(b);delta=b-a;L=float(np.linalg.norm(delta));z=delta/L;a=a-.06*z;L+=.12
 helper=np.array([0.,0.,1.]) if abs(z[2])<.9 else np.array([1.,0.,0.]);x=np.cross(helper,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return Manifold.cylinder(L,r,circular_segments=n).transform(np.column_stack((x,y,z,a)))
parts=[];material_for_id={};part_records=[]
palette=[('gray_structure_and_columns','#919C9C'),('green_roof_turf','#559346'),('warm_timber_decks','#B99765'),('white_rope_nets','#E5E5D9'),('dark_display_screen_and_lamps','#283B42'),('yellow_ticket_machine','#CEB53F'),('neutral_print_plinth','#939798'),('earth_and_gravel_terrain','#AFA99A'),('rope_wrapped_column_tops','#BAA47A')]
def add(m,col=0,name='structure'):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
# Added connector has no claim to be the real pavement boundary.
add(box(0,12,0,246,196,2.5),6,'invented_printing_plinth')
# Modest rising site terrain. Front waiting void is never filled with a wedge.
terrain=poly([(70,142),(370,142),(370,12),(175,12),(175,45),(70,45)])
terrain_m=slab(terrain,2.3,.2).warp(lambda v:(v[0],v[1],2.5+max(0,v[1]+3)*.135 if v[2]>2.4 else 2.3))
add(terrain_m,7,'approximate_rising_ground')
# Roof traced as an asymmetric skewed whole; low rear slopes, not a gable.
outer=poly([(77,235),(257,235),(368,41),(185,41)])
# The taper is truncated at its front: no zero-width pinched opening.
slot=poly([(226,164),(241,164),(266,41),(218,41)])
tree_hole=poly([(194,86),(210,86),(210,102),(194,102)])
net_hole=poly([(290,105),(323,105),(300,148),(291,148)])
roofplan=outer.difference(slot.union(tree_hole).union(net_hole))
hinge=P(0,185)[1]
def roofz(y):return 46.0-.235*max(0,y-hinge)
def roofs(p,offset,thickness):
 # Explicit triangulation at the bend; all shared hinge vertices have one index.
 # This is generator construction, not a repair of the exported STL.
 from shapely import constrained_delaunay_triangles
 pieces=[p.intersection(rect(-500,-500,500,hinge)),p.intersection(rect(-500,hinge,500,500))]
 xy=[];idx={};ff=[]
 def vi(q):
  key=tuple(round(float(x),8) for x in q)
  if key not in idx:idx[key]=len(xy);xy.append(key)
  return idx[key]
 for piece in pieces:
  if piece.is_empty:continue
  for tr in constrained_delaunay_triangles(piece).geoms:
   cc=list(orient(tr,sign=1).exterior.coords)[:-1];ff.append([vi(q) for q in cc])
 rings=[]
 for q in (list(p.geoms) if p.geom_type=='MultiPolygon' else [p]):
  q=orient(q,sign=1)
  for ring in [q.exterior,*q.interiors]:
   cc=list(ring.coords);rr=[]
   for aa,bb in zip(cc,cc[1:]):
    rr.append(vi(aa))
    if (aa[1]-hinge)*(bb[1]-hinge)<0:
     t=(hinge-aa[1])/(bb[1]-aa[1]);rr.append(vi((aa[0]+t*(bb[0]-aa[0]),hinge)))
   rings.append(rr)
 n=len(xy);vertices=[(x,y,roofz(y)+offset+dz) for dz in [0,thickness] for x,y in xy]
 faces=[tuple(reversed(q)) for q in ff]+[tuple(i+n for i in q) for q in ff]
 for rr in rings:
  for i,j in zip(rr,rr[1:]+rr[:1]):faces.extend([(i,j,j+n),(i,j+n,i+n)])
 tm=trimesh.Trimesh(vertices,faces,process=False)
 assert tm.is_watertight and tm.is_winding_consistent and tm.volume>0,'roof primitive invalid'
 return Manifold(Mesh(np.asarray(vertices,dtype=np.float32),np.asarray(faces,dtype=np.uint32)))
add(roofs(roofplan,-3.0,3.0),0,'continuous_roof_slab_with_three_openings')
# Turf terminates behind the front narrow gray overhang and leaves real open holes.
grass=roofplan.buffer(-1.2,join_style=2).intersection(poly([(81,219),(266,219),(371,38),(181,38)]))
add(roofs(grass,-.15,.8),1,'turf_two_asymmetric_ramps')
# Low perimeter metal rims; nothing crosses the central passage or its opening.
rim=roofplan.buffer(.6,join_style=2).difference(roofplan.buffer(-.6,join_style=2))
add(roofs(rim,-.27,1.15),0,'continuous_raised_roof_edge')
# Deck and furniture footprints trace first-floor plan at roughly /4 drawing scale.
def fp(points):return poly([(x/4,y/4) for x,y in points])
def deck(name,p,z,h=1.8,support=True,col=2):
 add(slab(p,z,h),0,name+'_gray_edge')
 add(slab(p.buffer(-.65,join_style=2),z+h-.12,.35),col,name+'_top')
 if support:
  bx,by,Bx,By=p.bounds;add(box((bx+Bx)/2,(by+By)/2,2.4,max(2.8,(Bx-bx)*.38),max(2.8,(By-by)*.40),z-2.3),0,name+'_simplified_support')
basefloor=fp([(328,887),(1369,887),(1369,566),(1005,566),(1005,740),(810,740),(810,790),(423,790),(423,687),(328,687)])
deck('main_waiting_floor',basefloor,3.2,1.5)
decks=[('left_low',[(423,790),(703,790),(703,708),(587,708),(587,687),(423,687)],6.0),('left_middle',[(290,687),(520,687),(520,619),(572,619),(572,558),(290,558)],9.0),('left_high',[(401,618),(840,618),(840,487),(401,487)],13.2),('middle_small',[(650,657),(794,657),(794,618),(650,618)],10.5),('right_bench',[(1119,749),(1191,749),(1191,572),(1119,572)],10.0)]
for name,coords,z in decks:deck(name,fp(coords),z)
# Stair passage rises toward rear grade. Five distinct horizontal landings.
for i,(y0,y1,x0,x1) in enumerate([(188,174,204,250),(174,153,213,251),(153,131,217,254),(131,111,226,260),(111,90,222,256)]):
 q=poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
 z=5.5+2.25*i;add(slab(q,2.4,z-2.4),0,'central_ground_step_'+str(i));add(slab(q.buffer(-.65),z-.1,.3),7,'gravel_step_top_'+str(i))
# Right T counter: solid pedestal, thin long horizontal slab, not an enclosure.
q=fp([(945,742),(1180,742),(1180,689),(945,689)])
add(box(*P(268,178),4.4,11,7,11.2),0,'counter_pedestal')
add(slab(q,15.2,1.8),0,'counter_slab')
# Left ticket/display cabinet, two differently oriented faces.
cab=fp([(548,718),(590,718),(590,603),(572,603),(572,644),(526,644),(526,714),(548,714)])
add(slab(cab,5.0,23),0,'ticket_and_screen_cabinet')
# Visible yellow front on short left return; no legible UI or fabricated text.
add(box(*P(135.0,178.5),7.0,5.7,.85,18.0),5,'yellow_machine_face')
add(box(*P(135.0,179.0),19.0,4.7,.45,4.6),4,'ticket_machine_screen')
add(box(*P(146.9,162.5),18.0,.5,10.0,7.0),4,'side_information_display')
# Exactly 29 distinct load-column axes. Front visible first-floor points traced;
# upper/rear locations are cross-view inference, not survey coordinates.
front_pixels=[(511,839),(773,839),(1063,839),(642,794),(921,794),(464,722),(767,722),(955,722),(1134,722),(541,586),(632,586),(906,586),(1217,586),(756,499),(899,499),(1004,499),(1136,499),(1267,499)]
colxy=[P(x/4,y/4) for x,y in front_pixels]
rearpx=[(155,111),(170,73),(188,44),(216,63),(217,105),(221,142),(263,66),(276,91),(344,73),(323,111),(279,150)]
colxy +=[P(x,y) for x,y in rearpx]
from shapely.ops import nearest_points
colxy=[(q.x,q.y) for xy in colxy for q in [nearest_points(roofplan.buffer(-1.25),Point(*xy))[0]]]
assert len(colxy)==29
column_distances=np.linalg.norm(np.array(colxy)[:,None,:]-np.array(colxy)[None,:,:],axis=2)+np.eye(29)*1e6
assert column_distances.min()>3.0,'Near-duplicate load axes must be resolved in the generator, not waved through QA'
for i,(x,y) in enumerate(colxy):
 assert outer.buffer(.1).contains(Point(x,y)),(i,x,y)
 assert not slot.buffer(-.1).contains(Point(x,y)),(i,'in slot')
 top=roofz(y)-1.2
 add(cyl(x,y,2.4,top-2.4,.88),0,'load_column_%02d'%i)
 if y<20:
  add(cyl(x,y,top-7.2,7.0,1.03),8,'rope_wrap_%02d'%i)
  add(box(x+1.0,y,top-7.3,1.2,1.35,3.6),4,'simplified_lamp_%02d'%i)
# Unequal roof terrace groups. Tree wing is x-left as seen from the bus side.
# Rows stop around the open tree hole instead of covering it.
terraces=[(141,181,33,10),(147,169,31,10),(154,157,30,10),(161,145,30,10),(160,133,31,10),(155,121,34,10),(168,108,34,10),(174,91,30,11),(187,66,31,12),(195,50,33,12),(198,35.4,35,12),(198,22,35,12),
          (280,174,31,12),(280,148,31,12),(277,124,29,12),(316,102,44,12),(286,60,34,12),(308,35.4,29,12)]
terrace_records=[]
for i,(px,py,w,d) in enumerate(terraces):
 q=poly([(px-w/2,py+d/2),(px+w/2,py+d/2),(px+w/2+5,py-d/2),(px-w/2+5,py-d/2)])
 # Roof stair slabs meet the ramp at upper edge; horizontal wood tread on top.
 q=q.difference(tree_hole.buffer(.7)).difference(net_hole.buffer(.7)).difference(slot.buffer(.3))
 if q.is_empty:continue
 z=roofz(P(px,py)[1])+1.6
 add(slab(q,z-4.0,4.0),0,'roof_terrace_%02d'%i)
 add(slab(q.buffer(-.5,join_style=2),z-.10,.45),2,'roof_tread_%02d'%i)
 terrace_records.append(dict(center_pixel=[px,py],top_z=z,plan_bounds=list(q.bounds)))
# Rear approach terraces reach raised ground and visibly join the roof ramps.
for px,py,w,d in [(200,9,33,13),(312,26,28,10)]:
 q=poly([(px-w/2,py+d/2),(px+w/2,py+d/2),(px+w/2+5,py-d/2),(px-w/2+5,py-d/2)])
 z=15.5;add(slab(q,2.4,z-2.4),0,'rear_approach_step');add(slab(q.buffer(-.6),z-.1,.4),2,'rear_approach_wood')
# Guard posts and sparse open diamond ropes follow 2020 official photo + photo8.
# They are upper guardrail segments, NOT extra load-column axes.
railpaths=[[(117,216),(188,216),(264,216)],[(117,216),(108,186),(128,148),(154,111),(172,76),(190.35,44.2)],[(264,216),(282,186),(302,148),(324,111),(346,73),(365,44)],[(229,163),(222,110),(220,64)],[(239,163),(250,112),(262,65)]]
rail_records=[]
for pi,path in enumerate(railpaths):
 for j,(px,py) in enumerate(path):
  x,y=P(px,py);z=roofz(y)+.1
  add(cyl(x,y,z-.6,14.5,.68),0,f'guard_post_{pi}_{j}')
 for j,(aa,bb) in enumerate(zip(path,path[1:])):
  a=np.array(P(*aa));b=np.array(P(*bb));L=np.linalg.norm(b-a);N=max(3,int(L/4.8));rail_records.append(dict(a=a.tolist(),b=b.tolist(),height=13.2,cell_count=N))
  # Sagged top cable and bottom cable each remain attached to both posts.
  def pt(t,h):
   xy=a+(b-a)*t;return [*xy,roofz(xy[1])+h]
  for k in range(N):
   t0=k/N;t1=(k+1)/N
   add(rod(pt(t0,13.2-1.4*math.sin(math.pi*t0)),pt(t1,13.2-1.4*math.sin(math.pi*t1)),.45),3,'top_guard_rope')
   add(rod(pt(t0,1.2),pt(t1,1.2),.45),3,'bottom_guard_rope')
   # Coarse crossed mesh, no opaque infill panel.
   add(rod(pt(t0,1.2),pt(t1,12.2-1.4*math.sin(math.pi*t1)),.44),3,'diagonal_guard_net')
   add(rod(pt(t0,12.2-1.4*math.sin(math.pi*t0)),pt(t1,1.2),.44),3,'diagonal_guard_net')
# Open hanging net in the right roof hole. A curved grid, not a filled plate.
# Bilinear trapezoid coordinates; slight sag estimated from photo15.
corners=np.array([P(290,105),P(323,105),P(300,148),P(291,148)])
def netpt(u,v):
 a=corners[0]*(1-u)+corners[1]*u;b=corners[3]*(1-u)+corners[2]*u;xy=a*(1-v)+b*v
 return [*xy,roofz(xy[1])-.3-4.2*math.sin(math.pi*u)*math.sin(math.pi*v)]
for axis in [0,1]:
 for k in range(7):
  c=k/6
  for j in range(10):
   a=netpt(c,j/10) if axis==0 else netpt(j/10,c);b=netpt(c,(j+1)/10) if axis==0 else netpt((j+1)/10,c)
   add(rod(a,b,.48),3,'hanging_open_rope_net')
# Edge cables sit inside roof slab margin and anchor the net perimeter.
for a,b in zip(corners,np.roll(corners,-1,axis=0)):
 add(rod([*a,roofz(a[1])-.3],[*b,roofz(b[1])-.3],.7),3,'hanging_net_border')
# Union original components; preserve face provenance for editable materials.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
# Source-part provenance is retained on the unsimplified constructive mesh.
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
# Construction cleanup happens BEFORE the exported artifact exists. Resetting
# ancestor face IDs allows 0.0001 mm tolerance simplification of coincident
# boolean seams. Exported raw STL is thereafter audited without any repair.
m=m.as_original().set_tolerance(.0001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);max_material_distance=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500])
 assert dist.max()<.0002,dist.max()
 max_material_distance=max(max_material_distance,float(dist.max()))
 colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl')
# Read exported float32 triangles with exact equality only; no repair.
import struct
raw=(O/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=dict(estimated_not_surveyed=True,school='國立陽明交通大學',campus='光復校區',slug='nycu-south-gate-bus-shelter-2020',target_path='國立陽明交通大學/光復校區/buildings/nycu-south-gate-bus-shelter-2020',front_direction='negative Y',source_project_year=2020,source_area_m2=153,source_ground_height_difference_m=1.2,source_area_not_used_as_survey_scale=True,source_column_count=29,modeled_load_column_count=29,min_load_axis_distance_mm=float(column_distances.min()),column_position_method='18 approximate first-floor-plan points nudged onto roof margins where drawing registration differs, plus 11 rear points inferred from multiple photos and low-resolution roof plan; upper rail posts counted separately',columns_xy_mm=colxy,rear_inferred_column_indices=list(range(18,29)),load_column_diameter_mm=1.76,guard_post_diameter_mm=1.36,rope_diameter_mm=[.88,.90,.96],roof_thickness_vertical_mm=3,roof_front_level_mm=46,roof_rear_level_mm=roofz(P(0,41)[1]),roof_hinge_y_mm=hinge,roof_outer_xy=list(outer.exterior.coords),central_slot_xy=list(slot.exterior.coords),tree_hole_xy=list(tree_hole.exterior.coords),hanging_net_hole_xy=list(net_hole.exterior.coords),roof_terraces=terrace_records,rails=rail_records,plinth_dimensions_mm=[246,196,2.5],generator_boolean_tolerance_mm=.0001,material_provenance_nearest_surface_max_distance_mm=max_material_distance,plinth_is_printing_addition_not_site_geometry=True,approximate_terrain=True,source_appearance='2020 official photographed white mesh guardrail + photo8, not asserted 2026 condition',bare_post_photo_difference='Most Ivan Chuang publicity photos show bare upper posts; no unverified sequence or present state inferred',omitted=['trees but not tree aperture','cars and people','parking markings','accurate cable knot weave','tiny display text','underground footings and services'],uncertain=['all actual dimensions','exact posterior load-column positions','roof steel and soil build-up','landscape boundary','net tension and knot count','hidden joints'],no_actual_print=True,support_free_certified=False)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b in palette:el(bm,'base',{'name':a,'displaycolor':b+'FF'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
