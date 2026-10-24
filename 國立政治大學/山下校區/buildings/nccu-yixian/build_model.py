"""NCCU Yixian Hall — source-relative approximate complete main-building exterior."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection,JoinType
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from NCCU source observations.
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


SCALE=3.; G=1.2; H=3.45; RF=G+7*H
palette=[('display_base','#858D87',255),('buff_tile_proxy','#B2A080',255),('white_screen_and_frames','#E2DED3',255),('opaque_green_blue_glass','#589395',255),('roof_and_recess_gray','#747E7B',255),('muted_red_canopy_frame','#A66B58',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
def poly(points,z,h,c,n):add(CrossSection([points]).extrude(h).translate((0,0,z)),c,n)
def coord(points):return [((x-150)*.1,(300-y)*.1) for x,y in reversed(points)]
# Independently traced rotated emergency layouts; pixel-relative, not measured metre dimensions.
traces={
'B1':[(150,89),(199,89),(199,65),(224,35),(297,35),(297,55),(580,55),(580,362),(150,362),(150,292),(199,292),(199,221),(150,221)],
'1F':[(150,145),(177,145),(177,88),(207,88),(207,108),(238,108),(238,118),(254,118),(254,107),(294,107),(294,89),(537,89),(537,118),(579,118),(579,196),(537,196),(537,294),(457,294),(457,361),(277,361),(277,294),(199,294),(199,218),(150,218)],
'2F':[(150,161),(177,161),(177,103),(537,103),(537,135),(579,135),(579,211),(537,211),(537,313),(431,313),(431,282),(302,282),(302,313),(199,313),(199,237),(150,237)],
'3F':[(150,139),(177,139),(177,80),(209,80),(209,74),(218,74),(251,101),(292,101),(292,53),(441,53),(441,80),(537,80),(537,112),(579,112),(579,188),(537,188),(537,351),(431,351),(431,258),(302,258),(302,351),(199,351),(199,214),(150,214)],
'4F':[(150,146),(177,146),(177,88),(209,88),(209,83),(218,83),(251,109),(292,109),(292,60),(441,60),(441,89),(537,89),(537,120),(579,120),(579,196),(537,196),(537,298),(431,298),(431,266),(302,266),(302,298),(199,298),(199,221),(150,221)],
'5F':[(150,145),(177,145),(177,87),(209,87),(209,80),(218,80),(251,107),(292,107),(292,59),(441,59),(441,87),(537,87),(537,118),(579,118),(579,194),(537,194),(537,295),(431,295),(431,265),(302,265),(302,295),(199,295),(199,220),(150,220)],
'6F':[(150,144),(177,144),(177,86),(209,86),(209,80),(218,80),(251,107),(292,107),(292,59),(441,59),(441,87),(537,87),(537,118),(579,118),(579,194),(537,194),(537,295),(431,295),(431,264),(302,264),(302,295),(199,295),(199,219),(150,219)],
'7F':[(150,136),(177,136),(177,78),(209,78),(209,72),(218,72),(251,99),(292,99),(292,51),(441,51),(441,78),(537,78),(537,110),(579,110),(579,186),(537,186),(537,286),(431,286),(431,256),(302,256),(302,286),(199,286),(199,211),(150,211)],
'R':[(150,136),(179,136),(179,116),(292,116),(292,78),(537,78),(537,110),(579,110),(579,186),(537,186),(537,286),(431,286),(431,256),(302,256),(302,286),(199,286),(199,211),(150,211)]}
offsets={'B1':9,'1F':8,'2F':25,'3F':2,'4F':10,'5F':8,'6F':8,'7F':0,'R':0}
raw_traces={k:list(v) for k,v in traces.items()}
traces={k:[(x,y-offsets[k]) for x,y in v] for k,v in traces.items()}
# B1 is present below ground as bounded exterior mass, interior tier stair omitted.
poly(coord(traces['B1']),0,G,4,'B1_below_display_ground_envelope')
block(-2,45,-8,29,0,.6,0,'display_base_not_surveyed_site')
for lev in range(1,8):
 pts=coord(traces[str(lev)+'F']);z=G+(lev-1)*H
 m=CrossSection([pts]).extrude(H+.02).translate((0,0,z))
 # Open circulation recess next to glazing and single stair screens, not dark paint.
 if lev>=3:
  m-=cube(5.7,14.2,19.8,23.1,z+.45,z+H-.38)
 if lev==1:m-=cube(5.7,29,18.8,23,z+.1,z+H-.3)
 add(m,1,'independent_'+str(lev)+'F_complete_outline')
 add(CrossSection([pts]).offset(.04,JoinType.Miter).extrude(.24).translate((0,0,z+H-.18)),2,'floor_'+str(lev)+'_slightly_proud_edge_band')
# 4F low rear terraces on footprints present on 3F, not extra enclosed storeys.
for x0,x1 in [(4.9,15.2),(28.1,38.7)]:block(x0+.03,x1-.03,-4.87,1.37,G+3*H-.12,G+3*H+.16,4,'4F_rear_terrace')
poly(coord(traces['R']),RF,.33,4,'R_continuous_asymmetric_roof_no_central_hole')
for a,b in zip(coord(traces['R']),coord(traces['R'])[1:]+coord(traces['R'])[:1]):beam((*a,RF+.45),(*b,RF+.45),.35,2,'R_low_parapet')
block(0,9.4,8.9,16.4,RF-.1,RF+2.1,1,'plan_left_two_lift_stair_roof_access')
block(38.65,42.9,11.4,19.0,RF-.1,RF+1.55,1,'plan_right_single_stair_roof_access')
# Front glazing on upper long side: 702/703 footprint, source-right core maps photo-left.
block(14.25,29.05,24.7,25.12,G+2*H,RF+.1,3,'projecting_central_glazed_702_703_front')
for xx in [14.2,29.1]:
 block(xx-.08,xx+.12,22.15,25.12,G+2*H,RF+.1,3,'central_curtainwall_visible_side_return')
 for yy in [22.2,23.65,25.1]:block(xx-.13,xx+.18,yy-.065,yy+.065,G+2*H,RF+.15,2,'glass_return_vertical_grid')
 for zz in [G+2*H+i*H/2 for i in range(11)]:block(xx-.13,xx+.18,22.15,25.15,zz-.065,zz+.065,2,'glass_return_transom')
for x in [14.2+i*1.49 for i in range(11)]:block(x-.065,x+.065,25.05,25.25,G+2*H,RF+.2,2,'central_glass_vertical_grid')
block(14.15,29.15,24.7,25.25,RF-.05,RF+.22,2,'central_glazing_top_frame_cap')
for z in [G+2*H+i*H/2 for i in range(11)]:block(14.15,29.15,25.05,25.25,z-.065,z+.065,2,'central_glass_half_storey_transom')
for lev in range(2,7):
 z=G+lev*H
 block(5.7,14.2,19.75,19.95,z+.45,z+H-.38,3,'recessed_adjacent_glazing')
 for x in [6,8,10,12,14]:block(x-.07,x+.07,19.9,20.1,z+.45,z+H-.38,2,'recessed_glass_mullion')
# Single stair end white half-floor screens anchored to core, with real narrow recessed intervals.
for z in [G+.65+i*H/2 for i in range(14)]:block(29.2,38.7,21.75,22.65,z,z+1.12,2,'single_stair_white_half_level_screen')
block(38.7,39.55,18.9,21.9,G,RF+1.1,3,'narrow_vertical_glass_at_buff_endwall')
block(39.55,42.9,18.9,22.1,G,RF+1.1,1,'tall_buff_endwall_beside_single_stair')
block(14.25,29.05,22.1,22.35,G+H, G+2*H+.05,3,'2F_setback_glazing_above_entry_canopy')
for x in [14.3+i*1.49 for i in range(11)]:block(x-.065,x+.065,22.3,22.45,G+H,G+2*H+.05,2,'2F_glass_grid')
# Opposite end and unphotographed rear: conservative opaque envelope; no invented mirrored curtainwall.
for lev in range(7):
 z=G+lev*H
 for x in [6.2,9.2,12.2,30.2,33.2,36.2]:
  y=(-4.9 if lev==2 else 1.4)
  block(x,x+1.65,y-.18,y+.05,z+.85,z+2.55,3,'rear_sparse_simplified_window_proxy')
# Attached first-floor entrance platform and rounded canopy only; separate bridge span excluded.
block(5.5,29.2,18.4,26.8,.6,G+.2,4,'entry_platform_attached')
for j in range(3):block(7,28,25.8,28.1-j*.4,.6+j*.2,.82+j*.2,2,'entrance_threshold_steps')
canopy=[(5.5,20.5),(29.18,20.5),(29.18,24.5)]+[(26.88+2.3*math.cos(t),24.5+2.3*math.sin(t)) for t in np.linspace(0,math.pi/2,9)]+[(7.8,26.8)]+[(7.8+2.3*math.cos(t),24.5+2.3*math.sin(t)) for t in np.linspace(math.pi/2,math.pi,9)]
poly(canopy,G+H-.65,1.2,2,'rounded_attached_2F_platform_and_thick_fascia_not_B1_tier')
for x in [6.4,28.3]:block(x-.26,x+.26,24.2,24.75,G,G+H,2,'entrance_canopy_pier')
block(5.7,29,18.8,19.05,G+.15,G+H-.35,3,'recessed_entry_glazing')
for x in [7,11,15,19,23,28]:
 beam((x,24.5,G+H+.55),(x,22.2,G+H+1.5),.20,5,'muted_red_small_canopy_rib')
beam((7,24.5,G+H+.55),(28,24.5,G+H+.55),.20,5,'muted_red_attached_canopy_edge')
# Bridge interface is the open top of entrance platform at2F: no fake wall and no arbitrary broken span.
parts=[p.translate((-21.5,-10,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'國立政治大學逸仙樓','scope':'complete main building plus attached entrance; separate學思 bridge excluded at natural platform interface','coordinate_transform':'x=(rotated_plan_pixel_x-150)*0.1; y=(300-rotated_plan_pixel_y)*0.1; model mm=((x-21.5)*3,(y-10)*3,z*3); upper plan side is +Y; photo-left single stair is +X','nominal_scale_mm_per_approx_design_m':SCALE,'floor_levels_mm':[(G+i*H)*SCALE for i in range(7)],'roof_mm':RF*SCALE,'plan_traces_pixels':traces,'raw_plan_traces_pixels':raw_traces,'registration_y_pixel_subtractions':offsets,'limitations':['all metres are proportional approximation, no certified dimensions','rear fenestration simplified not mirrored','solid exterior-study interiors, B1 internal curved stair not modelled','roof access heights approximate','white screen strip gaps are bounded exterior recess proxies backed by solid 705 mass, not a recovered open stair interior','floor edge bands are thickened 0.12 mm outward to preserve true mesh/material boundaries','2006 historical photos and 2026 PDF export do not establish 2026 condition','private technical build only; source rights unresolved'],'supports':'Overhangs and attached canopy require slicer review; no physical print or support-free guarantee.'}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.00005).simplify(.00005)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<1.2,(dist.max(),centers[start:start+500][dist.argmax()].tolist());maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);assert np.all(np.linalg.norm(cr,axis=1)>0),'float32 export degeneracy: repair generator, not QA';nn=cr/np.linalg.norm(cr,axis=1)[:,None]
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
