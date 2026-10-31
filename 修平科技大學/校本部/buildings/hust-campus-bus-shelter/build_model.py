#!/usr/bin/env python3
"""HUST campus bus shelter from official campus album two full shelter photographs, photo-proportional approximation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('blue','Blue structural columns','#143E9A','Official campus photograph blue columns, nominal color'),
('orange','Orange shallow curved roof','#CF5527','Observed orange translucent-looking canopy simplified opaque solid'),
('red','Red perforated side panel','#AD3529','Observed red panel and hexagonal openings; uncertain colored inserts omitted'),
('green','Green bench frame','#47885B','Observed green bench legs and rails'),
('seat','Dark bench surface','#57524B','Observed dark seat surface'),
('board','Pale blank information board and light','#D8DDD4','Visible pale board and roof lamp; all letters omitted'),
('seam','Dark nominal roof seams','#3D3931','Representative dark roof ribs; counts simplified'),
('base','Nominal connecting base','#B3B0A6','Authored support, not exact sidewalk')]]
SCALE=28.0
P={'roof_width':5.6,'roof_depth':2.8,'height':3.35,'nominal_scale_mm_per_unit':28,'right_panel':'Hexagonal through holes; uncertain colored infill omitted, not a claim that actual openings are all empty','roof':'Nominal short-axis shallow curve, opaque solid instead of translucent sheet'}
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2));items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.14]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed principal feature with nominal dimensions'):add(name,box(a,b),mat,evidence)
def yz_prism(points,x,width):return mf.CrossSection([points]).extrude(width).rotate([90,0,90]).translate([x,0,0])
def roof_profile(lo,hi,thickness):
 ys=np.linspace(lo,hi,19);zs=3.0+.35*(1-(ys/1.4)**2);return list(zip(ys,zs-thickness))+list(zip(ys[::-1],zs[::-1]))
bx('Nominal connected sidewalk base',[-2.55,-1.1,-.14],[2.55,1.1,0],7,'Authored support not surveyed curb/drain/pavement')
for x in [-2.2,2.2]:
 for y in [-.8,.8]:bx('Blue column '+str((x,y)),[x-.075,y-.075,0],[x+.075,y+.075,3.18])
for x in [-2.2,2.2]:bx('Blue side upper tie '+str(x),[x-.07,-.85,2.45],[x+.07,.85,2.56])
add('Orange shallow curved canopy',yz_prism(roof_profile(-1.4,1.4,.085),-2.8,5.6),1,'Observed shallow short-direction arc; nominal curve and opaque printable thickness')
for y in [-1.38,1.38]:
 add('Orange rolled outer edge '+str(y),mf.Manifold.cylinder(5.62,.075,.075,24).rotate([0,90,0]).translate([-2.81,y,2.985]),1,'Visible orange thick edge simplified smooth cylinder')
for x in [-2.73,2.73]:add('Orange side edge '+str(x),yz_prism(roof_profile(-1.4,1.4,.13),x-.045,.09),1,'Observed curved end edging')
for x in [-2.0,-1.0,0,1.0,2.0]:add('Representative dark curved rib '+str(x),yz_prism(roof_profile(-1.4,1.4,.105),x-.012,.024).translate([0,0,.008]),6,'Representative black seams/ribs simplified, not exact counts or fasteners')
# Left information board and blue enclosure, blank to avoid manufactured signage.
bx('Blank left information board',[-2.245,-.65,.55],[-2.16,.65,2.25],5,'Observed pale left side board; all map/text omitted')
for z in [.48,2.26]:bx('Left board frame rail '+str(z),[-2.27,-.83,z],[-2.13,.83,z+.08])
# Right side decorative six-sided holes. No assumed glazing or colored inserts.
panel=box([2.16,-.73,.16],[2.24,.73,3.17])
for row in range(11):
 for col in [-1,0,1]:
  y=col*.44;z=.34+row*.255
  pts=[(y+.12*math.cos(math.pi/3*k),z+.12*math.sin(math.pi/3*k)) for k in range(6)]
  panel=panel-yz_prism(pts,2.12,.16)
add('Red hexagon-perforated side panel',panel,2,'Representative 3 by 11 hexagonal holes; count/size nominal, uncertain colored transparent infill omitted, not asserted empty in reality')
bx('Dark bench seat',[-1.9,.03,.48],[.75,.72,.56],4,'Observed long dark seat toward left half')
for x in [-1.8,-.55,.65]:
 for y in [.08,.66]:bx('Green bench leg '+str((x,y)),[x-.045,y-.045,0],[x+.045,y+.045,.5],3)
for y in [.08,.66]:bx('Green bench longitudinal rail '+str(y),[-1.85,y-.035,.21],[.70,y+.035,.28],3)
for x in [-1.8,-.55,.65]:bx('Green bench cross rail '+str(x),[x-.04,.04,.43],[x+.04,.70,.5],3)
bx('Plain roof light',[ -.75,-.10,3.20],[.75,.10,3.29],5,'Observed white underside lamp simplified no wiring/text')
for o,i in zip(ops,items):
 assert i.status()==mf.Error.NoError,(o,i.status())
s=items[0]
for o,i in zip(ops[1:],items[1:]):
 s=s+i
 assert s.status()==mf.Error.NoError,(o,s.status())
s=s.set_tolerance(.001).simplify(.001)
m=s.to_mesh64();print('raw status',s.status(), 'merge',len(m.merge_from_vert));v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Collapse negligible coplanar material seams before export, preserving the true surface.
# Assign palette deterministically by closest point on original triangle surfaces after cleanup.

old_triangles=v[f].copy(); old_centres=v[f].mean(axis=1); old_mi=mi.copy()
s=s.set_tolerance(.001)
clean=s.to_mesh64();v=np.asarray(clean.vert_properties)[:,:3]*SCALE;f=np.asarray(clean.tri_verts)
centres=v[f].mean(axis=1); near=[]
for start in range(0,len(centres),20):
 points=centres[start:start+20]; tri=np.tile(old_triangles,(len(points),1,1)); pts=np.repeat(points,len(old_triangles),axis=0); cp=trimesh.triangles.closest_point(tri,pts); distances=((cp-pts)**2).sum(axis=1).reshape(len(points),len(old_triangles));near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
q=mf.Manifold(mf.Mesh(np.round(v,2).astype(np.float32),np.asarray(f,dtype=np.uint32)))
print('grid cleanup',q.status())
qc=q.to_mesh(); v=np.asarray(qc.vert_properties)[:,:3];f=np.asarray(qc.tri_verts)
centres=v[f].mean(axis=1);near=[]
for start in range(0,len(centres),20):
 points=centres[start:start+20]; tri=np.tile(old_triangles,(len(points),1,1)); pts=np.repeat(points,len(old_triangles),axis=0); cp=trimesh.triangles.closest_point(tri,pts); distances=((cp-pts)**2).sum(axis=1).reshape(len(points),len(old_triangles));near.extend(distances.argmin(axis=1).tolist())
mi=old_mi[near]
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-10;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='HUST campus bus shelter');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete principal bus shelter body. Unknown colored infill in hexagon panel omitted, not asserted to be empty in reality. External lamps, signs and walls excluded. Nominal photo-proportions.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
