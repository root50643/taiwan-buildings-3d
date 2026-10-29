"""Add source-guided approximate materials; never modify original mesh or locked previews.
Run Blender 4.3.2: blender -b -t 1 --python-exit-code 1 -P build_appearance.py
Requires original scene.blend and model.stl alongside this script. No source photos embedded.
"""
from pathlib import Path
import sys
import bpy,hashlib,json,math,struct,zipfile,xml.etree.ElementTree as ET
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
bpy.context.preferences.filepaths.save_version=0
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');mesh=obj.data
verts=[tuple(v.co) for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
assert all(len(f)==3 for f in faces)
def digest(a,fmt):return hashlib.sha256(b''.join(struct.pack(fmt,*r) for r in a)).hexdigest()
before={'vertices':digest(verts,'<3f'),'faces':digest(faces,'<3I')}
# Limited single2024photo-supported materials; front section only, not complete building.
palette=[('Unknown roof sides and artificial rear cut','#AAA79F',.86),('Observed front wall and full original columns warm beige grey','#CDC8AD',.86),('Original separate window frames grey white','#B7BDB8',.76),('Observed true recessed window mixed opaque grey green','#59645E',.8),('Observed original stair treads neutral grey','#898B82',.88)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x0,x1,y0,y1,z0,z1):
 if not bounds((x0,y0,z0),(x1,y1,z1)):return False
 return any((plane(k,a) and n[k]<-.8) or (plane(k,b) and n[k]>.8) for k,a,b in [(0,x0,x1),(1,y0,y1),(2,z0,z1)])
CN=np.array([[math.cos((k+.5)*math.pi/12),math.sin((k+.5)*math.pi/12)] for k in range(24)])
CT=np.column_stack((-CN[:,1],CN[:,0]));CR=1.55*math.cos(math.pi/24);CW=1.55*math.sin(math.pi/24)
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);lo=q.min(0);hi=q.max(0);n=np.array(p.normal);i=0
 # Frontal wall host planes only; side/rear section boundaries stay neutral.
 for side in [-1,1]:
  if plane(1,-4) and n[1]<-.8 and bounds((side*51-17,-4,7.1),(side*51+17,-4,51.1)):i=1
  for xc in [side*35,side*66]:
   if boxface(xc-.9,xc+.9,-8.3,-3.7,7,51.5):i=1
  for z in [10,20,30,40]:
   if boxface(side*51-17,side*51+17,-4.85,-3.75,z-1.2,z-.1):i=1
   for xc in [side*40,side*49,side*59]:
    if plane(1,-2.5) and n[1]<-.8 and bounds((xc-3.3,-2.5,z),(xc+3.3,-2.5,z+6)):i=3
 if plane(1,-.5) and n[1]<-.8 and bounds((-35,-.5,7.1),(35,-.5,62.1)):i=1
 if plane(1,-19.5) and n[1]<-.8 and bounds((-36.5,-19.5,35),(36.5,-19.5,62)):i=1
 if plane(1,.65) and n[1]<-.8 and bounds((-31.5,.65,8.5),(31.5,.65,23.5)):i=3
 for xc in [-26,-13,0,13,26]:
  if plane(1,.75) and n[1]<-.8 and bounds((xc-5,.75,27),(xc+5,.75,32.3)):i=3
 for z,h in [(39,5.5),(53,3.2)]:
  for xc in [-28,-14,0,14,28]:
   if plane(1,-17.95) and n[1]<-.8 and bounds((xc-5.5,-17.95,z),(xc+5.5,-17.95,z+h)):i=3
   if boxface(xc-.55,xc+.55,-21,-18.6,z,z+h):i=2
 for xc in range(-29,30,6):
  if boxface(xc-.55,xc+.55,-2.35,-.25,8.5,23.5):i=2
 for z in [12.5,18.2]:
  if boxface(-31.5,31.5,-2.35,-.25,z,z+1.1):i=2
 # Actual original24-facet column surfaces only, including CSG-trimmed surviving facets.
 if lo[2]>=7-EPS and hi[2]<=64+EPS and abs(n[2])<.01:
  for xc in [-36,-21.6,-7.2,7.2,21.6,36]:
   xy=q[:,:2]-[xc,-19]
   for k,nn in enumerate(CN):
    if np.dot(n[:2],nn)>.9999 and max(abs(xy@nn-CR))<EPS and max(abs(xy@CT[k]))<=CW+EPS:i=1;break
 # Source-facing fascia and original structural corbels; no thin red stripe invented.
 if plane(1,-23) and n[1]<-.8 and bounds((-43,-23,62),(43,-23,64.1)):i=1
 for xc in [-36,-21.6,-7.2,7.2,21.6,36]:
  if boxface(xc-1.25,xc+1.25,-22.5,-15.5,59.8,62.8) and n[2]<.8:i=1
 # Blank low sign panel only; no lettering or gold appearance added.
 if plane(1,-1.2) and n[1]<-.8 and bounds((-13,-1.2,24),(13,-1.2,26.1)):i=1
 # Existing seven stairs, front risers/top treads only; no broad foundation tint.
 for k in range(7):
  y=-27+k*1.75;top=2.8+.65*(k+1)
  if bounds((-68.5,y-1.05,2.8),(68.5,y+1.05,top)) and ((plane(2,top) and n[2]>.8) or (plane(1,y-1.05) and n[1]<-.8)):i=4
 if hi[2]<=3+EPS:i=0
 p.material_index=i;indices.append(i)
assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown rear neutral'
scene=bpy.context.scene;scene['appearance_revision']='color-v1'
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.seed=0;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=1
scene.render.resolution_x=900;scene.render.resolution_y=800
for attr in dir(scene.render):
 if attr.startswith('use_stamp'):
  try:setattr(scene.render,attr,False)
  except (TypeError,AttributeError):pass
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.85,.89,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
# New appearance lighting only: remove inherited lamps, never change original scene.
for lamp in list(scene.objects):
 if lamp.type=='LIGHT':bpy.data.objects.remove(lamp,do_unlink=True)
for name,energy,ang,rot in [('Key',2.1,.16,(28,-26,-32)),('Fill',.55,.35,(-20,32,140))]:
 light=bpy.data.lights.new(name,'SUN');light.energy=energy;light.angle=ang;o=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(o);o.rotation_euler=tuple(math.radians(a) for a in rot)

bpy.ops.wm.save_as_mainfile(filepath=str(R/'appearance.blend'))
# Core 3MF base materials per original triangle: no geometry splitting/resampling.
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns)
e=lambda tag,attrs={}:ET.Element('{'+ns+'}'+tag,attrs)
root=e('model',{'unit':'millimeter','xml:lang':'en-US'});res=ET.SubElement(root,'{'+ns+'}resources');bm=ET.SubElement(res,'{'+ns+'}basematerials',{'id':'1'})
for name,col,_ in palette:ET.SubElement(bm,'{'+ns+'}base',{'name':name,'displaycolor':col+'FF'})
o=ET.SubElement(res,'{'+ns+'}object',{'id':'2','type':'model'});m=ET.SubElement(o,'{'+ns+'}mesh');vs=ET.SubElement(m,'{'+ns+'}vertices')
for v in verts:ET.SubElement(vs,'{'+ns+'}vertex',dict(zip(['x','y','z'],[format(c,'.17g') for c in v])))
ts=ET.SubElement(m,'{'+ns+'}triangles')
for f,i in zip(faces,indices):ET.SubElement(ts,'{'+ns+'}triangle',{'v1':str(f[0]),'v2':str(f[1]),'v3':str(f[2]),'pid':'1','p1':str(i),'p2':str(i),'p3':str(i)})
build=ET.SubElement(root,'{'+ns+'}build');ET.SubElement(build,'{'+ns+'}item',{'objectid':'2'})
with zipfile.ZipFile(R/'appearance.3mf','w',zipfile.ZIP_DEFLATED) as out:
 for n,b in {'3D/3dmodel.model':ET.tostring(root,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>','_rels/.rels':b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'}.items():
  info=zipfile.ZipInfo(n,date_time=(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;out.writestr(info,b)
from collections import Counter
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Original single warm display material. One2024-08-25 photograph supports front warm cream-grey walls and six columns, actual grey-white original frames, opaque mixed grey-green window backs and grey steps. Whole column circumference same-material approximation, not all sides photographed. Original full-height facets have no couplet strip boundaries: no red full-column coloring or gold lettering; thin red roof stripe also omitted. Large side walls, artificial rear cut, roof tops and base neutral. This is a front-block portico section, not complete rear building. Original geometry/locked previews/printability caveats remain unchanged; no2026condition or safety claim.','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-220,145),(0,0,33),220),'rear':((195,230,145),(0,0,33),220),'elevation':((0,-260,33),(0,0,33),220),'source-angle':((30,-260,85),(0,0,33),220),'top':((0,0,350),(0,0,33),220)}
out=R/'appearance';out.mkdir(exist_ok=True)
for name,(pos,target,scale) in ([] if '--skip-render' in sys.argv else views.items()):
 c=scene.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 inv=c.rotation_euler.to_matrix().transposed();projected=[inv@(obj.matrix_world@Vector(corner)-c.location) for corner in obj.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 c.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 data=(out/(name+'.png')).read_bytes(); cleaned=data[:8]; off=8
 while off<len(data):
  length=struct.unpack_from('>I',data,off)[0];typ=data[off+4:off+8];body=data[off+8:off+8+length];key=body.split(b'\0',1)[0]
  variable=typ in (b'tEXt',b'zTXt',b'iTXt') # no private path/date/timing metadata
  if not variable:cleaned+=data[off:off+length+12]
  off+=length+12
 (out/(name+'.png')).write_bytes(cleaned)
print('APPEARANCE_DONE',before,dict(Counter(indices)))
