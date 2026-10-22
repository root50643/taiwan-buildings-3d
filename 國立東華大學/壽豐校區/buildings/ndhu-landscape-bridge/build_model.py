"""國立東華大學 壽豐校區 景觀橋 / NDHU Shoufeng Landscape Bridge.
2019-renovated open lattice version; approximate exterior, not surveyed.
Hidden bridge ribs and joints omitted rather than asserted.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('display_base','#697C78',255),('stone_mortar','#595C55',255),('stone_faces','#A5A295',255),('exposed_gray_arch','#A8AAA5',255),('walkway_wood','#725746',255),('lattice_dark_brown','#5B4238',255),('light_rail_and_frame','#E4E3CF',255),('gold_scroll_metal','#D3A53E',255),('yellow_rail_bands','#F0C638',255),('dark_red_rail_panels','#653937',255),('flat_road','#7E8582',255)]
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
def deck(x):return 25+7*(1-(x/60)**2)
def arch(x):return 5+10*(1-(x/60)**2)
box((0,0,1),(202,92,2),0,'non_survey_display_base')
# Short bank blocks and approach platforms only; bridge undercroft stays open.
for sx in [-1,1]:
 x=sx*80;box((x,0,13),(40,78,22),1,'short_bank_abutment');box((x,0,24.3),(40,78,1.8),2,'short_approach_platform')
 # Stylized relief masonry, not surveyed joint courses.
 for side in [-1,1]:
  for row in range(5):
   for j in range(8):
    xx=x-17.5+j*5+(1 if row%2 else 0);zz=4+row*4
    # Irregular chamfered stone relief, estimated pattern rather than brick bond.
    rng=np.random.default_rng(100+row*8+j);w=4.35;h=3.45
    pts=[[-w/2+.3,-h/2], [w/2-.45,-h/2+.15], [w/2,h/2-.5], [w/2-.65,h/2], [-w/2+.35,h/2-.15], [-w/2,-h/2+.65]]
    pts=np.array(pts)+rng.uniform(-.23,.23,(6,2))
    stone=CrossSection([pts]).extrude(.8).rotate((90,0,0)).translate((xx,side*39+.4,zz));add(stone,2,'estimated_irregular_stone_relief')
box((0,0,23.8),(121,40,2.4),10,'central_flat_vehicle_bridge_simplified_slab')
for y in [-18,18]:box((0,y,25.08),(199,.7,.18),6,'road_edge_line')
for x in range(-94,100,12):box((x,0,25.08),(6,.6,.18),6,'road_center_dash')
for side in [-1,1]:
 y=side*29
 # Narrow curved decks independently; no broad common arch surface.
 for x in np.linspace(-60,60,61)[:-1]:
  xm=x+1;beam((x,y,deck(x)),(x+2,y,deck(x+2)),1.8,4,'curved_walkway_core')
  box((xm,y,deck(xm)),(2.15,14,1.8),4,'walkway_plank_approximation')
 for edge in [-1,1]:
  yy=y+edge*6.6
  pts=[(x,yy,deck(x)+7.4) for x in np.linspace(-60,60,61)];path(pts,1.1,6,'curved_top_rail')
  path([(x,yy,deck(x)+1.5) for x in np.linspace(-60,60,61)],.9,6,'curved_lower_rail')
  for x in np.linspace(-59,59,60):beam((x,yy,deck(x)+1.4),(x,yy,deck(x)+7.4),.85,6,'white_open_railing_baluster')
  for k,x in enumerate(np.arange(-55,60,10)):
   beam((x-3.5,yy,deck(x-3.5)+4.1),(x+3.5,yy,deck(x+3.5)+4.1),1.45,8,'yellow_rail_band')
   beam((x-3.3,yy,deck(x-3.3)+6.1),(x+3.3,yy,deck(x+3.3)+6.1),1.55,9,'dark_red_rail_panel')
  for x in np.arange(-60,61,20):beam((x,yy,deck(x)),(x,yy,deck(x)+8),1.3,6,'rail_posts')
 yy=side*31
 path([(x,yy,arch(x)) for x in np.linspace(-61,61,80)],2.5,3,'visible_outer_gray_arch_band')
 # Six exposed supports each side: far side symmetry is expressly estimated.
 for x in [-46,-28,-9,9,28,46]:
  z=arch(x);beam((x,yy,z),(x,yy,z+3),1.5,3,'visible_arch_support')
  # Curled lower end plus upward sweeping gold bracket, planar exterior shape.
  z0=z+3; inner_y=side*31
  curl=[(x,inner_y+side*1.55*math.cos(t),z0+1.55*math.sin(t)) for t in np.linspace(math.pi*.4,math.pi*2.0,22)]
  path(curl,1.2,7,'gold_curled_bracket_end')
  p=[(x,inner_y+side*(1.55*(1-t)+5*t*t),z0+(deck(x)-1.1-z0)*t) for t in np.linspace(0,1,18)]
  path(p,1.6,7,'gold_curved_bracket_arm')
  beam(p[-1],(x,side*28,deck(x)-1),1.25,7,'gold_upper_bracket_seat')
 # Four piers at walkway termini, matching the four open pavilions.
 for x in [-73,73]:
  box((x,y,25),(25,22,1.8),3,'pavilion_platform')
  for dx in [-8.5,8.5]:
   for dy in [-8.5,8.5]:
    cx=x+dx;cy=y+dy
    for ox,oy in [(-1.15,-1.15),(-1.15,1.15),(1.15,-1.15),(1.15,1.15)]:beam((cx+ox,cy+oy,25.6),(cx+ox,cy+oy,53),.85,6,'four_corner_lattice_column_frame')
    for z in np.arange(26.5,53,2):ring(cx,cy,z,3.4,.9,5,'open_column_horizontal_lattice')
    ring(cx,cy,28.5,3.6,1.4,9,'column_dark_red_lower_band')
  ring(x,y,53,23.5,1.3,6,'square_eave_frame')
  ring(x,y,52.8,17,1.3,6,'column_top_tie_frame')
  for dx,dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:beam((x+dx*8.5,y+dy*8.5,52.8),(x+dx*11.75,y+dy*11.75,53),1.25,6,'eave_corner_tie')
  for dx,dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:beam((x+dx*11.75,y+dy*11.75,53),(x,y,62),1,6,'hip_roof_diagonal_frame')
  for i in range(9):ring(x,y,53.5+i,23-2.5*i,.9,5,'open_hip_roof_horizontal_lattice')
FEATURES=dict(name='景觀橋 / Landscape Bridge',school='國立東華大學',campus='壽豐校區',slug='ndhu-landscape-bridge',selected_version='2019 renovation; 2020,2023,2025 photographed open lattice pavilions',estimated_not_surveyed=True,three_parallel_routes=True,central_road_flat=True,independent_narrow_arched_walkways=2,pavilions=4,visible_gold_scrolls_per_outer_side=6,far_side_scroll_count_symmetry_estimated=True,hidden_internal_ribs_and_crossbeam_counts_omitted=True,roof_lattice_not_solid=True,all_materials_opaque=True,no_actual_print=True,support_free_certified=False,uncertain=['all physical dimensions and display scale','lattice,baluster and masonry counts','scroll curvature and far-side exact counts','hidden ribs, joints and crossbeam arrangement','NLSC2024 watermark is not verified capture year'],omitted=['lake and full banks','adjacent buildings','hidden engineering structure','source images'])
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.001).simplify(.001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
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
