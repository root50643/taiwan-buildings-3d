"""NCKU Wave Eaves (2021): photograph-bounded upper apex lattice FRAGMENT.
NOT a complete pavilion. No foot count, second saddle, hidden reciprocal joinery
or real-world dimensions inferred. x/z line graph estimated from visible upper
apex in creator photograph. Depth is a schematic shallow warped interpretation.
The blue plinth and cut supports are artificial display geometry, not architecture.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True);(O/'previews').mkdir(exist_ok=True)
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def point(px,py):
 x=(px-240)*.24; z=(400-py)*.24+18
 # Estimated depth, deliberately NOT exact 3D photogrammetry or engineered joints.
 y=.0025*x*x-.10*(z-18)+.035*x
 return np.array((x,y,z))
def timber(a,b,width=3.0,depth=2.7):
 a=np.asarray(a);b=np.asarray(b);v=b-a;length=np.linalg.norm(v);u=v/length
 side=np.cross([0,1,0],u);side/=np.linalg.norm(side);normal=np.cross(u,side)
 # rectangular section, a small joining overlap, not cylinders or a roof membrane
 tf=np.column_stack([side,normal,u,a-u*.45-side*width/2-normal*depth/2])
 return Manifold.cube((width,depth,length+.9)).transform(tf)
# Visible high apex and two bounding rectangular timbers, cut at photograph level400.
# Coordinates are tracing coordinates of a selected region, not survey coordinates.
nodes={'A':(260,65),'L':(50,400),'R':(408,400),
       'TL':(144,262),'TR':(290,235),'J':(254,306),
       'BR':(312,207),'D':(201,255),'E':(322,370),
       'F':(309,379),'G':(398,392), 'H':(88,340),'CUT':(106,400)}
P={k:point(*p) for k,p in nodes.items()}
# Two long boundary timbers. No unknown fourth foot or complete pavilion inferred.
for a,b in [('L','A'),('A','R')]:
 u=P[b]-P[a];u/=np.linalg.norm(u);side=np.cross([0,1,0],u);side/=np.linalg.norm(side)
 for offset in [-1.8,1.8]:parts.append(timber(P[a]+side*offset,P[b]+side*offset,3.0,3.4))
# Offset inner members, no regular-grid or triangular-truss substitution.
segments=[('TL','TR'),('J','BR'),('D','E'),('F','G'),('E','F'),('H','CUT')]
for a,b in segments:parts.append(timber(P[a],P[b],2.9,2.7))
# Nonarchitectural blue cut support rail and three feet on display plinth.
parts.append(box(0,3,0,104,36,3))
for key in ['L','R','CUT']:
 p=P[key];parts.append(box(p[0],p[1],2.5,7,7,p[2]-2.5))
# Local blue cut-end caps make truncation visible, not a real structural crossbeam.
for key in ['L','R','CUT']:
 p=P[key];parts.append(box(p[0],p[1],17,7.5,7.5,2.8))
# A small dark apex connector is visible in the source; bolt layout not invented.
a=P['A'];parts.append(box(a[0],a[1],a[2]-2.3,3.6,5.0,4.6))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
m=m.set_tolerance(.0001).simplify(.0005);me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('estimated_pale_timber','#D7C486'),('dark_apex_connector_schematic','#51453B'),('blue_DISPLAY_cut_stand_NOT_architecture','#608AA7')]
colors=np.zeros(len(f),dtype=int)
colors[(abs(c[:,0]-a[0])<=1.801)&(abs(c[:,1]-a[1])<=2.501)&(c[:,2]>=a[2]-2.301)]=1
colors[c[:,2]<19.801]=2
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
(O/'qa/design-features.json').write_text(json.dumps({'scope':'upper apex lattice fragment ONLY; not entire pavilion','complete_pavilion':False,'actual_foot_count':'unknown; no real feet included','estimated_not_surveyed':True,'solid_roof_skin':False,'source_directions':2,'source_photos':3,'inner_rectangular_beam_width_mm':2.9,'inner_rectangular_beam_depth_mm':2.7,'paired_boundary_single_width_mm':3.0,'paired_boundary_gap_mm':.6,'boundary_rectangular_beam_depth_mm':3.4,'depth':'schematic shallow warp, not solved 3D coordinates','blue_geometry':'artificial display plinth and cut-end supports; not source architecture','photograph_trace_nodes':nodes,'internal_segments':segments,'actual_print_tested':False},indent=2)+'\n')
# Deterministic 3MF, material assigned per triangle. Display materials, not extruder mapping.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
def el(p,name,attrs={}):return ET.SubElement(p,'{'+ns+'}'+name,{k:str(v) for k,v in attrs.items()})
r=ET.Element('{'+ns+'}model',{'unit':'millimeter','xml:lang':'en-US'});res=el(r,'resources');bm=el(res,'basematerials',{'id':2})
for a,b in palette:el(bm,'base',{'name':a,'displaycolor':b+'FF'})
obj=el(res,'object',{'id':1,'type':'model','pid':2,'pindex':0});mm=el(obj,'mesh');vs=el(mm,'vertices');ts=el(mm,'triangles')
for q in v:el(vs,'vertex',dict(zip('xyz',[repr(float(a)) for a in q])))
for tri,col in zip(f,colors):el(ts,'triangle',{'v1':tri[0],'v2':tri[1],'v3':tri[2],'pid':2,'p1':col,'p2':col,'p3':col})
b=el(r,'build');el(b,'item',{'objectid':1})
files={'3D/3dmodel.model':ET.tostring(r,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}
with zipfile.ZipFile(O/'model.3mf','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items(): info=zipfile.ZipInfo(name,(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
print(json.dumps({'faces':len(f),'vertices':len(v),'bounds':t.bounds.tolist(),'volume':t.volume,'components':len(t.split()),'material_counts':np.bincount(colors,minlength=len(palette)).tolist(),'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest()}))
