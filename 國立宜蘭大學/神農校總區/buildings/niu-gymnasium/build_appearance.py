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
# Historical-source supported facade and entrance material approximation.
palette=[('Unknown side rear roof court and base','#AAA79F',.86),('Supported tile facade and entrance frame','#D4D2C8',.86),('Original separated front storey bands pale pink','#CBB6B1',.86),('True glazing backing opaque mixed appearance','#68716B',.86),('Original supported mullions','#BEBEB0',.82),('Visible original entry step treads and risers','#92958F',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.002;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxface(x,y,z,w,d,h):
 a=(x-w/2,y-d/2,z);b=(x+w/2,y+d/2,z+h)
 return bounds(a,b) and any((plane(k,a[k]) and n[k]<-.8) or (plane(k,b[k]) and n[k]>.8) for k in range(3))
def fx(p):return -65+(p-25)/595*84
rows=[(50.,5.2,[(60,88),(135,163),(173,201),(284,317),(330,359),(443,474),(490,516),(579,597)]),(40.,6.,[(60,90),(135,160),(285,317),(330,359),(489,517),(571,608)]),(28.7,7.4,[(100,163),(250,318),(330,395),(490,555),(572,608)]),(18.3,6.7,[(40,86),(100,163),(250,318),(330,395),(490,555),(572,608)]),(9.5,5.4,[(40,86),(100,163),(250,318),(330,395),(490,555),(572,608)]),(3.8,4.5,[(40,86),(100,163),(250,318),(330,395),(490,555),(572,608)])]
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices]);n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 if plane(1,-59) and n[1]<-.99 and bounds((-65,-59,2.8),(19,-59,60)):i=1
 for x in [fx(167),fx(322),fx(481)]:
  if boxface(x,-59.5,3,1.5,1.2,57.5):i=1
 for z in [8.2,16.9,27.3,38.4,48.5,58.2]:
  if boxface(-23,-59.1,z,85,1.6,1.4):i=2
 # Supported corner only real primitive exterior faces, not a filled balcony.
 for z in [31.2,45.2,58.5]:
  if boxface(27,-54,z,18,15,1.8):i=1
 for z in [33,47]:
  if boxface(27,-60,z,17,1.7,2.5):i=1
 for x in [19.5,34.5]:
  if boxface(x,-60,30.5,2.2,2.7,30):i=1
 if plane(1,-59) and n[1]<-.99 and bounds((19,-59,2.8),(34,-59,60)):i=1
 if plane(1,-40.5) and n[1]<-.99 and bounds((35.5,-40.5,14.5),(60.5,-40.5,39.5)):i=1
 if boxface(48,-42,14.7,29,6,2):i=1
 # Source-visible north portal/frame; upper openings remain genuinely open.
 for z,h in [(35.6,2.5),(44.5,2.4)]:
  if boxface(41,64,z,44,3,h):i=1
 for x in [20,41,62]:
  if boxface(x,64,3,2.8,3,44):i=1
 for spec in [(41,58,16.5,42,14,2),(41,61,24.5,44,11,2),(41,65,26.4,44,2.1,2.8)]:
  if boxface(*spec):i=1
 if plane(1,65.9) and n[1]>.99 and bounds((40.25,65.9,3),(62.75,65.9,25.4)):i=1
 # Only the lower admin frontage, not the unresolved long high hall rear.
 if plane(1,65) and n[1]>.99 and bounds((19,65,2.8),(63,65,25)):i=1
 # True original glazing backs, not slot reveals or new rectangles.
 for z,h,groups in rows:
  for a,b in groups:
   if plane(1,-57.1) and n[1]<-.99 and bounds((fx(a),-57.1,z),(fx(b),-57.1,z+h)):i=3
   x=(fx(a)+fx(b))/2;w=fx(b)-fx(a)
   if w>7 and boxface(x,-58,z-.2,1.1,3.2,h+.4):i=4
 if plane(1,-39.1) and n[1]<-.99 and bounds((37.5,-39.1,18),(58.5,-39.1,36)):i=3
 for x in [40,48,56]:
  if boxface(x,-40,17.8,1.15,3.4,18.5):i=4
 if boxface(48,-40,26.3,22,3.4,1.2):i=4
 for x in [45.4,51.5,57.6]:
  if plane(1,51.2) and n[1]>.99 and bounds((x-2.5,51.2,5.1),(x+2.5,51.2,20.7)):i=3
 for x in [48.3,54.7]:
  if boxface(x,53,4.9,1.1,4.2,16.1):i=4
 if boxface(51.5,53,10,19,4.2,1.2):i=4
 # Stair visible treads and true risers only; no broad bbox side-wall paint.
 for k in range(5):
  y=73.1-k*1.45;h=(k+1)*.5
  if bounds((38.5,y-.85,2.9),(64.5,y+.85,2.9+h)) and ((plane(2,2.9+h) and n[2]>.99) or (plane(1,y+.85) and n[1]>.99)):i=5
 for k in range(14):
  y=-64+k*1.6;h=(k+1)*.87
  if bounds((34.5,y-.95,2.9),(61.5,y+.95,2.9+h)) and ((plane(2,2.9+h) and n[2]>.99) or (plane(1,y-.95) and n[1]<-.99)):i=5
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque mixed glazing backing only; true open courts, arch and upper frames remain open','Historical school-history photographs printed159-161/PDF15-17 personally viewed. Only field-facing facade and source-supported corner/vestibule plus north administrative entrance. Original discrete bands pale pink; true cut backs mixed opaque grey green; actual frames grey beige and exposed stair treads/risers grey. Six facade height bands are not six floors. Long west/high rear/wing side windows/court/whole roof neutral; five crown depths unknown. No murals/banners/new face stripes/phototextures/PV. PDF2020metadata not photography date, no2018-renovation or2026-condition claim. Original maximum openingloss about0.153percent retained, no new printQA','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-200,-250,160),(0,0,32),220),'rear':((170,250,140),(0,0,32),220),'elevation':((0,-300,32),(0,0,32),220),'source-angle':((200,-260,130),(0,0,32),220),'top':((0,0,400),(0,0,32),220)}
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
