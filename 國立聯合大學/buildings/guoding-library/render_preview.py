import bpy,math,os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=OUT+'/guoding_library_150mm.stl')
o=bpy.context.object;o.name='Guoding Library | printable mesh'
mat=bpy.data.materials.new('Warm ivory resin');mat.diffuse_color=(.75,.72,.66,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.75,.72,.66,1);bs.inputs['Roughness'].default_value=.76;o.data.materials.append(mat)
# Geometry is the actual STL; no cosmetic window planes or fake details.
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.2));floor=bpy.context.object
m=bpy.data.materials.new('Slate backdrop');m.diffuse_color=(.075,.09,.105,1);floor.data.materials.append(m)
world=bpy.context.scene.world;world.color=(.16,.16,.16)
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,20))-l.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-100,-150,210),650000,140);area('Fill',(160,-50,120),230000,100);area('Rim',(20,140,180),600000,110)
bpy.ops.object.camera_add();camera=bpy.context.object;bpy.context.scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=184
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
for name,loc,target in [('front_perspective',(135,-230,133),(0,-2,25)),('front_elevation',(0,-260,82),(0,0,27)),('rear_perspective',(-150,210,160),(0,0,25))]:
 camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=OUT+'/'+name+'.png';bpy.ops.render.render(write_still=True)
scene.render.filepath='//rear_perspective.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/guoding_library.blend')
