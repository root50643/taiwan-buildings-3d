"""Blender 4.3.2 editable original mesh and material previews.
blender -b --factory-startup --python source/render_appearance.py -- --out appearance
All rendering is of the delivered mesh, without added architecture or textures.
"""
import bpy,sys,json,argparse,math
from pathlib import Path
import numpy as np
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--render',action='store_true');ap.add_argument('--views',default='all');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);(out/'previews').mkdir(exist_ok=True)
d=np.load(out/'mesh-data.npz');info=json.loads((out/'face-materials.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):bpy.data.materials.remove(block)
for block in list(bpy.data.images):bpy.data.images.remove(block)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
mesh=bpy.data.meshes.new('Original_STL_triangles_exact_order');mesh.from_pydata(d['vertices'].tolist(),[],d['faces'].tolist());mesh.update()
obj=bpy.data.objects.new('FGU Huaien Hall - original mesh, material annotations',mesh);scene.collection.objects.link(obj)
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for p in info['palette']:
 rgb=[int(p['hex'][j:j+2],16)/255 for j in (1,3,5)];mat=bpy.data.materials.new(p['id']);mat.diffuse_color=(*[linear(c) for c in rgb],1);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.55 if p['id']!='glazing_dark_reflective' else .30;mat['display_srgb_hex']=p['hex'];mat['meaning']=p['meaning'];mat['sources']=', '.join(p['sources']);mesh.materials.append(mat)
original_ids=mesh.attributes.new('original_stl_face_id','INT','FACE')
for i,(poly,mi) in enumerate(zip(mesh.polygons,d['materials'])):poly.material_index=int(mi);poly.use_smooth=False;original_ids.data[i].value=i
obj['original_stl_sha256']=info['source_stl_sha256'];obj['scope']=info['scope'];obj['unknown_policy']=info['unknown_policy'];obj['third_party_pixels_embedded']=False;obj['triangle_order']='Original binary STL triangle order; coordinate tuples indexed by first occurrence';obj['known_glazing_bays']='enclosed -56.25,-45,-33.75; open 78.75,90,101.25 degrees'
# Only mesh object in this file is the editable building. Camera and lights are
# presentation helpers; no floor plane or hidden duplicate architecture exists.
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Presentation camera';cam.data.type='ORTHO';cam.data.clip_start=.1;cam.data.clip_end=5000;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.studiolight_rotate_z=.45;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=.8;scene.display.shading.curvature_valley_factor=.8;scene.display.shading.show_specular_highlight=False;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.display.render_aa='32';scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
views={
 'front':((190,-230,145),(0,0,19),235),
 'front-low':((180,-235,65),(0,0,23),235),
 'rear':((-130,240,135),(0,0,20),235),
 'rear-low':((100,240,78),(0,0,23),225),
 'east':((290,0,82),(0,0,20),190),
 'west':((-290,0,82),(0,0,20),190),
 'top':((0,0,300),(0,0,0),220),
 'glazing-front-detail':((170,-160,56),(32,-34,26),82),
 'glazing-gallery-detail':((90,260,94),(15,42,26),87)
}
def setview(name):
 pos,target,scale=views[name];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 if name=='top':cam.rotation_euler=(0,0,0)
def cleanpaths():
 # Clear full fixed-size buffers before setting a shorter portable path.
 scene.render.filepath=' '*(scene.render.bl_rna.properties['filepath'].length_max-1);scene.render.filepath='//previews/front.png'
 for screen in bpy.data.screens:
  for area in screen.areas:
   for space in area.spaces:
    if space.type=='FILE_BROWSER' and space.params:
     space.params.directory=b' '*(space.params.bl_rna.properties['directory'].length_max-1);space.params.directory=b'//'
setview('front');bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=220;area.spaces.active.region_3d.view_location=(0,0,20);area.spaces.active.shading.color_type='MATERIAL'
scene['model_export_object']=obj.name;scene['preview_renderer']='Workbench studio, uncalibrated display approximation';scene['known_color_limits']='No measured paint specification; all unregistered faces are neutral placeholders.'
bpy.context.preferences.filepaths.save_version=0;cleanpaths();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
if a.render:
 names=views.keys() if a.views=='all' else a.views.split(',')
 for name in names:
  setview(name);scene.render.filepath='//previews/'+name+'.png';bpy.ops.render.render(write_still=True)
setview('front');cleanpaths();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
(out/'render-manifest.json').write_text(json.dumps({'views':{name:{'position_mm':pos,'target_mm':target,'ortho_scale_mm':scale,'file':'previews/'+name+'.png'} for name,(pos,target,scale) in views.items()},'renderer':'Blender 4.3.2 Workbench studio','model_object':obj.name,'original_triangles':len(mesh.polygons),'geometry_modified':False,'materials':len(mesh.materials),'textures':False,'display_uncertainty':'Lighting and sRGB approximations; no calibrated finish match.'},indent=2)+'\n')
print('Editable original mesh saved: 36870 triangles; 4 face-material slots; 0 textures.')
