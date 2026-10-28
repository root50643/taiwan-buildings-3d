#!/usr/bin/env python3
"""First General Building: main linear wing and glass tower, bounded historical exterior."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':'wall','name':'Warm beige upper walls','hex':'#B6A38B','evidence':'official historical photos, uncalibrated'}, {'id':'glass','name':'Opaque green tower glass','hex':'#5C9994','evidence':'observed green glass shaft'}, {'id':'frame','name':'Blue green frames and sunshades','hex':'#587570','evidence':'observed exterior fins'}, {'id':'window','name':'Dark muted windows','hex':'#354D4C','evidence':'visible opaque window pattern'}, {'id':'stone','name':'Grey tower stone','hex':'#A7A7A0','evidence':'observed grey end masses'}, {'id':'roof','name':'Neutral roof plane','hex':'#A4A79C','evidence':'unseen roof equipment omitted'}, {'id':'base','name':'Display support','hex':'#BFC3B9','evidence':'authored support, not real terrain'}]
SCALE=2.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.65]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Estimated photo proportions; not surveyed'):add(name,box(a,b),mat,evidence)
L,D,H=104.,13.,19.6
bx('Display base',[-8,-3,-.65],[L+3,D+3,0],6,'Cropped artificial base; adjacent hall, sunken courtyard, road and landscape excluded')
# Two accommodation blocks separated by the central staircase, verified by 2024 renovation floor plans.
bx('Recessed lower core',[0,1.25,0],[L,D-1.25,10.2],3,'Two lower storeys supported by photo2/3; internal spaces not modeled')
bx('Upper long-wing core',[0,0,10.0],[L,D,H],0,'Four-storey main wing. 2024 plan confirms two ten-room segments per side on 3F/4F')
# End stone masses and thin glass tower; glass front faces local -X.
bx('Tower left stone cheek',[-4,0,0],[1,4.0,23.0],4,'Grey flanking cheek in front-end photo4')
bx('Tower right stone cheek',[-4,9.0,0],[1,13,23.0],4)
bx('End opaque glass shaft',[-5.5,4.0,0],[.8,9.0,29.0],1,'Tall narrow green tower, not broad curtain wall; approximate relative height')
bx('Glass tower top cap',[-5.65,3.85,28.75],[.95,9.15,29.08],3,'Thin dark flat tower cap')
for z in np.arange(.3,28.9,.72):
 bx(f'Tower front transom {z:.2f}',[-5.58,3.97,z],[-5.48,9.03,z+.055],2,'Approximate dense glazing grid, not exhaustive panel count')
 for y in [3.95,8.98]:bx(f'Tower side transom {y}-{z:.2f}',[-5.58,y,z],[.81,y+.07,z+.055],2)
for y in [4.02,5.2,6.5,7.8,8.95]:bx(f'Tower front mullion {y}',[-5.62,y,0],[-5.48,y+.07,29],2)
for x in [-4.1,-2.5,-.9]:
 for y in [3.95,8.98]:bx(f'Tower side mullion {x}-{y}',[x,y,0],[x+.07,y+.07,29],2)
# Visible small windows of the grey end cheek, three levels; no fabricated inscription.
for y in [-.06,12.99]:
 for z in [5.4,11.0,16.0]:bx(f'End cheek side window {y}-{z}',[-2.8,y,z],[-1.2,y+.08,z+1.8],3,'Observed narrow openings on stone end side, schematic placement')
# Forty rooms per upper floor plus ten narrow shared bathroom bays per side; floorplan-derived facade rhythm, not surveyed window sizes.
centres=[a+offset for a in [2.8+9.1*g for g in range(5)]+[56.8+9.1*g for g in range(5)] for offset in [0,5.9]]
bath_centres=[5.75+9.1*g for g in range(5)]+[59.75+9.1*g for g in range(5)]
for side,y,sg in [('A',0,-1),('B',D,1)]:
 for j,x in enumerate(centres):
  for z in [11.15,15.55]:
   ya,yb=sorted([y+sg*.12,y-sg*.04]);bx(f'{side} upper room frame {j+1}-{z}',[x-1.19,ya,z],[x+1.19,yb,z+3.2],2)
   ya,yb=sorted([y+sg*.16,y+sg*.10]);bx(f'{side} upper opaque window {j+1}-{z}',[x-1.05,ya,z+.12],[x+1.05,yb,z+3.05],3)
   ya,yb=sorted([y+sg*.20,y+sg*.08]);bx(f'{side} central window divider {j+1}-{z}',[x-.04,ya,z],[x+.04,yb,z+3.2],2)
  for dx in [-1.3,1.3]:
   ya,yb=sorted([y+sg*.9,y-sg*.04]);bx(f'{side} narrow vertical shade {j+1}-{dx}',[x+dx-.07,ya,10.5],[x+dx+.07,yb,19.5],2,'Observed projecting shade rhythm; bay-based simplification not literal exhaustive count')
 for j,x in enumerate(bath_centres):
  for z in [11.35,15.75]:
   ya,yb=sorted([y+sg*.16,y-sg*.04]);bx(f'{side} narrow shared bathroom window {j+1}-{z}',[x-.44,ya,z],[x+.44,yb,z+2.7],3,'Narrow shared bathroom bay between two rooms visible in renovation plan; window proportion schematic')
 # Lower colonnades with recessed dark walls, platform lines and real gaps between columns.
 for z in [.1,4.85,9.8]:
  ya,yb=sorted([y+sg*.30,y-sg*1.4]);bx(f'{side} lower walkway slab {z}',[0,ya,z],[L,yb,z+.23],4)
 for x in np.arange(1.8,104,4.65):
  ya,yb=sorted([y+sg*.18,y-sg*.20]);bx(f'{side} lower column {x}',[x-.16,ya,0],[x+.16,yb,10.2],2)
 # Mid-level rail is represented with solid rails and posts, not structural or code certified.
 for z in ([5.45,5.85] if side=='B' else []):
  ya,yb=sorted([y+sg*.22,y+sg*.12]);bx(f'{side} balcony rail {z}',[0,ya,z],[L,yb,z+.09],2)
 for x in (np.arange(1.8,104,2.325) if side=='B' else []):
  ya,yb=sorted([y+sg*.24,y+sg*.12]);bx(f'{side} balcony post {x}',[x-.04,ya,5.05],[x+.04,yb,5.94],2)
# Street-side lower band differs from courtyard gallery: observed opaque windows, not mirrored rails.
for x in centres:
 bx(f'Street lower band frame {x}',[x-1.6,-.12,5.25],[x+1.6,1.3,8.8],2)
 bx(f'Street lower band window {x}',[x-1.43,-.17,5.45],[x+1.43,-.10,8.62],3)
# Central circulation bay kept distinct. No invented inner stair flights.
for y in [-.15,12.9]:bx(f'Central stair bay glazing {y}',[49,y,1],[55,y+.25,19.4],1,'Central staircase shown in plan and changed facade rhythm visible in photos')
bx('Neutral main flat roof',[0,0,19.58],[L,D,19.8],5,'Roof equipment absent in historical evidence; neutral plane')
# Open projecting roof combs separated at the centre, not a giant solid arched roof.
for a,b in [(2,48),(56,102)]:
 for x in np.arange(a,b,.95):
  for y,sg in [(0,-1),(D,1)]:
   ya,yb=sorted([y+sg*2.5,y-sg*1.0]);bx(f'Open roof shade rib {x:.2f}-{y}',[x-.09,ya,20.6],[x+.09,yb,20.82],2,'Visible rows of open cantilevered roof ribs; spacing approximate')
 for y in [-.2,1.0,12.0,13.2]:bx(f'Roof shade longitudinal beam {a}-{y}',[a,y,20.45],[b,y+.12,20.65],2)
 for x in np.arange(a,b,4.65):
  for y in [1.02,12.02]:bx(f'Roof shade support {x:.2f}-{y}',[x-.07,y,19.5],[x+.07,y+.12,20.65],2)
# Curved green apron at central split, simplified bent band rather than full barrel vault.
for yy,sg in [(0,-1),(D,1)]:
 for k in range(8):
  ang=(k/7)*math.pi/2; zz=19.8-1.7*(1-math.cos(ang)); y=yy+sg*(.2+1.6*math.sin(ang))
  ya,yb=sorted([y,yy-sg*.05]);bx(f'Central curved shade segment {yy}-{k}',[49,ya-.04,zz-.16],[55,yb+.04,zz+.16],2,'Photo-observed curved green central edge, segmented approximation')
# Far end is a neutral termination; connected hall visible in official plan intentionally excluded.
bx('Far neutral stair-end',[102,-.05,0],[104,13.05,20],4,'Opposite terminal details unverified, no duplicate glass tower')
s=mf.Manifold.batch_boolean(items,mf.OpType.Add).set_tolerance(.002).simplify(.002)
m=s.to_mesh();v=np.asarray(m.vert_properties)[:,:3]*SCALE;f=np.asarray(m.tri_verts);mi=np.zeros(len(f),np.int32)
for i,oid in enumerate(m.run_original_id):mi[m.run_index[i]//3:m.run_index[i+1]//3]=ids[int(oid)]
t=trimesh.Trimesh(v,f,process=False);t.export(ROOT/'model.stl');np.savez_compressed(ROOT/'mesh-data.npz',vertices=v,faces=f,materials=mi)
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);E=lambda s:'{'+ns+'}'+s
root=ET.Element(E('model'),unit='millimeter');res=ET.SubElement(root,E('resources'));bm=ET.SubElement(res,E('basematerials'),id='1')
for p in PALETTE:ET.SubElement(bm,E('base'),name=p['name'],displaycolor=p['hex']+'FF')
o=ET.SubElement(res,E('object'),id='2',type='model',name='NUK first general building main linear wing and end tower');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Historical-photo main linear wing and end glass tower; opposite end and attached hall excluded; estimated dimensions; not current survey or trial printed'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
