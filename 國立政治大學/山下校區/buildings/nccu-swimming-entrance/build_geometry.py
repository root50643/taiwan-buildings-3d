#!/usr/bin/env python3
"""Original bounded NCCU service-wing model. No source pixels are required.
Run with numpy, trimesh and manifold3d. Values are model millimetres, not a survey.
The actual two-storey frontage, narrow plan strip and two locally enclosed stair
positions are approximated; pool hall, interior and unregistered ramp omitted.
"""
from pathlib import Path
import argparse, json, hashlib, zipfile, xml.etree.ElementTree as ET
import numpy as np
import trimesh
from manifold3d import Manifold, OpType

def build(param_path,out):
 p=json.loads(param_path.read_text());out.mkdir(parents=True,exist_ok=True)
 L,D,H,B=p['length'],p['depth'],p['wall_height'],p['base_thickness'];front=-D/2;rear=D/2
 parts=[];cutters=[];operations=[];after_cut=[]
 def box(name,x0,x1,y0,y1,z0,z1,negative=False):
  assert x1>x0 and y1>y0 and z1>z0,(name,x0,x1,y0,y1,z0,z1)
  m=Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0));(cutters if negative else parts).append(m)
  operations.append({'name':name,'operation':'difference' if negative else 'union','bounds_mm':[[x0,y0,z0],[x1,y1,z1]]})
 box('neutral_print_base',-L/2-p['base_margin_x'],L/2+p['base_margin_x'],front-p['base_front_margin'],rear+p['base_rear_margin'],0,B)
 box('closed_service_wing_no_interior',-L/2,L/2,front,rear,B-.1,B+H)
 # Two first-storey stair enclosures follow plan positions. No invented exposed
 # flights, railings or corresponding upper-storey glazing/roof additions.
 for i,s in enumerate(p['stair_enclosures']):
  box('schematic_local_stair_enclosure_'+str(i+1),s['x0'],s['x1'],front-s['projection'],front+.2,B-.1,B+s['height'])
 # Source-visible central entrance: shallow solid-backed recess and canopy.
 a,b=p['entry_x_min'],p['entry_x_max'];zfloor=B+p['plinth_height'];ztop=zfloor+p['entry_height']
 box('central_entry_shallow_recess',a,b,front-.05,front+p['recess_depth'],zfloor,ztop,True)
 box('central_entry_canopy',a-1,b+1,front-p['canopy_projection'],front+.2,ztop,ztop+p['canopy_thickness'])
 # Solid-backed doors, kept shallow for printing. Two integral slim divisions.
 for x in [a+(b-a)/3,a+2*(b-a)/3]:
  after_cut.append(Manifold.cube((.9,p['recess_depth']+.2,ztop+.05-zfloor)).translate((x-.45,front-.1,zfloor)))
  operations.append({'name':'entry_vertical_divider','operation':'union_after_difference','bounds_mm':[[x-.45,front-.1,zfloor],[x+.45,front+p['recess_depth']+.1,ztop+.05]]})
 # Broad entry steps only; not the two service-strip inter-storey stairs.
 # Accessibility ramp is deliberately unresolved/omitted, not replaced by steps.
 n=p['entry_steps'];t=p['entry_step_tread'];ph=p['plinth_height']
 for i in range(n):
  box('front_entry_step_'+str(i+1),a-1,b+1,front-(n-i)*t,front+.15,B-.1,B+ph*(i+1)/n)
 # Long upper horizontal glass band with robust, integral vertical frames.
 margin=2.1;start=-L/2+margin;stop=L/2-margin;nb=16;pitch=(stop-start)/nb;frame=p['frame_width'];dep=p['recess_depth']
 openings=[]
 for i in range(nb):
  x0=start+i*pitch+frame/2;x1=start+(i+1)*pitch-frame/2
  z0=B+p['upper_window_bottom'];z1=B+p['upper_window_top']
  box('upper_glazing_recess_%02d'%i,x0,x1,front-.05,front+dep,z0,z1,True);openings.append([x0,x1,z0,z1])
 # Dark louver-looking band, represented by two robust shallow horizontal slots.
 # It is not a resolved count of real blades.
 for k,(lo,hi) in enumerate([(p['louver_bottom'],p['louver_bottom']+.8),(p['louver_top']-.8,p['louver_top'])]):
  box('schematic_louver_slot_'+str(k),start,stop,front-.05,front+.45,B+lo,B+hi,True)
 # Lower ventilation openings: sparse clusters seen on the photo. Exact bay
 # count/positions are simplified; not a measured reconstruction.
 for i,(x0,x1) in enumerate([(-97,-79),(-77,-58),(-23,-14),(15,23),(57,75),(77,96)]):
  box('lower_vent_recess_'+str(i),x0,x1,front-.05,front+.5,B+11.2,B+13.6,True)
 solid=Manifold.batch_boolean(parts,OpType.Add)
 solid=Manifold.batch_boolean([solid]+cutters,OpType.Subtract)
 solid=Manifold.batch_boolean([solid]+after_cut,OpType.Add)
 assert str(solid.status()).endswith('NoError'),str(solid.status())
 m=solid.to_mesh();V0=np.array(m.vert_properties[:,:3],dtype=float);F0=np.array(m.tri_verts,dtype=int)
 # Deterministic conforming splits at color boundaries, with vertex coordinates
 # rounded to 0.00001 mm (far below inference or fabrication precision).
 cuts=sorted(set([B,B+p['plinth_height'],B+11.2,B+13.6,B+p['lower_floor_top'],B+p['upper_window_bottom'],B+p['upper_window_top'],B+p['louver_bottom'],B+p['louver_top'],B+H,ztop,ztop+p['canopy_thickness']]))
 def clip(poly,z,positive):
  result=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=(a[2]>=z) if positive else (a[2]<=z);ib=(b[2]>=z) if positive else (b[2]<=z)
   if ia:result.append(a)
   if ia!=ib:
    q=a+(b-a)*((z-a[2])/(b[2]-a[2]));q[2]=z;result.append(q)
  clean=[]
  for q in result:
   if not clean or np.linalg.norm(q-clean[-1])>1e-7:clean.append(q)
  if len(clean)>1 and np.linalg.norm(clean[0]-clean[-1])<1e-7:clean.pop()
  return clean
 verts=[];faces=[];vmap={}
 def vid(q):
  key=tuple(np.round(q,5))
  if key not in vmap:vmap[key]=len(verts);verts.append(key)
  return vmap[key]
 for tri in V0[F0]:
  pieces=[list(tri)]
  for z in cuts:
   if tri[:,2].min()+1e-5<z<tri[:,2].max()-1e-5:
    nxt=[]
    for poly in pieces:
     if min(q[2] for q in poly)+1e-5<z<max(q[2] for q in poly)-1e-5:nxt.extend([clip(poly,z,False),clip(poly,z,True)])
     else:nxt.append(poly)
    pieces=nxt
  for poly in pieces:
   if len(poly)<3:continue
   ts=[poly] if len(poly)==3 else [[np.mean(poly,axis=0),a,b] for a,b in zip(poly,poly[1:]+poly[:1])]
   for t in ts:
    f=[vid(q) for q in t]
    if len(set(f))==3 and np.linalg.norm(np.cross(np.array(verts[f[1]])-verts[f[0]],np.array(verts[f[2]])-verts[f[0]]))>1e-8:faces.append(f)
 V=np.array(verts);F=np.array(faces);mesh=trimesh.Trimesh(V,F,process=False)
 # Color only defensibly visible regions; cap/back and unknown left end neutral.
 def material(tri,n):
  x,y,z=tri.mean(axis=0);relz=z-B
  if z<B+1e-5:return 6,'display_base_not_architecture'
  if n[1]>.99 and abs(y-rear)<1e-4:return 0,'explicit_pool_hall_cut_not_real_facade'
  if n[2]>.99 and relz>p['lower_floor_top']-.01:return 0,'unknown_top_simplified_closure'
  if n[0]<-.99 and abs(x+L/2)<1e-4:return 0,'unobserved_short_end'
  # Main entrance-facing and observed right short-end surfaces only.
  if (n[1]<-.99 or (n[0]>.99 and abs(x-L/2)<1e-4)) and relz<=p['plinth_height']+.001:return 2,'photo700_dark_plinth_family'
  if n[1]<-.99 and abs(y-(front+dep))<1e-4 and B+p['upper_window_bottom']<z<B+p['upper_window_top']:return 3,'photo700_upper_glazing_simplified_16_bays'
  if n[1]<-.99 and abs(y-(front+dep))<1e-4 and a<x<b and zfloor<z<ztop:return 3,'photo700_central_entry_solid_backing'
  if n[1]<-.99 and abs(y-(front+.45))<1e-4:return 4,'photo700_dark_upper_louver_band_schematic'
  if n[1]<-.99 and abs(y-(front+.5))<1e-4:return 4,'photo700_lower_vent_band_schematic'
  if n[1]<-.99 and abs(y-front)<1e-4 and p['upper_window_bottom']<relz<p['upper_window_top']:return 5,'photo700_upper_window_frames_schematic'
  if n[1]<-.99 and p['louver_bottom']-.01<relz<p['louver_top']+.01:return 4,'photo700_louver_band_schematic'
  if y<front-.01:
   if a-1.01<x<b+1.01 and z<=zfloor+.001:return 5,'photo700_entry_steps_simplified'
   if a-1.01<x<b+1.01 and z>=ztop-.001:return 1,'photo700_entry_canopy_simplified'
   if n[1]<-.99:return 1,'plan_stair_enclosure_with_frontage_color_inferred'
   return 0,'unresolved_stair_enclosure_return_or_cap'
  if n[0]>.99 and abs(x-L/2)<1e-4:return 1,'photo700_visible_short_end_tan_family'
  if n[1]<-.99:return 1,'photo700_frontage_tan_family'
  return 0,'unobserved_or_recess_reveal_neutral'
 mats=[];labels=[]
 for t,n in zip(mesh.triangles,mesh.face_normals):
  a1,b1=material(t,n);mats.append(a1);labels.append(b1)
 data={'schema':'original-solid-mesh-v1','units':'millimeter','vertices':V.tolist(),'faces':F.tolist(),'material_indices':mats,'palette':p['palette'],'material_evidence_labels':labels}
 (out/'mesh.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 mesh.export(out/'model.stl');(out/'construction.json').write_text(json.dumps({'operations':operations,'notes':p['unknowns'],'source_pixels_embedded':False},ensure_ascii=False,indent=2)+'\n')
 # 3MF Core base materials, per-triangle assignments, default property present.
 NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
 def sub(e,n,**attrs):return ET.SubElement(e,'{'+NS+'}'+n,{k:str(v) for k,v in attrs.items()})
 model=ET.Element('{'+NS+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'});sub(model,'metadata',name='Title').text=p['title_zh'];sub(model,'metadata',name='Description').text=p['scope']+' Photo capture date unknown. Approximate geometry; no compass bearings.'
 res=sub(model,'resources');bm=sub(res,'basematerials',id=1)
 for c in p['palette']:sub(bm,'base',name=c['name'],displaycolor=c['hex']+'FF')
 obj=sub(res,'object',id=2,type='model',pid=1,pindex=0,name='NCCU entrance service-wing segment');me=sub(obj,'mesh');vs=sub(me,'vertices');fs=sub(me,'triangles')
 for v in V:sub(vs,'vertex',x=format(v[0],'.8f'),y=format(v[1],'.8f'),z=format(v[2],'.8f'))
 for f,mat in zip(F,mats):sub(fs,'triangle',v1=f[0],v2=f[1],v3=f[2],pid=1,p1=mat)
 sub(sub(model,'build'),'item',objectid=2)
 blobs={'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>',
 '_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
 '3D/3dmodel.model':ET.tostring(model,encoding='utf-8',xml_declaration=True)}
 with zipfile.ZipFile(out/'model.3mf','w',zipfile.ZIP_DEFLATED,compresslevel=9) as zz:
  for name,blob in blobs.items():
   info=zipfile.ZipInfo(name,date_time=(2026,10,24,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;zz.writestr(info,blob)
 qa={'vertices':len(V),'triangles':len(F),'bounds_mm':mesh.bounds.tolist(),'extents_mm':mesh.extents.tolist(),'volume_mm3':float(mesh.volume),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'shells':len(mesh.split(only_watertight=False)),'euler_number':int(mesh.euler_number),'degenerate_triangles_below_1e-8_mm2':int(sum(mesh.area_faces<1e-8)),'min_triangle_area_mm2':float(mesh.area_faces.min()),'non_two_face_edges':int(sum(np.bincount(mesh.edges_unique_inverse)!=2)),'material_face_counts':{p['palette'][i]['name']:mats.count(i) for i in range(len(p['palette']))},'evidence_label_counts':{s:labels.count(s) for s in sorted(set(labels))},'source_pixels_embedded':False,'rounding_mm':0.00001}
 (out/'geometry-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 assert qa['watertight'] and qa['winding_consistent'] and qa['shells']==1 and qa['degenerate_triangles_below_1e-8_mm2']==0 and qa['non_two_face_edges']==0,qa
 print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--parameters',type=Path,default=Path(__file__).with_name('parameters.json'));ap.add_argument('--output',type=Path,default=Path(__file__).parent);args=ap.parse_args();build(args.parameters,args.output)
