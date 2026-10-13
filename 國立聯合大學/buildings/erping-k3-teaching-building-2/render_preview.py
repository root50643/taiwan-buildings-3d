"""Blender preview uses model.stl unchanged. Run blender -b -t 4 -P render_preview.py"""
import bpy, os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));os.makedirs(OUT+'/previews',exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=OUT+'/model.stl');model=bpy.context.object;model.name='Printable landmark - actual STL'
mat=bpy.data.materials.new('Single-material ivory');mat.diffuse_color=(.72,.73,.72,1);mat.use_nodes=True
nd=mat.node_tree.nodes.get('Principled BSDF');nd.inputs['Base Color'].default_value=(.72,.73,.72,1);nd.inputs['Roughness'].default_value=.74;model.data.materials.append(mat)
# Everything below is presentation only; not part of printable geometry.
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.15));floor=bpy.context.object;floor.name='Studio floor (non-printing)'
mat=bpy.data.materials.new('Studio background');mat.diffuse_color=(.055,.077,.098,1);floor.data.materials.append(mat)
scene=bpy.context.scene;scene.world.color=(.18,.18,.18)
center=sum((model.matrix_world@Vector(c) for c in model.bound_box),Vector())/8
size=max(model.dimensions);aim=Vector((center.x,center.y,model.dimensions.z*.4))
def light(name,loc,power,sz):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=sz;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-125,-175,210),650000,110);light('Fill',(160,-40,125),190000,120);light('Rim',(20,150,180),540000,100)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam;cam.data.ortho_scale=size*1.55
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.5
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.4;scene.display.shading.curvature_valley_factor=1.3
scene.display.shading.cavity_ridge_factor=1.5;scene.display.shading.cavity_valley_factor=1.5
scene.display.shading.background_type='WORLD';scene.world.color=(.045,.06,.075)
scene.render.resolution_x=1200;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'

scene.render.use_stamp=False;scene.render.use_stamp_note=True;scene.render.stamp_font_size=16;scene.render.use_stamp_labels=False
for flag in ['date','time','render_time','frame','frame_range','memory','hostname','camera','lens','scene','marker','filename','sequencer_strip']:
 if hasattr(scene.render,'use_stamp_'+flag):setattr(scene.render,'use_stamp_'+flag,False)
scene.render.stamp_foreground=(.95,.96,.97,1);scene.render.stamp_background=(.02,.03,.04,.85)
for name,loc in [('front',(-155,-225,155)),('rear',(155,225,160)),('elevation',(0,-270,60))]:
 scene.render.stamp_note_text='NUU K3 Teaching Building 2 | Photo-interpreted | '+name.upper()+' | Actual STL'
 cam.location=loc;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=OUT+'/previews/'+name+'.png';bpy.ops.render.render(write_still=True)
# Embed rebuild code for inspection/editing while retaining the imported final mesh.
bpy.data.texts.load(OUT+'/build_model.py').filepath='';bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
scene.render.filepath='//previews/front.png';bpy.ops.wm.save_as_mainfile(filepath=OUT+'/scene.blend')
