# blender --background nhu-chengjun-hall.blend --python verify_blend.py
import bpy, pathlib,json,numpy as np
root=pathlib.Path(bpy.data.filepath).parent
D=np.load(root/'mesh-data.npz');scene=bpy.context.scene
obj=bpy.data.objects['Chengjun Hall — unified printable material mesh']
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
