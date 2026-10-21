"""Estimated NUU Bajia stop 1 two terminal cells. Plan curvature, not vertical arch."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent
R=240; ANG=14
parts=[]
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def arc(r0,r1,z,h,angle=ANG):
 aa=np.linspace(-math.radians(angle),math.radians(angle),29)
 pts=[(r*math.sin(t),r*math.cos(t)-R) for r,seq in [(r1,aa),(r0,aa[::-1])] for t in seq]
 return CrossSection([pts[::-1]]).extrude(h).translate((0,0,z))
def local(m,deg,r=R):
 t=math.radians(deg);return m.rotate((0,0,-deg)).translate((r*math.sin(t),r*math.cos(t)-R,0))
def yzprism(w,points):
 pts=np.array([[xx,y,z] for xx in [-w/2,w/2] for y,z in points]);q=trimesh.convex.convex_hull(pts)
 return Manifold(Mesh(np.asarray(q.vertices,dtype=np.float32),np.asarray(q.faces,dtype=np.uint32)))
# Added rectangular display plinth, no source paving claim.
parts=[box(0,-24,0,132,74,3)]
# Continuous gently curved lower wall and inner wall-backed bench support.
parts += [arc(232,240,2.8,37.2),arc(221,233,16.5,4,13.8),arc(219,234,20,2.6,13.8)]
# Real terminal low return only; continuation end remains openly cut.
parts += [local(box(0.25,-21.7,2.8,6,44,37.2),-ANG)]
# Exactly 3 rear posts; no front ground legs or side glazing.
for deg in [-ANG,0,ANG]:
 parts += [local(box(0,0,2.8,4.2,4.2,90.2),deg),local(box(0,-23,87.8,3.4,50,3.2),deg)]
 parts += [local(yzprism(3.4,[(-1,69),(-1,73),(-47,89.6),(-47,85.6)]),deg)]
# Two planar chords between consecutive posts, pale board fields in deep frame.
L=2*R*math.sin(math.radians(ANG/2));chordR=R*math.cos(math.radians(ANG/2))
for deg in [-ANG/2,ANG/2]:
 # Lower rail at 43 leaves a 3 mm physical slit above wall top40.
 panel=box(0,0,43,L,4,42)
 panel-=box(0,-2,45,L-5,1.4,37.5)
 panel-=box(0,2,45,L-5,1.4,37.5)
 parts.append(local(panel,deg,chordR))
# Unknown top: conservative plain flat slab; curves in plan only.
parts += [arc(188,244,90,3.5)]
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('muted_olive_teal_frame','#617D68'),('neutral_display_plinth','#929B9A'),('aggregate_wall_simplified','#A49F91'),('blank_notice_fields','#D4DBD7'),('warm_timber_seat','#785A3E'),('dark_plain_soffit','#384D49'),('unknown_plain_roof_top','#849187'),('pale_bench_support','#B2B2A6')]
colors=np.zeros(len(f),dtype=int)
rr=np.sqrt(c[:,0]**2+(c[:,1]+R)**2)
colors[(c[:,2]>3)&(c[:,2]<40.01)]=2
colors[(t.triangles[:,:,2].min(axis=1)>16.49)&(t.triangles[:,:,2].max(axis=1)<20.51)&(rr<232.01)]=7
colors[(t.triangles[:,:,2].min(axis=1)>=19.99)&(t.triangles[:,:,2].max(axis=1)<=22.61)&(rr<234.01)]=4
for deg in [-ANG,0,ANG]:
 q=math.radians(deg);px=R*math.sin(q);py=R*math.cos(q)-R
 near=(abs((c[:,0]-px)*math.cos(q)-(c[:,1]-py)*math.sin(q))<2.11)&(abs((c[:,0]-px)*math.sin(q)+(c[:,1]-py)*math.cos(q))<2.11)
 colors[near&(c[:,2]>3)]=0
for deg in [-ANG/2,ANG/2]:
 q=math.radians(deg);px=chordR*math.sin(q);py=chordR*math.cos(q)-R
 xx=(c[:,0]-px)*math.cos(q)-(c[:,1]-py)*math.sin(q);yy=(c[:,0]-px)*math.sin(q)+(c[:,1]-py)*math.cos(q)
 colors[(abs(xx)<(L-5)/2+.001)&(abs(yy)<1.31)&(c[:,2]>44.99)&(c[:,2]<82.51)]=3
colors[(c[:,2]>=89.99)&(t.face_normals[:,2]<-.5)]=5
colors[(c[:,2]>=93.49)&(t.face_normals[:,2]>.5)]=6
colors[c[:,2]<=3.001]=1
(O/'qa/design-features.json').write_text(json.dumps({'estimated_not_surveyed':True,'arc_radius_mm':R,'arc_turn_degrees':2*ANG,'roof_projection_mm':52,'roof_thickness_mm':3.5,'rear_post_mm':4.2,'board_backing_mm':2.6,'board_rail_min_mm':2.5,'diagonal_brace_width_mm':3.4,'seat_thickness_mm':2.6,'open_slit_height_mm':3,'scope_cut':'positive angular second interior post; negative angular true terminal return','unseen_geometry':'curvature, depth, roof top, anchorage, bench underside estimated; added display plinth'},indent=2)+'\n')
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
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
