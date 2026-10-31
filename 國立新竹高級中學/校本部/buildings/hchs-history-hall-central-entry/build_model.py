#!/usr/bin/env python3
"""HCHS historical hall entrance segment. Dimensions are photo proportions, not surveyed."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
('wall','Pale warm plaster','#D9D5BC','Official2023frontphoto, not calibrated'),
('frame','Pale grey door and frame','#B9C0B4','Visible ironwork and trim'),
('recess','Neutral dark recess','#4A4D47','Interior omitted; neutral shadow'),
('reserved','Reserved','#A0A49B','Unused'),
('dark','Eave shadow','#383C36','Observed dark eave underside'),
('base','Grey wash pebble and ramp','#969D99','Visible grey plinth and curved ramp walls'),
('reserved2','Reserved2','#D0CEBE','Unused'),
('cut','Artificial backing','#B1B1AA','Unobserved cut back not actual rear')]]
SCALE=8.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Observed visible feature; photo normalized, not measured'):add(name,box(a,b),mat,evidence)
def frontcyl(rad,depth,x,y,z,n=24):return mf.Manifold.cylinder(depth,rad,rad,n).rotate([90,0,0]).translate([x,y,z])
# Main source image shows central entrance only. Wider hall/roof excluded.
bx('Artificial segment footing',[-8.3,-6.5,-.6],[8.3,1.3,-.15],5,'Artificial cut support, not actual site boundary')
bx('Entrance segment wall',[-7.4,0,-.2],[7.4,1,10.9],0,'Visible central cream wall only, artificial shallow backing')
bx('Wash pebble grey dado',[-7.4,-.12,-.2],[7.4,.2,2.25],5,'Observed grey lower wall band')
bx('Dado top trim',[-7.4,-.2,2.2],[7.4,.2,2.38],1)
bx('Artificial rear closure',[-7.4,.92,-.2],[7.4,1.1,10.9],7,'No actual rear known; plain authored backing')
bx('Observed flat front eave edge',[-7.8,-.9,10.85],[7.8,1.1,11.16],1,'Visible front eave strip only, actual gabled roof beyond image omitted')
bx('Eave dark underside',[-7.75,-.92,10.70],[7.75,.1,10.87],4)
# Plain dark entry; no exhibit, people or interior guessed.
bx('Entry dark backing',[-1.80,-.23,.12],[1.80,.03,5.95],2,'Dark relief cut; museum interior deliberately excluded')
for x in [-1.95,1.95]:bx('Door jamb',[x-.13,-.40,.05],[x+.13,.15,6.05],1)
bx('Glazed transom',[-1.8,-.25,6.0],[1.8,.03,6.55],2)
for z in [5.95,6.55]:bx('Transom frame',[-2.02,-.41,z],[2.02,.12,z+.10],1)
bx('Projecting thin entrance canopy',[-2.75,-2.0,6.6],[2.75,.10,6.88],0,'Visible shallow rectangular canopy; thickness and depth approximate')
# Fanlight true semicircle: approximate radial mullions retained.
def halfdisk(rad,depth,y,z):return frontcyl(rad,depth,0,y,z) ^ box([-rad-.2,y-depth-.1,z-.002],[rad+.2,y+.1,z+rad+.1])
add('Semicircular fanlight shadow',halfdisk(1.66,.10,-.22,7.10),2,'Observed semicircular radial fanlight, not arbitrary rectangle')
ring=halfdisk(1.91,.28,-.14,7.10)-halfdisk(1.66,.60,.02,7.10)
add('Fanlight pale half-round surround',ring,1,'Semicircular raised surround visible over canopy')
bx('Fanlight sill',[-1.92,-.46,7.04],[1.92,.08,7.18],1)
# rods in facade XZ plane, no mesh of unseen interior
import math
def rod(name,a,b,r,mat=1,evidence='Visible simplified radial mullion'):
 v=np.array(b)-a;h=float(np.linalg.norm(v));yaw=math.degrees(math.atan2(v[1],v[0]));pitch=math.degrees(math.acos(v[2]/h));add(name,mf.Manifold.cylinder(h,r,r,12).rotate([0,pitch,yaw]).translate(a),mat,evidence)
for ang in [25,50,75,90,105,130,155]:
 q=math.radians(ang);rod('Fanlight radial bar',[0,-.34,7.1],[1.63*math.cos(q),-.34,7.1+1.63*math.sin(q)],.035)
# narrow flanking windows, clipped top corners. Local front relief, not room reconstruction.
for cx in [-3.45,3.45]:
 vv=[[cx-.64,-.22,2.9],[cx+.64,-.22,2.9],[cx+.64,-.22,6.1],[cx+.37,-.22,6.5],[cx-.37,-.22,6.5],[cx-.64,-.22,6.1]]
 poly=np.array([[x,z] for x,y,z in vv]);cs=mf.CrossSection([poly]);shape=cs.extrude(.12).rotate([90,0,0]).translate([0,.04,0])
 add('Narrow clipped-top window',shape,2,'Observed narrow side windows with chamfered top, approximate proportions')
 for x in [cx-.65,cx-.25,cx+.25,cx+.65]:bx('Side window vertical bar',[x-.035,-.34,2.88],[x+.035,.05,6.10 if abs(x-cx)>.4 else 6.48],1)
 for z in [2.88,3.25,5.85,6.10]:bx('Side window horizontal bar',[cx-.65,-.34,z],[cx+.65,.05,z+.06],1)
 for sign in [-1,1]:rod('Window clipped top frame',[cx+sign*.65,-.32,6.1],[cx+sign*.37,-.32,6.5],.055)
 bx('Window top frame',[cx-.37,-.34,6.47],[cx+.37,.02,6.55],1)
# Double perforated iron doors opened outwards as in source; reduced rectangular holes.
for side in [-1,1]:
 panel=box([0,-.10,0],[1.75,.10,5.8]);holes=[]
 for z0,z1 in [(.45,2.1),(3.25,5.35)]:
  for row in range(5):
   for col in range(5):
    x=.14+col*.31;z=z0+row*(z1-z0)/5;holes.append(box([x,-.2,z],[x+.17,.2,z+.18]))
 panel=panel-mf.Manifold.batch_boolean(holes,mf.OpType.Add)
 # left hinge starts at -1.9, opens left-forward; right is mirrored.
 if side==-1:panel=panel.rotate([0,0,-115]).translate([-1.9,-.30,.12])
 else:panel=panel.rotate([0,0,-65]).translate([1.9,-.30,.12])
 add('Open perforated door leaf',panel,1,'Observed open metal leaves; angle and hole counts approximated, no private interior')
# Gentle entry ramp represented as a sloped wedge, not access-code specification.
# The ramp surface fans out to follow the observed curved sidewalls, rather than a narrow rectangle.
vv=[]
for t in np.linspace(0,1,25):
 w=2.22+3.6*t*t;y=-.22-5.25*t;z=.4*(1-t)+.02*t
 vv.extend([[-w,y,-.20],[w,y,-.20],[-w,y,z],[w,y,z]])
ff=[]
for k in range(24):
 a=4*k;b=a+4
 ff.extend([[a,b,b+1],[a,b+1,a+1],[a+2,a+3,b+3],[a+2,b+3,b+2],[a,a+2,b+2],[a,b+2,b],[a+1,b+1,b+3],[a+1,b+3,a+3]])
ff.extend([[0,1,3],[0,3,2],[96,98,99],[96,99,97]])
# Orient outward robustly; constructed faces checked for positive volume.
mm=trimesh.Trimesh(vv,ff,process=False)
if mm.volume<0:ff=np.asarray(ff)[:,::-1]
add('Authored approximate curved fan entry ramp',mf.Manifold(mf.Mesh(np.array(vv,np.float32),np.array(ff,np.uint32))),5,'Visible fan-shaped sloped entry follows curved sidewalls; exact slope and width not measured')
# Bowed outer front edge visible in source, meets the flared slope with small real overlap.
cap=[[-5.84,-5.40],[5.84,-5.40]]
for x in np.linspace(5.84,-5.84,41):cap.append([x,-5.47-.55*(1-(x/5.84)**2)])
cap=np.array(cap);ar=np.sum(cap[:,0]*np.roll(cap[:,1],-1)-cap[:,1]*np.roll(cap[:,0],-1));cap=cap if ar>0 else cap[::-1]
add('Bowed ramp front lip',mf.CrossSection([cap]).extrude(.23).translate([0,0,-.20]),5,'Visible bowed outer ramp edge, curvature approximate')
# Low curving sidewalls flare outward toward viewer. Segment polygon extrusions attach base.
for side in [-1,1]:
 pts=[]
 for t in np.linspace(0,1,25):pts.append([side*(2.14+3.6*t*t),-.25-5.2*t])
 for t in np.linspace(1,0,25):pts.append([side*(2.55+3.6*t*t),-.25-5.2*t])
 pts=np.array(pts);area=np.sum(pts[:,0]*np.roll(pts[:,1],-1)-pts[:,1]*np.roll(pts[:,0],-1));pts=pts if area>0 else pts[::-1];wall=mf.CrossSection([pts]).extrude(.65).translate([0,0,-.18]);add('Curved low ramp wing',wall,5,'Observed curved flared low walls, curve normalized; no exact civil engineering claim')
 add('Rounded wing end',mf.Manifold.cylinder(.70,.45,.45,32).translate([side*5.98,-5.45,-.20]),5,'Rounded termination visible in photo')
# Drainpipes at outer edges of entry section, no unseen routes.
for x in [-5.8,5.8]:rod('Visible downpipe',[x,-.35,.15],[x,-.35,10.72],.075,1,'Visible vertical downpipe simplified, hidden connections omitted')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.001).simplify(.001)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v=np.round(v,4) # 0.0001mm export grid; STL reload verified independently
v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
used,inv=np.unique(f,return_inverse=True);v=v[used];f=inv.reshape(-1,3)
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='HCHS historical hall entrance');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Photo-informed central entrance slice ONLY,2023officialphoto; main gable roof/wider facade/unseenrear omitted, artificial backing; not wholehall.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
