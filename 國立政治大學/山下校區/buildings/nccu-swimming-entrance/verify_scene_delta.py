"""Compare geometry/materials/scene setup and actual rendered pixels of two blends.
blender -b --factory-startup --python verify_scene_delta.py -- OLD NEW OUTPUT
No paths or third-party pixels are embedded into the published report.
"""
import bpy,json,sys,hashlib
from pathlib import Path
old,new,out=map(Path,sys.argv[sys.argv.index('--')+1:]);out.mkdir(parents=True,exist_ok=True)
def norm(v):
 if isinstance(v,(str,int,float,bool))or v is None:return v
 try:return [norm(x)for x in v]
 except:return str(v)
def nodes(nt):
 if not nt:return None
 return [{'name':n.name,'type':n.bl_idname,'inputs':{i.identifier:norm(i.default_value)for i in n.inputs if hasattr(i,'default_value')}}for n in nt.nodes]
def snapshot():
 sc=bpy.context.scene;objs=[]
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  d={'name':o.name,'type':o.type,'matrix_world':norm(o.matrix_world),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
  if o.type=='MESH':d.update(vertices=[list(v.co)for v in o.data.vertices],faces=[list(p.vertices)for p in o.data.polygons],material_indices=[p.material_index for p in o.data.polygons],materials=[m.name for m in o.data.materials])
  if o.type=='LIGHT':d['light']={k:norm(getattr(o.data,k))for k in ['type','energy','color','shape','size']}
  if o.type=='CAMERA':d['camera']={k:norm(getattr(o.data,k))for k in ['type','lens','ortho_scale','clip_start','clip_end','shift_x','shift_y']}
  objs.append(d)
 return {'objects':objs,'materials':[{ 'name':m.name,'diffuse_color':norm(m.diffuse_color),'nodes':nodes(m.node_tree)}for m in sorted(bpy.data.materials,key=lambda x:x.name) if m.users>0],'world':nodes(sc.world.node_tree),'camera_name':sc.camera.name,'render':{k:norm(getattr(sc.render,k))for k in ['engine','resolution_x','resolution_y','resolution_percentage','film_transparent']},'image_settings':{k:norm(getattr(sc.render.image_settings,k))for k in ['file_format','color_mode','color_depth','compression']},'cycles':{k:norm(getattr(sc.cycles,k))for k in ['samples','seed','use_denoising']},'view_settings':{k:norm(getattr(sc.view_settings,k))for k in ['view_transform','look','exposure','gamma']},'scene_units':{'system':sc.unit_settings.system,'scale_length':sc.unit_settings.scale_length}}
snaps=[];render_hash=[];pixel_hash=[]
for label,path in [('old',old),('new',new)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();snaps.append(snapshot());sc=bpy.context.scene
 if label=='new':
  assert sc.render.filepath=='//previews/right-end.png'
  for screen in bpy.data.screens:
   for area in screen.areas:
    for sp in area.spaces:
     if sp.type=='FILE_BROWSER' and sp.params:assert sp.params.directory==b'//'
 target=out/(label+'-render.png');sc.render.filepath=str(target);bpy.ops.render.render(write_still=True);render_hash.append(hashlib.sha256(target.read_bytes()).hexdigest())
 # Decoded PNG float pixels avoid metadata-only image comparisons.
 import array
 render_image=bpy.data.images.load(str(target),check_existing=False);assert len(render_image.pixels)>0
 pixels=array.array('f',[0.0])*(len(render_image.pixels));render_image.pixels.foreach_get(pixels);pixel_hash.append(hashlib.sha256(pixels.tobytes()).hexdigest());bpy.data.images.remove(render_image)
assert snaps[0]==snaps[1],'geometry/material/camera/light/render setting delta';assert pixel_hash[0]==pixel_hash[1],'render pixels changed'
report={'compared_releases':['0.1.0','0.1.1'],'blender_version':bpy.app.version_string,'all_objects_geometry_transform_visibility_equal':True,'all_used_materials_nodes_colors_equal':True,'camera_lights_world_render_settings_equal':True,'new_saved_render_path':'//previews/right-end.png','new_file_browser_directories':'//','full_resolution_render':[snaps[0]['render']['resolution_x'],snaps[0]['render']['resolution_y']],'cycles_samples':snaps[0]['cycles']['samples'],'render_png_bytes_identical':render_hash[0]==render_hash[1],'old_new_render_sha256':render_hash,'decoded_png_float_pixel_sha256':pixel_hash,'limits':['Unused zero-user factory material is not part of the scene or model and may be dropped by Blender on save. PNG metadata may change while decoded pixels remain identical.'],'scene_semantics_sha256':hashlib.sha256(json.dumps(snaps[0],sort_keys=True,separators=(',',':')).encode()).hexdigest()}
(out/'path-portability-delta.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
