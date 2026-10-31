#!/usr/bin/env python3
"""TCFSH History Hall: exterior of the March 2012 survey, A-series existing state.
Meters in construction; output nominal 1:150 mm. Not a construction survey or current restoration.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
SCALE=1000/150
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e} for i,n,c,e in [
 ('wall','Survey cream plaster','#D6D2B6','2012 report photographs; nominal clean color, weathering omitted'),
 ('roof','2012 muted red corrugated metal','#8C4655','Survey p5/p6 photos and A2-4 metal sheet note, not 2015 roof'),
 ('trim','Pale masonry trim','#E8E1CB','2012 photographs; proportional relief'),
 ('glass','Dark closed window relief','#354340','Opaque printable relief; no interior or glass transparency claim'),
 ('wood','Dark timber door relief','#59493C','Survey entrance photograph; shutters simplified closed'),
 ('plinth','Grey plinth and stairs','#8D8D7F','2012 photographs; nominal color'),
 ('base','Authored neutral support','#B3B2A7','Not surveyed terrain; simplified single flat display base')]]
P={'state':'March 2012 A-series existing survey, not current building','length_axis_m':30.10,'width_axis_m':20.11,'ridge_height_front_datum_m':12.7787,'side_drawing_total_height_m':12.8617,'nominal_eave_height_m':7.36,'scale_denominator':150,'surface_detail':'Opaque closed relief openings and frames, not interior voids','estimated':'Outer wall offsets, front/rear projection depths, window positions traced from A-series images; small trim nominal','terrain':'Flat authored base, not the varying surveyed ground levels'}
(ROOT/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2));items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat=0,evidence='A-series existing drawing, dimensions traced proportionally where not annotated'):
 s=s.translate([0,0,.45]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='A-series existing drawing, proportional detail'):add(name,box(a,b),mat,evidence)
def xz_prism(pts,y,depth):return mf.CrossSection([pts]).extrude(depth).rotate([90,0,0]).translate([0,y+depth,0])
W=10.255;L=15.25;E=7.36;R=12.7787
bx('Authored flat support',[-11.15,-17.1,-.45],[11.15,18.1,0],6)
# Principal solid exterior, not an invented interior layout.
add('Main rectangular hall and two gables',xz_prism([(-W,0),(W,0),(W,E),(0,R-.12),(-W,E)],-L,2*L))
bx('Main grey plinth',[-W-.035,-L-.035,0],[W+.035,L+.035,.72],5)
# Two planes and observed representative corrugations. Every ridge is attached to roof slab.
for side in [-1,1]:
 xa,xb=sorted([0,side*(W+.18)])
 def rz(x):return R-abs(x)*(R-E)/(W+.18)
 add('Red metal roof '+str(side),xz_prism([(xa,rz(xa)-.13),(xb,rz(xb)-.13),(xb,rz(xb)+.06),(xa,rz(xa)+.06)],-L-.15,2*L+.30),1,'A2-4 corrugated metal roof; 2012 photographs red rather than restored grey')
 for j,y in enumerate(np.linspace(-L-.10,L+.10,76)):
  add('Representative attached roof rib '+str((side,j)),xz_prism([(xa,rz(xa)),(xb,rz(xb)),(xb,rz(xb)+.10),(xa,rz(xa)+.10)],y,.055),1,'Representative corrugation spacing; not a surveyed sheet count')
bx('Roof ridge cap',[-.11,-L-.2,R-.06],[.11,L+.2,R+.12],1)
# Horizontal belt and raised vertical pilasters, based on the 7 bays of high windows.
for side in [-1,1]:
 x=side*W
 bx('Long side belt '+str(side),[min(x-.12,x+.12),-L,2.62],[max(x-.12,x+.12),L,2.78],2)
 for y in [-L,L]: bx('Long side corner pier '+str((side,y)),[x-.13,y-.15,.72],[x+.13,y+.15,E+.02],2)
 # source X2..X9 enclose the 7 upper-window bays; lower openings are door/window/window/door/window/window/door
 for j,y in enumerate(np.linspace(-10.02,10.02,7)):
  for yy in [y-1.50,y+1.50]:bx('Upper bay pilaster '+str((side,j,yy)),[x-.07,yy-.045,2.77],[x+.07,yy+.045,6.73],2)
  bx('Upper bay top border '+str((side,j)),[x-.07,y-1.50,6.69],[x+.07,y+1.50,6.78],2)
 # windows/doors are backed by solid hall, not holes; the outer dark face is slightly proud to retain colors in printable mesh.
def facade_rect(name,plane,coord,u,z,w,h,mat=3,cols=2,rows=4):
 # Face coordinates u,z; front/back have x=u, long sides y=u.
 depth=.07;out=1 if coord>0 else -1
 lo,hi=sorted([coord-out*.015,coord+out*depth])
 def slab(n,uu,zz,ww,hh,m,dextra=0):
  a,b=sorted([coord-out*.015,coord+out*(depth+dextra)])
  if plane=='y':bx(n,[uu-ww/2,a,zz],[uu+ww/2,b,zz+hh],m)
  else:bx(n,[a,uu-ww/2,zz],[b,uu+ww/2,zz+hh],m)
 slab(name+' opaque recess representation',u,z,w,h,mat)
 # only backing-supported solid bars; no detached miniature parts.
 for uu in [u-w/2,u+w/2]:slab(name+' edge',uu,z-.035,.075,h+.07,2,.045)
 for zz in [z,z+h]:slab(name+' sill/head',u,zz-.04,w+.1,.08,2,.05)
 for k in range(1,cols):slab(name+' mullion',u-w/2+k*w/cols,z,.055,h,2,.045)
 for k in range(1,rows):slab(name+' transom',u,z+k*h/rows-.025,w,.05,2,.045)
for side in [-1,1]:
 for j,y in enumerate(np.linspace(-10.02,10.02,7)):
  facade_rect('High window '+str((side,j+1)),'x',side*W,y,3.12,.66,2.40,3,1,5)
  if j in [0,3,6]:facade_rect('Lower door '+str((side,j+1)),'x',side*W,y,.17,2.70,2.40,4,4,5)
  else:facade_rect('Lower horizontal window '+str((side,j+1)),'x',side*W,y,.98,2.95,1.47,3,8,4)
 for y in [-13.6,13.6]:facade_rect('Small end bay inset '+str((side,y)),'x',side*W,y,1.19,.65,.65,3,1,1)
 # three shallow steps at each external door, simplified from elevations
 for y in [-10.02,0,10.02]:
  for k in range(3):
   a,b=sorted([side*(W-.05),side*(W+.55-.14*k)])
   bx('Side entry step '+str((side,y,k)),[a,y-1.5,0],[b,y+1.5,.06+.06*k],5)
# Front: three doors, shallow four-column porch, broad lower windows and six-point angular vents.
for z in [.72,2.63]: bx('Front belt '+str(z),[-W,-L-.12,z],[W,-L+.02,z+.12],2)
for x in [-6.0,6.0]:facade_rect('Front low window '+str(x),'y',-L,x,1.0,2.95,1.48,3,8,4)
for x in [-1.875,0,1.875]:facade_rect('Front double door '+str(x),'y',-L-.02,x,.355,1.40,2.40,4,2,5)
# porch platform / steps are connected, depth proportional to A2-1 (not directly dimensioned)
for k in range(3):bx('Front step '+str(k),[-3.4,-L-1.15+.24*k,0],[3.4,-L+.06,.12*(k+1)],5)
for x in [-2.79,-.91,.91,2.79]:
 bx('Front porch column '+str(x),[x-.14,-L-.65,.35],[x+.14,-L+.03,2.97],2)
 bx('Front column plinth '+str(x),[x-.20,-L-.70,.35],[x+.20,-L+.03,.83],5)
bx('Front porch canopy',[-3.65,-L-1.0,2.93],[3.65,-L+.06,3.09],2)
# Central raised window-and-ornament frame over front entrance.
bx('Front central raised panel',[-2.95,-L-.075,3.03],[2.95,-L+.03,7.27],2)
for x in [-1.875,0,1.875]:
 facade_rect('Front upper window '+str(x),'y',-L-.08,x,3.18,1.42,2.46,3,4,6)
 facade_rect('Front ornament frame '+str(x),'y',-L-.08,x,5.91,1.42,.64,0,1,1)
 # restrained central ornamental lozenge, no invented inscription
 add('Front small lozenge '+str(x),xz_prism([(x-.24,6.20),(x,6.08),(x+.24,6.20),(x,6.32)],-L-.215,.075),4,'Central dark geometric motif in A3-1; ornamental carving simplified')
for z in [3.05,7.20]:bx('Central frame horizontal edge '+str(z),[-3.10,-L-.20,z],[3.10,-L+.02,z+.10],2)
for x in [-2.9,2.9]:bx('Central frame vertical edge '+str(x),[x-.06,-L-.18,3.06],[x+.06,-L+.02,7.25],2)
# All gable high vents from A3-1. Rear not copied from front.
for side in [-1,1]:
 for x in [-.55,0,.55]:facade_rect('Gable vent '+str((side,x)),'y',side*L,x,7.74,.35,1.15,3,1,3)
for x in [-6.05,6.05]:
 pts=[(x,5.27),(x+.25,5.03),(x+.42,5.03),(x+.42,4.18),(x+.25,4.18),(x,3.94),(x-.25,4.18),(x-.42,4.18),(x-.42,5.03),(x-.25,5.03)]
 add('Front angular vent trim '+str(x),xz_prism(pts[::-1],-L-.16,.18),2,'A3-1 angular decorative vent, simplified outline')
 cx=x;cz=4.605;inner=[(cx+(a-cx)*.70,cz+(b-cz)*.77) for a,b in pts]
 add('Front angular dark vent '+str(x),xz_prism(inner[::-1],-L-.205,.06),3)
 for dx in [-.16,0,.16]:bx('Angular vent grille '+str((x,dx)),[x+dx-.025,-L-.23,4.23],[x+dx+.025,-L-.15,4.98],2)
# Rear central stepped low projection (A2-1); plain closed face as existing-elevation A3-1.
rear_poly=[(-3.48,L-.1),(3.48,L-.1),(3.48,L+.68),(2.5,L+.68),(2.5,L+2.35),(-2.5,L+2.35),(-2.5,L+.68),(-3.48,L+.68)]
add('Rear low stepped projection',mf.CrossSection([rear_poly]).extrude(3.65),0,'A2-1 traced stepped footprint, A3-1 existing low closed back; depth estimated')
add('Rear projection flat cap',mf.CrossSection([rear_poly]).offset(.10).extrude(.14).translate([0,0,3.64]),2)
for x in [-3.22,3.22]:
 bx('Rear tall slender pilaster '+str(x),[x-.11,L-.04,3.65],[x+.11,L+.17,10.0],2)
 bx('Rear pilaster cap '+str(x),[x-.19,L-.05,9.93],[x+.19,L+.24,10.08],2)
for x0,x1 in [(-W,-3.5),(3.5,W)]:bx('Rear lower belt '+str(x0),[x0,L-.02,2.63],[x1,L+.10,2.75],2)
# No surrounding vegetation, signs/text, wiring, pipes, temporary objects, flaking-plaster meshes or invisible interior.
for o,i in zip(ops,items):assert i.status()==mf.Error.NoError,(o,i.status())
s=items[0]
for o,i in zip(ops[1:],items[1:]):
 s=s+i
 assert s.status()==mf.Error.NoError,(o,s.status())
s=s.set_tolerance(.0001).simplify(.0001)
m=s.to_mesh64();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
# Weld duplicate material-boundary positions, retaining each surface triangle's real original material.
v,inv=np.unique(np.round(v,7),axis=0,return_inverse=True);f=inv[f]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='TCFSH History Hall 2012 survey exterior');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
for row in v:ET.SubElement(vs,E('vertex'),**{k:f'{float(a):.7f}' for k,a in zip('xyz',row)})
for row,c in zip(f,mi):ET.SubElement(ts,E('triangle'),v1=str(row[0]),v2=str(row[1]),v3=str(row[2]),pid='1',p1=str(c),p2=str(c),p3=str(c))
b=ET.SubElement(root,E('build'));ET.SubElement(b,E('item'),objectid='2')
with zipfile.ZipFile(ROOT/'model.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats-package.relationships/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'.replace('http://schemas.openxmlformats-package.relationships/2006/relationships','http://schemas.openxmlformats.org/package/2006/relationships'))
 z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
parts=[]
for op,item in zip(ops,items):
 q=item.to_mesh();parts.append({**op,'vertices':(np.asarray(q.vert_properties)[:,:3]*SCALE).tolist(),'faces':np.asarray(q.tri_verts).tolist()})
(ROOT/'construction-parts.json').write_text(json.dumps(parts,separators=(',',':')));(ROOT/'editable-parts.json').write_text(json.dumps({'palette':PALETTE,'features':ops},indent=2))
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Complete principal exterior in 2012 A-series survey state; nominal reconciled heights and proportional details, no interior, current restoration or site terrain claim'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
