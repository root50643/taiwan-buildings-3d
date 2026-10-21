"""Historical NTU Si Nian Memorial Hall. Normalized approximate millimeters, not survey."""
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
# Approximate proportions only; X short facade / Y long axis.
parts=[]
for z,w,d,h in [(0,96,144,2.8),(2.6,90,138,2.8),(5.2,84,132,2.8),(7.8,80,128,1.8)]:parts.append(box(0,0,z,w,d,h))
centers=[(x,y) for x in [-36,-12,12,36] for y in [-60,60]]+[(x,y) for x in [-36,36] for y in [-36,-12,12,36]]
assert len(centers)==16
# Shallow, integral twenty-flute columns: no independent thin strips.
def column(x,y):
 n=160;verts=[]
 for z,r in [(9.3,4.7),(65.8,4.2)]:
  for i in range(n):
   a=2*math.pi*i/n; rr=r-.18*(1-math.cos(20*a));verts.append((x+rr*math.cos(a),y+rr*math.sin(a),z))
 faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([(i,j,n+j),(i,n+j,n+i)])
 for i in range(1,n-1):faces.extend([(0,i+1,i),(n,n+i,n+i+1)])
 return solid(trimesh.Trimesh(verts,faces,process=False))
for x,y in centers:
 parts.append(column(x,y))
 parts.append(Manifold.cylinder(2.8,4.25,5.9,64).translate((x,y,65.3)))
 parts.append(box(x,y,67.6,12,12,1.8))
# Perimeter entablature and completed pale flat ceiling. No invented exposed framing.
for z,w,d,h in [(69,82,130,4.4),(73.2,84,132,10.0),(83.0,87,135,3.0)]:parts.append(box(0,0,z,w,d,h))
# Solid rectangular roof mass includes front/back triangle pediments; closed ceiling is source supported.
parts.append(hull([(x,y,z) for y in [-66.5,66.5] for x,z in [(-42,85.8),(42,85.8),(0,105.1)]]))
# Two green roof slabs extending over the two triangular end walls.
for s in [-1,1]:parts.append(hull([(s*x,y,104.7-x*19/42+dz) for x in [0,45] for y in [-69,69] for dz in [0,2.0]]))
# Restrained integral thick ridge, no guessed tile count or isolated ornamental sculpture.
parts.append(box(0,0,105.7,2.4,138,1.1))
# Gable cornice bands, front/rear, preserving empty triangular field (sculptures omitted).
for y in [-67.0,67.0]:
 parts.append(box(0,y,85.7,85,2.2,1.6))
 for s in [-1,1]:parts.append(hull([(s*x,y+dy,105.43-x*19/42+dz) for x in [0,42.8] for dy in [-.8,.8] for dz in [-1.7,0]]))
# Backed triglyph-like frieze blocks: simplified spacing, not count of original sculpture.
for x,y in centers:
 if abs(y)==60: parts.append(box(x,(-1 if y<0 else 1)*66.0,73.7,2.5,1.0,8.6))
 if abs(x)==36: parts.append(box((-1 if x<0 else 1)*42, y,73.7,1.0,2.5,8.6))
# Independent central memorial base is physically joined to platform, no lettering/interior.
for z,w,d,h in [(9.3,23,35,2.8),(11.8,20,32,2.5),(14,18,30,17.5),(31.2,21.5,33.5,2.5)]:parts.append(box(0,0,z,w,d,h))
# Coarse integral panel rims, no fine iconography or inferred inscription.
for y in [-15,15]:
 for x in [-7,7]:parts.append(box(x,y,16,1.0,1.0,13))
 for z in [16,28]:parts.append(box(0,y,z,15,1.0,1.0))
for x in [-9,9]:
 for y in [-12,12]:parts.append(box(x,y,16,1.0,1.0,13))
 for z in [16,28]:parts.append(box(x,0,z,1.0,25,1.0))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export and exact-weld actual float32 STL coordinates; no tolerance repair.
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);t=trimesh.Trimesh(v,f,process=False)
palette=[('gray_steps','#A3A6A2'),('pale_column_and_ceiling','#DDDCD3'),('gray_entablature_pediment','#B9BCB2'),('dark_green_glazed_roof','#365E49'),('memorial_stone','#C2C1B6')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center
colors[c[:,2]>9.6]=1
colors[c[:,2]>=69.0]=2
roof_surface=104.7-abs(c[:,0])*19/42
colors[(c[:,2]>roof_surface+.05)&(c[:,2]>84.7)&(abs(c[:,1])<69.01)]=3
colors[(abs(c[:,0])<12)&(abs(c[:,1])<18)&(c[:,2]>9.6)&(c[:,2]<34)]=4
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,historical_photo_years=[2009,2010,2011],restoration_photo_year=2004,not_current_2026_survey=True,columns=16,short_side_columns=4,long_side_columns=6,column_center_span_mm=[72,120],column_centers=centers,column_shaft_height_mm=56.5,entablature_height_mm=17.0,roof_slopes=2,triangular_end_pediments=2,three_exposed_platform_steps=True,white_completed_flat_ceiling=True,central_rectangular_memorial=True,actual_print_tested=False,omitted=['inscriptions','fine gable sculpture','tile counts','obelisk','pool','garden','hidden construction']),indent=2)+'\n')
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
