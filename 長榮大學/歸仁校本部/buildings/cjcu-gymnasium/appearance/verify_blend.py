#!/usr/bin/env python3
"""Verify saved mesh, perform real native vertex/material edits, save and reopen a temporary copy."""
import bpy,numpy as np,json,hashlib,tempfile,argparse,sys,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);root=a.out or Path(bpy.data.filepath).parent
D=np.load(root/'mesh-data.npz');palette=json.loads((root/'palette.json').read_text());meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(meshes)==1 and len(bpy.data.meshes)==1
obj=meshes[0];v=np.array([tuple(q.co) for q in obj.data.vertices],dtype='<f4');f=np.array([tuple(q.vertices) for q in obj.data.polygons],dtype=np.int32);m=np.array([q.material_index for q in obj.data.polygons]);assert v.tobytes()==D['vertices'].tobytes() and f.tobytes()==D['faces'].tobytes() and np.array_equal(m,D['materials'])
assert np.array_equal([q.value for q in obj.data.attributes['original_stl_triangle_index'].data],np.arange(len(f)))
assert not obj.modifiers and not obj.hide_render and not obj.hide_viewport and np.array_equal(np.array(obj.matrix_world),np.eye(4))
assert len(obj.data.materials)==len(bpy.data.materials)==2
for mat,d in zip(obj.data.materials,palette):
 assert mat.name==d['id'] and np.allclose(mat.diffuse_color,d['blender_linear_rgba'],atol=5e-8)
 bsdf=mat.node_tree.nodes['Principled BSDF'];assert np.allclose(bsdf.inputs['Base Color'].default_value,d['blender_linear_rgba'],atol=5e-8)
 for k,value in [('Roughness',.65),('Metallic',0),('Emission Strength',0),('Transmission Weight',0)]:assert abs(bsdf.inputs[k].default_value-value)<5e-8
 assert len(mat.node_tree.nodes)==2 and not any(node.type=='TEX_IMAGE' for node in mat.node_tree.nodes)
assert not bpy.data.libraries and not bpy.data.texts and not bpy.data.images and not any(p.use_smooth for p in obj.data.polygons)
assert all(s.render.filepath=='//previews/front.png' for s in bpy.data.scenes)
assert bpy.context.scene.unit_settings.scale_length==np.float32(.001)
orig=root/'cjcu-gymnasium-roof-illustration.blend';before=hashlib.sha256(orig.read_bytes()).hexdigest();roof=int(np.flatnonzero(m==1)[0]);test=(.14,.34,.54,1);name=obj.name
with tempfile.TemporaryDirectory(prefix='native-edit-') as tmp:
 # First prove the delivered saved scene itself generates the front preview.
 render=Path(tmp)/'saved-front.png';bpy.context.scene.render.filepath=str(render);bpy.ops.render.render(write_still=True)
 b=render.read_bytes();out=b[:8];i=8
 while i<len(b):
  n=struct.unpack_from('>I',b,i)[0];tag=b[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=b[i:i+n+12]
  i+=n+12
 assert out==(root/'previews/front.png').read_bytes(),'Saved scene output differs from front preview'
 obj.data.vertices[0].co.x+=.125;obj.data.polygons[roof].material_index=0;mat=obj.data.materials[1];mat.diffuse_color=test;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=test;obj.data.update()
 copy=Path(tmp)/'native-edit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(copy),copy=True);bpy.ops.wm.open_mainfile(filepath=str(copy));edited=bpy.data.objects[name]
 assert tuple(edited.data.vertices[0].co)==(float(v[0,0]+np.float32(.125)),float(v[0,1]),float(v[0,2])) and edited.data.polygons[roof].material_index==0
 assert np.allclose(edited.data.materials[1].diffuse_color,test,atol=1e-7) and np.allclose(edited.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,test,atol=1e-7)
assert hashlib.sha256(orig.read_bytes()).hexdigest()==before
report={'blender_version':bpy.app.version_string,'mesh_objects_and_datablocks':1,'coordinates_face_order_winding_and_material_assignments_exact':True,'numeric_original_face_attribute_exact':True,'materials':2,'node_inputs_match_illustrative_palette':True,'image_textures_libraries_textblocks_modifiers':0,'hidden_geometry':0,'unit':'millimeters','saved_scene_front_PNG_bytes_equal':True,'real_vertex_edit_saved_and_reopened':True,'real_face_material_reassignment_saved_and_reopened':True,'real_material_base_color_edit_saved_and_reopened':True,'original_delivered_blend_unchanged_by_test':True}
(root/'qa'/'native-blend-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
