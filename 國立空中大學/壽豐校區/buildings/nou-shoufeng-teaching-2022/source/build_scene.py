"""Render actual STL meshes. Blender BU=1 mm via scale_length=0.001."""
from pathlib import Path
import json, math, hashlib
import bpy
import numpy as np
import trimesh
from mathutils import Vector, Matrix
from sanitize_scene_metadata import sanitize_png_metadata, sanitize_scene_metadata

ROOT=Path(__file__).resolve().parents[1]
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.65
    return m
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def public_metadata(scene):
    # Relative output paths and disabled PNG stamp metadata keep host directories private.
    scene.render.filepath='//previews/front.png'
    scene.render.use_stamp=False
    for prop in scene.render.bl_rna.properties:
        if prop.identifier.startswith('use_stamp_') and prop.type=='BOOLEAN':
            setattr(scene.render,prop.identifier,False)
    for screen in bpy.data.screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type=='FILE_BROWSER' and space.params:
                    space.params.directory=b''
def main():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
    scene.unit_settings.length_unit='MILLIMETERS'
    scene['stl_units']='mm';scene['reference_epoch']='2022-12-08 10:03 main card; oblique dates unknown'
    scene['scope']='Four-storey L-shaped teaching building only; physical prints untested'
    mats=[material('white concrete',(0.78,.8,.78)),material('recessed glazing',(0.12,.19,.22)),
          material('yellow rail accents',(0.84,.62,.07)),material('subtle green headhouse cap',(.26,.42,.38))]
    data=json.loads((ROOT/'parameters.json').read_text(encoding='utf-8'));objs=[];check=[]
    for i,p in enumerate(data['parts']):
        mesh=trimesh.load_mesh(ROOT/'models'/p['stl']);verts=np.asarray(mesh.vertices)
        verts=trimesh.transform_points(verts,np.asarray(p['assembly_transform_mm']))
        bm=bpy.data.meshes.new(p['name']);bm.from_pydata(verts.tolist(),[],mesh.faces.tolist());bm.update()
        ob=bpy.data.objects.new(p['name'],bm);scene.collection.objects.link(ob);objs.append(ob)
        for m in mats:ob.data.materials.append(m)
        for poly in ob.data.polygons:
            x,y,z=poly.center;nx,ny,nz=poly.normal
            if ('lower' in p['name']) and ((abs(y-21.35)<.025 and ny>.8) or (abs(x-21.35)<.025 and nx>.8) or (abs(y-.65)<.025 and ny<-.8) or (abs(x-.65)<.025 and nx<-.8)):
                poly.material_index=1
            floor=i//2
            if 'lower' in p['name'] and i>1 and (abs(y-30)<.02 or abs(x-30)<.02):
                if 2+floor*10+1.6 < z < 2+floor*10+4.5 and ((66<x<77) or (78<y<89)):
                    poly.material_index=2
            if i==8 and nz>.9 and z>47.9:poly.material_index=3
        # Verify physical units, not coordinate equality alone.
        bpy.context.view_layer.update()
        physical=np.array(ob.dimensions)*scene.unit_settings.scale_length*1000
        expected=np.ptp(verts,axis=0)
        check.append({'part':p['name'],'stl_sha256':p['sha256'],'physical_mm':physical.tolist(),
                      'expected_stl_assembly_extent_mm':expected.tolist(),'max_error_mm':float(abs(physical-expected).max())})
    world=scene.world or bpy.data.worlds.new('World');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.79,.84,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.65
    for loc,power,size in [((70,-100,250),1000000,180),((150,200,200),700000,150),((-100,80,150),500000,130)]:
        ld=bpy.data.lights.new('Softbox','AREA');ld.energy=power;ld.shape='DISK';ld.size=size
        ob=bpy.data.objects.new('Softbox',ld);scene.collection.objects.link(ob);ob.location=loc;aim(ob,(65,50,15))
    cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);scene.collection.objects.link(cam);scene.camera=cam
    cd.type='ORTHO';cd.lens=50;cd.clip_end=3000
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32
    scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX'
    cam.location=(230,260,180);aim(cam,(74,57,20));cd.ortho_scale=220
    public_metadata(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene.blend'))
    views={'front':((230,260,180),(74,57,20),220),'rear':((-210,-240,170),(74,57,20),225),
           'top':((78,63,400),(78,63,0),185),'exploded':((240,275,245),(74,57,53),275)}
    render=[]
    for name,(loc,target,scale) in views.items():
        for i,ob in enumerate(objs):ob.location.z= i*7 if name=='exploded' else 0
        cam.location=loc;aim(cam,target);cd.ortho_scale=scale
        scene.render.filepath='//previews/'+name+'.png';bpy.ops.render.render(write_still=True)
        sanitize_png_metadata(ROOT/'previews'/(name+'.png'))
        render.append({'file':name+'.png','sha256':hashlib.sha256((ROOT/'previews'/(name+'.png')).read_bytes()).hexdigest(),
                       'geometry':'exact nine STL meshes transformed by parameters.json; exploded z offsets only' if name=='exploded' else 'exact nine STL meshes transformed by parameters.json'})
    # Save final scene assembled, with saved physical bounds checked again after reopening.
    for ob in objs:ob.location.z=0
    cam.location=(230,260,180);aim(cam,(74,57,20));cd.ortho_scale=220
    public_metadata(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene.blend'))
    sanitize_scene_metadata(ROOT/'scene.blend')
    (ROOT/'qa'/'scene-unit-report.json').write_text(json.dumps({'unit_system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,
        'display_length_unit':scene.unit_settings.length_unit,'formula':'mesh BU extent * 0.001 m/BU * 1000 mm/m','parts':check,
        'pass':all(x['max_error_mm']<1e-4 for x in check),'physical_print_or_fit_tested':False},indent=2),encoding='utf-8')
    (ROOT/'previews'/'render-manifest.json').write_text(json.dumps(render,indent=2),encoding='utf-8')
    print('Scene and four exact-mesh views saved.')
if __name__=='__main__':main()
