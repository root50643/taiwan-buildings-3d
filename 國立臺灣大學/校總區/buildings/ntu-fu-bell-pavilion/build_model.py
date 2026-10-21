"""NTU Fu Bell Pavilion: historical 2005–2021 bounded exterior; reinforced miniature."""
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
# All dimensions are model millimetres, relative approximate proportions, NOT surveyed.
def tube(points,r,closed=False):
 pts=np.asarray(points,float);N=len(pts);K=16;verts=[]
 for i,p in enumerate(pts):
  tangent=pts[(i+1)%N]-pts[(i-1)%N] if closed else (pts[min(i+1,N-1)]-pts[max(0,i-1)])
  tangent/=np.linalg.norm(tangent);ref=np.array([0,0,1.]) if closed else np.array([-pts[0,1],pts[0,0],0.])
  ref/=np.linalg.norm(ref)
  u=np.cross(tangent,ref);u/=np.linalg.norm(u);v=np.cross(tangent,u)
  for j in range(K):verts.append(p+r*(u*math.cos(2*math.pi*j/K)+v*math.sin(2*math.pi*j/K)))
 faces=[]
 for i in range(N if closed else N-1):
  for j in range(K):
   a=i*K+j;b=i*K+(j+1)%K;c=((i+1)%N)*K+(j+1)%K;d=((i+1)%N)*K+j;faces.extend([(a,b,c),(a,c,d)])
 if not closed:
  for j in range(1,K-1):faces.extend([(0,j+1,j),((N-1)*K,(N-1)*K+j,(N-1)*K+j+1)])
 t=trimesh.Trimesh(verts,faces,process=False)
 if t.volume<0:t.invert()
 assert t.is_watertight
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
# Neutral circular display support (not surveyed plaza), actual raised platform.
add(cyl(0,0,0,51,2),0)
add(cyl(0,0,1.8,36,8.2),1)
# Four radial stairs: three exterior treads + platform top interpreted as fourth level.
for angle in [0,90,180,270]:
 for edge,top in [(49,4),(45,6),(41,8)]:
  add(box((edge+30)/2,0,1.8,edge-30,19,top-1.8).rotate((0,0,angle)),1)
# Eight squat washed-stone posts, each stair flanked by two. Rounded upper profile.
for a0 in [0,90,180,270]:
 for da in [-23,23]:
  a=math.radians(a0+da);x,y=32*math.cos(a),32*math.sin(a)
  post=box(0,0,9.7,7,8,14.3)+Manifold.cylinder(8,3.5,3.5,48).rotate((90,0,0)).translate((0,4,24))
  add(post.rotate((0,0,a0+da)).translate((x,y,0)),1)
# Four independent inward-curved radial iron columns, no cross-centre arch.
for deg in [45,135,225,315]:
 a=math.radians(deg);xy=lambda r,z:(r*math.cos(a),r*math.sin(a),z)
 add(cyl(*xy(27,9.7)[:2],9.7,1.45,126.3),2)
 pts=[]
 for t in np.linspace(0,1,37):
  p=(1-t)**3*np.array([27,135])+3*(1-t)**2*t*np.array([27,164])+3*(1-t)*t*t*np.array([15,155])+t**3*np.array([10,136])
  pts.append(xy(*p))
 add(tube(pts,1.25),2)
 # Visible sleeve collars regularized; not mechanical detail.
 for z in [63,113]:add(cyl(*xy(27,z)[:2],z,1.8,2.2),2)
# Two separated paired circular brace groups, four rails total.
for z in [48,52,88,92]:
 add(tube([(27*math.cos(a),27*math.sin(a),z) for a in np.linspace(0,2*math.pi,128,endpoint=False)],1.15,True),2)
# Round hanging disc: connected recessed waist, not floating upper wafer.
add(cyl(0,0,131,14,2),2);add(cyl(0,0,132.8,12.8,1.8),3);add(cyl(0,0,134.4,14,2),2)
# Deliberately reinforced suspension neck. No inferred motor/cable/striker or inscription.
add(cyl(0,0,125.8,1.8,5.5),3)
# Bronze bell: narrow upper body and flared skirt; shallow underside recess, not hollow shell.
bell=Manifold.cylinder(4.8,8,4.6,96).translate((0,0,109))+cyl(0,0,113.6,4.6,11.4)+Manifold.cylinder(2,4.6,2.3,96).translate((0,0,124.8))
bell=bell-cyl(0,0,108.5,6,1.7)
add(bell,4)
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
palette=[('neutral_display_support','#B3B0A7'),('washed_stone','#D0D0C8'),('muted_red_iron','#804D4C'),('recess_and_suspension','#493B38'),('oxidised_bronze_bell','#42685D')]
(O/'qa/design-features.json').write_text(json.dumps(dict(historical_source_era='2005–2021',estimated_not_surveyed=True,radial_columns=4,independent_inward_curves=4,paired_ring_groups=2,ring_rails=4,stone_posts=8,radial_stairs=4,exterior_treads_per_stair=3,platform_as_fourth_level=True,column_diameter_mm=2.9,upper_curve_diameter_mm=2.5,ring_diameter_mm=2.3,suspension_diameter_mm=3.6,base_artificial=True,no_interior_machinery_or_inscriptions=True,bell_underside_shallow_recess=True,actual_print_tested=False),indent=2)+'\n')
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
