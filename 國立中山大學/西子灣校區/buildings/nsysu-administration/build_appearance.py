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
# Four official admin-main-block photos; not adjacent red campus wings, dates unknown.
palette=[('Unknown sides rear roofs base','#A7AAA5',.86),('Muted brick red source-visible front wall','#9D6757',.86),('Pale grey beige original columns beams trim','#BBBBA9',.85),('Grey blue upper window proxies','#7D9596',.58),('Dark grey green lower window proxies','#414D49',.65),('Deep grey green entrance proxy','#293A34',.7),('Neutral grey original steps','#969B91',.86)]
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
 # Original front brick-backed main wall and upper box; unknown sides/rear left neutral.
 if near(y,-34.5,.015) and ny<-.8 and boxed(p,-59,59,-34.5,-34.5,2.8,64.2):i=1
 if near(y,-49.5,.015) and ny<-.8 and boxed(p,-65,65,-49.5,-49.5,65.4,88.4):i=1
 # Four actual24-facet columns, no arbitrary shadow staining or banners.
 for xx in [-54,-18,18,54]:
  if boxed(p,xx-2.05,xx+2.05,-46.05,-41.95,3,64):i=2
 for xx in [-42,-30,-6,6,30,42]:
  if boxed(p,xx-.675,xx+.675,-42.35,-39.65,29,63):i=2
 for zz in [27,39,51,62]:
  if boxed(p,-56.5,56.5,-45.5,-36.5,zz,zz+2.2):i=2
 # Existing projecting upper soffit slab; not broad roof or invented vertical piers.
 if boxed(p,-67,67,-51,59,63,65.6) and (nz<-.8 or (ny<-.8 and near(y,-51,.015))):i=2
 # Actual lower window backing planes, not portico depth or adjacent bays.
 for xx in [-44,-26,26,44]:
  for zz in [7,18,30,42,54]:
   if near(y,-33.3,.015) and ny<-.8 and boxed(p,xx-6.5,xx+6.5,-33.3,-33.3,zz,zz+7.3):i=4
 for xx in [-10,10]:
  for zz in [30,42,54]:
   if near(y,-33.3,.015) and ny<-.8 and boxed(p,xx-7,xx+7,-33.3,-33.3,zz,zz+7.3):i=4
 if near(y,-33.1,.015) and ny<-.8 and boxed(p,-15,15,-33.1,-33.1,3,24):i=5
 for xx in range(-58,59,12):
  if near(y,-48.2,.015) and ny<-.8 and boxed(p,xx-5.25,xx+5.25,-48.2,-48.2,67,74):i=3
  if boxed(p,xx-.5,xx+.5,-51,-49,67,74):i=2
 if near(y,-46.5,.015) and ny<-.8 and boxed(p,-17,17,-46.5,-46.5,78,84.7):i=4
 for xx in [-60,60]:
  if near(y,-48.4,.015) and ny<-.8 and boxed(p,xx-3.25,xx+3.25,-48.4,-48.4,78,81.8):i=3
 # Existing balcony base slab and narrow top face pale; original curved fascia red, not added text/rail.
 if boxed(p,-18,18,-52,-38,29,31.4):i=2
 if near(z,35.4,.015) and nz>.8 and boxed(p,-18,18,-52,-38,35.4,35.4):i=2
 if abs(nz)<.01 and ny<0 and boxed(p,-18,18,-52,-38,29,35.4):
  for k in range(48):
   aa=math.pi-k*math.pi/48;bb=math.pi-(k+1)*math.pi/48
   ax,ay=18*math.cos(aa),-38-14*math.sin(aa);bx,by=18*math.cos(bb),-38-14*math.sin(bb)
   dx,dy=bx-ax,by-ay;ll=math.hypot(dx,dy)
   if all(abs((mesh.vertices[v].co.x-ax)*dy-(mesh.vertices[v].co.y-ay)*dx)/ll<.015 for v in p.vertices):i=1
 for k in range(4):
  if boxed(p,-39,39,-58.3+2*k,-55.7+2*k,2.8,3.4+.8*k):i=6
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown sides rear roofs lightwell neutral; no adjacent campus wings, banners, golden text, grid ceilings or unbounded brick trim divisions added','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-280,165),(0,0,46.5),220),'rear':((195,280,165),(0,0,46.5),220),'elevation':((0,-330,46.5),(0,0,46.5),220),'source-angle':((-150,-270,85),(0,0,46.5),220),'top':((0,0,350),(0,0,0),220)}
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
