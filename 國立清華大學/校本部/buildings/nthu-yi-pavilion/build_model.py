"""Historical NTHU Yi Pavilion. Normalized approximate millimeters, not survey."""
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
parts=[box(0,0,0,138,138,3),box(0,0,3,108,108,3)]
# roof rise 18 / eave 126; outside principal post span 102 -> 1.235
def pyramid(r,z,top):return hull([(sx*r,sy*r,z) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]+[(0,0,top)])
roofparts=[pyramid(63,77,98),box(0,0,74,126,126,3.1)]
for r in range(5,63,4):
 z=98-r*21/63
 roofparts.append(pyramid(r,z+.3,98.3) ^ box(0,0,z-.5,130,130,1))
roof=Manifold.batch_boolean(roofparts,OpType.Add)-pyramid(64,73,94.8)
parts.append(roof)
for x in [-48,48]:
 for y in [-48,48]:
  parts.extend([box(x,y,5,10,10,7),box(x,y,6,6,6,73)])
# Four heavy ring beams; lower headers leave upper open strip.
for s in [-1,1]:
 parts.extend([box(0,s*48,75,102,5,5),box(s*48,0,75,5,102,5),box(0,s*48,66,99,2.8,3),box(s*48,0,66,2.8,99,3)])
# paired narrow ladder lattice flanking every post on each adjacent face
for x in [-48,48]:
 for y in [-48,48]:
  sx=-1 if x>0 else 1;sy=-1 if y>0 else 1
  parts.extend([box(x+sx*11,y,12,2,2.5,55),box(x,y+sy*11,12,2.5,2,55)])
  for z in [24,39,54]:parts.extend([box(x+sx*6,y,z,12,2.4,2),box(x,y+sy*6,z,2.4,12,2)])
# back and side bench/rail; inferred regular rear baluster count disclosed
for side in ['left','right','rear','frontleft','frontright']:
 if side=='left':cx,cy,L,rot=-48,0,90,True
 elif side=='right':cx,cy,L,rot=48,0,90,True
 elif side=='rear':cx,cy,L,rot=0,48,90,False
 elif side=='frontleft':cx,cy,L,rot=-34,-48,22,False
 else:cx,cy,L,rot=34,-48,22,False
 def bar(z,length,width,height,offset=0):return box(cx+offset if rot else cx,cy if rot else cy+offset,z,width if rot else length,length if rot else width,height)
 parts.extend([bar(17,L,3,2),bar(28,L,3,2),bar(15,L,7,2,3 if side=='left' else -3 if side in ['right','rear'] else 3)])
 for u in np.linspace(-L/2+3,L/2-3,max(3,int(L/6))):parts.append(box(cx if rot else cx+u,cy+u if rot else cy,17,1.7,1.7,12))
 for u in [-L/2+4,L/2-4]:parts.append(box(cx if rot else cx+u,cy+u if rot else cy,5.5,3,3,11))
# central approach remains open 46mm width. Under-roof hip rafters, 4 cardinal rafters.
for x,y in [(-59,-59),(59,-59),(59,59),(-59,59),(-59,0),(59,0),(0,-59),(0,59)]:parts.append(beam((x,y,74.5),(0,0,94.3),2.7,3))
parts.append(box(0,0,93.5,2,2,2.5))
# simplified triangulation above header, attached at upper ring
for s in [-1,1]:
 for a,b in [((-44.2,s*47.7,74.8),(-20,s*47.7,80.8)),((44.2,s*47.7,74.8),(20,s*47.7,80.8)),((s*47.7,-44.2,74.8),(s*47.7,-20,80.8)),((s*47.7,44.2,74.8),(s*47.7,20,80.8))]:parts.append(beam(a,b,2,2))
# blank plaque only: lettering/calligraphy not fabricated
parts.append(box(0,-49.5,65,18,2,8))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export and exact-weld actual float32 STL coordinates; no tolerance repair.
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);t=trimesh.Trimesh(v,f,process=False)
palette=[('warm_dark_timber','#66422C'),('neutral_display_ground','#A5A59D'),('weathered_roof_boards','#655C50'),('wooden_deck_and_benches','#90603D'),('blank_plaque','#B88042')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center;lo=t.triangles.min(axis=1);hi=t.triangles.max(axis=1)
colors[hi[:,2]<=3.001]=1
colors[lo[:,2]>=77.5]=2
colors[(c[:,2]>3)&(c[:,2]<6.01)]=3
colors[(c[:,2]>=15)&(c[:,2]<=17.01)]=3
colors[(abs(c[:,0])<=9.01)&(c[:,1]<-48.4)&(c[:,2]>=65)&(c[:,2]<=73)]=4
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,historical_photo_years=[2010,2012,2013,2018],not_current_2026_survey=True,roof_eave_mm=126,post_outside_mm=102,roof_rise_mm=21,roof_nominal_vertical_thickness_mm=3.2,principal_posts=4,front_central_approach_gap_mm=46,rear_rail_regularization_inferred=True,no_independent_rear_exterior_photo=True,minimum_nominal_baluster_mm=1.7,ladder_lattice=True,under_roof_rafters=True,blank_plaque_no_calligraphy=True,artificial_display_ground=True,omitted=['entire Go Garden','boardwalk','people','vegetation','temporary tables','tribute banners'],actual_print_tested=False),indent=2)+'\n')
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
