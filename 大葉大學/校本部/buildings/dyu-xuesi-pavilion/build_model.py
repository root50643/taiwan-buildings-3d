"""Historical Dayeh Xuesi Pavilion. Normalized approximate millimeters, not survey."""
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
parts=[box(0,0,0,126,126,2.5),box(0,0,2.5,108,108,2.5)]
# Four square posts and complete two-level perimeter frame.
for x in [-48,48]:
 for y in [-48,48]:parts.extend([box(x,y,4.8,8,8,2),box(x,y,6,5,5,61)])
for s in [-1,1]:
 parts.extend([box(0,s*48,60,101,4.5,7),box(s*48,0,60,4.5,101,7),box(0,s*48,46,99,2.8,3),box(s*48,0,46,2.8,99,3)])
# Four sloping metal roof planes: no long ridge. Hollow underside, not solid mass.
parts.extend(roof_ring(54,10,65,90,2.8))
for s in [-1,1]:parts.extend([box(0,s*53,62,108,2,2.7),box(s*53,0,62,2,108,2.7)])
# Standing seams on four slopes, clipped to actual square trapezoid face.
for side in range(4):
 for u in [-44,-33,-22,-11,0,11,22,33,44]:
  stop=max(10,abs(u));z=65+(54-stop)*25/44
  a=(u,-54,65);b=(u,-stop,z)
  def rot(p):
   x,y,z=p
   for _ in range(side):x,y=-y,x
   return x,y,z
  parts.append(hull([rot((u+dx,-r,65+(54-r)*25/44+dz)) for r in [53.65,stop+.37] for dx in [-.6,.6] for dz in [-.35,.8]]))
# Opaque central hood and backed grid relief; function is not asserted.
parts.append(box(0,0,88.8,20,20,14.2))
parts.append(hull([(-11,-11,102),(-11,11,102),(11,-11,102),(11,11,102),(0,0,107)]))
for s in [-1,1]:
 for u in [-9,0,9]:parts.extend([box(u,s*10,89,1.1,1.2,14),box(s*10,u,89,1.2,1.1,14)])
 for z in [90,96,102]:parts.extend([box(0,s*10,z,20,1.2,1.1),box(s*10,0,z,1.2,20,1.1)])
# Three rail sides, no entry-side rail. Horizontal bars and robust sparse supports.
for side in ['left','right','rear']:
 rot=side!='rear';cx=-48 if side=='left' else 48 if side=='right' else 0;cy=48 if side=='rear' else 0
 for z in [13,19,25]:parts.append(box(cx,cy,z,1.6 if rot else 96,96 if rot else 1.6,1.6))
 for u in [-32,-16,0,16,32]:parts.append(box(cx if rot else u,u if rot else cy,4.8,1.8,1.8,21.8))
# Source-supported side benches (three per side) and single front bench.
# Rear seat segmentation is occluded and intentionally omitted, not fabricated.
def bench(x,y,rot=False):
 parts.append(box(x,y,13,8 if rot else 25,25 if rot else 8,2.4))
 for s in [-1,1]:parts.append(box(x if rot else x+s*9,y+s*9 if rot else y,4.8,8 if rot else 4,4 if rot else 8,8.6))
for s in [-1,1]:
 for y in [-29,0,29]:bench(s*39,y,True)
bench(0,-32)
# Thick central rectangular stone on narrower pedestal. No purpose or lettering assigned.
parts.extend([box(0,4,4.8,27,18,15.2),box(0,4,19,36,23,12)])
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export and exact-weld actual float32 STL coordinates; no tolerance repair.
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);t=trimesh.Trimesh(v,f,process=False)
palette=[('red_pavilion_frame','#B62222'),('display_ground','#9B9D93'),('brown_gray_metal_roof','#75635E'),('gray_stone_and_pad','#AAAFA8'),('black_rails_bench_legs','#292E2C'),('opaque_hood_panels','#D3D8D3'),('hood_grid','#E9ECE2')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center;lo=t.triangles.min(axis=1);hi=t.triangles.max(axis=1)
colors[hi[:,2]<=2.501]=1
colors[(c[:,2]>2.5)&(c[:,2]<6.8)]=3
colors[c[:,2]>=62]=2
colors[(c[:,2]<28)&(c[:,2]>6.8)]=4
colors[(abs(c[:,0])<18.1)&(abs(c[:,1]-4)<11.6)&(c[:,2]>=5)&(c[:,2]<=31.01)]=3
colors[(c[:,2]>=13)&(c[:,2]<=15.41)&(((abs(c[:,0])>34)&(abs(c[:,0])<43.1))|((abs(c[:,0])<12.6)&(abs(c[:,1]+32)<4.1)))]=3
for x in [-48,48]:
 for y in [-48,48]:colors[(abs(c[:,0]-x)<=2.51)&(abs(c[:,1]-y)<=2.51)&(c[:,2]>=6.8)&(c[:,2]<=67)]=0
colors[(c[:,2]>=89)&(c[:,2]<102.1)&(abs(c[:,0])<=10.01)&(abs(c[:,1])<=10.01)]=5
colors[(c[:,2]>=89)&(c[:,2]<=103.01)&(abs(c[:,0])<=10.61)&(abs(c[:,1])<=10.61)&((abs(c[:,0])>10.01)|(abs(c[:,1])>10.01))]=6
colors[c[:,2]>103.01]=5
colors[(c[:,2]>=60)&(c[:,2]<=67)&(((abs(c[:,0])<=50.5)&(abs(abs(c[:,1])-48)<=2.25))|((abs(c[:,1])<=50.5)&(abs(abs(c[:,0])-48)<=2.25)))]=0
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,historical_photo_years=[2003,2004,2012],undated_official_panorama=True,not_current_2026_survey=True,principal_posts=4,roof_slopes=4,roof_eave_mm=108,roof_rise_mm=25,roof_nominal_vertical_thickness_mm=2.8,hood_square_mm=20,hood_function_unknown=True,rail_sides=3,entry_open=True,side_benches=6,front_benches=1,rear_hidden_seat_segmentation_omitted=True,central_stone_purpose_unknown=True,artificial_display_ground=True,minimum_rail_width_mm=1.6,opaque_backed_hood_grid=True,actual_print_tested=False,omitted=['rear occluded seating details','hillside','trees','stairs','lamp','hidden roof engineering']),indent=2)+'\n')
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
