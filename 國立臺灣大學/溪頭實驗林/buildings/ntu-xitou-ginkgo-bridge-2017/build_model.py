"""NTU Xitou Ginkgo Bridge: complete 2017 exterior approximation.
36 m = 8+20+8 m is authoritative; coordinates use a nominal 1:120 display scale.
Member sections, curve radii, approach/stair geometry and foundation exposure are
photo/drawing approximations, not engineering measurements. No 2014 40 m scheme.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Polygon,LineString,box as rect
from shapely.geometry.polygon import orient
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
def cross(p):
 loops=[]
 for q in (list(p.geoms) if p.geom_type=='MultiPolygon' else [p]):
  if q.is_empty:continue
  q=orient(q,sign=1);loops.append(np.array(q.exterior.coords[:-1]));loops.extend(np.array(a.coords[:-1]) for a in q.interiors)
 return CrossSection(loops)
def slab(p,z,h):return cross(p).extrude(h).translate((0,0,z))
def xz(p,y,d):return cross(p).extrude(d).transform(np.array([[1,0,0,0],[0,0,1,y],[0,1,0,0]],float))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def strip(p,t):return LineString(p).buffer(t/2,cap_style=2,join_style=1,quad_segs=5)
def rod(a,b,r=.4):
 a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;length=np.linalg.norm(d);zz=d/length
 q=np.array([0,0,1.]) if abs(zz[2])<.9 else np.array([1.,0,0]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cylinder(length+.08,r,r,10).transform(np.column_stack([xx,yy,zz,a-zz*.04]))
parts=[];material_for_id={};part_records=[]
palette=[('warm_cedar_glulam_main_structure','#9E603A',255),('darker_timber_railing_frames','#6D482F',255),('lighter_timber_walk_deck','#BB9366',255),('silver_gray_steel_bearings_and_bolts','#AAB6BA',255),('reinforced_concrete_piers_and_abutments','#A8AAA2',255),('added_display_print_base_not_terrain','#D5D1C5',255),('dark_underdeck_crossbeams_braces','#55594C',255),('fine_deck_board_joints','#725338',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
# Bridge datum: X along the straight 36 m main span; Y across the width.
# Left bank in official2017 drawing is negative X. Bend only the left APPROACH,
# not the main bridge plan. The nominal scale does not certify all inferred details.
L=150.;P=250./3.;SIDE=7.5;WIDTH=50./3.;FOOT=14.0;END=29.0;RISE=16.5
# Smooth Hermite spans: crest is slightly inward of each support, as seen in2017.
KNOTS=[(-150.,29.),(-78.,45.5),(0.,29.),(78.,45.5),(150.,29.)]
def profile(x):
 for (a,za),(b,zb) in zip(KNOTS,KNOTS[1:]):
  if x<=b:
   t=max(0.,min(1.,(x-a)/(b-a)));return za+(zb-za)*(3*t*t-2*t*t*t)
 return END
def line_profile(offset=0,step=1):return [(float(x),profile(float(x))+offset) for x in np.linspace(-L,L,int(2*L/step)+1)]
def profile_slab(y,depth,lower,upper):
 return xz(Polygon(line_profile(upper)+list(reversed(line_profile(lower)))),y,depth)
def bezier(a,c,b,n=35):
 return [(float((1-t)**2*a[0]+2*t*(1-t)*c[0]+t*t*b[0]),float((1-t)**2*a[1]+2*t*(1-t)*c[1]+t*t*b[1])) for t in np.linspace(0,1,n)]
# A transparent-in-description, physically solid connection plate, NOT site geology.
add(box(-6,-5,0,354,62,1.5),5,'added_thin_rectangular_display_print_base_not_real_terrain')
# RC piers: two width-spanning tapered solids, never four independent columns.
for i,px in enumerate([-P,P]):
 p=Polygon([(px-4.8,1.4),(px+4.8,1.4),(px+3.6,FOOT),(px-3.6,FOOT)])
 add(xz(p,-10.4,20.8),4,f'RC_main_pier_{i+1}_spans_bridge_width')
 # Four fans in total, two parallel planes on EACH pier.
 for side in [-1,1]:
  y=side*SIDE
  add(box(px,y,FOOT-.1,4.8,2.5,.55),3,f'steel_base_plate_pier{i+1}_side{side}')
  shoe=Polygon([(px-2.4,FOOT+.15),(px+2.4,FOOT+.15),(px+.55,FOOT+2.5),(px-.55,FOOT+2.5)])
  add(xz(shoe,y-1.05,.38),3,f'outer_steel_shoe_pier{i+1}_side{side}')
  add(xz(shoe,y+.67,.38),3,f'inner_steel_shoe_pier{i+1}_side{side}')
  # Near-side original photo four endpoints traceable. No extra rear-plane rib.
  endpoints=[-101.,-79.,-62.,-47.]
  controls=[(-87.,34.),(-82.,33.),(-77.,35.),(-72.,32.)]
  sign=1 if px<0 else -1
  for j,(ex,(cx,cz)) in enumerate(zip(endpoints,controls)):
   end=(sign*ex,profile(sign*ex)-.9);ctl=(sign*cx,cz);start=(px,FOOT+1.0)
   pts=bezier(start,ctl,end)
   add(xz(strip(pts,1.75 if j!=1 else 1.90),y-.63,1.26),0,f'primary_fan_pier{i+1}_side{side}_rib{j+1}_of4')
   # Readable large bolt heads, not a literal count of all real fasteners.
   for k in [2,5,15,24,31,34]:
    bx,bz=pts[k];add(rod((bx,y-.78,bz),(bx,y+.78,bz),.22),3,f'approx_rib_bolt_{i+1}_{side}_{j+1}_{k}')
  # Short visible secondary ties join ribs above the foot; not fifth radial ribs.
  for j,(a,b) in enumerate([((-101.,profile(-101.)-1),(-81.5,31.5)),((-79.,profile(-79.)-1),(-60.,34.0))]):
   add(xz(strip([(sign*a[0],a[1]),(sign*b[0],b[1])],.65),y-.40,.80),6,f'short_upper_secondary_tie_pier{i+1}_side{side}_{j+1}')
  # Widthwise ties connect paired fans; no extra radial same-plane members.
 for z,dx in [(21,0),(32,1.6)]:
  xx=px+(dx if px<0 else -dx)
  add(box(xx,0,z,.9,15.8,1.0),6,f'transverse_fan_tie_pier{i+1}_z{z}')
# End abutments carry all36m, not cropped to central20m. Exposed depth estimated.
for label,xx in [('left',-151.5),('right',151.5)]:
 add(box(xx,0,1.4,6.4,22.4,END-1.1),4,label+'_bank_abutment_exposed_approximation')
 add(box(xx,0,END-.1,6.4,WIDTH,.8),2,label+'_bank_landing_walk_surface')
# Slim underdeck, continuous walk surface and two deep waved longitudinal chords.
add(profile_slab(-WIDTH/2,WIDTH,-.65,.20),2,'continuous_double_crest_central_sag_timber_deck')
for side in [-1,1]:
 y=side*SIDE
 add(profile_slab(y-.83,1.66,-2.1,.9),0,f'waved_longitudinal_side_beam_side{side}')
 add(profile_slab(y-.48,.96,8.65,9.45),1,f'continuous_waved_handrail_side{side}')
 add(profile_slab(y-.42,.84,1.0,1.6),1,f'continuous_waved_lower_railing_rail_side{side}')
 # 30 regularised framed bays are a display simplification, not measured count.
 for j,x in enumerate(np.linspace(-150,150,31)):
  z=profile(float(x));add(box(float(x),y,z+.2,.85,1.66,9.15),1,f'railing_post_side{side}_{j+1}')
  add(box(float(x),y,z+.30,1.05,1.86,.75),3,f'post_steel_attachment_side{side}_{j+1}')
 for j in range(30):
  a=-150+j*10.;b=a+10.;za=profile(a);zb=profile(b)
  panel=Polygon([(a+.25,za+1.25),(b-.25,zb+1.25),(b-.25,zb+9.0),(a+.25,za+9.0)])
  mid=(a+b)/2
  # Ginkgo infill directions diverge near crests and reverse at central trough.
  # Central framed bays use a true small fan; others are complementary slants.
  if j in [6,7,8,21,22,23]:
   root=(mid,profile(mid)+1.1)
   for k,xx in enumerate(np.linspace(a-.3,b+.3,5)):
    q=strip([root,(float(xx),profile(float(xx))+9.1)],.55).intersection(panel)
    if not q.is_empty:add(xz(q,y-.30,.60),1,f'ginkgo_fan_infill_side{side}_bay{j+1}_ray{k+1}')
  else:
   direction=1 if (-150<mid<-78 or 0<mid<78) else -1
   for k,offset in enumerate(np.arange(-12,18,2.5)):
    q=strip([(a+offset,za+1.1),(a+offset+direction*7.5,za+9.4)],.55).intersection(panel)
    if not q.is_empty and q.area>.03:add(xz(q,y-.30,.60),1,f'directional_infill_side{side}_bay{j+1}_slat{k+1}')
 # Two bolt lines along main chord; modest stylised frequency only.
 for j,x in enumerate(np.linspace(-148,148,75)):
  for off in [-1.35,.15]:
   add(rod((float(x),y-.91,profile(float(x))+off),(float(x),y+.91,profile(float(x))+off),.18),3,f'approx_chord_bolt_side{side}_{j}_{off}')
# Deck boards regularised as shallow flush color joints, not slots through walking floor.
for i,x in enumerate(np.arange(-148.5,150,2.5)):
 z=profile(float(x));add(box(float(x),0,z+.17,.12,13.3,.08),7,f'approx_timber_deck_board_joint_{i+1}')
# Transverse joists and X bracing remain under the deck, open on both sides.
for i,x in enumerate(np.linspace(-148,148,61)):
 z=profile(float(x));add(box(float(x),0,z-1.7,.80,16.2,1.15),6,f'underdeck_transverse_joist_{i+1}')
for i in range(15):
 a=-150+i*20.+1;b=a+18
 for side in [-1,1]:
  add(rod((a,side*6.7,profile(a)-1.6),(b,-side*6.7,profile(b)-1.6),.37),6,f'underdeck_cross_brace_{i+1}_{side}')
# Short left landing and bent stepped continuation read from official2017 plan.
# These are bounded, approximate exterior approach pieces, not the full trail.
add(box(-158,0,1.4,9.2,20,END-1.1),4,'left_approach_landing_support')
add(box(-158,0,END-.05,9.2,WIDTH,.75),2,'left_approach_landing_walk')
# Turn the bounded stair run35degrees in plan, down toward the left/bottom.
angle=35.;dx,dy=-math.cos(math.radians(angle)),-math.sin(math.radians(angle))
for i in range(6):
 xx=-162+(i+.5)*3*dx;yy=(i+.5)*3*dy;top=END-.9-i*1.05
 # Each step solid connects with adjacent steps and explicitly added base below.
 add(box(0,0,1.4,3.2,16.7,top-1.4).rotate((0,0,angle)).translate((xx,yy,0)),4,f'left_bent_approach_stair_support_{i+1}')
 add(box(0,0,top,3.2,16.7,.55).rotate((0,0,angle)).translate((xx,yy,0)),2,f'left_bent_approach_timber_step_{i+1}')
# Approach rails use vertical closely set timber infill, visibly distinct from main fans.
for side in [-1,1]:
 yy=side*7.5
 for x in [-153.5,-158,-162]:add(box(x,yy,END,.85,1.0,9.3),1,f'left_landing_rail_post_{side}_{x}')
 add(box(-157.8,yy,END+8.6,9.4,1.,.8),1,f'left_landing_handrail_{side}')
 for j in range(9):add(box(-153.5-j,yy,END+.4,.4,.6,8.2),1,f'left_landing_vertical_picket_{side}_{j}')
 norm=np.array([-dy,dx]);a=np.array([-162.,0.])+norm*side*7.5;b=a+np.array([dx,dy])*18
 add(rod((a[0],a[1],END+8.8),(b[0],b[1],END+2.5),.45),1,f'left_bent_stair_sloped_handrail_{side}')
 for j in range(13):
  t=j/12;xy=a+(b-a)*t;z=END-.9-5.25*t
  add(box(float(xy[0]),float(xy[1]),z,.55,.55,9.3),1,f'left_bent_stair_rail_picket_{side}_{j}')
# Solid timber corner joint regularisation removes an unintended sealed microcavity
# where the straight and turned approach handrails overlap; no QA mesh healing.
add(box(-158.50,-7.35,37.05,1.15,1.15,.75),1,'left_approach_handrail_corner_join_block_approximate')
# Right bank ends at a short bounded level landing, no invented long approach.
add(box(157,0,1.4,5.8,20,END-1.1),4,'right_approach_landing_support')
add(box(157,0,END-.05,5.8,WIDTH,.75),2,'right_approach_landing_walk')
for side in [-1,1]:
 for j,x in enumerate(np.linspace(150,159.5,11)):
  add(box(float(x),side*7.5,END+.2,.50,.65,8.7),1,f'right_approach_vertical_picket_{side}_{j}')
 add(box(154.8,side*7.5,END+8.65,9.7,1.0,.8),1,f'right_approach_toprail_{side}')
FEATURES=dict(estimated_not_surveyed=True,school='國立臺灣大學',campus='溪頭實驗林',slug='ntu-xitou-ginkgo-bridge-2017',target_path='國立臺灣大學/溪頭實驗林/buildings/ntu-xitou-ginkgo-bridge-2017',name='銀杏橋（2017竣工外觀近似）',official_main_bridge_length_m=36,official_spans_m=[8,20,8],official_total_width_m=2.0,official_clear_width_m=1.6,official_bridge_height_m=3.08,bridge_height_definition_not_total_model_height=True,nominal_display_scale=120,main_span_model_mm=300,official2017_plan=True,not_2014_40m_angular_scheme=True,opening_date='2017-05-28',civil_works_completed='early April2017; environmental restoration before opening',individual_photo_capture_dates_unknown=True,main_bridge_straight_in_plan=True,deck_profile_knots_mm=KNOTS,main_pier_x_mm=[-P,P],RC_main_piers=2,fan_planes_per_pier=2,total_fans=4,primary_ribs_per_fan=4,primary_ribs_total=16,fan_side_y_mm=[-SIDE,SIDE],back_plane_not_counted_as_fifth_rib=True,primary_fan_left_endpoint_x_mm=[-101,-79,-62,-47],both_end_abutments=True,left_bent_stair_approach=True,right_short_landing=True,open_underside_and_between_fans=True,railing_fan_and_opposing_directions=True,railing_bays_per_side_approximate=30,minor_fittings_regularized=True,added_print_base=True,buried_foundations_not_reconstructed=True,uncertain=['all curve radii and precise heights','member cross sections and local steel details','wood board, bolt and railing subdivision counts','stair angle/count and exact landing dimensions','exposed foundation depth and site terrain'],omitted=['concealed combined foundations','forest landscape, rocks, streambed and full trail network','construction net, scaffolding, crane, temporary materials and people','source photographs, PDFs, original drawings and HTML'],not_2026_current_survey=True,no_actual_print=True,support_free_certified=False)
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.00005).simplify(.00005)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.05,(dist.max(),centers[start:start+500][dist.argmax()].tolist(),closest[dist.argmax()].tolist());maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_provenance_nearest_surface_max_distance_mm=maxdist,parts=part_records)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b,'alpha':c} for a,b,c in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
