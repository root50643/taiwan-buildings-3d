"""NYCU Rolling Pavilion 2024: complete visible exterior observational approximation.
Not exact surveyed NURBS, node layout, fine bamboo count or concealed foundations.
Units mm; approx 1:50. Blue plinth is display-only. Film thickened for exchange.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True);(O/'previews').mkdir(exist_ok=True)
parts=[]
def add(m,mat):parts.append(m.set_properties(1,lambda p,old:[mat]))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def surface(u,t):
 # Varying arch ellipses, shear and depth warp are observational spline surrogates.
 a=np.pi*t
 # Front seat has a low horizontal toe and a concave transition, not a ramp.
 z=3+(89+12*np.sin(np.pi*u)-20*u)*np.sin(a)+6*(1-u)**5*t**8
 if t>.78:
  w=(1-u)**5;q=(t-.78)/.22;h=89+12*np.sin(np.pi*u)-20*u
  z0=3+h*np.sin(np.pi*.78)+6*w*.78**8;dz0=h*np.pi*np.cos(np.pi*.78)+48*w*.78**7
  seat_z=(2*q**3-3*q**2+1)*z0+(q**3-2*q**2+q)*.22*dz0+(-2*q**3+3*q**2)*9
  z=z*(1-w)+seat_z*w
 return np.array([(70-30*u)*np.cos(a)+(55-30*u)*np.sin(a)-5+20*u-23*(1-u)**5*(max(t-.78,0)/.22)**2, -70+140*u+18*np.sin(a)*(1-.4*u), z])
def normal(u,t):
 du=surface(u+.0001,t)-surface(u-.0001,t);dt=surface(u,t+.0001)-surface(u,t-.0001)
 n=np.cross(du,dt);return n/np.linalg.norm(n)
def patch(us,ts,thick,offset=0):
 verts=[]
 for sign in [-1,1]:
  for u in us:
   for t in ts:verts.append(surface(u,t)+normal(u,t)*(offset+sign*thick/2))
 nu,nt=len(us),len(ts);n=nu*nt;faces=[]
 for i in range(nu-1):
  for j in range(nt-1):
   a=i*nt+j;b=a+nt
   faces.extend([(a,b,a+1),(a+1,b,b+1),(a+n,a+1+n,b+n),(a+1+n,b+1+n,b+n)])
 boundary=list(range(nt))+[i*nt+nt-1 for i in range(1,nu)]+list(range((nu-1)*nt+nt-2,(nu-1)*nt-1,-1))+[i*nt for i in range(nu-2,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.extend([(a,b,a+n),(b,b+n,a+n)])
 tm=trimesh.Trimesh(verts,faces,process=True);assert tm.is_winding_consistent;tm.invert() if tm.volume<0 else None;m=Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)));assert m.status().name=='NoError';return m
# Eight principal ribs: visual approximation, not an asserted construction schedule.
for u in np.linspace(0,1,8):
 for du in [-.024,.024]:add(patch([u+du-.005,u+du+.005],np.linspace(0,1,121),4.0),0)
# Continuous translucent film between ribs, thickened; this is not opaque concrete.
add(patch(np.linspace(0,1,43),np.linspace(0,1,121),.9,1.1),1)
# Reduced representative transverse slats. Count/spacing deliberately simplified.
for u in np.linspace(0,1,8):
 for t in np.linspace(.02,.98,61):add(patch([u-.025,u+.025],[t-.0016,t+.0016],1.25,-.7),0)
# Ground-level observed edge rail; hidden steel/footings intentionally omitted.
for t in [0,1]:add(patch(np.linspace(0,1,33),[t-.004,t+.004],3.4),0)
# Front left curling seating: only this edge broadens; no mirrored large rear seat.
def seatpoint(s,y):return np.array([-80-20*(1-s)**2,y+8*s,9+24*s**3])
def tube(points,r=1):
 vs=[];faces=[]
 for i,p in enumerate(points):
  d=points[min(i+1,len(points)-1)]-points[max(0,i-1)];d=d/np.linalg.norm(d);b=np.cross(d,[0,1,0]);b/=np.linalg.norm(b);c=np.cross(d,b)
  for a in np.linspace(0,2*np.pi,8,endpoint=False):vs.append(p+r*(b*np.cos(a)+c*np.sin(a)))
 for i in range(len(points)-1):
  for j in range(8):
   a=i*8+j;b=i*8+(j+1)%8;faces.extend([(a,b,a+8),(b,b+8,a+8)])
 for j in range(1,7):faces.extend([(0,j+1,j),((len(points)-1)*8,(len(points)-1)*8+j,(len(points)-1)*8+j+1)])
 tm=trimesh.Trimesh(vs,faces,process=True);assert tm.is_winding_consistent;tm.invert() if tm.volume<0 else None;return Manifold(Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)))
# Slatted seat follows the front-left curling shell edge, not a separate chair.
for u in np.linspace(0,.19,14):add(patch([u-.004,u+.004],np.linspace(.79,1,41),1.7,-1.0),0)
# Broad low horizontal slatted toe for several sitters, attached to curling edge.
for y in np.linspace(-72,-32,20):
 u=max(0,min(.29,(y+70)/140));end=surface(u,1)[0]+4
 add(box((-116+end)/2,y,7.6,end+116,1.9,1.8),0)
for z in [3,5,7]:add(box(-114.5,-52,z,3,43,2.2),0)
# Small reverse low bench, not a second mirrored curling seat.
add(box(15,70,3,80,10,6),0)
# Explicit blue display plinth ties observed visible roots; not a building foundation.
add(box(0,0,0,244,196,3.1),2)
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
orig=m.to_mesh64();ov=np.asarray(orig.vert_properties);of=np.asarray(orig.tri_verts);original_tri=ov[of,:3];oc=np.rint(ov[of,3].mean(axis=1)).astype(int)
from scipy.spatial import cKDTree
color_tree=cKDTree(original_tri.mean(axis=1))
# Explicit float32 construction roundtrip before export prevents quantization slivers.
m=m.set_properties(0,lambda p,old:[]).set_tolerance(.015).simplify(.02);m=Manifold(m.to_mesh());assert m.status().name=='NoError';me=m.to_mesh64();vv=np.asarray(me.vert_properties);ff=np.asarray(me.tri_verts)
centers=vv[ff,:3].mean(axis=1);colors=[]
# Exact closest points among 48 nearest original face centers, not centroid-only coloring.
for start in range(0,len(centers),512):
 pts=centers[start:start+512];idx=color_tree.query(pts,k=48)[1];points=np.repeat(pts,48,axis=0);tris=original_tri[idx.reshape(-1)]
 closest=trimesh.triangles.closest_point(tris,points);dist=np.sum((closest-points)**2,axis=1).reshape(-1,48)
 colors.extend(oc[idx[np.arange(len(pts)),np.argmin(dist,axis=1)]].tolist())
colors=np.asarray(colors,dtype=int)
v,remap=np.unique(vv[:,:3].astype(np.float32),axis=0,return_inverse=True);f=remap[ff]
t=trimesh.Trimesh(v,f,process=False);t.export(O/'model.stl')
palette=[('varnished_dark_warm_bamboo_approximate','#70482D'),('milky_agricultural_film_thickened_surrogate','#D8DDD7'),('blue_DISPLAY_plinth_NOT_foundation','#608AA7')]
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
(O/'qa/design-features.json').write_text(json.dumps({'complete_visible_exterior_approximation':True,'principal_ribs_schematic':8,'secondary_slats_simplified_per_band':61,'secondary_slats_schematic_total':488,'rib_thickness_mm':4.0,'film_thickened_mm':.9,'film_not_opaque_building_roof':True,'source_span_m':8,'source_height_m':4.8,'not_exact_nurbs':True,'hidden_foundations_included':False,'display_plinth_not_architecture':True,'actual_print_tested':False},indent=2)+'\n')
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(m.decompose()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
