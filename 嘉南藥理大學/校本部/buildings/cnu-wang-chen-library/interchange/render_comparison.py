"""Blender 4.3.2 visual comparison from the actual lib3mf-read mesh, not an STL proxy.

blender --background --factory-startup --disable-autoexec --python render_comparison.py -- \
  --blend ../scene.blend --model cnu-wang-chen-library.3mf \
  --native-mesh /tmp/cnu-qa/native-mesh.json --output /tmp/cnu-visual
Does not save or modify a Blend. No geometric or centroid classifications.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import bpy
from mathutils import Vector


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strip_metadata(path):
    raw=path.read_bytes();out=raw[:8];i=8
    while i<len(raw):
        size=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8]
        if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out+=raw[i:i+12+size]
        i+=12+size
    path.write_bytes(out)


def decode(v):
    c=v/255
    return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blend',type=Path,required=True);p.add_argument('--model',type=Path,required=True)
    p.add_argument('--native-mesh',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    blend_hash=sha(a.blend)
    if blend_hash!='d63ad8d2dcf1c896dda145966e4bad84e9475634c3080755fe60251e0cd0189a':raise ValueError('Original Blend pin mismatch')
    data=json.loads(a.native_mesh.read_text())
    if data['model_sha256']!=sha(a.model):raise ValueError('Native dump belongs to a different model')
    if len(data['triangles'])!=65686 or len(data['vertices'])!=32643:raise ValueError('Native dump size mismatch')
    a.output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(a.blend.resolve()),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    originals=[o for o in scene.objects if o.type=='MESH']
    if len(originals)!=1:raise ValueError('Original object count mismatch')
    original=originals[0]
    mesh=bpy.data.meshes.new('Native_3MF_read_mesh');mesh.from_pydata(data['vertices'],[],data['triangles']);mesh.update()
    native=bpy.data.objects.new('Native_3MF_read_display',mesh);scene.collection.objects.link(native)
    for i,m in enumerate(data['materials']):
        mat=bpy.data.materials.new('3MF_'+m['name']);rgba=m['rgba8']
        mat.diffuse_color=tuple(decode(x) for x in rgba[:3])+(rgba[3]/255,)
        mesh.materials.append(mat)
    for i,(p,mi) in enumerate(zip(mesh.polygons,data['face_materials'])):
        p.material_index=mi;p.use_smooth=original.data.polygons[i].use_smooth
        actual=b''.join(struct.pack('<3f',*mesh.vertices[j].co) for j in p.vertices)
        expected=b''.join(struct.pack('<3f',*original.data.vertices[j].co) for j in original.data.polygons[i].vertices)
        if actual!=expected or mi!=original.data.polygons[i].material_index:raise ValueError('Native-render geometry/binding mismatch')
    scene.render.resolution_x=900;scene.render.resolution_y=675;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    target_z=(min(v.co.z for v in mesh.vertices)+max(v.co.z for v in mesh.vertices))/2
    camera=scene.camera;camera.data.type='ORTHO'
    result={'model_sha256':data['model_sha256'],'reader':data['reader'],'blender_version':bpy.app.version_string,
            'all_native_faces_verified_before_render':True,'same_cameras_lighting_geometry_and_bindings':True,
            'display_difference':'Original stored linear RGB versus sRGB8 decoded to linear; quantization expected. No photoreal/pixel-identical promise.',
            'images':{}}
    for view,loc in [('front',(-160,-280,145)),('rear',(160,280,145))]:
        camera.location=loc;camera.rotation_euler=(Vector((0,0,target_z))-camera.location).to_track_quat('-Z','Y').to_euler()
        inv=camera.rotation_euler.to_matrix().transposed()
        points=[inv@(original.matrix_world@Vector(c)-camera.location) for c in original.bound_box]
        w=max(v.x for v in points)-min(v.x for v in points);h=max(v.y for v in points)-min(v.y for v in points)
        camera.data.ortho_scale=max(w,h*900/675)*1.18
        for label in ('original','3mf'):
            original.hide_render=label!='original';native.hide_render=label!='3mf'
            scene.render.filepath=str((a.output/(label+'-'+view+'.png')).resolve())
            bpy.ops.render.render(write_still=True)
            path=Path(scene.render.filepath);strip_metadata(path);result['images'][path.name]=sha(path)
    if sha(a.blend)!=blend_hash:raise ValueError('Original Blend changed')
    result['original_blend_byte_unchanged']=True
    (a.output/'visual-render.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
