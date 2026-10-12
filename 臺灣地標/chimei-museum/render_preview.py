"""Copy alongside model.stl, then run: blender -b -t 6 -P render_preview.py.
Renders the actual printable mesh; no decorative non-printing facade geometry.
"""
import bpy,os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));PREV=os.path.join(OUT,'previews');os.makedirs(PREV,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=os.path.join(OUT,'model.stl'));model=bpy.context.object;model.name='Printable building'
mat=bpy.data.materials.new('Warm limestone');mat.use_nodes=True
node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.62,.72,.66,1);node.inputs['Roughness'].default_value=.76;model.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.2));floor=bpy.context.object;floor.name='Studio floor (not part of model)'
m=bpy.data.materials.new('Slate');m.diffuse_color=(.075,.09,.105,1);floor.data.materials.append(m)
scene=bpy.context.scene;scene.world.color=(.16,.16,.16)
center=sum((model.matrix_world@Vector(c) for c in model.bound_box),Vector())/8
longest=max(model.dimensions);aim=Vector((center.x,center.y,model.dimensions.z*.49))
def light(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power*.5;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-100,-150,210),650000,140);light('Fill',(160,-50,120),230000,100);light('Rim',(20,140,180),600000,110)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=longest*1.55
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.45
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.3
scene.display.shading.cavity_ridge_factor=1.0;scene.display.shading.cavity_valley_factor=1.15
scene.display.shading.background_type='WORLD';scene.display.render_aa='32'
mat.diffuse_color=(.62,.72,.66,1)
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.use_stamp=False
scene.view_settings.view_transform='AgX';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
for name,loc in [('front',(172,-280,195)),('rear',(-170,280,190)),('elevation',(0,-350,60))]:
 cam.location=loc;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=os.path.join(PREV,name+'.png');bpy.ops.render.render(write_still=True)
cam.location=(172,-280,195);cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath='//previews/front.png';bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'scene.blend'))
