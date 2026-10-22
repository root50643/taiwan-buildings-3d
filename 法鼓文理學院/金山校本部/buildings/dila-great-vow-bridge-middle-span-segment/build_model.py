"""法鼓文理學院金山校本部大願橋 / Great Vow Bridge: source-bound whole exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_base','#788580',255),('gray_box_girder','#777C78',255),('wood_inner_panels','#6B5147',255),('bark_strip','#49382C',255),('wood_deck','#796555',255),('metal_rails_and_tubes','#92978E',255),('wood_handrail','#584A40',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(c,s,col,name):add(Manifold.cube(s,True).translate(c),col,name)
def beam(a,b,w,col,name):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;x=np.cross(z,[0,1,0])
 if np.linalg.norm(x)<.01:x=np.cross(z,[1,0,0])
 x/=np.linalg.norm(x);y=np.cross(z,x);T=np.column_stack([x,y,z,(a+b)/2]);add(Manifold.cube((w,w,L+w*.15),True).transform(T),col,name)
def path(points,w,col,name):
 for a,b in zip(points,points[1:]):beam(a,b,w,col,name)
def ring(x,y,z,s,w,col,name):
 for a,b in [((-s/2,-s/2),(s/2,-s/2)),((s/2,-s/2),(s/2,s/2)),((s/2,s/2),(-s/2,s/2)),((-s/2,s/2),(-s/2,-s/2))]:beam((x+a[0],y+a[1],z),(x+b[0],y+b[1],z),w,col,name)

def yhigh(x):
 t=(x+135)/270
 return -7+9.5*math.sin(math.pi*t)+1.6*math.sin(2*math.pi*t)
def width(x):return 8.4+6.6*math.sin(math.pi*(x+135)/270)**.8
def zd(x):return 14+2.1*math.sin(math.pi*(x+135)/270)
def wh(x):return 7.4+4.6*math.sin(math.pi*(x+135)/270)
def poly_sweep(sections):
 vs=np.array(sections).reshape(-1,3);n=len(sections);k=len(sections[0]);fs=[]
 for i in range(n-1):
  for j in range(k):
   a=i*k+j;b=i*k+(j+1)%k;c=b+k;d=a+k;fs.extend([[a,b,c],[a,c,d]])
 for j in range(1,k-1):fs.extend([[0,j+1,j],[(n-1)*k,(n-1)*k+j,(n-1)*k+j+1]])
 tm=trimesh.Trimesh(vs,fs,process=False);tm.fix_normals();return Manifold(Mesh(np.array(tm.vertices,dtype=np.float32),np.array(tm.faces,dtype=np.uint32)))
def roundbeam(a,b,r,col,name):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;x=np.cross(z,[0,1,0])
 if np.linalg.norm(x)<.01:x=np.cross(z,[1,0,0])
 x/=np.linalg.norm(x);y=np.cross(z,x);T=np.column_stack([x,y,z,a]);add(Manifold.cylinder(L,r,r,20).transform(T),col,name)
xs=np.linspace(-135,135,181)
box((0,3,.8),(286,47,1.6),0,'NON_SITE_display_base')
# Thin continuous deck carries shallow plank grooves, not a fictitious deep solid soffit.
secs=[]
for x in xs:
 y=yhigh(x);w=width(x);z=zd(x);secs.append([(x,y,z-1.1),(x,y+w,z-1.1),(x,y+w,z),(x,y,z)])
add(poly_sweep(secs),4,'continuous_variable_width_curved_deck')
# Gray thick outward-leaning high box silhouette; round bores through both end zones.
def wall_sections(inner=False):
 ss=[]
 for x in xs:
  y=yhigh(x);z=zd(x);h=wh(x);lean=2.0
  if inner:ss.append([(x,y+.04,z-.25),(x,y+.45,z-.25),(x,y-lean+.45,z+h-.35),(x,y-lean+.04,z+h-.35)])
  else:ss.append([(x,y-2,z-2.5),(x,y+.08,z-2.5),(x,y-lean+.08,z+h),(x,y-lean-2,z+h)])
 return ss
holes=[]
for x in [-128.5,128.5]:
 holes.append(Manifold.cylinder(15,2.75,2.75,64).rotate((90,0,0)).translate((x,yhigh(x)+5,zd(x)+3.65)))
cuts=Manifold.batch_boolean(holes,OpType.Add)
add(poly_sweep(wall_sections())-cuts,1,'one_high_outward_leaning_gray_box_two_true_round_bores')
add(poly_sweep(wall_sections(True))-cuts,2,'wood_inner_cladding_with_bores')
# Transverse planking and interior panel rhythm are shallow relief, not hidden structure.
for x in np.arange(-134,135,1.5):
 y=yhigh(x);w=width(x);z=zd(x)
 box((x,y+w/2,z+.08),(1.34,w-.12,.20),4,'transverse_wood_plank')
 if abs(x)<124:
  beam((x,y+.42,z+.5),(x,y-.25,z+3.2),.32,3,'simplified_bark_strip_relief')
# Actual open low railing: stronger slanted primary stanchions with finer infill.
railxs=np.linspace(-135,135,136)
path([(x,yhigh(x)+width(x)+.6,zd(x)+3.7) for x in railxs],.85,6,'curved_low_wood_handrail')
path([(x,yhigh(x)+width(x)+.25,zd(x)+1.2) for x in railxs],.5,5,'low_open_rail_lower_tie')
for x in np.linspace(-135,135,91):
 y=yhigh(x)+width(x);z=zd(x)
 beam((x,y-.1,z-.6),(x,y+.65,z+3.7),.58,5,'slanted_primary_rail_post')
for x in np.linspace(-134,134,181):
 y=yhigh(x)+width(x);z=zd(x)
 roundbeam((x,y+.12,z+1.15),(x,y+.58,z+3.6),.17,5,'fine_open_rail_infill')
for x in np.linspace(-133,133,90):
 y=yhigh(x);w=width(x);z=zd(x)
 roundbeam((x,y-3,z-1.5),(x,y+w+1.2,z-1.5),.55,5,'round_transverse_beam_two_exposed_ends')
# Visible longitudinal under-deck members and approximate alternating diagonal ties.
for frac in [.32,.74]:path([(x,yhigh(x)+width(x)*frac,zd(x)-1.25) for x in xs],.48,5,'soffit_longitudinal_support')
for i,x in enumerate(np.arange(-130,130,6)):
 a=.25 if i%2 else .75;b=1-a
 roundbeam((x,yhigh(x)+width(x)*a,zd(x)-1.5),(x+5,yhigh(x+5)+width(x+5)*b,zd(x+5)-1.5),.20,5,'visible_soffit_diagonal_approximation')
# Two bank groups, each with two separate upper connection heights. No center pier.
for x in [-105,105]:
 y=yhigh(x);z=zd(x)
 roundbeam((x-3,y-8,1.5),(x,y-2.8,z+2.1),1.05,5,'bank_double_tube_high_attachment')
 roundbeam((x+3,y+1,1.5),(x+1,y-.9,z-2),1.05,5,'bank_double_tube_low_attachment')
for x in [-137,137]:
 # Minimal end interfaces joined to display base; not surveyed bank landform.
 yy=yhigh(-135 if x<0 else 135)+width(-135 if x<0 else 135)/2
 box((x,yy,7.7),(4.2,11,12.4),1,'minimal_end_interface_not_terrain')
FEATURES=dict(name='法鼓文理學院金山校本部大願橋',school='法鼓文理學院',campus='金山校本部',slug='dila-great-vow-bridge',single_model_replacement=True,source_length_m=108,model_bridge_length_mm=270,two_true_end_bores=True,variable_width_curved_plan=True,one_high_leaning_box=True,low_open_railing=True,round_crossbeams=90,bank_double_tube_groups=2,upper_tube_attachments_not_common_apex=True,no_central_pier=True,estimated_not_surveyed=True,no_actual_print=True,support_free_certified=False,uncertain=['curvature, width and heights','all rib, rail and plank counts','support angles, diameter and locations','wood relief and exact color'],omitted=['adjacent buildings and stream banks','underground foundations','TMD and hidden box structure'],historical_segment_stl_sha256='ab8f4bab8b9e8bf708e9bc386dbfa6b012e06ca4912daaea881dd0839d64c913')
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.01).simplify(.01)
# Stabilize construction at the final exchange float32 precision before export.
for _ in range(2):
 q=m.to_mesh64();m=Manifold(Mesh(np.asarray(q.vert_properties[:,:3],dtype=np.float32),np.asarray(q.tri_verts,dtype=np.uint32))).set_tolerance(.005).simplify(.005)
 assert m.status().name=='NoError'
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.021,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
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
