"""懸鏈・榭 / Sewn Pavilion, NCKU Guangfu campus historical exterior approximation."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[('pale_plywood','#D8C9A8',255),('light_plywood','#E5D9BC',255),('warm_plywood','#CDBB98',255),('wood_seams_and_foot_tabs','#BCA782',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
def box(origin,size):return Manifold.cube(size).translate(origin)
def prism(poly,z,h):return CrossSection([poly]).extrude(h).translate((0,0,z))
def beam(a,b,w,d=None):
 a=np.asarray(a,float);b=np.asarray(b,float);zz=b-a;L=np.linalg.norm(zz);zz/=L
 q=np.array([0.,0.,1.]) if abs(zz[2])<.9 else np.array([1.,0.,0.]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cube((d or w,w,L)).translate((-(d or w)/2,-w/2,0)).transform(np.column_stack([xx,yy,zz,a]))
def rod(a,b,r,n=16):
 a=np.asarray(a,float);b=np.asarray(b,float);zz=b-a;L=np.linalg.norm(zz);zz/=L
 q=np.array([0.,0.,1.]) if abs(zz[2])<.9 else np.array([1.,0.,0.]);xx=np.cross(q,zz);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
 return Manifold.cylinder(L,r,r,n).transform(np.column_stack([xx,yy,zz,a]))

from scipy.interpolate import CubicSpline
from manifold3d import Mesh64
# Display millimetres ONLY. No source establishes real dimensions or a measured scale.
# Explicit seven arch boundaries give six indexed bands for each leaf, as source A/B/C 0..5.
# Curves are visual approximations, not an asserted catenary formula or fabrication geometry.
FOOT_R=68.;THICK=.95;L=180.;W=12.;T0=.014
feet=np.array([[0,68,0],[-58.889727,-34,0],[58.889727,-34,0]],float)
B=CubicSpline(np.arange(7),[19.,9.,-4.,-18.,-31.,-42.,-51.],bc_type='natural')
H=CubicSpline(np.arange(7),[80.,85.,87.,86.,82.,76.,69.],bc_type='natural')
def basis(leaf):
 a=feet[leaf];b=feet[(leaf+1)%3];mid=(a+b)/2;n=-mid.copy();n[2]=0;n/=np.linalg.norm(n);return a,b,n

def surface(leaf,t,s):
 a,b,n=basis(leaf);t=np.asarray(t);s=np.asarray(s);q=np.maximum(0,np.sin(np.pi*t))
 return a+(b-a)*t[...,None]+n*(B(s)*q)[...,None]+np.array([0,0,1])*(2.5+H(s)*q**.81)[...,None]
def normal(leaf,t,s):
 eps=.00001;dt=surface(leaf,t+eps,s)-surface(leaf,t-eps,s);ds=surface(leaf,t,s+eps)-surface(leaf,t,s-eps);norm=np.cross(dt,ds);return norm/np.linalg.norm(norm,axis=-1)[...,None]
HOLES=[];SEAMS=[]
for leaf in range(3):
 for band in range(6):
  rng=np.random.default_rng(5100+100*leaf+band)
  uv=CrossSection([[(0,-.8),(L,-.8),(L,W+.8),(0,W+.8)]])
  # Irregular through perforations, margins and representative patterns, NOT a count copy.
  for k,u in enumerate(np.linspace(25,155,13)):
   uu=u+rng.uniform(-2.5,2.5);vv=rng.uniform(3.5,8.5);rx=rng.uniform(1.4,3.7);ry=rng.uniform(1.25,2.5)
   ang=np.linspace(0,2*np.pi,7,endpoint=False);radii=rng.uniform(.75,1.18,7)
   pts=np.column_stack([uu+rx*np.cos(ang)*radii,vv+ry*np.sin(ang)*radii])
   uv-=CrossSection([pts.tolist()]);t=T0+uu/L*(1-2*T0);s=band+vv/W
   HOLES.append(dict(leaf='ABC'[leaf],band=band,index=k,uv_center=[float(uu),float(vv)],center=surface(leaf,t,s).tolist(),normal=normal(leaf,t,s).tolist()))
  flat=uv.extrude(THICK).translate((0,0,-THICK/2)).refine_to_length(3.2)
  def warp(p):
   t=T0+p[:,0]/L*(1-2*T0);s=band+p[:,1]/W;return surface(leaf,t,s)+normal(leaf,t,s)*p[:,2,None]
  solid=flat.warp_batch(warp);add(solid,[0,1,0,2,1,0][band],f'leaf_{"ABC"[leaf]}_indexed_curved_perforated_band_{band}')
 # Thin raised seam strips retain band readability without becoming new structural feet.
 for j in range(1,6):
  uv=CrossSection([[(0,-.4),(L,-.4),(L,.4),(0,.4)]]).extrude(1.37).translate((0,0,-.72)).refine_to_length(3.)
  def warp_seam(p):
   t=T0+p[:,0]/L*(1-2*T0);s=j+p[:,1]/W;return surface(leaf,t,s)+normal(leaf,t,s)*p[:,2,None]
  add(uv.warp_batch(warp_seam),3,f'leaf_{"ABC"[leaf]}_band_edge_seam_{j}')
 # A small transverse join strip at representative panel division t=.34/.66, not all fasteners.
 for t in [.34,.66]:
  for band in range(6):
   uv=CrossSection([[(t*L-.22,0),(t*L+.22,0),(t*L+.22,W),(t*L-.22,W)]]).extrude(.5).translate((0,0,-.63)).refine_to_length(2.)
   def warp_joint(p):
    tt=T0+p[:,0]/L*(1-2*T0);s=band+p[:,1]/W;return surface(leaf,tt,s)+normal(leaf,tt,s)*p[:,2,None]
   add(uv.warp_batch(warp_joint),3,f'leaf_{"ABC"[leaf]}_representative_panel_join_{band}_{t}')
# Central three-way arching connector: NOT a planar cap. Three ruled curved panels
# taper to the same feet and surround a small triangular opening at their crown.
# Size and hidden curvature are explicitly approximate; diagram blue is NOT paint.
# Construct patches between each inner arch and corresponding side of the little triangle.
hole=feet[:,:2]*.065
CONNECTOR=[];FRAME_SAMPLES=[];PATCHES=[];N_T=64;N_R=20
for leaf in range(3):
 a,b,n=basis(leaf);qa=np.r_[hole[leaf],82.5];qb=np.r_[hole[(leaf+1)%3],82.5]
 # Parametric transition starts at inner band edge s=0 and ends at small triangular rim.
 def patch(t,r):
  edge=surface(leaf,t,np.zeros_like(t)+.12);inner=qa+(qb-qa)*t[...,None]
  return edge*(1-r[...,None])+inner*r[...,None]
 def pnormal(t,r):
  eps=.00001;dt=patch(t+eps,r)-patch(t-eps,r);dr=patch(t,r+eps)-patch(t,r-eps);nn=np.cross(dt,dr);return nn/np.linalg.norm(nn,axis=-1)[...,None]
 # One shared-edge closed mesh for all three panels; no near-coincident seam solids.
 tt,rr=np.meshgrid(np.linspace(0,1,N_T+1),np.linspace(0,1,N_R+1),indexing='ij')
 pp=patch(tt,rr);nn=pnormal(tt,rr);fac=1/np.maximum(.12,np.abs(nn[:,:,2]))
 pp[0]=a+(qa-a)*rr[0,:,None];pp[0,:,2]=2.5+(82.5-2.5)*rr[0]
 pp[-1]=b+(qb-b)*rr[-1,:,None];pp[-1,:,2]=2.5+(82.5-2.5)*rr[-1]
 PATCHES.append((pp,fac))
 CONNECTOR.append(dict(leaf='ABC'[leaf],inner_triangle_edge=[qa.tolist(),qb.tolist()]));FRAME_SAMPLES.extend([dict(leaf='ABC'[leaf],t=t,center=patch(np.array(t),np.array(.5)).tolist(),normal=pnormal(np.array(t),np.array(.5)).tolist(),vertical_thickness_mm=float(THICK/max(.12,abs(pnormal(np.array(t),np.array(.5))[2]))),nominal_normal_thickness_mm=THICK) for t in [.1,.3,.5]])
# Shared radial seams use the exact same vertices AND averaged thickness.
cv=[];cf=[];cidx={}
def cvertex(leaf,i,j,k):
 if i==0:key=('seam',leaf,j,k);factor=(PATCHES[leaf][1][0,j]+PATCHES[(leaf-1)%3][1][-1,j])/2
 elif i==N_T:key=('seam',(leaf+1)%3,j,k);factor=(PATCHES[leaf][1][-1,j]+PATCHES[(leaf+1)%3][1][0,j])/2
 else:key=('panel',leaf,i,j,k);factor=PATCHES[leaf][1][i,j]
 if key not in cidx:
  p=PATCHES[leaf][0][i,j].copy();p[2]+=(1 if k else -1)*THICK*factor/2;cidx[key]=len(cv);cv.append(p.tolist())
 return cidx[key]
for leaf in range(3):
 for i in range(N_T):
  for j in range(N_R):
   for k in [0,1]:
    a,b,c,d=[cvertex(leaf,ii,jj,k) for ii,jj in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]]
    cf.extend([[a,b,c],[a,c,d]] if k else [[a,c,b],[a,d,c]])
  for j in [0,N_R]:
   a,b,c,d=cvertex(leaf,i,j,0),cvertex(leaf,i+1,j,0),cvertex(leaf,i+1,j,1),cvertex(leaf,i,j,1)
   cf.extend([[a,b,c],[a,c,d]] if j==0 else [[a,c,b],[a,d,c]])
add(Manifold(Mesh64(np.asarray(cv,dtype=np.float64),np.asarray(cf,dtype=np.uint64))),1,'central_threeway_shared_edge_arching_frame_with_small_triangle_gap')
# Three small shared foot/tab zones; never introduce a fourth support or a floor.
for i,f in enumerate(feet):
 add(box(f+np.array([-2.26,-2.26,0]),(4.52,4.52,10.6)),0,f'shared_foot_{i}_narrow_laminated_bundle')
 for angle in [0,60,120]:
  add(Manifold.cube((6.5,1.15,8.9)).translate((-3.25,-.575,0)).rotate((0,0,angle+120*i)).translate(f),3,f'shared_foot_{i}_interlocking_thin_plate_{angle}')
 # The intersecting plate bundle meets truncated band ends directly; no false struts.

FEATURES=dict(name='懸鏈・榭 / Sewn Pavilion',school='國立成功大學',campus='光復校區',site='建築系館院落（成品與校方院落照片成組特徵交叉推定）',slug='ncku-sewn-pavilion',target_path='國立成功大學/光復校區/buildings/ncku-sewn-pavilion',historical_exterior=True,thesis_year=2013,article_issue='2014-04',exact_photo_dates_unknown=True,current_survival_not_claimed=True,estimated_not_surveyed=True,display_dimensions_not_survey_scale=True,three_leaves=['A','B','C'],indexed_bands_per_leaf=6,shared_ground_feet=3,feet_centers_mm=feet.tolist(),central_threeway_arching_frame=True,small_central_triangle_opening=True,central_triangle_vertices_xy_mm=hole.tolist(),central_frame_simplified=True,central_frame_variable_vertical_thickness_to_approximate_normal_0_95mm=True,central_frame_max_vertical_factor=1/.12,normal_panel_thickness_mm=THICK,arch_boundary_bulges_mm=[19,9,-4,-18,-31,-42,-51],arch_boundary_heights_mm=[80,85,87,86,82,76,69],band_curvature_not_an_engineering_catenary=True,solid_band_samples=[dict(leaf='ABC'[leaf],band=band,center=surface(leaf,np.array(.10),np.array(band+.5)).tolist(),normal=normal(leaf,np.array(.10),np.array(band+.5)).tolist(),nominal_thickness_mm=THICK) for leaf in range(3) for band in range(6)],central_frame_samples=FRAME_SAMPLES,perforation_hole_samples=HOLES,representative_perforation_count=len(HOLES),no_added_ground_slab=True,all_materials_opaque=True,no_actual_print=True,support_free_certified=False,uncertain=['absolute real dimensions and exact 3D curves','individual perforations, counts and shapes','central connector hidden curvature and exact gap size','panel seams and tiny joints, foot tabs and sheet thickness'],omitted=['campus background, stairs, lawn, buildings, trees and temporary lights','hidden foundations, screw threads and internal fasteners','raw source photos, drawings, PDFs and HTML'])
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
clip=box((-200,-200,0),(400,400,200)).as_original();material_for_id[clip.original_id()]=1;m=m^clip;source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.02).simplify(.02)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3].astype(np.float32).astype(np.float64);fs=np.asarray(me.tri_verts);vs,inv=np.unique(vs,axis=0,return_inverse=True);fs=inv[fs]
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.06,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
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
