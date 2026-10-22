"""NYCU Guangfu Huang Courtyard: 2024 project-photo bounded complete pavilion.
One curved wafer shell, seven open-grid rows, seven left half-steps, rear rail.
Dimensions are approximate display millimetres; no measured or current-state claim.
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
def yz(p,x,w):return cross(p).extrude(w).transform(np.array([[0,0,1,x],[1,0,0,0],[0,1,0,0]],float))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def strip(p,t):return LineString(p).buffer(t/2,cap_style=2,join_style=1,quad_segs=8)
def rod(a,b,r=.4):
 a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;length=np.linalg.norm(d);zz=d/length
 q=np.array([0,0,1.]) if abs(zz[2])<.9 else np.array([1.,0,0]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cylinder(length+.10,r,r,12).transform(np.column_stack([xx,yy,zz,a-zz*.05]))
parts=[];material_for_id={};part_records=[]
palette=[('brushed_stainless_curved_wafer_shell','#B2BAC1',255),('stainless_open_grid_treads_and_front_beams','#A7B3BD',255),('dark_steel_diagonal_fins_and_ribs','#687783',255),('silver_side_half_steps_and_rear_handrail','#CDD5D9',255),('deep_blue_translucent_seat_cushions','#245FBA',200),('pale_blue_translucent_seat_cushions','#7EB3D4',180),('clear_white_translucent_seat_cushions','#D9E8EC',155)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def line(a,b,name,r=.4,col=5):add(rod(a,b,r),col,name)

# Photo-bounded display dimensions, not a surveyed architectural scale.
R=80.;BEND=-10.;THICK=1.65
# Front disk is horizontal. Rear is visibly curved, NOT a single inclined plane.
def shellz(y):
 u=max(0.,y-BEND)
 return THICK+.43*u+.00115*u*u
profile=[(float(y),shellz(y)) for y in np.linspace(-80,80,201)]
profile+= [(y,z-THICK) for y,z in profile[::-1]]
disk=Manifold.cylinder(100,R,R,256)
add(yz(Polygon(profile),-R,2*R)^disk,0,'continuous_front_flat_disk_and_curved_raised_rear_shell')
# Plan circle used only for tread boundaries; open grid is actual geometry.
from shapely.geometry import Point
circle=Point(0,0).buffer(R-.25,quad_segs=64)
ROWS=[]
for i in range(7):
 yf=-10+i*11.3;yb=yf+11.3;z=shellz(yb)+.25
 plan=circle.intersection(rect(-90,yf,90,yb))
 # Coarser-than-real grid: visible holes, no solid risers or filled stepped wedge.
 bars=[];grid=[]
 for x in np.arange(-80,80.01,2.4):
  q=plan.intersection(rect(float(x)-.28,yf,float(x)+.28,yb))
  if not q.is_empty and q.area>.02:grid.append(q)
 for y in np.arange(yf+.2,yb,2.4):
  q=plan.intersection(rect(-90,float(y)-.28,90,float(y)+.28))
  if not q.is_empty:grid.append(q)
 from shapely.ops import unary_union

 # Front and back members remain thin. Circular edge side trim follows the footprint.
 perim=[plan.intersection(rect(-90,yy-.4,90,yy+.4)) for yy in [yf+.35,yb-.35]]
 perim.append(plan.intersection(circle.difference(circle.buffer(-.65))))
 bars.append(slab(unary_union(grid+perim),z,.85))
 lower=plan.buffer(-.08).intersection(unary_union([rect(-90,yy-.32,90,yy+.32) for yy in [yf+.35,yb-.35]]))
 bars.append(slab(lower,z-.55,.75))
 add(Manifold.batch_boolean(bars,OpType.Add),1,f'row_{i+1}_true_open_grid_tread')
 # Oblique fins beneath every row, connecting shell to front beam. Major air is preserved.
 width=math.sqrt(R*R-yb*yb)-1
 xs=list(np.arange(-width+1,width,12))
 for j,x in enumerate(xs):
  ys=yf+.8;ye=yb-.35
  fin=Polygon([(ys,shellz(ys)-.12),(ye,z-.3),(ye,z+.15),(ys+2.2,z+.15)])
  add(yz(fin,float(x)-.48,.96),2,f'row_{i+1}_diagonal_fin_{j+1}')
 # Slender visible transverse rib below grate, no backing riser.
 add(box(0,yf+6,z-.8,2*math.sqrt(R*R-(yf+6)**2)-2.5,.65,1.05),2,f'row_{i+1}_underside_cross_rib')
 # Offset left half-step between each seat level, not another seating row.
 xstep=-math.sqrt(R*R-yf*yf)+15.0
 base=THICK if i==0 else ROWS[-1]['z']+.85
 steptop=base+(z+.85-base)/2
 # U-section tread/face/side cheeks retains under-step hollow; tiny inscriptions omitted.
 stepy=yf-3.1
 add(box(xstep,stepy,steptop-.8,17,6.4,.8),3,f'left_half_step_{i+1}_tread')
 add(box(xstep,stepy-2.8,base-.05,17,.8,steptop-base+.05),3,f'left_half_step_{i+1}_front_face')
 for xx in [xstep-8.1,xstep+8.1]:add(box(xx,stepy,base-.05,.8,6.4,steptop-base+.05),3,f'left_half_step_{i+1}_side_cheek')
 ROWS.append(dict(row=i+1,y_front=yf,y_back=yb,z=z,half_step_x=xstep,half_step_top=steptop,fin_x=xs))
# Rear/side single handrail only. Continuous arch drops into two front returns.
def railpoint(t):
 x=(R-.65)*math.cos(t);y=(R-.65)*math.sin(t)
 return (x,y,shellz(y)+16)
theta=np.linspace(-.126,math.pi+.126,150)
rail=[railpoint(float(t)) for t in theta]
def tube(path,r=.62,n=16):
 path=np.array(path,float);v=[];f=[]
 for i,p in enumerate(path):
  tang=path[min(i+1,len(path)-1)]-path[max(0,i-1)];tang/=np.linalg.norm(tang)
  xx=np.cross([0,0,1],tang);xx/=np.linalg.norm(xx);yy=np.cross(tang,xx)
  for t in np.linspace(0,2*math.pi,n,endpoint=False):v.append(p+r*(xx*math.cos(t)+yy*math.sin(t)))
 for i in range(len(path)-1):
  for j in range(n):
   k=(j+1)%n;a=i*n+j;b=i*n+k;c=(i+1)*n+k;d=(i+1)*n+j;f.extend([[a,b,c],[a,c,d]])
 v.extend([path[0],path[-1]]);c0=len(v)-2;c1=len(v)-1
 for j in range(n):
  k=(j+1)%n;f.extend([[c0,k,j],[c1,(len(path)-1)*n+j,(len(path)-1)*n+k]])
 return Manifold(Mesh(np.array(v,dtype=np.float32),np.array(f,dtype=np.uint32)))
add(tube(rail),3,'single_continuous_swept_rear_half_arc_handrail')
# Both forward rail ends fold down onto the low disk; never a stage ring.
for j,p in enumerate([rail[0],rail[-1]]):
 q=(p[0],p[1]-4.2,THICK+.1)
 add(rod(p,q,.62),3,f'forward_downfold_handrail_return_{j+1}')
# Source-visible supports are simplified to nine spaced rear and side posts.
for j,t in enumerate(np.linspace(.12,math.pi-.12,9)):
 p=railpoint(float(t));q=(p[0]*.99,p[1]*.99,shellz(p[1]*.99)-.15)
 add(rod(q,p,.50),3,f'back_and_side_handrail_support_{j+1}')
# 41 visible seat cushions from completed photograph06, independently counted.
# Explicit irregular positions (front view left=-X); never an equal-count layout.
SEATS=[[-49,-39,-19,-13,-7,13,21,40,47,64],[-45,-23,-15,10,18,36,48,67],[-43,-26,-8,13,27,46,63],[-32,-17,-1,18,30,52,62],[-22,-1,10,46],[-18,24,37],[13,26]]
# Circular shallow dish top plus a front downward semicircular skirt, not a chair/ball.
def cushion(x,y,z,rad=2.75):
 vv=[[x,y,z+.45],[x,y,z-.15]];ff=[];rings=[];n=36
 for rho in [.55,1.15,1.85,2.4,rad]:
  ring=[]
  for t in np.linspace(0,2*math.pi,n,endpoint=False):
   ring.append(len(vv));vv.append([x+rho*math.cos(t),y+rho*math.sin(t),z+.45+.48*(rho/rad)**2])
  rings.append(ring)
 for j in range(n):ff.append([0,rings[0][j],rings[0][(j+1)%n]])
 for ra,rb in zip(rings[:-1],rings[1:]):
  for j in range(n):k=(j+1)%n;ff.extend([[ra[j],rb[j],rb[k]],[ra[j],rb[k],ra[k]]])
 lower=[]
 for t in np.linspace(0,2*math.pi,n,endpoint=False):lower.append(len(vv));vv.append([x+rad*math.cos(t),y+rad*math.sin(t),z-.15])
 for j in range(n):
  k=(j+1)%n;ff.extend([[rings[-1][j],lower[j],lower[k]],[rings[-1][j],lower[k],rings[-1][k]],[1,lower[k],lower[j]]])
 dish=Manifold(Mesh(np.array(vv,dtype=np.float32),np.array(ff,dtype=np.uint32)))
 # Front skirt joins top dish with overlap and hangs below the edge beam.
 skirt=Polygon([(x-rad,z+.4),(x+rad,z+.4)]+[(x+rad*math.cos(t),z+.4-rad*.72*math.sin(t)) for t in np.linspace(0,math.pi,37)])
 return dish+xz(skirt,y-rad+.10,.85)
seat_records=[]
for i,row in enumerate(ROWS):
 for j,x in enumerate(SEATS[i]):
  col=(6 if i>=3 else (4 if j%3 else 5))
  if i==0 and j<2:col=6
  if i==3 and j in [2,4]:col=5
  if i>=5:col=5
  y=row['y_front']+2.5;z=row['z']+.85
  add(cushion(x,y,z),col,f'row_{i+1}_photo06_cushion_{j+1}')
  seat_records.append(dict(row=i+1,index=j+1,x=x,y=y,z=z,material=col))
FEATURES=dict(estimated_not_surveyed=True,school='國立陽明交通大學',campus='光復校區',slug='nycu-huang-courtyard',target_path='國立陽明交通大學/光復校區/buildings/nycu-huang-courtyard',project_year=2024,source_publication='2024-06-19',individual_photo_capture_dates_unknown=True,all_20_source_jpegs_no_EXIF_dates=True,front_direction='negative Y',reported_area_m2=50,display_diameter_mm=160,display_dimensions_not_survey_scale=True,seat_rows=7,left_half_steps=7,step_words_omitted=['道','天','地','將','法','容','易'],seat_counts_front_to_back=[len(x) for x in SEATS],visible_cushion_total=41,cushion_count_scope='41 discernible cushions in photo06, not an official permanent inventory',seat_records=seat_records,rows=ROWS,grating_pitch_mm=2.4,grating_web_mm=.56,grating_depth_mm=.85,rear_shell_equation='z=1.65+0.43*u+0.00115*u^2, u=max(0,y+10); approximate visible bend, not a flat tilted circle',rear_shell_vertical_thickness_mm=THICK,rail_radius_mm=.62,rail_post_radius_mm=.5,rear_rail_posts_simplified=9,front_stage_ring_rail=False,no_landscape_plinth=True,uncertain=['all absolute dimensions, curvature and spacing','support fin counts and cross-sections','grating density reduced for model readability','cushion positions and per-cushion color simplified from perspective photo','rail supports simplified; exact foot anchoring not surveyed'],omitted=['neighboring science building and triangular courtyard skylight','people, signs, surrounding pavement and drains','fine safety wires, LED strips, tiny joints and wafer floor etching','portrait and long rear inscriptions; step wording not modeled at this scale','unseen foundations','source originals and crops'],physical_cushions_solid=True,STL_has_no_transparency=True,no_actual_print=True,support_free_certified=False)
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
