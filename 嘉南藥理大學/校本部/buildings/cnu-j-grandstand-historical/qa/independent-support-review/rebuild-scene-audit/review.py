"""Independent byte reconstruction + evaluated Blend / preview binding audit.
Never writes into candidate. Run with the review's available Python libraries.
"""
from pathlib import Path
import ast, collections, datetime, hashlib, json, os, re, shutil, struct, subprocess, sys, time
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image, ImageOps, ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'candidate'
WORK=HERE/'rebuild-workcopy'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def triangles(path):
    b=path.read_bytes();n=struct.unpack_from('<I',b,80)[0]
    if len(b)!=84+50*n:raise ValueError('Not expected binary STL')
    d=np.frombuffer(b,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)
    return d['v'].copy()

def directed_canonical(a):
    a=np.asarray(a,dtype='<f4').copy()
    negative_zero=int(np.count_nonzero((a==0)&np.signbit(a)))
    a[a==0]=0
    out=[]
    for t in a:
        # Only cyclic rotations are allowed; reversing winding is NOT allowed.
        versions=[tuple(np.roll(t,-i,axis=0).ravel()) for i in range(3)]
        out.append(min(versions))
    out.sort()
    arr=np.asarray(out,dtype='<f4')
    return arr,negative_zero

def compare_triangles(a,b):
    ca,za=directed_canonical(a);cb,zb=directed_canonical(b)
    equal=bool(ca.shape==cb.shape and np.array_equal(ca,cb))
    return {'same_directed_binary32_triangles':equal,'triangles_a':len(ca),'triangles_b':len(cb),
        'negative_zero_coordinates_normalized':[za,zb],
        'canonical_sha256_a':hashlib.sha256(ca.tobytes()).hexdigest(),
        'canonical_sha256_b':hashlib.sha256(cb.tobytes()).hexdigest(),
        'maximum_coordinate_error_mm_if_same_shape':float(np.max(np.abs(ca-cb))) if ca.shape==cb.shape else None,
        'method':'Binary32 coordinates; normalize signed zero, cyclic vertex rotations only, sort directed triangles retaining multiplicity.'}

def main():
    start=time.time()
    inputs=['model.stl','assembly.json','build_model.py','parameters.json','scene.blend','render_preview.py','sanitize_scene.py','render-manifest.json']
    inputs+=['parts/'+p.name for p in sorted((ROOT/'parts').glob('*.stl'))]
    inputs+=['previews/'+p.name for p in sorted((ROOT/'previews').glob('*.png'))]
    before={n:sha(ROOT/n) for n in inputs}
    if WORK.exists():raise ValueError('Workcopy exists; preserve prior evidence rather than overwriting')
    WORK.mkdir()
    for n in ['build_model.py','parameters.json','requirements.txt']:
        shutil.copy2(ROOT/n,WORK/n)
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    proc=subprocess.run([sys.executable,str(WORK/'build_model.py')],capture_output=True,text=True,env=env)
    (HERE/'rebuild.stdout.log').write_text(proc.stdout,encoding='utf-8')
    (HERE/'rebuild.stderr.log').write_text(proc.stderr,encoding='utf-8')
    files=['model.stl','assembly.json']+['parts/'+p.name for p in sorted((ROOT/'parts').glob('*.stl'))]
    reconstruction={n:{'fixed_sha256':before[n],'rebuilt_sha256':sha(WORK/n),
        'byte_identical':(ROOT/n).read_bytes()==(WORK/n).read_bytes(),
        **({'directed_triangle_check':compare_triangles(triangles(ROOT/n),triangles(WORK/n))} if n.endswith('.stl') else
           {'json_equal':json.loads((ROOT/n).read_text())==json.loads((WORK/n).read_text())})} for n in files}
    result={'fixed_commit':'3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'inputs_sha256':before,'reconstruction':{'exit_code':proc.returncode,'outputs':reconstruction,'all_byte_identical':proc.returncode==0 and all(x['byte_identical'] for x in reconstruction.values())}}
    # Read the saved scene, evaluate modifiers/world transforms, and compare all
    # oriented triangles with raw binary STL, avoiding nearest-point-only checks.
    import bpy
    from mathutils import Vector
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene.blend'))
    scene=bpy.context.scene
    meshes=[o for o in scene.objects if o.type=='MESH']
    dg=bpy.context.evaluated_depsgraph_get()
    tri=[];objects=[]
    for o in meshes:
        ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        world=np.asarray([ev.matrix_world@v.co for v in me.vertices],dtype='<f4')
        obj_tri=np.asarray([[world[v] for v in f.vertices] for f in me.loop_triangles],dtype='<f4')
        tri.extend(obj_tri)
        objects.append({'name':o.name,'mesh_name':o.data.name,'matrix_world':[list(row) for row in o.matrix_world],
            'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),
            'modifiers':[m.type for m in o.modifiers],'evaluated_vertices':len(world),'evaluated_triangles':len(obj_tri),
            'hide_render':o.hide_render,'custom_properties':{k:o[k] for k in o.keys()},
            'bounds_world_mm':[world.min(axis=0).tolist(),world.max(axis=0).tolist()]})
        ev.to_mesh_clear()
    evaluation=compare_triangles(np.asarray(tri),triangles(ROOT/'model.stl'))
    file_browser_paths=[]
    for screen in bpy.data.screens:
        for area in screen.areas:
            for sp in area.spaces:
                if sp.type=='FILE_BROWSER' and sp.params:
                    file_browser_paths.append({'screen':screen.name,'directory':sp.params.directory.decode(errors='replace')})
    raw=(ROOT/'scene.blend').read_bytes()
    private_pattern=rb'(?:[A-Za-z]:[\\/])?(?:Users|home)[\\/][^\\/\x00]{1,128}[\\/][^\x00]{0,1024}'
    images=[{'name':i.name,'source':i.source,'filepath':i.filepath,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images]
    result['blend']={'version':bpy.app.version_string,'objects':objects,'evaluated_against_assembly_stl':evaluation,
        'scene_units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,'length_unit':scene.unit_settings.length_unit},
        'scene_camera':{'name':scene.camera.name,'type':scene.camera.data.type,'location':list(scene.camera.location),
            'rotation_euler':list(scene.camera.rotation_euler),'ortho_scale':scene.camera.data.ortho_scale},
        'render':{'engine':scene.render.engine,'cycles_samples':scene.cycles.samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],
            'filepath':scene.render.filepath},'images':images,'libraries':[l.filepath for l in bpy.data.libraries],
        'packed_images':[i['name'] for i in images if i['packed']],
        'file_browser_paths':file_browser_paths,'private_user_directory_pattern_matches':len(re.findall(private_pattern,raw)),
        'sanitization_limit':'The current saved scene is independently opened and scanned. The historical before-sanitization scene is not supplied; its reported former hash and removed-count are not independently recreated.'}
    manifest=json.loads((ROOT/'render-manifest.json').read_text())
    expected={
        'front':((-140,-240,130),(0,-3,23)),
        'rear':((140,230,110),(0,0,23)),
        'side':((240,-80,75),(0,0,24)),
        'front-low':((0,-250,40),(0,-3,22)),
        'top':((0,0,300),(0,0,0)),
    }
    # Bind the delivered rendering program's literal view list to these cameras.
    tree=ast.parse((ROOT/'render_preview.py').read_text())
    views_literal=None
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='views' for t in n.targets):views_literal=ast.literal_eval(n.value)
    cam=scene.camera
    camera_metrics=[]
    model=meshes[0]
    for name,(loc,aim) in expected.items():
        cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        inv=cam.rotation_euler.to_matrix().transposed()
        p=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
        w=max(v.x for v in p)-min(v.x for v in p);h=max(v.y for v in p)-min(v.y for v in p)
        scale=max(w,h*1100/760)*1.12
        camera_metrics.append({'preview':name+'.png','location':list(loc),'aim':list(aim),'computed_ortho_scale':scale,
            'camera_space_bbox_mm':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]],
            'w_h_mm':[w,h]})
    preview_checks={p.name:{'actual_sha256':sha(p),'manifest_sha256':manifest['previews'].get(p.name),
        'hash_match':sha(p)==manifest['previews'].get(p.name),'pixels':list(Image.open(p).size)} for p in sorted((ROOT/'previews').glob('*.png'))}
    result['previews']={'five_assembly_views_plus_one_unique_print_layout':len(preview_checks)==6 and all(n+'.png' in preview_checks for n in expected),
        'manifest_assembly_sha_match':manifest['assembly_sha256']==before['model.stl'],
        'manifest_scene_sha_match':manifest['scene_sha256']==before['scene.blend'],
        'source_view_literals_match':views_literal==[(n,*v) for n,v in expected.items()],
        'files':preview_checks,'assembly_camera_metrics':camera_metrics,
        'unique_print_parts_scope':'Four unique delivered bed-oriented print meshes, one of each type. It is not the 22-piece assembled overview and is not expected to equal model.stl.',
        'saved_scene_scope':'Saved before importing the four unique print-layout meshes. Saved camera is front with deliberately reset ortho_scale=250, while the delivered front render uses bounding-box framing.'}
    # Exactly one independent render, from the saved delivered geometry and its
    # existing materials/lights; use the generator's front framing calculation.
    name='front';loc,aim=expected[name]
    cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=camera_metrics[0]['computed_ortho_scale']
    scene.render.filepath=str(HERE/'independent-front.png')
    bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
    independent_raw_sha=sha(HERE/'independent-front.png')
    raw_png=(HERE/'independent-front.png').read_bytes();clean=raw_png[:8];pos=8;removed=[]
    while pos<len(raw_png):
        size=struct.unpack_from('>I',raw_png,pos)[0];kind=raw_png[pos+4:pos+8]
        if kind in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:removed.append(kind.decode())
        else:clean+=raw_png[pos:pos+size+12]
        pos+=size+12
    (HERE/'independent-front.png').write_bytes(clean)
    im1=np.asarray(Image.open(ROOT/'previews/front.png').convert('RGBA'))
    im2=np.asarray(Image.open(HERE/'independent-front.png').convert('RGBA'))
    delta=np.abs(im1.astype(int)-im2.astype(int))
    result['one_independent_front_render']={'source_scene_sha256':before['scene.blend'],'raw_render_sha256':independent_raw_sha,
        'image_sha256':sha(HERE/'independent-front.png'),'removed_metadata_chunk_types':removed,
        'same_pixels':bool(np.array_equal(im1,im2)),'different_channel_values':int(np.count_nonzero(delta)),
        'max_8bit_channel_delta':int(delta.max()),'mean_8bit_channel_delta':float(delta.mean()),
        'metadata_note':'Blender text/EXIF chunks removed from the review image without changing pixels; raw-render hash retained. Pixel comparison excludes metadata.'}
    # Contact sheet is only for QA of the supplied model images, not source photos.
    sheet=Image.new('RGB',(1200,846),'white');draw=ImageDraw.Draw(sheet)
    for i,n in enumerate(['front','rear','side','front-low','top','unique-print-parts']):
        image=Image.open(ROOT/'previews'/f'{n}.png').convert('RGB');image.thumbnail((600,398))
        x=(i%2)*600;y=(i//2)*282
        image.thumbnail((600,258));sheet.paste(image,(x+(600-image.width)//2,y+24))
        draw.text((x+8,y+5),n,fill='black')
    sheet.save(HERE/'supplied-preview-contact-sheet.jpg',quality=92)
    result['input_hashes_unchanged']=all(sha(ROOT/n)==s for n,s in before.items())
    result['scope_pass']=bool(result['reconstruction']['all_byte_identical'] and evaluation['same_directed_binary32_triangles']
        and result['previews']['manifest_assembly_sha_match'] and result['previews']['manifest_scene_sha_match']
        and result['previews']['source_view_literals_match'] and all(x['hash_match'] for x in preview_checks.values())
        and not result['blend']['libraries'] and not result['blend']['packed_images']
        and not any(i['source']=='FILE' and i['filepath'] for i in images)
        and result['blend']['private_user_directory_pattern_matches']==0 and result['input_hashes_unchanged'])
    result['limitations']=['This subreview covers rebuild, actual saved Blend mesh, preview binding and sanitation only; it does not certify printability, interface fit or support removal.',
        'Only one assembly front was independently rerendered. Other delivered view hashes, render-source cameras and framing are inspected; no historical rendering provenance is claimed.']
    result['elapsed_seconds']=round(time.time()-start,3)
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scope_pass':result['scope_pass'],'reconstruction_byte_identical':result['reconstruction']['all_byte_identical'],
        'blend_directed_binary32_triangles_equal':evaluation['same_directed_binary32_triangles'],'independent_front_pixels_equal':result['one_independent_front_render']['same_pixels'],
        'elapsed_seconds':result['elapsed_seconds']}))

if __name__=='__main__':main()
