#!/usr/bin/env python3
"""Render the one final union mesh; store authored construction parts separately with source evidence."""
import bpy,json,pathlib,sys,argparse,math
import numpy as np
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--views',default='');p.add_argument('--no-render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else [])
r=a.out;data=np.load(r/'mesh-data.npz');info=json.loads((r/'editable-parts.json').read_text());parts=json.loads((r/'construction-parts.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001
mats=[]
for d in info['palette']:
 c=[int(d['hex'][i:i+2],16)/255 for i in(1,3,5)];c=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in c];m=bpy.data.materials.new(d['name']);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.78;m['source_evidence']=d['evidence'];mats.append(m)
def addmesh(name,v,f,coll):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);coll.objects.link(o);return o
ob=addmesh('Lishan Jesus Church surveyed exterior2016-12',data['vertices'].tolist(),data['faces'].tolist(),s.collection)
for m in mats:ob.data.materials.append(m)
for poly,mi in zip(ob.data.polygons,data['materials']):poly.material_index=int(mi)
ob['scope']='December2016 Appendix9 surveyed church exterior with two wings, front bell tower and roof cupola; not historicalplans or reuseproposal. No sourceimages, fullinterior, trialprint or safetyclaim.'
ob['units']='Modelmm;5mm/source metre,nominal1:200.'
ob['coordinate_frame']='Localx front-view left-to-right,y front-to-rear; notgeoreferenced.'
c=bpy.data.collections.new('EDITABLE authored parts - pre-union overlaps, hidden');s.collection.children.link(c)
for pt in parts:
 q=addmesh(pt['name'],pt['vertices'],pt['faces'],c);q.data.materials.append(mats[pt['material']]);q['evidence']=pt['evidence'];q['construction_operation']=pt.get('operation','union_add');q.hide_render=True;q.hide_set(True)
c.hide_render=True;c.hide_viewport=True
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.90,.92,.94,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.seed=0;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=1800;s.render.resolution_y=950;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.use_stamp=False
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
for name,loc,pow,size in [('Key',(-90,-130,290),300000,170),('Fill',(220,240,250),200000,170)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=pow;d.shape='DISK';d.size=size;q=bpy.data.objects.new(name,d);s.collection.objects.link(q);q.location=loc;q.rotation_euler=(Vector((0,65,45))-q.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO'
views=[('front',(-210,-235,170),(0,65,40),390,'Whole church front and left side'),('rear',(240,330,180),(0,65,40),390,'Whole church rear and right side'),('front_elevation',(0,-500,48),(0,65,48),250,'Whole front elevation'),('rear_elevation',(0,550,48),(0,65,48),250,'Whole rear elevation'),('left_elevation',(-500,65,48),(0,65,48),280,'Whole left elevation'),('right_elevation',(500,65,48),(0,65,48),280,'Whole right elevation'),('top',(0,65,550),(0,65,0),360,'Whole roof and cross footprint'),('tower_detail',(-120,-160,100),(0,-8,50),165,'DETAIL bell tower and open porch; intentionally cropped'),('rear_detail',(170,300,150),(0,110,35),200,'DETAIL rear windows, wing and roof cupola; intentionally cropped')]
(r/'previews').mkdir(exist_ok=True)
for name,loc,target,scale,label in views:
 if a.views and name not in a.views.split(','):continue
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
 if name=='front':s.render.filepath='//previews/front.png';bpy.ops.wm.save_as_mainfile(filepath=str(r/'scene.blend'),compress=True)
 if not a.no_render:s.render.filepath=str(r/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
(r/'render-manifest.json').write_text(json.dumps({'renderer':'Blender Cycles','samples':40,'seed':0,'rendered_mesh':'mesh-data.npz','reference_images_embedded':0,'views':[{'name':n,'camera':l,'target':t,'ortho_scale':sc,'label':la,'elevation_degrees':math.degrees(math.atan2(l[2]-t[2],math.hypot(l[0]-t[0],l[1]-t[1])))}for n,l,t,sc,la in views],'axes':'Localx front-view left-to-right,y front-to-rear; notgeoreferenced.'},ensure_ascii=False,indent=2))
# Preserve pixels while removing host paths and timestamps from PNG metadata.
import runpy
normalizer=runpy.run_path(str(pathlib.Path(__file__).with_name('normalize_previews.py')))
for png in (r/'previews').glob('*.png'):normalizer['normalize'](png)
