"""NSYSU bridge pavilion. Eightfold topology INFERRED from complementary photos.
Seven true columns visible; one occluded column/rear facets symmetry approximation.
Display millimeters, no measured building dimensions. Raw photographs excluded.
"""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,math
import numpy as np,trimesh
from manifold3d import Manifold,Mesh,OpType,CrossSection
O=Path(__file__).resolve().parent;(O/'qa').mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return Manifold.cube((w,d,h)).translate((x-w/2,y-d/2,z))
def rb(a,r,z,tang,depth,h):return box(r,0,z,depth,tang,h).rotate((0,0,a))
def cyl(r,h,z,x=0,y=0):return Manifold.cylinder(h,r,r,circular_segments=40).translate((x,y,z))
def octagon(r,h,z):return Manifold.cylinder(h,r,r,circular_segments=8).rotate((0,0,22.5)).translate((0,0,z))
def frommesh(t):return Manifold(Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
# Immediate platform and short artificial continuation of visible support only.
parts=[octagon(30,8.4,0),octagon(53.5,4.2,8.2)]
for i in range(8):
 a=22.5+i*45;x=46.5*math.cos(math.radians(a));y=46.5*math.sin(math.radians(a))
 parts += [cyl(4.3,1.3,12.2,x,y),cyl(3.7,53.7,13.2,x,y),cyl(4.3,1.7,65.7,x,y),cyl(5.1,2.4,67.1,x,y),cyl(4.7,2.0,69.2,x,y)]
 # Six pierced parapets; opposite axial bridge-entry bays omitted.
 mid=(a+22.5)%360;ap=46.5*math.cos(math.pi/8);length=2*46.5*math.sin(math.pi/8)
 if mid not in [0,180]:
  panel=rb(mid,ap,12.2,length+1,3.3,11.3)
  # Two clipped-corner rectangular holes, actual open air not painted rectangles.
  for u in [-8.5,8.5]:
   w=9.5;h=5.5;c=1.15;pts=[(-w/2+c,0),(w/2-c,0),(w/2,c),(w/2,h-c),(w/2-c,h),(-w/2+c,h),(-w/2,h-c),(-w/2,c)]
   hole=CrossSection([pts]).extrude(6).transform([[0,0,1,ap-3],[1,0,0,u],[0,1,0,15.2]]).rotate((0,0,mid))
   panel=panel-hole
  parts += [panel,rb(mid,ap,22.7,length+1.8,4.2,1.7)]
 # Ring-beam sides genuinely supported by columns, empty central pavilion.
 parts.append(rb(mid,ap,70.4,length+.8,7.2,9.8))
# Sweeping octagonal roof shell: exact curvature/tile grid is deliberately approximate.
N=64;ts=np.linspace(.04,1,19)
def surface(t,j):
 sector=j//8;u=(j%8)/8;a=math.radians(22.5+45*sector);b=a+math.pi/4
 xy=62*((1-u)*np.array([math.cos(a),math.sin(a)])+u*np.array([math.cos(b),math.sin(b)]))*t
 z=81+22*(1-t)**2+3.2*t**8*(2*u-1)**2
 return [*xy,z]
v=[]
for dz in [0,-3.2]:
 v.append([0,0,103+dz])
 for t in ts:
  for j in range(N):q=surface(t,j);q[2]+=dz;v.append(q)
L=1+len(ts)*N;f=[]
for off,rev in [(0,False),(L,True)]:
 def add(a,b,c):f.append([c,b,a] if rev else [a,b,c])
 for j in range(N):add(off,off+1+j,off+1+(j+1)%N)
 for k in range(len(ts)-1):
  for j in range(N):a=off+1+k*N+j;b=off+1+k*N+(j+1)%N;c=a+N;d=b+N;add(a,c,d);add(a,d,b)
# Ring winding above is clockwise due a,c,d; invert top and bottom together if necessary below.
for j in range(N):a=1+(len(ts)-1)*N+j;b=1+(len(ts)-1)*N+(j+1)%N;f += [[a,b+L,b],[a,a+L,b+L]]
roof=trimesh.Trimesh(v,f,process=False)
# Consistent winding is established from analytic shell rather than repaired exported STL.
assert roof.is_watertight and roof.is_winding_consistent and roof.volume>0
parts.append(frommesh(roof))
# Attached radial tile relief: source-backed rhythm, simplified counts and geometry.
def rod(a,b,r):
 d=np.array(b)-a;t=trimesh.creation.cylinder(r,np.linalg.norm(d),sections=10);t.apply_transform(trimesh.geometry.align_vectors([0,0,1],d));t.apply_translation((np.array(a)+b)/2);return frommesh(t)
for j in range(N):
 # Every second row, plus broad hip ridges at octagon corners.
 if j%2:continue
 r=1.15 if j%8==0 else .72
 samples=[surface(t,j) for t in np.linspace(.11,.987,15)]
 for q in samples:q[2]-=.40
 for a,b in zip(samples,samples[1:]):parts.append(rod(a,b,r))
 for q in samples:parts.append(Manifold.sphere(r,16).translate(q))
 # Chunky tile-end bead fused into eave, not a disconnected ornament.
 q=samples[-1];parts.append(cyl(r+0.3,1.7,q[2]-1.1,q[0],q[1]))
# Thickened stacked finial; no invented inscription or detailed sacred glyph.
parts += [cyl(3.5,2.2,102.5),Manifold.sphere(4.5,32).scale((1,1,1.15)).translate((0,0,108)),cyl(2,4.2,111),cyl(2.4,1.2,114.7)]
m=Manifold.batch_boolean(parts,OpType.Add);assert m.status().name=='NoError'
m=m.set_tolerance(.0001).simplify(.001)
for _ in range(3):m=Manifold(m.to_mesh()).simplify(.001)
assert m.status().name=='NoError'
me=m.to_mesh64();t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
t.export(O/'model.stl');t=trimesh.load_mesh(O/'model.stl',process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces);c=t.triangles_center
palette=[('warm_weathered_concrete','#CFCDB5'),('immediate_platform_support','#A9ABA0'),('yellow_olive_glazed_roof','#9B9854'),('roof_tile_relief','#B5A964'),('ochre_frieze_simplified_beam','#B5A36D')]
lo=t.triangles.min(axis=1);hi=t.triangles.max(axis=1)
colors=np.zeros(len(f),dtype=int);colors[hi[:,2]<12.41]=1;colors[(lo[:,2]>=70.399)&(hi[:,2]<=80.201)]=4;colors[lo[:,2]>=77.5]=2
# Raised roof ridges highlighted only on actual exposed near-horizontal roof faces.
colors[c[:,2]>104]=3
(O/'mesh.json').write_text(json.dumps({'vertices':v.tolist(),'faces':f.tolist(),'face_materials':colors.tolist()},separators=(',',':')))
(O/'palette.json').write_text(json.dumps({'materials':[{'id':a,'srgb':b} for a,b in palette]},indent=2)+'\n')
(O/'qa/design-features.json').write_text(json.dumps(dict(estimated_not_surveyed=True,columns_inferred=8,roof_facets_inferred=8,true_columns_visible_in_individual_source=7,hidden_column_and_rear_regular_symmetry=True,roof_vertex_diameter_mm=124,shaft_diameter_mm=7.4,roof_shell_vertical_thickness_mm=3.2,parapet_thickness_mm=3.3,parapet_openings=12,parapet_bottom_sill_mm=3,roof_tile_relief_radius_mm=.72,hip_ridge_radius_mm=1.15,source_capture_dates='unknown',scope='whole pavilion plus immediate platform; no long bridge or pond',artificial_support='short solid octagonal support continuation, not surveyed submerged foundation',ornament='simplified attached ribs and bead ends; meander pattern replaced by color band; inscriptions omitted',actual_print_tested=False),indent=2)+'\n')
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
