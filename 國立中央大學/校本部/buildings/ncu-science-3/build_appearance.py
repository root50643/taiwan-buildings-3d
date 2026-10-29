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
# Full frontal Commons photo plus official SB3 entrance crop; not current-state survey.
palette=[('Unknown outer sides rear roof base','#A6AAA5',.86),('Pink grey original front columns and inner recesses','#B9A3A0',.84),('Dark grey green original window proxies','#4E5B57',.55),('Lighter inner entrance window curtain proxy','#7C8880',.55),('Pale grey original exhaust bodies','#BBC0B8',.78),('Grey original exhaust caps','#7D8882',.72),('Muted grey original steps','#A4AAA0',.85)]
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
 # Main photographed front and existing recess returns only, not outer rear walls.
 if near(y,-27,.015) and ny<-.8 and 3<z<60.81:i=1
 if near(y,-6,.015) and ny<-.8 and -65.01<x<-17.99 and 17<z<45:i=1
 if near(y,-16,.015) and ny<-.8 and -14.01<x<10.01 and 3<z<44:i=1
 if near(x,-18,.015) and nx<-.8 and -27.01<y<-5.99 and 17<z<45:i=1
 if near(x,-14,.015) and nx>.8 and -27.01<y<-15.99 and 3<z<44:i=1
 if near(x,10,.015) and nx<-.8 and -27.01<y<-15.99 and 3<z<44:i=1
 for xx in [-62,-34,-7]:
  if boxed(p,xx-1.4,xx+1.4,-30.25,-25.75,3,46):i=1
 if boxed(p,-63.5,-24.5,-29,1,31,33.2):i=1
 if boxed(p,-14,10,-18,-10,30,32.2):i=1
 # Original front backing planes: window and small vent slots, no new tile bands.
 if near(y,-25.5,.015) and ny<-.8:
  if any(abs(x-xx)<5.01 for xx in range(-56,57,15)) and (48.99<z<55.01 or 55.99<z<58.41):i=2
  if 6.99<x<63.01 and any(zz-.01<z<zz+7.01 for zz in [8,21,35]):i=2
 # Original mullions dividing lower right continuous openings, same pink structural family.
 for xx in [12,26,40,54]:
  for zz in [8,21,35]:
   if boxed(p,xx-.7,xx+.7,-28.75,-25.25,zz,zz+7):i=1
 if near(y,-5,.015) and ny<-.8 and any(abs(x-xx)<8.01 for xx in [-48,-21]) and any(zz-.01<z<zz+6.51 for zz in [21,35]):i=2
 if near(y,-14.6,.015) and ny<-.8 and -7.01<x<9.01 and any(zz-.01<z<zz+6.51 for zz in [21,35]):i=3
 # Original five vent groups only, not arbitrary roof machinery or new cap geometry.
 for xx,yy in [(-13,7),(-7,7),(36,11),(47,11),(52,11)]:
  if boxed(p,xx-2.6,xx+2.6,yy-2.6,yy+2.6,60.5,66):i=4
  if boxed(p,xx-2.6,xx+2.6,yy-2.6,yy+2.6,65,66):i=5
 for k in range(3):
  if boxed(p,-20,16,-39.85+k*1.4,-38.15+k*1.4,2.8,2.8+.7*(k+1)):i=6
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown outer sides rear flatroof neutral; narrow grey-green tile bands omitted without original face boundaries; no added entrance lettering glass frames or AC','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-260,145),(0,0,33),220),'rear':((195,260,145),(0,0,33),220),'elevation':((0,-300,33),(0,0,33),220),'source-angle':((-35,-300,50),(0,0,33),220),'top':((0,0,330),(0,0,0),220)}
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
