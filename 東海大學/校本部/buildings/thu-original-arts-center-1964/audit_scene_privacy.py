"""Inspect the saved scene through Blender APIs and scan raw fixed storage.
No binary patching, ctypes edits, or geometry changes are performed.
"""
from pathlib import Path
import bpy,hashlib,json,sys,struct,zlib
root=Path(sys.argv[sys.argv.index('--')+1]).resolve();path=root/'model.blend';raw=path.read_bytes();bpy.ops.wm.open_mainfile(filepath=str(path))
markers={'workspace_path_prefix':b'/workspace/','home_path_prefix':b'/home/','private_model_worktree_marker':b'restart-models/','windows_user_path_prefix':b'\\Users\\'}
hits={name:[i for i in range(len(raw)) if raw.startswith(marker,i)] for name,marker in markers.items()}
assets=list(bpy.utils.blend_paths(absolute=False));images=[{'name':i.name,'source':i.source,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
pngs=[]
for name in ['preview-entrance.png','preview-courtyard.png','preview-plan.png']:
 data=(root/name).read_bytes();pos=8;metadata={}
 while pos<len(data):
  length=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+length];pos+=12+length
  if kind==b'tEXt':
   key,value=payload.split(b'\0',1);metadata[key.decode('latin1')]=value.decode('latin1')
  elif kind==b'zTXt':
   key,value=payload.split(b'\0',1);metadata[key.decode('latin1')]=zlib.decompress(value[1:]).decode('latin1')
  elif kind==b'iTXt':
   key,value=payload.split(b'\0',1);flag,method=value[:2];language,translated,text=value[2:].split(b'\0',2);metadata[key.decode('latin1')]=(zlib.decompress(text) if flag else text).decode('utf8')
 combined=data+b'\n'+json.dumps(metadata).encode();found=[label for label,m in markers.items() if m in combined]
 pngs.append({'file':name,'sha256':hashlib.sha256(data).hexdigest(),'text_metadata':metadata,'private_marker_matches':found,'filename_or_hostname_metadata_present':any(k.casefold() in ['file','filename','hostname'] for k in metadata)})
checks={'png_metadata_contains_no_private_paths':all(not v['private_marker_matches'] and not v['filename_or_hostname_metadata_present'] for v in pngs),'relative_entrance_render_path':bpy.context.scene.render.filepath=='//preview-entrance.png','no_external_asset_paths':not assets,'no_images_or_reference_photos':not images,'no_linked_libraries':len(bpy.data.libraries)==0,'no_known_private_path_residues_in_raw_storage':not any(hits.values())}
r={'passed':all(checks.values()),'stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256(raw).hexdigest(),'checks':checks,'render_filepath':bpy.context.scene.render.filepath,'external_asset_paths':assets,'images':images,'linked_library_count':len(bpy.data.libraries),'raw_storage_marker_offsets':hits,'pngs':pngs,'method':'Fresh factory-default in-memory scene saved before any rendering; only relative render paths thereafter. Blender API inventory plus raw-byte marker search detects private working-path residue beyond string terminators. Filename and hostname PNG metadata are disabled through native render settings. All PNG text chunks and raw bytes are checked. No binary or ctypes patching.'}
(root/'qa-scene-privacy.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
