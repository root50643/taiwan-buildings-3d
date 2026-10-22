"""NCKU 56 Pavilion / Rotate Truss Pavilion. Photo/drawing based, NOT measured.
Single inclined tapered PC roof, two inverted triangular salvaged timber trusses.
2021 built; 2022 unveiling; 2023 official photo is independent capture evidence.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('charcoal_new_steel','#363A3C',255),('salvaged_timber_brown','#92705A',255),('concrete_footings_steps','#B7B5A8',255),('plastic_wood_deck','#82604D',255),('translucent_PC_roof_display_alpha','#D2E1DE',112),('light_sign_front','#E9EEF1',255),('metal_bolts_drain','#697174',255),('dark_timber_laminations','#765643',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(origin,size):return Manifold.cube(size).translate(origin)
def prism(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def beam(a,b,w,d=None):
 a=np.asarray(a,float);b=np.asarray(b,float);zz=b-a;L=np.linalg.norm(zz);zz/=L
 q=np.array([0.,0.,1.]) if abs(zz[2])<.9 else np.array([1.,0.,0.]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cube((d or w,w,L)).translate((-(d or w)/2,-w/2,0)).transform(np.column_stack([xx,yy,zz,a]))
def rod(a,b,r,n=16):
 a=np.asarray(a,float);b=np.asarray(b,float);zz=b-a;L=np.linalg.norm(zz);zz/=L
 q=np.array([0.,0.,1.]) if abs(zz[2])<.9 else np.array([1.,0.,0.]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cylinder(L,r,r,n).transform(np.column_stack([xx,yy,zz,a]))
def width(x):return 28.+x/12.
def roof(x):return 108.25+69.5*x/168.
def side(x,s,z,offset=0):return (x,s*(width(x)+offset),z)
# Display millimetres; source plan 365/475 proportions, NO unit/survey assertion.
COLS=[-84.,11.,84.];DECK=[(-104,-width(-104)-1), (88,-width(88)-1),(88,width(88)+1),(-104,width(-104)+1)]
# No invented ground slab: air remains beneath the entire elevated tapered deck.
deck=prism(DECK,11.,3.)
for x in np.arange(-101.,88.,3.4):deck-=box((x,-42,13.65),(.28,84,.5))
add(deck,3,'tapered_elevated_plastic_wood_deck_with_shallow_transverse_joints')
# Broad-end centred graduated concrete steps; isolated surrounding stepping stones omitted.
for i,(x,w,z,top) in enumerate([(88,54,0,3.),(88,50,0,6.),(88,46,0,9.),(88,42,0,12.)]):
 length=[18,13,8,3][i];add(box((x-.2,-w/2,z),(length+.2,w,top-z)),2,f'high_wide_end_concrete_step_{i+1}')
# Offset side blocks flanking the central treads, as in built high-end photograph.
for side_y in [-1,1]:
 for i,(length,w0,w1,top) in enumerate([(13.,25.,34.,3.),(8.,23.,35.,6.)]):
  y0=side_y*w0 if side_y==1 else -w1
  add(box((87.8,y0,0),(length+.2,w1-w0,top)),2,f'high_end_lateral_offset_block_{side_y}_{i}')
# Narrow end only a short oblique joining panel, not neighbouring building walkway.
add(prism([(-103.8,19.34),(-116,12),(-122,-11),(-103.8,-19.34)],10.9,2.6),2,'narrow_low_end_oblique_connection_panel')
for s in [-1,1]:
 add(beam(side(-104,s,11),side(88,s,11),3.,2.5),0,f'deck_edge_frame_{s}')
 for i,x in enumerate(COLS):
  y=s*width(x);add(box((x-4.3,y-4.3,0),(8.6,8.6,5.2)),2,f'footing_{s}_{i}_lower')
  add(box((x-3.5,y-3.5,5.),(7,7,2)),2,f'footing_{s}_{i}_upper')
  add(box((x-2,y-2,6.8),(4,4,.9)),0,f'base_plate_{s}_{i}')
  top=roof(x)-1.2 if x==84 else 70.4
  add(box((x-1.65,y-1.65,7.5),(3.3,3.3,top-7.5)),0,f'ground_column_{s}_{i}_of_six')
 add(beam(side(-88,s,69.7),side(84,s,69.7),3.8,3.),0,f'horizontal_long_perimeter_{s}')
 add(beam(side(11,s,68.5),side(84,s,roof(84)-1.4),5.2,3.4),0,f'rising_high_half_steel_diagonal_{s}')
for x in COLS:
 add(beam(side(x,-1,11),side(x,1,11),2.8,3),0,f'underdeck_crossbeam_{x}')
 add(beam(side(x,-1,69.7),side(x,1,69.7),3.6,3),0,f'horizontal_transverse_frame_{x}')
# Two genuine triangular trusses in converging vertical planes. Original long base
# follows single roof slope; former pitched top chords form the lower folded outline.
A=np.array([-79.,roof(-79)-4.7]);C=np.array([80.,roof(80)-4.7]);M=(A+C)/2
u=(C-A)/np.linalg.norm(C-A);down=np.array([u[1],-u[0]]);B=M+down*31.5
upper=[A+(C-A)*t/6 for t in range(7)];lower=[]
for i,P in enumerate(upper):
 if i==0:Q=A
 elif i==6:Q=C
 else:
  a,b=(A,B) if i<=3 else (B,C);mat=np.column_stack([down,-(b-a)]);d,t=np.linalg.solve(mat,a-P);Q=P+down*d
 lower.append(Q)
TIMBER=[]
for s in [-1,1]:
 def pt(p,off=0):return side(float(p[0]),s,float(p[1]),off)
 for label,p,q in [('long_inclined_base_chord',A,C),('lower_left_fold',A,B),('lower_right_fold',B,C)]:
  add(beam(pt(p),pt(q),4.4,2.8),1,f'truss_{s}_{label}');TIMBER.append(dict(name=f'truss_{s}_{label}',a=pt(p),b=pt(q),width=4.4,depth=2.8))
 for i in range(1,6):
  # Paired visible board laminations on the transverse ties, not invented X lattices.
  for off in [-1.55,1.55]:add(beam(pt(upper[i],off),pt(lower[i],off),3.4,1.3),7,f'truss_{s}_double_tie_{i}_{off}')
  if i<3:p,q=lower[i],upper[i+1]
  elif i>3:p,q=upper[i-1],lower[i]
  else:continue
  add(beam(pt(p),pt(q),2.1,2.7),1,f'truss_{s}_diagonal_web_{i}');TIMBER.append(dict(name=f'truss_{s}_diagonal_web_{i}',a=pt(p),b=pt(q),width=2.1,depth=2.7))
 for i,p in enumerate(upper[1:-1]+lower[1:-1]):
  add(rod(pt(p,-2.4),pt(p,2.4),.58,12),6,f'truss_{s}_representative_bolt_{i}')
 # Small saddles connect timber low fold to horizontal steel beam.
 for i in [1,2,3]:
  p=lower[i];add(beam(side(float(p[0]),s,70.2),pt(p),1.5,1.7),0,f'truss_{s}_small_support_saddle_{i}')
# Single planar roof: tapered sheet; the angle is an approximation from built views.
# Thickness 0.9 vertical (0.83 normal) strengthened model interpretation, not real PC thickness.
roofpoly=[(-90,-width(-90)-4.5),(90,-width(90)-4.5),(90,width(90)+4.5),(-90,width(-90)+4.5)]
R=prism(roofpoly,0,.9).transform(np.array([[1,0,0,0],[0,1,0,0],[69.5/168,0,1,108.25]]))
add(R,4,'single_inclined_tapered_translucent_PC_sheet')
for s in [-1,1]:
 add(beam(side(-90,s,roof(-90),4.5),side(90,s,roof(90),4.5),1.2,1.4),6,f'roof_edge_strip_{s}')
 add(beam(side(-86,s,roof(-86)-1.5),side(85,s,roof(85)-1.5),2.5,2.4),0,f'roof_long_support_{s}')
# Two internal longitudinal ribs + transverse PC grid (representative subdivisions).
for frac in [-.33,.33]:
 add(beam((-90,frac*(width(-90)+4.5),roof(-90)-.45),(90,frac*(width(90)+4.5),roof(90)-.45),1.2,1.2),0,f'roof_long_internal_grid_{frac}')
for i,x in enumerate(np.linspace(-90,90,11)):
 add(beam((x,-width(x)-4.5,roof(x)-.5),(x,width(x)+4.5,roof(x)-.5),1.2,1.3),0,f'roof_transverse_grid_{i}')
for x in [-88,86]:
 add(beam((x,-width(x)-3,roof(x)-2.5),(x,width(x)+3,roof(x)-2.5),3.5,2.4),0,f'roof_end_drain_beam_{x}')
# Short visible low eave pipe: hidden run and plumbing are intentionally not invented.
add(rod(side(-84,1,70.7,2),side(-84,1,9.,2),.75,16),6,'low_end_visible_drain_downpipe')
add(rod(side(-84,1,9.,2),(-91,width(-84)+2,7.5),.75,16),6,'low_end_visible_drain_elbow')
# One stylised '56亭' sign, only signed long side. Opposite sees its actual back.
# Original logo typography simplified to editable joined strokes. Dark metal back rails.
def signpt(x,z,offset=0):return (x+.24*(z-72),-width(x+.24*(z-72))-2.5+offset,z)
def stroke(a,b,w,col,name,depth=.9,off=0):add(beam(signpt(*a,off),signpt(*b,off),w,depth),col,name)
S5=[((36,89),(47,89)),((36,89),(36,81)),((36,81),(47,81)),((47,81),(47,72)),((36,72),(47,72))]
S6=[((50,89),(61,89)),((50,89),(50,72)),((50,81),(61,81)),((61,81),(61,72)),((50,72),(61,72))]
ST=[((69,91),(69,89)),((63,89),(77,89)),((65,86),(75,86)),((65,86),(65,82)),((75,86),(75,82)),((65,82),(75,82)),((63,79),(77,79)),((70,79),(70,72)),((67,72),(70,72))]
for letter,strokes in [('5',S5),('6',S6),('ting',ST)]:
 for i,(a,b) in enumerate(strokes):
  stroke(a,b,1.9,0,f'sign_{letter}_{i}_metal_back',1.25,0)
  stroke(a,b,1.25,5,f'sign_{letter}_{i}_light_front',.5,-.7)
for x in [37,52,67]:stroke((x,69.7),(x,90),.85,0,f'sign_back_mount_{x}',.9,.6)
stroke((35,70.5),(78,70.5),1.4,0,'single_sign_lower_mount',1.2,.6)
FEATURES=dict(name='56亭 / Rotate Truss Pavilion',school='國立成功大學',campus='成功校區',slug='ncku-56-rotate-truss-pavilion',target_path='國立成功大學/成功校區/buildings/ncku-56-rotate-truss-pavilion',built_year=2021,unveiling_date='2022-11-11',official_news_published='2022-11-15',official_photo_capture='2023-08-07 12:07:31; EXIF no timezone',official_photo_upload='2023-08-09',designer_photos_undated=True,designer_drawings_not_certified_as_built=True,estimated_not_surveyed=True,display_dimensions_not_survey_scale=True,single_planar_roof=True,roof_slope_degrees=math.degrees(math.atan(69.5/168)),roof_z_intercept_mm=108.25,roof_slope=69.5/168,roof_sheet_vertical_thickness_mm=.9,roof_sheet_normal_thickness_mm=.9/math.sqrt(1+(69.5/168)**2),roof_plan=roofpoly,deck_plan=DECK,deck_z=[11.,14.],deck_underside_air=True,ground_column_x_mm=COLS,ground_columns=6,column_bay_ratio_high_to_low=[365,475],column_halfwidth_function='28 + x/12',two_inverted_triangular_trusses=True,truss_upper_nodes=[p.tolist() for p in upper],truss_lower_nodes=[p.tolist() for p in lower],timber_members=TIMBER,high_wide_end_steps=4,central_step_widths_bottom_to_top_mm=[54,50,46,42],high_end_lateral_offset_blocks=4,low_narrow_end_oblique_panel=True,single_sign_front_side='negative Y only; rear is reverse of same sign',no_second_sign=True,all_materials_opaque=False,display_roof_alpha=112,STL_has_no_transparency=True,representative_PC_grid=True,representative_bolt_count=True,no_actual_print=True,support_free_certified=False,uncertain=['all absolute dimensions and fine proportions','roof slope chosen from built images not measured','PC grid subdivision count and thickness','bolt counts, doubled timber laminations and defects','footing exposure, slab thickness and steps','simplified stylised sign lettering','short visible drain and hidden drain route'],omitted=['courtyard buildings and demolished classrooms','loose furniture, plants, trees and people','adjacent long walkway and scattered stepping stones','hidden foundations/drainage/electrics','photographic weathering and timber chalk numbers','raw source photos drawings PDFs and HTML'])
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.001).simplify(.001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
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
