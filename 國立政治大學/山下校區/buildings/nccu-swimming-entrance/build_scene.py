"""Blender 4.3+: editable material mesh plus optional evidence-free construction guides.
blender -b --factory-startup --python build_scene.py -- --input PACKAGE --output PACKAGE
No third-party images are loaded, packed or used as textures.
"""
import bpy,sys,json,argparse,math
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path(__file__).parent);ap.add_argument('--output',type=Path,default=Path(__file__).parent);ap.add_argument('--render',action='store_true');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=args.input;out=args.output;out.mkdir(parents=True,exist_ok=True);(out/'previews').mkdir(exist_ok=True)
d=json.loads((root/'mesh.json').read_text());p=json.loads((root/'parameters.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
mesh=bpy.data.meshes.new('Original_closed_print_mesh');mesh.from_pydata(d['vertices'],[],d['faces']);mesh.update();obj=bpy.data.objects.new('NCCU service-wing segment — NOT full swimming hall',mesh);scene.collection.objects.link(obj)
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for ent in d['palette']:
 rgb=[int(ent['hex'][i:i+2],16)/255 for i in [1,3,5]];mat=bpy.data.materials.new(ent['name']);mat.diffuse_color=(*rgb,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*[linear(c) for c in rgb],1);bs.inputs['Roughness'].default_value=.558;mesh.materials.append(mat)
for poly,idx in zip(mesh.polygons,d['material_indices']):poly.material_index=idx
obj['scope']=p['scope'];obj['title_zh']=p['title_zh'];obj['photo_capture_date']='unknown';obj['nominal_scale']=p['nominal_scale'];obj['axis_registration']=p['axes'];obj['source_pixels_embedded']=False;obj['warning']='NOT measured, NOT complete building, NOT verified 2026 appearance. Solid interior; accessible ramp omitted.'
# Parametric union/difference boxes are wire-only guides, excluded from render.
# The final single mesh remains editable directly and is the only export object.
guides=bpy.data.collections.new('Construction guides — non-printing, hidden');scene.collection.children.link(guides);guides.hide_render=True;guides.hide_viewport=True
for op in json.loads((root/'construction.json').read_text())['operations']:
 a,b=op['bounds_mm'];bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((x+y)/2 for x,y in zip(a,b)));g=bpy.context.object;g.name=op['operation']+': '+op['name'];g.dimensions=tuple(y-x for x,y in zip(a,b));g.display_type='WIRE';g.hide_render=True;g['construction_operation']=op['operation']
 for c in list(g.users_collection):c.objects.unlink(g)
 guides.objects.link(g)
# Render floor is not model geometry and never exported.
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.06));floor=bpy.context.object;floor.name='Presentation floor (not part of model)';fm=bpy.data.materials.new('studio_floor');fm.diffuse_color=(.81,.83,.84,1);fm.use_nodes=True;fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.72,.75,.77,1);fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;floor.data.materials.append(fm)
world=bpy.data.worlds.new('Neutral studio') if not bpy.data.worlds else bpy.data.worlds[0];scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.8,.85,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
for name,loc,energy,size in [('Key',(40,-90,160),25000,150),('Fill',(-100,-10,80),12000,130),('Rim',(30,100,100),18000,120)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=energy;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,8))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Presentation camera';cam.data.type='ORTHO';cam.data.clip_start=.1;cam.data.clip_end=5000;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.cycles.seed=41;scene.render.resolution_x=1600;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [i.name for i in []] else 'None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
views={
 'front':((0,-260,30),(0,-3,16),228),
 'front-right':((170,-220,120),(0,-2,14),213),
 'rear-cut':((-125,210,105),(0,-2,14),220),
 'top':((0,-3,280),(0,-3,0),230),
 'right-end':((270,-35,72),(0,-3,15),62),
}
# For end inspection use camera near the short end, maintaining its target.
views['right-end']=((270,-36,60),(85,-3,15),80)
for name,(pos,target,scale) in views.items():
 cam.location=pos;direction=Vector(target)-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 if name=='top':cam.rotation_euler=(0,0,0)
 scene.render.filepath=str(out/'previews'/f'{name}.png')
 if args.render:bpy.ops.render.render(write_still=True)
# Save hero view and final mesh active. Materials are actual editable slots.
pos,target,scale=views['front-right'];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=240;area.spaces.active.region_3d.view_location=(0,0,15);area.spaces.active.shading.color_type='MATERIAL'
scene['model_export_object']=obj.name;scene['presentation_helpers_not_exported']=True
# Store portable paths in the editable scene, not this machine's output root.
scene.render.filepath=' '*(scene.render.bl_rna.properties['filepath'].length_max-1)
scene.render.filepath='//previews/right-end.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:
    space.params.directory=b' '*(space.params.bl_rna.properties['directory'].length_max-1)
    space.params.directory=b'//'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
print('Saved editable mesh:',len(mesh.vertices),'vertices',len(mesh.polygons),'triangles',len(mesh.materials),'materials')
