#!/usr/bin/env python3
"""Imperial Sugar Taichung office historic main body; source-supported exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','Gray green historic masonry','#8B9387','2019 official restored exterior photos; uncalibrated'),('trim','Pale stone cornice and trim','#CEC9B6','Restoration elevations and restored photographs'),('frame','Dark wooden frames','#4D3C2C','2019 restored wood window details'),('glass','Opaque inset glass proxy','#718186','Opaque manufacture proxy, no interior'),('roof','Gray tiled roof simplified','#676965','Hip-roof geometry from four elevations; coarse roof courses'),('base','Authored display support','#B4AF9F','Display support, not site reconstruction'),('door','Wooden doors','#76624A','Restored entrance details, simplified panels'),('metal','Roof ventilator','#80827A','Six visible ventilator caps in 2019 photo')]]
SCALE=.025
items=[];ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*100);b=np.round(np.array(b)*100);return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,evidence):
 s=s.translate([0,0,60]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat,evidence):add(name,box(a,b),mat,evidence)
def arch(w,bottom,spring,rise):
 pts=[(-w/2,bottom),(w/2,bottom),(w/2,spring)]+[(w/2*math.cos(t),spring+rise*math.sin(t))for t in np.linspace(0,math.pi,17)[1:]]
 return mf.CrossSection([(np.array(pts)*100).tolist()]).extrude(120).rotate([90,0,0]).translate([0,60,0])
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*100).tolist())
def hip(x0,x1,y0,y1,z0,z1):
 d=min((y1-y0)/2,(x1-x0)/2)
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(L*100,r*100,r*100,12).transform(np.column_stack([x,y,z,a*100]))



# Official 2016 restoration drawings; dimensions read as centimetres. Not an asbuilt survey.
W=64.58;D=14.545;E=50.915;lowD=7.29;H=6.27
bx('Authored support',[-1.5,-5,-.6],[W+1.5,23.3,0],5,'Display support, not landscape')
bx('Main historic office solid body',[0,0,0],[E,D,H],0,'Dimensioned restoration plan main body; interior omitted')
bx('Lower east office wing',[E-.02,0,0],[W,lowD,H],0,'Plan east wing and lower hip roof')
bx('Historic west return',[0,D-.02,0],[6.335,21.89,4.415],0,'West return retained per floor plan; excludes separate drawing-labelled restaurant addition; age not assigned')
add('Main hip roof',hip(-.5,E+.4,-.5,D+.5,H,10.23),4,'North south and end restoration elevations; roof surface simplified')
add('Lower east hip roof',hip(E-.4,W+.5,-.5,lowD+.5,H,8.43),4,'Lower eastern roof, official elevations')
add('West return shed roof',hull([[-.3,D,4.415],[6.6,D,4.415],[6.6,22.2,4.415],[-.3,22.2,4.415],[-.3,D,6.27],[6.6,D,6.27],[-.3,22.2,5.42],[6.6,22.2,5.42]]),4,'West return lower roof from west elevation; exact flashing omitted')
# Surface-attached frames preserve opaque inset depth without pretending to reconstruct rooms.
def slab(name,side,u0,u1,z0,z1,depth,mat,ev,plane=None):
 if side in ('N','S'):
  y=(0 if side=='N' else D) if plane is None else plane
  a,b=(y-depth,y+.02) if side=='N' else (y-.02,y+depth)
  bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  x=(0 if side=='W' else W) if plane is None else plane
  a,b=(x-depth,x+.02) if side=='W' else (x-.02,x+depth)
  bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def window(side,u,w=1.15,z=1.4,h=2.55,plane=None,door=False,upper=True):
 ev='Window or door position from corresponding restoration elevation; coarse estimated opening size'
 slab(side+' pale surround',side,u-w/2-.10,u+w/2+.10,z-.10,z+h+.10,.075,1,ev,plane)
 slab(side+' dark sash',side,u-w/2,u+w/2,z,z+h,.095,2,ev,plane)
 slab(side+' opaque pane',side,u-w/2+.075,u+w/2-.075,z+.075,z+h-.075,.11,3 if not door else 6,'Solid-backed pane, not real glazing or operable opening',plane)
 for frac in [.15,.30,.45,.60,.76]:slab(side+' horizontal sash bar',side,u-w/2,u+w/2,z+h*frac-.025,z+h*frac+.025,.16,2,'Lower multi-pane sash and separate taller upper light from official elevations',plane)
 if door:slab(side+' glazed upper door light',side,u-w/2+.075,u+w/2-.075,z+h*.77,z+h-.075,.17,3,'Glazed upper door light over solid lower leaf, coarse proxy',plane)
 slab(side+' central sash',side,u-.025,u+.025,z,z+h,.18,2,ev,plane)
 if upper:
  slab(side+' upper transom surround',side,u-w/2-.08,u+w/2+.08,4.55,5.03,.08,1,'Separate high ventilation window, not second storey',plane)
  slab(side+' upper transom glass',side,u-w/2,u+w/2,4.61,4.97,.115,3,ev,plane)
  for q in [-.22,.22]:slab(side+' vent mullion',side,u+q-.025,u+q+.025,4.61,4.97,.14,2,ev,plane)
# Front window locations explicitly differ from south and end elevations.
north=[1.15,3.43,7.4,9.53,11.65,13.99,16.54,19.09,21.65,24.0,25.55,33.1,34.65,36.90,39.45,42.0,44.54,47.09,52.06,54.36,56.42,58.54,60.96,63.37]
for u in north:
 if 27<u<32.7:continue
 window('N',u)
# Two auxiliary north doors, replacing nearby window centres with simplified framed doors.
for u in [5.45,48.95]:window('N',u,1.2,.62,3.35,door=True,upper=False)
# South repeated ceremonial doors with round upper lights; eastern service bays are not mirrored.
for u in [7.4,9.53,11.65,16.54,19.09,21.65,26.1,28.7,31.2,33.7,35.9,39.45,42.0,44.54,47.09,49.64]:
 if min(abs(u-dd) for dd in [13.99,24.0,33.0,43.0])>1.65:window('S',u)
for u in [13.99,24.0,33.0,43.0]:
 window('S',u,1.8,.62,2.6,door=True,upper=False)
 slab('South door stepped lintel','S',u-1.7,u+1.7,3.35,3.52,.22,1,'Stepped lintel and round light visible on drawing and 2019 south photo')
 for j in range(3):slab('South lintel bracket','S',u-1.45+j*.10,u-1.35+j*.10,3.52,4.2-j*.12,.18,1,'Coarse stepped bracket')
 disc=mf.Manifold.cylinder(12,42,42,32).rotate([90,0,0]).translate([u*100,(D+.12)*100,4.10*100]);add('South round upper light',disc,3,'Round light above paired door in south restoration elevation')
 ring=(mf.Manifold.cylinder(6,48,48,32)-mf.Manifold.cylinder(8,42,42,32).translate([0,0,-1])).rotate([90,0,0]).translate([u*100,(D+.17)*100,4.10*100]);add('South round upper-light pale rim',ring,1,'Round rim visible in south elevation; 32 facets')
 slab('Round light horizontal cross','S',u-.42,u+.42,4.075,4.125,.18,2,'Simplified round light cross frame')
 slab('Round light vertical cross','S',u-.025,u+.025,3.68,4.52,.19,2,'Simplified round light cross frame')
 for j in range(3):bx('South entry step',[u-1.1,D,.0+j*.20],[u+1.1,D+1.05-j*.30,.21+j*.20],1,'Raised floor stair simplified')
for u in [52.05,54.36,56.42,58.54,60.96,63.37]:window('S',u,1.3,.8,3.1,plane=lowD,door=u in [54.36,63.37],upper=False)
for u in [1.8,5.42,9.06]:window('W',u,1.7,1.4,2.55,upper=False)
window('W',12.0,1.8,.62,3.35,door=True,upper=False)
for j in range(3):bx('West doorway step',[-1.05+j*.3,10.9,0],[0,13.1,.21+j*.20],1,'West elevation door stairs')
for u in [16.4,20.0]:window('W',u,1.75,1.3,2.0,upper=False)
for u in [1.75,3.6,5.45]:window('E',u,1.1,1.45,2.2,upper=False)
for u in [9.05,12.0]:window('E',u,1.7,1.4,2.55,plane=E,upper=False)
# Continuous base and cornice lines follow each wall section.
for side,a,b,plane,top in [('N',0,W,0,H),('S',6.335,E,D,H),('S',E,W,lowD,H),('W',0,D,0,H),('E',0,lowD,W,H),('E',lowD,D,E,H),('W',D,21.89,0,4.415)]:
 for z,h,dep in [(0.12,.18,.15),(.45,.13,.17),(.9,.12,.12),(4.35,.10,.15),(top-.15,.13,.25)]:
  if z<top and not(side=='S' and z==4.35):slab('Stone continuous band',side,a,b,z,z+h,dep,1,'Official restoration horizontal base and cornice profiles, coarsened',plane)
# North entry layered stepped parapet, recessed opaque door and stairs.
c=29.25;pw=5.96;py=-3.45
add('Projecting main entry with true porch recess',box([c-pw/2,py,.62],[c+pw/2,.1,5.3])-box([c-1.75,py-.1,.62],[c+1.75,-.30,3.95]),0,'Central projecting entry and recessed passage visible in restored photo; depth estimated')
window('N',c,2.6,.62,3.0,plane=-.32,door=True,upper=False)
for j,(ww,zz) in enumerate([(6.7,5.25),(5.65,6.3),(3.85,7.05)]):
 by=py if j==0 else py+1.2
 bx('Entry layered pale ledge',[c-ww/2,by-.22,zz],[c+ww/2,.05,zz+.16],1,'Stepped Chinese-influenced entrance cornice seen in restored photos')
 for xx in [c-ww/2,c+ww/2-.18]:bx('Entry upturned ledge end',[xx,by-.22,zz],[xx+.18,by+.12,zz+.33],1,'Coarse raised cornice ends')
bx('Entry upper parapet',[c-1.65,py+1.2,5.3],[c+1.65,py+1.62,7.07],0,'Central high parapet, not an enclosed second floor')
bx('Entry crest solid neck',[c-.18,py+1.24,7.07],[c+.18,py+1.56,7.77],0,'Fused structural core of stepped crest, coarse print simplification')
for zz,ww in [(7.20,.85),(7.42,.68),(7.64,.85)]:bx('Entry stepped crest',[c-ww/2,py+1.2,zz],[c+ww/2,py+1.6,zz+.13],1,'Small stepped central crest seen in official entrance photo; coarse proxy')
add('Entry central diamond plaque',hull([[c-.34,py-.15,4.31],[c,py-.15,4.58],[c+.34,py-.15,4.31],[c,py-.15,4.04],[c-.34,py+.02,4.31],[c,py+.02,4.58],[c+.34,py+.02,4.31],[c,py+.02,4.04]]),1,'Central diamond plaque silhouette only; historic lettering/seal omitted')
# Coarse sawtooth border on actual portal, no text or seal imitation.
for xx in [c-1.89,c+1.75]:
 bx('Entry portal surround',[xx,py-.12,.62],[xx+.14,py+.04,4.08],1,'Stone portal edge in official close-up')
 for k in range(12):
  zz=.75+k*.25
  add('Coarse portal sawtooth',hull([[xx,py-.14,zz],[xx+.14,py-.14,zz],[xx+.14,py+.02,zz],[xx,py+.02,zz],[xx+.14,py-.14,zz+.17],[xx+.14,py+.02,zz+.17]]),1,'Approximate repetitive sawtooth relief, not exact carving')
bx('Entry portal lintel',[c-1.89,py-.12,3.95],[c+1.89,py+.04,4.1],1,'Portal lintel')
for j in range(11):bx('Entry decorative square band',[c-2.65+j*.49,py-.12,4.19],[c-2.4+j*.49,py+.02,4.4],1,'Coarse repeating square entrance ornament, no logos')
for j in range(3):bx('Entry front stair',[c-1.7,py-1.2+j*.30,0],[c+1.7,py,.21+j*.20],1,'Three coarse entry steps to raised floor')
# Six north-visible ridge ventilators plus one on west return shown in west elevation.
for x,z,y in [(9.5,10.23,D/2),(18,10.23,D/2),(26.5,10.23,D/2),(35,10.23,D/2),(43.5,10.23,D/2),(57.4,8.43,lowD/2),(3.2,5.82,18.2)]:
 add('Roof ventilator stem',mf.Manifold.cylinder(95,15,15,12).translate([x*100,y*100,(z-.12)*100]),7,'Main and east six ventilators cross-checked in 2019 north photo; west-return seventh from west drawing, positions approximate')
 add('Ventilator tapered base',mf.Manifold.cylinder(35,33,17,12).translate([x*100,y*100,(z-.1)*100]),7,'Coarse ventilator profile')
 bx('Ventilator square cap',[x-.22,y-.22,z+.65],[x+.22,y+.22,z+.84],7,'Cap simplified, no tiny openings')
# Roof tile ribs and ridge end ornaments omitted; smooth hips explicitly disclosed.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.000125 mm3.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Imperial Sugar Taichung historic office main body');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historic office exterior study based on restoration design and 2019 photographs; excludes drawing-labelled restaurant addition and known modern landscape canopy; opaque glazing and solid interior, no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
