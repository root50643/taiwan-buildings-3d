"""Render actual STL, save editable Blender scene and verify identical triangle geometry."""
from pathlib import Path
import bpy,json,hashlib,struct
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));m=bpy.context.object;m.name='Printable exterior mesh'
mat=bpy.data.materials.new('Warm architectural plaster');mat.diffuse_color=(.68,.71,.73,1);m.data.materials.append(mat)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.5
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.1
scene.display.shading.background_type='WORLD';scene.world.color=(.13,.15,.18)
scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
center=sum((m.matrix_world@Vector(c) for c in m.bound_box),Vector())/8
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=215
(OUT/'previews').mkdir(exist_ok=True)
for name,delta in [('front',(180,-280,195)),('rear',(-180,280,195))]:
 cam.location=center+Vector(delta);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();right=cam.rotation_euler.to_matrix()@Vector((1,0,0));up=cam.rotation_euler.to_matrix()@Vector((0,1,0));corners=[m.matrix_world@Vector(c)-center for c in m.bound_box];px=[c.dot(right) for c in corners];py=[c.dot(up) for c in corners];cam.data.ortho_scale=max(max(px)-min(px),(max(py)-min(py))*1.25)*1.15
 scene.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
# Triangle-coordinate multiset, normal-independent; confirms imported STL vertices at float32 precision.
def canonical(tris):
 return sorted(tuple(sorted(tuple(round(float(c),5) for c in v) for v in tri)) for tri in tris)
raw=(OUT/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];st=[]
for i in range(n):
 vals=struct.unpack_from('<12fH',raw,84+i*50);st.append([vals[3:6],vals[6:9],vals[9:12]])
blend=[[(m.matrix_world@m.data.vertices[i].co)[:] for i in p.vertices] for p in m.data.polygons]
report={'passed':canonical(st)==canonical(blend),'stl_triangles':n,'blender_triangles':len(blend),'comparison':'Triangle-coordinate multisets, rounded to 5 decimal mm; excludes cameras and studio objects.'}
(OUT/'blender-stl-agreement.json').write_text(json.dumps(report,indent=2));assert report['passed']
scene.render.filepath='//previews/rear.png';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
