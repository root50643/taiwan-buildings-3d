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
# Official document supports front arcade and front roof only.
palette=[('Unknown surfaces neutral','#AAA79F',.86),('Observed brick two adjacent walls','#A56553',.86),('Original stone supports','#A8ABA3',.86),('Original pale clock dials','#D0D1C4',.86),('Historical opaque bell','#343A34',.86),('Visible original step risers','#868C84',.86)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
import numpy as np
EPS=.003;indices=[]
def bounds(a,b):return bool(np.all(lo>=np.array(a)-EPS) and np.all(hi<=np.array(b)+EPS))
def plane(k,t):return max(abs(q[:,k]-t))<EPS
def edges(poly):
 ans=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  e=b-a;v=np.array([e[1],-e[0]],dtype=float);v/=np.linalg.norm(v);ans.append((a,v))
 return ans
def inside(p,ed):return all(max((p-a)@v)<=EPS for a,v in ed)
def area(p):return abs(sum(np.cross(b-a,c-a) for a,b,c in [(p[0],p[k],p[k+1]) for k in range(1,len(p)-1)]))*.5 if len(p)>2 else 0.
def clip(poly,ed):
 out=list(poly)
 for a,v in ed:
  src=out;out=[]
  if not src:break
  for u,w in zip(src,src[1:]+src[:1]):
   du=(u-a)@v;dw=(w-a)@v;iu=du<=1e-8;iw=dw<=1e-8
   if iu:out.append(u)
   if iu!=iw:out.append(u+(w-u)*du/(du-dw))
 return out
def segmentpoly(z,w,h,rise):
 spring=z+h-rise
 return np.array([(-w/2,z),(w/2,z),(w/2,spring)]+[(w/2*np.cos(t),spring+rise*np.sin(t)) for t in np.linspace(0,np.pi,33)[1:]])
def surface_poly(poly,y0,y1):
 ed=edges(poly);qq=q[:,[0,2]]
 if lo[1]<y0-EPS or hi[1]>y1+EPS or not inside(qq,ed):return False
 if (plane(1,y0) and n[1]<-.99) or (plane(1,y1) and n[1]>.99):return True
 return any(max(abs((qq-a)@v))<EPS and n@np.array([v[0],0,v[1]])>.999 for a,v in ed)
def ring(z,w,h,rise,th,y):
 oe=edges(segmentpoly(z,w+2*th,h+th,rise+th));ie=edges(segmentpoly(z-.2,w,h+.2,rise));qq=q[:,[0,2]]
 if not bounds((-w/2-th,y-1.2,z),(w/2+th,y+1.2,z+h+th)) or not inside(qq,oe):return False
 if ((plane(1,y-1.2) and n[1]<-.99) or (plane(1,y+1.2) and n[1]>.99)) and area(clip(qq,ie))<1e-6:return True
 return any(max(abs((qq-a)@v))<EPS and n@np.array([sign*v[0],0,sign*v[1]])>.999 for ed,sign in [(oe,1),(ie,-1)] for a,v in ed)
def diskpoly(rad):return np.array([(rad*np.cos(t),130+rad*np.sin(t)) for t in np.arange(48)*2*np.pi/48])
def rim():
 oe=edges(diskpoly(9.3));ie=edges(diskpoly(7.6));qq=q[:,[0,2]]
 if not bounds((-9.3,-36,120.7),(9.3,-34.8,139.3)) or not inside(qq,oe):return False
 if ((plane(1,-36) and n[1]<-.99) or (plane(1,-34.8) and n[1]>.99)) and area(clip(qq,ie))<1e-6:return True
 return any(max(abs((qq-a)@v))<EPS and n@np.array([sg*v[0],0,sg*v[1]])>.999 for ed,sg in [(oe,1),(ie,-1)] for a,v in ed)
def coneface(z,h,r0,r1,segments):
 if not bounds((-max(r0,r1),-max(r0,r1),z),(max(r0,r1),max(r0,r1),z+h)):return False
 dr=(r1-r0)/h;theta=(np.arange(segments)+.5)*2*np.pi/segments;c=np.cos(np.pi/segments)
 if ((plane(2,z) and n[2]<-.99) or (plane(2,z+h) and n[2]>.99)):
  rr=r0 if plane(2,z) else r1
  return all(max(q[:,:2]@np.array([np.cos(t),np.sin(t)]))<=rr*c+EPS for t in theta)
 for t in theta:
  u=np.array([np.cos(t),np.sin(t)]);nn=np.array([u[0],u[1],-dr*c]);nn/=np.linalg.norm(nn)
  if max(abs(q[:,:2]@u-(r0+(q[:,2]-z)*dr)*c))<EPS and n@nn>.999:return True
 return False
wedge1=np.array([[-36,118],[0,144],[0,147],[-36,121]])
wedge2=np.array([[0,144],[36,118],[36,121],[0,147]])
gable=edges(np.array([[-35,118.5],[35,118.5],[0,144]]))
for p in mesh.polygons:
 originalq=np.array([verts[j] for j in p.vertices]);originaln=np.array(p.normal);i=0
 # Actual two source-observed adjacent sides, assigned illustrative -Y and -X.
 for left in [False,True]:
  q=originalq.copy();n=originaln.copy()
  if left:q=np.column_stack((-originalq[:,1],originalq[:,0],originalq[:,2]));n=np.array([-originaln[1],originaln[0],originaln[2]])
  lo=q.min(0);hi=q.max(0)
  if plane(1,-42) and n[1]<-.99 and bounds((-42,-42,7.5),(42,-42,71.5)):i=1
  if plane(1,-33) and n[1]<-.99 and bounds((-33,-33,75.5),(33,-33,119.5)):i=1
  if plane(1,-35) and n[1]<-.99 and inside(q[:,[0,2]],gable):i=1
  if ring(7.6,56,55,14,3,-42) or ring(76,46,36,10,2.2,-33):i=2
  # Only source-visible front fascia of original corner relief and cornices.
  for x in [-36,36]:
   if plane(1,-42.5) and n[1]<-.99 and bounds((x-6.5,-42.5,7.5),(x+6.5,-42.5,21.5)):i=2
  for half,z,h in [(44,69.5,3.5),(47,72.5,3.5)]:
   if plane(1,-half) and n[1]<-.99 and bounds((-half,-half,z),(half,-half,z+h)):i=2
  if surface_poly(wedge1,-36.25,-33.75) or surface_poly(wedge2,-36.25,-33.75):i=2
  if rim():i=2
  if plane(1,-35.2) and n[1]<-.99 and inside(q[:,[0,2]],edges(diskpoly(8.5))):i=3
  # Steps: only two documented riser faces; broad unsplit top surfaces remain neutral.
  for half,z,h in [(51,2.8,1.7),(47.5,4.3,1.7),(43.5,5.8,2)]:
   if plane(1,-half) and n[1]<-.99 and bounds((-half,-half,z),(half,-half,z+h)):i=5
 q=originalq;n=originaln;lo=q.min(0);hi=q.max(0)
 if coneface(88,22,10,6,40) or coneface(86,3,11.5,10,40) or coneface(109,10,3,3,24):i=4
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Four-way openings remain genuinely open, not glass; historical bell is original fused geometry','Two official day/night and one listed visitor day photo personally read. Capture dates unknown; article2025date not freshly verified; night orange lighting not finish color. Two observed adjacent faces mapped to -Y/-X only illustrative not geographic. Original lower and upper brick walls, gable face planes, exact32segment surrounds and48facet dials/rims supported. Unseen opposite faces, large roof slopes, ridge balls, broad unsegmented step tops and interiors neutral. Front/left step risers only, no invented lower wall stone belt. Full original fused bell with40facet tapered body and24facet neck is historic-photo proxy, not2026 presence confirmation. No clock hands/numbers/tile/brick textures/new topology or filled portals. Original printQA and support warnings unchanged','No actual trial print; original partial-model QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((-220,-260,195),(0,0,75),230),'rear':((220,260,195),(0,0,75),230),'elevation':((0,-320,75),(0,0,75),230),'source-angle':((-270,-180,180),(0,0,75),230),'top':((0,0,420),(0,0,75),230)}
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
