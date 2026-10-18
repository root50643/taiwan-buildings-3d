"""Three own-STL assembly aids. No source photos, no slicer/print claims."""
from pathlib import Path
import hashlib,json,argparse
import bpy
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aim(obj,p):obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
    return m
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='*',default=['assembled','exploded','print-orientations']);args=parser.parse_args()
    report=json.loads((ROOT/'models/build-report.json').read_text(encoding='utf8'))
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS';scene.unit_settings.scale_length=.001
    colors=[(.54,.60,.64),(.83,.62,.36),(.66,.76,.70),(.90,.72,.46),(.69,.79,.83),(.63,.32,.24)]
    objects=[]
    for row,color in zip(report['parts'],colors):
        stl=ROOT/'models'/row['stl'];assert digest(stl)==row['stl_sha256']
        bpy.ops.wm.stl_import(filepath=str(stl));o=bpy.context.object;o.name=row['id']
        o['STL_SHA256']=row['stl_sha256'];o['assembly_transform']=sum(row['transform_print_to_assembled'],[])
        o.matrix_world=Matrix(row['transform_print_to_assembled']);o.data.materials.append(mat(row['id'],color));objects.append(o)
    world=bpy.data.worlds.new('Neutral');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.80,.84,.86,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.6;scene.world=world
    groundmat=mat('Display ground only',(.84,.85,.84))
    bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.1));bpy.context.object.name='RenderGround_NOT_PRINTED';bpy.context.object.data.materials.append(groundmat)
    for name,location,energy,size in [('Key',(-130,-200,300),60000,220),('Fill',(150,120,250),40000,200)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=location;aim(o,(0,0,25))
    d=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.clip_end=5000
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=1200;scene.render.resolution_y=860;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    bpy.context.preferences.filepaths.save_version=0;bpy.context.preferences.filepaths.file_preview_type='NONE'
    cam.location=(190,250,170);aim(cam,(0,0,22));d.ortho_scale=200
    bpy.ops.object.select_all(action='DESELECT');objects[0].select_set(True);bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene.blend'),compress=True)
    out=ROOT/'previews';out.mkdir(exist_ok=True)
    old=json.loads((out/'render-manifest.json').read_text(encoding='utf8')) if (out/'render-manifest.json').exists() else {'views':[]}
    manifest={'input_build_report_sha256':digest(ROOT/'models/build-report.json'),'scene_sha256':digest(ROOT/'scene.blend'),'scope':'Own-STL assembly and orientation aids; not slicer screenshots','views':old['views']}
    def render(name):
        if name not in args.only:return
        p=out/(name+'.png');scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
        manifest['views']=[v for v in manifest['views'] if v['name']!=name]
        manifest['views'].append({'name':name,'sha256':digest(p),'camera':list(cam.location),'ortho_scale':d.ortho_scale})
    render('assembled')
    for o,row in zip(objects,report['parts']):
        o.matrix_world=Matrix(row['transform_print_to_assembled']);o.location.z+=12*row['horizontal_band']
    cam.location=(190,250,240);aim(cam,(0,0,48));d.ortho_scale=250;render('exploded')
    # Each STL in its delivered print orientation; spread apart for inspection.
    # This is NOT a single-bed packing layout or ready-to-run machine placement.
    labels=[]
    labelmat=mat('Render label only',(.08,.10,.11))
    for i,(o,row) in enumerate(zip(objects,report['parts'])):
        o.matrix_world=Matrix.Identity(4)
        bounds=row['print_bounds_mm'];cx=(bounds[0][0]+bounds[1][0])/2;cy=(bounds[0][1]+bounds[1][1])/2
        x=(-90,90)[i%2];y=(140,0,-140)[i//2];o.location=(x-cx,y-cy,0)
        curve=bpy.data.curves.new('Label '+str(i+1),'FONT');curve.body=f'{i+1:02d}';curve.size=12;curve.extrude=0
        text=bpy.data.objects.new('Render label '+str(i+1),curve);scene.collection.objects.link(text);text.location=(x-6,y-62,.02);labels.append(text)
        text.data.materials.append(labelmat)
    cam.location=(0,-450,650);aim(cam,(0,0,0));d.ortho_scale=520;render('print-orientations')
    (out/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print('Three STL-based assembly aids rendered; six-part scene saved')
if __name__=='__main__':main()
