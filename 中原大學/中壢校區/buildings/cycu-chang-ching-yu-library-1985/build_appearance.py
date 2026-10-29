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
# Contemporary photographic approximation, NOT a reconstruction of 1985 finishes.
palette=[('Unknown paving and display base','#A9AAA5',.85),('Grey beige faint pink tile','#A89E96',.83),('Exposed concrete columns and steps','#B3B0A6',.85),('Grey blue glass proxy','#48555F',.4),('Dark grey existing frames','#555859',.6),('Unknown roof neutral proxy','#A5A6A1',.85)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
# Coordinates below are original nominal metres; no mesh coordinate is changed.
s=150/83.5
for p in mesh.polygons:
 x,y,z=p.center.x/s,p.center.y/s,p.center.z/s-1.2;n=p.normal;i=1
 if z<=.01 or (abs(x)>30.25 and z<=4.01) or (y>18.8 and z<=4.11) or (y<-29 and z<=8.21):i=0
 if y<-40 and z>.01:i=2
 # Front terrace top and portico columns are existing concrete, no added lawn.
 if y<-18.5 and z<=8.21:i=2 if z>4.01 else 0
 for cx in [-11,-3.2,4.6,12.4]:
  if math.hypot(x-cx,y+17)<.68 and 8.19<z<12.11:i=2
 # All roof slopes/caps are neutral proxies where photo finish is unresolved.
 if z>=22.44 and (n.z>.1 or (abs(x)<21.42 and any(yy-.01<y<yy+5.51 for yy in [-9.2,-3.2,2.8]) and z<=26.21) or (z<23.81 and any(abs(x-cx)<2.21 and abs(y-cy)<2.21 for cx in [-24,24] for cy in [-13.3,13.3]))):i=5
 # Only actual backing planes receive glass; side mid-wall grooves stay opaque.
 glass=False
 if 20.09<z<22.21:
  glass=(near(abs(y),17.85,.012) and n.y*y>0.8*abs(y)) or (near(abs(x),29.4,.012) and n.x*x>0.8*abs(x))
 if 16.14<z<18.61 and near(abs(y),17,.012) and n.y*y>0.8*abs(y):glass=True
 if 12.54<z<15.11 and near(abs(y),16.95,.012) and n.y*y>0.8*abs(y):glass=True
 for lo,hi in [(.8,3.3),(4.5,7.4),(8.7,11.4)]:
  if lo-.001<z<hi+.001 and near(abs(y),17.1,.012) and n.y*y>0.8*abs(y):glass=True
 for lo,hi in [(.7,3.3),(4.5,7.2),(8.7,11.4)]:
  if lo-.001<z<hi+.001 and near(abs(x),28.7,.012) and n.x*x>0.8*abs(x):glass=True
 if 8.59<z<11.51 and near(y,-13.85,.012) and n.y<-.8:glass=True
 # Actual backed narrow mullions only, not opaque wide bands or solid side ribs.
 if (16.09<z<18.71 and 16.924<abs(y)<17.156) or (12.49<z<15.151 and 16.874<abs(y)<17.106):
  if any(abs(x-(-26+j*2.6))<.191 for j in range(21)):i=4
 for yy in [-9.2,-3.2,2.8]:
  if 23.59<z<25.51 and near(y,yy+5.05,.012) and n.y>.8:glass=True
 # Existing four tilted south plaza skylights, no new frames or text.
 if abs(x-4)<5.5 and abs(y+33)<5.5 and 8.21<z<=10.001 and n.z>.65:glass=True
 if glass:i=3
 p.material_index=i;indices.append(i)
assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unresolved roof neutral; contemporary photo approximation, not 1985 finishes'
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unresolved roof and paved base neutral; no invented greenery; contemporary finish not 1985 restoration','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((150,-250,90),(0,-15,20),205),'rear':((125,220,90),(0,-5,22),205),'top':((0,-21,300),(0,-21,0),205),'aerial':((150,-230,220),(0,-18,15),205),'side':((-240,0,85),(0,-10,22),205),'entry':((0,-240,90),(0,-15,20),205),'garden':((120,180,100),(0,-5,22),205),'roof':((150,-100,220),(0,-10,22),205)}
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
