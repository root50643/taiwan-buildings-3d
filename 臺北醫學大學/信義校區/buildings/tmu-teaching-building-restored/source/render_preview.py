"""CPU Cycles render of unchanged original STL triangles; no reference-image textures."""
import bpy,json,struct,hashlib,math,sys,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
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
obj=bpy.data.objects.new('TMU restored Teaching Building',mesh);bpy.context.collection.objects.link(obj)
obj['stl_sha256']=hashlib.sha256(raw).hexdigest();obj['geometry_policy']='No repair, modifiers, textures from references or substitute geometry'
palette=[('wall',(.61,.60,.54)),('concrete',(.62,.61,.55)),('brick',(.42,.16,.11)),('stone',(.69,.62,.45)),('metal',(.36,.40,.42)),('roof',(.31,.32,.30)),('base',(.23,.27,.29)),('paving',(.53,.54,.52)),('glass',(.115,.19,.21)),('trim',(.76,.75,.68)),('steel',(.17,.23,.24)),('frame',(.34,.39,.40)),('spandrel',(.48,.50,.49)),('stairs',(.45,.43,.40))]
lookup={n:i for i,(n,c) in enumerate(palette)}
for name,col in palette:
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nd=mat.node_tree.nodes.get('Principled BSDF');nd.inputs['Base Color'].default_value=(*col,1);nd.inputs['Roughness'].default_value=.82;obj.data.materials.append(mat)
regions=json.loads((M/'color-regions.json').read_text())
for f in mesh.polygons:
    x,y,z=f.center
    for q in regions:
        a,b,c,d,e,g=q['bounds_mm']
        if a-1e-4<=x<=b+1e-4 and c-1e-4<=y<=d+1e-4 and e-1e-4<=z<=g+1e-4:f.material_index=lookup[q['material']]
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8 if version in ['v0','v1','v2'] else 64;scene.cycles.use_denoising=False;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
scene.render.threads_mode='FIXED';scene.render.threads=1;scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=70 if version in ['v0','v1','v2'] else 100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.78,.78,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.view_settings.exposure=0;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for name,energy,rot in [('Key',2.1,(50,-35,-40)),('Fill',.7,(-20,25,140))]:
    data=bpy.data.lights.new(name,'SUN');data.energy=energy;data.angle=.2;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.rotation_euler=tuple(math.radians(v) for v in rot)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_end=2000
views={
 'front':((265,-190,140),(102.5,22,20),240),
 'rear':((270,210,140),(102.5,23,20),240),
 'west':((-250,20,22),(20,20,22),100),
 'east':((450,20,22),(180,20,22),100),
 'south':((102.5,-300,22),(102.5,20,22),230),
 'north':((102.5,350,22),(102.5,20,22),230),
 'top':((102.5,24,450),(102.5,24,0),230),
 'entry-detail':((120,-130,45),(102.5,10,10),88),
 'roof-detail':((270,175,135),(156,32,24),120)
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
