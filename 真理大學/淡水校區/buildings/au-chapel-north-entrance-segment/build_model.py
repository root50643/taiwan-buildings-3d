#!/usr/bin/env python3
"""Aletheia University chapel north entrance segment; all dimensions photo-estimated, not a survey."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('stone','Grey stone facing','#969991','Official chapel exterior photo, uncalibrated'),
 ('brick','Muted orange brick','#A96948','Official exterior photo tower vertical strips and upper band'),
 ('glass','Opaque dark aperture','#283839','Solid dark inlay approximation, not transparent glazing'),
 ('roof','Charcoal roof','#565F61','Official exterior photo visible hipped faceted caps'),
 ('base','Authored display base','#B8BBB2','Author-created support, not actual site geometry'),
 ('cut','Unevidenced cut face','#D3D4CE','Explicitly authored cropped rear termination')]]
SCALE=6.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photograph-proportioned visible detail; dimensions estimated'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
# Local front is y=0; positive y is into church. Model explicitly ends at y=5.6.
# x spans a nominal 24 m; none of these units are a measured building dimension.
import math

def ngon(cx,cy,r,z0,z1,mat,name,n=8):
 pts=[(cx+r*math.cos(math.pi/8+2*math.pi*i/n),cy+r*math.sin(math.pi/8+2*math.pi*i/n))for i in range(n)]
 poly(name,pts,z0,z1,mat,'Visible faceted tower lantern; polygon proportions estimated')
def taper(cx,cy,r0,r1,z0,z1,mat,name):
 # Convex eight-sided frustum, exact authored polygon, no fictitious as-built dimensions.
 v=[(cx+r*math.cos(math.pi/8+2*math.pi*i/8),cy+r*math.sin(math.pi/8+2*math.pi*i/8),z)for z,r in [(z0,r0),(z1,r1)]for i in range(8)]
 f=[]
 for i in range(1,7):f.append((0,i+1,i));f.append((8,8+i,8+i+1))
 for i in range(8):j=(i+1)%8;f.extend([(i,j,8+j),(i,8+j,8+i)])
 add(name,mf.Manifold(mf.Mesh(np.array(v,dtype=np.float32),np.array(f,dtype=np.uint32))),mat,'Faceted cap/taper visible in official photo; slopes and heights estimated')
def arch(cx,y,z,w,h,mat,name,depth=.12):
 # Pointed low relief; solid inlay, deliberately not a thin open hole.
 pts=[(cx-w/2,z),(cx+w/2,z),(cx+w/2,z+h*.65),(cx+w*.27,z+h*.87),(cx,z+h),(cx-w*.27,z+h*.87),(cx-w/2,z+h*.65)]
 depth=max(depth,.45)
 sh=mf.CrossSection([pts]).extrude(depth).rotate([90,0,0]).translate([0,y+depth,0])
 add(name,sh,mat,'Visible pointed aperture, solid closed inlay; no interior reconstruction')
def side_arch(yc,x,z,w,h,mat,name):
 pts=[(yc-w/2,z),(yc+w/2,z),(yc+w/2,z+h*.65),(yc+w*.27,z+h*.87),(yc,z+h),(yc-w*.27,z+h*.87),(yc-w/2,z+h*.65)]
 sh=mf.CrossSection([pts]).extrude(.45).rotate([90,0,90]).translate([x,0,0])
 add(name,sh,mat,'Visible left exterior tower pointed aperture, solid inlay; side positions estimated')
def circle_front(cx,y,z,r,mat,name):
 sh=mf.Manifold.cylinder(.6,r,r,32).rotate([90,0,0]).translate([cx,y+.6,z])
 add(name,sh,mat,'Circular upper tower aperture visible in school photo; solid color inlay')
# Authored base and shallow rear wall ensure connected solid but are not alleged full building.
bx('Authored base',[-.8,-1,-.6],[24.8,6.2,0],4,'Display support only')
bx('Entrance wall behind porch',[4.8,2.3,0],[19.2,5.6,13.5],0,'Front entrance wall from photograph; rear at5.6 is an explicit authored cutoff')
bx('Explicit rear crop termination',[0,5.48,0],[24,5.6,13.5],5,'Author-created straight cut boundary, not church back wall or actual plan')
for cx in [2.5,21.5]:
 bx('Square lower tower '+str(cx),[cx-2.5,0,0],[cx+2.5,5.6,15.6],0,'Front twin square towers visible; depth cropped, not measured')
 # Brick corner piers visible framing stone shaft.
 for x in [cx-2.45,cx+1.95]:bx('Brick corner pier',[x,-.065,0],[x+.5,.10,10.0],1,'Front brick vertical accents visible on tower corners')
 for z in [1.4,5.8,9.8,14.9]:bx('Stone tower horizontal course',[cx-2.55,-.12,z],[cx+2.55,.15,z+.25],0,'Strong horizontal stone bands, simplified from facade photo')
 # Tower front pointed openings, upper and ground; broad gray frame then dark inner inlay.
 arch(cx,-.07,.7,2.3,4.5,3,'Lower pointed stone reveal',.12)
 arch(cx,-.20,.85,1.65,3.95,2,'Ground tower opaque opening',.10)
 arch(cx,-.07,9.6,2.6,4.0,3,'Upper pointed stone reveal',.12)
 arch(cx,-.20,9.8,1.85,3.45,2,'Upper tower opaque opening',.10)
 # Shoulder tapers to octagonal lantern, cap octagon is a readable photo-based approximation.
 taper(cx,2.65,2.72,1.92,15.4,19.0,0,'Tapered stone tower shoulder')
 # Orange panels at shoulder center indicated in front photograph.
 bx('Brick shoulder central panel',[cx-1.2,.36,16.25],[cx+1.2,.58,18.1],1,'Visible orange central patch around round aperture; simplified rectangle, not masonry pattern')
 circle_front(cx,.27,17.2,.72,0,'Circular stone rim')
 circle_front(cx,.10,17.2,.48,2,'Round dark shoulder aperture')
 ngon(cx,2.65,1.93,18.85,20.65,1,'Octagonal brick lantern')
 ngon(cx,2.65,2.04,18.85,19.08,0,'Lantern lower grey belt')
 ngon(cx,2.65,2.04,20.35,20.62,0,'Lantern upper grey belt')
 arch(cx,.86,19.20,.68,.94,2,'Lantern small front pointed aperture',.1)
 taper(cx,2.65,2.18,.1,20.58,22.15,3,'Faceted charcoal tower cap')
 ngon(cx,2.65,.26,21.98,22.6,0,'Small terminal finial')
# Only the outer left tower face is clearly evidenced in the school oblique photo.
side_arch(2.6,-.12,9.6,2.6,4.0,3,'Left tower side pointed reveal')
side_arch(2.6,-.24,9.8,1.85,3.45,2,'Left tower side opaque window')
side_arch(2.6,-.12,.7,2.3,4.5,3,'Left tower ground side reveal')
side_arch(2.6,-.24,.85,1.65,3.95,2,'Left tower ground side opaque aperture')
# Large front bridge-like clerestory with seven small pointed openings.
bx('Upper front panel',[4.9,0,10.65],[19.1,2.5,14.5],0,'Seven-window upper front panel visible over porch')
for i in range(7):
 cx=6.0+i*2.0
 arch(cx,-.08,11.5,.9,1.95,3,'Small clerestory reveal '+str(i+1),.12)
 arch(cx,-.21,11.65,.57,1.6,2,'Seven clerestory windows '+str(i+1),.10)
bx('Upper front low roof edge',[4.75,-.15,14.4],[19.25,2.5,14.72],3,'Visible dark straight roof cornice; full triangular church roof omitted')
bx('Porch lintel stone ledge',[4.65,-.35,10.25],[19.35,2.55,10.7],0,'Broad porch horizontal cornice visible under7windows')
bx('Porch dark underside edge',[4.72,-.42,10.15],[19.28,.2,10.32],3,'Shadowed thin lower porch cornice')
# Four visible robust piers, nominal placement from photograph, not structural plans.
for x in [5.8,9.0,15.0,18.2]:
 bx('Porch brick pier '+str(x),[x-.32,.45,0],[x+.32,1.05,10.3],1,'Visible brick porch support rhythm; count/position photo-proportioned')
 bx('Porch pier stone foot '+str(x),[x-.43,.34,0],[x+.43,1.16,.6],0,'Simplified base visually observed')
# Recessed central pointed entry and two subsidiary side openings.
arch(12,2.25,.25,3.2,6.9,3,'Central entry stone reveal',.14)
arch(12,2.10,.4,2.35,5.95,2,'Central entry opaque door',.11)
bx('Door mullion',[11.92,1.93,.4],[12.08,2.17,5.0],0,'Central vertical door divider visible')
for x in [7.5,16.5]:
 arch(x,2.24,.4,1.35,4.1,3,'Subsidiary pointed frame',.14)
 arch(x,2.09,.55,.85,3.45,2,'Subsidiary opaque opening',.1)
# Site trees, people, planting, lettering, full nave and unseen rear roof deliberately omitted.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
v, inv=np.unique(v,axis=0,return_inverse=True);f=inv[f]
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)*.5
keep=area>1e-9;f=f[keep];mi=mi[keep]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='AU chapel north twin-tower entrance segment');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Official chapel facade photograph: front twin-tower and porch segment only. All dimensions estimated; rear plane is authored crop. No full nave, interior or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
