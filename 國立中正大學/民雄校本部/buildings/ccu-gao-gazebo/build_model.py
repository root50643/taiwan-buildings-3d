#!/usr/bin/env python3
"""CCU Gao gazebo: simplified six-sided raised timber pavilion from official navigation photos, dates unknown."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
('wood','Dark weathered timber posts','#554A35','Official navigation three-photo set, uncalibrated'),
('rail','Weathered warm wood rails','#78694D','Visible natural log rails'),
('thatch','Gray brown thatch roof','#958C74','Visible thick pale-brown thatch canopy, fibers not reconstructed'),
('eave','Shadowed thatch eave band','#776E56','Thick hanging edge abstracted as continuous skirt'),
('deck','Weathered timber deck','#897F69','Visible raised plank deck, seam count simplified'),
('step','Pale weathered step boards','#A5A48F','Five pale entry treads visible'),
('base','Authored neutral display support','#B2B2A6','Support footprint not surveyed ground or foundation')]]
SCALE=12.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-proportioned visible feature; nominal dimensions'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):
 if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))<0:pts=list(reversed(pts))
 add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
# Six visible main posts; regular hexagon is a photo-proportioned approximation.
angles=[math.radians(i*60)for i in range(6)]
def pts(r):return [(r*math.cos(a),r*math.sin(a))for a in angles]
def rod(a,b,r,n=16):
 a=np.array(a,float);b=np.array(b,float);d=b-a;l=np.linalg.norm(d);yaw=math.degrees(math.atan2(d[1],d[0]));tilt=math.degrees(math.acos(d[2]/l))
 return mf.Manifold.cylinder(l+.025,r,r,n).rotate([0,tilt,yaw]).translate(a.tolist())
def beam(name,a,b,r,mat=1,e='Visible round timber structure; nominal size'):add(name,rod(a,b,r),mat,e)
poly('Authored display support',[(-6.6,-7.7),(6.6,-7.7),(6.6,6.2),(-6.6,6.2)],-.6,-.4,6,'Neutral support connects feet; not real ground or site perimeter')
poly('Raised six-sided timber floor',pts(4.95),.9,1.25,4,'Six-sided high timber platform visible; regularized dimensions')
P=pts(4.65)
for i,(x,y)in enumerate(P):
 add('Main round timber post '+str(i+1),mf.Manifold.cylinder(6.30,.18,.18,24).translate([x,y,-.45]),0,'Six main log posts visible across three official angles; size and circular sections simplified')
 # Vertical supports connect deck to base; no invented stone feet.
for i in range(6):
 a=P[i];b=P[(i+1)%6]
 beam('Upper perimeter log beam',(*a,5.65),(*b,5.65),.15,0)
 beam('Underfloor perimeter bearer',(*a,.95),(*b,.95),.17,0)
# Entry in the left half of the near side, matching navigation entrance photographs.
for i in range(6):
 a=np.array(P[i]);b=np.array(P[(i+1)%6]); intervals=[(0,1)]
 if i==4:intervals=[(.56,1)]
 for t0,t1 in intervals:
  u=a+(b-a)*t0;v=a+(b-a)*t1
  for z in [1.5,2.5]:beam('Simplified perimeter horizontal rail',(*u,z),(*v,z),.085,1,'Visible two horizontal rail levels, dimensions approximate')
  for t in np.linspace(t0,t1,5):
   q=a+(b-a)*t;beam('Regularized vertical railing',(*q,1.27),(*q,2.53),.065,1,'Four regularly spaced railing divisions per retained full/partial bay; exact source count not asserted')
# Five tread boards and two stringers; no hidden riser walls invented.
x0=-2.30;x1=.13;edge=P[4][1]
for j in range(5):
 y=edge-2.65+j*.49;z=.08+j*.215
 bx('Entry tread '+str(j+1),[x0,y,z],[x1,y+.50,z+.14],5,'Five separate pale wood treads visible in close official entrance photograph')
for x in [x0+.35,x1-.35]:beam('Stair stringer',[x,edge-2.72,-.24],[x,edge+.10,1.00],.12,0,'Two longitudinal tread supports visible; inclination approximate')
# Source navigation set shows one outer handrail; do not import different two-sided later rail state.
beam('Entry single handrail',[x0-.05,edge-2.75,.85],[x0-.05,edge+.02,2.45],.09,1,'Single clearly visible entry handrail retained from navigation source set')
beam('Entry handrail lower post',[x0-.05,edge-2.75,-.42],[x0-.05,edge-2.75,.9],.11,0)
# Six-sector thick thatch shell, rounded low apex, no invented individual fibers.
rings=[.10,.35,.8,1.5,2.5,3.6,4.7,5.6,6.25]
def zroof(r):return 4.90+4.0*(1-(r/6.25)**1.15)
v=[]
for lower in [0,1]:
 for r in rings:
  for a in angles:v.append([r*math.cos(a),r*math.sin(a),zroof(r)-lower*.36])
f=[];N=len(rings);off=N*6
for layer in [0,1]:
 for j in range(N-1):
  for i in range(6):
   a=layer*off+j*6+i;b=layer*off+j*6+(i+1)%6;c=layer*off+(j+1)*6+(i+1)%6;d=layer*off+(j+1)*6+i
   f.extend([[a,c,b],[a,d,c]]if layer==0 else [[a,b,c],[a,c,d]])
for j in [0,N-1]:
 for i in range(6):
  a=j*6+i;b=j*6+(i+1)%6;f.extend([[a,b,b+off],[a,b+off,a+off]]if j==0 else [[a,b+off,b],[a,a+off,b+off]])
me=trimesh.Trimesh(np.array(v),np.array(f),process=True)
add('Six-slope thick thatch roof shell',mf.Manifold(mf.Mesh(np.asarray(me.vertices,dtype=np.float32),np.asarray(me.faces,dtype=np.uint32))),2,'Six roof slopes and thick thatch canopy visible; smooth profile and thickness approximated, not individual fibers')
poly('Continuous flat micro apex closure',pts(.14),8.50,zroof(.10),2,'Small six-sided flat closure continuous with roof shell; no separate ball or finial')
# Thick irregular-looking eave is abstracted as one continuous six-sided hanging band.
ring=mf.CrossSection([pts(6.25)])-mf.CrossSection([pts(6.05)])
add('Continuous hanging thatch eave abstraction',ring.extrude(.40).translate([0,0,4.53]),3,'Thick draped eave edge; irregular straw fibers deliberately omitted')
# Six visible roof support directions simplified, join to upper beams and roof shell.
for a in angles:
 beam('Simplified radial roof support',[0,0,8.55],[4.65*math.cos(a),4.65*math.sin(a),5.72],.12,0,'Principal radial supporting poles visible; detailed secondary rafters/rope joints omitted')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='CCU Gao gazebo simplified whole pavilion');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Undated official navigation-photo source-state whole simplified gazebo. Six main posts, six roof sectors and five entry treads supported; nominal dimensions, regularized rails, no joinery, landscape or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
