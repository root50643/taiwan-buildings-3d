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
# Architect-supplied009/010/014: rectangular teaching building, not adjacent colorful auditorium.
palette=[('Unknown outer left rear broad roof base','#A7AAA5',.86),('Pale grey beige source-visible frame walls','#C0C2B9',.84),('Grey blue green original window proxies','#657E7B',.55),('Pale original exterior mullions','#B8BFBB',.8),('Warm grey original small round lecture wall and rails','#B6B2A5',.84),('Grey metal roof wells not photovoltaic certification','#AAB1B0',.8),('Muted ochre brown limited original terrace floor','#AF8A62',.86),('Grey original entrance steps','#A0A69C',.85)]
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
 # Observed monumental front and court opening, not far end/back or unobserved left exterior.
 if near(y,-59,.015) and ny<-.8 and -53.01<x<53.01 and 3<z<63:i=1
 if near(x,53,.015) and nx>.8 and -59.01<y<59.01 and 3<z<63:i=1
 if near(x,25,.015) and nx<-.8 and -59.01<y<35.01 and 3<z<54:i=1
 if near(x,-25,.015) and nx>.8 and -59.01<y<35.01 and 3<z<54:i=1
 if near(y,35,.015) and ny<-.8 and -25.01<x<25.01 and 3<z<54:i=1
 if near(z,54,.015) and nz<-.8 and -25.01<x<25.01 and -59.01<y<35.01:i=1
 # Source-visible right exterior original long window backs; left outer face remains unknown.
 if near(x,51.5,.015) and nx>.8 and -53.01<y<53.01 and any(zz-.01<z<zz+6.61 for zz in [8,20,32,44,54]):i=2
 for zz in [8,20,32,44,54]:
  for yy in range(-49,50,7):
   if boxed(p,51,55,yy-.5,yy+.5,zz,zz+6.6):i=3
 # Inner courtyard true windows, not arbitrary metal spandrel bands.
 for side in [-1,1]:
  if near(x,side*26.5,.015) and nx*side<-.8 and any(abs(y-yy)<5.01 for yy in [-46,-32,-18,-4,10,24]) and any(zz-.01<z<zz+6.01 for zz in [9,21,33,45]):i=2
 for zz in [15,27,39]:
  if boxed(p,-27.5,27.5,16.5,23.5,zz,zz+2.3):i=1
  if boxed(p,-27.5,27.5,15.8,17.2,zz+2,zz+4):i=4
 # Existing shallow roof-well floors only; broad roof and mechanical boxes neutral.
 if near(z,61,.015) and nz>.8 and any(boxed(p,xx-12.5,xx+12.5,-29.5,23.5,61,61) for xx in [-31,31]):i=5
 # Original round lecture body only, not the separate auditorium or its blue night glass.
 radius=math.hypot(x-26,y+53)
 actual_round_face=abs(nz)<.015 and all(abs(nx*(mesh.vertices[v].co.x-26)+ny*(mesh.vertices[v].co.y+53)-20*math.cos(math.pi/96))<.015 for v in p.vertices)
 if actual_round_face and 3<z<33.81:i=4
 if actual_round_face and boxed(p,6,46,-73,-33,26.3,31):i=2
 for zz in [25,31]:
  if boxed(p,5.2,46.8,-73.8,-32.2,zz,zz+1.3):i=4
 if boxed(p,5.5,46.5,-73.5,-32.5,33,35.2):i=4
 # Exact pre-existing cut-floor face only, not planting or invented timber subdivisions.
 if near(z,33,.015) and nz>.8 and boxed(p,10.5,41.5,-68.5,-37.5,33,33):i=6
 for k in range(4):
  if boxed(p,-23,-1,-65.85+k*1.4,-64.15+k*1.4,2.8,2.8+.7*(k+1)):i=7
 # True planar court window backs remain window material at round-wall/rim intersections.
 for side in [-1,1]:
  if near(x,side*26.5,.015) and nx*side<-.8 and any(abs(y-yy)<5.01 for yy in [-46,-32,-18,-4,10,24]) and any(zz-.01<z<zz+6.01 for zz in [9,21,33,45]):i=2
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown left exterior far rear broad roofs neutral; no adjacent auditorium colors or nighttime yellow lighting; missing metal spandrel boundaries omitted not subdivided; terrace only exact existing floor','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((195,-260,145),(0,0,34.5),220),'rear':((-195,260,145),(0,0,34.5),220),'elevation':((0,-300,34.5),(0,0,34.5),220),'source-angle':((260,-180,130),(0,0,34.5),220),'top':((0,0,330),(0,0,0),220)}
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
