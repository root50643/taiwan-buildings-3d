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
# Actual independent Commons01 courtyard and05 tower/dish photographs, not all4 sources.
palette=[('Unknown outer sides rear roofs base','#A7AAA5',.86),('Pale grey beige existing courtyard tile walls','#C4C5BA',.84),('Warm grey beige original box shades and entry porch','#BAB5A3',.84),('Grey blue green original window proxies','#727F7D',.55),('Dark original entrance and shade recess shadows not extra glass','#3E4E49',.78),('Pale cream grey source-visible rooftop room walls','#C9C9B9',.84),('Grey coarse original tower staircase','#969F9B',.78),('Near white grey smooth satellite dish and support proxy','#CDD0C7',.72)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
def boxed(p,x0,x1,y0,y1,z0,z1):
 return all(x0-.015<=mesh.vertices[v].co.x<=x1+.015 and y0-.015<=mesh.vertices[v].co.y<=y1+.015 and z0-.015<=mesh.vertices[v].co.z<=z1+.015 for v in p.vertices)
def dish_surface(p):
 c=math.cos(math.radians(35));s=math.sin(math.radians(35))
 for v in p.vertices:
  x,y,z=mesh.vertices[v].co;ly=c*(y-40)-s*(z-86);lz=s*(y-40)+c*(z-86);rr=x*x+ly*ly
  if rr>625.03 or not (abs(lz-rr/100)<.03 or abs(lz-rr/100+2)<.03 or abs(math.sqrt(rr)-25)<.015):return False
 return True
for p in mesh.polygons:
 x,y,z=p.center;nx,ny,nz=p.normal;i=0
 # Original source-visible front wing ends and inner court, not exterior backs.
 if near(y,-60,.015) and ny<-.8 and any(abs(x-xx)<17.51 for xx in [-46,46]) and 3<z<51.81:i=1
 if near(x,-28.5,.015) and nx>.8 and -60.01<y<60.01 and 3<z<51.81:i=1
 if near(x,28.5,.015) and nx<-.8 and -60.01<y<60.01 and 3<z<51.81:i=1
 if near(y,20,.015) and ny<-.8 and -46.51<x<46.51 and 3<z<51.81:i=1
 # Deep upper fascia only photographed inner/front planes, broad tops neutral.
 if near(y,-61.5,.015) and ny<-.8 and any(abs(x-xx)<19.51 for xx in [-46,46]) and 49<z<54:i=1
 if near(x,-26.5,.015) and nx>.8 and -61.51<y<61.51 and 49<z<54:i=1
 if near(x,26.5,.015) and nx<-.8 and -61.51<y<61.51 and 49<z<54:i=1
 if near(y,19,.015) and ny<-.8 and -47.51<x<47.51 and 49<z<54:i=1
 for zz in [7,22,37]:
  for xx in [-46,46]:
   if boxed(p,xx-15.5,xx+15.5,-63.5,-58.5,zz+8,zz+12):i=2
   if near(y,-60.5,.015) and ny<-.8 and abs(x-xx)<13.51 and zz+9.19<z<zz+11.01:i=4
   if near(y,-58.5,.015) and ny<-.8 and any(abs(x-wx)<5.01 for wx in [xx-9,xx+9]) and zz-.01<z<zz+7.01:i=3
  for side in [-1,1]:
   for yy in [-46,-22,2,23]:
    if boxed(p,side*27.5-2.5,side*27.5+2.5,yy-10.5,yy+10.5,zz+8,zz+12):i=2
    if near(x,side*28,.015) and nx*side<-.8 and abs(y-yy)<8.51 and zz+9.19<z<zz+11.01:i=4
    if near(x,side*30,.015) and nx*side<-.8 and abs(y-yy)<8.51 and zz-.01<z<zz+7.01:i=3
  for xx in [-20,0,20]:
   if boxed(p,xx-9,xx+9,16.5,21.5,zz+8,zz+12):i=2
   if near(y,19.5,.015) and ny<-.8 and abs(x-xx)<7.01 and zz+9.19<z<zz+11.01:i=4
   if near(y,21.5,.015) and ny<-.8 and abs(x-xx)<7.01 and zz-.01<z<zz+7.01:i=3
 if boxed(p,-17.5,17.5,5.5,20.5,15,18):i=2
 for xx in [-14,14]:
  if boxed(p,xx-1.25,xx+1.25,5.5,8.5,3,15.2):i=2
 if near(y,21.5,.015) and ny<-.8 and -7.51<x<7.51 and 3<z<14:i=4
 # Roof tower and adjacent room: source-visible front and stair side only, unseen back neutral.
 if near(y,26,.015) and ny<-.8 and -15.51<x<15.51 and 53.5<z<75.5:i=5
 if near(x,-15.5,.015) and nx<-.8 and 25.99<y<54.01 and 53.5<z<75.5:i=5
 if boxed(p,-19,19,22.5,57.5,74.5,77.1) and nz<.8:i=5
 if near(y,28,.015) and ny<-.8 and 26.99<x<45.01 and 53.5<z<63.5:i=5
 if near(x,27,.015) and nx<-.8 and 27.99<y<52.01 and 53.5<z<63.5:i=5
 if boxed(p,25.5,46.5,26.5,53.5,62.5,64.5) and nz<.8:i=5
 if near(y,27.5,.015) and ny<-.8 and any(abs(x-xx)<3.01 for xx in [-8,8]) and 59.99<z<68.01:i=3
 for k in range(12):
  if boxed(p,-21.5,-16.5,28.05+k*1.8,29.95+k*1.8,54,54+(k+1)*1.65):i=6
 if boxed(p,-22.5,-15.5,48,54,72.8,74.8):i=6
 if dish_surface(p) or boxed(p,-3.8,3.8,36.2,43.8,76,85.2):i=7
 # Real rear shade cuts also penetrate the porch; keep the two shared recess backs dark.
 if near(y,19.5,.015) and ny<-.8 and any(abs(x-xx)<7.01 for xx in [-20,0,20]) and any(zz+9.19<z<zz+11.01 for zz in [7,22,37]):i=4
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown outer walls backs broad roofs neutral; shade recesses are dark void proxies not glass; original smooth dish does not add lattice feed struts cables signs or people','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-290,155),(0,0,50),220),'rear':((195,290,155),(0,0,50),220),'elevation':((0,-320,50),(0,0,50),220),'source-angle':((-140,-280,100),(0,20,60),220),'top':((0,0,360),(0,0,0),220)}
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
