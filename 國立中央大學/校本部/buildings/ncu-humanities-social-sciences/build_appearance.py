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
# Two architect exterior photographs; remaining photos unread, capture date unknown.
palette=[('Unknown roof rear outer flank display base','#A7A9A5',.86),('Muted ochre orange source-visible cladding','#B88A4D',.85),('Pale beige grey courtyard wall proxy','#C4BFB0',.84),('Coarse grey source-visible tower side and window box','#92968C',.87),('Dark grey green existing glazing or mixed recess proxy','#455652',.5),('Dark brown original frames and bridge','#655246',.8),('Grey original stair and platform walking surface','#9D9D92',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
for p in mesh.polygons:
 x,y,z=p.center;n=p.normal;i=0
 # Actual ochre front faces of existing left tower and right theatre block, not entire complex.
 if near(y,-53,.015) and n.y<-.8 and -55.51<x<-30.49 and 3<z<88.81:i=1
 if near(y,-53.5,.015) and n.y<-.8 and -55.01<x<-28.99 and 3<z<80.81:i=1
 if near(y,-50,.015) and n.y<-.8 and 12.99<x<61.01 and 3<z<44.81:i=1
 # Source-visible inward side of theatre, bounded to original wall plane.
 if near(x,13,.015) and n.x<-.8 and -50.01<y<18.01 and 3<z<44.81:i=1
 # Tall tower right side visibly rough grey; same known plane only.
 if near(x,-30.5,.015) and n.x>.8 and -53.01<y<-32.99 and 3<z<88.81:i=3
 # Ivory courtyard elevations, not outer rear.
 if near(x,-29,.015) and n.x>.8 and -53.51<y<59.51 and 3<z<80.81:i=2
 if near(y,34.5,.015) and n.y<-.8 and -39.01<x<39.01 and 3<z<67.81:i=2
 # Existing slot backings are mixed shade/louver/glazing proxies, not certified all-glass bands.
 if near(y,-51.5,.015) and n.y<-.8 and -47.51<x<-40.49 and 12.99<z<83.01:i=4
 if near(x,-30.3,.015) and n.x>.8 and any(abs(y-yy)<2.61 for yy in [-30,-13,4,21,38]) and 26.99<z<74.01:i=4
 if near(y,36,.015) and n.y<-.8 and any(abs(x-xx)<2.41 for xx in [-26,-12,2,16,30]) and 24.99<z<58.01:i=4
 # Coarse grey original theatre window box and its actual glazing backing.
 if 14.49<x<59.51 and -56.501<y<-47.499 and 31.99<z<44.01:i=3
 if near(y,-55.5,.015) and n.y<-.8 and 16.99<x<57.01 and 33.49<z<41.51:i=4
 if any(abs(x-xx)<.551 for xx in [21,31,41,51]) and -58.001<y<-55.999 and 33.49<z<41.51:i=5
 # Existing tower and courtyard crossbars; tower crossbar fronts are pale in photographs.
 if -47.901<x<-40.099 and -54.001<y<-51.999 and any(lo-.01<z<lo+1.41 for lo in range(21,78,13)):i=2
 if -30.801<x<-27.799 and any(abs(y-yy)<3.001 for yy in [-30,-13,4,21,38]) and any(lo-.01<z<lo+1.41 for lo in [39,53,67]):i=5
 # Existing cross-bridge/rail component family is brown; platform front fascia pale and treads grey.
 if -30.51<x<34.51 and 7.999<y<14.001 and 27.99<z<30.51:i=5
 if -30.51<x<34.51 and 7.649<y<8.951 and 30.199<z<32.701:i=5
 if -40.01<x<22.01 and -35.51<y<-18.49 and 16.99<z<20.01:i=6 if n.z>.8 else 2
 if -13.01<x<-2.99 and -53.51<y<-24.49 and 16.99<z<20.01:i=6 if n.z>.8 else 2
 # Existing staircase steps and retaining triangle, not arbitrary nearby walls.
 if -7.05<x<57.86 and -59.01<y<-46.99 and 3<z<19.11 and ((n.z>.8 and any(near(z,3.8+.85*k,.015) for k in range(19))) or (n.x>.8 and any(near(x,57.85-3.4*k,.015) for k in range(19)))):i=6
 if near(y,-59.9,.015) and n.y<-.8 and -7.01<x<60.01 and 3<z<21.01:i=3
 # No unsupported horizontal roof finish. Base and unseen opposite/rear remain neutral.
 if z<=3 or (n.z>.8 and z>40):i=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown roofs rear outer flanks neutral; slot colors are mixed recess proxies; no invented louvers or tile seams','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-195,-260,160),(0,0,44.4),220),'rear':((195,260,160),(0,0,44.4),220),'elevation':((0,-300,44.4),(0,0,44.4),220),'source-angle':((150,-300,75),(0,0,44.4),220),'top':((0,0,330),(0,0,0),220)}
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
