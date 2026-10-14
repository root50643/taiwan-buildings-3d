"""Import only actual model.stl, save editable scene.blend and render four views.
Display colors aid reading; STL has no color. Blender 4.3+.
"""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent; P=R/'previews';P.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(R/'model.stl'));obj=bpy.context.object;obj.name='NOU_North_Courtyard_actual_STL'
for name,col in [('Warm plaster',(.77,.75,.65,1)),('Red weatherproof roof',(.60,.13,.10,1)),('Base',(.58,.61,.59,1)),('Gate relief frame',(.15,.17,.16,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=col;obj.data.materials.append(m)
for p in obj.data.polygons:
 c=p.center
 if c.z<=1.81:p.material_index=2
 elif c.z>=7.8 and not (-67.2<c.y<-65.8 and abs(c.x)<8.1 and c.z>9.4):p.material_index=1
 elif c.y<-73.1 and (abs(c.x-4.15)<.65 or abs(c.x+4.15)<.65 or abs(abs(c.x)-9.05)<.65 or c.z>=7.0):p.material_index=3
 else:p.material_index=0
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
s=scene.display.shading;s.light='STUDIO';s.studiolight_rotate_z=.3;s.color_type='MATERIAL';s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.curvature_ridge_factor=1.35;s.curvature_valley_factor=1.25;s.show_specular_highlight=True;s.background_type='WORLD'
scene.world.color=(.12,.14,.16);scene.view_settings.view_transform='Standard'
scene.render.resolution_x=900;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Review_camera';scene.camera=cam;cam.data.type='ORTHO'
views=[('front',(-170,-240,150)),('rear',(170,240,150)),('side',(260,-25,135)),('top',(0,0,300)),('front_elevation',(0,-260,6)),('courtyard_detail',(100,-180,82)),('gate_detail',(0,-170,25))]
manifest={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'geometry_source':'model.stl','views':{}}
for name,loc in views:
 target=(0,0,4.4)
 if name=='front_elevation':target=(0,0,6)
 if name=='gate_detail':target=(0,-67,6)
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();pts=[inv@Vector(c) for c in obj.bound_box]
 width=max(v.x for v in pts)-min(v.x for v in pts);height=max(v.y for v in pts)-min(v.y for v in pts)
 cam.data.ortho_scale=max(width,height*900/720)*1.12
 if name=='gate_detail':cam.data.ortho_scale=25
 scene.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
 manifest['views'][name]={'camera_location':list(cam.location),'camera_rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'aim':target,'size_px':[900,720]}
v=manifest['views']['front'];cam.location=v['camera_location'];cam.rotation_euler=v['camera_rotation_euler'];cam.data.ortho_scale=v['ortho_scale'];scene.render.filepath='//previews/front.png'
obj['geometry_source']='model.stl';obj['stl_sha256']=manifest['stl_sha256'];obj['units']='millimetres';obj['scope']='Photo-derived exterior massing; red weatherproof roof version; photography dates uncertain.'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene.blend'))
(R/'render-manifest.json').write_text(json.dumps(manifest,indent=2))
