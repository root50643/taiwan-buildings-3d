#!/usr/bin/env python3
"""Lishan Jesus Church December2016 survey; authored exterior proxies, Appendix9 only."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=5.;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL;BASE=.4
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':'Uncalibrated display palette supported by2016 survey photos; not precise originalfinish'}for i,(n,c) in enumerate([('Survey pale stonewash','#D7D5BD'),('Cream trims','#E6E2C8'),('Aged copper roof proxy','#697A79'),('Window frames','#C7C9B9'),('Opaque glazing','#74898D'),('Blind recess backing','#313D42'),('Red repair sheet proxy','#8E5550'),('Neutral plinth','#A7A995'),('Authored display support','#CECCBC'),('Door brown','#74685B')])]
items=[];ops=[];cut_items=[];cut_ops=[];ids={}
def box(a,b):return mf.Manifold.cube(((np.array(b)-a)*INTERNAL).tolist()).translate((np.array(a)*INTERNAL).tolist())
def add(n,s,m,e):
 s=s.translate([0,0,BASE*INTERNAL]).as_original();ids[int(s.original_id())]=m;items.append(s);ops.append({'name':n,'material':m,'evidence':e})
def bx(n,a,b,m,e):add(n,box(a,b),m,e)
def cut(n,s,e):
 s=s.translate([0,0,BASE*INTERNAL]).as_original();ids[int(s.original_id())]=5;cut_items.append(s);cut_ops.append({'name':n,'material':5,'operation':'subtract','evidence':e})
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*INTERNAL).tolist())
def section(pts):
 p=np.array(pts,float)
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 return mf.CrossSection((p*INTERNAL)[None,:,:].tolist())
def faceprofile(cs,side,plane,depth):
 if side=='F':M=[[1,0,0,0],[0,0,-1,plane*INTERNAL],[0,1,0,0]]
 elif side=='B':M=[[1,0,0,0],[0,0,1,plane*INTERNAL],[0,1,0,0]]
 elif side=='L':M=[[0,0,-1,plane*INTERNAL],[1,0,0,0],[0,1,0,0]]
 else:M=[[0,0,1,plane*INTERNAL],[1,0,0,0],[0,1,0,0]]
 return cs.extrude(depth*INTERNAL).transform(M)
def panel(n,side,plane,u0,u1,z0,z1,d,m,e):add(n,faceprofile(section([[u0,z0],[u1,z0],[u1,z1],[u0,z1]]),side,plane-.025 if side in('B','R')else plane+.025,d+.025),m,e)
def gable_y(x0,x1,y0,y1,eave,ridge):return hull([[x0,y0,eave],[x1,y0,eave],[x0,y1,eave],[x1,y1,eave],[(x0+x1)/2,y0,ridge],[(x0+x1)/2,y1,ridge]])
def gable_x(x0,x1,y0,y1,eave,ridge):return hull([[x0,y0,eave],[x1,y0,eave],[x0,y1,eave],[x1,y1,eave],[x0,(y0+y1)/2,ridge],[x1,(y0+y1)/2,ridge]])
def beam(a,b,r,seg=8):
 a=np.array(a);b=np.array(b);v=b-a;le=np.linalg.norm(v);z=v/le;t=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(t,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return mf.Manifold.cylinder(le*INTERNAL,r*INTERNAL,r*INTERNAL,seg).transform(np.column_stack([x,y,z,a*INTERNAL]))
def outline(u,w,z,h,head='point',rise=.35):
 if head=='rect':pts=[[u-w/2,z],[u+w/2,z],[u+w/2,z+h],[u-w/2,z+h]]
 elif head=='round':
  rad=w/2;pts=[[u-w/2,z],[u+w/2,z]]+[[u+rad*math.cos(t),z+h-rad+rad*math.sin(t)]for t in np.linspace(0,math.pi,25)]
 else:pts=[[u-w/2,z],[u+w/2,z],[u+w/2,z+h-rise],[u,z+h],[u-w/2,z+h-rise]]
 return section(pts)
def shaped_panel(n,side,p,cs,depth,m,e):
 q=p+.025 if side in('F','L')else p-.025
 add(n,faceprofile(cs,side,q,depth+.025),m,e)
def window(n,side,p,u,w,z,h,head,cols,rows,rise=.35,body_h=None,rails=None):
 ev='Appendix9 surveyed opening; counts and detailtypes controlled byopening-positions.json; solid opaque glazing notcompleteinterior'
 cs=outline(u,w,z,h,head,rise);shaped_panel(n+' pale surround',side,p,cs.offset(.09*INTERNAL),.055,1,ev)
 shaped_panel(n+' opaque glazing',side,p,cs,.085,4,ev)
 # Profile-clipped mullions ensure pointed/arched heads follow measured silhouette.
 bars=[]
 for j in range(cols+1):
  x=u-w/2+w*j/cols;bars.append(section([[x-.025,z],[x+.025,z],[x+.025,z+h],[x-.025,z+h]]))
 # rows refers to body below head, not forcing square cells into its top.
 hh=body_h if body_h is not None else h-(w/2 if head=='round'else rise if head=='point'else 0)
 for rr in (rails if rails is not None else [hh*j/rows for j in range(rows+1)]):
  zz=z+rr;bars.append(section([[u-w/2,zz-.025],[u+w/2,zz-.025],[u+w/2,zz+.025],[u-w/2,zz+.025]]))
 grid=bars[0]
 for b in bars[1:]:grid=grid+b
 shaped_panel(n+' frame and grid',side,p,(grid^cs)+(cs-cs.offset(-.04*INTERNAL)),.14,3,ev+'; frames coarsened legibilityproxy')

# Coordinates: main front wall y0, rear y27.96; x frontviewleft-to-right.
W=13.71;H=W/2;D=27.96;WY0=14.93;WY1=21.96;WC=(WY0+WY1)/2;OUT=14.02
EV='Appendix9 A2-1/A2-3 surveyed plan, nominal wall envelope based on13.71m transversechain; axis/externalface uncertainty disclosed'
bx('Main nave solid exterior',[-H,0,0],[H,D,5.53],0,EV)
add('Main nave gabled masonry',gable_y(-H,H,0,D,5.50,9.13),0,'A3 side923cm roofridge,553cm eave; solidexteriornotinterior')
# Thin cap strips follow measured envelope; no invented fullynew roof.
add('Main aged copper roof',gable_y(-H-.32,H+.32,-.18,D+.18,5.48,9.23)-gable_y(-H-.4,H+.4,-.25,D+.25,5.32,9.07),2,'A3 mainridge9.23m; roofthicknessauthoredproxy, overhangestimated .32m')
for sign,side in [(-1,'L'),(1,'R')]:
 x0,x1=(-OUT,-H+.08)if sign<0 else(H-.08,OUT)
 bx(side+' transept wall',[x0,WY0,0],[x1,WY1,3.34],0,'381 lowwing334cmwall,195cmrise; nominal externalwallproxy')
 add(side+' transept gable masonry',gable_x(x0,x1,WY0,WY1,3.31,5.19),0,'Lowwing334+195=529cm outerroof; no flat5.53mwing')
 add(side+' transept copper roof',gable_x(x0-.12,x1+.12,WY0-.24,WY1+.24,3.25,5.29)-gable_x(x0-.2,x1+.2,WY0-.32,WY1+.32,3.09,5.13),2,'381 5.29m nominalwingridge; localroofendpoint±.25m')
 # End gable parapet profile rises slightly above roof; independent rearlinenotforcedequal.
 xp=sign*OUT;cs=section([[WC-3.6,0],[WC+3.6,0],[WC+3.6,3.55],[WC,5.53],[WC-3.6,3.55]])
 shaped_panel(side+' transept end gable edge',side,xp,cs,.16,0,'382/383 enddecorativegable approx5.53m, notwholewingroofheight')
 # Main side buttresses skip hidden segment behind lowerwing.
 for yy in [0,5.5,7.59,11.2,14.93,21.96,27.96]:
  bx(side+' side buttress',sorted([sign*(H-.05),sign*(H+.24)])[:1]+[yy-.12,0],sorted([sign*(H-.05),sign*(H+.24)])[1:]+[yy+.12,5.03],0,'A3 slenderexternalbuttress; nominalwidth/depthgraphicalproxy')
  bx(side+' buttress cap',[min(sign*(H-.07),sign*(H+.29)),yy-.15,4.99],[max(sign*(H-.07),sign*(H+.29)),yy+.15,5.25],1,'A3 cappedbuttress headprofile simplified')
# Front/rear gable bargeboards, geometric3D bands.
for yy,n in [(0,'Front'),(D,'Rear')]:
 for xa,xb in [(-H-.3,0),(0,H+.3)]:
  za=5.53 if xa else 9.23;zb=5.53 if xb else 9.23
  add(n+' sloping gable cornice',beam([xa,yy,za],[xb,yy,zb],.105,8),1,'A3 gablebargeboardposition,memberprofileproxy')
# Plinths and rear intermediate strips are genericfinish proxies, notfictitious windows.
bx('Main low plinth',[-H-.03,-.03,0],[H+.03,D+.03,.38],7,'Survey lowwallbase; coarse neutralproxy')
for yy in [0,D]:
 for xx in [-H,-3.6,0,3.6,H]:
  if yy==0 and abs(xx)<3:continue
  panel('Gable facade pilaster','F'if yy==0 else'B',yy,xx-.11,xx+.11,.38,5.18,.10,0,'A3 front/rear verticalwalljoints andbuttressproxy')
# Existing roof repair patches on leftslope only; graphical boundarynotnewuniform copper.
for ya,yb in [(0,7.59),(21.96,D)]:
 xa,xb=-H-.28,0
 z=lambda x:9.23-(9.23-5.48)*abs(x)/(H+.32)
 add('Left roof red repair sheet patch',hull([[x,y,z(x)-.025]for x in[xa,xb]for y in[ya,yb]]+[[x,y,z(x)+.025]for x in[xa,xb]for y in[ya,yb]]),6,'PDF101 redcorrugatedrepairphoto and379 leftslopehatchedrepairregions; graphicboundaryproxy')
# Copper seam rhythm45cm from101/102, simplified relief not exacttileedge reconstruction.
for yy in np.arange(.25,D,.45):
 for sign in [-1,1]:
  if sign<0 and(yy<7.59 or yy>21.96):continue
  add('Main roof standing seam',beam([0,yy,9.245],[sign*(H+.25),yy,5.52],.025,6),2,'PDF101/102 nominal45cm copperseam rhythm,coarse reliefproxy')
# Tower atfront; three genuinelyopen lowerarches, mainD1 belongs to rearhallwall.
TX=1.925;TF=-3.75;TB=.15;TZ=5.16
bx('Tower upper square shaft',[-TX,TF,5.13],[TX,TB,13.12],0,'A380 516+407+389=1312cm; envelope3.85x3.90m graphicestimate around357x360axes')
for side,plane,u in [('F',TF,0),('L',-TX,(TF+TB)/2),('R',TX,(TF+TB)/2)]:
 half=TX if side=='F'else(TB-TF)/2
 cs=section([[u-half,0],[u+half,0],[u+half,TZ],[u-half,TZ]])-outline(u,2.55,0,3.65,'point',.60)
 shaped_panel('Tower '+side+' openporch spandrel',side,plane,cs,.18,0,'377 foreporch+37 andA3threeopenarches; notopaquefakedoor')
 ring=outline(u,2.55,0,3.65,'point',.60).offset(.12*INTERNAL)-outline(u,2.55,0,3.65,'point',.60)
 shaped_panel('Tower '+side+' porcharch trim',side,plane,ring,.26,1,'A3 archtrim coarseprofile; openingkept clear')
for xx in [-TX,TX]:
 for yy in [TF,TB]:
  bx('Tower projecting corner pier',[xx-.20,yy-.20,0],[xx+.20,yy+.20,13.20],0,'377 irregularcornerpierexternalprojection, simplified .40m capmember')
  bx('Tower corner capital',[xx-.25,yy-.25,12.95],[xx+.25,yy+.25,13.27],1,'A380cornercap graphicalprofileproxy')
bx('Foreporch raised floor',[-TX-.1,TF-.10,0],[TX+.1,TB,.37],7,'377 foreporchfloor+37cm; adjacenthall+46cm')
for j in range(3):bx('Entry step'+str(j),[-1.38,TF-.65+j*.18,0],[1.38,TF+.01,.10+j*.10],7,'A380 entrancetreads; profilecoarseproxy')
for zz in [5.16,9.23,13.02]:
 bx('Tower belt cornice',[-TX-.13,TF-.13,zz-.08],[TX+.13,TB+.13,zz+.08],1,'A380 shaftdivision5.16/9.23/13.12, cornerprofileapprox')
add('Tower pyramid copper spire',hull([[-1.7,TF+.2,13.08],[1.7,TF+.2,13.08],[-1.7,TB-.2,13.08],[1.7,TB-.2,13.08],[0,(TF+TB)/2,18.47]]),2,'A380 spire rise535cm from13.12, apex18.47m; roofdiamondtiles omitted')
add('Tower cross upright',beam([0,(TF+TB)/2,18.43],[0,(TF+TB)/2,19.48],.035),3,'A380 total1948cm includes101cm cross; rodwidth displayproxy')
add('Tower cross arm',beam([-.34,(TF+TB)/2,19.18],[.34,(TF+TB)/2,19.18],.035),3,'A380 crossspan graphicallyestimated .68m')
# Smallrooflantern; reserve exactwindowhost after control reconciliation.
CY=WC;C=.99
bx('Roof cupola base',[-C,CY-C,8.68],[C,CY+C,10.30],0,'381/382 smallcupola highbody10.30m approx, intersects ridge9.23m')
add('Roof cupola pyramid',hull([[-1.04,CY-1.04,10.26],[1.04,CY-1.04,10.26],[-1.04,CY+1.04,10.26],[1.04,CY+1.04,10.26],[0,CY,12.38]]),2,'A381 cone/pyramidtop12.38m, not367above mainridge')
add('Roof cupola thin finial proxy',beam([0,CY,12.35],[0,CY,13.38],.028),3,'A381 unlabelledthinfinial above12.38m, nominal1m graphicalproxy; notdimensioned')
# Groundsupport authoring only.
bx('Authored display base',[-15.3,-5.0,-BASE],[15.3,D+1.1,0],8,'Author2mm displaybase at1:200,notrealterrain')

# Source-specific openingtypes and independently estimated positions.
O=json.loads((ROOT/'opening-positions.json').read_text())
def door(n,side,p,u,w,z,h,point=True):
 cs=outline(u,w,z,h,'point'if point else'rect',.23)
 shaped_panel(n+' pale door surround',side,p,cs.offset(.11*INTERNAL),.065,1,'395–397 surveyedwooddoor dimensions,nominalprofile')
 shaped_panel(n+' closed door leaf proxy',side,p,cs,.10,9,'Opaque closedwooddoorproxy, nofullinterior reconstruction')
 # Source main panel count retained; carving and hardware omitted.
 shaped_panel(n+' perimeter door frame',side,p,cs-cs.offset(-.055*INTERNAL),.16,1,'Surveydoorframe, simplifiedlegiblememberwidth')
 cols=2 if w>1.3 else 1
 for i in range(cols):
  leaf=u-w/2+(i+.5)*w/cols;lw=w/cols
  for j in [-1,1]:
   uu=leaf+j*lw*.22;ww=lw*.34
   zones=[(z+.25,h*.53),(z+h*.82,h*.10)] if point else [(z+.18,h*.27),(z+h*.39,h*.25),(z+h*.73,h*.15)]
   for zz,hh in zones:
    pane=section([[uu-ww/2,zz],[uu+ww/2,zz],[uu+ww/2,zz+hh],[uu-ww/2,zz+hh]])
    shaped_panel(n+' insetpanel',side,p,pane^cs,.14,7,'395–397 two main panel columns per leaf; simplified borders not finecarving')
 if cols==2:panel(n+' central stile',side,p,u-.035,u+.035,z,z+h-.23,.18,1,'Surveydoubleleaf separation')
for side,x in [('L',-H),('R',H)]:
 for i,yy in enumerate(O['longside']['W2_front4']['centre_y_m']):window(side+' nave W2 '+str(i+1),side,x,yy,1.79,1.2,3.06,'point',6,4,.16,2.02)
 window(side+' rear W1',side,x,23.8,1.79,1.2,3.15,'point',6,6,.14,2.12,[0,.275,.53,.785,1.04,1.57,2.12])
 door(side+' small rear D5',side,x,27.1,1.01,.40,2.32,False)
 # End doors belong tooutward wingfaces.
 door(side+' wing D2',side,-(OUT+.16) if side=='L'else OUT+.16,18.4,1.90,.19,2.76)
for side,plane,field in [('F',WY0,'W3_front_faces'),('B',WY1,'W3_rear_faces')]:
 for i,xx in enumerate(O['transept'][field]['centres_x_m']):window(side+' wing W3 '+str(i+1),side,plane,xx,1.74,1.2,1.54,'point',6,2,.34,.80)
for xx in [-5.3,5.3]:window('Rear flanking W1','B',D,xx,1.79,1.2,3.15,'point',6,6,.14,2.12,[0,.275,.53,.785,1.04,1.57,2.12])
window('Rear lower W4','B',D,0,1.80,1.2,1.7,'rect',2,2)
window('Rear upper W5','B',D,0,1.80,3.9,3.75,'round',4,4,body_h=2.90)
# Distinct X motif onlyupperrearwindow cells; crossingbars clippedtoarchedglazing.
cs=outline(0,1.8,3.9,3.75,'round');diag=[]
for ua,ub in [(-.86,-.08),(.08,.86)]:
 for za,zb in [(6.07,6.70),(6.91,7.55)]:
  for a,b in [([ua,za],[ub,zb]),([ua,zb],[ub,za])]:
   va=np.array(a);vb=np.array(b);v=vb-va;v=np.array([-v[1],v[0]])/np.linalg.norm(v)*.018
   shape=section([va+v,vb+v,vb-v,va-v]);shaped_panel('Rear W5 upper X tracery','B',D,shape^cs,.17,3,'399 X motifs upperzonesonly; finegridproxy')
door('Mainhall entrance D1','F',0,0,1.8,.46,2.7)
# Blank nameplate is explicitly no invented legibletext.
panel('Tower blank nameplate','F',TF,-.85,.85,3.93,4.64,.23,1,'A380 existingtextpanel withunreadablelettering intentionallyblank')
for side,plane,u in [('F',TF,0),('L',-TX,(TF+TB)/2),('R',TX,(TF+TB)/2)]:
 # Fulltowerarchprofile surroundsseparate louvers andtopwindow; do notglaze entiretallfield.
 tall=outline(u,1.82,6.12,5.71,'round')
 shaped_panel('Tower '+side+' tall surround',side,plane,tall-tall.offset(-.075*INTERNAL),.16,1,'A380–383 tallornamentcontains blankwall between distinctW6/W7')
 for off in [-.53,.53]:
  panel('Tower '+side+' W6 dark slot',side,plane,u+off-.26,u+off+.26,6.3,7.88,.075,5,'400 W6two52cmstrips,54cm solidmiddlewall')
  for zz in np.linspace(6.32,7.85,17):panel('Tower '+side+' W6 louver',side,plane,u+off-.26,u+off+.26,zz,zz+.035,.13,3,'W6 horizontallyslattedopaqueproxy, notglass')
 window('Tower '+side+' W7',side,plane,u,1.58,9.2,2.38,'round',2,1)
# Rear upper tower: only visible arched silhouette supported by381, notcompletefourthface detail.
shaped_panel('Tower rear neutral upper arch proxy','B',TB,outline(0,1.58,9.2,2.38,'round'),.06,4,'381 distantupperarchsilhouette only; no invented rearW6, talllowerframe or precisegrid; rearfaceunknown belowroof')
# Cupola fourfaces: W8flatbottom sides andW9 invertedV acrossridge.
for side,x in [('L',-C),('R',C)]:window('Cupola '+side+' W8',side,x,CY,1.71,8.91,1.09,'rect',2,1)
for side,y in [('F',CY-C),('B',CY+C)]:
 w=1.73;zz=8.96;cs=section([[-w/2,zz],[0,zz+.33],[w/2,zz],[w/2,10.06],[-w/2,10.06]])
 shaped_panel('Cupola '+side+' W9 opaque V-bottom','F'if side=='F'else'B',y,cs,.08,4,'401 Vbottom173cmwide110high; hostalignededge8.96/center9.29 top10.06mproxy;6cm clearancestabilization within graphicaltolerance')
 shaped_panel('Cupola '+side+' W9 frame',side,y,cs-cs.offset(-.045*INTERNAL),.14,3,'W9Vprofile followsridge; .20m hostalignment versus rawgraphical datum disclosed')
 panel('Cupola '+side+' W9 middle stile',side,y,-.025,.025,9.29,10.06,.15,3,'401twopaneW9')

# EXPORT_FINAL

# All boolean cuts preserve missing apertures; no detailed interior room layout is implied.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
if cut_items:s=s-mf.Manifold.batch_boolean(cut_items,mf.OpType.Add)
pre_simplify_components=[{'volume_mm3':q.volume()*SCALE**3,'bounds_internal':q.bounding_box()}for q in s.decompose()]
s=s.set_tolerance(2.).simplify(2.)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda x:'{'+ns+'}'+x
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Lishan Jesus Church surveyed exterior2016-12');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.8f}'for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
files={'[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>','3D/3dmodel.model':ET.tostring(root,encoding='utf-8',xml_declaration=True)}
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED)as z:
 for name,blob in files.items():
  zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,blob)
parts=[]
for op,item in zip(ops+cut_ops,items+cut_items):
 q=item.to_mesh64();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops+cut_ops},indent=2))
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':2.*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'December2016 Appendix9 surveyed church mainbody, two wings, openporch bell tower and roofcupola. Printedaxes reconciledwith graphicalexternalproxies; roofrepairpatches retained. No reuseproposal, dormitory, fountain, detailedinteriors, sourceimagery, trialprint or safetyclaim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
