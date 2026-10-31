#!/usr/bin/env python3
"""TKU former Ying-yuan / history house: bounded front facade after2020 refurbishment. Not whole building."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh,manifold3d as mf
ROOT=Path(__file__).resolve().parent
PALETTE=[{'id':i,'name':n,'hex':c,'evidence':e}for i,n,c,e in [
 ('wall','Warm white plaster','#DFDFD1','Two official exterior photographs; uncalibrated'),
 ('red','Red brown coping and brick','#995847','Visible red-brown parapet edge and right vertical brick zone'),
 ('glass','Dark glazing abstraction','#394547','Opaque color block, not transparent or exact reflection'),
 ('door','Brown timber door','#624329','Visible front wood door; panels simplified'),
 ('frame','Gray window frame','#8D928C','Visible metal window surrounds'),
 ('base','Authored neutral display base','#A5A69C','Display support not real site footprint'),
 ('cut','Authored rear cut face','#B6BAC0','Neutral cutoff plane, not building rear')]]
SCALE=7.0
items=[];ops=[];ids={}
def box(a,b):return mf.Manifold.cube(np.subtract(b,a).tolist()).translate(a)
def add(name,s,mat,evidence):
 s=s.translate([0,0,.6]).as_original();ids[int(s.original_id())]=mat;items.append(s);ops.append({'name':name,'material':mat,'evidence':evidence})
def bx(name,a,b,mat=0,evidence='Photo-proportioned visible feature; nominal dimensions'):add(name,box(a,b),mat,evidence)
def poly(name,pts,z0,z1,mat,evidence):
 if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))<0:pts=list(reversed(pts))
 add(name,mf.CrossSection([pts]).extrude(z1-z0).translate([0,0,z0]),mat,evidence)
# Width18 nominal units; retained slabdepth3 is authored cutoff, not building depth.
bx('Authored support base',[-.5,-3.2,-.6],[18.5,3.4,0],5,'Display footprint only')
bx('Left two-storey facade',[0,0,0],[8.05,3,9],0,'Four visible rectangular front openings on left white two-storey zone')
bx('Right recessed facade',[8,1.1,0],[18,3,9],0,'Back wall of open curved porch and balcony, depth estimated')
bx('Neutral rear cutoff',[0,2.96,0],[18,3.05,9],6,'Authored section cut, not building exterior rear')
# Semicircular elliptical front edge, arbitrary fitted curvature explicitly documented.
def arc(rx,ry,n=64):return [(13+rx*math.cos(math.pi*i/n),-ry*math.sin(math.pi*i/n))for i in range(n+1)]
def shape(rx,ry):return arc(rx,ry)+[(13-rx,1.2),(13+rx,1.2)]
def band(rx,ry,th=.25):return arc(rx,ry)+list(reversed(arc(rx-th,ry-th)))
poly('Curved balcony floor',shape(5.05,2.25),4.35,4.7,0,'Curved balcony front slab visible in both views; elliptical fit not surveyed')
poly('Curved lower solid parapet',band(5.05,2.25,.28),4.65,5.25,0,'Solid lower curved parapet visible')
poly('Curved upper railing band',band(5.05,2.25,.3),5.85,6.15,0,'Continuous upper curved rail above rectangular perforations')
# Repeated bars are an explicit regularized approximation, NOT verified total count.
for i in range(29):
 a=math.pi*i/28;x=13+4.9*math.cos(a);y=-2.1*math.sin(a)
 bx('Regularized railing bar'+str(i),[x-.085,y-.15,5.2],[x+.085,y+.15,5.91],0,'29 evenly spaced authored balusters approximate visible repetitive openings; exact count not claimed')
poly('Curved overhead canopy',shape(5.05,2.25),8.6,9.15,0,'Rounded white canopy edge over open upper balcony')
poly('Red curved roof coping',band(5.1,2.3,.23),9.08,9.35,1,'Red-brown curved cap visible; roof interior not reconstructed')
bx('Left red roof coping',[-.05,-.12,8.95],[8.1,.14,9.3],1,'Continuous red-brown edge over left white facade')
# Right visible brick end zone is a simplified support; hidden/receding fins are omitted.
for j,x in enumerate([16.8,17.35,17.9]):
 bx('Right visible brick fin'+str(j),[x-.14,-.04,0],[x+.14,1.22,8.7],1,'Three visible red-brick vertical blades at right end approximated from wider official photograph; concealed blades not asserted')
# Applied opaque opening surfaces, not hollow rooms or literal glass.
def window(name,x0,x1,z0,z1,y=0):
 bx(name+' frame',[x0-.1,y-.08,z0-.1],[x1+.1,y+.1,z1+.1],4,'Metallic rectangular surround seen in official photos')
 bx(name+' opaque pane',[x0,y-.105,z0],[x1,y+.025,z1],2,'Opaque glazing abstraction; reflections/interior excluded')
window('Upper left narrow',1.2,2.5,5.8,8.05)
window('Upper left broad',4.5,6.65,5.8,8.05)
window('Ground left narrow',.75,2.35,.25,3.5)
window('Ground left broad',4.0,6.95,.25,3.5)
window('Porch right window',14.4,16.7,1.1,3.4,1.1)
window('Upper porch recess window',10.0,12.4,6.4,8.1,1.1)
bx('Front timber door',[10.1,.98,.1],[12.2,1.2,3.5],3,'Brown double wood door visible; detailed carving omitted')
bx('Door central stile',[11.08,.91,.1],[11.2,1.1,3.5],3,'Simplified double-door division')
for x in [10.25,11.35]:
 for z in [.35,1.35,2.35]:bx('Simplified timber panel',[x,.92,z],[x+.65,1.08,z+.7],3,'Authored coarse panel subdivision, not exact joinery')
bx('Front plinth',[-.05,-2.85,0],[18.05,1.2,.19],1,'Low front terrace approximate; decorative tiles omitted')
bx('Light terrace top',[-.02,-2.82,.15],[18.02,1.2,.24],0,'Paving simplified neutral; no copied tile pattern')
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
o=ET.SubElement(res,E('object'),id='2',type='model',name='TKU history house bounded front facade');mesh=ET.SubElement(o,E('mesh'));vs=ET.SubElement(mesh,E('vertices'));ts=ET.SubElement(mesh,E('triangles'))
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
r={'vertices':len(v),'triangles':len(f),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':len(s.decompose()),'volume_mm3':float(t.volume),'dimensions_mm':t.extents.tolist(),'min_triangle_area_mm2':float(t.area_faces.min()),'material_counts':{p['id']:int((mi==i).sum()) for i,p in enumerate(PALETTE)},'scope':'Post2020 refurbishment source-state front facade only. Unknown rear and left new entrance/elevator excluded. Dimensions and repeated baluster count approximated; no interior or trial print.'}
(ROOT/'build-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
