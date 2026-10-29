#!/usr/bin/env python3
"""Wuqi police station and connected Residence A:2014-10 survey,2015-06 report."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
MODEL_MM_PER_METRE=10.;INTERNAL=1000.;SCALE=MODEL_MM_PER_METRE/INTERNAL;BASE=.2
PALETTE=[{'id':str(i),'name':n,'hex':c,'evidence':'Uncalibrated2015report surveyphoto finish proxy, notoriginal1931 exactcolor'}for i,(n,c)in enumerate([('Survey cream paint','#D7CAA0'),('Pale stone and cornice','#C3BCA5'),('Dark roof tile proxy','#55534B'),('Blue grey wood frames','#50616C'),('Opaque glazing','#71848A'),('Blind recess backing','#303A3F'),('Residence red brick','#965B43'),('Grey base and RC','#91958D'),('Authored display support','#C8C5B7'),('Weatherboard wood','#665F4E'),('Existing red lamp','#793B32')])]
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
 ev='Survey2014-10 opening on2015report Appendix3; opening-positions.json controls, opaque proxy notcompleteinterior'
 cs=outline(u,w,z,h,head,rise);shaped_panel(n+' pale surround',side,p,cs.offset(.09*INTERNAL,mf.JoinType.Miter),.055,1,ev)
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
 shaped_panel(n+' frame and grid',side,p,(grid^cs)+(cs-cs.offset(-.04*INTERNAL,mf.JoinType.Miter)),.14,3,ev+'; frames coarsened legibilityproxy')

EV='Volume3 current-condition sheets94–109 dated2014-10-30; independently traced nominal controls ±3%/local0.2m'
# Authored 2mm connected display support, not surveyed terrain.
bx('Authored support',[-.65,-1.0,-BASE],[12.75,16.0,0],8,'Authored display and connectivity support, not historical paving')
# Phase-separated exterior masses, not inferred room interiors.
bx('1931 office lower platform',[5.67,-.12,0],[12.042,5.95,.42],7,EV)
add('1931 office flat-roof body',box([5.67,0,.35],[12.042,5.95,4.50])-box([7.47,-.7,.42],[10.37,.45,4.28]),0,EV+'; recessed entry per94')
bx('1931 actual roof slab',[5.57,-.12,4.44],[12.142,6.05,4.58],7,EV+'; slab is lower than parapets')
for x in [5.67,11.84]:bx('Side parapet '+str(x),[x,0,4.50],[x+.20,5.95,5.25],0,EV)
bx('Rear parapet',[5.67,5.75,4.50],[12.042,5.95,5.25],0,EV)
# Original front tall asymmetrical parapet; graphical trace of elevation99.
front_profile=[[5.67,4.5],[12.042,4.5],[12.042,5.70],[11.88,5.74],[11.68,5.82],[10.58,5.82],[10.58,6.38],[10.45,6.51],[10.38,6.72],[8.36,6.72],[8.36,6.79],[8.14,6.79],[8.14,6.85],[7.81,6.85],[7.75,6.68],[7.63,6.50],[7.53,6.43],[7.53,5.40],[7.07,5.40],[7.07,6.50],[6.72,6.50],[6.72,5.20],[5.99,5.20],[5.99,5.0],[5.67,5.0]]
shaped_panel('Asymmetrical front ornamental parapet','F',0,section(front_profile),.20,0,EV+'; original silhouette traced99, no reconstructed emblem')
# Horizontal cornice and plinth at the exposed original front and side.
for side,p,u0,u1 in [('F',0,5.67,12.042),('R',12.042,0,5.95)]:
 panel('Cornice lower '+side,side,p,u0-.05,u1+.05,4.30,4.47,.17,1,EV)
 panel('Cornice upper '+side,side,p,u0-.12,u1+.12,4.47,4.61,.20,1,EV)
 for a,b in ([(5.67,7.47),(10.37,12.042)] if side=='F' else [(0,3.73),(5.47,5.95)]):panel('Stone plinth belt '+side+str(a),side,p,a,b,.62,.82,.06,1,EV+'; interrupted at doorway')
# Later front timber wing is a different phase, roof ridge parallel localx.
bx('Timber office plinth',[0,0,0],[5.67,4.93,.42],7,EV)
bx('Timber office weatherboard body',[0,0,.42],[5.67,4.93,3.38],0,EV)
add('Timber office gable roof',gable_x(-.28,5.76,-.30,5.23,3.32,4.80)-gable_x(-.35,5.85,-.21,5.14,3.15,4.66),2,EV+'; ridge alongx, thin roofskin preserves visible weatherboard gable')
add('Timber office solid gable backing',gable_x(0,5.67,0,4.93,3.32,4.68),0,EV+';weatherboardgableunderroofnotgreyroofmass')
# Left exposed weatherboard gable no invented openings.
add('Timber north gable weatherboard',faceprofile(section([[0,3.32],[4.93,3.32],[2.465,4.68]]),'L',.01,.055),0,EV+'; northgable102 solid')
for z in np.arange(.65,4.6,.22):
 y0=0 if z<3.32 else (z-3.32)/(4.68-3.32)*2.465;y1=4.93-y0
 if y1>y0:panel('North weatherboard joint %.2f'%z,'L',0,y0,y1,z,z+.022,.070,1,EV+'; coarsened joint spacing, projection clears gablepanel for visible board seams')
# Raised tilecourses are stylized surveyed covering, not exact tile counts.
for x in np.arange(-.22,5.74,.22):
 add('Timber roof tile ridge %.2f'%x,beam([x,-.30,3.35],[x,2.465,4.83],.026),2,EV+'; coarsened roof texture')
 add('Timber roof tile rear %.2f'%x,beam([x,2.465,4.83],[x,5.23,3.35],.026),2,EV+'; coarsened roof texture')
add('Timber main ridge cap',beam([-.28,2.465,4.82],[5.76,2.465,4.82],.085),1,EV)
# Later RC block. Flat roof has no added decorative merlons.
bx('Later two-storey RC mass',[0,4.93,0],[3.52,10.227,6.65],0,EV)
bx('Later RC roof finish',[-.035,4.91,6.57],[3.555,10.262,6.67],7,EV)
panel('RC floor band','L',0,4.93,10.227,3.30,3.39,.025,1,EV)
panel('RC rear floor band','B',10.227,0,3.52,3.30,3.39,.025,1,EV)
# Front middle door wall is set back, not an invented projecting porch.
# Recess is subtracted from body before door details, not globally from later inserted frames.
for j in range(3):
 bx('Three entry steps '+str(j),[7.43,-.62+j*.20,j*.14],[10.41,.50,(j+1)*.14],1,EV+';plinth.42m and3steps, treaddepth approximate')
for x in [6.54,11.06]:
 panel('Front pilaster lower %.2f'%x,'F',0,x-.45,x+.45,.84,4.50,.065,1,EV)
 panel('Front pilaster capital %.2f'%x,'F',0,x-.55,x+.55,4.50,4.74,.12,1,EV)
 for xx in [x-.12,x+.12]:panel('Front paired vertical ornament %.2f'%xx,'F',0,xx-.035,xx+.035,3.63,4.49,.13,1,EV+';simplified incised motif')
# Lintels and dentils above recessed entry.
for j in range(7):
 x=7.44+j*.47;panel('Entry cornice dentil%d'%j,'F',0,x-.045,x+.045,4.03,4.34,.17,1,EV)
panel('Entry long lintel','F',.45,7.40,10.45,3.72,3.87,.10,1,EV)
# Existing red lamp and flanking vegetal relief only; missing central emblem not reconstructed.
add('Existing central red lamp',mf.Manifold.sphere(.075*INTERNAL,12).translate([8.80*INTERNAL,.28*INTERNAL,3.65*INTERNAL]),10,'Volume1p181 missingcentralemblem replaced byredlamp; shape approximate')
for sign in [-1,1]:
 for j in range(6):
  xx=8.8+sign*(.12+j*.065);zz=3.60-j*.055
  add('Simplified flanking foliage %d_%d'%(sign,j),beam([xx,.44,zz],[xx+sign*.09,.43,zz-.07],.035),1,'Volume1p181 survivingvegetalrelief; notsymbol reconstruction')

add('Lamp wall attachment',beam([8.80,.28,3.65],[8.80,.47,3.65],.035),1,'Authored concealed connection for lamp relief')
# Openings use opaque glazing skins rather than unsupported invented interiors.
def sash(n,side,p,u,w,z,h,cols=6,rows=4,transom=.32):
 window(n,side,p,u,w,z,h,'rect',cols,rows)
 if transom:window(n+' separate transom',side,p,u,w,z+h+.06,transom,'rect',cols,1)
def door(n,side,p,u,w,z,h,cols=4,rows=3,transom=.3):
 panel(n+' opaque lower leaves',side,p,u-w/2,u+w/2,z,z+.68,.10,3,EV+';source opening map')
 for k in [0,1]:
  c=u-w/4+k*w/2
  panel(n+' lower inset%d'%k,side,p,c-w*.20,c+w*.20,z+.1,z+.57,.115,1,EV+';opaque lowerpanels')
 window(n+' upper glazed leaves',side,p,u,w,z+.68,h-.68,'rect',cols,rows)
 if transom:window(n+' separate transom',side,p,u,w,z+h+.06,transom,'rect',cols,1)
def louver(n,side,p,u,w,z,h):
 panel(n+' dark backing',side,p,u-w/2,u+w/2,z,z+h,.09,5,EV)
 for zz in np.arange(z,z+h,.055):panel(n+' slat %.3f'%zz,side,p,u-w/2,u+w/2,zz,min(zz+.024,z+h),.14,3,EV+';coarsened louvers')
# Front timber paired windows: each leaf3x4, measured different widths.
sash('A102 front left','F',0,1.70,1.370,1.27,1.510,6,4,0)
sash('A102 front right','F',0,4.02,1.364,1.27,1.467,6,4,0)
for x in [6.54,11.06]:
 window('A101 narrow sash%.2f'%x,'F',-.065,x,.523,1.16,1.504,'rect',2,4,rails=[0,.52,.74,1.29,1.504])
 louver('A101 narrow louver%.2f'%x,'F',-.065,x,.587,2.74,.40)
 panel('A101 narrow lintel%.2f'%x,'F',0,x-.40,x+.40,3.16,3.36,.13,1,EV)
door('A101 entrance','F',.45,8.80,1.734,.42,1.918,6,3,0)
for x in [8.80-1.734/4,8.80+1.734/4]:louver('Entrance louver%.2f'%x,'F',.45,x,.80,2.40,.42)
window('Entrance upper sixpane strip','F',.45,8.80,1.81,2.91,.23,'rect',6,1)
for x in [7.62,9.98]:
 panel('Entrance upright %.2f'%x,'F',.45,x-.035,x+.035,.90,2.95,.15,1,EV)
 for zz in np.arange(.95,2.94,.24):panel('Entrance stoneblock %.2f_%.2f'%(x,zz),'F',.45,x-.29 if x<8 else x+.06,x-.06 if x<8 else x+.29,zz,zz+.21,.08,1,EV)
# Exterior long side corresponding source left elevation101, local+x.
sash('A101 side window','R',12.042,1.70,1.664,1.27,1.59,6,4,.35)
door('A101 side sliding door','R',12.042,4.60,1.723,.42,1.781,4,3,.42)
# RC rear: independent ground/upper sizes, not mirrored.
window('A103 rear ground','B',10.227,1.70,.822,1.0,1.502,'rect',2,2,rails=[0,1.16,1.502])
window('A103 rear upper','B',10.227,1.94,1.2,4.62,1.5,'rect',2,2,rails=[0,1.16,1.5])
window('A103 north lower large','L',0,8.55,1.183,1.17,1.893,'rect',2,2,rails=[0,1.48,1.893])
window('A103 north lower small','L',0,6.44,.679,1.76,.49,'rect',2,1)
window('A103 north upper large','L',0,8.55,1.194,4.54,1.512,'rect',2,2,rails=[0,1.17,1.512])
panel('A103 unidentified upper blindplate','L',0,6.14,6.74,5.58,5.98,.025,1,EV+';notestablishedwindow, no glazing')

for u in [1.70,4.02]:
 for x in [u-.23,u+.23]:panel('Timber front wall trim %.2f'%x,'F',0,x-.022,x+.022,2.85,3.25,.035,1,EV+';walltrimnotglazedtransom')
# Attached Residence A: stepped footprint and lower north corridor.
Apoly=[[4.16,5.95],[12.042,5.95],[12.042,13.51],[9.24,13.51],[9.24,15.367],[4.16,15.367]]
def prism(poly,z,h):return section(poly).extrude(h*INTERNAL).translate([0,0,z*INTERNAL])
add('Residence A plinth',prism(Apoly,0,.45),7,EV)
mainpoly=[[5.30,5.95],[12.042,5.95],[12.042,13.51],[9.24,13.51],[9.24,15.367],[5.30,15.367]]
add('Residence A redbrick body',prism(mainpoly,.35,3.40),6,EV)
bx('Residence A north low corridor',[4.16,5.95,.35],[5.32,15.367,2.80],9,EV+';notfullheightmainbody')
# Asymmetric pitched roof planes retain measured nominal ridge rather than auto-centred ridge.
roofpoly=[[5.15,5.87],[12.22,5.87],[12.22,13.65],[9.38,13.65],[9.38,15.50],[5.15,15.50]]
roof=hull([[5.15,5.87,3.68],[12.22,5.87,3.68],[5.15,15.50,3.68],[12.22,15.50,3.68],[8.5,5.87,5.76],[8.5,15.50,5.76]])
add('Residence A stepped main roof',roof^prism(roofpoly,0,8),2,EV+';97/98notchedroofwithclosedverticalreturn')
lean=hull([[4.02,5.87,2.78],[5.35,5.87,3.13],[4.02,15.50,2.78],[5.35,15.50,3.13],[4.02,5.87,2.72],[4.02,15.50,2.72]])
add('Residence A low north lean-to',lean,2,EV+';108/109 lowcorridor roof distinct')
# Coarse linear roof tile texture follows planes, not full exact tile count.
for y in np.arange(5.92,15.49,.23):
 end=12.22 if y<13.65 else 9.38
 zr=5.76-(end-8.5)/(12.22-8.5)*(5.76-3.68)
 add('A tile west %.2f'%y,beam([5.15,y,3.70],[8.5,y,5.78],.025),2,EV+';coarsened tilecourseproxy')
 add('A tile east %.2f'%y,beam([8.5,y,5.78],[end,y,zr+.02],.025),2,EV+';coarsened tilecourseproxy')
add('Residence A ridge cap',beam([8.5,5.87,5.78],[8.5,15.50,5.78],.08),1,EV)
# Rear decorative gable is the stepped far-end portion, not an invented coplanar full-width rear wall.
rearprof=[[4.16,.40],[9.24,.40],[9.24,5.64],[8.72,5.98],[8.72,6.40],[8.30,6.40],[8.30,6.08],[4.16,3.64]]
shaped_panel('Residence A far rear gable brick','B',15.367,section(rearprof),.18,6,EV+';ornamentalbackgablehigherthanactualroof;twoendplanes')
rearline=[[4.16,3.64],[8.30,6.08],[8.30,6.40],[8.72,6.40],[8.72,5.98],[9.24,5.64]]
for a,b in zip(rearline,rearline[1:]):add('Rear gable coping '+str(a),beam([a[0],15.54,a[1]],[b[0],15.54,b[1]],.105),1,EV+';coarsened mouldedcoping')
# Short rear face follows same roof slope, below the steppednotch, no fake outdoor roofhole.
shortprof=[[9.24,.40],[12.042,.40],[12.042,3.75],[9.24,5.35]]
shaped_panel('Residence A short rear brick gable','B',13.51,section(shortprof),.18,6,EV)
add('Residence A short rear coping',beam([9.24,13.69,5.35],[12.042,13.69,3.75],.075),1,EV)
# Low symbolic mortar courses; not measured brickcounts. Sideandbackonly, openingscover these.
for z in np.arange(.68,3.60,.18):
 panel('A side mortar %.2f'%z,'R',12.042,5.95,13.51,z,z+.016,.012,1,EV+';stylized masonry finishproxy')
 panel('A farrear mortar %.2f'%z,'B',15.547,4.16,9.24,z,z+.016,.012,1,EV+';stylized masonry finishproxy')
 panel('A shortrear mortar %.2f'%z,'B',13.69,9.24,12.042,z,z+.016,.012,1,EV+';stylized masonry finishproxy')
# Existing altered opening at A202 is not restored to paired identical windows.
panel('A202 altered left opaque area','R',12.042,7.391,8.22,1.08,2.457,.09,7,EV+';photo/table current alteration, no guessed original sash')
window('A202 surviving right sash','R',12.042,8.6345,.829,1.08,1.377,'rect',3,4)
door('A201 side entrance','R',12.042,10.52,1.727,.20,1.803,4,3,0)
window('A201 wide separate upper transom','R',12.042,10.52,2.12,2.42,.35,'rect',4,1)
window('A208 side window','R',12.042,12.47,.955,1.08,1.424,'rect',2,4)
panel('Far stepped service doorway neutral','R',9.24,13.69,14.79,.10,2.05,.09,9,EV+';obscured service door no invented panegrid')
door('Residence rear door','B',13.69,10.43,1.647,.15,1.767,6,3,0)
panel('Rear door shallow canopy','B',13.69,9.47,11.37,2.18,2.30,.32,1,EV+';canopydepthgraphicalproxy')
# Infilled old tall door outlines with current smaller windows.
for x,w in [(8.24,.693),(6.74,.601)]:
 panel('Filled old tallbay %.2f'%x,'B',15.547,x-w/2-.08,x+w/2+.08,.98,2.66,.035,1,EV+';filledoldopeningnotrestored door')
window('Rear tallbay1 current small window','B',15.582,8.24,.693,1.64,.491,'rect',2,1)
window('Rear tallbay2 current small window','B',15.582,6.74,.601,1.84,.695,'rect',2,2)
window('Rear horizontal window','B',15.547,5.41,1.312,1.84,.702,'rect',4,2)
window('Rear gable window','B',15.547,8.55,.50,4.20,.72,'rect',2,2)
# Corridor four paired groups; fronts wide3x4 perleaf, rear two2x4.
for j,(u,w,cols) in enumerate([(7.715,1.75,6),(9.545,1.75,6),(11.18,1.30,4),(12.52,1.30,4)]):
 panel('North corridor bottom panel%d'%j,'L',4.16,u-w/2,u+w/2,.60,.96,.10,9,EV+';105C-C completefourgroup exterior')
 window('North corridor glazing%d'%j,'L',4.16,u,w,.96,1.39,'rect',cols,4)
 window('North corridor transom%d'%j,'L',4.16,u,w,2.41,.25,'rect',cols,1)
# Tall rectangular feature: its function is unconfirmed, not a chimney.
for x in [8.30,8.94]:
 for y in [4.90,5.74]:bx('Tall rectangular feature upright %.2f %.2f'%(x,y),[x,y,4.52],[x+.06,y+.06,9.60],1,EV+';99/101/98rearplacement,coarsenedframe')
for z in [5.42,6.75,7.72,8.59,9.54]:
 for y in [4.90,5.74]:bx('Tall rectangular feature crossbar %.2f %.2f'%(z,y),[8.30,y,z],[9.0,y+.06,z+.06],1,EV+';openrectangularframe,notfilledshaft')
 for x in [8.30,8.94]:bx('Tall rectangular feature depthbar %.2f %.2f'%(z,x),[x,4.90,z],[x+.06,5.80,z+.055],1,EV+';depthnominalproxy')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='Wuqi Police Station and connected Residence A survey2014-10');me=ET.SubElement(o,E('mesh'));vs=ET.SubElement(me,E('vertices'));ts=ET.SubElement(me,E('triangles'))
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
r={'pre_simplify_components':pre_simplify_components,'simplification_tolerance_model_mm':2.*SCALE,'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum())for i,p in enumerate(PALETTE)},'source_metres_to_model_mm':MODEL_MM_PER_METRE,'scope':'October2014 surveyed exterior of Wuqi Police Station with connected Residence A, June2015 report; includes later timber and two-storey RC extensions. No separate B/C/D residences, neighbouring structures, restorationproposals, fullinterior, sourceimagery, trialprint or safetyclaim.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
