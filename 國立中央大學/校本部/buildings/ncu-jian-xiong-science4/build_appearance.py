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
# Official astronomy lake photograph; filename is not verified capture date.
palette=[('Unknown outer backs flat roofs base','#A7A9A5',.86),('Pale grey beige lake facade frames and end cores','#BEC0B4',.84),('Dark grey green original window proxies','#485650',.5),('Dark recessed curved galleries not glass','#676E67',.85),('Grey metal opaque simplified satellite dish','#A8AEAA',.72)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
def boxed(p,x0,x1,y0,y1,z0,z1):
 return all(x0-.015<=mesh.vertices[v].co.x<=x1+.015 and y0-.015<=mesh.vertices[v].co.y<=y1+.015 and z0-.015<=mesh.vertices[v].co.z<=z1+.015 for v in p.vertices)
for p in mesh.polygons:
 x,y,z=p.center;nx,ny,nz=p.normal;i=0
 # Source-facing inner L wings only. Broad outside rear faces remain neutral.
 if near(x,-26,.015) and nx>.8 and -62.01<y<56.01 and 3<z<112.81:i=1
 if near(y,28,.015) and ny<-.8 and -42.01<x<64.01 and 3<z<112.81:i=1
 # Exact original frame and slab component bounds, no arbitrary color cuts.
 for yy in [-52,-40,-28,-16,-4,8,20]:
  if boxed(p,-26.15,-23.65,yy-1.1,yy+1.1,3,113):i=1
 for xx in [-14,-2,10,22,34,46,58]:
  if boxed(p,xx-1.1,xx+1.1,25.65,28.15,3,113):i=1
 for zz in [7+10.5*k for k in range(10)]:
  for yy in [-46,-34,-22,-10,2,14]:
   if boxed(p,-26.25,-22.75,yy-5,yy+5,zz+7.5,zz+9):i=1
  for xx in [-8,4,16,28,40,52]:
   if boxed(p,xx-5,xx+5,24.75,28.25,zz+7.5,zz+9):i=1
 # Original recessed window backing planes only, not inferring actual transparent glass.
 if near(x,-27.5,.015) and nx>.8 and any(abs(y-yy)<4.01 for yy in [-46,-34,-22,-10,2,14]) and any(zz-.01<z<zz+6.61 for zz in [7+10.5*k for k in range(10)]):i=2
 if near(y,29.5,.015) and ny<-.8 and any(abs(x-xx)<4.01 for xx in [-8,4,16,28,40,52]) and any(zz-.01<z<zz+6.61 for zz in [7+10.5*k for k in range(10)]):i=2
 # Photo-visible end cores and rounded close end, not their top/back faces.
 if near(y,-63,.015) and ny<-.8 and -60.51<x<-25.49 and 3<z<118.81:i=1
 if near(y,26.5,.015) and ny<-.8 and 54.99<x<67.01 and 3<z<118.81:i=1
 if near(x,67,.015) and nx>.8 and 26.49<y<57.51 and 3<z<118.81:i=1
 if abs(math.hypot(x+36,y+55)-9)<.12 and ny<-.05 and abs(nz)<.2 and 3<z<114.81:i=1
 if near(y,-61.5,.015) and ny<-.8 and -39.51<x<-32.49 and any(zz-.01<z<zz+7.01 for zz in range(7,116,11)):i=2
 if near(y,-62.5,.015) and ny<-.8 and -39.01<x<-28.99 and any(zz-.01<z<zz+6.51 for zz in range(7,108,11)):i=2
 if near(y,28,.015) and ny<-.8 and 58.99<x<63.01 and any(zz-.01<z<zz+8.01 for zz in range(7,116,11)):i=2
 # Curved inner corner: pale projecting slabs, dark recessed galleries NOT glazing.
 if x>-26.01 and y<28.01 and abs(nz)<.2 and 3<z<112.81:
  radius=math.hypot(x+26,y-28)
  if abs(radius-14)<.12:i=1
  if abs(radius-11.5)<.12 and any(zz-.01<z<zz+7.01 for zz in [9+10.5*k for k in range(10)]):i=3
 # Original satellite support and thickened opaque bowl; no missing feed rods invented.
 if boxed(p,27,45,33,51,112,128):i=4
 if z<=3:i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown outer backs roofs neutral; pale pink spandrels omitted where no exact original face boundaries; dark curved recesses are gallery proxies not glass; satellite dish not optical observatory','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((220,-300,180),(0,0,64),220),'rear':((-220,300,180),(0,0,64),220),'elevation':((210,-300,64),(0,0,64),220),'source-angle':((220,-300,85),(0,0,64),220),'top':((0,0,360),(0,0,0),220)}
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
