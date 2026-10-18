from pathlib import Path
import json, hashlib, math
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(HERE/'model.stl'))
obj=bpy.context.object;obj.name='Original fused maritime museum candidate'
mesh=obj.data
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.74
    obj.data.materials.append(m)
mat('Original white massing',(0.78,0.81,0.80))
mat('Original muted green upper roof',(0.03,0.38,0.26))
mat('Original blue glazing indication - solid printable surface',(0.24,0.43,0.48))
mat('Original dark cap',(0.10,0.14,0.18))
for f in mesh.polygons:
    c=f.center; x,y,z=c
    if 79.7<z<81.5 and abs(x)<35.1 and 23.9<y<66.1:f.material_index=1
    elif z>99.15 and -17.1<x<1.1 and 44.9<y<60.1:f.material_index=3
    elif abs(x)<24.1 and -17.1<y<18.1 and 44.1<z<66.1:f.material_index=2
    elif (50.6<abs(x)<51.0 and 12.9<z<38) or (-34<x<34 and 25.6<y<25.9 and 68<z<76):f.material_index=2
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=0.001
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('neutral studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.82,0.86,0.90,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.6
scene.view_settings.view_transform='AgX'
for name,loc,power,size in [('key',(-130,-180,290),450000,180),('fill',(190,-30,170),260000,160),('rim',(0,210,220),350000,140)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,40))-o.location).to_track_quat('-Z','Y').to_euler()
camera_data=bpy.data.cameras.new('Review camera');camera=bpy.data.objects.new('Review camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
camera_data.type='ORTHO';camera_data.lens=48
views={
 'front':((210,-260,190),(-8,0,54),224),
 'rear':((-210,250,175),(-8,0,54),224),
 'deck-end':((0,-300,74),(-8,0,60),214),
 'back-end':((0,300,74),(-8,0,60),214),
 'left':((-300,0,75),(-8,0,60),214),
 'right':((300,0,75),(-8,0,60),214),
 'top':((0,0,350),(-8,0,0),218),
 'roof-detail':((170,-175,200),(0,20,80),147),
 'bridge-detail':((-190,-90,78),(-60,-3,22),102),
 'underside':((-210,-200,-150),(-8,0,46),224)
}
(HERE/'previews').mkdir(exist_ok=True)
record=[]
for name,(loc,target,scale) in views.items():
    camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=scale
    scene.render.filepath=str(HERE/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
    record.append({'file':f'previews/{name}.png','sha256':hashlib.sha256((HERE/'previews'/f'{name}.png').read_bytes()).hexdigest(),'camera':loc,'target':target,'ortho_scale':scale})
camera.location=views['front'][0];camera.rotation_euler=(Vector(views['front'][1])-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=224
obj['stl_sha256']=hashlib.sha256((HERE/'model.stl').read_bytes()).hexdigest();obj['source_images_in_scene']=False
scene.render.filepath='//previews/front.png'
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'scene.blend'),compress=False)
(HERE/'previews/render-manifest.json').write_text(json.dumps({'stl_sha256':obj['stl_sha256'],'renderer':bpy.app.version_string,'views':record,'scene_has_one_model_mesh':True,'textures':[]},indent=2)+'\n')
