"""Read actual reopened BLEND; verify exact oriented triangles/materials and editability."""
import bpy,sys,pathlib,json,hashlib,tempfile,struct
import numpy as np
root=pathlib.Path(bpy.data.filepath).parent;sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from material_geometry import load_stl,load_materials,bijection
file=pathlib.Path(bpy.data.filepath);before=hashlib.sha256(file.read_bytes()).hexdigest();scene=bpy.context.scene
objects=[x for x in scene.objects if x.type=='MESH'];assert len(objects)==1;o=objects[0];assert not o.modifiers and not o.hide_render
v=np.asarray([tuple(x.co)for x in o.data.vertices]);f=np.asarray([tuple(x.vertices)for x in o.data.polygons]);source=load_stl(root/'model.stl')[2];ids=bijection(source,v[f]);mi=load_materials(root);actual=np.asarray([x.material_index for x in o.data.polygons]);assert np.array_equal(actual,mi[ids]);assert np.array_equal(np.asarray([x.value for x in o.data.attributes['original_stl_triangle_index'].data]),ids)
assert np.array_equal(np.asarray(o.matrix_world),np.eye(4));assert scene.unit_settings.system=='METRIC' and abs(scene.unit_settings.scale_length-.001)<1e-9
palette=json.loads((root/'parameters.json').read_text())['palette'];assert len(o.data.materials)==len(palette)==3
for p,m in zip(palette,o.data.materials):
 h=p['hex'].lstrip('#');srgb=[int(h[i:i+2],16)/255 for i in(0,2,4)];c=[x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in srgb]+[1]
 assert m.name==p['id'] and np.allclose(m.diffuse_color,c,rtol=0,atol=1e-7);node=m.node_tree.nodes['Principled BSDF'];assert np.allclose(node.inputs['Base Color'].default_value,c,rtol=0,atol=1e-7);assert abs(node.inputs['Roughness'].default_value-p['roughness'])<1e-7;assert node.inputs['Metallic'].default_value==0
assert not bpy.data.libraries and not bpy.data.sounds and not bpy.data.movieclips and not bpy.data.texts
assert not any(x.packed_file or(x.source=='FILE'and x.filepath)for x in bpy.data.images)
assert all(not x.filepath or x.filepath=='<builtin>' for x in bpy.data.fonts)
assert all(x.render.filepath.startswith('//')for x in bpy.data.scenes)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER'and space.params:assert space.params.directory==b'//'
report={'all_pass':True,'blender_version':bpy.app.version_string,'visible_mesh_objects':1,'vertices':len(v),'triangles':len(f),'full_oriented_triangle_mapping_bijective':True,'all_triangle_coordinates_exact':True,'normals_independently_identical':True,'native_source_index_attribute_matches_bijection':True,'all_material_indices_match_original_face_mask':True,'material_counts':np.bincount(actual,minlength=3).tolist(),'diffuse_and_shader_palette_match_public_srgb':True,'modifiers':0,'model_transform_identity':True,'external_or_packed_images':0,'linked_libraries':0,'embedded_scripts':0,'relative_render_and_browser_paths':True,'deliverable_sha256':before}
(root/'qa/blend-validation.json').write_text(json.dumps(report,indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='pine-native-check-')as tmp:
 temp=pathlib.Path(tmp);scene.render.filepath=str(temp/'front.png');bpy.ops.render.render(write_still=True);b=(temp/'front.png').read_bytes();clean=b[:8];at=8
 while at<len(b):
  n=struct.unpack('>I',b[at:at+4])[0]
  if b[at+4:at+8]not in(b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):clean+=b[at:at+n+12]
  at+=n+12
 assert clean==(root/'previews/front.png').read_bytes()
 (root/'qa/saved-scene-render-validation.json').write_text(json.dumps({'all_pass':True,'reopened_actual_scene_rendered':True,'reference':'previews/front.png','png_bytes_identical_after_metadata_normalization':True,'sha256':hashlib.sha256(clean).hexdigest()},indent=2)+'\n')
 scene.render.filepath='//previews/front.png';name=o.name;matname=o.data.materials[1].name;first=o.data.vertices[0];first.co.x+=.125;expected=tuple(first.co);color=(.12,.34,.56,1);mat=bpy.data.materials[matname];mat.diffuse_color=color;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;o.data.polygons[0].material_index=1
 probe=temp/'editability.blend';bpy.ops.wm.save_as_mainfile(filepath=str(probe));bpy.ops.wm.open_mainfile(filepath=str(probe));obj=bpy.data.objects[name];assert tuple(obj.data.vertices[0].co)==expected and obj.data.polygons[0].material_index==1
 assert np.allclose(bpy.data.materials[matname].diffuse_color,color,atol=1e-7,rtol=0);assert np.allclose(bpy.data.materials[matname].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,color,atol=1e-7,rtol=0)
assert hashlib.sha256(file.read_bytes()).hexdigest()==before
(root/'qa/native-edit-validation.json').write_text(json.dumps({'all_pass':True,'temporary_mesh_vertex_edit_saved_and_reopened':True,'temporary_per_face_material_edit_saved_and_reopened':True,'temporary_diffuse_and_shader_edit_saved_and_reopened':True,'temporary_probe_removed':True,'delivered_blend_modified':False,'before_and_after_sha256':before},indent=2)+'\n')
print(json.dumps(report,indent=2))
