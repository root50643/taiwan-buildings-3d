"""Render delivered STLs in Blender 5.2.2; saves an editable assembly scene.
python render_preview.py OR blender -b -t 4 -P render_preview.py
No reference image is packed. Materials are only explanatory preview colours.
"""
from pathlib import Path
import bpy, hashlib, json, struct, sys
sys.dont_write_bytecode=True
from mathutils import Vector
R=Path(__file__).resolve().parent;D=R/'previews';D.mkdir(exist_ok=True)
sys.path.insert(0,str(R))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean_png(p):
    raw=p.read_bytes();out=raw[:8];i=8
    while i<len(raw):
        n=struct.unpack('>I',raw[i:i+4])[0];t=raw[i+4:i+8]
        if t not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:out+=raw[i:i+n+12]
        i+=n+12
    p.write_bytes(out)

bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(R/'model.stl'))
model=bpy.context.object;model.name='CNU_J_historical_assembly_22_pieces'
for name,c in [('Ivory exterior',(.8,.82,.78,1)),('Base',(.31,.37,.38,1)),
               ('Roof and observed structural frames',(.23,.37,.40,1)),
               ('Central rear glass relief',(.24,.43,.47,1))]:
    m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
    model.data.materials.append(m)
for f in model.data.polygons:
    z=[model.data.vertices[i].co.z for i in f.vertices];c=f.center
    if max(z)<3.01:f.material_index=1
    elif min(z)>23.7 and c.z>28:f.material_index=2
    elif abs(c.x)<26.1 and 22.65<c.y<23.45 and 5.99<c.z<23.61:f.material_index=3
model['units']='mm';model['source_stl_sha256']=sha(R/'model.stl')
model['period']='Historical source composite: dated 2006 / 2010 / 2012 photographs plus undated elevated roof photo. Not a 2026 current-state claim.'
model['piece_count']=22;model['print_warning']='Use the four unique bed-oriented parts at 100%, quantities 1+1+10+10. Assembly STL is overview only. No physical print or fit test.'
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU'
scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.37,.42,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for loc,power,size in [((-90,-100,180),650000,140),((100,80,140),450000,120)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object
    light.data.energy=power;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(Vector((0,0,15))-light.location).to_track_quat('-Z','Y').to_euler()
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=1.2;scene.display.shading.background_type='WORLD'
scene.world.color=(.055,.065,.08);scene.view_settings.view_transform='Standard'
scene.render.resolution_x=1100;scene.render.resolution_y=760;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';cam.data.type='ORTHO';scene.camera=cam

def render(name,loc,aim,objects):
    cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
    inv=cam.rotation_euler.to_matrix().transposed()
    p=[inv@(o.matrix_world@Vector(c)-cam.location) for o in objects for c in o.bound_box]
    w=max(v.x for v in p)-min(v.x for v in p);h=max(v.y for v in p)-min(v.y for v in p)
    cam.data.ortho_scale=max(w,h*1100/760)*1.12
    scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
    clean_png(D/(name+'.png'))

views=[('front',(-140,-240,130),(0,-3,23)),('rear',(140,230,110),(0,0,23)),
       ('side',(240,-80,75),(0,0,24)),('front-low',(0,-250,40),(0,-3,22)),
       ('top',(0,0,300),(0,0,0))]
for a,b,c in views:render(a,b,c,[model])
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png';cam.data.ortho_scale=250
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene.blend'),compress=False)
from sanitize_scene import sanitize
sanitize(R/'scene.blend')
# A separate preview of the four unique pieces in their delivered bed orientation.
model.hide_render=True;objects=[]
for name,xy in [('main_body',(0,0)),('roof',(0,106)),('column',(205,110)),('mast_brace_frame',(205,126))]:
    bpy.ops.wm.stl_import(filepath=str(R/'parts'/f'{name}-print.stl'))
    o=bpy.context.object;o.location=(xy[0],xy[1],0);o.name=name+'_print'
    o.data.materials.append(bpy.data.materials['Ivory exterior' if name=='main_body' else 'Roof and observed structural frames'])
    objects.append(o)
bpy.context.view_layer.update()
render('unique-print-parts',(320,-350,360),(112,87,10),objects)
manifest={'source':'Delivered model.stl for assembly; delivered *-print.stl for unique-print-parts. No proxy geometry.',
          'assembly_sha256':sha(R/'model.stl'),'scene_sha256':sha(R/'scene.blend'),
          'previews':{p.name:sha(p) for p in sorted(D.glob('*.png'))}}
(R/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
