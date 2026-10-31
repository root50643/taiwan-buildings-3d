#!/usr/bin/env python3
"""TNFSH comprehensive gym: 2012 completed, 2013 architect-supplied publication exterior.
Main geometry uses dimensioned elevations. Details simplified, not as-built survey.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent;SCALE=1000/250
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('concrete','Exposed concrete','#A4A5A4','Architect supplied completion photos; illustrative hue'),
('glass','Opaque blue-grey glazing backing','#426A75','Observed glazing represented opaque for printing, no interior claim'),
('metal','Aluminium mullions and louvres','#777E80','Completion photographs and elevation annotations'),
('roof','Simplified roof surface','#A0A2A0','Sections show shallow roof below perimeter; unobserved equipment omitted'),
('base','Authored support','#BDB9AD','Flat support is authored; no surveyed ground')]]
P={'building':'國立臺南第一高級中學 綜合體育館','state':'2012 completed / 2013 architect-supplied publication exterior','scale_denominator':250,'width_m':57,'depth_m':41,'parapet_height_m':21,'floor_levels_m':[0,5,9,13,17,20.4],'axis_grid_m':4,'coordinate_system':'x east, y north, z up; local aligned axes, not georeferenced','dimension_policy':'Four elevations give overall5700/4100cm, repeated400cm bays, floor +500/+900/+1300/+1700/+2040 and parapet about21m. Details proportionally interpreted. Not construction-ready or as-built survey.','scope':'Whole above-ground gym exterior including north semi-outdoor court, south recessed entry, west/east entry gaps. No surrounding connected building or underground parking reconstruction.','limitations':['Opaque window backing; no hidden room reconstruction','Representative louvre spacing and frame depths; concrete formwork tie pattern omitted rather than invented exact count','Roof section form simplified; no undocumented rooftop plant, lightning-protection diagram rays or 9m rod reconstructed','Flat authored support, site slope and basement ramp omitted explicitly; isolated above-ground building model']}
(ROOT/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2));items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(n,s,mat=0,e='Architect-supplied 2013 drawings, cross-checked completion photographs'):
 s=s.translate([0,0,.55]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':n,'material':mat,'evidence':e})
def bx(n,a,b,mat=0,e='Dimensioned drawings with proportional detail'):add(n,box(a,b),mat,e)
def xz(pts,y,d):return mf.CrossSection([pts]).extrude(d).rotate([90,0,0]).translate([0,y+d,0])
def face(pts,plane,coord,depth):
 s=xz(pts,-depth/2,depth)
 if plane=='x':s=s.rotate([0,0,90])
 return s.translate([coord,0,0] if plane=='x' else [0,coord,0])
def rect(n,plane,c,u0,u1,z0,z1,d,mat):add(n,face([(u0,z0),(u1,z0),(u1,z1),(u0,z1)],plane,c,d),mat)
bx('Authored flat support',[-30,-22,-.55],[30,22,0],4)
# Core and corner stair volumes follow first/second floor plans, not a solid blocked archway.
bx('Lower central rooms exterior core',[-27.75,-15.65,0],[27.75,3.65,8.55])
for sx in [-1,1]:
 x0,x1=(-27.75,-19.65)if sx<0 else(19.65,27.75)
 bx('North corner stair and service block'+str(sx),[x0,11.65,0],[x1,19.75,8.55])
 bx('South corner stair block'+str(sx),[x0,-19.75,0],[x1,-15.5,8.55])
# Upper exterior backing, opaque model not inferred interior.
bx('Upper gym exterior volume',[-27.75,-19.75,8.35],[27.75,19.75,20.42])
# perimeter roof parapet and shallow section roof, without invented equipment.
for sy in [-1,1]:bx('North-south roof rim'+str(sy),[-28.5,sy*20-.5,20.25],[28.5,sy*20+.5,21])
for sx in [-1,1]:bx('East-west roof rim'+str(sx),[sx*28-.5,-20,20.25],[sx*28+.5,20,21])
add('Shallow pitched roof from section',xz([(-28,20.38),(28,20.38),(28,20.55),(0,20.78),(-28,20.55)],-20,40),3)
# 4m facade modules with actual lower openings retained. Grids on x faces use y coordinates.
def active(plane,u,z):
 if z>=8.35:return True
 if plane=='y':return abs(u)>19.6
 return not (3.6<u<12.4)
def backing(plane,c,u,z0,z1,louvre,out_override=None):
 w=3.06;out=(1 if c>0 else -1) if out_override is None else out_override
 rect('Opaque glazing/louvre backing',plane,c-out*.30,u-w/2-.06,u+w/2+.06,z0,z1,.28,2 if louvre else 1)
 for du in [-w/2,0,w/2]:rect('Window upright',plane,c-out*.18,u+du-.035,u+du+.035,z0,z1,.10,2)
 if louvre:
  for zz in np.arange(z0+.12,z1,.26):rect('Representative louvre blade',plane,c-out*.16,u-w/2,u+w/2,zz,zz+.045,.14,2)
 else:
  for zz in np.arange(z0+.65,z1,.70):rect('Glazing transom',plane,c-out*.18,u-w/2,u+w/2,zz,zz+.045,.12,2)
for plane,c,half in [('y',-20,28),('y',20,28),('x',-28,20),('x',28,20)]:
 levels=[(.50,4.58),(5.48,8.40),(9.48,12.55),(13.48,16.55),(17.48,20.10)]
 for z0,z1 in levels:
  for u in np.arange(-half+2,half,4):
   if active(plane,u,z0):backing(plane,c,u,z0,z1,plane=='x')
 # Horizontal frame beams interrupted at actual open entrance spans below 9m.
 for zz in [0,4.5,8.5,12.5,16.5,20.1]:
  for u in np.arange(-half+2,half,4):
   if active(plane,u,zz):rect('Facade horizontal concrete grid',plane,c,u-2.5,u+2.5,zz,zz+.90,1.0,0)
 for u in np.arange(-half,half+.1,4):
  for z0,z1 in [(0,8.6),(8.3,21)]:
   if active(plane,u,z0) or (plane=='x' and u in [4,12]):rect('Facade vertical concrete grid',plane,c,u-.5,u+.5,z0,z1,1.0,0)
 # Diagonal facade structural braces follow supplied elevation, not guessed mirrored walls.
 points=[(-28,.8),(-8,20.45),(0,8.9),(8,20.45),(28,.8)] if plane=='y' else[(-20,.8),(0,20.45),(20,.8)]
 for (u0,z0),(u1,z1) in zip(points[:-1],points[1:]):
  dx=u1-u0;dz=z1-z0;ln=math.hypot(dx,dz);du=-dz/ln*.50;dv=dx/ln*.50
  pts=[(u0-du,z0-dv),(u1-du,z1-dv),(u1+du,z1+dv),(u0+du,z0+dv)]
  add('Exposed diagonal brace '+str((plane,c,u0)),face(pts,plane,c,1.05))
# Lower recessed north court back and south entrance frontage, visible from exterior.
for plane,c,h in [('y',3.95,28),('y',-15.95,20)]:
 for z0,z1 in [(.30,4.55),(5.45,8.35)]:
  for u in np.arange(-h+2,h,4):backing(plane,c,u,z0,z1,False)
 for zz in [0,4.55,8.4]:rect('Recessed horizontal beam',plane,c,-h,h,zz,zz+.5,.8,0)
 for u in np.arange(-h,h+.1,4):rect('Recessed vertical pier',plane,c,u-.25,u+.25,0,8.55,.8,0)
# Exposed ceiling beams above north court and south entry follow structural bays.
for x in np.arange(-20,20.1,8):
 bx('North court ceiling beam'+str(x),[x-.22,3.5,8.0],[x+.22,20,8.5])
 bx('South entry ceiling beam'+str(x),[x-.22,-20,8.0],[x+.22,-15.5,8.5])
# Entrance portal returns retain window/louvre fields on four real corner inner faces.
for sx in [-1,1]:
 for c,out in [(11.35,-1),(-15.2,1)]:
  for x in np.arange(20,28,4)*sx:
   for z0,z1 in [(.5,4.5),(5.5,8.3)]:backing('y',c,x,z0,z1,True,out)
# East and west entrance flat landings, no invented stairs/slope.
for sx in [-1,1]:bx('Entry landing'+str(sx),[sx*28-.65,4,0],[sx*28+.65,12,.12],0)

for o,i in zip(ops,items):assert i.status()==mf.Error.NoError,(o,i.status())
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
assert s.status()==mf.Error.NoError,s.status()
s=s.set_tolerance(.001).simplify(.001)
m=s.to_mesh64()
# Quantize into STL's actual float32-mm precision before final topology simplification.
# This removes sub-precision CSG seam slivers rather than shipping a broken float32 STL.
qv=np.ascontiguousarray((np.asarray(m.vert_properties)*SCALE).astype(np.float32).astype(np.float64))
qm=mf.Mesh64(qv,np.array(m.tri_verts,dtype=np.uint64,order="C",copy=True),merge_from_vert=np.array(m.merge_from_vert,dtype=np.uint64,copy=True),merge_to_vert=np.array(m.merge_to_vert,dtype=np.uint64,copy=True),run_index=np.array(m.run_index,dtype=np.uint64,copy=True),run_original_id=np.array(m.run_original_id,dtype=np.uint32,copy=True),tolerance=.002)
qs=mf.Manifold(qm).simplify(.01);assert qs.status()==mf.Error.NoError,qs.status()
# Remove only sub-0.001 mm3 numerical CSG crumbs, never meaningful geometry.
comps=qs.decompose();crumbs=[q for q in comps if abs(q.volume())<.001];assert sum(abs(q.volume()) for q in crumbs)<.01
qs=mf.Manifold.batch_boolean([q for q in comps if abs(q.volume())>=.001],mf.OpType.Add)
m=qs.to_mesh64();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Weld duplicate material-boundary positions, retaining each surface triangle's real original material.
v,inv=np.unique(np.round(v,9),axis=0,return_inverse=True);f=inv[f]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='TNFSH Comprehensive Gym 2012 exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats-package.relationships/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'.replace('http://schemas.openxmlformats-package.relationships/2006/relationships','http://schemas.openxmlformats.org/package/2006/relationships'))
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete above-ground 2012 gym exterior using 2013 architect-supplied dimensioned drawings; simplified roof and opaque glazing, no basement/site slope/current-state claim'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
