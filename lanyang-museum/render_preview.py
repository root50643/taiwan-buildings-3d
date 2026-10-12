"""Copy alongside model.stl, then run: blender -b -t 6 -P render_preview.py.
Renders the actual printable mesh; no decorative non-printing facade geometry.
"""
import bpy,os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));PREV=os.path.join(OUT,'previews');os.makedirs(PREV,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=os.path.join(OUT,'model.stl'));model=bpy.context.object;model.name='Printable building'
mat=bpy.data.materials.new('Warm ivory');mat.use_nodes=True
node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.75,.72,.66,1);node.inputs['Roughness'].default_value=.76;model.data.materials.append(mat)
# Assign material solely to faces imported from the printable STL.
import math
C=math.cos(math.radians(20));S=math.sin(math.radians(20))
for label,color in [('Glass interpretation',(.075,.20,.27,1)),('Granite dark',(.24,.26,.25,1)),('Granite light',(.48,.47,.43,1)),('Granite medium',(.33,.34,.31,1))]:
    mm=bpy.data.materials.new(label);mm.use_nodes=True;mm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color;mm.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.68;model.data.materials.append(mm)
for poly in model.data.polygons:
    c=poly.center;u=c.x*C-c.z*S
    if c.z>3.75 and abs(c.y)<.405*(65.5-c.x)+4:
        if (-56<u<-32) or (-7<u<-3) or (19<u<24) or (37<u<41):poly.material_index=1
        elif u<-61.4 and -42<c.y<23:poly.material_index=1
        else:poly.material_index=4
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.2));floor=bpy.context.object;floor.name='Studio floor (not part of model)'
m=bpy.data.materials.new('Slate');m.diffuse_color=(.075,.09,.105,1);floor.data.materials.append(m)
scene=bpy.context.scene;scene.world.color=(.16,.16,.16)
center=sum((model.matrix_world@Vector(c) for c in model.bound_box),Vector())/8
longest=max(model.dimensions);aim=Vector((center.x,center.y,model.dimensions.z*.42))
def light(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-100,-150,210),650000,140);light('Fill',(160,-50,120),230000,100);light('Rim',(20,140,180),600000,110)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=longest*1.4
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.use_stamp=False
scene.view_settings.view_transform='AgX';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
for name,loc in [('front',(-165,-215,155)),('rear',(155,215,170)),('elevation',(0,-250,85))]:
 cam.location=loc;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=os.path.join(PREV,name+'.png');bpy.ops.render.render(write_still=True)
scene.render.filepath='//previews/rear.png';bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'scene.blend'))
