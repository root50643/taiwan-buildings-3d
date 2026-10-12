"""Render the exact final STL and save editable.blend. Requires Blender 4.x."""
import bpy, os, math
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));PREV=os.path.join(OUT,'previews');os.makedirs(PREV,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=os.path.join(OUT,'model.stl'));model=bpy.context.object;model.name='Print-ready exterior (mm)'
mat=bpy.data.materials.new('Warm limestone clay');mat.use_nodes=True
node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.62,.40,.26,1);node.inputs['Roughness'].default_value=.72;model.data.materials.append(mat)
# Studio scenery is deliberately in a separate non-printing collection.
studio=bpy.data.collections.new('STUDIO ONLY - do not export');bpy.context.scene.collection.children.link(studio)
def studio_object(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 studio.objects.link(o)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.25));floor=bpy.context.object;floor.name='Non-printing studio floor';studio_object(floor)
mat=bpy.data.materials.new('Studio bluegray');mat.diffuse_color=(.085,.10,.125,1);floor.data.materials.append(mat)
scene=bpy.context.scene;scene.world.color=(.20,.20,.20)
center=sum((model.matrix_world@Vector(c) for c in model.bound_box),Vector())/8;aim=Vector((center.x,center.y,model.dimensions.z*.35))
def light(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler();studio_object(o)
light('Key',(-110,-150,230),550000,140);light('Fill',(140,-35,140),240000,110);light('Rim',(10,150,200),700000,110)
bpy.ops.object.camera_add();cam=bpy.context.object;studio_object(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=184
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
for name,loc in [('front',(175,-230,170)),('rear',(-175,230,185)),('elevation',(0,-300,50))]:
 cam.location=loc;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=os.path.join(PREV,name+'.png');bpy.ops.render.render(write_still=True)
# Select only printable mesh on open. A single editable object matches exported STL.
bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
for ar in bpy.context.screen.areas:
 if ar.type=='VIEW_3D':
  ar.spaces.active.region_3d.view_distance=220;ar.spaces.active.region_3d.view_location=aim
scene.render.filepath='//previews/front.png';bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'editable.blend'))
