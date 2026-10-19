"""Render exactly the supplied STL; cameras and lighting add no building features."""
from pathlib import Path
import json,hashlib,os,math,re
import bpy
from mathutils import Vector
import trimesh
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'previews/v1';OUT.mkdir(parents=True,exist_ok=True)
STL=ROOT/'models/v1/model.stl'
t=trimesh.load_mesh(STL,process=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mesh=bpy.data.meshes.new('exact_STL');mesh.from_pydata(t.vertices.tolist(),[],t.faces.tolist());mesh.update()
obj=bpy.data.objects.new('NIU_Cultivation_Hall_candidate_exact_STL',mesh);bpy.context.collection.objects.link(obj)
palette=[('plaster',(0.73,0.72,0.65,1)),('grey tile',(0.29,0.32,0.33,1)),('wood',(0.20,0.085,0.035,1)),('glass recess',(0.035,0.065,0.065,1)),('stone plinth',(0.36,0.37,0.34,1)),('base',(0.50,0.47,0.40,1))]
for name,col in palette:
    mat=bpy.data.materials.new(name);mat.diffuse_color=col;mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=col;bs.inputs['Roughness'].default_value=0.72
    obj.data.materials.append(mat)
for p in obj.data.polygons:
    x,y,z=p.center;n=p.normal;idx=0
    if z<2.41:idx=5
    elif z<5.7:idx=4
    if z>36.35 and n.z>0.2:idx=1
    if y<-37.6 and z>32.3 and n.z>0.2:idx=1
    if 36.2<z<39 and abs(y)>37.3 and n.z<0:idx=2
    if y<-58.4 and 2.4<z<28.5 and abs(x)<17.6:idx=3 if y>-59 else 2
    for cx in [-35.5,35.5]:
        if abs(x-cx)<8.05 and 8<z<30.05 and -37.6<y<-36.4:idx=3 if y>-37.0 else 2
    for cx in [-63,-53,53,63]:
        allowed=z<=26.75 or (x-cx)**2+(z-26.75)**2<=3.3**2
        if abs(x-cx)<3.3 and 7<z<30.1 and -37.6<y<-36.4 and allowed:idx=3 if y>-37.0 else 2
    if -24.1<x<-23.1 and -54<y<-44 and 13.4<z<22.6:idx=3 if x>-23.7 else 2
    if -61.95<y<-61.0 and x*x+(z-39)**2<8.0:idx=3 if y>-61.5 else 2
    for cy in [-18,-5]:
        if -75.1<x<-74.0 and abs(y-cy)<3.8 and 8<z<30.1:idx=3 if x>-74.6 else 2
    p.material_index=idx
obj['source_stl_sha256']=hashlib.sha256(STL.read_bytes()).hexdigest()
obj['units']='mm';obj['status']='Review candidate; no physical print'
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24
# Coordinates are millimetres. Set display/physical units; do not scale any mesh or object.
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=0.001
scene.unit_settings.length_unit='MILLIMETERS'
scene.render.resolution_x=1200;scene.render.resolution_y=820;scene.render.resolution_percentage=100
scene.world.color=(0.28,0.28,0.28)
scene.view_settings.view_transform='AgX'
bpy.ops.object.light_add(type='AREA',location=(-110,-130,220));bpy.context.object.data.energy=650000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=180
bpy.ops.object.light_add(type='AREA',location=(130,70,150));bpy.context.object.data.energy=400000;bpy.context.object.data.size=150
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-0.12));floor=bpy.context.object;floor.name='render_floor_not_model'
mat=bpy.data.materials.new('background');mat.diffuse_color=(0.83,0.83,0.79,1);floor.data.materials.append(mat)
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=205;scene.camera=camera
views={'front':((0,-280,120),(0,-8,20),195),'oblique':((-210,-260,180),(0,-8,20),205),'rear':((210,250,175),(0,-6,20),205),'top':((0,-0.1,350),(0,-10,0),190),'left':((-280,-70,125),(0,-8,20),190),'entry-detail':((-100,-190,105),(0,-42,27),105)}
for name,(pos,target,scale) in views.items():
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
floor.hide_render=True
scene.render.filepath='//../../previews/v1/entry-detail.png'
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/v1/scene.blend'),compress=False)
# No photographic image datablocks are used. Clear obsolete JPG names in saved UI/cache buffers.
saved_scene=ROOT/'models/v1/scene.blend'
saved_scene.write_bytes(re.sub(rb'[A-Za-z0-9_.-]+\.jpg',lambda m:b'\0'*len(m.group()),saved_scene.read_bytes(),flags=re.I))
(OUT/'render-manifest.json').write_text(json.dumps({'stl_sha256':hashlib.sha256(STL.read_bytes()).hexdigest(),'bpy':bpy.app.version_string,'views':list(views),'geometry':'Exact STL reloaded; only non-model render floor, cameras and lights added; mesh/object coordinates are not scaled','model_vertices':len(t.vertices),'model_faces':len(t.faces),'scene_units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,'length_unit':scene.unit_settings.length_unit},'coordinate_unit':'millimetre'},indent=2)+'\n')
