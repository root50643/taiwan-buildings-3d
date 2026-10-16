"""Render the exact unmodified original STL. No photo textures or added architecture."""
import bpy,json,struct,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
version=args.pop(0) if args else 'v0';M=R/'models'/version;out=R/'previews'/version;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
raw=(M/'model.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0]
verts=[];faces=[];index={}
for i in range(count):
    coords=struct.unpack_from('<9f',raw,84+50*i+12);f=[]
    for j in range(3):
        v=tuple(coords[j*3:j*3+3])
        if v not in index:index[v]=len(verts);verts.append(v)
        f.append(index[v])
    faces.append(f)
mesh=bpy.data.meshes.new('Original STL, unchanged triangles');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('BWBC Zongde Hall exterior',mesh);bpy.context.collection.objects.link(obj)
obj['stl_sha256']=hashlib.sha256(raw).hexdigest();obj['geometry_policy']='No modifiers, repairs, image textures, or hidden replacement geometry'
palette=[('concrete',(.69,.68,.62)),('base',(.34,.36,.35)),('glass',(.16,.27,.29)),('roof',(.09,.12,.14)),('solar',(.045,.085,.13)),('bamboo',(.48,.24,.08)),('rail',(.40,.44,.43)),('lawn',(.25,.34,.16)),('garden',(.24,.35,.15)),('walk',(.60,.58,.52)),('steel',(.37,.41,.40))]
lookup={n:i for i,(n,c) in enumerate(palette)}
for name,col in palette:
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*col,1);node.inputs['Roughness'].default_value=1.08;obj.data.materials.append(mat)
    if name=='solar':
        # Original procedural colour only: indicative module rhythm, not a measured panel count.
        nt=mat.node_tree;geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0])
        outputs=[]
        for axis,pitch in [('X',3.6),('Y',5.6)]:
            div=nt.nodes.new('ShaderNodeMath');div.operation='DIVIDE';div.inputs[1].default_value=pitch;nt.links.new(sep.outputs[axis],div.inputs[0])
            fract=nt.nodes.new('ShaderNodeMath');fract.operation='FRACT';nt.links.new(div.outputs[0],fract.inputs[0])
            cmp=nt.nodes.new('ShaderNodeMath');cmp.operation='LESS_THAN';cmp.inputs[1].default_value=.035;nt.links.new(fract.outputs[0],cmp.inputs[0]);outputs.append(cmp.outputs[0])
        mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';nt.links.new(outputs[0],mx.inputs[0]);nt.links.new(outputs[1],mx.inputs[1])
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*col,1);mix.inputs[2].default_value=(.36,.42,.43,1);nt.links.new(mx.outputs[0],mix.inputs[0]);nt.links.new(mix.outputs[0],node.inputs['Base Color'])

regions=json.loads((M/'color-regions.json').read_text())
for f in mesh.polygons:
    x,y,z=f.center
    for q in regions:
        a,b,c,d,e,g=q['bounds_mm']
        if a-1e-4<=x<=b+1e-4 and c-1e-4<=y<=d+1e-4 and e-1e-4<=z<=g+1e-4:f.material_index=lookup[q['material']]
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12 if version in ['v0','v1','v2','v8','v9','v11','v12','v14'] else 64;scene.cycles.use_denoising=False;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
scene.render.threads_mode='FIXED';scene.render.threads=1;scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.85,.87,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=1.0
scene.view_settings.exposure=.35;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for name,energy,rot in [('Key',2.0,(25,-30,-35)),('Fill',1.0,(-20,25,140))]:
    data=bpy.data.lights.new(name,'SUN');data.energy=energy;data.angle=.2;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.rotation_euler=tuple(math.radians(v) for v in rot)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_end=2000
views={
 'front':((-210,-250,210),(79,71,19),255),
 'rear':((300,310,220),(79,71,19),255),
 'local-plus-y':((79,450,26),(79,71,26),239),
 'local-minus-y':((79,-350,26),(79,71,26),239),
 'local-plus-x':((450,71,26),(79,71,26),222),
 'local-minus-x':((-350,71,26),(79,71,26),222),
 'top':((79,71,450),(79,71,0),245),
 'court-open':((115,-95,120),(78,80,18),170),
 'court-high-wings':((70,70,7.5),(37.5,107.5,23),115),
 'entry':((71,-140,35),(71,31,17),100),
 'court-stair':((72,52,9),(110,65,12),100),
 'roof-screen-detail':((154,86,100),(102,129,49),42)
}
def pose(name):
    pos,target,scale=views[name];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale;camdata.clip_start=.1
    camdata.type='PERSP' if name in ['court-high-wings','court-stair'] else 'ORTHO';camdata.lens=26
pose('front');scene['revision']=version;scene['local_axes']='X plan right, Y plan up; geographic north not asserted';scene['original_stl_sha256']=hashlib.sha256(raw).hexdigest()
bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.wm.save_as_mainfile(filepath=str(M/'scene.blend'))
chosen=args or [v for v in views if v!='roof-screen-detail']
manifest={'stl_sha256':hashlib.sha256(raw).hexdigest(),'render_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((M/'scene.blend').read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'cycles_samples':scene.cycles.samples,'use_denoising':scene.cycles.use_denoising,'exposure':scene.view_settings.exposure,'threads':1,'views':{}}
for name in chosen:
    pose(name);p=out/(name+'.png');scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    manifest['views'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':views[name]}
(out/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
