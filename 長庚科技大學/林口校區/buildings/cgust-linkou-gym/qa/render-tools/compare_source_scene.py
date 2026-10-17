"""Recreate only the frozen render source's scene-building prefix; compare state.
The original scene construction statements are executed without edits. Only the
trailing image-render/manifest loop is excluded, with exact source range recorded.
Run in an independent reproduction tree (source/ and models/<version>/ siblings).
"""
import argparse,ast,hashlib,json,math,sys
from pathlib import Path
import bpy

def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scalar(v):
 if hasattr(v,'to_dict'):return scalar(v.to_dict())
 if hasattr(v,'to_list'):return scalar(v.to_list())
 if isinstance(v,dict):return {str(k):scalar(x) for k,x in v.items()}
 if isinstance(v,set):return sorted(scalar(x) for x in v)
 if v is None or isinstance(v,(str,bool,int,float)):return v
 try:return [scalar(x) for x in v]
 except TypeError:return {'rna_type':type(v).__name__,'name':getattr(v,'name',None)}
def rna(v,exclude=()):
 out={'rna_type':v.bl_rna.identifier}
 for p in v.bl_rna.properties:
  if p.is_readonly or p.identifier in {'rna_type',*exclude} or p.type in {'POINTER','COLLECTION'}:continue
  try:out[p.identifier]=scalar(getattr(v,p.identifier))
  except Exception as e:raise RuntimeError('Cannot serialize RNA '+p.identifier) from e
 return out
def nested_node_state(node):
 # Bounded state set used by this scene: Noise TexMapping and ColorMapping,
 # including the latter's built-in ramp even while use_color_ramp is false.
 out={}
 if hasattr(node,'texture_mapping'):out['texture_mapping']=rna(node.texture_mapping)
 if hasattr(node,'color_mapping'):
  mapping=node.color_mapping;ramp=mapping.color_ramp
  out['color_mapping']={'rna':rna(mapping),'color_ramp':{'rna':rna(ramp),'elements':[rna(e) for e in ramp.elements]}}
 return out
def nodes(tree):
 return {'rna':rna(tree),'nodes':{n.name:{'rna':rna(n),'nested_mapping_state':nested_node_state(n),'inputs':[{'name':s.name,'identifier':s.identifier,'default':scalar(s.default_value) if hasattr(s,'default_value') else None} for s in n.inputs],'outputs':[{'name':s.name,'identifier':s.identifier,'default':scalar(s.default_value) if hasattr(s,'default_value') else None} for s in n.outputs]} for n in sorted(tree.nodes,key=lambda x:x.name)},'links':sorted((x.from_node.name,list(x.from_node.outputs).index(x.from_socket),x.to_node.name,list(x.to_node.inputs).index(x.to_socket)) for x in tree.links)}
def layer_collection(c):
 return {'name':c.name,'exclude':c.exclude,'holdout':c.holdout,'indirect_only':c.indirect_only,'hide_viewport':c.hide_viewport,'collection':c.collection.name,'objects':sorted(o.name for o in c.collection.objects),'children':[layer_collection(x) for x in sorted(c.children,key=lambda x:x.name)]}
def snapshot():
 s=bpy.context.scene;objects={}
 require(not s.use_nodes and (s.sequence_editor is None or len(s.sequence_editor.sequences_all)==0),'Compositor/sequencer unsupported by the authored scene')
 require(all(layer.material_override is None for layer in s.view_layers),'Unexpected view-layer material override')
 require(not any(n.type=='GROUP' for collection in [bpy.data.materials,bpy.data.worlds] for x in collection if x.use_nodes for n in x.node_tree.nodes),'Shader node groups require recursive review')
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  row={'type':o.type,'matrix_world':[list(x) for x in o.matrix_world],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'parent':o.parent.name if o.parent else None,'properties':scalar(dict(o.items())),'visibility':{k:getattr(o,k) for k in ['visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','visible_shadow','is_holdout','is_shadow_catcher']},'constraints':[rna(c) for c in o.constraints]}
  if o.type=='MESH':
   mesh={'vertices':[list(v.co) for v in o.data.vertices],'faces':[[*p.vertices] for p in o.data.polygons],'materials':[m.name if m else None for m in o.data.materials],'polygon_material_indices':[p.material_index for p in o.data.polygons],'smooth':[p.use_smooth for p in o.data.polygons]}
   row['mesh_sha256']=hashlib.sha256(json.dumps(mesh,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest();row['vertex_count']=len(o.data.vertices);row['face_count']=len(o.data.polygons);row['modifiers']=[rna(m) for m in o.modifiers]
  elif o.type in ['CAMERA','LIGHT']:
   row['data']=rna(o.data)
   if o.type=='LIGHT':row['light_nodes']=nodes(o.data.node_tree) if o.data.use_nodes else None
   if o.type=='CAMERA':row['dof']={'settings':rna(o.data.dof),'focus_object':o.data.dof.focus_object.name if o.data.dof.focus_object else None}
  else:raise RuntimeError('Unexpected scene object '+o.type)
  objects[o.name]=row
 return {'objects':objects,'materials':{m.name:{'rna':rna(m),'nodes':nodes(m.node_tree) if m.use_nodes else None} for m in sorted(bpy.data.materials,key=lambda x:x.name)},'world':{'name':s.world.name,'rna':rna(s.world),'nodes':nodes(s.world.node_tree)},'scene_properties':scalar(dict(s.items())),'camera':s.camera.name if s.camera else None,'scene_scalar_state':rna(s),'render':rna(s.render),'display_settings':rna(s.display_settings),'sequencer_colorspace_settings':rna(s.sequencer_colorspace_settings),'image_settings':rna(s.render.image_settings),'cycles':rna(s.cycles),'view_settings':rna(s.view_settings),'unit_settings':rna(s.unit_settings),'frame_current':s.frame_current,'view_layers':{x.name:{'rna':rna(x),'layer_collection':layer_collection(x.layer_collection)} for x in s.view_layers},'collections':{x.name:{'hide_render':x.hide_render,'hide_viewport':x.hide_viewport,'objects':sorted(o.name for o in x.objects),'children':sorted(c.name for c in x.children)} for x in bpy.data.collections}}
def differences(a,b,path=''):
 if type(a)!=type(b):return [path+': type differs']
 if isinstance(a,dict):
  out=[path+'/'+str(k)+': key differs' for k in sorted(set(a)^set(b))]
  for k in sorted(set(a)&set(b)):out+=differences(a[k],b[k],path+'/'+str(k))
  return out
 if isinstance(a,(list,tuple)):
  if len(a)!=len(b):return [path+': length differs']
  out=[]
  for i,(x,y) in enumerate(zip(a,b)):out+=differences(x,y,path+'/'+str(i))
  return out
 return [] if a==b else [path+': value differs']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--version',required=True);ap.add_argument('--original-blend',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--expected-stl-sha256',required=True);ap.add_argument('--out',type=Path,required=True)
 args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);require(not args.out.exists(),'Refusing existing output');args.out.mkdir(parents=True)
 report={'passed':False,'source_sha256':sha(args.source),'original_blend_sha256':sha(args.original_blend),'manifest_sha256':sha(args.manifest),'checker_sha256':sha(__file__),'scope':'Exact equality of the scene state set used by this case: serialized scalar RNA, mesh/material assignments, sockets/links, Noise texture/color mappings and their built-in ramp, camera/render/visibility and collections. This is not a claim to serialize arbitrary Blender RNA. Original source construction prefix executed; no source PNGs rendered.'}
 try:
  tree=ast.parse(args.source.read_text(),filename=str(args.source));cuts=[i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='chosen' for t in n.targets)]
  require(len(cuts)==1,'Expected one explicit image-render-loop boundary');cut=cuts[0];prefix=tree.body[:cut];tail=tree.body[cut:]
  require(len(tail)==4 and isinstance(tail[0],ast.Assign) and isinstance(tail[1],ast.Assign) and isinstance(tail[2],ast.For) and isinstance(tail[3],ast.Expr),'Unexpected render-source tail; review required')
  q=lambda n:ast.unparse(n.func) if isinstance(n,ast.Call) else ''
  require(not any(q(n)=='bpy.ops.render.render' for p in prefix for n in ast.walk(p)),'Prefix contains image rendering')
  require(any(q(n)=='bpy.ops.wm.save_as_mainfile' for p in prefix for n in ast.walk(p)),'Prefix does not save source scene')
  require(any(q(n)=='bpy.ops.render.render' for n in ast.walk(tail[2])),'Tail lacks expected rendering loop')
  root=args.source.resolve().parent.parent;generated=root/'models'/args.version/'scene.blend';require(not generated.exists(),'Refusing to replace an existing generated Blend')
  require(sha(root/'models'/args.version/'model.stl')==args.expected_stl_sha256,'Reproduction STL not frozen original')
  report.update(executed_source_lines=[1,tail[0].lineno-1],excluded_source_lines=[tail[0].lineno,len(args.source.read_text().splitlines())],excluded_source_ast_types=[type(x).__name__ for x in tail],source_prefix_ast_sha256=hashlib.sha256(ast.dump(ast.Module(body=prefix,type_ignores=[]),include_attributes=True).encode()).hexdigest())
  oldargv=sys.argv;sys.argv=['blender','--',args.version];namespace={'__name__':'__main__','__file__':str(args.source.resolve())}
  try:exec(compile(ast.Module(body=prefix,type_ignores=[]),str(args.source),'exec'),namespace)
  finally:sys.argv=oldargv
  require(generated.is_file(),'Source scene was not saved');constructed=snapshot();report['generated_blend_sha256']=sha(generated)
  bpy.ops.wm.open_mainfile(filepath=str(generated.resolve()));built=snapshot()
  report['source_construction_to_saved_reload_differences']=differences(constructed,built)
  report['state_comparison_policy']='Both original and source-built saved Blend files are opened with the same Blender version before full-state serialization. No state fields are ignored due to differences.'
  (args.out/'source-constructed-memory-state.json').write_text(json.dumps(constructed,sort_keys=True,indent=2,allow_nan=False)+'\n')
  manifest=json.loads(args.manifest.read_text());require(manifest['stl_sha256']==args.expected_stl_sha256,'Manifest STL hash differs')
  sourceviews=namespace.get('views',{});camera_checks={name:scalar(sourceviews.get(name))==row['camera'] for name,row in manifest['views'].items()}
  camera_policy={name:('PERSP',20) if name in {'courtyard-gallery','courtyard-arcade'} else ('ORTHO',50) for name in sourceviews}
  source_specs=namespace.get('camera_specs',{});require(set(source_specs)==set(sourceviews),'Source camera spec set differs')
  require(all(source_specs[name]=={'projection':expected[0],'lens_mm':expected[1]} and manifest['views'][name].get('projection')==expected[0] and manifest['views'][name].get('lens_mm')==expected[1] for name,expected in camera_policy.items()),'Source/manifest per-view camera policy differs')
  require(set(camera_checks)=={'front','rear','west','east','south','north','top','courtyard-gallery','courtyard-arcade'} and set(sourceviews)==set(camera_checks),'Expected exactly nine original source and manifest views');report['all_nine_camera_definitions_match']=all(camera_checks.values());report['camera_definition_checks']=camera_checks
  bpy.ops.wm.open_mainfile(filepath=str(args.original_blend.resolve()));original=snapshot();diff=differences(original,built)
  for name,value in [('original-scene-state.json',original),('source-scene-state.json',built)]:
   (args.out/name).write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')
  report['state_difference_count']=len(diff);report['state_differences']=diff;report['exact_scene_state_matches']=not diff
  report['source_unchanged']=sha(args.source)==report['source_sha256'];report['original_blend_unchanged']=sha(args.original_blend)==report['original_blend_sha256'];report['manifest_unchanged']=sha(args.manifest)==report['manifest_sha256']
  report['passed']=all(report[k] for k in ['all_nine_camera_definitions_match','exact_scene_state_matches','source_unchanged','original_blend_unchanged','manifest_unchanged'])
 except Exception as e:report.update(passed=False,error_type=type(e).__name__,error=str(e))
 (args.out/'source-scene-audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':report['passed'],'error':report.get('error'),'differences':report.get('state_difference_count')}))
 if not report['passed']:raise RuntimeError('Source scene reproduction audit failed')
if __name__=='__main__':main()
