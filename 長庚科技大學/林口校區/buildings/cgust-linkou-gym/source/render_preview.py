"""CPU Cycles render of unchanged original STL triangles; no reference-image textures."""
import bpy,json,struct,hashlib,math,sys,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
version=args.pop(0) if args else 'v0';M=R/'models'/version;out=R/'previews'/version;out.mkdir(parents=True,exist_ok=True)
p=json.loads((M/'parameters.json').read_text());base=p['base_thickness_mm']
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
obj=bpy.data.objects.new('CGUST Linkou gym proportional exterior prototype',mesh);bpy.context.collection.objects.link(obj)
obj['stl_sha256']=hashlib.sha256(raw).hexdigest();obj['geometry_policy']='No repair, modifiers, textures from references or substitute geometry'
palette=[('wall',(.55,.58,.57)),('annex',(.32,.34,.33)),('roof',(.70,.73,.72)),('base',(.20,.24,.23)),('paving',(.48,.49,.46)),('glass',(.11,.19,.20)),('canopy',(.57,.62,.63)),('bracket',(.34,.08,.12))]
lookup={n:i for i,(n,c) in enumerate(palette)}
for name,col in palette:
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;nd=nodes.get('Principled BSDF');nd.inputs['Base Color'].default_value=(*col,1);nd.inputs['Roughness'].default_value=.65
    if name=='glass':nd.inputs['Roughness'].default_value=.32;nd.inputs['Metallic'].default_value=.12
    obj.data.materials.append(mat)
regions=json.loads((M/'color-regions.json').read_text())
for f in mesh.polygons:
    x,y,z=f.center
    for q in regions:
        if 'plane_band' in q:
            spec=q['plane_band'];normal=Vector(spec['outward_normal']);point=Vector(spec['point_mm']);lo,hi=spec['z_bounds_mm']
            hit=f.normal.dot(normal)>=spec['minimum_normal_dot'] and all(abs((mesh.vertices[vi].co-point).dot(normal))<=spec['plane_tolerance_mm'] and lo-1e-4<=mesh.vertices[vi].co.z<=hi+1e-4 for vi in f.vertices)
            if hit and 'y_bounds_mm' in spec:
                ymin,ymax=spec['y_bounds_mm'];hit=all(ymin<=mesh.vertices[vi].co.y<=ymax for vi in f.vertices)
        elif 'bounds_mm' in q:
            a,b,c,d,e,g=q['bounds_mm'];hit=a-1e-4<=x<=b+1e-4 and c-1e-4<=y<=d+1e-4 and e-1e-4<=z<=g+1e-4
        else:
            a,b,cy,cz,r=q['cylinder_x'];hit=a<=x<=b and (y-cy)**2+(z-cz)**2<=r*r
        if hit:f.material_index=lookup[q['material']]
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=p['render_samples'];scene.cycles.use_denoising=False;scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=0;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
scene.render.threads_mode='FIXED';scene.render.threads=1;scene.render.resolution_x=1000;scene.render.resolution_y=780;scene.render.resolution_percentage=p['render_resolution_percent']
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.78,.78,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=1.0
scene.view_settings.exposure=0;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for name,energy,rot in [('Key',2.6,(50,-35,-40)),('Fill',.45,(-20,25,140))]:
    data=bpy.data.lights.new(name,'SUN');data.energy=energy;data.angle=.2;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.rotation_euler=tuple(math.radians(v) for v in rot)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_end=2000
views={
 'front':((-235,-290,155),(0,80,24),290),
 'rear':((235,355,165),(0,90,24),290),
 'east':((380,80,100),(0,80,24),290),
 'west':((-380,80,100),(0,80,24),290),
 'south':((0,430,85),(0,80,24),240),
 'north':((0,-340,85),(0,80,24),240),
 'top':((0,82,500),(0,82,0),310),
 'courtyard-gallery':((-105,10,48),(-64,45,22),150),
 'courtyard-arcade':((-95,245,110),(0,163,27),320)
}
camera_specs={name:{'projection':'PERSP' if name in {'courtyard-gallery','courtyard-arcade'} else 'ORTHO','lens_mm':20 if name in {'courtyard-gallery','courtyard-arcade'} else 50} for name in views}
def pose(name):
    pos,target,scale=views[name];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale;camdata.clip_start=.1
    camdata.type=camera_specs[name]['projection'];camdata.lens=camera_specs[name]['lens_mm']
pose('front');scene['revision']=version;scene['local_axes']=p['local_axes'];scene['original_stl_sha256']=hashlib.sha256(raw).hexdigest()
bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.wm.save_as_mainfile(filepath=str(M/'scene.blend'));shutil.copy2(__file__,M/'render_preview.py')
chosen=args or list(views)
manifest={'stl_sha256':hashlib.sha256(raw).hexdigest(),'render_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((M/'scene.blend').read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'cycles_samples':scene.cycles.samples,'use_denoising':scene.cycles.use_denoising,'exposure':scene.view_settings.exposure,'threads':1,'views':{}}
for name in chosen:
    pose(name);dest=out/(name+'.png');scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True);manifest['views'][name]={'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'camera':views[name],**camera_specs[name]}
(out/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
