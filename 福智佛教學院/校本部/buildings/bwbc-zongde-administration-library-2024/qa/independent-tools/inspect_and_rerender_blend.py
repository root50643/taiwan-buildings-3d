"""Inspect a frozen saved Blender scene, then rerender its declared eleven views.
Run with Blender --background --threads 1 --python this_file -- ARGS.
"""
import argparse,collections,hashlib,json,math,struct,sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from png_exact_compare import compare as compare_png, sanitize as sanitize_png

def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def directed(t):
 a=tuple(tuple(float(c) for c in p) for p in t)
 return min(a,a[1:]+a[:1],a[2:]+a[:2])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--stl',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',required=True);ap.add_argument('--inspect-only',action='store_true')
 args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(args.out);require(not out.exists(),'Output exists; refusing to overwrite');out.mkdir(parents=True)
 report={'passed':False,'strict_passed':False,'source_sha256':sha(__file__),'original_blend_sha256':sha(args.blend),'original_stl_sha256':sha(args.stl),'original_manifest_sha256':sha(args.manifest),'blender':bpy.app.version_string,'png_comparator_source_sha256':sha(Path(__file__).with_name('png_exact_compare.py')),'checks':{}}
 try:
  require(report['original_stl_sha256']==args.expected_sha256,'STL hash does not match freeze');raw=Path(args.stl).read_bytes();n=struct.unpack_from('<I',raw,80)[0];require(len(raw)==84+50*n,'Invalid original STL')
  stl=[]
  for i in range(n):
   v=struct.unpack_from('<9f',raw,84+50*i+12);stl.append(directed([v[k*3:k*3+3] for k in range(3)]))
  bpy.ops.wm.open_mainfile(filepath=str(Path(args.blend).resolve()));scene=bpy.context.scene
  all_meshes=[o for o in bpy.data.objects if o.type=='MESH'];require(len(all_meshes)==1,'Expected exactly one mesh, including hidden/unlinked objects')
  obj=all_meshes[0];require(len(obj.modifiers)==0,'Saved mesh has modifiers');require(all(len(p.vertices)==3 for p in obj.data.polygons),'Saved mesh contains non-triangle polygons')
  require(all(obj.matrix_world[i][j]==(1 if i==j else 0) for i in range(4) for j in range(4)),'Saved mesh world transform is not identity')
  depsgraph=bpy.context.evaluated_depsgraph_get();instances=[i for i in depsgraph.object_instances if i.object.type=='MESH'];require(len(instances)==1,'Expected exactly one evaluated mesh instance')
  evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();actual=[]
  for tri in mesh.loop_triangles:actual.append(directed([evaluated.matrix_world@mesh.vertices[i].co for i in tri.vertices]))
  evaluated.to_mesh_clear()
  stl_counter,blend_counter=collections.Counter(stl),collections.Counter(actual)
  material_image_nodes=[(m.name,node.name) for m in bpy.data.materials if m.use_nodes for node in m.node_tree.nodes if node.type=='TEX_IMAGE']
  checks=report['checks'];checks.update(exact_world_directed_triangle_multiset_matches=stl_counter==blend_counter,
    original_triangle_count_matches=len(actual)==n,no_modifiers=len(obj.modifiers)==0,
    no_hidden_replacement_mesh=len(all_meshes)==1 and not obj.hide_render and obj in scene.objects.values(),
    no_external_photo_images=len(bpy.data.images)==0 and not material_image_nodes,
    scene_stl_hash_matches=scene.get('original_stl_sha256')==args.expected_sha256,
    mesh_stl_hash_matches=obj.get('stl_sha256')==args.expected_sha256,
    millimetre_units=scene.unit_settings.system=='METRIC' and abs(scene.unit_settings.scale_length-.001)<1e-10,
    one_cpu_render_thread=scene.render.threads_mode=='FIXED' and scene.render.threads==1,
    cycles_cpu_renderer=scene.render.engine=='CYCLES' and scene.cycles.device=='CPU',
    no_compositor_or_sequencer=not scene.use_nodes and (scene.sequence_editor is None or len(scene.sequence_editor.sequences_all)==0),
    no_view_layer_material_overrides=all(layer.material_override is None for layer in scene.view_layers),
    mesh_normally_visible=obj.visible_camera and not obj.is_holdout and not obj.is_shadow_catcher,
    no_shader_node_groups=not any(n.type=='GROUP' for collection in [bpy.data.materials,bpy.data.worlds] for x in collection if x.use_nodes for n in x.node_tree.nodes),
    no_shape_keys=len(bpy.data.shape_keys)==0,
    no_object_constraints=all(len(o.constraints)==0 for o in bpy.data.objects),
    no_animation_or_drivers=all(getattr(x,'animation_data',None) is None for collection in [bpy.data.objects,bpy.data.meshes,bpy.data.materials,bpy.data.node_groups,bpy.data.worlds,bpy.data.cameras,bpy.data.lights,bpy.data.scenes] for x in collection) and all(getattr(x.node_tree,'animation_data',None) is None for collection in [bpy.data.materials,bpy.data.worlds] for x in collection if x.use_nodes),
    fixed_nonanimated_render_seed=scene.cycles.seed==0 and not scene.cycles.use_animated_seed,
    denoising_disabled_or_cpu_oidn=not scene.cycles.use_denoising or (scene.cycles.denoiser=='OPENIMAGEDENOISE' and not scene.cycles.denoising_use_gpu),
    no_image_textures=not material_image_nodes,
    no_unexpected_renderable_objects=all(o.type in ('MESH','CAMERA','LIGHT') for o in bpy.data.objects),
    one_camera_two_suns=sum(o.type=='CAMERA' for o in scene.objects)==1 and len([o for o in scene.objects if o.type=='LIGHT' and o.data.type=='SUN'])==2 and sum(o.type=='LIGHT' for o in scene.objects)==2,
    frozen_image_resolution=scene.render.resolution_x==1000 and scene.render.resolution_y==780 and scene.render.resolution_percentage==100)
  report.update(original_face_count=n,saved_world_face_count=len(actual),blend_missing_triangle_count=sum((stl_counter-blend_counter).values()),blend_extra_triangle_count=sum((blend_counter-stl_counter).values()),image_names=[im.name for im in bpy.data.images],material_image_nodes=material_image_nodes,
    render_settings={'engine':scene.render.engine,'samples':scene.cycles.samples,'device':scene.cycles.device,'use_denoising':scene.cycles.use_denoising,'denoiser':scene.cycles.denoiser,'denoising_use_gpu':scene.cycles.denoising_use_gpu,'seed':scene.cycles.seed,'animated_seed':scene.cycles.use_animated_seed,'exposure':scene.view_settings.exposure,'resolution':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage]})
  # Render Result is transient and may be stored by Blender as a generated image;
  # no image is used in a material regardless. Non-generated input images fail.
  checks['no_external_photo_images']=not any(im.source in ('FILE','SEQUENCE','MOVIE','TILED') for im in bpy.data.images) and not material_image_nodes
  manifest=json.loads(Path(args.manifest).read_text());required={'front','rear','local-plus-y','local-minus-y','local-plus-x','local-minus-x','top','court-open','court-high-wings','entry','court-stair'}
  require(set(manifest['views'])==required,'View manifest does not contain exactly the eleven required views');require(manifest['stl_sha256']==args.expected_sha256,'Render manifest bound to wrong STL')
  cam=scene.camera;require(cam is not None,'Saved scene has no camera');camdata=cam.data;rows=[]
  pos,target,scale=manifest['views']['front']['camera'];rotation=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
  checks['saved_initial_camera_matches_front']=all(abs(a-b)<=1e-6 for a,b in zip(cam.location,pos)) and all(abs(a-b)<=1e-6 for a,b in zip(cam.rotation_euler,rotation)) and camdata.type=='ORTHO' and camdata.ortho_scale==scale and camdata.lens==26
  if not args.inspect_only:
   require(all(checks.values()),'Blend inspection failed; not rendering mismatching scene')
   for name,item in manifest['views'].items():
    pos,target,scale=item['camera'];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale;camdata.clip_start=.1
    camdata.type='PERSP' if name in ['court-high-wings','court-stair'] else 'ORTHO';camdata.lens=26
    bpy.context.view_layer.update();posed=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());posed_mesh=posed.to_mesh();posed_mesh.calc_loop_triangles()
    posed_triangles=collections.Counter(directed([posed.matrix_world@posed_mesh.vertices[i].co for i in t.vertices]) for t in posed_mesh.loop_triangles);posed.to_mesh_clear()
    require(posed_triangles==stl_counter,'Evaluated geometry changed for view '+name)
    p=out/(name+'.png');scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    original_png=Path(args.manifest).parent/(name+'.png');clean_original=out/'sanitized-original'/(name+'.png');clean_rerender=out/'sanitized-rerender'/(name+'.png')
    original_cleanup=sanitize_png(original_png,clean_original,item['sha256']);rerender_cleanup=sanitize_png(p,clean_rerender,sha(p));comparison=compare_png(clean_original,clean_rerender,original_cleanup['sanitized_png_sha256'])
    rows.append({'view':name,'original_raw_png_sha256':item['sha256'],'rerendered_raw_png_sha256':sha(p),'raw_png_files_bitwise_identical':sha(p)==item['sha256'],'original_metadata_cleanup':original_cleanup,'rerendered_metadata_cleanup':rerender_cleanup,'sanitized_png_comparison':comparison,'posed_world_directed_geometry_matches_stl':posed_triangles==stl_counter})
    (out/'view-results-in-progress.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
   checks['all_eleven_decoded_rgba_bytes_identical']=len(rows)==11 and all(r['sanitized_png_comparison']['decoded_rgba_bytes_identical'] for r in rows)
   checks['all_eleven_nonremoved_metadata_identical']=len(rows)==11 and all(r['sanitized_png_comparison']['all_nonvolatile_metadata_identical'] for r in rows)
   checks['all_eleven_metadata_only_cleanups_proved']=len(rows)==11 and all(r['original_metadata_cleanup']['passed'] and r['rerendered_metadata_cleanup']['passed'] and r['sanitized_png_comparison']['passed'] for r in rows)
   report['raw_png_file_bitwise_identity_all_views']=all(r['raw_png_files_bitwise_identical'] for r in rows)
   report['sanitized_png_file_bitwise_identity_all_views']=all(r['sanitized_png_comparison']['whole_png_file_bytes_identical'] for r in rows)
   report['image_reproduction_scope']='Exact decoded RGBA8 pixels and every surviving chunk/metadata after explicit privacy/time tEXt whitelist removal. Original raw PNG hashes remain bound; raw file-byte reproducibility is not asserted.'
  report['views']=rows;report['inspect_only']=args.inspect_only
  checks['inspector_source_unchanged']=sha(__file__)==report['source_sha256']
  checks['png_comparator_source_unchanged']=sha(Path(__file__).with_name('png_exact_compare.py'))==report['png_comparator_source_sha256']
  checks['original_blend_unchanged']=sha(args.blend)==report['original_blend_sha256'];checks['original_stl_unchanged']=sha(args.stl)==report['original_stl_sha256'];checks['original_manifest_unchanged']=sha(args.manifest)==report['original_manifest_sha256']
  report['passed']=all(checks.values());report['strict_passed']=report['passed']
 except Exception as e:report.update(error_type=type(e).__name__,error=str(e))
 (out/'blend-rerender-audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':report['passed'],'error':report.get('error')}))
 if not report['passed']:raise RuntimeError('Saved Blend/rerender audit failed')
if __name__=='__main__':main()
