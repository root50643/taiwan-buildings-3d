#!/usr/bin/env python3
"""Exact original triangles + fail-closed sheet-family face labels, never a geometry builder."""
from pathlib import Path
import argparse, csv, hashlib, json, struct
import numpy as np
HERE=Path(__file__).resolve().parent
PIN='ebecf2597fbc17fd0faf5a8bcd3ac13d1d9511d70a9600c5c09084ddbd26d879'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load_stl(path):
 b=Path(path).read_bytes()
 if sha(b)!=PIN:raise ValueError('Original STL hash mismatch; refusing changed geometry')
 n=struct.unpack_from('<I',b,80)[0]
 if n!=4694 or len(b)!=234784:raise ValueError('Original STL size/count mismatch')
 dt=np.dtype([('normal','<f4',3),('vertices','<f4',(3,3)),('attribute','<u2')])
 t=np.frombuffer(b,dtype=dt,count=n,offset=84)['vertices'].copy()
 verts=[];faces=[];lookup={}
 for triangle in t:
  face=[]
  for v in triangle:
   key=v.tobytes()
   if key not in lookup:lookup[key]=len(verts);verts.append(v.copy())
   face.append(lookup[key])
  faces.append(face)
 v=np.asarray(verts,dtype='<f4');f=np.asarray(faces,dtype=np.int32)
 if v[f].tobytes()!=t.tobytes():raise ValueError('Exact-coordinate indexing changed original float32 stream')
 return b,v,f,t

def independently_select_roof(tri):
 # All 3 vertices must lie on ONE original 80-segment barrel facet;
 # exact facet planes are derived from the public original model parameters.
 t=tri.astype(np.float64);lo=t.min(1);hi=t.max(1)
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 xs=np.linspace(-57.,57.,81);zs=42+np.sqrt(108**2-xs**2)-np.sqrt(108**2-57**2)
 eps=3e-4;mask=np.zeros(len(t),dtype=bool)
 for x0,x1,z0,z1 in zip(xs[:-1],xs[1:],zs[:-1],zs[1:]):
  expected=z0+(t[:,:,0]-x0)*(z1-z0)/(x1-x0)
  mask|=((lo[:,0]>=x0-eps)&(hi[:,0]<=x1+eps)&np.all(np.abs(t[:,:,2]-expected)<eps,axis=1))
 mask&=(lo[:,1]>=-37-eps)&(hi[:,1]<=63+eps)&(n[:,2]>.8)&(abs(n[:,1])<eps)
 return np.flatnonzero(mask).tolist()

def assign(tri,contract):
 if contract['original_stl_sha256']!=PIN:raise ValueError('Contract input pin mismatch')
 ids=contract['face_indices_0_based']
 if len(ids)!=1206 or ids!=sorted(set(ids)) or contract['roof_face_count']!=1206:raise ValueError('Contract IDs invalid')
 if independently_select_roof(tri)!=ids:raise ValueError('Independent whole-triangle roof selector mismatch')
 rec=contract['faces']
 if [r['face_id_0_based'] for r in rec]!=ids:raise ValueError('Fingerprint ID sequence mismatch')
 for r in rec:
  q=tri[r['face_id_0_based']].tobytes();cyc=min(q,q[12:]+q[:12],q[24:]+q[:24])
  if sha(q)!=r['ordered_float32_le_sha256'] or sha(cyc)!=r['oriented_cyclic_float32_le_sha256']:raise ValueError('Original oriented face fingerprint mismatch')
 mi=np.zeros(len(tri),dtype=np.int32);mi[ids]=1
 return mi

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=HERE.parent/'model.stl');p.add_argument('--out',type=Path,default=HERE);a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True);(out/'qa').mkdir(exist_ok=True)
 b,v,f,t=load_stl(a.input);c=json.loads((HERE/'roof-face-contract.json').read_text());mi=assign(t,c)
 np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi)
 with (out/'face-materials.csv').open('w',newline='') as h:
  w=csv.writer(h);w.writerow(['original_stl_triangle_index','material_index','material_id','ordered_float32_le_sha256','scope'])
  for i,m in enumerate(mi):w.writerow([i,m,'roof_sheet_metal_family_illustrative_neutral' if m else 'retained_original_preview_neutral',sha(t[i].tobytes()),'nonphotometric_family_illustration' if m else 'unverified_unchanged_preview'])
 area=np.linalg.norm(np.cross(t[:,1].astype(float)-t[:,0],t[:,2].astype(float)-t[:,0]),axis=1)*.5
 report={'original_stl_sha256':sha(b),'triangles':len(f),'vertices':len(v),'full_original_float32_triangle_sequence_equal':v[f].tobytes()==t.tobytes(),'changed_coordinates':0,'added_removed_split_reversed_faces':0,'original_builder_executed':False,'roof_faces':int((mi==1).sum()),'other_faces_retained_original_preview':int((mi==0).sum()),'roof_area_mm2':float(area[mi==1].sum()),'roof_area_fraction':float(area[mi==1].sum()/area.sum()),'ordered_triangle_stream_sha256':sha(t.tobytes()),'bounds_mm':[t.min((0,1)).tolist(),t.max((0,1)).tolist()],'independent_whole_triangle_selector_matches_numeric_contract':True,'all_contract_ordered_and_oriented_cyclic_signatures_verified':True}
 (out/'qa'/'mapping-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
