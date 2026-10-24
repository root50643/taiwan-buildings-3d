"""blender -b scene.blend --python verify_blend.py -- --input PACKAGE --output QA
Opens the saved file in a fresh process, verifies topology and all material
slots, then writes a separate edited-material temporary file for reopen.
"""
import bpy,json,sys,argparse,tempfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path(__file__).parent);ap.add_argument('--output',type=Path);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else []);root=args.input;out=args.output or root/'qa';out.mkdir(parents=True,exist_ok=True)
d=json.loads((root/'mesh.json').read_text());scene=bpy.context.scene;obj=bpy.data.objects[scene['model_export_object']];me=obj.data;v=[list(x.co)for x in me.vertices];f=[list(x.vertices)for x in me.polygons];mi=[x.material_index for x in me.polygons]
max_delta=max(abs(a-b)for x,y in zip(v,d['vertices'])for a,b in zip(x,y));images=[im.name for im in bpy.data.images if im.source=='FILE' or im.packed_file]
qa={'blender_version':bpy.app.version_string,'vertices':len(v),'triangles':len(f),'max_coordinate_delta_mm':max_delta,'face_indices_exact':f==d['faces'],'material_indices_exact':mi==d['material_indices'],'material_names_exact':[m.name for m in me.materials]==[m['name']for m in d['palette']],'file_or_packed_images':images,'unit_scale_length':scene.unit_settings.scale_length,'guide_collection_hidden_render':bpy.data.collections['Construction guides — non-printing, hidden'].hide_render,'model_object_scale':list(obj.scale),'scope_property':obj['scope']}
assert max_delta<8e-6 and qa['face_indices_exact']and qa['material_indices_exact']and qa['material_names_exact']and not images
# Actually edit the displayed tan material, save to a temporary directory,
# reopen it, and verify both the edit and unchanged model data.
with tempfile.TemporaryDirectory() as td:
 name=obj.name;material=me.materials[1];old=material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[0];new=old+.017;material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[0]=new;path=str(Path(td)/'material-edit.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path);ob=bpy.data.objects[name];values=ob.data.materials[1].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
 qa['material_edit_save_reopen']={'color_edit_persisted':abs(values[0]-new)<1e-7,'vertices_exact':v==[list(x.co)for x in ob.data.vertices],'faces_exact':f==[list(x.vertices)for x in ob.data.polygons],'material_indices_exact':mi==[x.material_index for x in ob.data.polygons]};assert all(qa['material_edit_save_reopen'].values())
(out/'blend-readback-edit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False,indent=2))
