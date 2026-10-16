"""Create isolated scene mutants for inspection/state-comparison negative tests.
Never render. Input Blender scene and manifest remain read-only.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy

def main():
    p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.out.exists():raise RuntimeError('Refusing existing output')
    a.out.mkdir(parents=True);original=json.loads(a.manifest.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();initial={'blend':sha(a.blend),'manifest':sha(a.manifest)}
    for case in ['lens26','samples32','denoising-on','material-changed','wrong-view-set']:
        folder=a.out/case;folder.mkdir();bpy.ops.wm.open_mainfile(filepath=str(a.blend.resolve()));bpy.context.preferences.filepaths.save_version=0;scene=bpy.context.scene
        if case=='lens26':scene.camera.data.lens=26
        if case=='samples32':scene.cycles.samples=32
        if case=='denoising-on':scene.cycles.use_denoising=True
        if case=='material-changed':bpy.data.materials['wall'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.25
        target=folder/'scene.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target.resolve()));manifest=json.loads(json.dumps(original));manifest['blend_sha256']=sha(target)
        if case=='wrong-view-set':manifest['views']['undeclared-view']=manifest['views'].pop('roof-detail')
        (folder/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if sha(a.blend)!=initial['blend'] or sha(a.manifest)!=initial['manifest']:raise RuntimeError('Original mutated')
    (a.out/'FIXTURE-BINDING.json').write_text(json.dumps({'passed':True,'source_blend_sha256':initial['blend'],'source_manifest_sha256':initial['manifest'],'no_images_rendered':True,'mutations':['camera lens 26','samples 32','denoising enabled','wall material roughness 0.25','undeclared view replacing roof-detail']},indent=2)+'\n')
if __name__=='__main__':main()
