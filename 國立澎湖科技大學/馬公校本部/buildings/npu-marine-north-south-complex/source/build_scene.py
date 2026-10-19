"""Render actual print meshes and keep four editable material slots.
Blender 4.5 CLI: blender -b --python source/build_scene.py
No source photographs or textures are embedded. BU=1mm via scale_length=.001.
"""
from pathlib import Path
import json,struct,hashlib,os,math
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
def read_stl(p):
 data=p.read_bytes();verts=[];faces=[];look={}
 for i in range(struct.unpack_from('<I',data,80)[0]):
  v=struct.unpack_from('<12fH',data,84+50*i)[3:12];ids=[]
  for j in range(3):
   xyz=tuple(v[j*3:j*3+3])
   if xyz not in look:look[xyz]=len(verts);verts.append(xyz)
   ids.append(look[xyz])
  faces.append(ids)
 return verts,faces
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def material(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=c;m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c
 m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72
 return m
def main():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.preferences.filepaths.save_version=0
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
 scene['scope']='NPU Marine north4F/south3F group with 2F open-under bridge and single-low conference hall; candidate, print/fit untested'
 scene['source_date']='Photographs undated; 2018 campus diagram historical; no 2026 as-built claim'
 scene['manufacturing']='8 STL types / 10 physical pieces, glue joints. Material previews do not validate four-nozzle printing.'
 d=json.loads((ROOT/'assembly.json').read_text('utf-8'));names=list(d['colors']);mats=[material(n,d['colors'][n]) for n in names]
 objects=[];checks=[]
 for p in d['parts']:
  vs,fs=read_stl(ROOT/p['stl']);T=Matrix(p['assembly_transform']);vworld=[tuple(T@Vector(v)) for v in vs]
  mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata(vworld,[],fs);mesh.update()
  ob=bpy.data.objects.new(p['id'],mesh);scene.collection.objects.link(ob);objects.append(ob)
  ob['stl_sha256']=p['sha256'];ob['prototype_stl']=p['stl'];ob['print_orientation']='as stored STL, minXYZ0';ob['fit_status']='not physically tested'
  for mat in mats:mesh.materials.append(mat)
  regs=[r for r in d['color_regions'] if r['part']==p['id']]
  for face in mesh.polygons:
   for r in regs:
    a,b=r['bounds_mm'];v=face.center
    if all(a[j]-1e-4<=v[j]<=b[j]+1e-4 for j in range(3)):face.material_index=names.index(r['color'])
  bpy.context.view_layer.update();dims=list(ob.dimensions)
  checks.append({'id':p['id'],'stl_sha256':p['sha256'],'physical_mm':[v*.001*1000 for v in dims],'stl_extent_mm':p['bounds_print_mm'],'max_error_mm':max(abs(dims[j]-p['bounds_print_mm'][j]) for j in range(3))})
 world=bpy.data.worlds.new('Soft neutral background');scene.world=world;world.use_nodes=True
 world.node_tree.nodes['Background'].inputs[0].default_value=(.74,.79,.84,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
 for loc,power,size in [((10,-100,250),1500000,180),((210,200,200),1200000,180),((-150,120,100),900000,150)]:
  light=bpy.data.lights.new('Softbox','AREA');light.energy=power;light.shape='DISK';light.size=size
  ob=bpy.data.objects.new('Softbox',light);scene.collection.objects.link(ob);ob.location=loc;aim(ob,(50,75,10))
 data=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.clip_end=3000
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20
 scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
 target=(60,76,13)
 views={'front':((245,290,190),target,260),'rear':((-190,-200,180),target,265),'courtyard':((25,250,130),(55,65,15),250),'end-hall':((-200,140,120),(45,70,14),260),'top':((59,79,420),(59,79,0),236),'elevation':((60,360,24),(60,75,22),255),'exploded':((245,290,240),(60,76,35),280),'bridge-detail':((155,145,90),(96,73,10),88)}
 manifests=[]
 for name,(loc,t,scale) in views.items():
  for ob in objects:
   ob.location.z=({'02-north-upper':20,'04-hall-roof':12,'05-bridge-tray':8,'06-bridge-lid':22}.get(ob.name,0) if name=='exploded' else 0)
  cam.location=loc;aim(cam,t);data.ortho_scale=scale
  scene.render.filepath=str(ROOT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
  manifests.append({'file':name+'.png','geometry':'exact STL instance transforms; exploded changes only vertical separation' if name=='exploded' else 'exact STL instance transforms','sha256_before_metadata_strip':hashlib.sha256((ROOT/'previews'/f'{name}.png').read_bytes()).hexdigest()})
 for ob in objects:ob.location.z=0
 cam.location=views['front'][0];aim(cam,target);data.ortho_scale=260
 scene.render.filepath='//previews/front.png'
 for screen in bpy.data.screens:
  for area in screen.areas:
   for space in area.spaces:
    if space.type=='FILE_BROWSER' and space.params:
     space.params.directory=b'//'
 os.chdir(ROOT);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene.blend'),compress=False)
 (ROOT/'qa/scene-unit-report.json').write_text(json.dumps({'unit_system':'METRIC','scale_length':.001,'length_unit':'MILLIMETERS','parts':checks,'pass':all(x['max_error_mm']<1e-4 for x in checks),'physical_print_or_fit_tested':False},indent=2)+'\n','utf-8')
 (ROOT/'previews/render-manifest.json').write_text(json.dumps(manifests,indent=2)+'\n','utf-8')
 print('Scene and 8 exact-mesh renders saved.')
if __name__=='__main__':main()
