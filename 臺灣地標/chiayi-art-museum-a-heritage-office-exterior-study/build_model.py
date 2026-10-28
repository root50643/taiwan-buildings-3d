#!/usr/bin/env python3
"""Chiayi Art Museum A heritage office only, source-limited exterior study."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [('wall','Brown scratch brick approximation','#A3947C','Official2021photos, not calibratedcolor or individualtiles'),('roof','Roof walking surface','#AAA99F','Official A aerial flatroof'),('glass','Opaque window infill','#344E4A','Solid print proxy, not transparentglass'),('frame','Green painted window frames','#509C87','Officialphotos greenframes'),('trim','Pale stone horizontal trims','#B8A68A','Official roundedcanopy and facade bands'),('base','Authored display support','#B8B8AF','Authorednottrueground'),('metal','Dark metalwork','#4C5351','Photographed drains'),('rail','Pale painted roof stair','#D8DAD6','Official A aerial white stair')]]
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


# Plan traced from source3F1080x763pixels; approx44px=5m, crosschecked official1F0-10mbar.
L=270*5/44;D=200*5/44;R=70*5/44;SW=110*5/44;MW=110*5/44;JW=160*5/44;JD=140*5/44;TD=165*5/44
pts=[[R,0],[L,0],[L,MW],[JW,MW],[JW,JD],[SW,JD],[SW,TD],[0,TD],[0,R]]
pts += [[R+R*math.cos(t),R+R*math.sin(t)] for t in np.linspace(math.pi,1.5*math.pi,25)[1:]]
cs=mf.CrossSection([(np.array(pts)*100).tolist()]);H=13.05
bx('Authored display plinth',[-3,-3,-.6],[L+1,D+1,0],5,'Authored display support, not actualsite')
# Firstfloor doorway setback; upperfloors span over entry asplan/photo.
notch=box([SW,-.1,0],[JW,3.2,4.35])
add('Lower A wall footprint',cs.extrude(435)-notch,0,'1Fplan recessed mainentry; otherinterior solid')
add('Upper A footprint',cs.extrude((H-4.3)*100).translate([0,0,430]),0,'3Fplan Lshape roundedcorner and steppedcourtyard, not1F extrusion')
# Rear short-wing terminal has lowerterrace atthirdfloor, not fullheight.
bx('Short terminal twofloor wing',[0,TD-.02,0],[SW,D,8.8],0,'Official3F terrace and aerial')
bx('Terrace walking surface',[.25,TD,8.78],[SW-.25,D-.25,8.88],1,'Official aerial terrace')
# Main rooftop surface and continuous curvedparapet, open roof not addedroom.
add('Main flatroof surface',cs.offset(-25).extrude(12).translate([0,0,(H-.02)*100]),1,'4Fplan A area isroof, not occupied4F')
ring=cs.offset(0)-cs.offset(-28)
add('Main roof parapet',ring.extrude(125).translate([0,0,(H-.03)*100]),0,'Officialaerial high continuous parapet includingroundedcorner')
add('Parapet coping', (cs.offset(10)-cs.offset(-35)).extrude(10).translate([0,0,(H+1.18)*100]),4,'Pale roundedcontinuous roofedge trim')
for a,b in [([0,TD,8.78],[.28,D,9.9]),([SW-.28,TD,8.78],[SW,D,9.9]),([0,D-.28,8.78],[SW,D,9.9])]:bx('Terrace parapet'+str(a),a,b,0,'Official aerial threeedge terraceparapet')
# Horizontal bands follow curvedoutside; upperroof bands distinctfromfloors.
for z in [3.95,8.15,12.35]:
 outer=cs.offset(22)-cs.offset(-15)
 add('Facade continuous horizontal belt'+str(z),outer.extrude(14).translate([0,0,z*100]),4,'Photographed projectinghorizontal bands, not additionalfloors')
# Local x tangent, localy wall inward. Solidglass and coarse2x4frame.
def localpart(name,a,b,mat,px,py,ang,evidence):add(name,box(a,b).rotate([0,0,ang]).translate([px*100,py*100,0]),mat,evidence)
def win(name,px,py,ang,z,w=1.12,h=2.05,rows=4,vent=True):
 def q(s,a,b,m):localpart(name+s,a,b,m,px,py,ang,'Officialphotos windowframe rhythm; positions and divisions approximate')
 q(' glass',[-w/2,-.075,z],[w/2,.12,z+h],2)
 for x in [-w/2,0,w/2]:q(' jamb'+str(x),[x-.035,-.12,z-.035],[x+.035,.16,z+h+.035],3)
 for zz in np.linspace(z,z+h,rows+1):q(' rail'+str(zz),[-w/2-.035,-.14,zz-.035],[w/2+.035,.16,zz+.035],3)
 if vent:
  q(' lower vent',[-.40,-.08,z-.62],[.40,.12,z-.22],2)
  for xx in [-.3,-.1,.1,.3]:q(' ventbar'+str(xx),[xx-.025,-.13,z-.59],[xx+.025,.13,z-.25],3)
  for zz in [z-.59,z-.42,z-.25]:q(' ventline'+str(zz),[-.38,-.16,zz-.025],[.38,.13,zz+.025],3)
# Streetlongwing; doorway atmiddle lowerfloor deliberatelynotwindow.
for i,x in enumerate([8.9,11.05,13.2,15.35,17.5,20.7,22.3,24.5,26.7,28.9]):
 for floor,z in enumerate([1.3,5.5,9.7]):
  if floor==0 and SW-.2<x<JW+.2:continue
  win('Streetlong window'+str((i,floor)),x,0,0,z)
  win('Streetlong highlight'+str((i,floor)),x,0,0,z+2.9,1.12,.48,1,False)
# Shortwingstreet x=0; terminalrearonlytwofloors.
for i,y in enumerate([9.3,11.6,13.9,16.2,18.5,20.8]):
 for floor,z in enumerate([1.3,5.5,9.7]):
  if floor==2 and y>TD-.5:continue
  if floor==0 and 13.5<y<15.5:continue
  win('Shortstreet window'+str((i,floor)),0,y,-90,z)
  win('Shortstreet highlight'+str((i,floor)),0,y,-90,z+2.9,1.12,.48,1,False)
# Curvedcorner tangentwindows, maintain outwardcurving actual silhouette.
for deg in [192,211,230,249,266]:
 t=math.radians(deg);x=R+R*math.cos(t);y=R+R*math.sin(t)
 for floor,z in enumerate([1.3,5.5,9.7]):
  win('Curvedcorner window'+str((deg,floor)),x,y,deg+90,z,1.05,2.05)
  win('Curvedcorner highlight'+str((deg,floor)),x,y,deg+90,z+2.9,1.05,.48,1,False)
# Visible courtyardlongface and steppedinnercorner. B jointx=L leftplain.
for i,x in enumerate([19.3,21.6,23.9,26.2,28.5]):
 for floor,z in enumerate([1.3,5.5,9.7]):
  win('Courtyard longwindow'+str((i,floor)),x,MW,180,z,.95,2.0)
  win('Courtyard highlight'+str((i,floor)),x,MW,180,z+2.9,.95,.48,1,False)
for y in [16.6,18.0,20.2,21.8]:
 for floor,z in enumerate([1.3,5.5,9.7]):
  if floor==2 and y>TD-.4:continue
  win('Courtyard shortwindow'+str((y,floor)),SW,y,90,z,.8,1.9)
# Rearterminal face supported aerial / officialnearphoto, mixednarrowlights simplified.
for x in [2.,4.3,6.6,9.,10.8]:
 for floor,z in enumerate([1.3,5.5]):win('Terminalrear window'+str((x,floor)),x,D,180,z,.8 if x>8 else 1.1,1.9)
# Shallowverticalpilasters on visible streets, and drainpipes.
for x in [7.9,18.7,25.6]:bx('Street pilaster'+str(x),[x-.10,-.14,0],[x+.10,.15,H],0,'Photographed vertical masonry piers, coarsened')
for y in [8.3,14.8]:bx('Short pilaster'+str(y),[-.14,y-.10,0],[.15,y+.10,H],0,'Visible facade piers')
for x in [8.2,18.5,30.0]:add('Street drain'+str(x),beam([x,-.22,.1],[x,-.22,H-.4],.065),6,'Photographed dark drainpipes')
# Main recessdoor and large curvedcorner canopy withthreefine projectingedges.
win('Recessed mainentry door',(SW+JW)/2,3.00,0,.65,2.9,3.0,3,False)
for j in range(5):bx('Mainentry step'+str(j),[SW+.4,-1+j*.7,0],[JW-.4,3.2,.15*(j+1)],4,'Photographed raisedbase stair, steprhythm approximate')
can=mf.CrossSection.square([((JW-SW)+2)*100,360]).offset(-25).offset(25).translate([(SW-1)*100,-190])
for z,dh,off in [(4.18,.16,0),(4.30,.12,5),(4.39,.14,0)]:add('Roundedentry canopy layer'+str(z),can.offset(off).extrude(dh*100).translate([0,0,z*100]),4,'Officialentry photo broadrounded canopy steppededge')
# Rounded doorwaycheeks are modeled coarsely, supportedphoto, no decorativelettering.
for x in [SW,JW]:
 cheek=mf.Manifold.cylinder(420,65,65,32).translate([x*100,30,0])
 add('Roundedentry cheek'+str(x),cheek,0,'Entryphoto curvedwallcheek, approximate radius')
# Arched green smallwindow clearly visible beside mainentry, solidbacked coarse lattice.
aw=.85;zb=1.25;spring=2.45;rise=.52
ap=[(-aw/2,zb),(aw/2,zb),(aw/2,spring)]+[(aw/2*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(0,math.pi,17)[1:]]
ac=mf.CrossSection([(np.array(ap)*100).tolist()])
def archface(cs,depth):return cs.extrude(depth*100).rotate([90,0,0]).translate([(JW+1.1)*100,4,0])
add('Entry arched smallwindow darkglass',archface(ac,.10),2,'Officialentry rightcheek arched green latticewindow')
add('Entry arched greenborder',archface(ac.offset(5)-ac.offset(-4),.16),3,'Visible arched greenwindowframe, thickened')
for x in [-.22,0,.22]:
 bx('Archedwindow verticalbar'+str(x),[JW+1.1+x-.025,-.13,zb],[JW+1.1+x+.025,.05,spring+.22],3,'Coarse lattice proxy, not exact diamond mesh')
for z in [1.55,1.9,2.25,2.55]:bx('Archedwindow crossbar'+str(z),[JW+.70,-.14,z-.025],[JW+1.50,.05,z+.025],3,'Coarse arched lattice')
# Photographed secondentry on shortstreet with smaller roundedcanopy.
win('Secondary streetdoor',0,14.5,-90,.75,1.7,2.8,3,False)
bx('Secondary entry support',[-1.1,13.2,0],[.1,15.8,.65],4,'Raisedsecondary threshold')
add('Secondary canopy',mf.CrossSection.square([240,350]).offset(-20).offset(20).extrude(22).translate([-210,1280,420]),4,'Visible secondary projectingcanopy')
# White external stair connects lower rear terrace to mainroof; solid support forprint.
for j in range(18):
 y=D-.5-j*.2;bx('Roof access stair'+str(j),[5.1,y,8.8],[6.25,y+.22,8.95+j*.235],7,'Aerial white external stair, coarsened withsolid support')
for x in [5.1,6.25]:
 add('Stair sloping handrail'+str(x),beam([x,D-.4,9.9],[x,TD-.1,14.0],.055),7,'Aerialwhite stairrail, thickened')
 for j in range(0,18,3):
  y=D-.4-j*.2;bx('Stair railpost'+str((x,j)),[x-.04,y-.04,8.85+j*.235],[x+.04,y+.04,9.95+j*.235],7,'Simplifiedrailposts')
# Rooftoppipe and sparse scoredpanel joints; not complete pavingdetail.
add('Photographed roof ventstack',mf.Manifold.cylinder(280,14,14,20).translate([135,1660,(H-.1)*100]),0,'Aerialsingle visible ventstack approximateplacement')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.2).simplify(.2)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Chiayi Art Museum A heritage office exterior study');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'A heritage office only; officialscaled1F and architect3F/roofplans plus2021photos. Approximate dimensions, no B/C or interiors, B joint unmodeled, no trialprint'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
