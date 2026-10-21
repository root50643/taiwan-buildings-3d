"""NCKU Minor West Gate / Jingbo Gate. Normalized approximate millimeters, not survey."""
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
# Coordinates millimeters are normalized display size, not site survey.
# Road/front = negative Y; campus/rear = positive Y.
parts=[]
parts.append(box(0,0,0,106,61,2.4)) # independent display plinth
base=box(0,0,2.2,100,55,56)
# Round-headed through tunnel: vertical jambs + half circular head.
arch=Manifold.cylinder(70,25,25,96).rotate((90,0,0)).translate((0,35,19))
arch=arch+box(0,0,-1,50,70,20.1)
base=base-arch
parts.append(base)
# Forecourt, front parapet and short side returns; not a second-storey front wall.
parts += [box(0,-25.7,57.9,100,3.6,8),box(-48.2,-15,57.9,3.6,21,8),box(48.2,-15,57.9,3.6,21,8)]
# Chamber rear wall continuous; only front facade receives recessed openings.
chamber=box(0,8,57.9,54,35,28)
chamber=chamber-box(0,-9.5,65.8,11,2.3,15)
for x in [-18,18]:chamber=chamber-box(x,-9.5,68,4,2.3,8)
parts.append(chamber)
# Single slope annexes extend beyond base; front set back to Y=-9.5.
for s in [-1,1]:
 parts.append(box(s*40,8,57.4,27.5,36.5,2))
 annex=hull([(s*x,y,z) for x in [26.6,52.5] for y in [-9.5,25.5] for z in [58.2,84-(x-27)*8/25.5]])
 # side lattice: shallow backed recess, supported grilles simplified counts.
 annex=annex-box(s*52.3,8,65,1.5,10,9)
 for z in [66.5,69.5,72.5]:annex=annex+box(s*52.0,8,z,1.6,10.3,1.1)
 for y in [5,9,12]:annex=annex+box(s*52.0,y,65,1.6,1.1,9)
 parts.append(annex)
 parts.append(hull([(s*x,y,84-(x-27)*8/25.5+dz) for x in [26.4,54] for y in [-11,27] for dz in [0,1.8]]))
 # pale raised front and back roof edge (integral, not a second eave)
 for y in [-10.5,26.5]:parts.append(hull([(s*x,y+dy,85.4-(x-27)*8/25.5+dz) for x in [26.5,54] for dy in [-.65,.65] for dz in [0,1.2]]))
# Main SINGLE-EAVE hip-and-gable roof, lower hip return, upper triangular gables.
# Layered solid convex frusta create modestly concave pitches, no hollow invisible roof.
parts.append(box(0,8,85.5,80,50,1.1))
levels=[(86.5,40,25),(89.0,36,21),(94,27,14)]
for (z0,x0,y0),(z1,x1,y1) in zip(levels,levels[1:]):
 parts.append(hull([(sx*x,8+sy*y,z) for z,x,y in [(z0,x0,y0),(z1,x1,y1)] for sx in [-1,1] for sy in [-1,1]]))
parts.append(hull([(x,8+y,z) for x in [-27,27] for y,z in [(-14,93.9),(14,93.9),(0,104)]]))
# Low solid roof support band and merged bracket approximations.
parts.append(box(0,8,84.8,56,37,2.5))
for x in [-24,-12,0,12,24]:
 for y in [-1,1]:parts.append(beam((x,8+y*17,82.8),(x,8+y*23,86.8),2.4,2.4))
# Thick simplified pale gable rim; swallowtail ridge drawn as merged solid profile.
for x in [-27,27]:
 for s in [-1,1]:parts.append(beam((x,8,104.2),(x,8+s*14,94.1),1.6,1.6))
for i in range(24):
 x0=-29+i*58/24;x1=-29+(i+1)*58/24
 z0=104+3*(abs(x0)/29)**6;z1=104+3*(abs(x1)/29)**6
 parts.append(hull([(x,y,z) for x,zbase in [(x0,z0),(x1,z1)] for y in [7,9] for z in [102.5,zbase+1.2]]))
# Pale arch lining is material only; plaques are blank shallow integral relief.
for y in [-27.6,27.6]:parts.append(box(0,y,46,13,1.4,6))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);t=trimesh.Trimesh(v,f,process=False)
palette=[('red_brown_brick','#985E49'),('terracotta_roof','#B96343'),('pale_ridge_and_stone','#C4C1AE'),('dark_recess','#393B32'),('display_plinth','#777C77')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center
colors[c[:,2]<2.41]=4
colors[(c[:,2]>85.49)]=1
# Paint visible triangular gable faces pale (one planar source-supported field).
colors[(np.abs(np.abs(c[:,0])-27)<.001)&(c[:,2]>94)]=2
colors[c[:,2]>103.7]=2
# Gable rim material exact construction vicinity.
colors[(np.abs(np.abs(c[:,0])-27)<1.2)&(c[:,2]>94)&(c[:,2]>104.2-np.abs(c[:,1]-8)*10.1/14-.8)]=2
annexz=84-(np.abs(c[:,0])-27)*8/25.5
colors[(np.abs(c[:,0])>27)&(c[:,2]>annexz-.01)&(c[:,2]<86.49)]=1
colors[(np.abs(c[:,0])>28)&(c[:,2]>annexz+1.7)&(c[:,2]<85.49)&((abs(c[:,1]+10.5)<.66)|(abs(c[:,1]-26.5)<.66))]=2
colors[(np.abs(c[:,0])>49)&(c[:,2]>57.4)&(c[:,2]<59.4)]=2
# Inner tunnel faces light grey; not painted arch voussoirs on a guessed grid.
rad=np.sqrt(c[:,0]**2+(c[:,2]-19)**2)
colors[((abs(c[:,0])<25.01)&(c[:,2]<19.1)&(c[:,2]>2.41))|((rad<25.01)&(c[:,2]>=19)&(c[:,2]<44.1))]=2
colors[(abs(c[:,0])<6.51)&(c[:,2]>45.99)&(c[:,2]<52.01)&(abs(c[:,1])>27)]=2
# Front recess backs and side vent recess backs only.
colors[(c[:,1]>-9)&(c[:,1]<-8.3)&(((abs(c[:,0])<5.51)&(c[:,2]>65.8)&(c[:,2]<80.81))|((abs(abs(c[:,0])-18)<2.01)&(c[:,2]>68)&(c[:,2]<76)))]=3
colors[(abs(abs(c[:,0])-51.55)<.01)&(abs(c[:,1]-8)<5.01)&(c[:,2]>65)&(c[:,2]<74)]=3
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,front_axis='negative Y / roadside',rear_axis='positive Y / campus',base_width=100,base_depth=55,arch_clear_width=50,arch_crown_z=44,front_parapet_top=65.9,central_chamber_width=54,central_chamber_y=8,central_chamber_depth=35,main_roof='single-eave hip-and-gable; lower hip returns and upper triangular gables',annex_roofs='two outward single-slope roofs',annex_outer_extent=52.5,front_openings='one doorway plus two narrow windows; shallow backed recesses',campus_upper_wall='blank continuous brick',fine_ornaments_and_text_omitted=True,actual_print_tested=False),indent=2)+'\n')
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
