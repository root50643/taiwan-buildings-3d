"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os,struct
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews'; PREV.mkdir(exist_ok=True)
def strip_nondeterministic_metadata(path):
 raw=path.read_bytes(); out=raw[:8]; i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0]; kind=raw[i+4:i+8]; chunk=raw[i:i+12+n]
  if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out+=chunk
  i+=12+n
 path.write_bytes(out)  # Pixel bytes unchanged; remove date/time and private-path stamps.

bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='Tajen_Admin_Library'
mat=bpy.data.materials.new('Neutral building preview');mat.diffuse_color=(.85,.85,.81,1);model.data.materials.append(mat)
base_mat=bpy.data.materials.new('Base contrast preview only');base_mat.diffuse_color=(.32,.39,.42,1);model.data.materials.append(base_mat)
roof_mat=bpy.data.materials.new('Roof contrast preview only');roof_mat.diffuse_color=(.52,.30,.24,1);model.data.materials.append(roof_mat)
pink=bpy.data.materials.new('Pink wall contrast only');pink.diffuse_color=(.62,.44,.43,1);model.data.materials.append(pink)
glass=bpy.data.materials.new('Actual recessed glazing');glass.diffuse_color=(.19,.29,.33,1);model.data.materials.append(glass)
S=150/62
for f in model.data.polygons:
 v=[model.data.vertices[i].co for i in f.vertices];x=sum(q.x for q in v)/len(v)/S;y=sum(q.y for q in v)/len(v)/S;z=(sum(q.z for q in v)/len(v)-2)/S
 if max(q.z for q in v)<=2.00001:f.material_index=1
 elif abs(f.normal.z)>.9 and (abs(z-31.8)<.02 or abs(z-38.45)<.02):f.material_index=2
 elif z<25.5 and (y<9 or x>17.6):f.material_index=3
 if 17.0<x<18.15 and z>8.5:f.material_index=0
 if any(abs(x-a)<.012 for a in [17.35,17.3,-19.36,16.8,16.85,-16.7,36.3,22.35]) or any(abs(y-a)<.012 for a in [-17.45,-22.40,-19.,19.35,9.65,-18.4]):f.material_index=4
# Primary review is single-grey actual geometry; no painted glazing substitute.
for face in model.data.polygons:face.material_index=0
# Materials improve base/roof readability only, with no change to STL triangles.

target_z=(min(v.co.z for v in model.data.vertices)+max(v.co.z for v in model.data.vertices))/2
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=900;scene.render.resolution_y=675;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=180
for name,loc,aim in [('front',(240,-260,160),(0,0,target_z)),('rear',(-240,260,150),(0,0,target_z)),('west',(-250,-60,115),(0,0,target_z)),('east',(250,-60,115),(0,0,target_z)),('south-elevation',(0,-260,target_z),(0,0,target_z)),('north-elevation',(0,260,target_z),(0,0,target_z)),('front-low',(320,-130,target_z+5),(0,0,target_z)),('rear-low',(-240,280,target_z+5),(0,0,target_z)),('top',(0,0,300),(0,0,0))]:
 # Only the two straight elevations need asymmetric base-centering.
 if name in {'south-elevation','north-elevation'}:
  center_x=(min(v.co.x for v in model.data.vertices)+max(v.co.x for v in model.data.vertices))/2
  loc=(center_x,loc[1],loc[2]);aim=(center_x,aim[1],aim[2])
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
 strip_nondeterministic_metadata(PREV/(name+'.png'))
cam.location=(240,-260,160);cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png'
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='Tajen official 2001 photos, 2024 northwest street image, NLSC2016/2024 roofs; bounded exterior prototype.';model['stl_sha256']=__import__('hashlib').sha256((OUT/'model.stl').read_bytes()).hexdigest()
model['period_scope']='2001 main exterior with 2016/2024 roof checks; visual draft pending review.'
model['model_category']='Single connected printable solid'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
(OUT/'render-manifest.json').write_text(json.dumps({'stl_sha256':model['stl_sha256'],'render_source':'Imported delivered model.stl, no proxy geometry','previews':{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in sorted(PREV.glob('*.png'))}},indent=2))


