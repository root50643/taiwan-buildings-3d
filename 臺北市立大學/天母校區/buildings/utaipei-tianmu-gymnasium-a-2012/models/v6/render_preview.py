"""Render original STL triangles, original procedural colours, no photo textures."""
import bpy,json,struct,hashlib,math,sys,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'source'))
import ast
_build_ast=ast.parse((R/'source/build_model.py').read_text())
_wave_node=next(n for n in _build_ast.body if isinstance(n,ast.FunctionDef) and n.name=='wave_height')
exec(compile(ast.Module(body=[_wave_node],type_ignores=[]),'wave_height','exec'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
version=args.pop(0) if args else 'v0';M=R/'models'/version;out=R/'previews'/version;out.mkdir(parents=True,exist_ok=True)
p=json.loads((M/'parameters.json').read_text());s=p['scale_mm_per_estimated_m'];base=p['base_thickness_mm']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
raw=(M/'model.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];verts=[];faces=[];index={}
for i in range(count):
    coords=struct.unpack_from('<9f',raw,84+50*i+12);face=[]
    for j in range(3):
        v=tuple(coords[j*3:j*3+3])
        if v not in index:index[v]=len(verts);verts.append(v)
        face.append(index[v])
    faces.append(face)
mesh=bpy.data.meshes.new('Original STL unchanged triangles');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('UTaipei Tianmu Gymnasium A original exterior',mesh);bpy.context.collection.objects.link(obj)
obj['stl_sha256']=hashlib.sha256(raw).hexdigest();obj['geometry_policy']='No repair, modifiers, photographic textures or substitute geometry'
palette=[('wall',(.73,.66,.42)),('base',(.26,.29,.30)),('paving',(.51,.53,.53)),('glass',(.15,.28,.30)),('door',(.11,.19,.21)),('pink',(.69,.36,.41)),('silver',(.49,.55,.59)),('frame',(.43,.49,.49)),('clerestory',(.23,.30,.32)),('shutter',(.38,.41,.41)),('stairs',(.46,.49,.48))]
lookup={n:i for i,(n,c) in enumerate(palette)}
for name,col in palette:
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nd=mat.node_tree.nodes.get('Principled BSDF');nd.inputs['Base Color'].default_value=(*col,1);nd.inputs['Roughness'].default_value=.62 if name=='silver' else .85;nd.inputs['Metallic'].default_value=.30 if name=='silver' else 0;obj.data.materials.append(mat)
    if name in ['wall','silver']:
        # Procedural cosmetic seams only. Not measured physical panel inventory.
        nt=mat.node_tree;geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);outputs=[]
        for axis,pitch in ([('X',3.2),('Y',3.2)] if name=='silver' else [('X',2.5),('Y',2.5),('Z',2.7)] if name=='wall' else [('X',2.0),('Y',2.0)]):
            mod=nt.nodes.new('ShaderNodeMath');mod.operation='PINGPONG';mod.inputs[1].default_value=pitch/2;nt.links.new(sep.outputs[axis],mod.inputs[0])
            comp=nt.nodes.new('ShaderNodeMath');comp.operation='LESS_THAN';comp.inputs[1].default_value=.035;nt.links.new(mod.outputs[0],comp.inputs[0]);outputs.append(comp.outputs[0])
        combined=outputs[0]
        for other in outputs[1:]:
            mx=nt.nodes.new('ShaderNodeMath');mx.operation='MAXIMUM';nt.links.new(combined,mx.inputs[0]);nt.links.new(other,mx.inputs[1]);combined=mx.outputs[0]
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*col,1);mix.inputs[2].default_value=(*(tuple(v*.74 for v in col) if name!='clerestory' else (.50,.55,.55)),1);nt.links.new(combined,mix.inputs[0]);nt.links.new(mix.outputs[0],nd.inputs['Base Color'])
regions=json.loads((M/'color-regions.json').read_text())
for f in mesh.polygons:
    x,y,z=f.center;xm,ym,zm=x/s,y/s,(z-base)/s-.5
    for q in regions:
        a,b,c,d,e,g=q['bounds_mm']
        if a-1e-4<=x<=b+1e-4 and c-1e-4<=y<=d+1e-4 and e-1e-4<=z<=g+1e-4:f.material_index=lookup[q['material']]
    if 21.5<zm<28.4 and abs(xm)<14.61 and abs(ym)<10.66 and abs(f.normal.z)<.15:
        f.material_index=lookup['clerestory']
    if zm<13.82+.01 and zm>8.0:
        for side,uv,facematch in [('west',ym,-43.6<xm<-43.0),('east',ym,43.0<xm<43.6),('south',xm,-34.4<ym<-33.8),('north',xm,33.8<ym<34.4)]:
            if facematch and zm>=wave_height(uv,side)-.03:f.material_index=lookup['pink']
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16 if version in ['v0','v1'] else 64;scene.cycles.use_denoising=False;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
scene.render.threads_mode='FIXED';scene.render.threads=1;scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.86,.89,.92,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
scene.view_settings.exposure=.0;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for name,energy,rot in [('Key',2.1,(50,-35,-40)),('Fill',.35,(-20,25,140))]:
    data=bpy.data.lights.new(name,'SUN');data.energy=energy;data.angle=.2;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.rotation_euler=tuple(math.radians(v) for v in rot)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_end=2000
views={
 'front':((-260,-220,170),(-7,0,25),245),
 'rear':((245,210,160),(-7,0,25),245),
 'west':((-350,0,31),(-4,0,31),198),
 'east':((350,0,31),(0,0,31),198),
 'south':((-11,-350,31),(-11,0,31),230),
 'north':((-11,350,31),(-11,0,31),230),
 'top':((-11,0,450),(-11,0,0),224),
 'entry-detail':((-230,-90,70),(-90,0,17),135),
 'roof-detail':((160,-145,160),(0,0,43),155)
}
def pose(name):
    pos,target,scale=views[name];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale;camdata.clip_start=.1
pose('front');scene['revision']=version;scene['local_axes']=p['local_axes'];scene['original_stl_sha256']=hashlib.sha256(raw).hexdigest()
bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.wm.save_as_mainfile(filepath=str(M/'scene.blend'));shutil.copy2(__file__,M/'render_preview.py')
chosen=args or list(views)
manifest={'stl_sha256':hashlib.sha256(raw).hexdigest(),'render_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((M/'scene.blend').read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'cycles_samples':scene.cycles.samples,'use_denoising':scene.cycles.use_denoising,'exposure':scene.view_settings.exposure,'threads':1,'views':{}}
for name in chosen:
    pose(name);dest=out/(name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);manifest['views'][name]={'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'camera':views[name]}
(out/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
