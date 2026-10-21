"""TMU Dream-Way Building: complete bounded approximate EXTERIOR, no interior plan."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def cyl(x,y,z,r,h):return Manifold.cylinder(h,r,r,64).translate((x,y,z))
def extr(p,z,h):
 ps=[orient(q,sign=1) for q in (list(p.geoms) if p.geom_type=='MultiPolygon' else [p])]
 cs=CrossSection([list(q.exterior.coords)[:-1] for q in ps]+[list(h.coords)[:-1] for q in ps for h in q.interiors])
 return Manifold.extrude(cs,h).translate((0,0,z))
def beam(a,b,w=1.6,d=1.6):
 a=np.array(a,float);b=np.array(b,float);t=trimesh.creation.box((w,d,np.linalg.norm(b-a)));t.apply_transform(trimesh.geometry.align_vectors([0,0,1],b-a));t.apply_translation((a+b)/2)
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
parts=[]
def add(m,c):parts.append(m.set_properties(1,lambda pos,pr:[c]))
def curve(start,segments):
 pts=[start];s=np.array(start,float)
 for c1,c2,end in segments:
  a,b,e=map(lambda q:np.array(q,float),[c1,c2,end])
  for t in np.linspace(0,1,17)[1:]:pts.append(((1-t)**3*s+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*e).tolist())
  s=e
 return Polygon(pts)
main=curve((0,45),[
 ((25,45),(40,31),(55,16)),((64,7),(72,3),(84,3)),
 ((96,3),(106,-7),(106,-19)),((106,-31),(96,-41),(84,-41)),
 ((67,-41),(60,-29),(43,-33)),((28,-36),(23,-45),(0,-45)),
 ((-25,-45),(-45,-25),(-45,0)),((-45,25),(-25,45),(0,45))])
rear=Point(98,56).buffer(23,quad_segs=32)
neck=LineString([(56,18),(87,48)]).buffer(9,cap_style=1,join_style=1)
low=unary_union([main,rear,neck]).buffer(3).buffer(-3)
# Artificial thin neutral display plinth, not surveyed paving.
add(extr(low.buffer(7),0,3),1)
add(extr(low.buffer(2),3,2),2)
# Filled exterior envelope intentionally excludes all interior room/evacuation/security detail.
add(extr(low,4.8,60.2),0)
add(extr(main,64.8,27.2),0)
# Broad 2F silver fascia, thin 3F inter-floor band, broad main roof.
for p,z,h,b in [(low,36,3.3,5),(main,64,1.8,1.5),(main,91,3,6),(rear.union(neck),64,2.5,3)]:add(extr(p.buffer(b),z,h),2)
# Balcony solid-color glazing and top rail: geometric closed strips, opacity disclosed.
for p,z,h,b in [(low,39.2,6.4,4.3),(main,94,6.6,5.3),(rear.union(neck),66.3,5.7,2.4)]:
 ring=p.buffer(b).difference(p.buffer(b-1.15));add(extr(ring,z,h),3);add(extr(ring.buffer(.15),z+h-.5,.9),2)
# Main/front perimeter continuous two-storey white columns, and thin vertical glazing bars.
def facade(p,z0,z1,spacing,column_every):
 line=p.exterior;N=max(12,round(line.length/spacing))
 for i in range(N):
  q=line.interpolate(i*line.length/N);x,y=q.x,q.y
  add(cyl(x,y,z0,.62,z1-z0),2)
  if i%column_every==0:add(cyl(x,y,36.8,1.25,55),2)
facade(main,4.8,91.3,5.8,4)
# Rear window rhythm is deliberately regularized, not per-window reconstruction.
for i in range(24):
 a=2*math.pi*i/24;x=98+23*math.cos(a);y=56+23*math.sin(a)
 add(cyl(x,y,4.8,.65,59.7),2)
# Ground glazing horizontal transom and second/third storey slim horizontal strips.
for p,z in [(low,18),(main,50),(main,78)]:add(extr(p.buffer(.6).difference(p.buffer(-.35)),z,.9),2)
# Front stair turret rises above main roof; opaque gray-green glazing and wide cap.
add(cyl(84,-19,92,18,20),0)
for i in range(20):
 a=2*math.pi*i/20;add(cyl(84+18*math.cos(a),-19+18*math.sin(a),92,.65,20),2)
add(cyl(84,-19,111.5,23,2.2),2)
# Rectilinear glass entrance canopy, perimeter/joist frame and diagonal brackets.
add(box(66,-43,31.7,63,20,1.5),3)
for y in [-52.4,-33.6]:add(box(66,y,31.1,64,1.5,2.1),2)
for x in [35,50.5,66,81.5,97]:add(box(x,-43,31,1.5,20,2),2)
for x in [42,91]:add(beam((x,-35,23),(x,-50,32),1.8,1.8),2)
# Entrance steps attach display plinth and model; no exact stairs surveyed.
for z,y,d in [(2.8,-52,10),(3.5,-49,8),(4.2,-46,6)]:add(box(67,y,z,64,d,1.2),2)
# Exterior rear arc stair: simplified attached rising flights, no evacuation diagram reproduced.
for z0 in [5,38]:
 for i in range(22):
  a=math.radians(66+i*2.9);b=math.radians(66+(i+1)*2.9);z=z0+i*(27/22)
  poly=Polygon([(r*math.cos(t),r*math.sin(t)) for r,t in [(42.5,a),(53,a),(53,b+.008),(42.5,b+.008)]])
  add(extr(poly,z,1.8),2)
  if i%3==0:add(cyl(52*math.cos(a),52*math.sin(a),z,.7,6),2)
 # one continuous sloping rectangular rail, avoiding near-coincident segmented beams
 verts=[]
 for j in range(23):
  a=math.radians(66+j*2.9);zz=z0+5.3+j*27/22
  verts.extend([(r*math.cos(a),r*math.sin(a),zz+dz) for r,dz in [(51.3,0),(52.7,0),(52.7,1.4),(51.3,1.4)]])
 faces=[]
 for j in range(22):
  for k in range(4):
   a=j*4+k;b=j*4+(k+1)%4;c=b+4;d=a+4;faces.extend([(a,b,c),(a,c,d)])
 faces.extend([(0,2,1),(0,3,2),(88,89,90),(88,90,91)])
 tt=trimesh.Trimesh(verts,faces,process=False)
 if tt.volume<0:tt.invert()
 assert tt.is_watertight
 add(Manifold(Mesh(np.array(tt.vertices,dtype=np.float32),np.array(tt.faces,dtype=np.uint32))),2)
print('invalid parts',[(i,p.status().name) for i,p in enumerate(parts) if p.status().name!='NoError'],flush=True)
m=Manifold.batch_boolean(parts,OpType.Add);print('union status',m.status().name,flush=True);assert m.status().name=='NoError'
m=m.simplify(.002) # generator-level 0.002 mm contour simplification, before any exports/QA
me=m.to_mesh64();vv=np.asarray(me.vert_properties);ff=np.asarray(me.tri_verts)
colors=np.rint(vv[ff,3].mean(axis=1)).astype(int)
wv,wi=np.unique(vv[:,:3],axis=0,return_inverse=True)
t=trimesh.Trimesh(wv.astype(np.float32).astype(np.float64),wi[ff],process=False) # compute STL normals from its actual quantized coordinates
assert t.is_watertight and t.is_winding_consistent and t.volume>0
# exact-weld actual raw float32 STL, face order preserved
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);t=trimesh.Trimesh(v,f,process=False)
palette=[('opaque_gray_green_glazing','#536D70'),('neutral_display_plinth','#AAA99F'),('silver_white_structure','#D6D9D5'),('opaque_balcony_glazing','#91ACAA')]
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,main_circle_radius_mm=45,front_turret_center_mm=[84,-19],rear_wing_center_mm=[98,56],main_roof_z_mm=94,rear_terrace_z_mm=66.5,front_cap_top_mm=113.7,rear_wing_floors=2,rear_terrace_at_floor=3,glazing_opaque=True,filled_exterior_no_interior=True,front_rectangular_canopy=True,back_arc_stairs_simplified=True,rear_window_counts_inferred=True,opening_date='2018-06-01',public_form_construction_year='2019; distinct source field, unresolved discrepancy',minimum_nominal_glazing_bar_diameter_mm=1.24,actual_print_tested=False),indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
# Deterministic 3MF, material assigned per triangle. Display materials, not extruder mapping.
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
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(trimesh.graph.connected_components(t.face_adjacency,nodes=np.arange(len(t.faces)),engine='scipy')),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
