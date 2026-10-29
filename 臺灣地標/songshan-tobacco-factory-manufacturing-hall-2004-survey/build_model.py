#!/usr/bin/env python3
"""Source-qualified Songshan manufacturing hall exterior study; exact and inferred controls distinguished."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=5/3;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL
BASE=1.20;WIDTH=90.99;LENGTH=164.68;F2=4.3;RC=10.2;EAVE=12.6;RIDGE=13.6
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':e}for i,(n,c,e) in enumerate([
('RC facade proxy','#C2C0B3','PDF56 RC manufacturing hall1939; display color uncalibrated'),
('Bands and coping','#D4D0C2','PDF263–267 light horizontal facade bands, approximate'),
('Added sheet roof proxy','#58645D','PDF95 added iron-sheet roof,263–267 thin pitched shelters; no original1939 material claim'),
('Frames and accents','#55564D','PDF263–267 dark joinery and facade details; approximate enlarged members'),
('Opaque glazing','#829897','Solid display panes, no interior or transparent-glass restoration'),
('Dark recess','#333D3B','Authored opaque doorway backing, not complete interior'),
('Neutral auxiliary','#A3A69B','Approximate flat roof/secondary material'),
('Pale wall field','#B5B9AC','Uncalibrated neutral wall variation'),
('Authored support','#D1CABB','2mm display base, not surveyed terrain'),
('Neutral detail','#858779','Authored accent')])]
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

# Local x north->south, y west->east. Raster-controlled exterior only.
def rounded(a,b,r,steps=6):
 pts=[]
 for cx,cy,start in [(a[0]+r,a[1]+r,180),(b[0]-r,a[1]+r,270),(b[0]-r,b[1]-r,0),(a[0]+r,b[1]-r,90)]:
  for ang in np.linspace(start,start+90,steps+1):
   for z in [a[2],b[2]]:pts.append([cx+r*math.cos(math.radians(ang)),cy+r*math.sin(math.radians(ang)),z])
 return hull(pts)
def hip(x0,x1,y0,y1,z0,z1):
 d=min(x1-x0,y1-y0)/2
 if x1-x0>=y1-y0:return hull([[x,y,z0] for x in [x0,x1] for y in [y0,y1]]+[[x0+d,(y0+y1)/2,z1],[x1-d,(y0+y1)/2,z1]])
 return hull([[x,y,z0] for x in [x0,x1] for y in [y0,y1]]+[[(x0+x1)/2,y0+d,z1],[(x0+x1)/2,y1-d,z1]])

def roof_shelter(name,x0,x1,y0,y1,axis='y'):
 # Survey-era added sheet shelter: thin pitched skin and open support gap above originalRCslab.
 t=.20
 if axis=='y':
  mid=(x0+x1)/2
  for xa,xb,za,zb in [(x0,mid,EAVE,RIDGE),(mid,x1,RIDGE,EAVE)]:
   pts=[[x,y,z+dz]for x,z in [(xa,za),(xb,zb)]for y in [y0,y1]for dz in [-t,0]]
   add(name+' thin sheet slope',hull(pts),2,'PDF95 later iron-sheet roof addition;263–267 raised thin roof, pitch/offsets approximate; not solid thirdstorey')
  for y in np.linspace(y0+.8,y1-.8,max(2,round((y1-y0)/4.2))):
   for x in [x0+.5,x1-.5]:bx(name+' shelter post',[x-.15,y-.15,RC-.08],[x+.15,y+.15,EAVE+.10],3,'PDF262/263–267 two roof-support rows; approximate spacing/section enlarged at1:600')
 else:
  mid=(y0+y1)/2
  for ya,yb,za,zb in [(y0,mid,EAVE,RIDGE),(mid,y1,RIDGE,EAVE)]:
   pts=[[x,y,z+dz]for y,z in [(ya,za),(yb,zb)]for x in [x0,x1]for dz in [-t,0]]
   add(name+' thin sheet slope',hull(pts),2,'PDF95 later iron-sheet roof addition;263–267 raised thin roof, pitch/offsets approximate; not solid thirdstorey')
  for x in np.linspace(x0+.8,x1-.8,max(2,round((x1-x0)/4.2))):
   for y in [y0+.5,y1-.5]:bx(name+' shelter post',[x-.15,y-.15,RC-.08],[x+.15,y+.15,EAVE+.10],3,'PDF262/263–267 two roof-support rows; approximate spacing/section enlarged at1:600')

ev='OfficialJanuary2004 report PDF260–267,1939 RC manufacturinghall; independent per-pagegraphical50m scales, approx±3%, not exact measured dimensions'
ctl=json.loads((ROOT/'geometry-controls.json').read_text());opctl=json.loads((ROOT/'opening-controls.json').read_text())
bx('Authored flat support',[-18,-5,-BASE],[101,180,0],8,'2mm display support at1:600, not historic ground levels')
for key in ['north_strip','south_strip','west_outer_strip','west_inner_strip','east_strip','central_west_hall']:
 r=ctl['rectangles'][key];x0,x1=r['model_x_north_to_south'];y0,y1=r['model_y_west_to_east']
 bx(key+' solid exterior body',[x0,y0,0],[x1,y1,RC],0,ev+'; solid envelope not reconstructed interiors')
 bx(key+' RC roof slab',[x0-.05,y0-.05,RC-.28],[x1+.05,y1+.05,RC+.03],1,'PDF262 originalroof-floor plane distinct from later raised sheet shelter')
# Main courtyard corners are chamfered, not an undifferentiated rectangle.
for x,dx in [(16.715,1),(74.419,-1)]:
 for y,dy in [(46.802,1),(146.802,-1)]:
  add('Main court chamfer body',hull([[xx,yy,z]for xx,yy in [(x,y),(x+dx*3.63,y),(x,y+dy*3.63)]for z in [0,RC]]),0,'PDF260–262 four approximately3.63m chamfered courtyardcorners')
# Four two-floor courtyard stair envelopes; correct small raster gaps at hostwall.
for key,r in ctl['courtyard_stair_projection_full_footprints'].items():
 x0,x1=r['model_x_north_to_south'];y0,y1=r['model_y_west_to_east']
 if key=='north':x0=16.65
 if key=='south':x1=74.48
 if key=='west':y0=46.70
 if key=='east':y1=146.90
 bx(key+' court staircase envelope',[x0,y0,0],[x1,y1,RC],0,'PDF260/261 full staircase projection footprint, not262smallroofcap; hostwall join adjusted within raster error; no internal stairs')
 bx(key+' stair roof coping',[x0-.05,y0-.05,RC-.15],[x1+.05,y1+.05,RC+.05],1,'Approximate neutral stairroofedge')
# Only small roof-level enclosures actually plotted in262, shallow heightproxy.
for px in [(824,337,863,367),(914,337,940,353),(826,707,864,737),(914,721,940,737),(538,490,579,585),(1186,490,1226,585)]:
 ya,xa,yb,xb=px;x0=(xa-224)/6.88;x1=(xb-224)/6.88;y0=(ya-216)/6.88;y1=(yb-216)/6.88
 bx('Small stair roof cap',[x0,y0,RC-.05],[x1,y1,RC+1.0],6,'PDF262 small cap footprint; height1m author proxy unknown, not measured upperroom')
# Semicircular low bath roof outlines within two western small courts, not outdoor fountains.
for key,pix,sgn in [('north',(374,438),-1),('south',(374,638),1)]:
 y=(pix[0]-216)/6.88;x=(pix[1]-224)/6.88;rad=38/6.88
 full=cylinder(x,y,0,3.5,rad,seg=64)
 half=full^box([x-rad-.1,y-rad-.1,-.1],[x+.01,y+rad+.1,3.6]) if sgn<0 else full^box([x-.01,y-rad-.1,-.1],[x+rad+.1,y+rad+.1,3.6])
 add(key+' low semicircular bath enclosure',half,0,'PDF260–262 semicircular bathing-room roof outline;3.5mheight proxy(range3–4.3), material/roof profile unknown')
 x0,x1=(x,34.08) if sgn<0 else (56.90,x)
 bx(key+' bath rectangular root',[x0,15.55,0],[x1,31.84,3.5],0,'Plan bath rectangle joins centralhall; not fountain basin')
# Later east annexes use level-specific footprints; south long strip remains open.
bx('East north two-storey annex',[-5.087,164.60,0],[45.64,173.983,RC],7,'260/261 enclosed eastnorthaddition bothlevels; neutral envelopeheight atmainroofproxy, exact roofjunction/material unknown')
bx('East north annex flat cap',[-5.15,164.55,RC-.15],[45.7,174.05,RC+.05],6,'262 laterannex outline, neutral thinflatcap not claimed exact historicroofmaterial')
bx('East south low annex',[45.64,166.424,0],[85.901,173.983,F2],7,'260 continuousgroundeaststrip; lowheight proxy at commonF2datum')
bx('East south upper enclosed segment',[65.29,166.424,F2-.10],[85.67,173.983,RC],7,'261 onlysouthern upperenclosedsegment; middleupper stair/open interval explicitlynotsealed')
bx('East south upper cap',[65.24,166.37,RC-.15],[85.72,174.04,RC+.05],6,'Neutral thinannexroof proxy')
# No fake treads in upper middle staircase/void; outline deck and open balustrade only.
bx('East middle open upper deck',[45.64,166.424,F2-.2],[65.29,173.983,F2],1,'261 middleupper stair/openinterval approximated openplatform, exact stairs omitted')
for x in np.arange(46,65,3.8):
 bx('East open deck railing post',[float(x)-.1,173.7,F2-.1],[float(x)+.1,173.9,F2+1.0],3,'Neutral openplatformguard proxy, unknown exactpattern')
bx('East open deck upper rail',[45.64,173.7,F2+.9],[65.29,173.9,F2+1.1],3,'Authored guard proxy not measuredrailing')
for z in [.15,F2,RC]:bx('South external strip deck',[90.94,51.599,z-.18],[96.802,143.314,z],1,'260/261/262 southlaterexternalstrip interpretedopen supporteddeck, not solidtallannex; levels approximate')
for y in np.linspace(52,142.7,23):
 for x in [91.10,96.48]:bx('South external strip post',[x-.14,float(y)-.14,0],[x+.14,float(y)+.14,RC+.01],1,'Sourceouterpostrhythm, section/spacing approximate')
for z in [F2+1.0,RC+1.0]:
 bx('South external strip guard',[96.45,51.599,z-.10],[96.65,143.314,z+.10],3,'Neutral open railing proxy; exactcladdingnotconfirmed')
 for y in np.arange(52,143,3.9):bx('South guard upright',[96.43,float(y)-.10,z-1.10],[96.67,float(y)+.10,z+.05],3,'Authoredguarddetail, nohistoricalpatternclaim')
# Added roof shelters must stay thin and open above the originalroof.
roof_shelter('North long roof',0,16.715,-.1,164.75,'y')
roof_shelter('South long roof',74.419,90.99,-.1,164.75,'y')
for name,y0,y1 in [('West outer',0,11.628),('West inner',34.593,46.802)]:
 for x0,x1 in [(16.6,34.012),(56.977,74.50)]:roof_shelter(name+' short roof',x0,x1,y0,y1,'x')
roof_shelter('East roof',16.6,74.5,146.802,164.68,'x')
# Central hall is a distinct higher gable with narrower raised ventilationmonitor.
add('Central hall gable envelope',hull([[x,y,z]for x,z in [(34.012,RC-.05),(56.977,RC-.05),(45.4945,15.2)]for y in [0,42.733]]),0,'PDF266 centralhall gabled envelope aboveassemblyhall; opaque proxy, not truss/interior reconstruction')
for xa,xb,za,zb in [(33.7,45.4945,10.15,15.3),(45.4945,57.3,15.3,10.15)]:
 add('Central hall pitched roof skin',hull([[x,y,z+dz]for x,z in [(xa,za),(xb,zb)]for y in [-.2,42.95]for dz in [-.2,0]]),2,'PDF262/266 larger centralhallroof; approximate eaves')
bx('Hall ridge ventilation monitor',[41.6,12.0,14.25],[49.4,38.8,16.0],6,'262 centrewhite roofrectangle and266 ridgeventilationmonitor; footprint/height graphicalproxy')
add('Hall monitor gable',hull([[x,y,z]for x,z in [(41.3,15.9),(49.7,15.9),(45.5,17.0)]for y in [11.8,39.0]]),2,'266 narrow uppercap with dualpitch, approx17m maximum')
for y in np.arange(13,38,2.6):
 for side,x in [('N',41.6),('S',49.4)]:win('Hall monitor louver',side,x,float(y),1.5,14.7,.8,2,2,'266 ventilationmonitor neutral coarse grille, not exact count')
# North ground projecting wing known from260, upperplan261 shows its roofonly.
bx('North west ground projection',[-8.4,47.05,0],[.1,55.16,F2],7,'260 projectingrectangulargroundwing;261roofoutline supports onelevel proxy')
bx('North west projection cap',[-8.5,46.95,F2-.15],[.15,55.26,F2+.05],6,'Neutral flatcap unknown detailedroofmaterial')
# Northeast upper external connection, open-ended at sourceextent; no fabricated adjoiningbuilding.
bx('North east raised connection deck',[-15.9,146.50,F2-.25],[.05,150.65,F2],1,'261 northeasternupper projectingpassage;262no separateupperroof, deckonly not fullheighttower')
for y in [146.55,150.45]:
 bx('North east connection guardrail',[-15.9,y,F2+.9],[.05,y+.20,F2+1.1],3,'Neutralguardrail proxy; sourceextent not fullyrestored adjoiningconnection')
 for x in [-15.6,-11.7,-7.8,-3.9]:bx('North east connection guardpost',[x-.12,y,F2-.05],[x+.12,y+.20,F2+1.05],3,'Authoredguardposts; no precisehistoricalpattern')
# Exterior window fields derived separately for each elevation, not symmetry-invented.
def field(name,side,plane,u,w,typ,level,ev):
 z0=0 if level==0 else F2
 if typ in ['D','D_plain']:
  if typ=='D':
   for sign in [-1,1]:recess(name+' pairedleaf'+str(sign),side,plane,u+sign*(w+.13)/4,(w-.13)/2,z0+.10,3.45,.25,ev+'; paired opaque blinddoorway with retainedcentralframe, not interior')
  else:recess(name,side,plane,u,w,z0+.10,3.45,.25,ev+'; opaque blinddoorway proxy not interior')
  if typ=='D':
   for uu in [u-w/2,u,u+w/2]:panel(name+' door frame',side,plane,uu-.055,uu+.055,z0+.1,z0+3.55,.18,3,'Schematic pairedleaf/frame, exactjoinerynotrestored')
   panel(name+' door lintel',side,plane,u-w/2-.1,u+w/2+.1,z0+3.45,z0+3.65,.18,1,ev)
 elif typ=='X':panel(name+' unclear neutral panel',side,plane,u-w/2,u+w/2,z0+1.0,z0+3.1,.08,7,ev+'; filled/unclear field, no fabricatedglazing')
 else:
  z,h,cols,rows={'T':(z0+.75,2.85,3,4),'H':(z0+2.65,.95,3,1),'S':(z0+1.20,1.65,2,2)}[typ]
  win(name,side,plane,u,w,z,h,cols,rows,ev+'; coarsefieldgriddisplayproxy, exactdenseleafpatternnotrestored at1:600')
for face,side,plane in [('north','N',0),('south','S',WIDTH)]:
 spec=opctl['long_faces'][face]
 for level,lv in enumerate(['ground','upper']):
  for j,(u,t) in enumerate(zip(spec['normalized_centres'],spec[lv])):
   if face=='north' and level==0 and j==10:continue # Mapped to projection-end doorway, not duplicated hostwall hole.
   y=u*LENGTH;w=2.35 if j<36 else 1.45
   field(f'{face} exterior field{j} level{level}',side,plane,y,w,t,level,f'PDF{spec["page"]} independent40field schedule; orientationinferred byplanprojections despitecaptionconflict')
# North ground projection hides hostfield: give its end the documenteddoor motif.
field('North projection end doorway','N',-8.4,51.1,2.3,'D',0,'260groundextension/265north doorway field; endpositionapproximate')
# West asymmetric18principal groundwindowgroups and5doorfields.
w=opctl['west_shortface']
for i,u in enumerate(w['ground_window_centres_u']):field(f'West ground windowgroup{i}','W',0,u*WIDTH,2.35,'T',0,'PDF263 westground principalwindowgroup; southernterminalsmallleafsubdivisionssimplified')
for i,u in enumerate(w['ground_door_centres_u']):field(f'West ground doorgroup{i}','W',0,u*WIDTH,2.6 if i!=2 else 3.5,'D',0,'PDF263 fivewestgrounddoorgroups; opaqueproxy')
up=w['upper']
for key,typ in [('north_terminal_T_u','T'),('north_middle_S_u','S'),('central_raised_H_u','H'),('south_middle_S_u','S')]:
 for i,u in enumerate(up[key]):field(f'West upper {key}{i}','W',0,u*WIDTH,2.4,typ,1,'PDF263 westupper differentiatedfields; not mirroredside')
for key in ['north_stair_door_u','south_stair_door_u']:field(key,'W',0,up[key]*WIDTH,2.15,'D',1,'PDF263 upperstairdoorfield, not openfreefall accessclaim')
for i,(u,t) in enumerate(zip(up['south_terminal_mixed_u'],up['south_terminal_types'])):field(f'West upper southterminal{i}','W',0,u*WIDTH,1.8,t,1,'PDF263 mixedsouthernterminal groupedproxy, not northernsymmetry')
win('West hall high gable grille','W',0,45.5,3.0,12.4,.9,3,1,'PDF263 gableupper smallventilationfield; approximate')
# East outline is layered across later annex and mainwall planes.
e=opctl['east_shortface']
for level,lv in enumerate(['ground','upper']):
 for i,(u,t) in enumerate(zip(e['normalized_centres_S_to_N'],e[lv])):
  x=-5.087+(1-u)*(WIDTH+5.087)
  plane=173.983 if x<45.64 or (45.64<=x<=85.90 and level==0)or(65.29<=x<=85.67 and level==1)else LENGTH
  field(f'East exterior field{i} level{level}','E',plane,x,2.4 if 5<=i<=18 else 1.9,t,level,'PDF265 east24fields screenS-to-N reversed; uppermiddle highstrips, unknownfilledfieldsneutral; laterannexplaneapproximate')
# Main court window positions from260/261: 9+9 eachlongwall and4+4 eachshortwall perlevel.
for side,plane in [('S',16.715),('N',74.419)]:
 for level in [0,1]:
  for segment,(a,b) in enumerate([(52.0,85.0),(109.0,141.5)]):
   for i,y in enumerate(np.linspace(a,b,9)):win(f'Court long{side} segment{segment} window{i} level{level}',side,plane,float(y),2.1,.9+F2*level,2.45,1,1,'PDF260/261 nineplanwindowmarks eachsideofstair; height/sill/1x1grid AUTHOR DISPLAY PROXY, exactelevationunknown')
for side,plane in [('E',46.802),('W',146.802)]:
 for level in [0,1]:
  for segment,(a,b) in enumerate([(22.5,35.5),(56.5,69.0)]):
   for i,x in enumerate(np.linspace(a,b,4)):win(f'Court short{side} segment{segment} window{i} level{level}',side,plane,float(x),2.1,.9+F2*level,2.45,1,1,'PDF260/261 fourplanwindowmarks eachsideofstair; unknownheight/grid plainproxy, not mirroredexternalfacade')
# Horizontal RC floor/facade bands, approximate profile from263–267.
for side,plane,a,b in [('N',0,0,LENGTH),('S',WIDTH,0,LENGTH),('W',0,0,WIDTH),('E',LENGTH,45.64,WIDTH),('E',173.983,-5.087,85.90)]:
 for z,t in [(.15,.12),(.55,.10),(F2-.18,.25),(F2+.22,.15),(RC-.4,.35)]:panel('Facade RC horizontal band',side,plane,a,b,z,z+t,.16,1,'PDF263–267 horizontalfloor/cornice bands; exactprofile/rasterdetailapproximate')

# Diagonal courtyard corners: one ground door and two plain upper openings per plan.
def facet_panel(name,c,t,n,u0,u1,z0,z1,depth,mat,ev):
 pts=[]
 for u in [u0,u1]:
  for off in [-.03,depth]:
   for z in [z0,z1]:pts.append([c[0]+t[0]*u+n[0]*off,c[1]+t[1]*u+n[1]*off,z])
 add(name,hull(pts),mat,ev)
for x,dx in [(16.715,1),(74.419,-1)]:
 for y,dy in [(46.802,1),(146.802,-1)]:
  c=np.array([x+dx*3.63/2,y+dy*3.63/2]);n=np.array([dx,dy])/math.sqrt(2);t=np.array([-dy,dx])/math.sqrt(2)
  for ua,ub in [(-1.15,-.065),(.065,1.15)]:
   pts=[[c[0]+t[0]*u+n[0]*off,c[1]+t[1]*u+n[1]*off,z]for u in [ua,ub]for off in [-.25,.4]for z in [.12,3.5]]
   cut('Court diagonal ground door cutter',hull(pts),'260 eachchamfer has double-leaf door, notwindow; twoleafrecesses preservecentralframe, blinddepthauthorproxy')
  facet_panel('Court diagonal dark doorback',c-n*.26,t,n,-1.15,1.15,.12,3.5,.025,5,'Opaque blind doorway backing not completecirculation')
  for u in [-1.18,0,1.18]:facet_panel('Court diagonal doorframe',c,t,n,u-.055,u+.055,.10,3.60,.18,3,'Schematic paired-doorframe fromplan, joineryunknown')
  facet_panel('Court diagonal doorlintel',c,t,n,-1.24,1.24,3.48,3.65,.18,1,'Sourcegrounddoor, approximateheight')
  for u in [-1.1,1.1]:
   facet_panel('Court diagonal upper opening surround',c,t,n,u-.63,u+.63,F2+.85,F2+2.85,.10,3,'261 twochamferopeningmarks; sill/height/grid authorproxy')
   facet_panel('Court diagonal upper plain pane',c,t,n,u-.53,u+.53,F2+.95,F2+2.75,.13,4,'Neutral1x1opaquepane, exactwindowpatternunknown')
# Two source-confirmed small-court stair/notch accesses, not decorativewindows.
for side,x,y in [('S',16.715,13.4),('N',74.419,13.4)]:
 recess('Small court corner access',side,x,y,1.8,.1,2.9,.25,'260 smallcourt NW/SW stair/notchaccess; neutral blindopening, exactstairinterior not modeled')

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
o=ET.SubElement(res,E('object'),id='2',type='model',name='Songshan manufacturing hall surveyed exterior2004-01');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':.5*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'January2004 surveyed manufacturinghall,1939RC; threecourts and thinraised lateriron-sheet roofs. Sourcecaptionconflicts disclosed, graphdimensionsapprox±3%, level-specificannex/neutralwindowproxies. No fullinteriors, original1939restoration, trialprint or safetyclaim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
