"""THU Priest bell tower. Four wall slabs, photo-proportioned display millimetres."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
from shapely.geometry import LineString
O=Path(__file__).resolve().parent
(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def solid(t):
 if t.volume<0:t.invert()
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
 return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
def rod(a,b,r):
 a=np.array(a);b=np.array(b);t=trimesh.creation.cylinder(radius=r,height=np.linalg.norm(b-a),sections=24);t.apply_transform(trimesh.geometry.align_vectors([0,0,1],b-a));t.apply_translation((a+b)/2);return solid(t)
parts=[box(0,0,0,90,90,3),box(0,0,2.6,86,86,.9)]
# Parallel rows, each with TWO coplanar thick rectangular walls. 4mm through slit.
for x in [-23,23]:
 for y in [-15,15]:
  parts.append(box(x,y,3,10,26,120))
  # Shallow raised diamond tiles, clipped to inset broad-face region.
  for side in [-1,1]:
   tileparts=[]
   for iy in range(-5,6):
    yy=y+iy*4.6
    for iz in range(28):
     zz=5+iz*4.4;cy=yy+(2.3 if iz%2 else 0)
     # diamond points in local xy, extrude then rotate to broad yz plane
     poly=CrossSection([[(cy-2.17,zz),(cy,zz-4.2),(cy+2.17,zz),(cy,zz+4.2)]]).extrude(.6)
     poly=poly.rotate((90,0,90)).translate((x+side*5-(.15 if side>0 else .45),0,0))
     tileparts.append(poly)
   tile=Manifold.batch_boolean(tileparts,OpType.Add)^box(x+side*5,y,4,1.3,24,118)
   parts.append(tile)
# Bearing blocks bridge each side slot and project inward, dark yoke pivot at z92.
for x in [-23,23]:parts.append(box(x,0,85,16,9,10))
parts.append(rod((-22,0,92),(22,0,92),1.65))
# Bell is a rotational profile, shallow open lower cavity, crown solid for printable union.
profile=np.array([[0,100],[5,100],[6,99],[7.5,97],[8.2,94],[8.5,90],[10,86],[13,82],[15.5,81],[15.5,79.6],[13.8,79.6],[12,81.5],[9,86],[7,91],[0,91]])
parts.append(solid(trimesh.creation.revolve(profile,sections=96)))
parts.append(rod((0,0,92),(0,0,78.8),1.1));parts.append(solid(trimesh.creation.icosphere(subdivisions=2,radius=2).apply_translation((0,0,78))))
# Source-backed inverted U yoke with strengthened segments, simplified fixed hardware.
pts=[(-18,0,92),(-15,0,94),(-14,0,101),(-11,0,104),(-6,0,105),(6,0,105),(11,0,104),(14,0,101),(15,0,94),(18,0,92)]
outline=LineString([(x,z) for x,y,z in pts]).buffer(1.8,quad_segs=8,join_style=1,cap_style=1)
parts.append(CrossSection([list(outline.exterior.coords)[:-1][::-1]]).extrude(3.6).rotate((90,0,0)).translate((0,1.8,0)))
parts.append(rod((0,0,99),(0,0,105),1.8))
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces)
palette=[('exposed_gray_concrete','#959991'),('ochre_glazed_diamond_tiles','#CBAF50'),('bronze_bell','#71684A'),('dark_iron_yoke_axle','#373B34'),('light_paving_rim','#C8C8B9'),('paving','#AAA593')]
colors=np.zeros(len(f),dtype=int);c=t.triangles_center;hi=t.triangles.max(axis=1)
colors[hi[:,2]<=3.501]=5
colors[(hi[:,2]<=3.001)&((np.abs(c[:,0])>43)|(np.abs(c[:,1])>43))]=4
for x in [-23,23]:
 for side in [-1,1]:
  xx=x+side*5
  colors[(side*(c[:,0]-xx)>.001)&(side*(c[:,0]-xx)<.46)&(c[:,2]>4)&(c[:,2]<122)&(np.abs(c[:,1])>2.99)&(np.abs(c[:,1])<27.01)]=1
colors[(np.abs(c[:,0])<16)&(np.abs(c[:,1])<16)&(c[:,2]>75)]=2
colors[(np.abs(c[:,0])>=14)&(np.abs(c[:,1])<4.51)&(c[:,2]>85)&(c[:,2]<95)]=0
colors[(np.abs(c[:,0])<20)&(np.abs(c[:,1])<2)&(c[:,2]>90)&((c[:,2]>100)|(np.abs(c[:,0])>9))]=3
# Outer bearing faces must stay concrete, never be misclassified as yoke triangles.
outer_bearing=(np.abs(c[:,0])>30.99)&(np.abs(c[:,1])<4.51)&(c[:,2]>85)&(c[:,2]<95)
assert outer_bearing.sum()>0 and np.all(colors[outer_bearing]==0)
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,photo_dates_unknown=True,source_appearance_not_claimed_current=True,wall_count=4,parallel_rows=2,panels_per_row=2,wall_height_mm=120,wall_thickness_mm=10,panel_depth_mm=26,side_slit_mm=4,central_passage_mm=36,bell_mouth_diameter_mm=31,bell_lower_lip_mm=79.6,display_base_mm=[90,90,3.5],diamond_relief_mm=.45,bearing_outer_projection_mm=3,mechanism_fixed_and_strengthened=True,not_functional_bell=True,no_actual_print=True,omitted=['chapel','office','trees','planters','warning_sign','lettering'],notes='Proportions from nine official photographs, not measured dimensions; 2022 renovation means appearance cannot be claimed current. Tile counts and mechanism are simplified.'),indent=2)+'\n')
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
