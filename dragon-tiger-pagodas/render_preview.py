"""Actual STL preview and editable Blender scene. Run blender -b -t 4 -P render_preview.py."""
import bpy,os,hashlib
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));PREV=os.path.join(OUT,'previews');os.makedirs(PREV,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=os.path.join(OUT,'model.stl'));model=bpy.context.object;model.name='Printable_STL_mm';model['stl_sha256']=hashlib.sha256(open(os.path.join(OUT,'model.stl'),'rb').read()).hexdigest();model['source_file']='model.stl'
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.68;m.diffuse_color=(*color,1);return m
model.data.materials.append(material('Warm ivory',(.70,.68,.59)));model.data.materials.append(material('Stone detailing',(.64,.66,.63)))
for p in model.data.polygons:
 if p.center.z<5.6:p.material_index=1
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.3));floor=bpy.context.object;floor.name='Studio floor, not printable';floor.data.materials.append(material('Studio slate',(.065,.078,.093)))
scene=bpy.context.scene;scene.world.color=(.18,.18,.18);aim=Vector((0,0,48))
def light(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-110,-180,240),800000,140);light('Fill',(140,-80,130),430000,140);light('Rim',(20,140,200),850000,120)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=192
scene.render.engine='BLENDER_WORKBENCH';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.render.resolution_x=1200;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.background_type='WORLD';scene.world.color=(.085,.10,.12)
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
for name,loc in [('front',(125,-300,190)),('rear',(-165,290,180)),('elevation',(0,-350,92))]:
 if os.environ.get('VIEW') and name!=os.environ['VIEW']:continue
 cam.location=loc;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=os.path.join(PREV,name+'.png');bpy.ops.render.render(write_still=True)
scene.render.filepath='//previews/front.png';bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'scene.blend'))
