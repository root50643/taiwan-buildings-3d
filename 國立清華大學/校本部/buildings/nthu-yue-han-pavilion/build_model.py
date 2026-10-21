"""NTHU Yue Han Pavilion: 2016 official source approximate whole pavilion, mm."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def radialbox(a,r,z,tang,depth,h):return box(r,0,z,depth,tang,h).rotate((0,0,a))
# Simplified solid terrain/terrace support, not surveyed hill or foundation.
parts=[Manifold.cylinder(11,56,54,circular_segments=120),Manifold.cylinder(1.4,54.8,54.8,circular_segments=120).translate((0,0,10.8))]
# Twelve vertex piers; one full portal centered on front -Y.
for i in range(12):
 a=-105+i*30
 parts.append(radialbox(a,48,12,4.8,4.6,52.3))
 # Panel joins endpoints of a regular twelve-sided inner ring.
 mid=a+15;ap=48*math.cos(math.pi/12);length=2*48*math.sin(math.pi/12)
 parts.append(radialbox(mid,ap,41.2,length+.2,3.2,17.3))
 # Opaque thickened proxy for a narrow clerestory: printable closed backing.
 parts.append(radialbox(mid,ap,58.4,length+.2,1.6,5.9))
 # Visible radial pier-head rib underside reaches out to round eave.
 parts.append(radialbox(a,54,62,2.2,12.4,3.4))
# Shallow circular roof shell, slight dome underside, deliberately no top ornament.
profile=np.array([[0,65.4],[12,65.3],[24,65.0],[36,64.5],[48,63.8],[60,63.0],[60,65.3],[48,66.1],[36,66.8],[24,67.3],[12,67.6],[0,67.6]])
roof=trimesh.creation.revolve(profile,sections=120)
assert roof.is_watertight and roof.volume>0
parts.append(Manifold(Mesh(np.array(roof.vertices,dtype=np.float32),np.array(roof.faces,dtype=np.uint32))))
# Eleven simplified broad risers. Upper step overlaps terrace, never disconnected.
for i in range(11):
 y=-80+i*2.8;w=44-i*.6;h=(i+1)*1.1
 parts.append(box(0,(y-50)/2,0,w,-50-y,h))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('warm_offwhite_concrete','#E5E2D7'),('simplified_terrain_display_support','#999A87'),('opaque_clerestory_glazing_proxy','#91ABB0'),('stone_access_stairs','#8F9087'),('shallow_roof_concrete','#D6D5CA')]
colors=np.zeros(len(f),dtype=int);tri=t.triangles;lo=tri.min(axis=1);hi=tri.max(axis=1);c=t.triangles_center
colors[hi[:,2]<=12.201]=1
colors[(hi[:,1]<-53)&(hi[:,2]<=12.201)]=3
colors[(lo[:,2]>=58.399)&(hi[:,2]<=64.301)]=2
colors[lo[:,2]>=62.99]=4
# Assign full roof surface by smooth shallow-shell elevation, not false floating overlay.
colors[(c[:,2]>63.0)&(np.linalg.norm(c[:,:2],axis=1)>50.5)]=4
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,source_appearance_year=2016,roof_diameter_mm=120,ring_vertex_diameter_mm=96,portals=12,regular_repeated_ring_is_symmetry_approximation=True,pier_mm=[4.8,4.6],clear_portal_height_mm=29,spandrel_height_mm=17.3,spandrel_thickness_mm=3.2,clerestory_height_mm=5.9,opaque_glazing_proxy_thickness_mm=1.6,roof_shell_min_nominal_mm=2.2,radial_rib_width_mm=2.2,stairs_simplified_risers=11,step_rise_mm=1.1,step_run_mm=2.8,terrace_support='solid artificial truncated round terrain proxy, not measured foundation',roof_top_and_back='No aerial or rear exterior source. Shallow shell curvature, regular rear bays and top are inferred.',omitted=['inscriptions','floor emblem','bench','trees','lamppost','cameras','full hillside'],scope='Coherent whole pavilion source approximation, not exact survey or verified 2026 condition'),indent=2)+'\n')
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
