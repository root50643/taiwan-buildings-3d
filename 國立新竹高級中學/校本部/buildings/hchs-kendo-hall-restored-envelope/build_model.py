#!/usr/bin/env python3
"""HCHS restored kendo hall exterior envelope; nominal photo-proportional model."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('brick','Restored red brick','#8D4838','PDF16 exterior photo; approximate uncalibrated color'),
('roof','Blue grey metal roof','#6D929F','PDF16 restored roof photo; no exact tile pattern'),
('trim','Pale roof fascia','#D3C7AB','Visible pale fascia at gable edge'),
('window','Dark window recess','#253830','Opaque simplified openings, not glazing simulation'),
('wood','Brown timber frames','#62412A','Visible window mullions and doors'),
('base','Grey plinth and display base','#97938A','Visible grey plinth; extended display base authored')]]
SCALE=15.0
P={'width':6.0,'depth':9.0,'wall_height':4.3,'roof_ridge_height':7.5,'nominal_scale_mm_per_unit':15,'measured_dimensions':False,'unseen_walls':'lower opening counts text-corroborated, exact positions nominal; upper rear blank and not verified'}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.2]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='PDF16 visible form; nominal photo proportions, not measured'):add(name,box(a,b),mat,evidence)
def prism_xz(points,y,depth):return mf.CrossSection([points]).extrude(depth).rotate([90,0,0]).translate([0,y+depth,0])
def panel(name,x,y,z,w,h,side=False,inferred=False,rise=None):
 ev='Inferred opening arrangement from PDF15 text; not directly observed exterior' if inferred else 'PDF16 visible arched windows; nominal dimensions and simplified frame subdivisions'
 # A raised dark arch reads as inset glazing on a solid printable envelope.
 rad=w/2; rise=rad if rise is None else rise; spring=z+h-rise
 pts=[[x-w/2,z],[x+w/2,z]]+[[x+rad*math.cos(a),spring+rise*math.sin(a)] for a in np.linspace(0,math.pi,13)]
 s=prism_xz(pts,y-.035,.065)
 if side:s=s.rotate([0,0,90])
 add(name+' dark arched opening',s,3,ev)
 for xx in [x-w/2+.035,x,x+w/2-.035]:
  ss=box([xx-.022,y-.052,z],[xx+.022,y+.07,spring])
  if side:ss=ss.rotate([0,0,90])
  add(name+' vertical frame',ss,4,ev)
 for zz in np.arange(z+.35,spring,.38):
  ss=box([x-w/2,y-.052,zz-.02],[x+w/2,y+.07,zz+.02])
  if side:ss=ss.rotate([0,0,90])
  add(name+' horizontal frame',ss,4,ev)
 ss=box([x-w/2-.055,y-.09,z-.08],[x+w/2+.055,y+.09,z+.02])
 if side:ss=ss.rotate([0,0,90])
 add(name+' sill',ss,5,ev)
bx('Authored display slab',[-3.6,-5,-.2],[3.6,5,0],5,'Authored support, not surveyed pavement')
bx('Rectangular red brick envelope',[-3,-4.5,0],[3,4.5,4.3])
add('Gable red brick body',prism_xz([[-3,4.25],[3,4.25],[0,7.5]],-4.5,9),0,'PDF16 visible two-slope principal gable; nominal body proportions; front apex clipped per PDF8')
bx('Grey plinth',[-3.025,-4.525,0],[3.025,4.525,.32],5)
# Slightly overhanging roof: continuous two-slope shell, no invented ridge decoration.
for name,pts in [('left',[[-3.3,3.95],[0,7.47],[0,7.67],[-3.3,4.15]]),('right',[[0,7.47],[3.3,3.95],[3.3,4.15],[0,7.67]])]:
 add(name+' roof plane',prism_xz(pts,-4.69,9.38),1,'Visible blue-grey main roof; front apex clipped per PDF8; nominal small cutback')
 for yy in [-4.70,4.63]:add(name+' pale gable fascia',prism_xz(pts,yy,.09),2,'Front fascia visible; rear fascia nominal extrapolation')
# Four facade buttresses separating five windows; rear layout text-supported.
for y,inf in [(-4.5,False),(4.5,True)]:
 sign=-1 if y<0 else 1
 for j,x in enumerate([-1.8,-.6,.6,1.8]):
  bx(('Rear inferred' if inf else 'Front visible')+f' buttress {j}',[x-.11,min(y,y+sign*.22),.25],[x+.11,max(y,y+sign*.22),5.05 if abs(x)<1 else 4.5],0,'PDF15 north/south four buttresses; front seen, rear nominal inferred')
 for j,x in enumerate([-2.4,-1.2,0,1.2,2.4]):panel(('Rear inferred' if inf else 'Front visible')+f' window {j}',x,y+sign*.018,.63,.77,2.75 if j in [0,4] else 2.47,inferred=inf,rise=None if j in [0,4] else .16)
# Three narrow upper windows are directly visible on front only.
for x in [-.9,0,.9]:
 bx('Front upper narrow dark window',[x-.15,-4.57,4.6],[x+.15,-4.49,5.8],3)
 bx('Front upper window central mullion',[x-.018,-4.59,4.6],[x+.018,-4.51,5.8],4)
 for z in [4.92,5.25,5.57]:bx('Front upper window cross bar',[x-.15,-4.59,z],[x+.15,-4.51,z+.035],4)
 bx('Front upper window lintel',[x-.2,-4.61,5.8],[x+.2,-4.49,5.88],4)
# Long walls: six buttresses / two doors each per text; visible side positions approximate.
for x,inf in [(3,False),(-3,True)]:
 sign=1 if x>0 else -1
 for j,y in enumerate(np.linspace(-3.2,3.2,6)):
  bx(('Left inferred' if inf else 'Right visible')+f' side buttress {j}',[min(x,x+sign*.22),y-.105,.25],[max(x,x+sign*.22),y+.105,4.12],0,'PDF15 east/west six buttresses; hidden side arrangement inferred')
 for j,y in enumerate(np.linspace(-3.84,3.84,7)):
  if j in [1,5]:
   panel(('Left inferred' if inf else 'Right visible')+f' arched door {j}',y,-x-sign*.018,.25,.72,2.7,True,inf,rise=.18)
   bx(('Left inferred' if inf else 'Right visible')+f' door lower timber panel {j}',[min(x,x+sign*.09),y-.315,.26],[max(x,x+sign*.09),y+.315,2.64],4,'Visible wooden door below short dark arched transom; hidden side inferred')
  else:panel(('Left inferred' if inf else 'Right visible')+f' side window {j}',y,-x-sign*.018,.63,.76,2.75,True,inf)
# PDF8 exposes a small clipped front ridge and pale slatted inset; rear not mirrored.
add('Front pale clipped-top inset',prism_xz([[-.70,6.82],[.70,6.82],[.25,7.18],[-.25,7.18]],-4.57,.09),2,'PDF8 complete front apex silhouette; nominal depth, simplified pale inset')
for xx in [-.50,-.25,0,.25,.50]:
 top=7.18 if abs(xx)<=.25 else 6.82+(.70-abs(xx))*.8
 bx('Front inset vertical timber line',[xx-.016,-4.59,6.84],[xx+.016,-4.52,top],4,'PDF8 visible vertical divisions; representative number and width')
bx('Front inset lower edging',[-.74,-4.60,6.77],[.74,-4.51,6.84],4,'PDF8 visible darker lower border; approximate')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
cut=prism_xz([[-5,6.7],[-3.5,8.2],[-3.5,9],[-5,9]],-4,8).rotate([0,0,90]).translate([0,0,.2]).as_original();ids[int(cut.original_id())]=1
s=(s-cut).set_tolerance(.01).simplify(.01)
m=s.to_mesh64();print('raw status',s.status(), 'merge',len(m.merge_from_vert));v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Collapse negligible coplanar material seams before export, preserving the true surface.
# Assign palette deterministically by nearest original triangle centroid after geometric cleanup.

old_centres=v[f].mean(axis=1); old_mi=mi.copy()
s=s.as_original().set_tolerance(.001).simplify(.001)
clean=s.to_mesh64();v=np.asarray(clean.vert_properties)[:,:3]*SCALE;f=np.asarray(clean.tri_verts)
centres=v[f].mean(axis=1); near=[]
for start in range(0,len(centres),80):
 distances=((centres[start:start+80,None,:]-old_centres[None,:,:])**2).sum(axis=2);near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
q=mf.Manifold(mf.Mesh(np.round(v,2).astype(np.float32),np.asarray(f,dtype=np.uint32)))
print('grid cleanup',q.status())
qc=q.to_mesh(); v=np.asarray(qc.vert_properties)[:,:3];f=np.asarray(qc.tri_verts)
centres=v[f].mean(axis=1);near=[]
for start in range(0,len(centres),80):
 distances=((centres[start:start+80,None,:]-old_centres[None,:,:])**2).sum(axis=2);near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-10;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
# Preserve explicit roof color on the newly cut sloped apex plane after cleanup.
cut_faces=np.all(np.abs((v[f][:,:,2]-v[f][:,:,1])-178.5)<.035,axis=1);mi[cut_faces]=1
roof_faces=np.all(np.abs(v[f][:,:,2]+np.abs(v[f][:,:,0])*(3.52/3.3)-118.05)<.035,axis=1);mi[roof_faces]=1
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='HCHS restored kendo hall exterior envelope');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Restored exterior main envelope based on 2022 alumni PDF15-16. Rear opening positions inferred from text; no internal structure or surveyed dimensions; front clipped apex/pale inset supported by PDF8; depth nominal.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
