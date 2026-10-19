"""Rebuild the editable display scene from canonical colored mesh arrays.
Blender 4.3.2+. Source photo pixels are neither read nor embedded.
Use -- --samples 64 --views front,rear,top,exploded. No changes to STL/geometry.json.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
def linear(v):
 c=v/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 ap=argparse.ArgumentParser();ap.add_argument('--samples',type=int,default=64);ap.add_argument('--views',default='front,rear,top,exploded');a=ap.parse_args(args)
 d=json.loads((ROOT/'geometry.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
 scene.name='Chong-De bounded seven-column entrance section';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
 scene['scope']=d['source_scope']
 scene['appearance_materials']=len(d['materials']);scene['tool_mapping']='None; surface colors are not a validated print profile.'
 mats=[]
 for p in d['materials']:
  h=p['srgb'];rgb=[linear(int(h[j:j+2],16)) for j in [1,3,5]];mat=bpy.data.materials.new(p['id']);mat.use_nodes=True;node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*rgb,1);node.inputs['Roughness'].default_value=.68;mat.diffuse_color=(*rgb,1);mat['approximate_srgb_hex']=h;mat['interpretation']=p['interpretation'];mats.append(mat)
 objects=[];meshes={};lookup={p['id']:p for p in d['parts']}
 for part in d['parts']:
  mesh=bpy.data.meshes.new(part['id']);mesh.from_pydata(part['vertices'],[],part['triangles']);mesh.update()
  for m in mats:mesh.materials.append(m)
  for poly,index in zip(mesh.polygons,part['material_indices']):poly.material_index=index
  meshes[part['id']]=mesh
 for inst in d['instances']:
  part=lookup[inst['prototype']];obj=bpy.data.objects.new(inst['id'],meshes[part['id']]);scene.collection.objects.link(obj);obj.matrix_world=Matrix(inst['transform']);obj['print_geometry']=True;obj['source_STL']=part['stl'];obj['prototype_id']=part['id'];objects.append(obj)
 # Explicit render-only ground, excluded from all print and 3MF assets.
 bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.04));floor=bpy.context.object;floor.name='StudioGround_RENDER_ONLY';floor['print_geometry']=False
 m=bpy.data.materials.new('StudioGround_RENDER_ONLY');m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.74,.76,.78,1);n.inputs['Roughness'].default_value=.9;floor.data.materials.append(m)
 world=bpy.data.worlds.new('NeutralStudio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.82,.88,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7;scene.world=world
 for name,loc,power,size in [('Key',(-90,-120,190),500000,130),('Fill',(140,-40,140),250000,110),('Rim',(-60,110,150),350000,100)]:
  light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=loc;aim(obj,(0,0,55))
 camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_end=5000;camdata.lens=50
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=a.samples;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=6
 scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
 scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=-1.05;scene.view_settings.gamma=1
 bpy.context.preferences.filepaths.save_version=0
 views={'front':((20,-245,100),(0,-10,26),181),'rear':((-100,225,115),(0,-10,26),181),'top':((45,-90,280),(0,-10,22),181),'exploded':((90,-240,135),(0,-7,39),208)}
 # Check every requested view before spending render time on any view.
 for name in a.views.split(','):
  for obj,p in zip(objects,d['instances']):obj.matrix_world=Matrix(p['transform'])
  if name=='exploded':
   objects[1].location.y+=22;objects[1].location.z+=8;objects[2].location.z+=30;
   for obj in objects[3:]:obj.location.z+=10
  loc,target,scale=views[name];cam.location=loc;aim(cam,target);camdata.ortho_scale=scale;bpy.context.view_layer.update()
  coords=[world_to_camera_view(scene,cam,obj.matrix_world@v.co) for obj in objects for v in obj.data.vertices]
  margins=[min(v.x for v in coords),min(v.y for v in coords),1-max(v.x for v in coords),1-max(v.y for v in coords)];assert min(margins)>.015,(name,margins)
 records=[]
 for name in a.views.split(','):
  for obj,p in zip(objects,d['instances']):obj.matrix_world=Matrix(p['transform'])
  if name=='exploded':
   objects[1].location.y+=22;objects[1].location.z+=8;objects[2].location.z+=30;
   for obj in objects[3:]:obj.location.z+=10
  loc,target,scale=views[name];cam.location=loc;aim(cam,target);camdata.ortho_scale=scale;bpy.context.view_layer.update()
  coords=[world_to_camera_view(scene,cam,obj.matrix_world@v.co) for obj in objects for v in obj.data.vertices]
  margins=[min(v.x for v in coords),min(v.y for v in coords),1-max(v.x for v in coords),1-max(v.y for v in coords)];assert min(margins)>.015,(name,margins)
  scene.render.filepath=str(ROOT/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True);records.append({'view':name,'resolution':[1400,1000],'samples':a.samples,'camera_margin':margins,'camera_location':list(loc),'target':list(target),'ortho_scale':scale})
 for obj,p in zip(objects,d['instances']):obj.matrix_world=Matrix(p['transform'])
 loc,target,scale=views['front'];cam.location=loc;aim(cam,target);camdata.ortho_scale=scale;scene.render.filepath='//previews/front.png'
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='FILE_BROWSER':
    for space in area.spaces:
     if getattr(space,'params',None):space.params.directory=b'//'
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene.blend'))
 existing=ROOT/'qa/render-manifest.json'
 if existing.exists():
  previous=json.loads(existing.read_text());new={x['view']:x for x in records};records=[new.pop(v['view'],v) for v in previous['views']]+list(new.values())
 (ROOT/'qa/render-manifest.json').write_text(json.dumps({'Blender':bpy.app.version_string,'geometry_sha256':hashlib.sha256((ROOT/'geometry.json').read_bytes()).hexdigest(),'model_meshes':10,'unique_prototype_meshes':4,'display_materials':len(d['materials']),'render_only_meshes':1,'views':records,'original_photo_pixels_embedded':False,'visual_inspection_pending':True,'PNG_metadata_removal_pending':True},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
