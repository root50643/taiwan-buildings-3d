#!/usr/bin/env python3
"""Chiayi Art Museum B new wing only, source-limited exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','Grey facade panels','#9A9992','Completed architect and official photographs, uncalibrated'),('frame','Pale window box rims','#B6B5A9','Photographed projecting window boxes, coarse approximation'),('glass','Recessed opaque glazing proxy','#476061','Manufacturing proxy; not transparent material'),('roof','Pale roof and terrace','#BABCB4','Aerial completed photograph'),('metal','Dark facade framework','#535E59','Photographed narrow vertical and horizontal divisions'),('base','Authored display plinth','#B8B8AF','Authored support, not actual ground'),('timber','Coarse atrium structural proxy','#AD9873','Photographed wood-colored structure, not engineering reconstruction'),('dark','Shadow inset','#343D3A','Small dark facade openings')]]
SCALE=.05
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



# Coordinates traced from 3F plan1080x763;5m/44px approximated, not surveyed.
# Rotate streetedge into model x so one unit represents one approximate source metre.
origin=np.array([601.,610.]); ex=np.array([313.,-95.]);ex/=np.linalg.norm(ex);ey=np.array([ex[1],-ex[0]])
def xy(p):
 q=np.array(p)-origin;return np.array([q@ex,q@ey])*5/44
pix=[(601,610),(914,515),(927,507),(937,495),(943,480),(942,466),(936,452),(925,438),(800,305),(590,505)]
pts=[xy(p).tolist()for p in pix]
def cross(pp):
 pp=np.array(pp);area=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-pp[:,1]*np.roll(pp[:,0],-1));pp=pp if area>0 else pp[::-1];return mf.CrossSection([(pp*100).tolist()])
cs=cross(pts); H=14.22;top=18.17
mn=np.min(pts,axis=0);mx=np.max(pts,axis=0)
bx('Authored display plinth',[mn[0]-2,mn[1]-2,-.6],[mx[0]+2,mx[1]+2,0],5,'Authored support, not site map')
# Shallow courtyard cavity, not through-building atrium; preserving shadow/depth and framework.
ca=xy((590,505));cb=xy((800,305));dt=cb-ca;length=np.linalg.norm(dt);u=dt/length;n=np.array([u[1],-u[0]])
# n points into streetmass; ensure midpoint inward.
if (xy((790,470))-(ca+cb)/2)@n<0:n=-n
channel=[ca-u*.1-n*.3,cb+u*.1-n*.3,cb+u*.1+n*1.8,ca-u*.1+n*1.8]
cut=cross(channel).extrude(1800).translate([0,0,58])
add('Lower three-level mass with shallow courtyard recess',cs.extrude(H*100)-cut,0,'3F wedge outline; internal floors not reconstructed; recess is display proxy')
# Rooflevel salon and court-side upper envelope; alongstreet terrace stays open.
upper=[xy(p).tolist()for p in [(590,505),(800,305),(840,470),(650,532),(665,580),(610,598)]]
ucs=cross(upper)
add('Recessed fourthlevel roof mass',ucs.extrude((top-H)*100).translate([0,0,H*100])-cut,0,'4F plan20/21 separates upperroom and open streetterrace')
add('Thin main roof overhang',ucs.offset(24).extrude(20).translate([0,0,top*100-5]),3,'Publishedsection RF+18.17 and completed aerial thin overhangingroof')
# Top terrace surface and street screen parapet, elevated but open atsky.
add('Open 4F terrace walking surface',(cs-ucs).extrude(12).translate([0,0,(H-.02)*100]),3,'4Fplan21/22 uncovered terraces; no false fullheightvolume')
# Perimeter streetfaces from longedge through roundedcorner to Cjoint.
def loc(name,a,b,mat,p,angle,evidence):add(name,box(a,b).rotate([0,0,angle]).translate([p[0]*100,p[1]*100,0]),mat,evidence)
segments=[]
for i in range(8):
 aa=np.array(pts[i]);bb=np.array(pts[i+1]);d=bb-aa;l=np.linalg.norm(d);angle=math.degrees(math.atan2(d[1],d[0]));segments.append((aa,bb,l,angle))
 for z in [.5,5.06,9.55,14.22]:
  loc('Street horizontal levelband'+str((i,z)),[0,-.16,z-.09],[l,.17,z+.09],4,aa,angle,'Photographed levelbands; section relative GL datum')
 loc('Street upper terrace screen'+str(i),[0,0,H-.05],[l,.28,17.4],0,aa,angle,'Open 4F terrace edge height visually estimated, not RF+18.17')
 loc('Terrace edge coping'+str(i),[0,-.1,17.33],[l,.32,17.47],4,aa,angle,'Photographed streetedge coping')
 # Fine vertical facade grid approximated on solid wall, no tinyperforations.
 for x in np.linspace(0,l,max(2,round(l/.95)+1)):
  loc('Vertical facade mullion'+str((i,float(x))),[x-.035,-.19,.4],[x+.035,.1,17.44],4,aa,angle,'Visible dense vertical divisions; coarse solid backed ribs')
# Streetfront irregular window sizes, including low smallmouths rather than regular grid.
def window(name,aa,ang,x,z,w,h):
 ev='Completed facadephoto mixed narrow/wide projecting windowboxes; dimensions coarse'
 loc(name+' shadow',[x-w/2,-.11,z],[x+w/2,.12,z+h],2,aa,ang,ev)
 # Thick rectangular rims approximate sloped reveal, no measured bevel claim.
 for xx in [x-w/2,x+w/2]:loc(name+' box jamb'+str(xx),[xx-.065,-.30,z-.06],[xx+.065,.16,z+h+.06],1,aa,ang,ev)
 for zz in [z,z+h]:loc(name+' box sill'+str(zz),[x-w/2-.07,-.32,zz-.06],[x+w/2+.07,.17,zz+.06],1,aa,ang,ev)
 # one visible inset edge adds coarse depth
 loc(name+' inset lower',[x-w/2+.05,-.19,z+.05],[x+w/2-.05,.13,z+.12],4,aa,ang,ev)
for si in [0,7]:
 aa,bb,l,ang=segments[si]
 for fl,z0 in enumerate([.5,5.06,9.55]):
  for j,f in enumerate([.08,.145,.215,.29,.41,.56,.72,.87]):
   w=1.05 if j<4 or j==6 else min(3.4,l*.10);h=2.05 if j<4 or j==6 else 1.5
   window('Street mixed box'+str((si,fl,j)),aa,ang,l*f,z0+(1.0 if (j+fl)%3 else 1.35),w,h)
  for j,f in enumerate([.08,.145,.215,.29,.49,.72,.92]):
   loc('Low dark slot'+str((si,fl,j)),[l*f-.36,-.115,z0+.3],[l*f+.36,.12,z0+.64],7,aa,ang,'Photographed low ventilation/window slots; coarse placement')
 for j,f in enumerate([.08,.145,.215,.29,.41,.56,.72,.87]):
  loc('Upper terrace lowlight'+str((si,j)),[l*f-.4,-.11,H+.2],[l*f+.4,.12,H+.53],7,aa,ang,'Photographed upper screen small lowopenings')
# Curve has fewer distinct bays; no windows at everytinyfacet.
for si in [2,4,6]:
 aa,bb,l,ang=segments[si]
 for fl,z0 in enumerate([.5,5.06,9.55]):window('Roundedcorner box'+str((si,fl)),aa,ang,l*.5,z0+1.1,min(1.2,l*.75),1.65)
# 4F salon glazing faces open terrace, according to plan20/21 and section.
ua=xy((650,532));ub=xy((840,470));ud=ub-ua;ul=np.linalg.norm(ud);uang=math.degrees(math.atan2(ud[1],ud[0]))
loc('Upper salon terrace glazing',[0,-.09,H+.2],[ul,.12,top-.25],2,ua,uang,'4F plan salon/terrace boundary; opaque glazing proxy')
for x in np.linspace(0,ul,13):loc('Upper salon mullion'+str(x),[x-.045,-.15,H+.15],[x+.045,.15,top-.2],4,ua,uang,'Coarse 4F salon window rhythm, not surveyed divisions')

# Courtyard frame proud of shallowrecess, with dark infill behind. Not internal structural reconstruction.
angle=math.degrees(math.atan2(u[1],u[0])); outward=-n
# general world facade strip helper alongca->cb; local yleftnormal may point opposite n
left=np.array([-u[1],u[0]]);sgn=1 if left@n>0 else -1
for i,tv in enumerate(np.linspace(.15,length-.15,max(3,round(length/2.3)+1))):
 p=ca+u*tv
 add('Courtyard fullheight mullion'+str(i),beam([p[0],p[1],.45],[p[0],p[1],top+.05],.075),4,'Completed courtyard curtainwall coarse verticalgrid')
for z in [.55,3.0,5.06,7.3,9.55,11.8,14.22,16.2,18.10]:
 add('Courtyard horizontal grid'+str(z),beam([*ca,z],[*cb,z],.06),4,'Photographed curtainwall grid, rounded coarse frame')
# Recessedback glazing fills only backof1.8mshowcase, so main glass front is omitted deliberately.
back=[ca+n*1.7,cb+n*1.7,cb+n*1.86,ca+n*1.86]
add('Opaque recessed courtyard glazing',cross(back).extrude((top-.6)*100).translate([0,0,58]),2,'Disclosed 1.7m shallowdepth proxy, no actual transparency or complete atrium')
# Coarse timber-colored vertical supports within recessedgap, from photo butnot surveyed structural spacing.
for t in np.linspace(2,length-2,6):
 p=ca+u*t+n*1.35
 add('Atrium pale vertical structural proxy'+str(t),beam([*p,.5],[*p,top-.05],.13),6,'Visible timber-colored supports simplified; not structural engineering model')
# Courtyard entrance canopy near middle, connected into facade body through recesseddepth.
p=ca+u*(length*.55);ev='Aerial courtyard projecting glass/metal entrycanopy coarse solid printproxy'
can=[p-u*3-n*2,p+u*3-n*2,p+u*3+n*2,p-u*3+n*2]
add('Courtyard entry canopy',cross(can).extrude(18).translate([0,0,390]),4,ev)
for t in [-2.7,2.7]:
 pp=p+u*t-n*1.65;add('Canopy support'+str(t),beam([*pp,.05],[*pp,4.0],.09),4,'Coarse supportedcanopy for printing, supportplacementapproximate')
# Entrance door is on recessed glazing backing, not an unsupported invented opening.
doorp=p+n*1.52; doorang=angle if sgn>0 else angle+180
window('Courtyard recessed entry door',doorp,doorang,0,.55,3.2,3.0)
loc('Entry double door centre stile',[-.055,-.35,.55],[.055,.2,3.6],1,doorp,doorang,'Visible entry double door, coarse frame')
loc('Entry transom',[-1.6,-.36,2.95],[1.6,.2,3.05],1,doorp,doorang,'Visible glazed entry transom, approximate position')

# Rooflong strip from completed aerial, not labeled equipment function without evidence.
mid=(ca+cb)/2+n*4; rr=[mid-u*6-n*.55,mid+u*6-n*.55,mid+u*6+n*.55,mid-u*6+n*.55]
add('Visible roof longitudinal raised strip',cross(rr).extrude(90).translate([0,0,top*100]),3,'Completed aerial longroofraisedcomponent, details/function notasserted')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.2).simplify(.2)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Chiayi Art Museum B new wing exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'B new wing only; published floorplans/section and completed photographs. Approximate plan dimensions, shallow opaque atrium proxy, no interiors or A/C, no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
