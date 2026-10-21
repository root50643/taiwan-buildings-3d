"""NTHU Yuning Island pavilion, 2023 as-built source-bounded approximation. Normalized approximate millimeters, not survey."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def solid(t):
 if t.volume<0:t.invert()
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
def hull(points):return solid(trimesh.convex.convex_hull(np.array(points)))
def beam(a,b,w=2,d=2):
 a=np.array(a,float);b=np.array(b,float);t=trimesh.creation.box((w,d,np.linalg.norm(b-a)));t.apply_transform(trimesh.geometry.align_vectors([0,0,1],b-a));t.apply_translation((a+b)/2);return solid(t)
def roof_ring(r0,r1,z0,z1,thick):
 q=[]
 for r,z in [(r0,z0),(r1,z1)]:
  q.append([(sx*r,sy*r,z+dz) for dz in [-thick,0] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
 # four trapezoid solid boards; union at corner seams
 return [hull([q[0][j] for j in [i,(i+1)%4,i+4,(i+1)%4+4]]+[q[1][j] for j in [i,(i+1)%4,i+4,(i+1)%4+4]]) for i in range(4)]
# Model design millimetres only: no measured scale. x long axis; +y lake, -y land.
parts=[box(0,0,0,142,102,3)] # artificial connected display support, not lake bed
# Three observed lake-edge piers; landward hidden foundation simplified as continuous support.
for x in [-50,0,50]:parts.append(box(x,30,2.5,9,9,15))
parts.append(box(0,-30,2.5,106,9,15))
parts.extend([box(0,30,14,112,10,4),box(0,0,17,128,86,4)])
for x in [-50,0,50]:
 for y in [-30,30]:parts.append(box(x,y,20,5.5,5.5,61))
for y in [-30,30]:parts.append(box(0,y,77,106,5.5,5))
for x in [-50,50]:parts.append(box(x,0,77,5.5,66,5))
# Four-slope HIP roof: ridge x=-20..20, y=0; no open gable.
def hip(eavez,ridgez):return hull([(-66,-45,eavez),(66,-45,eavez),(66,45,eavez),(-66,45,eavez),(-20,0,ridgez),(20,0,ridgez)])
roof=hip(82,101)-hip(78.8,97.8)
parts.append(roof)
# Coarse roof course relief; exact waves/count omitted to avoid fragile micron-scale intersections.
for t in [i/11 for i in range(1,11)]:
 x=66-46*t;y=45*(1-t);z=82+19*t
 for a,b in [((-x,-y,z),(x,-y,z)),((x,-y,z),(x,y,z)),((x,y,z),(-x,y,z)),((-x,y,z),(-x,-y,z))]:parts.append(beam(a,b,1.0,1.0))
parts.append(beam((-20,0,100.7),(20,0,100.7),2.3,1.8))
for a,b in [((-66,-45,81.8),(-20,0,100.8)),((-66,45,81.8),(-20,0,100.8)),((66,-45,81.8),(20,0,100.8)),((66,45,81.8),(20,0,100.8))]:parts.append(beam(a,b,1.6,1.6))
# Exposed underside rafters; intersections with shell/ring are deliberate.
for x in [-45,-25,0,25,45]:
 peak=97.6 if abs(x)<=20 else 97.6-(abs(x)-20)*19/46
 for y in [-41,41]:parts.append(beam((x,y,79),(x,0,peak),2.2,2.2))
# Sloping-back benches on the long lakeside and one short end.
def bench(cx,cy,length,rot,out):
 def point(u,v,z):return (cx+v,cy+u,z) if rot else (cx+u,cy+v,z)
 def bar(u,v,z,L,W,H):
  x,y,_=point(u,v,z);return box(x,y,z,W if rot else L,L if rot else W,H)
 parts.append(bar(0,-out*2,32,length,8,2.5))
 for u in [-length/2+5,0,length/2-5]:
  parts.append(bar(u,-out*2,20.5,3,5,12))
  parts.append(beam(point(u,0,31),point(u,out*4,48),2.6,2.6))
 parts.extend([bar(0,0,34,length,2.5,2.5),bar(0,out*4,47,length,3,2.5)])
 for u in np.arange(-length/2+4,length/2-2,4):parts.append(beam(point(float(u),0,34),point(float(u),out*3.6,47.5),1.8,1.8))
bench(0,29,96,False,1)
bench(49,0,55,True,1)
# Opposite short-end geometric rail. Entire landward long approach remains open.
parts.extend([box(-50,0,23,2.8,56,2.8),box(-50,0,47,3,56,3)])
for y in [-27,0,27]:parts.append(box(-50,y,23,2.8,2.4,26))
for y in [-26,1]:
 parts.append(beam((-50,y,24),(-50,y+25,47),2,2))
 parts.append(beam((-50,y,47),(-50,y+25,24),2,2))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Exact float32 weld only; no healing.
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);t=trimesh.Trimesh(v,f,process=False)
palette=[('brown_timber_frame','#593A2B'),('artificial_display_base','#93958D'),('charcoal_tiled_hip_roof','#353C40'),('white_concrete_platform_and_piers','#DEDED4'),('timber_benches_and_rail','#795039')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center;lo=t.triangles.min(axis=1);hi=t.triangles.max(axis=1)
colors[hi[:,2]<=3.001]=1
colors[(c[:,2]>3)&(hi[:,2]<=21.001)]=3
colors[lo[:,2]>=78.8]=2
colors[(c[:,2]>23)&(hi[:,2]<=50)&~((abs(c[:,0])<3)|(abs(abs(c[:,0])-50)<2.76))]=4
features=dict(estimated_not_surveyed=True,as_built_completion_year=2023,photo_capture_dates_unknown=True,roof_topology='hip: two trapezoids and two triangles; short level ridge',roof_eave_mm=[132,90],ridge_endpoints_mm=[[-20,0,101],[20,0,101]],roof_nominal_vertical_thickness_mm=3.2,principal_posts=6,post_grid_x=[-50,0,50],post_grid_y=[-30,30],lakeside_piers=3,open_landward_bays_x=[[-47,-3],[3,47]],sloping_back_benches=True,opposite_short_end_diagonal_rail=True,hidden_landward_foundation_inferred=True,minimum_nominal_slat_mm=1.8,artificial_display_ground=True,omitted=['island','lake','bridge','trees','signboard','utilities','2022 proposal gable'],actual_print_tested=False)
(O/'qa/design-features.json').write_text(json.dumps(features,indent=2)+'\n')
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
