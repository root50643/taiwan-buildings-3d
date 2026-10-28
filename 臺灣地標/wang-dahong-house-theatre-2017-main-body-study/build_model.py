#!/usr/bin/env python3
"""Wang Dahong House Theatre reconstructed main body; source-supported exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('brick','Unpainted red brick','#925B46','2018 TFAM replica photos; coarse joint relief, uncalibrated'),('white','White beam and whitewashed end','#E5E2D8','2018 TFAM replica photos'),('black','Dark window frames and roof edge','#292F2B','2018 replica photos; solid opaque glazing'),('glass','Opaque dark glazing proxy','#57615D','No transparent glazing or internal furniture reconstructed'),('floor','Dark cement floor','#535551','Reconstruction report two-foot module'),('base','Authored display support','#AEA99C','Not reconstructed garden'),('joint','Approximate coarse brick joints','#AF8C78','Not a bond-by-bond construction survey'),('metal','Door handle','#A28B54','Visible replica entrance hardware, coarse proxy')]]
SCALE=.08
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
 d=4.25
 return hull([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
def beam(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d);z=d/L;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(L*100,r*100,r*100,12).transform(np.column_stack([x,y,z,a*100]))



# Based on TFAM reconstruction article 189 pp20-31 and 2018 official media photographs.
# Model the 2017 replica main body, NOT a precise reconstruction of the demolished 1953 original.
U=.6096; W=9.23;D=W;floor=.16;ceil=floor+2.934;roof=ceil+.27
bx('Authored support plinth',[-1.3,-1.8,-.6],[W+1.3,D+1.1,0],5,'Display support only, original estate garden and boundary walls excluded')
bx('Dark raised floor',[0,0,0],[W,D,floor],4,'Plan main body and dark cement floor; floor rise approximate')
# U-shaped masonry shell with north and west openings, a true circular east recess.
west=box([0,0,floor],[.35,D,ceil]) - box([-.1,5.75,floor],[.5,5.75+2*U,ceil])
north=box([0,D-.35,floor],[W,D,ceil])-box([2.60,D-.5,floor],[2.60+4*U,D+.1,ceil])
cy=6.80;cz=floor+1.65;rr=.8382
# Cylinder axes normally Z; rotate about Y into the east wall.
moon=mf.Manifold.cylinder(80,rr*100,rr*100,64).rotate([0,90,0]).translate([(W-.5)*100,cy*100,cz*100])
east=box([W-.35,0,floor],[W,D,ceil])-moon
add('West red masonry wall with entry',west,0,'Official plan west entry + replica photos; opening offset estimated from plan')
add('North masonry with four-panel opening',north,0,'Original plan north four cross-checked with reconstruction article eighteen total and fourteen south; no direct complete replica north photograph')
add('East masonry and circular window opening',east,0,'Official plan and 2018 replica moon-window photograph; 5.5ft aperture approximated')
# Solid roof, white perimeter fascia and thin dark weathering cap. No invented rooftop equipment.
bx('White continuous roof fascia',[-.04,-.04,ceil],[W+.04,D+.04,roof],1,'Replica flat roof and continuous pale band, thickness estimated')
bx('Dark roof weathering cap',[-.06,-.06,roof],[W+.06,D+.06,roof+.045],2,'2018 exterior photograph thin dark upper edge; roof drainage/hidden structure omitted')
bx('Opaque solid interior proxy',[.20,.86,floor],[W-.30,D-.18,ceil+.02],0,'Interior intentionally solid; no room or furniture reconstruction')
# South glazed front recessed by a short porch.
y=.82
bx('South opaque glazing',[.35,y,floor],[W-.35,y+.07,ceil],3,'Fourteen glazed pivot leaves; opaque manufacture proxy, no visible interior')
for j in range(15):
 x=.35+j*U;bx('South pivot leaf edge',[x-.023,y-.045,floor],[x+.023,y+.10,ceil],2,'14 equal two-foot leaves; paired fine edges exaggerated for print, not fixed structural mullions')
for z in [floor+.02,floor+.66,ceil-.035]:bx('South leaf horizontal rail',[.35,y-.05,z],[W-.35,y+.10,z+.045],2,'Replica glazing low horizontal rail; height photo-estimated')
# Two slim free-standing black columns in front of glazing at 2:3:2 bay divisions.
for x in [.35+4*U,.35+10*U]:add('South porch black round column',beam([x,.28,floor],[x,.28,ceil+.025],.045),2,'Two black columns, plan 4:6:4 glazing modules; diameter approximate')
# Four north glazed leaves from original plan cross-checked with article 18 total minus 14 south; not a mirrored facade.
bx('North opaque glazing',[2.60,D-.22,floor],[2.60+4*U,D-.13,ceil],3,'Four north leaves inferred from original plan and article eighteen total minus fourteen south; opaque proxy')
for j in range(5):
 x=2.60+j*U;bx('North leaf frame',[x-.023,D-.24,floor],[x+.023,D-.10,ceil],2,'Four leaf layout, coarse visible frame')
for z in [floor+.02,floor+.66,ceil-.035]:bx('North horizontal leaf rail',[2.60,D-.24,z],[2.60+4*U,D-.10,z+.045],2,'Same glazed leaf module; small rail levels estimated')
# West entry two black leaves recessed in masonry; metal replacement noted by reconstruction team.
bx('West black entry leaves',[.12,5.75,floor],[.23,5.75+2*U,ceil],2,'Replica west double entry; article records replacement with metal for durability')
bx('West entry centre reveal',[.10,5.75+U-.012,floor],[.235,5.75+U+.012,ceil],4,'Two-leaf division')
for yy in [5.75+U-.10,5.75+U+.10]:
 add('West entry coarse handle',beam([.09,yy,1.14],[.09,yy,1.40],.025),7,'Coarse handle proxy, not exact hardware')
 for z in [1.16,1.38]:bx('Handle connection',[.08,yy-.02,z-.02],[.15,yy+.02,z+.02],7,'Coarse fused handle support')
# Moon window backed on inner side so the aperture retains genuine depth.
back=mf.Manifold.cylinder(8,(rr+.03)*100,(rr+.03)*100,64).rotate([0,90,0]).translate([(W-.32)*100,cy*100,cz*100])
add('Moon opaque inset backing',back,3,'Opaque backing, not transparent view through bedroom')
# White circular reveal at exterior side (faceted 64-sided approximation).
outer=mf.Manifold.cylinder(6,(rr+.055)*100,(rr+.055)*100,64)-mf.Manifold.cylinder(8,(rr+.03)*100,(rr+.03)*100,64).translate([0,0,-1])
add('White circular aperture rim',outer.rotate([0,90,0]).translate([(W-.035)*100,cy*100,cz*100]),1,'White circular reveal in 2018 replica photo; slight thickening for readability')
# Closed lattice proxy; source sliding sash may be open in photograph, represented closed here.
for off in [-.70,-.525,-.35,-.175,0,.175,.35,.525,.70]:
 h=(rr*rr-off*off)**.5-.04
 bx('Moon window vertical lattice',[W-.27,cy+off-.014,cz-h],[W-.20,cy+off+.014,cz+h],2,'Fine rectangular sliding lattice, represented closed; grid estimated')
for off in [-.50,0,.50]:
 h=(rr*rr-off*off)**.5-.04
 bx('Moon window horizontal lattice',[W-.27,cy-h,cz+off-.017],[W-.20,cy+h,cz+off+.017],2,'Three coarse transverse lattice bars')
# Enlarged approximate joint relief, kept clear of aperture edges to avoid sliver faces.
def runs(name,z0,z1):
 if name=='West':return [(.035,5.71),(5.75+2*U+.04,D-.035)]
 if name=='North':return [(.035,2.56),(2.60+4*U+.04,W-.035)]
 dz=0 if z0<=cz<=z1 else min(abs(z0-cz),abs(z1-cz))
 if dz<rr+.035:
  h=(max(0,(rr+.035)**2-dz**2))**.5+.035
  return [(.035,cy-h),(cy+h,D-.035)]
 return [(.035,D-.035)]
def joint(name,a,b,z0,z1):
 if b-a<.004:return
 if name=='West':q=box([-.015,a,z0],[.025,b,z1])
 elif name=='East':q=box([W-.025,a,z0],[W+.015,b,z1])
 else:q=box([a,D-.025,z0],[b,D+.015,z1])
 add(name+' approximate brick joint',q,6,'Enlarged coarse alternating joint rhythm; clearances around openings and exact French bond simplified')
for row in range(34):
 z=round(floor+.055+row*.083,3)
 if z+.065>=ceil:continue
 for name in ['West','East','North']:
  for a,b in runs(name,z,z+.012):joint(name,a,b,z,z+.012)
  for a,b in runs(name,z+.022,z+.065):
   for k in range(27):
    for off in [0,.23]:
     u=.10+k*.35+off+(.115 if row%2 else 0)
     if a+.02<u<b-.025:joint(name,u,u+.012,z+.022,z+.065)
# Front wall-end whitewash observed from courtyard; no whitewash extended to other external walls.
bx('West front whitewashed wall end',[-.002,-.015,floor],[.351,.013,ceil],1,'Replica courtyard-facing masonry return is whitewashed')
bx('East front whitewashed wall end',[W-.351,-.015,floor],[W+.002,.013,ceil],1,'Whitewashed front wall return, coarse solid tone not distressed surface')
# A short stepping stone approach only; no claim to historic landscaping.
for k in range(3):bx('Entry approach slab',[-.95,5.73+k*.43,.01],[.04,6.10+k*.43,.10],4,'Minimal source-visible side-entry approach, surrounding estate omitted')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
# Remove only isolated numerical union slivers smaller than 0.000125 mm3.
chunks=s.decompose();removed_slivers=[q.volume()*SCALE**3 for q in chunks if abs(q.volume())<1];s=mf.Manifold.batch_boolean([q for q in chunks if abs(q.volume())>=1],mf.OpType.Add)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Wang Dahong House Theatre replica main-body exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'removed_numerical_sliver_volumes_mm3':removed_slivers,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'2017 replica main body exterior only; excludes garden boundary/cafe/interior. Modular and photo-estimated dimensions, opaque glazing, approximate brick courses; no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
