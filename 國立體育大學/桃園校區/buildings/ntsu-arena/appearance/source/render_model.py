#!/usr/bin/env python3
"""Render the actual editable material mesh; no textures or added geometry."""
from pathlib import Path
import bpy,json,argparse,sys,struct,collections
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sys
sys.dont_write_bytecode=True
from common import *
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=a.out
D=load(a.stl,root/'parameters.json',root/'palette.json');(root/'previews').mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
mesh=bpy.data.meshes.new('Exact original 30648 triangles');mesh.from_pydata(D['vertices'],[],D['faces']);mesh.update()
obj=bpy.data.objects.new('NTSU Arena — limited material-family illustration',mesh);bpy.context.scene.collection.objects.link(obj)
for name in ORDER:
 d=D['palette'][name];c=(*srgb_linear(d['srgb8']),1);m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=d['roughness'];m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=d['metallic'];m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=d['alpha'];m.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=0.0;m['meaning']=d['meaning'];mesh.materials.append(m)
# Never rely on importer polygon indices: map EVERY face by oriented vertex signature.
ids=mapping(D['signatures'],[[tuple(mesh.vertices[v].co)for v in f.vertices]for f in mesh.polygons])
for f,i in zip(mesh.polygons,ids):f.material_index=D['materials'][i];f.use_smooth=False
attr=mesh.attributes.new('original_stl_triangle_index','INT','FACE')
for v,i in zip(attr.data,ids):v.value=i
obj['source_mesh']='../model.stl';obj['source_stl_sha256']=SHA;obj['scope']='既有近似幾何上的有限材料色系示意；非精準原色或現況重建。';obj['unknown']='6786 original triangles neutral; neutral does not assert actual gray material';obj['units']='Raw coordinates millimeters; no building survey scale claimed'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if False else 'None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.image_settings.compression=15;scene.render.film_transparent=False;scene.render.use_stamp=False
for name,loc,power,size in [('Key',(-110,-140,220),150000,180),('Fill',(150,30,140),70000,140)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,25))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Appearance camera');cam=bpy.data.objects.new('Appearance camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO'
views=[('front',(-70,-260,120),(0,0,24)),('front-right',(150,-225,135),(0,0,24)),('elevation',(0,-300,31),(0,0,31)),('rear',(130,230,125),(0,0,24)),('left',(-300,0,31),(0,0,31)),('right',(300,0,31),(0,0,31)),('top',(0,0,320),(0,0,0)),('underside',(150,-225,-150),(0,0,25)),('rim-detail',(-45,-165,79),(0,-55,35))]
def aim(loc,target,detail=False):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();inv=cam.rotation_euler.to_matrix().transposed();v=[inv@(obj.matrix_world@Vector(c)-cam.location)for c in obj.bound_box];width=max(q.x for q in v)-min(q.x for q in v);height=max(q.y for q in v)-min(q.y for q in v);camdat.ortho_scale=70 if detail else max(width,height*1200/900)*1.15

def strip(path):
 raw=path.read_bytes();out=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack_from('>I',raw,i)[0];tag=raw[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=raw[i:i+n+12]
  i+=n+12
 path.write_bytes(out)
manifest=[]
for name,loc,target in views:
 aim(loc,target,name=='rim-detail');manifest.append({'name':name,'camera_model_mm':loc,'target_model_mm':target,'orthographic_scale_mm':camdat.ortho_scale})
 if a.views and name not in a.views.split(','):continue
 scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip(root/'previews'/f'{name}.png')
aim(views[0][1],views[0][2]);bpy.context.view_layer.objects.active=obj;obj.select_set(True);cam.select_set(False)
for ss in bpy.data.scenes:
 limit=ss.render.bl_rna.properties['filepath'].length_max;ss.render.filepath='_'*(limit-1);ss.render.filepath='//previews/front.png'
 if ss.sequence_editor is not None:ss.sequence_editor_clear()
 limit=ss.render.bake.bl_rna.properties['filepath'].length_max;ss.render.bake.filepath='_'*(limit-1);ss.render.bake.filepath='//'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER'and space.params:
    limit=space.params.bl_rna.properties['directory'].length_max;space.params.directory=b'_'*(limit-1);space.params.directory=b'//'
    limit=space.params.bl_rna.properties['filename'].length_max;space.params.filename='_'*(limit-1);space.params.filename=''
   if space.type=='VIEW_3D':space.shading.color_type='MATERIAL';space.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'ntsu-arena-appearance.blend'))
dump(root/'qa/render-manifest.json',{'blender_version':bpy.app.version_string,'engine':'Cycles CPU','samples':32,'seed':0,'denoising':False,'dimensions_px':[1200,900],'images_are_actual_output_mesh':True,'image_textures':0,'views':manifest,'orientation':'Front is negative Y, not a surveyed geographic bearing. Only dome, horizontal rim lip and front glazing colored; rear glazing, vertical ring, V columns, raised bands, entrances and base are neutral. y=0 is evidence scope, not a physical color seam. Detail changes camera only.'})
