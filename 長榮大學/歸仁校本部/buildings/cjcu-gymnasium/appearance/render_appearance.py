#!/usr/bin/env python3
"""Blender 4.3.2: actual material-face mesh renders, not photo reconstruction."""
from pathlib import Path
import argparse,bpy,json,numpy as np,struct,sys
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--views',default='');p.add_argument('--no-render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=a.out;root.mkdir(exist_ok=True);(root/'previews').mkdir(exist_ok=True);(root/'qa').mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for collection in (bpy.data.meshes,bpy.data.cameras,bpy.data.lights,bpy.data.materials):
 for d in list(collection):collection.remove(d)
D=np.load(root/'mesh-data.npz');palette=json.loads((Path(__file__).resolve().parent/'palette.json').read_text())
mesh=bpy.data.meshes.new('Exact original STL triangles in original face order');mesh.from_pydata(D['vertices'].tolist(),[],D['faces'].tolist());mesh.update()
obj=bpy.data.objects.new('CJCU gymnasium — roof family illustration only',mesh);bpy.context.scene.collection.objects.link(obj)
for d in palette:
 m=bpy.data.materials.new(d['id']);m.diffuse_color=d['blender_linear_rgba'];m.use_nodes=True;bsdf=m.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=d['blender_linear_rgba'];bsdf.inputs['Roughness'].default_value=d['roughness'];bsdf.inputs['Metallic'].default_value=d['metallic'];bsdf.inputs['Emission Strength'].default_value=0;bsdf.inputs['Transmission Weight'].default_value=0;m['interpretation']=d['meaning'];mesh.materials.append(m)
for p,mi in zip(mesh.polygons,D['materials']):p.material_index=int(mi);p.use_smooth=False
attr=mesh.attributes.new('original_stl_triangle_index','INT','FACE');attr.data.foreach_set('value',np.arange(len(mesh.polygons),dtype=np.int32))
obj['source_mesh']='../model.stl';obj['source_stl_sha256']='ebecf2597fbc17fd0faf5a8bcd3ac13d1d9511d70a9600c5c09084ddbd26d879'
obj['scope']='Non-photometric neutral sheet-material family illustration only, from 2020 official night roof photograph. Not actual daylight color, alloy, coating, calibrated PBR, or current 2026 condition.'
obj['excluded']='All domes, roof ends, brick and other walls remain original preview neutral. No ribs, texture, geometry edits or hidden reconstruction.'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2;scene.display.shading.show_specular_highlight=False;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.resolution_x=1200;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False;scene.render.threads_mode='FIXED';scene.render.threads=4
camdat=bpy.data.cameras.new('Illustration camera');cam=bpy.data.objects.new('Illustration camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO'
views=[('front',(195,-220,155),(0,0,29.733345)),('rear',(-195,230,160),(0,0,29.733345)),('top',(0,0,300),(0,0,0)),('front-elevation',(0,-260,29.733345),(0,0,29.733345)),('rear-elevation',(0,260,29.733345),(0,0,29.733345)),('left',(-260,0,100),(0,0,29.733345)),('right',(260,0,100),(0,0,29.733345)),('roof-oblique',(-150,-200,260),(0,0,29.733345)),('rear-roof',(170,210,250),(0,0,29.733345))]
def aim(loc,target):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();inv=cam.rotation_euler.to_matrix().transposed();points=[inv@(obj.matrix_world@Vector(c)-cam.location) for c in obj.bound_box];width=max(v.x for v in points)-min(v.x for v in points);height=max(v.y for v in points)-min(v.y for v in points);camdat.ortho_scale=max(width,height*1.25)*1.18
 # Recenter both projected bounds (orthographic crop must include whole base).
 mid=Vector(((max(v.x for v in points)+min(v.x for v in points))/2,(max(v.y for v in points)+min(v.y for v in points))/2,0));cam.location+=cam.rotation_euler.to_matrix()@mid

def strip_png(path):
 b=path.read_bytes();out=b[:8];i=8
 while i<len(b):
  n=struct.unpack_from('>I',b,i)[0];tag=b[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=b[i:i+n+12]
  i+=n+12
 path.write_bytes(out)
manifest=[]
for name,loc,target in views:
 aim(loc,target);manifest.append({'name':name,'camera_model_mm':list(cam.location),'look_at_initial_model_mm':target,'orthographic_scale_mm':camdat.ortho_scale})
 if a.views and name not in a.views.split(','):continue
 if not a.no_render:scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_png(root/'previews'/f'{name}.png')
aim(views[0][1],views[0][2]);bpy.context.view_layer.objects.active=obj;obj.select_set(True);cam.select_set(False)
for s in bpy.data.scenes:
 limit=s.render.bl_rna.properties['filepath'].length_max;s.render.filepath='_'*(limit-1);s.render.filepath='//previews/front.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:
    limit=space.params.bl_rna.properties['directory'].length_max;space.params.directory=b'_'*(limit-1);space.params.directory=b'//'
   if space.type=='VIEW_3D':space.shading.color_type='MATERIAL';space.region_3d.view_perspective='CAMERA'
for im in list(bpy.data.images):bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'cjcu-gymnasium-roof-illustration.blend'))
(root/'qa'/'render-manifest.json').write_text(json.dumps({'engine':'Blender 4.3.2 Workbench studio, actual per-face material display','non_photometric':True,'image_textures':0,'dimensions_px':[1200,960],'views':manifest,'orientation':'Front and rear follow original model local Y axes, not surveyed compass directions.','disclaimer':'Historical sheet-family neutral illustration only; not actual daylight paint/material specification or 2026 condition.'},indent=2)+'\n')
