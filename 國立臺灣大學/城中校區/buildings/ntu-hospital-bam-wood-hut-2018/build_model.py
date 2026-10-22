"""NTUH International Convention Center forecourt Bam-Wood Hut, photographed 2018.
Source-bound complete exterior approximation; not survey or engineering geometry.
Display mm: nominal envelope about 1:100, with disclosed strengthened thin members.
Front/step = negative Y. Both sides and ends remain geometrically open.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,Mesh64,OpType
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('warm_cypress_cedar_timber','#C89453',255),('light_bamboo_tension_members','#D9BD81',255),('translucent_polycarbonate_roof','#E3ECEA',100),('galvanized_steel_brackets_and_drip_edges','#8E999B',255),('cedar_deck_boards','#B58B5C',255),('dark_steel_deck_base','#384046',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty() and m.volume()>0,name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def beam(a,b,w,d):
 a,b=np.array(a,float),np.array(b,float);z=b-a;length=np.linalg.norm(z);z/=length
 ref=np.array([0,1,0.]) if abs(z[1])<.95 else np.array([1,0,0.]);x=np.cross(ref,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return Manifold.cube((w,d,length)).translate((-w/2,-d/2,0)).transform(np.column_stack([x,y,z,a]))
def rod(a,b,r=.43):
 a,b=np.array(a,float),np.array(b,float);z=b-a;length=np.linalg.norm(z);z/=length
 ref=np.array([0,1,0.]) if abs(z[1])<.95 else np.array([1,0,0.]);x=np.cross(ref,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return Manifold.cylinder(length,r,r,12).transform(np.column_stack([x,y,z,a]))
def roof_patch(a,b,c,d,th=.78):
 # Two planar triangular prisms over a bilinear frame-to-frame panel.
 vs=np.array([a,b,c,d],float);vs=np.vstack([vs,vs+[0,0,th]])
 fs=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint32)
 m=Manifold(Mesh64(vs,fs[:,[0,2,1]]));assert m.status().name=='NoError';return m
# Original raised deck, not an additional arbitrary site plinth. Hidden underside
# is intentionally a filled display core, NOT a reconstruction of every joist.
base=box(0,0,0,99,182,2.5)
# Shallow steel-edge vent recesses preserve real negative space only at the edge;
# their spacing/size are inferred, no hidden through-deck installation is claimed.
for y in np.linspace(-82,82,17):
 for side in [-1,1]:base-=box(side*49.5,y,.85,.7,2.1,.8)
for x in np.linspace(-40,40,9):base-=box(x,91,.85,2.1,.7,.8)
add(base,5,'original_raised_steel_deck_base_hidden_core_simplified')
for i in range(66):
 x=-49.5+(i+.5)*1.5
 add(box(x,0,2.45,1.40,182,1.05),4,f'cedar_deck_board_{i+1:02}')
for y in [-29.33,29.33]:add(box(0,y,3.38,99,.55,.20),5,'deck_cross_seam_approximation')
add(box(0,-93.4,0,20,5.2,1.8),4,'source_front_access_step')
# Published total 18.2m/9.9m/5.2m, post span 5.0--8.2m. Photos establish 20
# transverse portals. Intermediate coordinates remain fitted estimates.
ys=np.linspace(-88,88,20);frames=[]
for i,y in enumerate(ys):
 u=(y/88)**2;span=50+32*u;ridge_z=43.6+7.0*u;ridge_x=7.5+1.5*u;eave_z=27.6-.9*u
 left=(-span/2-7,y,eave_z);ridge=(ridge_x,y,ridge_z);right=(span/2+7,y,eave_z)
 def roof_z(x):return eave_z+(ridge_z-eave_z)*(x-left[0])/(ridge_x-left[0]) if x<=ridge_x else ridge_z+(eave_z-ridge_z)*(x-ridge_x)/(right[0]-ridge_x)
 posts=[(-span/2,y,roof_z(-span/2)),(span/2,y,roof_z(span/2))]
 for k,p in enumerate(posts):
  add(beam((p[0],y,3.4),p,1.8,1.0),0,f'frame_{i+1:02}_timber_post_{k+1}')
  add(box(p[0],y,3.4,2.0,1.5,.55),3,f'frame_{i+1:02}_post_shoe_{k+1}')
 for k,(a,b) in enumerate([(left,ridge),(ridge,right)]):add(beam(a,b,1.8,1.0),0,f'frame_{i+1:02}_straight_rafter_{k+1}')
 # Six-segment bamboo tension polygon stays distinctly below each roof rafter.
 # The seven nodes are estimates constrained by the published typical section.
 xs=[-span/2+.3,-span/2+5.0,-span*.18,ridge_x-1.4,span*.32,span/2-4.2,span/2-.3]
 zs=[5.3,roof_z(xs[1])-5.0,roof_z(xs[2])-4.1,ridge_z-5.0,roof_z(xs[4])-4.7,roof_z(xs[5])-5.2,5.3]
 # Source section10 has a flattened high bamboo segment, NOT a second gable.
 zs[3]=(zs[2]+zs[4])/2+.6
 nodes=[(x,y,z) for x,z in zip(xs,zs)]
 for k,(a,b) in enumerate(zip(nodes,nodes[1:])):add(rod(a,b),1,f'frame_{i+1:02}_bamboo_tension_segment_{k+1}')
 for k,n in enumerate(nodes[1:-1],1):
  # Paired stand-offs form a narrow V in the longitudinal direction. Small
  # rectangular galvanized steel pipes are strengthened to .55 x .65 mm.
  top=(n[0],y,roof_z(n[0]))
  for side in [-1,1]:add(beam((top[0],y+side*.46,top[2]),n,.55,.65),3,f'frame_{i+1:02}_steel_standoff_{k}_{side}')
  add(rod((n[0],y-.55,n[2]),(n[0],y+.55,n[2]),.45),3,f'frame_{i+1:02}_node_pin_{k}')
 for k in [0,6]:add(beam(nodes[k],(posts[k//6][0],y,5.3),.65,.65),3,f'frame_{i+1:02}_bamboo_foot_connection_{k}')
 frames.append(dict(number=i+1,y=float(y),span=span,roof=[left,ridge,right],posts=posts,bamboo_nodes=nodes))
# Roof has two DIFFERENT planar slopes per frame, and varies along its length.
# 19 paired translucent panels join consecutive rafters, rather than an opaque
# barrel vault. Geometry remains physical solid in monochrome STL.
for i,(a,b) in enumerate(zip(frames,frames[1:])):
 for k in [0,1]:
  # Raising panel datum .72 above rafter centre maintains physical overlap.
  p=[np.array(a['roof'][k])+[0,0,.72],np.array(b['roof'][k])+[0,0,.72],np.array(b['roof'][k+1])+[0,0,.72],np.array(a['roof'][k+1])+[0,0,.72]]
  add(roof_patch(*p),2,f'polycarbonate_roof_bay_{i+1:02}_slope_{k+1}')
 for k,label in [(0,'left_eave'),(1,'ridge'),(2,'right_eave')]:
  aa=np.array(a['roof'][k])+[0,0,1.23];bb=np.array(b['roof'][k])+[0,0,1.23]
  add(beam(aa,bb,.72,.72),3,f'continuous_{label}_trim_bay_{i+1:02}')
 # A single longitudinal diagonal per side/bay, NOT arbitrary paired Xs.
 # This schematic connection sequence is photo-based and explicitly uncertain.
 # The two halves reverse hand toward the waist, like the repeated side ties.
 for side in [0,1]:
  j=0 if side==0 else 6;shoulder=1 if side==0 else 5
  lo,hi=(a,b) if i<9 else (b,a)
  add(rod(lo['bamboo_nodes'][j],hi['bamboo_nodes'][shoulder],.38),1,f'longitudinal_single_diagonal_side_{side+1}_bay_{i+1:02}')
# Thin roof sheet edges at the two open ends, no opaque gable triangle.
for i in [0,19]:
 r=frames[i]['roof']
 for k in [0,1]:add(beam(np.array(r[k])+[0,0,1.2],np.array(r[k+1])+[0,0,1.2],.70,.7),3,f'open_end_drip_trim_{i+1}_{k}')
# Boolean union and exact post-export triangle identity across STL/3MF/Blend.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.0001);me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Compute stored STL normals from the exact FLOAT32 triangle coordinates to be
# exported, rather than stale higher-precision normals. No triangle is repaired.
tri=np.asarray(vs[fs],dtype=np.float32);normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lens=np.linalg.norm(normals,axis=1);assert np.all(lens>0)
out=np.zeros(len(fs),dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);out['n']=normals/lens[:,None];out['v']=tri
raw=b'NTUH 2018 Bam-Wood Hut original approximate mesh'.ljust(80,b'\0')+struct.pack('<I',len(fs))+out.tobytes();(O/'model.stl').write_bytes(raw);n=len(fs)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32));t=trimesh.Trimesh(v,f,process=False)
features=dict(estimated_not_surveyed=True,school='國立臺灣大學',campus='城中校區（臺大醫院場域）',slug='ntu-hospital-bam-wood-hut-2018',target_path='國立臺灣大學/城中校區/buildings/ntu-hospital-bam-wood-hut-2018',source_project_year=2018,front_direction='negative Y, small access step; not geographic north',frame_count=20,bay_count=19,roof_panels=38,source_envelope_m=[18.2,9.9,5.2],source_height_conflict='Specification5.2m; typical section4.2–5.0m; magazine5m. Not a surveyed reconciliation.',frames=frames,nominal_scale='approximately1:100 envelope only; not exact fabrication scale',display_deck_mm=[99,182,3.5],timber_section_display_mm=[1.8,1.0],bamboo_diameter_display_mm=.86,longitudinal_diagonal_diameter_display_mm=.76,steel_standoff_display_mm=[.55,.65],roof_vertical_thickness_mm=.78,roof_alpha_0_255=100,deck_hidden_core_is_simplified=True,no_added_site_plinth=True,generator_boolean_tolerance_mm=.0001,material_provenance_method="nearest source surface after manifold generator simplification; not a geometric post-export repair",material_provenance_nearest_surface_max_distance_mm=maxdist,roof_STL_translation='38 roof patches become a continuous physical sheet, opaque with opaque filament; alpha only in 3MF/Blend. Not pre-separated fabrication parts.',uncertain=['per-frame stations and longitudinal waist/ridge curves','ridge offset and asymmetric slopes','longitudinal diagonal exact connection sequence and hand reversals','roof panel seams and drip trims','steel joint hardware and pins','deck plank/vent count and hidden filled underside core'],omitted=['surrounding plaza, buildings, trees, sculpture and people','precise bolts, bamboo nodes and LED installation','underground anchors','unbuilt Prototype II and III variants','source photos and drawings'],source_appearance='2018 photographed state, not verified 2026 condition',no_actual_print=True,support_free_certified=False,parts=part_records)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b,'alpha':c} for a,b,c in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vv=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vv,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,22,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
