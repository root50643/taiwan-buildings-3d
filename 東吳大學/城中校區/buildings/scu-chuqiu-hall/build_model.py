"""Soochow Chu-Chiu Hall / 東吳鑄秋大樓. Archival as-built exterior with 2025 author-photo crosscheck."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
parts=[];material_for_id={};part_records=[]
palette=[] # Assigned below from SCU source observations.
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

# Metres from labelled plan chains (not scan DPI). X east; Y north.
# Main axis 6363.5 cm, east wing 1590 cm; main depth 1760 cm;
# wing depth 3030 cm. Seventh floor wraps outward slightly.
SCALE=3.0; G=1.6; L=63.635; E=79.535; D=17.6
FLOORS=[G,G+3.45,G+6.68,G+9.91,G+13.14,G+16.37,G+19.6];RF=G+22.9
palette=[('neutral_display_base','#89908B',255),('warm_gray_exposed_concrete','#AEA69A',255),('ochre_brick_fields','#B77F51',255),('pale_window_frames','#CEC8B4',255),('opaque_muted_glazing','#657671',255),('roof_weathered_gray','#96978B',255)]
def cube(x0,x1,y0,y1,z0,z1):return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def block(x0,x1,y0,y1,z0,z1,col,name):add(cube(x0,x1,y0,y1,z0,z1),col,name)
def poly(points,z,h,col,name):add(CrossSection([points]).extrude(h).translate((0,0,z)),col,name)
# Narrow removable conceptual display slab, no adjacent campus buildings.
block(-2,E+4,-11,23,0,.7,0,'display_plinth_not_surveyed_terrain')
outline=[(0,0),(L,0),(L,-8.9),(E,-8.9),(E,21.4),(L,21.4),(L,D),(0,D)]
# Enclosed interiors are intentionally solid exterior-study masses, not inferred hollow rooms.
body=CrossSection([outline]).extrude(FLOORS[6]-.7).translate((0,0,.7))
# East entrance is genuinely recessed; open under canopy, not black painted air.
body-=cube(E-1.25,E+.1,3.7,10.8,G,G+7.0)
# North main entrance modest recess, three double-door arrangement.
body-=cube(44.3,53.4,D-.9,D+.1,G,G+3.35)
# South small entrance at central stair bay.
body-=cube(17.4,22.9,-.1,.7,G,G+3.2)
# East 3F-5F wall is set back behind the 6F projecting band and tall portal frame.
body-=cube(E-1.3,E+.1,-2.7,16.7,FLOORS[2],FLOORS[5])
body-=cube(-.1,.65,9.05,11.25,G,G+2.9)
add(body,1,'six_floor_T_body_with_three_entry_recesses')
upper=[(0,-.55),(L-.45,-.55),(L-.45,-9.35),(E+.45,-9.35),(E+.45,21.85),(L-.45,21.85),(L-.45,D+.55),(0,D+.55)]
poly(upper,FLOORS[6],RF-FLOORS[6],1,'seventh_floor_slight_outward_wrap_not_setback')
poly(upper,RF,.28,5,'flat_T_roof')
for a,b in zip(upper,upper[1:]+upper[:1]):beam((*a,RF+.42),(*b,RF+.42),.38,1,'low_continuous_roof_parapet')
# RF drawing has three DIFFERENT protrusion groups. South-oriented main circulation cores.
block(.3,3.845,.4,6.8,RF-.1,RF+2.75,1,'west_stair_roof_protrusion_H275')
# Central乙: high lift room 937 x 715 cm; right low stair 349 cm wide,
# complete combined envelope 1286 x 944 cm, not concentric nested boxes.
block(23.8,33.17,2.6,9.75,RF-.1,RF+4.35,1,'central_937x715_lift_machine_H435')
block(33.13,36.66,.31,9.75,RF-.1,RF+2.75,1,'central_east_low_349_stair_H275')
# East甲: high L-shaped 613 x 720 cm (south part 489 cm wide),
# separate northern low stair 343 cm long. Total north-south envelope1063cm.
eastcore=CrossSection([[(64.14,2.7),(69.03,2.7),(69.03,9.9),(62.9,9.9),(62.9,7.2),(64.14,7.2)]]).extrude(4.45).translate((0,0,RF-.1))
eastcore+=cube(62.9,69.03,9.86,13.33,RF-.1,RF+2.75)
add(eastcore,1,'east_L_613x720_machine_H435_plus_north_343_stair_H275')
for x in [4.0,48.0]:block(x,x+9.8,10.0,11.6,RF+.2,RF+1.69,1,'north_low_long_roof_water_tank_H149')
# Omit fine lightning rods and small cooling equipment, do not model protection triangles.
# Recessed ochre brick bay fields. The long concrete ribs read continuous to 6F.
def panel_y(a,b,y,side,name):
 z0=G;zt=FLOORS[6]-.18;ch=.36
 pts=[(a,z0),(b,z0),(b,zt-ch),(b-ch,zt),(a+ch,zt),(a,zt-ch)]
 # Extruded X/Z polygon mapped into facade Y thickness; outward orientation irrelevant to manifold transform.
 m=CrossSection([pts]).extrude(.28).transform([[1,0,0,0],[0,0,side,y-.04*side],[0,1,0,0]])
 if y==D:m-=cube(44.3,53.4,D-.1,D+.5,G,G+3.35)
 if y==0:m-=cube(17.4,22.9,-.5,.1,G,G+3.2)
 add(m,2,name)
def window_y(x,y,z,w,h,side,name):
 # Opaque closed glass proxy, not an asserted open aperture.
 ya,yb=sorted([y-.035*side,y+.25*side]);block(x-w/2,x+w/2,ya,yb,z,z+h,3,name+'_frame')
 ya,yb=sorted([y+.20*side,y+.31*side]);block(x-w/2+.14,x+w/2-.14,ya,yb,z+.14,z+h-.14,4,name+'_glass')
 for xx in ([x] if w<1.2 else [x-w/6,x+w/6]):
  ya,yb=sorted([y+.20*side,y+.34*side]);block(xx-.075,xx+.075,ya,yb,z+.1,z+h-.1,3,name+'_mullion')
 ya,yb=sorted([y+.20*side,y+.34*side]);block(x-w/2+.1,x+w/2-.1,ya,yb,z+h*.45-.065,z+h*.45+.065,3,name+'_transom')
# Main bay chain: 331.5 + 17 x 324 cm with end/structural margins.
bays=[1.65]+[4.95+3.24*j for j in range(18)]
for side,y in [(-1,0),(1,D)]:
 for j,x in enumerate(bays):
  a=x-1.42;b=min(x+1.42,L-.3)
  if b<=a:continue
  panel_y(a,b,y,side,'south_brick_field' if side<0 else 'north_brick_field')
  narrow=(j in [0,7,8,9,17,18]) if side<0 else (j<=4)
  for lev,z in enumerate(FLOORS[:6]):
   if (side>0 and lev==0 and 44<x<54) or(side<0 and lev==0 and 17<x<23):continue
   if narrow:
    for dx in [-.62,.62]:window_y(x+dx,y+.12*side,z+1.05,.66,1.95,side,'narrow_classroom_or_service_window')
   else:window_y(x,y+.12*side,z+1.12,2.55,1.7,side,'broad_classroom_window')
 # Seventh floor repeated slender windows, independent of lower bay width.
 for x in np.arange(1,L-.5,1.08):window_y(x,y+side*.55,FLOORS[6]+.7,.48,2.15,side,'7F_long_side_narrow_band')
# Exposed south/north cross-wing faces: five narrow-window bays.
for side,y in [(-1,-8.9),(1,21.4)]:
 for x in np.linspace(L+1.55,E-1.55,5):
  panel_y(x-1.36,x+1.36,y,side,'wing_end_ochre_brick_bay')
  for z in FLOORS[:6]:
   for dx in [-.6,.6]:window_y(x+dx,y+.12*side,z+1.05,.65,1.95,side,'wing_narrow_window')
 for x in np.arange(L+.6,E-.3,1.08):window_y(x,y+side*.45,FLOORS[6]+.7,.48,2.15,side,'7F_wing_narrow_band')
# Concrete vertical frame ribs stand proud of the brick fields, as in completed photos.
for side,y in [(-1,0),(1,D)]:
 for x in [0]+[q+1.61 for q in bays]+[L]:
  if x>L:continue
  ya,yb=sorted([y-.06*side,y+.50*side]);block(x-.20,x+.20,ya,yb,.65,FLOORS[6]-.1,1,'long_facade_projecting_concrete_rib')
for side,y in [(-1,-8.9),(1,21.4)]:
 for x in np.linspace(L,E,6):
  ya,yb=sorted([y-.06*side,y+.50*side]);block(x-.20,x+.20,ya,yb,.65,FLOORS[6]-.1,1,'crosswing_projecting_concrete_rib')
# X-facing end wall helper swaps x/y without changing the geometry proof.
def window_x(y,x,z,w,h,side,name):
 start=len(parts);window_y(y,x,z,w,h,side,name)
 for k in range(start,len(parts)):
  old=parts[k];c=material_for_id[old.original_id()];parts[k]=old.transform([[0,1,0,0],[1,0,0,0],[0,0,1,0]]).as_original();material_for_id[parts[k].original_id()]=c
# East lower facade with genuine 3F-5F recess. 6F is an outward full narrow-window band.
eastbrick=cube(E-.05,E+.22,-8.55,21.05,G,FLOORS[6]-.2)
eastbrick-=cube(E-2,E+.5,3.7,10.8,G,G+7)
eastbrick-=cube(E-2,E+.5,-2.7,16.7,FLOORS[2],FLOORS[5])
add(eastbrick,2,'east_short_end_brick_field_cut_back_at_3F_to_5F')
block(E-1.35,E-1.08,-2.7,16.7,FLOORS[2]-.04,FLOORS[5]+.04,2,'east_recessed_3F_5F_brick_wall')
# First/second floor flanking fields are populated, not blank on either side of the entry.
for y in [-7.5,-5.9,-4.3,-2.7,-1.1,.5,2.1,12.8,14.4,16,17.6,19.2,20.5]:
 for z in FLOORS[:2]:window_x(y,E+.12,z+1.05,.68,1.95,1,'east_1F_2F_flanking_narrow_window')
for z in FLOORS[2:5]:
 for y in [-7.5,-5.9,-4.3,17.7,19.2,20.5]:window_x(y,E+.12,z+1.05,.68,1.95,1,'east_3F_5F_outer_narrow_window')
 for y in [-.2,7.25,14.5]:window_x(y,E-1.18,z+1.1,4.1,1.75,1,'east_3F_5F_recessed_broad_window')
for y in [-7.5,-5.9,-4.3,-2.7,-1.1,.5,2.1,4.4,5.9,7.4,8.9,10.1,12.8,14.4,16,17.6,19.2,20.5]:
 window_x(y,E+.12,FLOORS[5]+1.05,.68,1.95,1,'east_6F_projecting_narrow_window_band')
block(E-1.35,E+.66,-2.9,16.9,FLOORS[5]-.30,FLOORS[5]+.12,1,'east_6F_projecting_soffit_beam')
for y in [-1.8,1.3,4.5,7.7,10.9,14.1,16.2]:
 block(E-1.35,E+.65,y-.12,y+.12,FLOORS[5]-.65,FLOORS[5]-.2,1,'east_6F_visible_underside_rib')
for y in np.arange(-8.2,21,1.08):window_x(y,E+.45,FLOORS[6]+.7,.48,2.15,1,'east_7F_narrow_band')
for y in [3.55,10.95]:block(E-.1,E+.65,y-.3,y+.3,G,FLOORS[6]-.25,1,'east_tall_portal_pier')
# Present east canopy at approximately second-floor head, attached to piers and back wall.
block(E-1.3,E+2.5,3.25,11.25,G+6.8,G+7.35,1,'east_projecting_entry_canopy')
for y in [4.2,6.5,8.8,10.4]:block(E-1.3,E+2.5,y-.12,y+.12,G+6.45,G+6.9,1,'east_canopy_underside_rib')
block(E-1.27,E-1.02,4.0,10.5,G,G+6.4,4,'recessed_east_entry_glass_and_glassblock_proxy')
for y in np.arange(4.2,10.4,.7):block(E-1.02,E-.84,y-.065,y+.065,G+3.2,G+6.4,3,'east_glassblock_vertical_grid')
for z in np.arange(G+3.2,G+6.4,.65):block(E-1.02,E-.84,4,10.5,z-.065,z+.065,3,'east_glassblock_horizontal_grid')
block(E-1.02,E-.7,7.1,7.35,G,G+6.4,1,'east_entry_center_mullion')
for j in range(4):block(E-.2,E+2.6-j*.48,3.4,11.1,.7+j*.225,.945+j*.225,1,'east_entry_threshold_step')
# West end asymmetric elevation: one narrow north/left brick bay, four-window
# south/right brick bay, broad shallow-gray centre, and a real bottom centre door.
def west_brick(a,b):
 z0=G;zt=FLOORS[6]-.18;ch=.3
 pts=[(a,z0),(b,z0),(b,zt-ch),(b-ch,zt),(a+ch,zt),(a,zt-ch)]
 add(CrossSection([pts]).extrude(.28).transform([[0,0,-1,.04],[1,0,0,0],[0,1,0,0]]),2,'west_asymmetric_brick_side_bay')
west_brick(.25,4.8);west_brick(15.15,17.3)
for y in [.75,1.85,2.95,4.05,16.2]:
 for z in FLOORS[:6]:window_x(y,-.12,z+1.05,.65,1.9,-1,'west_brick_side_narrow_window')
for y in [.1,4.95,15.0,17.5]:block(-.5,.05,y-.18,y+.18,.65,FLOORS[6]-.1,1,'west_side_bay_concrete_rib')
for lev,z in enumerate(FLOORS):
 for y in [7.8,10.0,10.8,13.3]:
  if lev==0 and 9<y<12:continue
  window_x(y,0,z+1.1,.65,1.8,-1,'west_gray_center_sparse_narrow_window')
for y in [.65,1.7,2.75,3.8,4.6,15.7,16.8]:window_x(y,0,FLOORS[6]+.7,.48,2.15,-1,'west_7F_asymmetric_side_band')
window_x(10.15,.65,G+.05,1.9,2.65,-1,'west_recessed_bottom_door')
for y in [8.95,11.35]:block(-.35,.72,y-.14,y+.14,G,G+3.05,1,'west_door_jamb')
block(-.35,.72,8.8,11.5,G+2.85,G+3.1,1,'west_door_lintel')
for j in range(4):block(-1.6+j*.3,.75,8.7,11.6,.7+j*.225,.945+j*.225,1,'west_small_door_platform_steps')
# Recessed north entry / three double doors, with threshold and supporting piers.
for x in [45.8,48.85,51.9]:window_y(x,D-.9,G+.1,2.5,2.85,1,'north_three_double_door_entry')
for x in [44.25,47.3,50.35,53.4]:block(x-.22,x+.22,D-.2,D+.5,G,G+3.55,1,'north_entry_pier')
block(44,53.7,D-.95,D+1.1,G+3.25,G+3.65,1,'north_entry_lintel_canopy')
for j in range(4):block(44,53.7,D-.1,D+2.3-j*.42,.7+j*.225,.945+j*.225,1,'north_entry_step')
# South modest entrance visible in archival elevation; not a large new canopy.
for x in [18.5,21.5]:window_y(x,.7,G+.1,2.1,2.65,-1,'south_recessed_door')
for j in range(4):block(17.2,23.1,-1.7+j*.32,.8,.7+j*.225,.945+j*.225,1,'south_threshold_step')
parts=[p.translate((-E/2,-6,0)).scale((SCALE,SCALE,SCALE)) for p in parts]
FEATURES={'identity':'東吳大學城中校區鑄秋大樓（第二大樓）','campus':'城中校區','scope':'Complete T-shaped seven-storey exterior, four distinct facades, flat roof, three roof stair/machine groups and two low elongated water tanks; attached entrance canopies/piers/steps. No neighboring clock tower.','basis':'Museum archival as-built drawings; 1979 design date; author reports 1981 completion and 2025-01-14 exterior photos. Not a 2026 survey.','nominal_scale_mm_per_design_m':SCALE,'coordinate_transform':'x=(east_m-39.7675)*3; y=(north_m-6)*3; z=metres*3','ground_level_mm':G*SCALE,'floor_levels_mm':[v*SCALE for v in FLOORS],'roof_mm':RF*SCALE,'thin_details':{'frame_mullion_mm':.15*SCALE,'roof_parapet_mm':.38*SCALE,'canopy_vertical_mm':.55*SCALE},'supports':'Entry canopy overhangs and recessed lintels require slicer-specific support review. Interiors solidified for exterior study; no physical print or slicer claim.','omissions':['fine lightning rods and protection diagram lines','small rooftop cooling equipment','internal rooms/basement volume below display ground','adjacent clock tower and campus structures'],'dimension_reading':'Main chain 6363.5 cm + wing 1590 cm; 324 cm repeating bays; main depth 1760 cm and wing 3030 cm. Slight 7F offsets and facade small details approximate.'}
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
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split(only_watertight=False,repair=False)),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256(raw).hexdigest()}))
