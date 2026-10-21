"""NCU Ting Song streetfront canopy only; source-approximate mm, not full terrace."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def beam(a,b,w,d):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);v=b-a
 # X-running pitched rectangular beam; top/bottom slope exactly parallel.
 if abs(v[0])>0:
  return Manifold.cube((v[0],d,w)).transform(np.array([[1,0,0,a[0]],[0,1,0,a[1]-d/2],[v[2]/v[0],0,1,a[2]]]))
 raise ValueError('x-running beam only')
xs=[-106,-66,-28,14,54,86,106];zs=[33,28,23,22,24,27,28]
def roofz(x):return float(np.interp(x,xs,zs))
parts=[box(0,1,0,220,36,3)]
# Seven visible/approximate longitudinal alignments, not a measured bay count.
for x in xs:
 for y in [-10,9]:parts.append(box(x,y,2.8,2.4,2.4,roofz(x)-2.8))
# Asymmetric high left / low long middle / gentle raised far end.
for i in range(len(xs)-1):
 a,b=xs[i:i+2];za,zb=zs[i:i+2]
 parts.append(beam((a-1.2,0,roofz(a-1.2)),(b+1.2,0,roofz(b+1.2)),1.8,25))
 for y in [-10,9]:parts.append(beam((a-1.2,y,za-2),(b+1.2,y,zb-2),2.2,2.4))
for x in xs:parts.append(box(x,-.5,roofz(x)-2,2.4,22,2.2))
# Vertical fascia slats are backed shallow relief, not detached sticks.
for x in np.arange(-105.6,106,2.5):
 parts.append(box(float(x),-12.65,roofz(x)-.1,.95,.55,1.95))
# Near waiting bay solid transverse brick wall, perforated return, integrated bench.
wall=box(-66,0,2.9,3,23,roofz(-66)-3.1)
parts.append(wall)
returnwall=box(-51,10,2.9,30,2.4,14)
for x in np.arange(-61,-37,4):
 for z in [7,11,15]:returnwall-=box(float(x),10,z,1.8,3.5,1.5)
parts.append(returnwall)
# Backed mortar line relief on solid cross wall; 0.35mm recess, not loose bricks.
for z in np.arange(5,26,2):
 parts[-2]-=box(-67.45,0,float(z),.5,22,.35)
parts += [box(-51,7.4,6,24,4,1.5),box(-61,8,3,2.2,3,3.3),box(-41,8,3,2.2,3,3.3)]
# One broad stair, immediately after brick bay, NOT a duplicate on far end.
# Ten steps solid-filled for reliability, neutral explicit rear cut at y=15.
for i in range(10):parts.append(box(-17,-9.5+i*2.5,2.9,28,2.7,1.5*(i+1)))
# Thickened side handrails; solid post/rail simplification, not measured details.
for x in [-31.5,-2.5]:
 for i in [0,3,6,9]:parts.append(box(x,-9.5+i*2.5,2.8+1.5*(i+1),1.3,1.3,5.6))
 # rotate rising x beam to run along y
 rail=beam((0,0,9.7),(22.5,0,23.2),1.4,1.4).rotate((0,0,90)).translate((x,-9.5,0));parts.append(rail)
# Small landing only; no invented full rear observation/parking deck.
parts.append(box(-17,14.1,16.2,31,3,1.8))
# Low linear planter edge and short rail-backed walkway fragment, openly truncated.
parts.append(box(26,6,3,53,2,2.5))
# Far ATM simple recessed gray portal, glazed fields as backed relief, no machine detail.
parts += [box(70,0,3,31,16,21),box(70,-8.7,3,31,1.4,1.6)]
# recesses cut into front; preserve a solid rear backing, not interior reconstruction.
atm=parts[-2]
atm-=box(70,-8,4.6,25,3.2,17)
# central deeper door/recess; kept dark by face coloring
atm-=box(70,-7.5,4.6,7,5,17)
parts[-2]=atm
for x in [57,65.8,74.2,83]:parts.append(box(x,-8.1,4.4,1,1.2,17.7))
for z in [10,19.7]:
 for x in [61.4,78.6]:parts.append(box(x,-8.1,z,8.8,1.2,.9))
# Keep far-right open frame; no old guardhouse above ATM.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('coffee_brown_canopy_and_frames','#674431'),('neutral_added_display_base','#A0A39B'),('red_brick_waiting_bay','#AB5942'),('gray_ATM_portal_and_stairs','#9A9E9B'),('dark_backed_ATM_glazing','#334B4D'),('thickened_dark_stair_rails','#4E5350')]
tri=t.triangles;lo=tri.min(axis=1);hi=tri.max(axis=1);cen=tri.mean(axis=1);colors=np.zeros(len(f),dtype=int)
colors[hi[:,2]<=3.001]=1
colors[(((lo[:,0]>=-67.51)&(hi[:,0]<=-64.49)&(hi[:,2]<27.51))|((lo[:,0]>=-66.01)&(hi[:,0]<=-35.99)&(lo[:,1]>=5.39)&(hi[:,2]<=16.91)))&(lo[:,2]>=2.99)]=2
colors[(lo[:,0]>=-33)&(hi[:,0]<=-1)&(hi[:,2]<=18.01)&(lo[:,2]>=2.99)]=3
colors[(lo[:,0]>=54.49)&(hi[:,0]<=85.51)&(hi[:,2]<=24.01)&(lo[:,2]>=2.99)]=3
colors[(lo[:,0]>=57.49)&(hi[:,0]<=82.51)&(lo[:,1]>=-6.41)&(hi[:,1]<=-4.99)&(lo[:,2]>=4.59)&(hi[:,2]<=21.61)]=4
for x in [-31.5,-2.5]:colors[(lo[:,0]>=x-.71)&(hi[:,0]<=x+.71)&(lo[:,2]>5)]=5
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,scope='Street-facing canopy, brick waiting bay, single broad stair, far ATM portal; not full Ting Song terrace or parking deck',canopy_alignment_x_mm=xs,canopy_top_profile_z_mm=zs,profile='asymmetric raised near end, long low middle, gently raised far end',support_count_is_approximation=True,stair_count=1,stair_location='immediately after left waiting bay; not center of full frontage',approximate_stair_steps=10,canopy_depth_mm=25,roof_thickness_mm=1.8,main_posts_mm=2.4,stair_rail_mm=1.4,brick_perforations_mm=[1.8,1.5],fascia_relief_projection_mm=.55,added_base_mm=[220,36,3],unseen_rear='Neutral cut; only a short landing, no full terrace deck/parking slab',excluded=['old pitched-roof guardhouse','rear parking','full upper deck','trees','lettering','ATM machinery','road','underground foundations']),indent=2)+'\n')
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
