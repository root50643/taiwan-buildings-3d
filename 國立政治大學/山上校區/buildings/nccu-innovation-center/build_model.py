"""政大研創總中心 — 官方PDF外觀平面參考版，攝年未知、非已核2026現況。"""
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


SCALE=2.2
palette=[('approximate_slope_base','#8E9486',255),('pale_stone_proxy','#D1D0C3',255),('dark_long_facade_proxy','#555354',255),('opaque_bluegray_glazing','#405762',255),('neutral_roof_coping','#92968F',255),('red_entry_canopy','#BA1731',255),('window_frame_proxy','#A8ADA6',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,c,n):add(cube(x0,x1,y0,y1,z0,z1),c,n)
def poly(ps,z0,z1):
 ps=np.array(ps);area=np.sum(ps[:,0]*np.roll(ps[:,1],-1)-ps[:,1]*np.roll(ps[:,0],-1))
 return CrossSection([ps if area>0 else ps[::-1]]).extrude(z1-z0).translate((0,0,z0))
def wedge(x0,x1,y0,y1,z0,za,zb):
 v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,za],[x1,y0,zb],[x1,y1,zb],[x0,y1,za]],dtype=np.float32)
 f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],dtype=np.uint32)
 return Manifold(Mesh(v,f))
TRACES={'1F': {'outline': [[-33.68438, 19.75504], [31.90996, 18.61059], [31.88564, 15.55131], [40.3492, 15.37544], [40.29273, 8.27355], [39.23479, 8.29553], [39.06105, -13.55645], [3.09091, -12.80902], [3.02576, -21.00351], [-33.98495, -18.0489], [-33.88592, -5.59327], [-48.59136, -5.2877], [-53.95213, -0.80518], [-53.88263, 7.93561], [-33.74606, 11.99758]], 'entry_low': [[3.5775, -4.84184], [39.12446, -5.58048], [39.06105, -13.55645], [3.51409, -12.81781]]}, '2F': {'outline': [[-35.76923, -21.07692], [-35.76923, -1.84615], [-34.23077, -1.84615], [-34.23077, 8.53846], [-0.84615, 8.53846], [-0.84615, 18.76923], [31.84615, 18.76923], [31.84615, 14.53846], [41.46154, 14.53846], [41.46154, 8.53846], [39.53846, 8.53846], [39.53846, -12.23077], [15.84615, -12.23077], [15.84615, -22.46154], [-0.84615, -23.53846]], 'left_void': [[-20.84615, -2.23077], [-0.61538, -2.23077], [-0.61538, -4.84615], [-4.30769, -4.84615], [-4.30769, -9.30769], [-0.61538, -9.30769], [-0.61538, -12.0], [-16.23077, -12.0], [-16.23077, -9.30769], [-20.84615, -9.30769]]}, '3F': {'outline': [[-36.81328, -21.16949], [-36.71922, -1.2745], [-35.19579, -1.29681], [-35.14483, 9.48294], [-0.94385, 8.98211], [-0.89289, 19.76186], [32.16553, 19.27776], [32.14417, 14.75977], [41.89411, 14.61699], [41.87575, 10.73311], [40.65701, 10.75096], [40.54234, -13.50349], [15.55811, -13.13763], [15.50714, -23.91738], [-1.33237, -24.85981]], 'left_void': [[-16.1548, -1.97199], [-0.53966, -2.20066], [-0.55127, -4.65781], [-4.28367, -4.60315], [-4.30691, -9.51745], [-0.5745, -9.57211], [-0.59062, -12.98041], [-16.20577, -12.75175]], 'right_void': [[7.58323, 7.98528], [26.47375, 7.70865], [26.42691, -2.19921], [7.53639, -1.92258]]}, '4F': {'outline': [[-37.03328, -21.11087], [-37.12496, -1.33182], [-35.47495, -1.34827], [-35.52471, 9.38892], [-1.03159, 9.04506], [-1.07836, 19.13641], [31.68617, 18.80978], [31.70638, 14.45032], [41.2136, 14.35554], [41.23118, 10.56119], [40.91689, 10.56433], [41.02653, -13.08979], [6.76913, -12.74828], [-15.86037, -12.36123], [-15.81359, -22.45258]], 'classroom': [[-15.85925, -12.60343], [-6.41863, -15.28081], [-2.87653, -16.68848], [-1.66427, -23.966], [-15.81247, -22.69477]], 'right_void': [[7.61545, 8.07086], [26.15845, 7.88601], [26.20447, -2.04388], [7.66147, -1.85903]], 'low_terrace': [[-15.85925, -12.60343], [15.33385, -12.91439], [15.38362, -23.65158], [-1.66427, -23.966]]}, '5F': {'outline': [[-1.56142, 19.96706], [31.76335, 19.18308], [31.92158, 14.6921], [41.55678, 14.46543], [41.69864, 10.43903], [39.30795, 10.49528], [39.39253, 8.09492], [41.49344, 8.0455], [42.29823, -14.79655], [-0.37196, -13.79271]]}, 'R': {'outline': [[-0.86871, 19.43844], [32.02485, 18.87831], [32.01571, 14.52082], [41.59636, 14.35768], [41.58843, 10.57571], [39.11343, 10.61786], [39.10827, 8.15135], [42.30181, 8.09697], [42.25667, -13.44381], [-0.93608, -12.7083]]}}
# Regularized repeated wall lines use the stable2F outline, NOT per-page raster origins.
# Raw per-floor traces retained here for audit; real occupied-step/classroom/entry changes remain.
RAW_TRACES=json.loads(json.dumps(TRACES))
canonical_high=[[-.84615,-12.23077],[39.53846,-12.23077],[39.53846,8.53846],[41.46154,8.53846],[41.46154,14.53846],[31.84615,14.53846],[31.84615,18.76923],[-.84615,18.76923]]
TRACES['3F']['outline']=TRACES['2F']['outline']
TRACES['4F']['outline']=[[-35.76923,-21.07692],[-35.76923,-1.84615],[-34.23077,-1.84615],[-34.23077,8.53846],[-.84615,8.53846],[-.84615,18.76923],[31.84615,18.76923],[31.84615,14.53846],[41.46154,14.53846],[41.46154,8.53846],[39.53846,8.53846],[39.53846,-12.23077],[-16,-12.23077],[-16,-22.5]]
TRACES['4F']['classroom']=[[-16,-12.23077],[-6.4,-15.28],[-2.87,-16.68],[-1.66,-23.48],[-16,-22.5]]
TRACES['4F']['low_terrace']=[[-16,-12.23077],[15.84615,-12.23077],[15.84615,-22.46154],[-.84615,-23.53846],[-1.66,-23.48]]
TRACES['5F']['outline']=canonical_high;TRACES['R']['outline']=canonical_high
H=4.;LH=H;Z=1.;LOW_ROOF=15.

# Pixel-traced floor silhouettes registered by shared lift and end stairs.
# Exact traces are numerical source interpretations, not source pixels or measured metres.
basepoly=[(-56,-26),(18,-27),(18,-17),(45,-17),(45,22),(-56,22)]
add(poly(basepoly,0,.8),0,'minimal_grade_contact_base_not_full_landscape')
grade=wedge(-27,22,-45,56,0,.75,2.7).rotate((0,0,90)) ^ poly(basepoly,0,4)
add(grade,0,'approximate_sloped_grade_contact_wedge')
highmask=CrossSection([canonical_high]);occupied=[]
for floor in range(1,6):
 name=str(floor)+'F';outline=TRACES[name]['outline'];cs=CrossSection([outline if sum(outline[i][0]*outline[(i+1)%len(outline)][1]-outline[i][1]*outline[(i+1)%len(outline)][0] for i in range(len(outline)))>0 else outline[::-1]])
 high=cs ^ highmask;low=cs-highmask
 if not high.is_empty():occupied.append(high.extrude(H+.03).translate((0,0,Z+(floor-1)*H-.03)))
 if not low.is_empty():occupied.append(low.extrude((LOW_ROOF-(Z+3*H) if floor==4 else H)+.03).translate((0,0,Z+(floor-1)*H-.03)))
add(Manifold.batch_boolean(occupied,OpType.Add),1,'registered_1F_to5F_occupied_body_union_same_pale_material')
# Bounded retaining/skirt contact below2F's traced south projection; no guessed columns.
# Approximate slope-contact solid, not an extra occupied basement floor or whole terrain.
skirt=[[-35.76923,-21.07692],[-.84615,-23.53846],[15.84615,-22.46154],[15.84615,-12.23077],[-35.76923,-12.23077]]
add(poly(skirt,.65,Z+LH+.05),0,'bounded_south_grade_skirt_contact_under_low2F_projection')
# Finite internal halls, not courtyard shafts; retain enclosed negative boundaries.
left2=poly(TRACES['2F']['left_void'],Z+LH+.5,Z+2*LH+.04)
left3=poly(TRACES['3F']['left_void'],Z+2*LH-.04,Z+3*LH-.45)
right3=poly(TRACES['3F']['right_void'],Z+H+.5,Z+3*H+.04)
right4=poly(TRACES['4F']['right_void'],Z+3*H-.04,Z+4*H-.45)
for cutter in [left2,left3,right3,right4]:
 cutter=cutter.as_original();material_for_id[cutter.original_id()]=1;parts=[p-cutter for p in parts]
# Classroom350425 is separate from adjacent low roof: sloping bounded4F volume.
cl=poly(TRACES['4F']['classroom'],Z+3*LH-.05,Z+4*LH)
cl=cl ^ wedge(-16,0,-26,-10,Z+3*LH-.1,LOW_ROOF,Z+3*LH+.7)
add(cl,1,'4F_350425_bounded_stepped_classroom_sloping_roof_proxy')
# Existing3F roof exposed at southeast; no fabricated5F on low wing.
add(poly(TRACES['4F']['low_terrace'],Z+3*LH-.2,Z+3*LH+.12),4,'low_southeast_exposed_3F_roof')
# R upper perimeter follows roof tracing, limited shallow slab not full occupied6F.
add(poly(TRACES['R']['outline'],Z+5*H-.06,Z+5*H+.16),4,'R_traced_high_roof_edge_not6F')
# Roof core positions are the registration anchors; low stair head is lower.
block(-5,-1,-9.5,-4.5,LOW_ROOF-.08,Z+5*H+2.8,1,'shared_lift_core_registered')
block(-34.5,-27.5,-1.2,2.2,LOW_ROOF-.08,LOW_ROOF+1.1,1,'low_end_stair_head_registered')
block(34,41.7,10.5,14.8,Z+5*H-.08,Z+5*H+1.1,1,'high_end_stair_head_registered')
block(-5.16,-.84,-9.66,-4.34,Z+5*H+2.75,Z+5*H+3,4,'shared_lift_core_cap')
block(-5.12,-4.9,-8.8,-5.4,Z+5*H+.8,Z+5*H+1.7,3,'shared_core_louver_proxy')
for x in [8,14,20,26,32]:block(x-.35,x+.35,-2,8,Z+5*H+.12,Z+5*H+.32,4,'R_five_unassigned_neutral_strip_proxy')
# Geometry-aligned facade strips; straight segment extrusion, not nearest-face recoloring.
def wall_segment(a,b,z0,z1,depth,col,name):
 a=np.array(a,float);b=np.array(b,float);d=b-a;n=np.array([d[1],-d[0]])/np.linalg.norm(d)
 add(poly([a-n*.12,b-n*.12,b+n*depth,a+n*depth],z0,z1),col,name)
# Dark long front boundary per each high-storey trace. Proxies only on observed-Y face.
longs={3:((15.84615,-12.23077),(39.53846,-12.23077)),4:((-.84615,-12.23077),(39.53846,-12.23077)),5:((-.84615,-12.23077),(39.53846,-12.23077))}
for floor,(a,b) in longs.items():
 z=Z+(floor-1)*H;a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);a=a+u*.2;b=b-u*.3
 wall_segment(a,b,z+.02,z+H-.08,.12,2,'841_dark_small_window_long_face_only')
 for f in [.08,.2,.32,.46,.59,.72,.86]:
  c=a+(b-a)*f;u=(b-a)/np.linalg.norm(b-a)
  wall_segment(c-u*.62,c+u*.62,z+.9,z+2.25,.25,3,'841_small_square_window_proxy')
  wall_segment(c-u*.75,c+u*.75,z+.78,z+.92,.43,6,'841_projecting_small_sill')
# Photo-observed low-front bay rhythm follows actual trace bowed segments.
for floor in [2,3,4]:
 z=Z+(floor-1)*LH
 segs=[([-35.76923,-21.07692],[-.84615,-23.53846]),([-.84615,-23.53846],[15.84615,-22.46154])] if floor<4 else [([-35.76923,-21.07692],[-16,-22.5])]
 for a,b in segs:
  a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a)
  for f in ([.12,.35,.59,.83] if np.linalg.norm(b-a)>25 else [.2,.55,.85]):
   c=a+(b-a)*f;w=2.2 if floor==4 else 2.8
   wall_segment(c-u*w/2,c+u*w/2,z+.65,z+(1.7 if floor==4 else 2.35),.18,3,'841_low_pale_wing_window_proxy')
   wall_segment(c-u*(w/2+.1),c+u*(w/2+.1),z+.53,z+.68,.36,6,'low_wing_sill')
   wall_segment(c-u*.065,c+u*.065,z+.65,z+(1.7 if floor==4 else 2.35),.24,6,'low_wing_window_mullion')
# Distinct pale banded+X end: actual recessed bays. Window counts are approximated.
ends={floor:((39.53846,-12.23077),(39.53846,8.53846)) for floor in [3,4,5]}
for floor,(a,b) in ends.items():
 z=Z+(floor-1)*H;a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]])
 aa=a+u*.8;bb=b-u*.6;recess=2.0 if floor==5 else 1.2
 cut=poly([aa-n*recess,bb-n*recess,bb+n*.3,aa+n*.3],z+.28,z+H-.55).as_original();material_for_id[cut.original_id()]=1;parts=[p-cut for p in parts]
 wall_segment(aa+u*.08-n*(recess-.02),bb-u*.08-n*(recess-.02),z+.3,z+H-.57,.1,3,'839_recessed_glazing_band')
 wall_segment(a+u*.15,b-u*.15,z+H-.55,z+H+.01,.16,1,'839_pale_horizontal_spandrel')
 for f in np.linspace(.06,.94,7):
  c=a+(b-a)*f-n*(recess-.07)
  wall_segment(c-u*.09,c+u*.09,z+.3,z+H-.57,.3,6,'839_glazing_mullion')
 if floor==5:
  # Source839 top gallery has a rail in front of deeper shadowed glazing.
  wall_segment(a+u*.7-n*.4,b-u*.6-n*.4,z+1.02,z+1.42,.38,6,'839_top_recessed_gallery_handrail_proxy')
  for f in np.linspace(.05,.95,22):
   c=a+(b-a)*f-n*.4
   wall_segment(c-u*.19,c+u*.19,z+.05,z+1.2,.38,6,'839_top_gallery_baluster_proxy')
# Entry-adjacent1F right/lower mass retained from real1F footprint, not arbitrary mirrored box.
# Its exact photographic correspondence remains bounded approximation.
# Ground end glass and red canopy along+X; no semantic claim for plan's small X rectangle.
entrycut=cube(38.75,39.8,-11.8,7.8,Z+.12,Z+2*H-.35).as_original();material_for_id[entrycut.original_id()]=1;parts=[p-entrycut for p in parts]
wall_segment((38.83,-11.7),(38.83,7.7),Z+.15,Z+2*H-.4,.18,3,'839_entry_glass_unresolved_lower_two_level_proxy')
for y in [-11,-7,-3,1,5]:block(38.79,39.12,y-.1,y+.1,Z+.1,Z+2*H-.3,6,'entry_mullion')
block(38.9,42.2,-12.6,7.8,Z+2*H-.18,Z+2*H+.12,5,'839_attached_red_entry_canopy_photo_band_height_proxy')
# Low room next to entrance is restrained below-band attached southern edge, not entire low wing.
# Slight source1F/2F perimeter difference is retained; do not enlarge it into invented major annex.
wall_segment((3.51409,-12.81781),(39.06105,-13.55645),Z+.08,Z+H-.08,.08,1,'1F_right_lower_entry_adjacent_trace_edge')
parts=[p.scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'政大研創總中心 — 官方PDF外觀平面參考版，攝年未知、非已核2026現況','geometry_revision':'v6-common-levels-lower4F-roof-top-gallery-entry','coordinate_transform':'2F shared-lift/stair anchors define common frame; each other floor affine-registered from3 anchors; plan right+X/up+Y not compass;841-Y dark face and839+X pale end bounded candidate','nominal_scale_mm_per_approx_design_m':SCALE,'high_floor_height_approx_design':H,'low_floor_height_approx_design':LH,'ground_Z':Z,'source_trace_coordinates':RAW_TRACES,'regularized_model_coordinates':TRACES,'regularization':'Repeated2/3F and high2–R exterior wall lines share2F stable outline; retain1F whole attached masses,4F425/low-terrace changes,finite cavities,stair projections. All floor datums shareH4; only low4F roof lowered to15.839 top3 window bands and deeper top gallery control facade; canopy/lower2level entrance height remains unmeasured photo proxy, not certified floor assignment.','limits':['Exact heights/windowcounts/materialRGB approximate','Plan illustration affine residual/scale changes not measured as-built','1F whole attached auditorium and right-lower entry mass preserved;839 lowvolume correspondence bounded not unique','B1 hidden parking omitted not full exposed storey','Right2Fhall3/4Fvoid capped5F floor andR; left2/3 finite cavity cap4F','Low4F425 stepped classroom retained next to lower3F roof;5Fleftblank no fullnewfloor','Roof five strips unassigned function not PV/skylights','Slope minimal approximate contact only','No source pixels/source rights unresolved/private/no broad license','No print test/support-free guarantee']}
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
# Keep Boolean original-run provenance through simplification: no nearest-surface repaint.
m=m.set_tolerance(.00001).simplify(.00001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
colors=np.empty(len(fs),dtype=int)
for i,rid in enumerate(me.run_original_id):colors[me.run_index[i]//3:me.run_index[i+1]//3]=material_for_id[rid]
maxdist=0.0
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Export exact float32 triangles with analytically normalized normals; no small-face threshold.
tri=np.asarray(t.triangles,dtype=np.float32);cr=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);print('DEGENERATES',tri[np.linalg.norm(cr,axis=1)==0].tolist());assert np.all(np.linalg.norm(cr,axis=1)>0),'float32 export degeneracy: repair generator, not QA';nn=cr/np.linalg.norm(cr,axis=1)[:,None]
buf=bytearray(80)+struct.pack('<I',len(tri))
for nor,face in zip(nn,tri):buf+=struct.pack('<12fH',*nor,*face.ravel(),0)
(O/'model.stl').write_bytes(buf);raw=bytes(buf);n=len(tri)
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=FEATURES
features.update(material_provenance='Manifold Boolean original run ids retained through simplification; no nearest transfer',parts=part_records)
(O/'qa/design-features.json').write_text(json.dumps(features,ensure_ascii=False,indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b,'alpha':c} for a,b,c in palette]},indent=2)+'\n')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});el(r,'metadata',{'name':'Title'}).text='政大研創總中心 — 官方PDF外觀平面參考版，攝年未知、非已核2026現況';res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b,c in palette:el(bm,'base',{'name':a,'displaycolor':b+f'{c:02X}'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0,'name':'政大研創總中心 — 官方PDF外觀平面參考版，攝年未知、非已核2026現況'});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
