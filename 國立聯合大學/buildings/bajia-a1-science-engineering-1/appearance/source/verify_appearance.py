from pathlib import Path
import bpy,json,hashlib,struct,xml.etree.ElementTree as ET,zipfile,sys
P=Path(sys.argv[-1]);A=P/'appearance';M=P/'multicolor';bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'))
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(M/'a1-four-tool-core.3mf') as z:r=ET.fromstring(z.read('3D/3dmodel.model'))
mapid={'light_frames':'wall_and_light_frame','wall':'wall_and_light_frame','glass':'glass_teal','pv':'photovoltaic_blue_violet','roof':'metal_roof_gray_green','dark_facade':'dark_facade','plinth':'display_plinth','brick':'brick_terracotta'}
palette={p['id']:p['candidate_rgb'] for p in json.loads((M/'color-evidence.json').read_text())['fine_material_identities']};rows=[]
for e in r.findall('.//m:object',ns):
 mesh=e.find('m:mesh',ns)
 if mesh is None:continue
 name=e.get('name');o=bpy.data.objects[name];v=[tuple(struct.unpack('<f',struct.pack('<f',float(n.get(k))))[0] for k in ['x','y','z']) for n in mesh.findall('m:vertices/m:vertex',ns)];f=[tuple(int(n.get(k)) for k in ['v1','v2','v3']) for n in mesh.findall('m:triangles/m:triangle',ns)];assert v==[tuple(x.co) for x in o.data.vertices] and f==[tuple(x.vertices) for x in o.data.polygons];assert tuple(o.location)==(0,0,0) and tuple(o.rotation_euler)==(0,0,0) and tuple(o.scale)==(1,1,1) and not o.modifiers
 mid=mapid[name];mat=o.data.materials[0];hexcolor='#'+''.join(f'{x:02X}' for x in palette[mid]);assert mat.name==mid and mat['approximate_srgb_hex']==hexcolor
 def lin(c):c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
 assert max(abs(a-b) for a,b in zip(mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3],[lin(c) for c in palette[mid]]))<1e-7
 rows.append({'mesh':name,'vertices':len(v),'triangles':len(f),'material':mid,'approximate_srgb_hex':hexcolor,'source_float32_coordinates_indices_exact':True})
assert len(rows)==8 and len([o for o in bpy.data.objects if o.type=='MESH'])==8 and len(bpy.data.materials)==7
assert abs(bpy.context.scene.unit_settings.scale_length-.001)<1e-9 and not bpy.data.libraries
assert all(i.type=='RENDER_RESULT' and not i.packed_file and not i.filepath for i in bpy.data.images)
assert bpy.context.scene.render.filepath.startswith('//')
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='FILE_BROWSER':
   for sp in ar.spaces:
    if getattr(sp,'params',None):assert sp.params.directory in [b'//',b'']
report={'Blender':bpy.app.version_string,'mesh_count':8,'material_count':7,'all_source_mesh_float32_coordinates_indices_exact':True,'source_3mf_sha256':hashlib.sha256((M/'a1-four-tool-core.3mf').read_bytes()).hexdigest(),'geometry_changed':False,'print_assets_changed':False,'unit':'mm','scale_length':.001,'source_photo_pixels_embedded':False,'external_image_or_library_dependencies':False,'saved_render_path_relative':True,'parts':rows};(A/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
