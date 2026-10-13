"""Render the actual STL, save editable Blender scene, verify mesh equality.
Run blender -b -t 4 -P render_preview.py. Blender 4.x, no external assets.
"""
import bpy,os,json,hashlib,struct
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__));os.makedirs(os.path.join(ROOT,'previews'),exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=os.path.join(ROOT,'model.stl'));o=bpy.context.object;o.name='Printable exterior (millimetres)'
mat=bpy.data.materials.new('Ivory clay preview');mat.diffuse_color=(.58,.64,.66,1);o.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.5;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.5;sh.curvature_valley_factor=1.2;sh.background_type='WORLD';scene.world.color=(.055,.07,.08)
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
center=sum((o.matrix_world@Vector(c) for c in o.bound_box),Vector())/8
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=max(o.dimensions)*1.70
for name,offset in [('front',(160,-260,170)),('rear',(-170,260,170))]:
 cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=os.path.join(ROOT,'previews',name+'.png');bpy.ops.render.render(write_still=True)
# Compare canonical triangle coordinates, invariant to vertex reindexing and triangle order.
def signature(tris):
 values=[]
 for tri in tris:
  pts=sorted(tuple(round(float(a),5) for a in p) for p in tri);values.append(tuple(pts))
 return hashlib.sha256(repr(sorted(values)).encode()).hexdigest()
raw=open(os.path.join(ROOT,'model.stl'),'rb').read();n=struct.unpack_from('<I',raw,80)[0]
source=[]
for i in range(n):
 vs=struct.unpack_from('<9f',raw,84+i*50+12);source.append([vs[j:j+3] for j in [0,3,6]])
o.data.calc_loop_triangles();blend=[[(o.matrix_world@o.data.vertices[j].co)[:] for j in p.vertices] for p in o.data.loop_triangles]
a,b=signature(source),signature(blend)
report={'passed':a==b,'method':'All actual STL and Blender triangle coordinates compared after 0.00001 mm rounding, independent of face order.','stl_triangles':len(source),'blender_triangles':len(blend),'stl_geometry_sha256':a,'blender_geometry_sha256':b,'unit_scale_metres':.001}
open(os.path.join(ROOT,'blender-geometry-check.json'),'w').write(json.dumps(report,indent=2));assert report['passed']
scene.render.filepath='//previews/front.png'
cam.location=center+Vector((160,-260,170));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'scene.blend'))
