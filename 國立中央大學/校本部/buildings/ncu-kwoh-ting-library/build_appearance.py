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
# Undated official LIB_KT photo; approximate colors, no borrowed Commons EXIF date.
palette=[('Unknown sides rear roof display base','#A7A9A5',.86),('Light grey front wing panels','#C7C8C3',.84),('Grey taupe front core belts','#8F8C87',.8),('Dark blue grey front glazing proxy','#3F4C52',.45),('Dark grey existing mullions pergolas trim','#555354',.7),('Grey pink taupe curved porch stone','#8A807E',.85),('Muted brown existing porch cornice','#8C6D5D',.82),('Grey entrance steps','#A2A19B',.85)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
for p in mesh.polygons:
 x,y,z=p.center;n=p.normal;i=0;rad=math.hypot(x,y)
 # Only observed front faces and existing recess reveals, not the large plain side triangles.
 if 21.49<abs(x)<46.51 and -31.51<y<-29.69 and 3<z<127.81:i=1
 if near(y,-15.5,.015) and n.y<-.8 and 46.49<abs(x)<58.51 and 3<z<112.81:i=1
 # Source-visible cylinder front: opaque belts and actual conical recess backings.
 if y<-1 and 24.2<rad<27.1 and 36.79<z<145.81:i=2
 for lo in [36,54,72,90,108,124,135]:
  if lo-.01<z<lo+6.41 and y<-1 and 24.2<rad<25.55 and (n.x*x+n.y*y)>.7*rad:i=3
 if near(y,-29.7,.015) and n.y<-.8 and 28.49<abs(x)<39.51:i=3
 if near(y,-14,.015) and n.y<-.8 and 48.79<abs(x)<53.21:i=3
 # Existing crown mullions use observed dark framing; no thin grids added.
 if 130.99<z<142.01 and y<-1 and 25.2<rad<27.6:
  if any(math.hypot(x-26.4*math.cos(math.radians(a)),y-26.4*math.sin(math.radians(a)))<1.12 for a in range(210,331,20)):i=4
 # Same-material extension only on original visible pergola component family.
 if 43.49<abs(x)<58.51 and -11.01<y<23.01 and 113.49<z<122.71:i=4
 if 19.99<abs(x)<48.01 and near(y,-32.5,.015) and n.y<-.8 and 126.99<z<129.01:i=4
 # Low elliptical porch front stone. Pale upper panels lack separable faces: omitted.
 er=math.hypot(x/40,(y+21)/18.8)
 if y<-21 and .995<er<1.005 and 3<z<36.8 and abs(n.z)<.25:i=5
 if near(y,-35,.015) and n.y<-.8 and abs(x)<18.01 and 3<z<20.01:i=3
 if near(y,-32.5,.015) and n.y<-.8 and 25.99<abs(x)<30.01 and 4.99<z<19.01:i=3
 if y<-21 and 35.99<z<37.81 and abs(n.z)<.25 and math.hypot(x/41,(y+21)/(41*.47))>.99:i=6
 if abs(x)<36.01 and y<-41.9 and 3<z<5.61:i=7
 # Never transfer a front-wall color onto unknown broad side/rear planes or roof tops.
 if (any(near(abs(x),xx,.015) for xx in [21.5,46.5,58.5]) and abs(n.x)>.8) or (near(y,41.5,.015) and n.y>.8):i=0
 if z<=3 or (n.z>.8 and z>35.9):i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown sides rear roof neutral; pale porch panels omitted rather than inventing face splits','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-260,170),(0,0,72.9),200),'rear':((195,260,170),(0,0,72.9),200),'elevation':((0,-300,72.9),(0,0,72.9),200),'source-angle':((75,-300,55),(0,0,72.9),200),'top':((0,0,330),(0,0,0),200)}
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
