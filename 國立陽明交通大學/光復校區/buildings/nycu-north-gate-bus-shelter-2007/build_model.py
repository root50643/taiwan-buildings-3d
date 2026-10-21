"""NYCU Guangfu campus 2007 Bamboo Lake / North Gate white steel-and-glass shelter.
Original approximate reconstruction, not a measured survey. Road/front = negative Y.
Dimensions below are display millimetres; manufactured thicknesses are strengthened.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math,struct
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import Polygon,LineString,box as rect
from shapely.geometry.polygon import orient
O=Path(__file__).resolve().parent
for p in ['qa','previews']:(O/p).mkdir(exist_ok=True)
def cross(p):
 loops=[]
 for q in (list(p.geoms) if p.geom_type=='MultiPolygon' else [p]):
  if q.is_empty:continue
  q=orient(q,sign=1);loops.append(np.array(q.exterior.coords[:-1]));loops.extend(np.array(a.coords[:-1]) for a in q.interiors)
 return CrossSection(loops)
def slab(p,z,h):return cross(p).extrude(h).translate((0,0,z))
def xz(p,y,d):return cross(p).extrude(d).transform(np.array([[1,0,0,0],[0,0,1,y],[0,1,0,0]],float))
def yz(p,x,w):return cross(p).extrude(w).transform(np.array([[0,0,1,x],[1,0,0,0],[0,1,0,0]],float))
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def arc(cx,cy,r,a,b,n=24):return [(cx+r*math.cos(t),cy+r*math.sin(t)) for t in np.linspace(math.radians(a),math.radians(b),n+1)]
def strip(points,t):return LineString(points).buffer(t/2,cap_style=2,join_style=1,quad_segs=16)
parts=[];material_for_id={};part_records=[]
palette=[('white_folded_steel_shell','#E9ECEB',255),('cool_white_support_frames','#ADBCC2',255),('transparent_glass_panels','#A6CCD4',46),('recessed_LED_approximation','#677B7D',255),('invented_neutral_print_plinth','#6B7475',255)]
def add(m,col,name):
 assert m.status().name=='NoError' and not m.is_empty(),name
 m=m.as_original();material_for_id[m.original_id()]=col;parts.append(m);part_records.append(dict(name=name,material=col))
add(box(0,-1,0,206,94,3),4,'added_print_plinth_not_real_site_boundary')
# Main continuous asymmetric shell: a suspended lower-left turn and a right
# side that reaches the ground. Rounded profile is extruded through real depth.
profile=[(-56,15),(-70,15)]+arc(-70,28,13,-90,-180)[1:]+[(-83,65)]+arc(-71,65,12,180,90)[1:]+[(71,77)]+arc(71,65,12,90,0)[1:]+[(83,2.7)]
shell=xz(strip(profile,2.6),-10,36)
# As-built front-edge step: the glass-covered middle/right roof band is recessed
# relative to the left shell canopy, not one uniform extruded rounded frame.
shell=shell-box(40,-7.0,0,144,6.1,100)
add(shell,0,'asymmetric_rounded_shell_with_roof_step')
# Left rear sheet and the tall true slot are visible in the source frontal view.
# This sheet is a bounded left bay, NEVER glazing replaced by a white back wall.
leftpanel=Polygon([(-70,15)]+arc(-70,28,13,-90,-180)[1:]+[(-83,65)]+arc(-71,65,12,180,90)[1:]+[(-32,77),(-32,15)])
slot=LineString([(-62,25),(-62,64)]).buffer(5.4,quad_segs=24)
leftpanel=leftpanel.difference(slot)
add(xz(leftpanel,24.8,1.8),0,'left_rear_white_sheet_with_tall_through_slot')
# Left curl turns forward in plan and down into a return, leaving a real
# horizontal aperture beneath it. Its top also overlaps the main shell turn.
curl=[(25,15),(-19,15)]+arc(-19,9.7,5.3,90,270,32)[1:]+[(20,4.4)]
add(yz(strip(curl,2.5),-70,17.5),0,'left_forward_projecting_rolled_seat_with_open_underside')
# Short discreet mounting feet connect the return to the invented display plate.
for y in [-14,19]:add(box(-61,y,2.8,9,2.2,1.2),1,'left_return_mounting_foot')
# The L-shaped long rear seat is not a freestanding symmetric bench.
bench=[(-55,15),(59,15)]+arc(59,10,5,90,0)[1:]+[(64,2.8)]
add(xz(strip(bench,2.5),13,12.5),0,'long_rear_seat_with_right_downturned_end')
# Central downward-and-left return supports the long seat and leaves the void.
support=[(9,15),(9,8.8)]+arc(5.6,8.8,3.4,0,-90)[1:]+[(-55,5.4)]
add(xz(strip(support,1.9),15.0,9.3),0,'central_seat_return_not_filled_pedestal')
# Four narrow independent back frames curve forward above the white roof.
# They share supports with the three rear glazing bays and three roof panes.
axes=[-32,0,32,64]
for i,x in enumerate(axes):
 path=[(27.0,2.8),(27,78.5)]+arc(21,78.5,6,0,90)[1:]+[(-37,84.5)]
 add(yz(strip(path,1.65),x-.9,1.8),1,f'back_frame_and_forward_arm_{i+1}')
 add(box(x,27,2.8,4.2,5,1.4),1,f'back_frame_foot_{i+1}')
 # Joined clamp dots simplified to full small boxes, not floating decorations.
 for z in [21,62]:add(box(x,26.1,z,2.2,2.4,1.5),1,f'rear_glass_clamp_{i+1}')
# Six separate strengthened glazing solids (1.1 mm). Alpha is explicit in 3MF
# and Blender. STL cannot encode transparency: monochrome print = opaque sheets.
for i,(a,b) in enumerate(zip(axes,axes[1:])):
 add(box((a+b)/2,27.1,3.0,b-a-.6,1.1,73.8),2,f'transparent_rear_pane_{i+1}')
 # Canopy sits over the arms. Slight upward tilt toward the front (estimated).
 roof=box((a+b)/2,-5,84.5,b-a-.6,64,1.1).warp(lambda v:(v[0],v[1],v[2]+.025*(27-v[1])))
 add(roof,2,f'transparent_roof_pane_{i+1}')
 # Small attached front rail makes each glass-bay edge unambiguous in STL.
 add(box((a+b)/2,-36.6,86.03,b-a+.5,1.35,1.0),1,f'roof_front_pane_edge_{i+1}')
# Sparse LED seams are shallow attached dark strips, not structural cuts.
# No fabricated signage/text, fake all-white glass, or complete light installation.
for x,y,z,h in [(-83,-10.05,43,25),(83,-4.00,44,27)]:add(box(x,y,z,0.50,.16,h),3,'outer_vertical_LED_seam')
for x,w in [(-58,26),(0,20),(40,18)]:add(box(x,-3.98,77.0,w,.20,.48),3,'roof_edge_LED_seam')
# Combine primitives and retain visible surface material provenance.
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
source=m.to_mesh64();source_colors=np.empty(len(source.tri_verts),dtype=int)
for i,rid in enumerate(source.run_original_id):source_colors[source.run_index[i]//3:source.run_index[i+1]//3]=material_for_id[rid]
source_tm=trimesh.Trimesh(np.asarray(source.vert_properties)[:,:3],np.asarray(source.tri_verts),process=False)
m=m.as_original().set_tolerance(.0001)
me=m.to_mesh64();vs=np.asarray(me.vert_properties)[:,:3];fs=np.asarray(me.tri_verts)
centers=vs[fs].mean(axis=1);colors=np.empty(len(fs),dtype=int);maxdist=0
for start in range(0,len(fs),500):
 closest,dist,idx=trimesh.proximity.closest_point(source_tm,centers[start:start+500]);assert dist.max()<.0002,dist.max();maxdist=max(maxdist,float(dist.max()));colors[start:start+500]=source_colors[idx]
t=trimesh.Trimesh(vs,fs,process=False);assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');raw=(O/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
rec=np.frombuffer(raw,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(rec['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
assert np.array_equal(v[f],np.asarray(t.triangles,dtype=np.float32))
t=trimesh.Trimesh(v,f,process=False)
features=dict(estimated_not_surveyed=True,school='國立陽明交通大學',campus='光復校區',slug='nycu-north-gate-bus-shelter-2007',target_path='國立陽明交通大學/光復校區/buildings/nycu-north-gate-bus-shelter-2007',source_project_year=2007,front_direction='negative Y, road side; rear positive Y, Bamboo Lake',source_glass_height_m=3.2,source_cladding_mm=3,source_dimensions_not_used_as_exact_scale=True,back_frame_count=4,back_frame_x_mm=axes,rear_glass_count=3,roof_glass_count=3,glass_thickness_display_mm=1.1,glass_alpha_0_255=46,shell_thickness_display_mm=2.6,back_frame_cross_section_mm=[1.8,1.65],plinth_dimensions_mm=[206,94,3],left_slot_center_x_mm=-62,left_slot_radius_mm=5.4,left_slot_segment_z_mm=[25,64],left_return_seat_x_mm=[-70,-52.5],left_return_seat_y_mm=[-25.55,25],main_roof_front_edge_y_mm=[-10,-3.95],roof_step_x_mm=-32,central_seat_return_x_mm=9,generator_boolean_tolerance_mm=.0001,material_provenance_nearest_surface_max_distance_mm=maxdist,glass_STL_translation='All six glazing sheets retained geometrically; STL has no color/alpha and will print opaque in opaque filament. Transparent material preview is not physical print proof. 3MF display alpha may not survive every slicer.',plinth_is_added_not_real_site=True,source_appearance='2007 project publication and as-built photography, capture dates unknown; not asserted 2026 condition',uncertain=['overall length depth height and curves inferred from photos/drawings','all display mm dimensions','exact glass slope and panel gaps','left rear panel width and slot proportions','LED locations/lengths simplified','hidden steel and footing details'],omitted=['trees lake slopes roadway and people','precise fasteners and glass brackets','underground anchors','source photos and drawings'],no_actual_print=True,support_free_certified=False,parts=part_records)
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
