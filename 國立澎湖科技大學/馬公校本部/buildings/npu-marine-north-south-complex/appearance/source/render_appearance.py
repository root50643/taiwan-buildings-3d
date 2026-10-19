"""Build an editable five-material Blender scene from the exact 3MF surface data.

blender -b --threads 6 --python appearance/source/render_appearance.py
Four views only. No reference photos/textures or printer settings are embedded.
"""
from pathlib import Path
import hashlib,json,os,zipfile,xml.etree.ElementTree as ET
import bpy
from mathutils import Matrix,Vector

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parent
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def linear(s):return s/12.92 if s<=.04045 else ((s+.055)/1.055)**2.4
def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
    scene['purpose']='Editable photo-informed APPEARANCE master; surface colors are not printer tool mappings.'
    scene['source_limits']='Undated photos; 2018 historical campus configuration. No measured pigment, real scale, current-as-built or physical-print claim.'
    scene['geometry']='8 original STL prototypes / 10 physical instances; no added room, roof equipment, texture photo or remodeled geometry.'
    pal=json.loads((OUT/'palette.json').read_text())['materials'];mats=[]
    for p in pal:
        m=bpy.data.materials.new(p['id']);rgb=[linear(int(p['srgb'][i:i+2],16)/255) for i in [1,3,5]]+[1.0]
        m.diffuse_color=rgb;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=rgb
        bs.inputs['Roughness'].default_value=.4 if 'glaz' in p['id'] or 'window' in p['id'] else .75
        m['approximate_srgb']=p['srgb'];m['not_a_printer_tool']=True;mats.append(m)
    with zipfile.ZipFile(OUT/'npu-appearance-ASSEMBLED.3mf') as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
    resources={int(o.get('id')):o for o in root.findall('m:resources/m:object',NS)}
    assembly=json.loads((ROOT/'assembly.json').read_text())['parts'];components=resources[100].findall('m:components/m:component',NS)
    objects=[]
    for p,c in zip(assembly,components):
        meshxml=resources[int(c.get('objectid'))].find('m:mesh',NS)
        verts=[[float(v.get(k)) for k in ['x','y','z']] for v in meshxml.findall('m:vertices/m:vertex',NS)]
        triangles=meshxml.findall('m:triangles/m:triangle',NS);faces=[[int(t.get(k)) for k in ['v1','v2','v3']] for t in triangles]
        T=Matrix(p['assembly_transform']);vertices=[tuple(T@Vector(v)) for v in verts]
        mesh=bpy.data.meshes.new(p['id']);mesh.from_pydata(vertices,[],faces);mesh.update()
        ob=bpy.data.objects.new(p['id'],mesh);scene.collection.objects.link(ob);objects.append(ob)
        ob['source_stl']=p['stl'];ob['source_sha256']=p['sha256'];ob['physical_fit_tested']=False
        for m in mats:mesh.materials.append(m)
        for face,tri in zip(mesh.polygons,triangles):face.material_index=int(tri.get('p1'))
    world=bpy.data.worlds.new('Neutral world');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.74,.79,.84,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
    for idx,(loc,power,size) in enumerate([((10,-100,250),1100000,180),((210,200,200),700000,180),((-150,120,100),500000,150)]):
        light=bpy.data.lights.new('Softbox '+str(idx),'AREA');light.energy=power;light.shape='DISK';light.size=size
        ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=loc;aim(ob,(60,76,13))
    data=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.clip_end=3000
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False
    scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.35
    target=(60,76,13)
    views={'front':((245,290,190),target,270),'rear':((-190,-200,180),target,275),'top':((59,79,420),(59,79,0),246),'exploded':((245,290,240),(60,76,35),290)}
    (OUT/'previews').mkdir(exist_ok=True)
    for name,(loc,t,scale) in views.items():
        for ob in objects:ob.location.z=({'02-north-upper':20,'04-hall-roof':12,'05-bridge-tray':8,'06-bridge-lid':22}.get(ob.name,0) if name=='exploded' else 0)
        cam.location=loc;aim(cam,t);data.ortho_scale=scale
        scene.render.filepath=str(OUT/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
    for ob in objects:ob.location.z=0
    cam.location=views['front'][0];aim(cam,target);data.ortho_scale=270;scene.render.filepath='//previews/front.png'
    for screen in bpy.data.screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
    os.chdir(OUT);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'),compress=False)
    print('Saved geometry-preserving appearance scene and four previews.')
if __name__=='__main__':main()
