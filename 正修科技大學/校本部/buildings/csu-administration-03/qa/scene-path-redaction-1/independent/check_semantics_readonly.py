"""Independent read-only bpy signatures, fixed old/new SHA guards, no save/render."""
from pathlib import Path
import argparse,hashlib,json
import bpy

EXPECTED={
 'v1':('18736d0ee70384fba9a20f83d3632b9a237c0f1d01f1d4eaf28ec85bf837e750','fc0c4ac3a4106a8f7c28ec4b526d6cac33ec433297329c69e7dbccea76be99a3'),
 'v2':('b9b0cf0a1411b4c29a69656888610223d5952a6b0fbb8b91c58b30bf6908c056','d852f85363988a986e7ed225ebfeb39433e9e8fe6a1d8e48fb8d09f6fec0f01c')}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def require(value,message):
 if not value:raise RuntimeError(message)
def freeze(value):
 if value is None or isinstance(value,(bool,int,float,str)):return value
 if isinstance(value,bpy.types.ID):return {'ID_name':value.name_full,'ID_type':value.bl_rna.identifier}
 return [freeze(x) for x in value]
def primitive_rna(value):
 result={}
 for prop in value.bl_rna.properties:
  if prop.type not in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:continue
  if prop.identifier in {'name','name_full','session_uid','is_updated','is_updated_data','is_updated_transform','is_runtime_data','is_evaluated'}:continue
  result[prop.identifier]=freeze(getattr(value,prop.identifier))
 return result
def tree_signature(tree):
 if tree is None:return None
 nodes=[]
 for node in sorted(tree.nodes,key=lambda x:x.name):
  sockets=[]
  for socket in node.inputs:
   sockets.append({'identifier':socket.identifier,'name':socket.name,
    'default_value':freeze(socket.default_value) if hasattr(socket,'default_value') else None})
  nodes.append({'name':node.name,'type':node.bl_idname,'properties':primitive_rna(node),'inputs':sockets})
 links=sorted((x.from_node.name,x.from_socket.identifier,x.to_node.name,x.to_socket.identifier) for x in tree.links)
 return {'nodes':nodes,'links':links}
def signature(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
 objects=[];meshes=[];cameras=[];lights=[]
 for obj in sorted(scene.objects,key=lambda x:x.name):
  objects.append({'name':obj.name,'type':obj.type,'data_name':obj.data.name if obj.data else None,
   'parent':obj.parent.name if obj.parent else None,'matrix_world':freeze(obj.matrix_world),
   'properties':primitive_rna(obj),'print_part':obj.get('print_part'),
   'modifiers':[{'name':x.name,'type':x.type,'properties':primitive_rna(x)} for x in obj.modifiers],
   'action_name':obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None})
  if obj.type=='MESH':
   mesh=obj.data;data={'positions':[freeze(v.co) for v in mesh.vertices],
    'edges':[list(e.vertices) for e in mesh.edges],
    'polygons':[{'vertices':list(p.vertices),'material_index':p.material_index,'smooth':p.use_smooth} for p in mesh.polygons]}
   meshes.append({'object':obj.name,'mesh':mesh.name,'vertices':len(mesh.vertices),'edges':len(mesh.edges),
    'polygons':len(mesh.polygons),'exact_local_data_sha256':digest(data),'properties':primitive_rna(mesh),
    'materials':[m.name if m else None for m in mesh.materials]})
  elif obj.type=='CAMERA':
   cameras.append({'object':obj.name,'camera':obj.data.name,'properties':primitive_rna(obj.data),'dof':primitive_rna(obj.data.dof),'stereo':primitive_rna(obj.data.stereo)})
  elif obj.type=='LIGHT':
   lights.append({'object':obj.name,'light':obj.data.name,'properties':primitive_rna(obj.data),'nodes':tree_signature(obj.data.node_tree)})
 materials=[{'name':m.name,'properties':primitive_rna(m),'nodes':tree_signature(m.node_tree)} for m in sorted(bpy.data.materials,key=lambda x:x.name)]
 world=None if scene.world is None else {'name':scene.world.name,'properties':primitive_rna(scene.world),'nodes':tree_signature(scene.world.node_tree)}
 render={'scene_properties':primitive_rna(scene),'render_properties':primitive_rna(scene.render),
  'cycles_properties':primitive_rna(scene.cycles),'image_settings':primitive_rna(scene.render.image_settings),
  'view_settings':primitive_rna(scene.view_settings),'unit_settings':primitive_rna(scene.unit_settings),
  'selected_camera':scene.camera.name if scene.camera else None,'frame':scene.frame_current,
  'layers':[{'name':x.name,'properties':primitive_rna(x)} for x in scene.view_layers]}
 return {'objects':objects,'meshes':meshes,'cameras':cameras,'lights':lights,'materials':materials,'world':world,
  'render':render,'linked_libraries':len(bpy.data.libraries),'images':len(bpy.data.images),
  'external_dependencies':list(bpy.utils.blend_paths())}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old-root',type=Path,required=True);p.add_argument('--new-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 require(not a.output.exists(),'Fresh report required');rows=[]
 for version,(old_expected,new_expected) in EXPECTED.items():
  old=a.old_root/'models'/version/'scene.blend';new=a.new_root/'models'/version/'scene.blend'
  require(sha(old)==old_expected and sha(new)==new_expected and old_expected!=new_expected,'Fixed independent old/new SHA guard failed')
  source=signature(old);delivered=signature(new)
  groups={key:source[key]==delivered[key] for key in source}
  require(sha(old)==old_expected and sha(new)==new_expected,'Scene bytes changed during read-only load')
  rows.append({'version':version,'original_scene_sha256':old_expected,'delivered_scene_sha256':new_expected,
   'original_and_delivered_inputs_distinct':True,'groups_identical':groups,'all_groups_identical':all(groups.values()),
   'source_signature_sha256':digest(source),'delivered_signature_sha256':digest(delivered),
   'source_signature':source,'delivered_signature':delivered,'input_files_unchanged_after_load':True})
 control_path=a.old_root/'models/v2/scene.blend'
 first=signature(control_path)
 def uids():return {group+'/'+item.name:item.session_uid for group in ['objects','meshes','cameras','lights','materials','worlds','scenes'] for item in getattr(bpy.data,group)}
 first_uids=uids();second=signature(control_path);second_uids=uids()
 control={'same_input_scene_sha256':sha(control_path),'same_input_loaded_twice':True,
  'all_non_session_uid_signature_data_identical':first==second,
  'runtime_session_UIDs_changed':first_uids!=second_uids,
  'changed_runtime_UID_count':sum(first_uids[k]!=second_uids[k] for k in first_uids),
  'RNA_session_uid_description':bpy.types.ID.bl_rna.properties['session_uid'].description}
 report={'passed':all(x['all_groups_identical'] for x in rows) and control['all_non_session_uid_signature_data_identical'] and control['runtime_session_UIDs_changed'],'bpy_version':bpy.app.version_string,
  'checker_source_sha256':sha(__file__),'files':rows,'render_performed':False,'scene_saved':False,
  'same_file_runtime_ID_control':control,'excluded_runtime_identifier':'ID.session_uid only; every other declared signature field retained',
  'method':'Open two independently SHA-guarded old/new files with UI and script loading disabled. Compare object transforms/properties, exact mesh coordinate/topology data, cameras, lights, materials/world nodes and render settings. Does not use the author semantic comparison.',
  'limits':'The independent byte/SDNA audit separately proves every other decoded byte unchanged. This sampled API signature does not constitute a physical print or a new render.'}
 a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':report['passed'],'files':[{'version':x['version'],'all_groups_identical':x['all_groups_identical'],'groups':x['groups_identical']} for x in rows]}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
