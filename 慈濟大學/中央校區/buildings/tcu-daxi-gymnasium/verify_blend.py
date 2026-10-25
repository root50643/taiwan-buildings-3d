# blender --background tcu-daxi-gymnasium.blend --python verify_blend.py
import bpy, pathlib,json,numpy as np
root=pathlib.Path(bpy.data.filepath).parent
D=np.load(root/'mesh-data.npz');scene=bpy.context.scene
obj=bpy.data.objects['TCU Daxi Gymnasium — unified printable material mesh']
v=np.array([tuple(x.co)for x in obj.data.vertices]);f=np.array([tuple(x.vertices)for x in obj.data.polygons]);mi=np.array([x.material_index for x in obj.data.polygons])
assert np.array_equal(v,D['vertices']) and np.array_equal(f,D['faces']) and np.array_equal(mi,D['materials'])
assert all(x.render.filepath.startswith('//') for x in bpy.data.scenes)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:assert space.params.directory==b'//'
external_images=[x.name for x in bpy.data.images if x.source=='FILE' and x.filepath]
assert not external_images
parts=bpy.data.collections['EDITABLE authored components (hidden; overlaps pre-union)'];assert parts.hide_render and parts.hide_viewport
report={'blender_version':bpy.app.version_string,'final_vertices':len(v),'final_triangles':len(f),'final_materials':len(obj.data.materials),'editable_construction_objects':len(parts.objects),'construction_hidden':True,'final_mesh_matches_generated_arrays':True,'external_image_textures':external_images,'relative_output_and_browser_paths':True,'scale_length':scene.unit_settings.scale_length,'unit_system':scene.unit_settings.system}
(root/'qa'/'blend-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

# Render the actual reopened native scene and compare with its corresponding preview.
import tempfile,struct,hashlib
with tempfile.TemporaryDirectory(prefix='native-render-check-') as tmp:
 render=pathlib.Path(tmp)/'front.png';scene.render.filepath=str(render);bpy.ops.render.render(write_still=True)
 raw=render.read_bytes();clean=raw[:8];at=8
 while at<len(raw):
  n=struct.unpack('>I',raw[at:at+4])[0];tag=raw[at+4:at+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):clean+=raw[at:at+n+12]
  at+=n+12
 expected=(root/'previews/front.png').read_bytes();assert clean==expected
 report={'actual_saved_blend_reopened_and_rendered':True,'reference_preview':'previews/front.png','png_bytes_identical_after_metadata_normalization':True,'sha256':hashlib.sha256(clean).hexdigest(),'deliverable_modified':False}
 (root/'qa/saved-scene-render-validation.json').write_text(json.dumps(report,indent=2)+'\n')
scene.render.filepath='//previews/front.png'

# Exercise editable native geometry AND material persistence, without altering the deliverable.
import tempfile,os
final_name=obj.name
vertex_before=tuple(obj.data.vertices[0].co);obj.data.vertices[0].co.x+=0.125
vertex_after=tuple(obj.data.vertices[0].co)
material_name=obj.data.materials[0].name
mat=obj.data.materials[0];color_before=tuple(mat.diffuse_color);color_after=(0.12,0.34,0.56,1.0)
mat.diffuse_color=color_after;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color_after
part=next(iter(parts.objects));part_name=part.name;part_before=tuple(part.data.vertices[0].co);part.data.vertices[0].co.z+=0.2;part_after=tuple(part.data.vertices[0].co)
with tempfile.TemporaryDirectory(prefix='daxi-native-edit-') as tmp:
 test=pathlib.Path(tmp)/'native-edit-probe.blend';bpy.ops.wm.save_as_mainfile(filepath=str(test));bpy.ops.wm.open_mainfile(filepath=str(test))
 reopened=bpy.data.objects[final_name];assert tuple(reopened.data.vertices[0].co)==vertex_after
 assert all(abs(x-y)<1e-6 for x,y in zip(bpy.data.materials[material_name].diffuse_color,color_after))
 assert all(abs(x-y)<1e-6 for x,y in zip(bpy.data.materials[material_name].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,color_after))
 assert tuple(bpy.data.objects[part_name].data.vertices[0].co)==part_after
 native={'native_vertex_changed_and_reopened':True,'native_material_diffuse_and_shader_changed_and_reopened':True,'construction_component_vertex_changed_and_reopened':True,'final_vertex_delta_mm':0.125,'construction_vertex_delta_mm':0.2,'deliverable_modified':False,'temporary_probe_removed':True}
(root/'qa/native-edit-validation.json').write_text(json.dumps(native,indent=2)+'\n');print(json.dumps(native,indent=2))
