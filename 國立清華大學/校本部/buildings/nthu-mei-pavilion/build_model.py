"""NTHU Mei/Ji Pavilion continuous hypar shell, approximate mm display reconstruction."""
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
def height(x,y):return 49+33*x*y/(55*45)
def patch(x0,x1,y0,y1,below,above,nx=60,ny=50):
 # One bilinear saddle with corresponding vertical offsets, never planar roof panels.
 v=[];f=[]
 for dz in [-below,above]:
  for i in range(nx+1):
   for j in range(ny+1):
    x=x0+(x1-x0)*i/nx;y=y0+(y1-y0)*j/ny;v.append((x,y,height(x,y)+dz))
 n=(nx+1)*(ny+1)
 for i in range(nx):
  for j in range(ny):
   a=i*(ny+1)+j;b=a+ny+1
   f.extend([(a,a+1,b),(a+1,b+1,b),(a+n,b+n,a+1+n),(a+1+n,b+n,b+1+n)])
 boundary=list(range(ny+1))+[i*(ny+1)+ny for i in range(1,nx+1)]+[nx*(ny+1)+j for j in range(ny-1,-1,-1)]+[i*(ny+1) for i in range(nx-1,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):f.extend([(a,a+n,b),(b,a+n,b+n)])
 return solid(trimesh.Trimesh(v,f,process=False))
parts=[box(0,0,0,136,116,3)]
parts.append(patch(-55,55,-45,45,0,2.6))
# Four deep inset edge ribs follow shell ruling and stop short of the free tips.
for x in [-49,49]:parts.append(patch(x-1.7,x+1.7,-39,39,5.2,.5,2,48))
for y in [-39,39]:parts.append(patch(-49,49,y-1.7,y+1.7,5.2,.5,60,2))
# Only two diagonal low supports: outward flared short concrete fins.
for sign in [-1,1]:
 x=sign*48;y=-sign*39
 pts=[]
 for z,cx,cy,w,d in [(2.5,x+sign*5,y-sign*4,20,18),(27,x,y,7,7)]:
  pts.extend([(cx+sx*w/2,cy+sy*d/2,z) for sx in [-1,1] for sy in [-1,1]])
 parts.append(solid(trimesh.convex.convex_hull(np.array(pts))) ^ patch(-70,70,-60,60,110,.2,70,60))
# Robust simplified table; open slot and central gap; stools deliberately omitted.
parts.extend([box(0,0,12,25,15,2),box(-9,0,3,3,12,7),box(9,0,3,3,12,7),box(-9,0,9,3,12,1.5),box(9,0,9,3,12,1.5),box(-9,-5,9,3,2,3.3),box(-9,5,9,3,2,3.3),box(9,-5,9,3,2,3.3),box(9,5,9,3,2,3.3)])
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('warm_offwhite_shell_and_piers','#E3E1D7'),('neutral_paved_display_base','#94958E'),('stone_table','#C5C8BF'),('pale_roof_upper_surface','#D6D6CE')]
colors=np.zeros(len(f),dtype=int);tri=t.triangles;lo=tri.min(axis=1);hi=tri.max(axis=1);c=t.triangles_center
colors[hi[:,2]<=3.001]=1
colors[(np.abs(c[:,0])<13)&(np.abs(c[:,1])<8)&(lo[:,2]>3.001)&(hi[:,2]<14.01)]=2
# Assign upper surface by analytic height plus normal, no centroid straight-plane bands.
colors[(c[:,2]>height(c[:,0],c[:,1])+2.55)&(t.face_normals[:,2]>.1)]=3
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,source_appearance_years=[2016,2020,2025],roof_footprint_mm=[110,90],roof_low_high_corners_mm=[16,82],continuous_saddle=True,low_support_corners=[[-55,45],[55,-45]],high_free_corners=[[-55,-45],[55,45]],support_count=2,shell_vertical_thickness_mm=2.6,inset_rib_width_mm=3.4,inset_rib_depth_mm=5.2,roof_grid=[60,50],symmetry_and_mathematical_curvature_are_approximations=True,table_simplified=True,omitted=['stools','lettering','utilities','vegetation','full hillside'],upper_back_reference='Official book421x286 image, unknown date, far raised corner clipped at image border; topology evidence only, not high-resolution360 survey',scope='Complete coherent architectural primary structure, not measured conservation model; artificial joined display base; no actual print'),indent=2)+'\n')
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
