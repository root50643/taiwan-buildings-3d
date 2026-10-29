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
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');mesh=obj.data
verts=[tuple(v.co) for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
assert all(len(f)==3 for f in faces)
def digest(a,fmt):return hashlib.sha256(b''.join(struct.pack(fmt,*r) for r in a)).hexdigest()
before={'vertices':digest(verts,'<3f'),'faces':digest(faces,'<3I')}
# sRGB photo approximations, not calibrated finish specifications.
palette=[('Unknown cut / authored base','#949793',.82),('Rose brown wall','#95756C',.8),('Warm sand tower','#B9A487',.8),('Pale upper tower','#D2C7B0',.8),('Concrete fins and grille','#A2A49E',.84),('Deep green glazing proxy','#22564E',.3),('Pale metal frames','#A8B6AE',.45),('Grey brown sunshades','#797C73',.76)]
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mesh.materials.clear()
for name,col,rough in palette:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple(lin(v) for v in rgb(col))+(1,);bs.inputs['Roughness'].default_value=rough;m.diffuse_color=tuple(rgb(col))+(1,);mesh.materials.append(m)
indices=[]
def near(v,t,e=.035):return abs(v-t)<e
for p in mesh.polygons:
 x,y,z=p.center;n=p.normal;i=1
 # Unobserved cut and authored plinth are explicitly neutral.
 if z<=3.5 or (y>=23.95 and n.y>.3):i=0
 # pale tower; source-visible front beige / upper-side light cream.
 if x>=56.95 and z>3.5:i=2
 if x>=68.95 and z>84:i=3
 # six giant fins, their roof beams, and open high rear grille.
 if z>77.4 and y>=20.95:i=4
 for fx in [-47,-36,-25,-14,-3,8]:
  if abs(x-fx)<=1.66 and ((-11.81<=y<=-4.29 and z>=3) or (85.29<=z<=88.61 and y<=25.01)):i=4
 # front sunshades, return, balcony pier; preserve opaque material.
 if 10.2<x<58 and -19.2<y<-15.7 and any(a-.02<=z<=a+1.22 for a in [49.4,52.5,57,64.4,67.5,72]):i=7
 if 12.15<x<17.05 and -20.25<y<-14.05 and 33.15<z<48.05:i=4
 # lower wing glass: only recessed back planes, not side reveals.
 if -59.01<x<10.01 and near(y,-5.4) and n.y<-.8 and any(a<=z<=b for a,b in [(7,15),(20,28),(34,43)]):i=5
 if -59.01<x<-49.99 and near(y,-6.2) and n.y<-.8 and any(a<=z<=b for a,b in [(49,57),(63,71)]):i=5
 # upper ribbon panes and return recess back planes.
 if any(a<=z<=b for a,b in [(50.5,52.5),(54.1,57),(65.5,67.5),(69.1,72)]):
  if 14.19<x<56.51 and near(y,-16.05) and n.y<-.8:i=5
  if near(x,12.85) and -15.61<y<-7.29 and n.x<-.8:i=5
 # balcony recessed glass back faces.
 if 17.99<x<59.3 and near(y,-6.7) and 36.49<z<45.31 and n.y<-.8:i=5
 # tower's side recessed glass floor, with existing raised mullions left pale.
 if x>=68.15 and -15.05<y<2.75 and 4.8<z<84.2:i=6
 if near(x,68.35) and -14.91<y<2.61 and 5<z<84 and n.x>.8:i=5
 # Drum: silver original frames; only the inset curved pocket backing is glass.
 rad=math.hypot(x-35,y+17);rz=22.5+(27-22.5)*(z-3)/(32.6-3)
 if 3.5<z<32.61 and y<-17 and 7<x<63 and rad>rz-1.2:
  i=6
  if rad<rz-.38 and n.z<.2 and any(a-.01<z<b+.01 for a,b in [(4.5,11.2),(12.45,18.8),(20.05,30.9)]):i=5
 # existing thick railing stays gray proxy: no newly invented glass geometry.
 if 32.1<z<35.2 and y<-17 and rad>25.8:i=6
 if near(z,78) and n.z>.9:i=0 # main roof finish not established by photographs
 if y>=24 and n.y>.5:i=0
 p.material_index=i;indices.append(i)
assert before=={'vertices':digest([tuple(v.co) for v in mesh.vertices],'<3f'),'faces':digest([tuple(p.vertices) for p in mesh.polygons],'<3I')}
obj['appearance_policy']='Source-guided approximate sRGB; same exact vertices/triangles as original; unknown rear neutral'
scene=bpy.context.scene;scene['appearance_revision']='color-v1';scene.cycles.samples=32;scene.cycles.seed=0
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
(R/'appearance-materials.json').write_text(json.dumps({'revision':'color-v1','geometry':before,'palette':[{'name':n,'srgb':c,'roughness':r} for n,c,r in palette],'face_counts':dict(Counter(indices)),'face_material_indices':indices,'limits':['Photographic approximation, not calibrated real finish values','Opaque glazing proxies, no real transparency or physical material certification','Unknown rear cut neutral; authored base not a grass slope','No actual trial print; original small-feature QA caveats remain']},indent=2))
# New images only; locked previews/front.png and original scene are never overwritten.
views={'front':((165,-265,165),(0,-6,45),205),'rear':((-165,265,165),(0,-6,45),205),'elevation':((0,-320,52),(0,0,52),180),'top':((0,-7.5,360),(0,-7.5,0),180)}
out=R/'appearance';out.mkdir(exist_ok=True)
for name,(pos,target,scale) in ([] if '--skip-render' in sys.argv else views.items()):
 c=scene.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 data=(out/(name+'.png')).read_bytes(); cleaned=data[:8]; off=8
 while off<len(data):
  length=struct.unpack_from('>I',data,off)[0];typ=data[off+4:off+8];body=data[off+8:off+8+length];key=body.split(b'\0',1)[0]
  variable=typ==b'tEXt' and key.startswith(b'cycles.') and key.endswith((b'.total_time',b'.render_time',b'.synchronization_time'))
  if not variable:cleaned+=data[off:off+length+12]
  off+=length+12
 (out/(name+'.png')).write_bytes(cleaned)
print('APPEARANCE_DONE',before,dict(Counter(indices)))
