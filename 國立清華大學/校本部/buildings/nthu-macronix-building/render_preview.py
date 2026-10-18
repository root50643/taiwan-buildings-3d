"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os,hashlib
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews'; PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='Printable_NTHU'
mat=bpy.data.materials.new('Warm stone preview only');mat.diffuse_color=(.69,.64,.54,1)
mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.69,.64,.54,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72
model.data.materials.append(mat)
for name,color in [('Roof display only',(.18,.21,.24,1)),('Inset upper storey display only',(.28,.32,.34,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color
 m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72
 model.data.materials.append(m)
for face in model.data.polygons:
 c=face.center
 if -53<c.x<9 and -45<c.y<-4 and c.z>39 and face.normal.z>.3:face.material_index=1
 elif -51<c.x<7 and -43<c.y<-7 and c.z>32.8 and abs(face.normal.z)<.1:face.material_index=2
target_z=(min(v.co.z for v in model.data.vertices)+max(v.co.z for v in model.data.vertices))/2
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32
scene.cycles.use_denoising=False;scene.cycles.seed=0
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.60,.66,.75,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for loc,power,size in [((-110,-140,240),30000,150),((120,80,180),16000,150)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object
 light.data.energy=power;light.data.shape='DISK';light.data.size=size
 light.rotation_euler=(Vector((0,0,25))-light.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=180
views=[('front',(-195,-220,155),(0,0,target_z)),('rear',(195,230,160),(0,0,target_z)),('elevation',(0,-260,39),(0,0,target_z)),('roof',(-100,-180,250),(-10,-5,30))]
records=[]
for name,loc,aim in views:
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
 records.append({'file':'previews/'+name+'.png','camera':loc,'aim':aim,'ortho_scale':cam.data.ortho_scale,'sha256':hashlib.sha256((PREV/(name+'.png')).read_bytes()).hexdigest()})
cam.location=(-195,-220,155);cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png'
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='NTHU public exterior photos; unobserved elevations deliberately simplified';model['model_category']='Single connected printable solid'
model['stl_sha256']=hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest()
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.context.preferences.filepaths.save_version=0
bpy.context.preferences.filepaths.file_preview_type='NONE'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
(OUT/'qa'/'render-manifest.json').write_text(json.dumps({'stl_sha256':model['stl_sha256'],'blender':bpy.app.version_string,'engine':'CYCLES CPU','samples':32,'seed':0,'denoising':False,'views':records},indent=2),encoding='utf-8')

