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
# Contractor Hakka-specific photograph and official HSB photo; capture dates unknown.
palette=[('Unknown rear large roofs display base','#A7A9A5',.86),('Muted red brown source-visible brick proxy','#946753',.85),('Warm ivory existing eaves gables frames','#D0C6B1',.84),('Grey blue original recessed window proxy','#52656A',.45),('Grey brown existing pitched roof','#827D70',.85),('Grey stone entrance steps','#A2A19B',.85)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
for p in mesh.polygons:
 x,y,z=p.center;n=p.normal;i=0
 # Observed inner courtyard front of tall wing and tower, not unseen rear.
 if near(y,22,.015) and n.y<-.8 and -50.51<x<60.51 and 3<z<86.81:i=1
 if near(y,19.5,.015) and n.y<-.8 and 52.99<x<69.01 and 3<z<103.81:i=1
 if near(y,23,.015) and n.y<-.8 and -43.26<x<53.26 and any(lo-.01<z<lo+7.41 for lo in [9,20,31,42,53,64,75]):i=3
 if near(y,20.5,.015) and n.y<-.8 and 62.89<x<67.11 and 9.99<z<86.01:i=3
 # Existing high facade framing and thin eave components.
 if any(abs(x-xx)<.851 for xx in range(-44,55,11)) and 18.849<y<21.551 and 64.99<z<86.01:i=2
 if -51.51<x<61.51 and 18.249<y<21.751 and 85.49<z<87.51:i=2
 if -51.01<x<61.01 and 17.499<y<22.501 and 61.99<z<63.71:i=2
 if 62.59<x<67.41 and 18.999<y<21.001 and any(lo-.01<z<lo+1.01 for lo in range(18,81,12)):i=2
 # Low return visible inner elevation and its existing gallery back.
 if near(x,-36.5,.015) and n.x>.8 and -31.01<y<41.01 and 3<z<42.81:i=1
 if near(x,-37.55,.015) and n.x>.8 and -25.51<y<31.51 and 28.99<z<37.01:i=3
 if -36.701<x<-33.699 and any(abs(y-yy)<.851 for yy in range(-19,29,12)) and 28.99<z<38.01:i=2
 # Front pavilions: actual front wall, original gable triangles and sloped roof only.
 for cx in [-38,35]:
  if near(y,-44.5,.015) and n.y<-.8 and abs(x-cx)<12.01 and 3<z<22.81:i=1
  if near(y,-43.5,.015) and n.y<-.8 and abs(x-cx)<11.01 and 3<z<16.01:i=3
  if near(y,-46,.015) and n.y<-.8 and abs(x-cx)<14.01 and 22.69<z<29.71:i=2
  if abs(x-cx)<14.01 and -46.01<y<-7.99 and 22.69<z<29.71 and n.z>.2:i=4
  # Existing side arcade component seen in courtyard source; recess shadow is not glazing.
  if near(x,cx+12,.015) and n.x>.8 and -44.51<y<-9.49 and 3<z<22.81:i=1
  if near(x,cx+9,.015) and n.x>.8 and -41.51<y<-14.49 and 3<z<17.01:i=0
  if abs(x-(cx+12))<1.001 and any(abs(y-yy)<1.001 for yy in [-40,-28,-16]) and 3<z<19.01:i=2
  if abs(x-cx)<1.501 and -46.101<y<-43.699 and 28.39<z<30.81:i=2
 # Existing connecting arcade and little pitched roof; all component faces same observed material family.
 if -29.01<x<29.01 and -39.01<y<-28.99 and 17.99<z<20.21:i=2
 if -29.01<x<29.01 and -40.01<y<-27.99 and 19.99<z<22.01:i=4 if n.z>.2 else 2
 if any(abs(x-xx)<.901 for xx in [-24,-12,0,12,24]) and -38.001<y<-35.999 and 3<z<18.31:i=2
 # Tower upper platform/fascia and original shallow pitched cap, not an invented glazing band.
 if 49.99<x<72.01 and 16.99<y<51.01 and 86.99<z<89.21:i=2 if abs(n.z)<.2 else 0
 if 48.99<x<73.01 and 16.99<y<51.01 and 107.99<z<113.01:i=4 if n.z>.2 else 2
 if any(abs(x-xx)<.901 for xx in [55,67]) and 19.99<y<48.01 and 101.99<z<108.01:i=2
 if 20.99<x<49.01 and y<-46.3 and 3<z<5.11:i=5
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown rear large flat roofs neutral; no invented brick texture or extra gable ornament','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-260,170),(0,0,56.5),210),'rear':((195,260,170),(0,0,56.5),210),'elevation':((0,-300,56.5),(0,0,56.5),210),'source-angle':((125,-300,90),(0,0,56.5),210),'top':((0,0,330),(0,0,0),210)}
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
