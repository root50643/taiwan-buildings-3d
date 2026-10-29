"""Read-only Blender verifier: blender -b --python verify_color_geometry.py -- ORIGINAL CANDIDATE REPORT [3MF]."""
import bpy,sys,json,hashlib,struct,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]; original,candidate,report=map(Path,args[:3])
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
 result=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  m=o.data;vs=[list(v.co) for v in m.vertices];fs=[list(p.vertices) for p in m.polygons]
  result.append({'object':o.name,'vertices':vs,'faces':fs,'matrix':[list(r) for r in o.matrix_world],'material_indices':[p.material_index for p in m.polygons],'material_count':len(m.materials),'shader_linear_rgba':[(list(mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value) if mat.node_tree and mat.node_tree.nodes.get('Principled BSDF') else None) for mat in m.materials]})
 return sorted(result,key=lambda o:o['object'])
a,b=snapshot(original),snapshot(candidate)
checks={'mesh_count_unchanged':len(a)==len(b),'object_names_unchanged':[o['object'] for o in a]==[o['object'] for o in b]}
for i,(x,y) in enumerate(zip(a,b)):
 checks[f'vertices_exact_{i}']=x['vertices']==y['vertices'];checks[f'faces_exact_{i}']=x['faces']==y['faces'];checks[f'transform_exact_{i}']=x['matrix']==y['matrix'];checks[f'material_indices_valid_{i}']=all(0<=k<y['material_count'] for k in y['material_indices'])
checks['multiple_materials_actually_used']=any(len(set(o['material_indices']))>1 for o in b)
if len(args)>3:
 with zipfile.ZipFile(args[3]) as z:
  root=ET.fromstring(z.read('3D/3dmodel.model'))
  mesh=root.find('.//{*}mesh');vs=[[float(e.attrib[k]) for k in ['x','y','z']] for e in mesh.find('{*}vertices')];fs=[[int(e.attrib[k]) for k in ['v1','v2','v3']] for e in mesh.find('{*}triangles')]
  checks['3mf_vertices_exact_to_scene']=len(b)==1 and vs==b[0]['vertices'];checks['3mf_float32_bytes_exact_to_scene']=len(b)==1 and b''.join(struct.pack('<3f',*v) for v in vs)==b''.join(struct.pack('<3f',*v) for v in b[0]['vertices']);checks['3mf_faces_exact_to_scene']=len(b)==1 and fs==b[0]['faces'];tri=list(mesh.find('{*}triangles'));checks['3mf_face_materials_match_scene']=len(b)==1 and [int(t.attrib.get('p1','-1')) for t in tri]==b[0]['material_indices'];checks['3mf_uniform_per_triangle_materials']=all(t.attrib.get('pid')=='1' and t.attrib.get('p1')==t.attrib.get('p2')==t.attrib.get('p3') for t in tri);checks['3mf_millimeters']=root.attrib.get('unit')=='millimeter'
  bases=root.find('.//{*}basematerials');rgba=[[int(e.attrib['displaycolor'][j:j+2],16)/255 for j in [1,3,5,7]] for e in bases];linear=[[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c[:3]]+[c[3]] for c in rgba];checks['palette_count_matches_scene']=len(b)==1 and len(rgba)==b[0]['material_count'];checks['palette_srgb_to_shader_linear']=len(b)==1 and len(linear)==len(b[0]['shader_linear_rgba']) and all(abs(x-y)<1e-7 for c,d in zip(linear,b[0]['shader_linear_rgba']) for x,y in zip(c,d))
checks['original_neutral_material_only']=all(len(set(o['material_indices']))==1 for o in a)
out={'passed':all(checks.values()),'checks':checks,'original_vertex_count':sum(len(o['vertices']) for o in a),'original_face_count':sum(len(o['faces']) for o in a),'candidate_material_face_counts':[{str(k):o['material_indices'].count(k) for k in sorted(set(o['material_indices']))} for o in b],'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [original,candidate]}}
report.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
