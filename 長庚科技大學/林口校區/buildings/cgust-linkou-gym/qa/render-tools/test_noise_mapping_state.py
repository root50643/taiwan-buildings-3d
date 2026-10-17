"""Fresh synthetic normal/-O controls for this case's Noise/MixRGB state set.
No project scene is loaded or rendered. Mutations must differ from a fresh baseline.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_source_scene import nodes, differences

def require(value, message):
    if not value: raise RuntimeError(message)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    material = bpy.data.materials.new('Synthetic Noise MixRGB')
    material.use_nodes = True
    tree = material.node_tree
    noise = tree.nodes.new('ShaderNodeTexNoise')
    mix = tree.nodes.new('ShaderNodeMixRGB')
    mix.inputs[1].default_value = (.23, .36, .32, 1)
    mix.inputs[2].default_value = (.68, .75, .64, 1)
    tree.links.new(noise.outputs['Fac'], mix.inputs[0])
    tree.links.new(mix.outputs[0], tree.nodes['Principled BSDF'].inputs['Base Color'])
    return tree, noise, mix

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    require(not args.out.exists(), 'Refuse existing control output')
    args.out.mkdir(parents=True)
    source = Path(__file__).with_name('compare_source_scene.py')
    start = sha(source)
    tree, noise, mix = scene()
    baseline = nodes(tree)
    cases = [
        ('unchanged', None, True),
        ('noise-vector-type', lambda n,m: setattr(n.texture_mapping,'vector_type','NORMAL'), False),
        ('noise-translation', lambda n,m: setattr(n.texture_mapping,'translation',(1,2,3)), False),
        ('noise-rotation', lambda n,m: setattr(n.texture_mapping,'rotation',(.1,.2,.3)), False),
        ('noise-scale', lambda n,m: setattr(n.texture_mapping,'scale',(2,3,4)), False),
        ('noise-min', lambda n,m: setattr(n.texture_mapping,'min',(-2,-3,-4)), False),
        ('noise-max', lambda n,m: setattr(n.texture_mapping,'max',(2,3,4)), False),
        ('noise-use-min', lambda n,m: setattr(n.texture_mapping,'use_min',True), False),
        ('noise-use-max', lambda n,m: setattr(n.texture_mapping,'use_max',True), False),
        ('noise-map-x', lambda n,m: setattr(n.texture_mapping,'mapping_x','Z'), False),
        ('noise-map-y', lambda n,m: setattr(n.texture_mapping,'mapping_y','X'), False),
        ('noise-map-z', lambda n,m: setattr(n.texture_mapping,'mapping_z','Y'), False),
        ('noise-map-mode', lambda n,m: setattr(n.texture_mapping,'mapping','SPHERE'), False),
        ('noise-color-ramp-enabled', lambda n,m: setattr(n.color_mapping,'use_color_ramp',True), False),
        ('noise-brightness', lambda n,m: setattr(n.color_mapping,'brightness',.3), False),
        ('noise-contrast', lambda n,m: setattr(n.color_mapping,'contrast',.4), False),
        ('noise-saturation', lambda n,m: setattr(n.color_mapping,'saturation',.5), False),
        ('noise-blend-type', lambda n,m: setattr(n.color_mapping,'blend_type','ADD'), False),
        ('noise-blend-color', lambda n,m: setattr(n.color_mapping,'blend_color',(.1,.2,.3)), False),
        ('noise-blend-factor', lambda n,m: setattr(n.color_mapping,'blend_factor',.7), False),
        ('noise-ramp-color', lambda n,m: setattr(n.color_mapping.color_ramp.elements[0],'color',(.2,.3,.4,.5)), False),
        ('noise-ramp-position', lambda n,m: setattr(n.color_mapping.color_ramp.elements[0],'position',.2), False),
        ('noise-ramp-interpolation', lambda n,m: setattr(n.color_mapping.color_ramp,'interpolation','CONSTANT'), False),
        ('noise-ramp-color-mode', lambda n,m: setattr(n.color_mapping.color_ramp,'color_mode','HSV'), False),
        ('noise-ramp-hue-mode', lambda n,m: setattr(n.color_mapping.color_ramp,'hue_interpolation','FAR'), False),
        ('noise-ramp-extra-element', lambda n,m: n.color_mapping.color_ramp.elements.new(.4), False),
        ('mix-color-input', lambda n,m: setattr(m.inputs[1],'default_value',(.4,.3,.2,1)), False),
        ('mix-operation', lambda n,m: setattr(m,'blend_type','ADD'), False),
        ('mix-clamp', lambda n,m: setattr(m,'use_clamp',True), False),
        ('noise-scale-input', lambda n,m: setattr(n.inputs['Scale'],'default_value',7), False),
        ('noise-type', lambda n,m: setattr(n,'noise_dimensions','4D'), False),
        ('mix-link', lambda n,m: tree.links.remove(next(x for x in tree.links if x.to_node==m)), False),
    ]
    rows=[]
    for name, mutate, expected in cases:
        tree, noise, mix = scene()
        if mutate: mutate(noise, mix)
        observed=nodes(tree); delta=differences(baseline, observed)
        accepted = not delta
        row={'case':name,'expected_equal':expected,'observed_equal':accepted,
             'passed':accepted is expected,'differences':delta}
        rows.append(row)
        (args.out/(name+'.json')).write_text(json.dumps({'result':row,'state':observed},indent=2)+'\n')
    (args.out/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    report={'passed':all(r['passed'] for r in rows) and sha(source)==start,
            'case_count':len(rows),'optimization_level':sys.flags.optimize,
            'blender_version':bpy.app.version_string,'tool_sha256':start,
            'test_source_sha256':sha(__file__),'no_project_scene_loaded':True,
            'no_image_rendering':True,'tool_source_unchanged':sha(source)==start,
            'cases':rows}
    (args.out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','case_count','optimization_level']}))
    require(report['passed'],'Noise/MixRGB state controls failed')
if __name__=='__main__':main()
