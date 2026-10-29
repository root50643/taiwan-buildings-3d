#!/usr/bin/env python3
"""Source-qualified Taipei North Police survey exterior, July 2001; no current restoration claim."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=4.;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=.50; MAIN_RFL=14.98
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':'Authored uncalibrated display proxy; not a claim of historical paint or material composition'}for i,(n,c) in enumerate([
('Survey exterior neutral wall','#C4C2B6'),('Coping and bands','#DED9CA'),('Survey roof proxy','#999D95'),('Frames','#555D58'),('Opaque glazing','#829A99'),('Dark blind backing','#333D3B'),('Secondary wall','#AAAFA5'),('Accent','#B5B9AC'),('Authored display support','#D1CABB'),('Neutral detail','#858779')])]
items=[];ops=[];cut_items=[];cut_ops=[];ids={}
def box(a,b):
 a=np.round(np.array(a)*INTERNAL);b=np.round(np.array(b)*INTERNAL)
 return mf.Manifold.cube((b-a).tolist()).translate(a.tolist())
def add(name,s,mat,ev):
 s=s.translate([0,0,BASE*INTERNAL]).as_original(); ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':ev})
def bx(name,a,b,mat,ev):add(name,box(a,b),mat,ev)
def cut(name,s,ev):
 s=s.translate([0,0,BASE*INTERNAL]).as_original();ids[int(s.original_id())]=5;cut_items.append(s);cut_ops.append({'name':name,'material':5,'operation':'subtract','evidence':ev})
def hull(pts):return mf.Manifold.hull_points((np.array(pts)*INTERNAL).tolist())
def beam(a,b,r,seg=12):
 a=np.array(a);b=np.array(b);d=b-a;le=np.linalg.norm(d);z=d/le;h=np.array([0,0,1.])if abs(z[2])<.9 else np.array([1.,0,0]);x=np.cross(h,z);x/=np.linalg.norm(x);y=np.cross(z,x)
 return mf.Manifold.cylinder(le*INTERNAL,r*INTERNAL,r*INTERNAL,seg).transform(np.column_stack([x,y,z,a*INTERNAL]))
def cylinder(x,y,z,h,r1,r2=None,seg=64):return mf.Manifold.cylinder(h*INTERNAL,r1*INTERNAL,(r1 if r2 is None else r2)*INTERNAL,seg).translate([x*INTERNAL,y*INTERNAL,z*INTERNAL])
def gable(x0,x1,y0,y1,z0,z1):return hull([[x0,y0,z0],[x1,y0,z0],[x0,y1,z0],[x1,y1,z0],[x0,(y0+y1)/2,z1],[x1,(y0+y1)/2,z1]])
def panel(name,side,plane,u0,u1,z0,z1,depth,mat,ev):
 if side in ('W','E'):
  a,b=(plane-depth,plane+.03)if side=='W'else(plane-.03,plane+depth);bx(name,[u0,a,z0],[u1,b,z1],mat,ev)
 else:
  a,b=(plane-depth,plane+.03)if side=='N'else(plane-.03,plane+depth);bx(name,[a,u0,z0],[b,u1,z1],mat,ev)
def recess(name,side,plane,u,w,z,h,depth,ev):
 # Real 3D recess with explicit author-added blind backing, never closed leaf.
 if side=='W': aa,bb=[u-w/2,plane-.4,z],[u+w/2,plane+depth,z+h]
 elif side=='E': aa,bb=[u-w/2,plane-depth,z],[u+w/2,plane+.4,z+h]
 elif side=='N': aa,bb=[plane-.4,u-w/2,z],[plane+depth,u+w/2,z+h]
 else: aa,bb=[plane-depth,u-w/2,z],[plane+.4,u+w/2,z+h]
 cut(name+' recess cutter',box(aa,bb),ev+'; depth is authored blind-recess proxy, not measured room depth')
 # backing placed deeper than the cutter, intersecting original mass
 backplane=plane+depth+.01 if side in ('W','N')else plane-depth-.01
 panel(name+' dark back surface',side,backplane,u-w/2+.01,u+w/2-.01,z+.01,z+h-.01,.025,5,'Authored dark blind-recess backing, not a door or complete interior; visible depth '+str(depth)+'m')
def win(name,side,plane,u,w,z,h,cols,rows,ev):
 panel(name+' surround',side,plane,u-w/2-.075,u+w/2+.075,z-.075,z+h+.075,.085,3,ev)
 panel(name+' opaque pane',side,plane,u-w/2,u+w/2,z,z+h,.105,4,'Opaque glazing proxy; not restored transparent glass or full interior')
 for i in range(cols+1):
  q=u-w/2+i*w/cols;panel(name+' mullion',side,plane,q-.034,q+.034,z,z+h,.165,3,ev+'; enlarged member width for legibility')
 for i in range(rows+1):
  q=z+i*h/rows;panel(name+' rail',side,plane,u-w/2,u+w/2,q-.034,q+.034,.17,3,ev+'; enlarged member width for legibility')

# Digitized plan coordinates use 1888px-wide inspection copies, not raster texture assets.
# Axis chain 60.28m is used only with its own plan endpoints; finished elevation 59.05m is separate.
TRACE={211:{'x0':380,'yf':918,'s':60.28/(1657-381)},212:{'x0':310,'yf':940,'s':60.28/(1588-313)},213:{'x0':310,'yf':1002,'s':60.28/(1590-313)}}
def arc(cx,cy,rx,ry,start,end,n=24):return [[cx+rx*math.cos(t),cy+ry*math.sin(t)]for t in np.linspace(start,end,n)]
def xy(page,pts):
 d=TRACE[page];return [[(x-d['x0'])*d['s'],(d['yf']-y)*d['s']]for x,y in pts]
def section(pts):
 p=np.array(pts,dtype=float)
 if np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])<0:p=p[::-1]
 return mf.CrossSection((p*INTERNAL)[None,:,:].tolist())
def prism(pts,z,h):return section(pts).extrude(h*INTERNAL).translate([0,0,z*INTERNAL])
def polygon(name,pts,z,h,mat,ev):add(name,prism(pts,z,h),mat,ev)
def ring(name,pts,z,h,width,mat,ev):
 c=section(pts); inner=c.offset(-width*INTERNAL);add(name,(c-inner).extrude(h*INTERNAL).translate([0,0,z*INTERNAL]),mat,ev)
P3=[[432,1002],[1557,1002],[1557,605],[1480,605],[1480,660],[1306,660],[1306,714],[689,714],[689,666]]+arc(638,666,51,46,0,-math.pi/2)+[[593,620],[593,468],[310,468],[310,900]]+arc(432,900,122,102,math.pi,math.pi/2)
P2=[[430,940],[1550,940],[1550,560],[1493,560],[1493,632],[1303,632],[1303,652],[686,652],[686,602]]+arc(636,602,50,46,0,-math.pi/2)+[[592,556],[592,406],[310,406],[310,838]]+arc(430,838,120,102,math.pi,math.pi/2)
P1=[[516,918],[1625,918],[1625,582],[1550,582],[1550,630],[1373,630],[758,630],[758,582]]+arc(707,582,51,46,0,-math.pi/2)+[[663,536],[663,386],[380,386],[380,816]]+arc(516,816,136,102,math.pi,math.pi/2)
MAIN=[xy(211,P1),xy(212,P2),xy(213,P3)]
# Body changes between survey storeys retained; floor relief is a solid exterior study, not rooms.
for i,(poly,z0,z1) in enumerate(zip(MAIN,[0,5.78,10.38],[5.78,10.38,14.98])):
 polygon('Main surveyed storey '+str(i+1),poly,z0,z1-z0,0,'PDF'+str(211+i)+' independent B2 plan trace, approximate±3%; front levels B3-1 1.18+3x4.60m')
# Rear wing has its OWN level chain and semicircular west projection; no one-storey simplification.
R=xy(213,[[1073,327],[1306,327],[1306,714],[1073,714],[1073,597]]+arc(1073,520,77,77,math.pi/2,3*math.pi/2)+[[1073,327]])
polygon('Connected rear three-storey wing and semicircle',R,0,13.58,6,'PDF211–213,216 rear-wing 13.58m adopted;217 13.38m variant not averaged; storeys4.83/9.18m; graphical footprint')
ring('Rear wing open roof parapet',R,13.58,.50,.22,1,'PDF214,216 parapet approximate; roof-datum discrepancy±.20m disclosed')
polygon('Main flat roof slab',MAIN[2],14.94,.08,2,'PDF214 surveyed roof, not subsequent A restoration')
ring('Main parapet',MAIN[2],14.98,.71,.22,1,'PDF215 RFL+71cm ordinary parapet; open interior of roof ring')
# Preserve entry portico void under curved upper corner, diagonal doorway backing, and stair flight.
entry=[[0,0],[6.45,0],[6.45,3.35],[3.0,7.0],[0,7.0]]
items[0]=(items[0]-prism(entry,1.18,4.30).translate([0,0,BASE*INTERNAL])).as_original();ids[int(items[0].original_id())]=0
ops[0]['evidence']+='; entry portico void subtracted before adding columns, PDF211/215'
for angle in np.linspace(math.pi,1.5*math.pi,4):
 x=6.4+5.7*math.cos(angle);y=6.0+5.4*math.sin(angle)
 add('Corner entrance column',cylinder(x,y,1.18,4.4,.19,seg=24),1,'PDF211/215 portico column positions graph trace; round section simplified')
for j in range(6):
 # curved entrance steps progressively decrease rise toward street, intersect support.
 st=section([[0,-.7],[6.6,-.7],[6.6,1.1],[1.1,6.7],[-.7,6.7],[-.7,0]])
 add('Entrance step '+str(j+1),st.offset(-j*.13*INTERNAL).extrude((.20+j*.165)*INTERNAL),1,'PDF211 curved entrance steps,6 illustrative treads; tread dimensions approximated')
# Far-end vehicle passage stays open through body; solid backing NOT inserted.
items[0]=(items[0]-box([51.35,-.4,0],[55.20,19.3,4.36]).translate([0,0,BASE*INTERNAL])).as_original();ids[int(items[0].original_id())]=0
ops[0]['evidence']+='; vehicle passage3.85m graphical body width, street gate separately narrower; not same dimension endpoints'
# Authored display support ensures a single connected display object; not actual surveyed ground.
bx('Authored display base',[-2,-2,-BASE],[61,34,0],8,'2mm nominal print support slab; not source terrain')
def profile_on_wall(cs,side,plane,depth):
 # Local profile coordinates (u,z), extrusion points out of cardinal wall.
 if side=='W':M=[[1,0,0,0],[0,0,-1,plane*INTERNAL],[0,1,0,0]]
 elif side=='E':M=[[1,0,0,0],[0,0,1,plane*INTERNAL],[0,1,0,0]]
 elif side=='N':M=[[0,0,-1,plane*INTERNAL],[1,0,0,0],[0,1,0,0]]
 else:M=[[0,0,1,plane*INTERNAL],[1,0,0,0],[0,1,0,0]]
 return cs.extrude(depth*INTERNAL).transform(M)
def archwin(name,side,plane,u,w,z,h,ev):
 rad=w/2; spring=z+h-rad
 pts=[[u-rad,z],[u+rad,z],[u+rad,spring]]+[[u+rad*math.cos(t),spring+rad*math.sin(t)]for t in np.linspace(0,math.pi,21)]
 cs=section(pts);add(name+' arched opaque pane',profile_on_wall(cs,side,plane-.015 if side in ('E','S')else plane+.015,.12),4,ev+'; solid opaque pane, not interior')
 rim=cs.offset(.07*INTERNAL)-cs.offset(-.055*INTERNAL)
 add(name+' arched frame',profile_on_wall(rim,side,plane-.02 if side in ('E','S')else plane+.02,.19),3,ev+'; frame thickness enlarged')
 for fraction in [.24,.62,1.0]:
  zz=z+(spring-z)*fraction;panel(name+' horizontal rail',side,plane,u-rad,u+rad,zz-.03,zz+.03,.18,3,ev)
 panel(name+' vertical muntin',side,plane,u-.028,u+.028,z,z+(spring-z)*.24,.18,3,ev)
# Main horizontal bands follow curved surveyed contour rather than flattening corner.
for z in [1.18,5.78,10.38,14.98]:
 poly=MAIN[0 if z<5.78 else 1 if z<10.38 else 2]
 cs=section(poly);band=(cs.offset(.055*INTERNAL)-cs.offset(-.04*INTERNAL)).extrude(.13*INTERNAL).translate([0,0,(z-.08)*INTERNAL])
 if z==1.18:band=band-box([51.35,-.4,0],[55.20,19.3,4.36])
 add('Continuous main floor belt '+str(z),band,1,'PDF215–218 floor belts, interrupted atvehiclepassage; profile and thickness approximated')
# Rear wing has a different, source-selected datum chain.
for z in [1.18,4.83,9.18,13.58]:ring('Rear floor belt '+str(z),R,z-.08,.13,.10,1,'PDF216 selected rear level chain; PDF217 alternative disclosed')
controls=json.loads((ROOT/'opening-positions.json').read_text())
L=max(p[0] for p in MAIN[2]);F=[(1,1.83,2.76),(2,6.55,2.88),(3,11.15,2.88)]
for level,z,h in F:
 bays=controls['front']['ten_main_pair_bays']+(controls['front']['three_terminal_upper_pairs']if level>1 else[])
 for i,bay in enumerate(bays):
  for j,u in enumerate(bay['individual_centres_u']):
   name=f'Front {level}F bay{i+1} field{j+1}';ev='PDF215 individually traced independent paired opening,239/240 window families; survey replacement frames simplified'
   if level==1:win(name,'W',0,u*L,.98,z,h,1,3,ev)
   else:archwin(name,'W',0,u*L,.98,z,h,ev)
 if level>1:archwin(f'Front stair {level}F','W',0,.76537*L,1.02,5.45 if level==2 else z,4.03 if level==2 else h,'PDF215/240 single stair opening distinctly taller on2F')
# Thin bay field borders are facade relief, not new structural supports.
for u in [.108,.174,.239,.301,.363,.425,.486,.548,.610,.672,.737,.797,.868,.939,.997]:
 x=u*L;panel('Front vertical bay strip','W',0,x-.055,x+.055,1.2,14.85,.055,1,'PDF215 shallow vertical bay field borders, proxy thickness')
for level,z,h in F:
 for i,g in enumerate(controls['left']['upper_main_groups']):
  for j,u in enumerate(g['individual_screen_u']):
   yy=(1-u)*31.73
   if level>1:archwin(f'Left {level}F group{i} field{j}','N',0,yy,.97,z,h,'PDF218 own4paired+single pattern, not mirroredfront')
   else:win(f'Left ground group{i} field{j}','N',0,yy,.97,z,h,1,3,'PDF218 visible groundrect fields; some canopy occlusion simplified')
# A single shared curved W11 band, three groups, not duplicate front/left projections.
# Polygonal tangent segments follow actual plan ellipse. Widths175/224/175 and piers35cm.
angles=np.linspace(math.pi,1.5*math.pi,1001);curve=np.column_stack([5.76*np.cos(angles),4.82*np.sin(angles)]);dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
margin=(dist[-1]-6.44)/2
window_angles=np.interp(np.array([.875,1.75+.35+1.12,1.75+.35+2.24+.35+.875])+margin,dist,angles)
for level,z,h in F[1:]:
 for g,(ang,width,cols) in enumerate(zip(window_angles,[1.75,2.24,1.75],[2,3,2])):
  cx,cy=5.76,4.82;rx,ry=5.76,4.82
  center=np.array([cx+rx*math.cos(ang),cy+ry*math.sin(ang)])
  # Tangent orientation and outward normal; components overlap exterior by.10m.
  tangent=np.array([-rx*math.sin(ang),ry*math.cos(ang)]);tangent/=np.linalg.norm(tangent)
  normal=np.array([tangent[1],-tangent[0]])
  def curved_piece(n,u0,u1,zz0,zz1,depth,mat):
   pts=[center+tangent*u+normal*d for u,d in[(u0,-.12),(u1,-.12),(u1,depth),(u0,depth)]]
   polygon(n,[q.tolist()for q in pts],zz0,zz1-zz0,mat,'PDF242 W11 shared2/3/2column curved band; tangent facets and frame thickness approximated')
  curved_piece(f'Corner W11 {level}F group{g} pane',-width/2,width/2,z,z+2.46,.12,4)
  for j in range(cols+1):
   u=-width/2+j*width/cols;curved_piece(f'Corner W11 group{g} mullion',u-.035,u+.035,z,z+2.46,.19,3)
  for dz in[0,1.25,1.84,2.46]:curved_piece('Corner W11 rail',-width/2,width/2,z+dz-.035,z+dz+.035,.20,3)
# Right main elevation is intentionally blank on first two storeys.
for i,u in enumerate([.11,.28,.47,.68,.89]):
 win(f'Right main top window{i}','S',L,u*18.71,2.7 if i<2 else 1.6 if i<4 else 1.2,12.35,1.08,4 if i<2 else 2,2,'PDF217 five upper rectangular windows only')
# Rear rectangular wing end and right side: two upper rows, detention ground shell largelyblank.
rx0=min(p[0]for p in R if p[1]>30);rx1=max(p[0]for p in R);ry=max(p[1]for p in R)
for lv,z in[(2,5.55),(3,10.0)]:
 for i,u in enumerate([.20,.50,.80]):win(f'Rear wing end {lv}F {i}','E',ry,rx0+(rx1-rx0)*u,1.65,z,2.5,2,3,'PDF216 three groups onrearend, not groundcells')
 for i,yy in enumerate([18.3,21.8,25.3,28.8]):win(f'Rear wing right {lv}F {i}','S',rx1,yy,1.65,z,2.5,2,3,'PDF217 four separate verticalwindowstrips on rear projection')
 for yy in[27.0,30.0]:win(f'Rear wing left {lv}F {yy}','N',rx0,yy,1.3,z,2.5,2,3,'PDF218 two upper rectangulargroups on distant rearwing, not arches')
# Recessed rear corridor, mirrored PROJECTION order mapped to existing wall, not mirroredfacade.
rearplane=(1002-714)*TRACE[213]['s']
for lv,z in[(2,6.50),(3,11.10)]:
 rearplane=(940-652)*TRACE[212]['s'] if lv==2 else (1002-714)*TRACE[213]['s']
 for i,u in enumerate([.13,.34,.43,.59,.68,.84,.93]):
  x=32.6-u*14.49;win(f'Recessed rear {lv}F {i}','E',rearplane,x,.95,z,2.65,1,3,'PDF216 long recessedwall1single+3pairs at y13.5, not rearwingend')
 win(f'Rear return sliver {lv}F','E',rearplane,34.2,.75,z,2.2,1,2,'PDF216 narrow visible return, existingwallonly, no inventedvolume')
rearplane=(918-630)*TRACE[211]['s']
for i,(x,z,h,w)in enumerate([(30.4,1.5,3.1,.95),(28.0,1.7,2.8,.95),(26.6,3.4,1.1,.95),(24.0,1.8,2.7,.95),(22.6,1.8,2.7,.95),(19.5,1.6,1.2,1.8),(19.6,4.1,.5,.7)]):win(f'Irregular rear ground{i}','E',rearplane,x,w,z,h,1,2,'PDF216 irregulargroundopenings, not copyofupperrow')
# Terminal rear body and separate stub use their actual independent wallplanes.
for lv,z in[(2,6.5),(3,11.2)]:
 for i,x in enumerate([49.0,52.0]if lv==3 else[48.3,49.3,52.3]):win(f'Terminal rear {lv}F {i}','E',(940-632)*TRACE[212]['s'] if lv==2 else (1002-660)*TRACE[213]['s'],x,1.0,z,1.6,1,2,'PDF216 terminalwing rearwall, not farstub')
leftrear=(1002-468)*TRACE[213]['s']
for x in[2.1,5.2]:win('Left rear thirdfloor square','E',leftrear,x,1.5,11.8,1.4,2,2,'PDF216 leftrear2squares, lowerwallblank')
for lv,z in[(1,1.8),(2,6.5)]:
 for x in[11.1,12.4]:win(f'Left rear side strip {lv}F','E',(918-386)*TRACE[211]['s'] if lv==1 else (940-406)*TRACE[212]['s'],x,.85,z,2.3,1,3,'PDF216 beside roofstair strip, no thirdfloorcopy')
# Street gate dimensions are independent of interior passage trace:335cm clear,72cm piers.
gate_mid=(51.35+55.20)/2
for sign in[-1,1]:
 x=gate_mid+sign*(3.35/2+.72/2);bx('Street gate72cm pier',[x-.36,-.55,0],[x+.36,.15,4.38],1,'PDF215 streetgate72cm pier,335cm clear, not same endpoints as internalpassage')
bx('Street gate lintel',[gate_mid-2.55,-.62,4.22],[gate_mid+2.55,.20,4.48],1,'PDF215 linteloveropenstreetgate; gateleaf omitted, not glazed Xpattern')
def roundfield(name,side,plane,u,z,r):
 pts=[[u+r*math.cos(t),z+r*math.sin(t)]for t in np.linspace(0,2*math.pi,49)]
 c=section(pts);add(name+' dark opaque circular field',profile_on_wall(c,side,plane+.02,.11),5,'PDF215 circularopening; blindopaque exterior proxy not full interior')
 add(name+' roundrim',profile_on_wall(c.offset(.07*INTERNAL)-c.offset(-.04*INTERNAL),side,plane+.03,.18),1,'PDF215 roundrim approximate')
roundfield('Stair groundcircle','W',0,.76537*L,2.15,.51)
for x in[48.1,57.9]:
 bx('Street low guardwall',[x-1.7,-.60,0],[x+1.7,-.20,3.1],0,'PDF215 lowstreetguardwall, relativepositiongraphical')
 roundfield('Guardwallcircle','W',-.60,x,2.10,.56)
 for xx in[x-.65,x+.65]:win('Small guardzone upperrect','W',0,xx,.8,3.55,.55,1,1,'PDF215 smallrectangles aboveguardwall; not typicalgroundbay')
cs=section(MAIN[2]); corner=(cs-cs.offset(-.22*INTERNAL)).extrude(1.40*INTERNAL).translate([0,0,14.98*INTERNAL])^box([-.2,-.2,14.97],[6.5,6.5,16.4])
add('Localized raised corner parapet',corner,1,'PDF215 localized+140cm parapet not ordinary+71cm; transition profile simplified')

for yy in[26.8,29.8]:win('Rear wing west ground window','N',rx0,yy,.95,1.5,2.1,1,3,'PDF218 two narrow groundrects onwesternstraightwall; unlike blankrearend, dimensionsgraphicalproxy')
# Permanent roof stair structure follows214plan and215height, not unresolved222section.
bx('Permanent rooftop stair room',[7.20,17.91,14.90],[10.47,25.20,18.27],0,'PDF214 enlarged roofstair3.27x7.29m; locationgraphicallyaligned toleftwing rear;215 RFL+3.29m')
bx('Stair room coping',[7.10,17.81,18.15],[10.57,25.30,18.27],1,'PDF215 roofstaircoping, approximateprojection')
bx('Survey rooftop water tank',[8.00,20.305,18.27],[9.69,23.895,20.35],6,'PDF214 tank1.69x3.59m,215+2.08m above stairroom; top20.35mGL')
win('Roof stair rear window','E',25.20,8.85,.95,16.35,1.0,1,2,'PDF216 permanent roofstair singlewindow, graphicalsize')
recess('Roof stair door','W',17.91,8.85,.95,15.15,1.85,.15,'PDF215 rooftopstair door withblindbacking')
# Five small equipment tanks visible in214 are approximated, no hidden pipework invented.
for i,(x,r)in enumerate([(19.25,.70),(23.55,.62),(26.0,.62),(29.0,.62),(31.4,.62)]):
 add('Survey roof equipment tank '+str(i+1),cylinder(x,11.95,14.98,1.20,r,seg=32),6,'PDF214 five circular tank footprints; height1.20m displayproxy, no contents or function beyond tanklabel')
# Rear rounded stair junction windows follow its tangent rather than a flat fictitious rearwall.
for lv,z in[(1,2.4),(2,6.6),(3,11.3)]:
 win('Rear stair straight portion '+str(lv),'E',[(918-536)*TRACE[211]['s'],(940-556)*TRACE[212]['s'],(1002-620)*TRACE[213]['s']][lv-1],14.5,1.6,z,1.1 if lv==1 else 2.3,3 if lv>1 else 2,2,'PDF216 roundedstairprojection upperrects/lower shortfields; tangent approximate')
 win('Rear stair return portion '+str(lv),'S',[(758-380)*TRACE[211]['s'],(686-310)*TRACE[212]['s'],(689-310)*TRACE[213]['s']][lv-1],15.1,1.4,z,1.1 if lv==1 else 2.3,2,2,'PDF216 curvedstair returnplane, approximate projectedwindow')
# Diagonal entrance backing is visible within the portico, not a sealed exterior curve.
tangent=np.array([.687,-.726]);normal=np.array([-.726,-.687]);center=np.array([4.5,5.41])
for k in[-1,1]:
 c=center+tangent*(k*.56)
 pts=[(c+tangent*u+normal*d).tolist()for u,d in[(-.50,-.20),(.50,-.20),(.50,.08),(-.50,.08)]]
 polygon('Diagonal entrance door field',pts,1.27,3.35,5,'PDF211/215 diagonal entrance door behindportico; opaque closedfield proxy,nointerior')
# Side entrance canopy/ramp visible in218, coarse survey attachment not an added room.
bx('Left entry canopy',[-1.4,10.8,4.1],[.10,14.0,4.25],1,'PDF211/218 sideentrycanopy graph-traced approximate')
polygon('Left entry ramp',[[-1.35,10.6],[-.05,10.6],[-.05,17.4],[-1.35,17.4]],0,.25,6,'PDF211/218 ramp footprint proxy; detailed accessibility slope not reconstructed')
win('Rear stair strip thirdfloor lower window','E',leftrear,8.85,.95,10.8,1.65,1,3,'PDF216 separate lower longrect inthirdfloorstairstrip; graphical sill/height')
win('Rear stair strip thirdfloor upper window','E',leftrear,8.85,.95,13.2,.70,1,1,'PDF216 separate smallupperrect; uncertain lowerblankpatch notmadeintoopening')
# Exposed rear stair is separately evidenced, not the unresolved rooftop temporary shed.
for j in range(18):
 x=27.0+j*(5.25/18);h=.25+(j+1)*4.58/18
 bx('Rear exterior stair tread '+str(j+1),[x,13.55,0],[x+5.25/18+.015,14.85,h],1,'PDF211/216 exposedrearstair silhouette;18illustrativetreads and1.30mwidth are graphicalproxies')
for yy in[13.65,14.80]:
 add('Rear exterior stair sloped handrail',beam([27.0,yy,1.20],[32.25,yy,5.68],.065),3,'PDF216 exposedstairrailing, memberdiameter enlarged proxy')
 for j in range(9):
  x=27+j*5.25/8;z=.5+j*4.58/8
  add('Rear exterior stair railing post',beam([x,yy,z],[x,yy,z+.95],.05),3,'PDF216 coarse exterior stairrails, postcount simplified')
bx('Rear exterior stair landing',[32.05,13.55,4.63],[33.15,14.85,4.83],1,'PDF211/216 rearstair upperlanding approximate')
# EXPORT_FINAL
# All boolean cuts preserve missing apertures; no detailed interior room layout is implied.
s=mf.Manifold.batch_boolean(items,mf.OpType.Add)
if cut_items:s=s-mf.Manifold.batch_boolean(cut_items,mf.OpType.Add)
pre_simplify_components=[{'volume_mm3':q.volume()*SCALE**3,'bounds_internal':q.bounding_box()}for q in s.decompose()]
s=s.set_tolerance(.5).simplify(.5)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda x:'{'+ns+'}'+x
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='Taipei North Police exterior study2001-07');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'2001-07 B-series three-storey exterior incl rear semicircular wing. Approximate graph-traced geometry and disputed rear datums13.58/13.38m explicitly qualified. Source plans and elevation extents differ. No interiors, original source imagery, trial print or safety claim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
