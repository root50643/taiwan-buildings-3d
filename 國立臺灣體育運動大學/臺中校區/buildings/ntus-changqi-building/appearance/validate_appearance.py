#!/usr/bin/env python3
"""Exact source triangle equality plus topology, image, and public-artifact checks."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,hashlib,struct,re,collections
import numpy as np
from PIL import Image
from build_appearance import load_stl
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--input',type=Path,default=Path(__file__).resolve().parent.parent/'model.stl');a=p.parse_args();root=a.out
raw,v,f,tri=load_stl(a.input);D=np.load(root/'mesh-data.npz');assert np.array_equal(D['vertices'][D['faces']],tri);assert np.array_equal(D['vertices'],v)and np.array_equal(D['faces'],f);assert len(D['materials'])==len(f)
rules=json.loads((root/'mapping-rules.json').read_text())['rules'];pal=json.loads((root/'palette.json').read_text())
t=tri.astype(float);t[:,:,0]=t[:,:,0]/(150/68)+30;t[:,:,1]=-t[:,:,1]/(150/68)+13;t[:,:,2]=t[:,:,2]/(150/68)-1.2
norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]).astype(float);norm/=np.linalg.norm(norm,axis=1)[:,None];norm[:,1]*=-1
checked=0
for i,r in enumerate(rules[1:],1):
 ix=np.flatnonzero(D['rule_indices']==i)
 if not len(ix):continue
 axis='xyz'.index(r['plane_axis']);assert np.all(abs(t[ix,:,axis]-r['plane_source_m'])<2e-5);assert np.all(norm[ix,axis]*r['outward_sign']>.999)
 for ax,bounds in r['all_vertex_bounds_source_m'].items():
  j='xyz'.index(ax);assert np.all(t[ix,:,j]>=bounds[0]-2e-5)and np.all(t[ix,:,j]<=bounds[1]+2e-5)
 assert all(pal[int(D['materials'][k])]['id']==r['material']for k in ix);assert r['evidence'];checked+=len(ix)
assert checked==np.count_nonzero(D['materials']);assert np.all((D['materials']==0)==(D['rule_indices']==0))
edges=collections.Counter();directed=collections.Counter()
for face in f:
 for x,y in zip(face,np.roll(face,-1)):edges[tuple(sorted((int(x),int(y))))]+=1;directed[(int(x),int(y))]+=1
assert all(n==2 for n in edges.values());assert all(directed[(a,b)]==directed[(b,a)]for a,b in edges)
assert np.isfinite(v).all();area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;assert np.all(area>0)
volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert volume>0
parent=np.arange(len(v))
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
for x,y in edges:parent[find(x)]=find(y)
components=len(set(find(i)for i in range(len(v))));assert components==1
rows=[];pixelhashes=[]
for path in sorted((root/'previews').glob('*.png')):
 b=path.read_bytes();i=8;tags=[]
 while i<len(b):n=struct.unpack_from('>I',b,i)[0];tags.append(b[i+4:i+8].decode());i+=n+12
 assert not set(tags)&{'tEXt','zTXt','iTXt','eXIf','tIME'}
 im=Image.open(path).convert('RGB');assert im.size==(1200,900);pix=np.array(im);assert pix.std()>10;h=hashlib.sha256(pix.tobytes()).hexdigest();pixelhashes.append(h);rows.append({'view':path.stem,'dimensions':list(im.size),'pixel_sha256':h,'text_exif_time_metadata_absent':True,'unique_rgb_colors':len(np.unique(pix.reshape(-1,3),axis=0))})
assert len(rows)==9 and len(set(pixelhashes))==9
blend=(root/'ntus-changqi-appearance.blend').read_bytes();needles=[b'/workspace/',b'/tmp/',b'/home/agent/',b'Authorization:',b'Bearer ',b'WebDAV',b'webdav',b'password='];hits=[x.decode()for x in needles if x in blend];assert not hits,hits
report={'source_stl_sha256':hashlib.sha256(raw).hexdigest(),'source_stl_bytes':len(raw),'all_original_triangle_coordinates_and_order_exact':True,'independently_rechecked_registered_face_count':checked,'every_assigned_face_satisfies_full_vertex_plane_bounds_normal_and_material_rule':True,'vertices':len(v),'triangles':len(f),'edges':len(edges),'bounds_mm':[v.min(0).tolist(),v.max(0).tolist()],'dimensions_mm':np.ptp(v,axis=0).tolist(),'watertight_edge_incidence':True,'consistent_winding':True,'components':components,'euler_number':len(v)-len(edges)+len(f),'volume_mm3':volume,'minimum_triangle_area_mm2':float(area.min()),'unchanged_geometry_inherits_original_print_limitations':True,'blend_private_path_scan_hits':hits,'previews':rows}
(root/'qa'/'geometry-and-preview-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='previews'},indent=2))
