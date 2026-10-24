"""Deliberate negative controls in temporary files; original and deliverables stay read-only."""
from pathlib import Path
import argparse,tempfile,copy
import sys
sys.dont_write_bytecode=True
from common import *
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.out;D=load(a.stl,root/'parameters.json',root/'palette.json');tests={}
def reject(name,fn):
 try:fn()
 except (AssertionError,ValueError):tests[name]='REJECTED'
 else:raise AssertionError('Accepted tampering: '+name)
with tempfile.TemporaryDirectory(prefix='fail-closed-')as td:
 t=Path(td);pp=t/'parameters.json';cp=t/'palette.json';s=t/'model.stl'
 b=bytearray(a.stl.read_bytes());b[96]^=1;s.write_bytes(b);reject('changed_original_stl_bytes',lambda:load(s,root/'parameters.json',root/'palette.json'))
 neutral=D['parameters']['neutral_original_face_ids'][0]
 changes=[('add_unlisted_neutral_face',lambda p:p['regions']['main_dome']['original_face_ids'].append(neutral)),('remove_roof_face',lambda p:p['regions']['main_dome']['original_face_ids'].pop()),('white_lip_assigned_green',lambda p:p['regions']['horizontal_roof_rim_lip'].__setitem__('material_family','roof_pale_yellow_green')),('substitute_neutral_face_for_front_glass',lambda p:p['regions']['observed_front_glazing']['original_face_ids'].__setitem__(0,neutral)),('changed_face_fingerprint',lambda p:p['regions']['main_dome']['oriented_vertex_sha256_by_face_id'].__setitem__(str(p['regions']['main_dome']['original_face_ids'][0]),'0'*64)),('missing_neutral_face',lambda p:p['neutral_original_face_ids'].pop()),('extra_region',lambda p:p['regions'].__setitem__('vertical_ring',{}))]
 for name,change in changes:
  p=copy.deepcopy(D['parameters']);change(p);dump(pp,p);reject(name,lambda:load(a.stl,pp,root/'palette.json'))
 for name,change in [('extra_material',lambda p:p.__setitem__('extra_white',{'srgb8':[255]*3})),('changed_palette',lambda p:p['roof_pale_yellow_green']['srgb8'].__setitem__(0,199)),('transparent_glass',lambda p:p['front_glazing_family'].__setitem__('alpha',.5))]:
  p=copy.deepcopy(D['palette']);change(p);dump(cp,p);reject(name,lambda:load(a.stl,root/'parameters.json',cp))
 tris=list(D['triangles']);tris[0]=tuple(reversed(tris[0]));reject('reversed_winding',lambda:mapping(D['signatures'],tris))
 tris=list(D['triangles']);tris[0]=tris[1];reject('duplicate_or_missing_face',lambda:mapping(D['signatures'],tris))
 tris=list(reversed(D['triangles']));reject('reordered_original_faces',lambda:mapping(D['signatures'],tris))
 tris=[(t[1],t[2],t[0])for t in D['triangles']];reject('cyclic_original_corner_rotation',lambda:mapping(D['signatures'],tris))
 tris=list(D['triangles']);q=list(tris[0]);v=list(q[0]);v[0]+=.00001;q[0]=tuple(v);tris[0]=tuple(q);reject('moved_vertex',lambda:mapping(D['signatures'],tris))
 tris=list(D['triangles'])+[D['triangles'][0]];reject('new_triangle_or_subdivision',lambda:mapping(D['signatures'],tris))
 # Vertex-table reindexing alone is allowed only when the exact face/corner coordinate stream is restored.
 vertices=list(reversed(D['vertices']));faces=[[len(vertices)-1-i for i in f]for f in D['faces']]
 need(mapping(D['signatures'],[[vertices[i]for i in f]for f in faces])==list(range(N)),'Lossless vertex reindex control failed');tests['vertex_table_reindex_exact_ordered_stream']='PASS'
need(sha(a.stl.read_bytes())==SHA,'Original changed');dump(root/'qa/fail-closed.json',{'status':'PASS','tests':tests,'production_original_stl_unchanged':True,'negative_control_count':sum(v=='REJECTED'for v in tests.values())});print(tests)
