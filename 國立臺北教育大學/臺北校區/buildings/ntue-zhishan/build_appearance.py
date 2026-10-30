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
# Official disaster-plan PDF photos support three original exterior faces; unknown fourth side/roof neutral.
palette=[('Unknown unobserved surfaces neutral','#AAA79F',.86),('Observed brick exterior family','#A56C59',.86),('Opaque mixed window backing proxy','#82918D',.62),('Original canopy front rim red','#A9443D',.78),('Original canopy pale underside','#BBB9A9',.84),('Original entrance steps','#969A90',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
S=150/117.7;EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def boxsurface(x,y,z,w,d,h):
 aa=np.array([x-w/2,y-d/2,z]);bb=np.array([x+w/2,y+d/2,z+h])
 if not bounds(aa,bb):return False
 return any((plane(k,aa[k]) and n[k]<-.999) or (plane(k,bb[k]) and n[k]>.999) for k in range(3))
def back_y(x,y,z,w,h,sg):return plane(1,y) and n[1]*sg>.999 and bounds((x-w/2,y,z),(x+w/2,y,z+h))
def back_x(x,y,z,w,h):return plane(0,x) and n[0]>.999 and bounds((x,y-w/2,z),(x,y+w/2,z+h))
poly=np.array([(-33.5,-6),(-30,-8),(-20,-11),(0,-13.5),(20,-11),(30,-8),(33.5,-6),(33.5,10.5),(-33.5,10.5)],dtype=float)+[14,-34]
edges=[]
for a,b in zip(poly,np.roll(poly,-1,axis=0)):
 e=b-a;v=np.array([e[1],-e[0]],dtype=float);v/=np.linalg.norm(v);edges.append((a,b,v))
def canopy_inside():return all(max((q[:,:2]-a)@v)<=EPS for a,b,v in edges)
def canopy_rim():
 if lo[2]<17-EPS or hi[2]>19.5+EPS or not canopy_inside():return False
 return any(max(abs((q[:,:2]-a)@v))<EPS and n@np.array([v[0],v[1],0])>.999 for a,b,v in edges[:6])
for p in mesh.polygons:
 q=np.array([verts[j] for j in p.vertices])/S;n=np.array(p.normal);lo=q.min(0);hi=q.max(0);i=0
 # Exact original source-visible exterior planes; unseen fourth wall and returns stay neutral.
 if back_y(0,-30,2.8,98,114,-1) or back_y(0,42,2.8,98,114,1):i=1
 if plane(0,49) and n[0]>.999 and bounds((49,-30,2.8),(49,42,116.8)):i=1
 if back_y(39,46.5,14,18,102.8,1):i=1
 # Genuine original cut backs only, never the void of the large entrance recess.
 for z in [33,47,61]:
  for x in [-36,-17,2,21]:
   if back_y(x,-27.8,z,16,7.6,-1):i=2
 for z in [75,88,101]:
  for x in [-20.25,-10.75,-1.25,8.25,17.75,27.25]:
   if back_y(x,-27.8,z,6.8,7.8,-1):i=2
 for x in [-37,-24,-11]:
  if back_y(x,-27.75,19,9.5,7.5,-1):i=2
 if back_y(23,-27,19,39,8.3,-1):i=2
 for x,w in [(-1,28),(25,16)]:
  if back_y(x,-28,112,w,2.1,-1):i=2
 for x in [9,23,37]:
  if back_y(x,-20.5,4,10,11,-1):i=2
 for y in [-14,18]:
  for z in [10,24,38,52,66,80,94,108]:
   if back_x(47.1,y,z,2.6,6.8):i=2
 for z in [20,34,48,62,76,90,104]:
  for x in [-31,-8,15]:
   if back_y(x,39.75,z,16,8,1):i=2
  for x in [35,43]:
   if back_y(x,44.5,z,4.5,8,1):i=2
 if canopy_rim():i=3
 if plane(2,17) and n[2]<-.999 and canopy_inside():i=4
 for k in range(4):
  if boxsurface(15,-45+k*2,2.8,61,2.8,.65*(k+1)):i=5
 p.material_index=i;indices.append(i)

assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown or unresolved surfaces neutral'
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Original recessed entrance remains open; mixed window color only on actual cut backing planes, never on a filled portal','Official PDFphysical35 printed2-29 front and rear-side photos personally read, identity18-06 onphysical34 and groundplan37. Document2023-10-25/table2023-09-13 not capture dates and no2026 current-condition guarantee. Front -Y, slit side +X, rear +Y and projecting strip exterior +Y use observed brick family with locally tree-obscured continuity disclosed. Unseen -X, projection returns, roofs/parapet tops, window reveals and internal ceilings neutral. Opaque mixed glass/reflection/curtain/shadow proxy only on genuine original cut backs. Canopy six front polygon extrusion edges red, original underside pale; canopy top and back/side edges neutral. Original steps gray. No new mullions, letters, AC, trees or geometry. Classifier uses pre-scale primitives, original scale150/117.7 and mesh unchanged. Original printQA and support warnings unchanged','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-220,-270,200),(0,0,75),230),'rear':((220,270,200),(0,0,75),230),'elevation':((0,-350,75),(0,0,75),230),'source-angle':((250,-230,170),(0,0,75),230),'top':((0,0,450),(0,0,75),230)}
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
