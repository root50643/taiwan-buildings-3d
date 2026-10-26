#!/usr/bin/env python3
"""Blender 4.3.2: render unchanged mesh and save editable per-face material scene."""
import bpy,sys,pathlib,argparse,json,struct
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from material_geometry import load_stl,load_materials,bijection
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);root=a.out
(root/'qa').mkdir(exist_ok=True);(root/'previews').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');params=json.loads((root/'parameters.json').read_text());palette=params['palette']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
mesh=bpy.data.meshes.new('Anping exact legacy triangle mesh');mesh.from_pydata(D['vertices'].tolist(),[],D['faces'].tolist());mesh.update();o=bpy.data.objects.new('Anping material upgrade',mesh);scene.collection.objects.link(o)
actual=np.asarray([list(v.co)for v in mesh.vertices])[np.asarray([list(p.vertices)for p in mesh.polygons])];source=load_stl(root/'model.stl')[2];ids=bijection(source,actual);mi=load_materials(root)
attr=mesh.attributes.new('original_stl_triangle_index','INT','FACE')
for poly,index in zip(mesh.polygons,ids):poly.material_index=int(mi[index]);poly.use_smooth=False;attr.data[poly.index].value=int(index)
for q in palette:
 h=q['hex'].lstrip('#');srgb=[int(h[i:i+2],16)/255 for i in (0,2,4)];c=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in srgb]
 m=bpy.data.materials.new(q['id']);m.use_nodes=True;m.diffuse_color=(*c,1);node=m.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(*c,1);node.inputs['Roughness'].default_value=q['roughness'];node.inputs['Metallic'].default_value=0;m['source_evidence']=q['source_evidence'];mesh.materials.append(m)
o['scope']='Existing legacy crop, material-only historical front interpretation: 14 plaster, 2 roof, 142 brick/stair faces. 3460 unknown neutral; no cabin, landing, side, rear or hall paint. Occluded material continuity inferred.'
o['geometry_policy']='Original 3618 STL triangles preserved exactly; editable mesh is not a repaired or newly measured building.'
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
scene.render.engine='CYCLES';scene.cycles.samples=params['render']['samples'];scene.cycles.seed=0;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.use_stamp=False;scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
for name,loc,power,size in [('Key',(-100,-150,210),260000,140),('Fill',(160,70,160),170000,130)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,25))-ob.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO'
views=[('front',(155,-270,190),240,(0,0,47),850),('rear',(-155,270,190),240,(0,0,47),850),('front-elevation',(0,-300,52),170,(0,0,52),900),('rear-elevation',(0,300,52),170,(0,0,52),900),('right-end',(300,0,52),150,(0,0,52),1000),('top',(0,0,300),170,(0,0,0),850)]
framing=[]
def clean_png(path):
 b=path.read_bytes();out=b[:8];at=8
 while at<len(b):
  n=struct.unpack('>I',b[at:at+4])[0];tag=b[at+4:at+8]
  if tag not in(b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=b[at:at+n+12]
  at+=n+12
 path.write_bytes(out)
for name,loc,scale,target,height in views:
 if a.views and name not in a.views.split(','):continue
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.resolution_y=height
 bpy.context.view_layer.update();projected=[world_to_camera_view(scene,cam,o.matrix_world@v.co)for v in mesh.vertices];bounds=[[min(q[i]for q in projected),max(q[i]for q in projected)]for i in range(2)];assert all(lo>=.03 and hi<=.97 for lo,hi in bounds),(name,bounds);framing.append({'name':name,'normalized_xy_bounds':bounds,'minimum_required_frame_margin':.03,'all_vertices_inside_frame':True})
 if name=='front':
  for sc in bpy.data.scenes:sc.render.filepath='_'*(sc.render.bl_rna.properties['filepath'].length_max-1);sc.render.filepath='//previews/front.png'
  for screen in bpy.data.screens:
   for area in screen.areas:
    for space in area.spaces:
     if space.type=='FILE_BROWSER'and space.params:space.params.directory=b'_'*(space.params.bl_rna.properties['directory'].length_max-1);space.params.directory=b'//'
  bpy.ops.wm.save_as_mainfile(filepath=str(root/'scene.blend'),compress=False)
 scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);clean_png(root/'previews'/f'{name}.png')
(root/'qa/render-manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':'Cycles','source_pixels':0,'geometry':'All views render exact whole original mesh with same per-triangle materials. No clipping, texture, facade decoration or extra mesh.','palette':palette,'executed_view_framing':framing,'views':[{'name':n,'camera':l,'scale_mm':s,'target':t,'height':h}for n,l,s,t,h in views]},indent=2)+'\n')
