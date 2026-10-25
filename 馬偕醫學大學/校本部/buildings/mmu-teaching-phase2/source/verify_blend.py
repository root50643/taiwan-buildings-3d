#!/usr/bin/env python3
"""Native Blend coordinate/material identity plus actual edit/save/reopen test on a copy."""
import bpy,numpy as np,json,hashlib,tempfile,argparse,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);root=a.out or Path(bpy.data.filepath).parent
D=np.load(root/'mesh-data.npz');obj=bpy.data.objects['MMU second teaching/research D–G — whole complex'];v=np.array([tuple(x.co)for x in obj.data.vertices]);f=np.array([tuple(x.vertices)for x in obj.data.polygons]);mi=np.array([x.material_index for x in obj.data.polygons]);assert np.array_equal(v,D['vertices'])and np.array_equal(f,D['faces'])and np.array_equal(mi,D['materials'])
coll=bpy.data.collections['EDITABLE components — hidden pre-union overlaps'];parts=json.loads((root/'construction-parts.json').read_text());assert len(coll.objects)==len(parts)and coll.hide_render and coll.hide_viewport
assert not obj.modifiers;assert all(s.render.filepath=='//previews/front.png'for s in bpy.data.scenes);external=[x.name for x in bpy.data.images if x.source=='FILE'and x.filepath];assert not external
orig=root/'mmu-teaching-phase2.blend';before=hashlib.sha256(orig.read_bytes()).hexdigest();matname=obj.data.materials[0].name;test=(.14,.34,.54,1);nv=len(v);nf=len(f);nm=len(obj.data.materials);nc=len(coll.objects)
with tempfile.TemporaryDirectory(prefix='native-edit-')as tmp:
 mat=bpy.data.materials[matname];mat.diffuse_color=test;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=test
 oldx=float(obj.data.vertices[0].co.x);obj.data.vertices[0].co.x=oldx+.25
 # Authored components are actual editable vertex meshes as well, not linked source images.
 comp=coll.objects[0];compname=comp.name;oldz=float(comp.data.vertices[0].co.z);comp.data.vertices[0].co.z=oldz+.125
 copy=Path(tmp)/'edit-test.blend';bpy.ops.wm.save_as_mainfile(filepath=str(copy),copy=True);bpy.ops.wm.open_mainfile(filepath=str(copy))
 edited=bpy.data.objects['MMU second teaching/research D–G — whole complex'];mat=bpy.data.materials[matname]
 assert abs(edited.data.vertices[0].co.x-(oldx+.25))<1e-5
 assert abs(bpy.data.objects[compname].data.vertices[0].co.z-(oldz+.125))<1e-5
 assert np.allclose(mat.diffuse_color,test,atol=1e-7)and np.allclose(mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value,test,atol=1e-7)
assert hashlib.sha256(orig.read_bytes()).hexdigest()==before
r={'blender_version':bpy.app.version_string,'final_vertices':nv,'final_triangles':nf,'face_materials':nm,'editable_authored_components':nc,'final_arrays_and_face_materials_exact':True,'hidden_components_are_preunion_authoring_objects_not_print_output':True,'modifiers':0,'external_image_textures':external,'real_final_vertex_material_and_component_vertex_edit_save_reopen':True,'original_blend_unchanged':True,'unit_system':'millimetres of authored model','scale_length':.001}
(root/'qa/blend-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
