"""Render only the delivered STL, then save editable Blender mesh. Blender 4.3+."""
import bpy,json
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent;PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='NTUS_Changqi_2017_Actual_STL_mm'
mat=bpy.data.materials.new('Warm limestone, preview only');mat.diffuse_color=(.71,.66,.55,1);model.data.materials.append(mat)
# Material assignment uses actual STL triangle coordinates, not overlay geometry.
colors=[('Dark window recess',(.18,.26,.28,1)),('Dark gray library base',(.38,.41,.43,1)),('Original green-roof areas',(.34,.45,.22,1)),('Light roof surface',(.76,.75,.68,1)),('Recessed stair green wall',(.29,.38,.23,1))]
for name,c in colors:
 m=bpy.data.materials.new(name);m.diffuse_color=c;model.data.materials.append(m)
S=150/68;regions=json.loads((OUT/'preview-material-regions.json').read_text())['windows']
for p in model.data.polygons:
 v=p.center;x=v.x/S+30;y=-v.y/S+13;z=v.z/S-1.2
 if z<0:continue
 if z<4.5 or (x>27 and z<8.7):p.material_index=2
 for a,b,c,d,e,f in regions:
  if a-1e-4<=x<=b+1e-4 and c-1e-4<=y<=d+1e-4 and e+1e-4<z<f-1e-4:
   p.material_index=1;break
 if p.normal.z>.9 and ((.7<x<15.9 and .8<y<21.9 and z>27.7) or (20.3<x<27.5 and 11.25<y<22.4 and 21.5<z<21.7) or (35<x<54.8 and 24.2<y<30.7 and 21.5<z<21.7)):p.material_index=3
 if p.normal.z>.9 and 28.7<x<55.8 and 10.5<y<23 and 23<z<23.7:p.material_index=4
 if (13.3<x<18.6 and abs(y+3.55)<1e-3 and 4.8<z<27) or (8.5<x<17 and abs(y-28.55)<1e-3 and 4.8<z<27):p.material_index=5

scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.45;scene.display.shading.curvature_valley_factor=1.3;scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085);scene.view_settings.view_transform='Standard'
scene.render.resolution_x=900;scene.render.resolution_y=680;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.render.use_stamp=False
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Actual_STL_camera';scene.camera=cam;cam.data.type='ORTHO'
views=[('front',(-190,-240,145),(0,0,32)),('rear',(205,235,140),(0,0,32)),('street',(-270,15,95),(-20,0,35)),('south',(30,-280,98),(0,0,33)),('north',(30,280,98),(0,0,33)),('end',(270,25,98),(0,0,33)),('southeast',(230,-210,135),(0,0,33)),('top',(0,0,300),(0,0,0))]
saved_views={}
for name,loc,aim in views:
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 if name=='top':cam.rotation_euler=(0,0,0)
 inv=cam.rotation_euler.to_matrix().transposed();projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*900/680)*1.12
 saved_views[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale}
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=front_scale
scene.render.filepath='//previews/front.png'
model['preview_cameras_json']=json.dumps(saved_views);model['units']='mm';model['school']='國立臺灣體育運動大學';model['period']='2017 completed core';model['source_mesh']='model.stl';model['scope']='Original exterior approximation, not a measured survey'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))

# Strip timestamp, host file path, EXIF and all other ancillary PNG chunks.
import struct
for path in PREV.glob('*.png'):
 raw=path.read_bytes();out=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8];chunk=raw[i:i+n+12]
  if kind in [b'IHDR',b'PLTE',b'IDAT',b'IEND',b'tRNS']:out+=chunk
  i+=n+12
 path.write_bytes(out)
