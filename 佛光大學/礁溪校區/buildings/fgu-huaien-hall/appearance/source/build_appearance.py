#!/usr/bin/env python3
"""Annotate the frozen original FGU mesh, without changing any triangle.
Python 3 + numpy. Default input is ../../model.stl; --out creates its directories.
No networking, third-party textures, remeshing, repair, face splitting or welding
tolerance. Identical coordinate tuples share indices in first-appearance order.
"""
from pathlib import Path
import argparse, hashlib, json, math, struct
import numpy as np

ORIGINAL_SHA256='95974eb366614bb7caffeba43a5e0ae52cdb971668c51a385de9cc5f46be13e9'
PALETTE=[
 {'id':'unknown_neutral','name':'Unknown / neutral placeholder','hex':'#B9B9B4','sources':[], 'meaning':'Unverified surface, not an assertion of actual wall/column/terrain color'},
 {'id':'cap_white','name':'Observed off-white membrane cap','hex':'#E8E8E3','sources':['S3','S5 daytime page 6','S6'], 'meaning':'Uncalibrated daytime white family; not a polymer specification'},
 {'id':'roof_ring_gray','name':'Observed gray sloping roof ring','hex':'#919592','sources':['S3','S4 technical page only','S5 daytime page 6','S6'], 'meaning':'Gray titanium-zinc standing-seam appearance; seams are not added geometry'},
 {'id':'glazing_dark_reflective','name':'Registered glazing recess backs','hex':'#46545A','sources':['S1','S2','S3','S6'], 'meaning':'Muted blue-gray appearance approximation; opaque material, not glass specification'}
]
# Approximate per-bay source registration, deliberately narrower than visibility.
# Enclosed arc: three consecutive readable upper-window groups in S1.
# Open gallery: three clear right-of-foliage groups in S3, checked with S6.
# Unseen/occluded neighboring bays remain neutral; symmetry is never inferred.
REGISTERED={
 'enclosed':{'angles_degrees':[-56.25,-45,-33.75], 'radius_m':29.25,'halfspan_degrees':4.1,'rows_m':[[8.8,9.5],[9.7,10.4],[10.6,11.3],[11.5,12.2],[12.4,13.1]],'sources':['S1','S2'], 'registration':'From the east portico/enclosed-wall junction toward the southern arc, match the three clearly readable upper-window groups left of the entrance. Exclude uncertain boundary bay -22.5, tree-occluded -67.5 and more tangential far-left bays. The original simplified bay rhythm is not a surveyed feature-to-feature projection.'},
 'open_gallery':{'angles_degrees':[78.75,90.0,101.25], 'radius_m':25.8,'halfspan_degrees':4.2,'rows_m':[[7.15,8.15],[8.4,9.4],[9.65,10.65],[10.9,11.9],[12.15,13.15]],'sources':['S3','S6'], 'registration':'View from the north/northeast, with east portico at image left. Select three clear open-gallery groups to the right of the foreground foliage, behind repeated slanted columns; leave foliage-occluded central groups, entrance, tangential neighbors and western gallery unknown. Angular registration is bounded on the original simplified geometry, not photogrammetric calibration.'}
}

def original(path):
 b=Path(path).read_bytes(); assert hashlib.sha256(b).hexdigest()==ORIGINAL_SHA256,'Not the approved original STL'
 count=struct.unpack_from('<I',b,80)[0]; assert len(b)==84+50*count
 dt=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
 tri=np.frombuffer(b,dt,offset=84)['vertices'].copy()
 vertices=[]; faces=[]; index={}
 for t in tri:
  face=[]
  for v in t:
   k=tuple(float(x) for x in v)
   if k not in index:index[k]=len(vertices);vertices.append(k)
   face.append(index[k])
  faces.append(face)
 v=np.asarray(vertices,dtype=np.float32); f=np.asarray(faces,dtype=np.int32)
 assert np.array_equal(v[f],tri)
 return b,v,f,tri

def classify(tri):
 xyz=(tri.astype(float)-[0,0,3])/2.0; rad=np.linalg.norm(xyz[:,:,:2],axis=2); z=xyz[:,:,2]
 ctr=xyz.mean(axis=1); normals=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]); lengths=np.linalg.norm(normals,axis=1)
 assert (lengths>0).all(); normals/=lengths[:,None]
 ids=np.zeros(len(tri),dtype=np.uint8)
 # Recover original cap vertex profile, including its original corrugation and
 # summit landing. The unmatched horizontal ring collar is NOT cap material.
 capz=19.35+3.0*(1-(rad/25.7)**2)
 capz-=.20*(1-np.cos(2*np.pi*(.866025403784*xyz[:,:,0]-.5*xyz[:,:,1])/4.4))*np.maximum(0,1-(rad/25.7)**2)*np.minimum(1,(rad/15)**2)
 capz=np.minimum(capz,22.30)
 cap=(rad.max(1)<=25.701)&(z.min(1)>=19.44)&(normals[:,2]>.5)&(np.abs(z-capz).max(1)<.005)
 ids[cap]=1
 # All vertices must lie on the sloped annulus profile, and the normal must
 # point out/up. This explicitly excludes low fascia, underside and collar.
 ringz=14.0+(30.5-rad)*(5.05/4.8)
 radial_dot=np.sum(normals[:,:2]*ctr[:,:2],axis=1)/np.linalg.norm(ctr[:,:2],axis=1)
 ring=(rad.min(1)>=25.699)&(rad.max(1)<=30.501)&(z.min(1)>=13.999)&(z.max(1)<=19.051)&(np.abs(z-ringz).max(1)<.002)&(normals[:,2]>.68)&(normals[:,2]<.70)&(radial_dot>.70)
 assert not np.any(cap&ring);ids[ring]=2
 theta=np.degrees(np.arctan2(xyz[:,:,1],xyz[:,:,0])); registered=[]
 for region,cfg in REGISTERED.items():
  for a in cfg['angles_degrees']:
   for row,(lo,hi) in enumerate(cfg['rows_m']):
    angle_error=np.abs((theta-a+180)%360-180)
    # BACK faces have outward radial normals, horizontal normals in Z, the
    # recess radius and every vertex within one row/bay. Reveals cannot pass.
    sel=(np.abs(rad-cfg['radius_m']).max(1)<.02)&(angle_error.max(1)<=cfg['halfspan_degrees']+.001)&(z.min(1)>=lo-.00001)&(z.max(1)<=hi+.00001)&(np.abs(normals[:,2])<.00001)&(radial_dot>.995)
    assert not np.any(ids[sel]);assert sel.sum()>0,(region,a,row)
    ids[sel]=3;registered.append({'region':region,'angle_degrees':a,'row':row+1,'z_design_m':[lo,hi],'original_face_ids':np.flatnonzero(sel).tolist(),'face_count':int(sel.sum()),'sources':cfg['sources']})
 groups=[]
 for i,p in enumerate(PALETTE):
  sel=ids==i;groups.append({**p,'material_index':i,'face_count':int(sel.sum()),'surface_area_mm2':float((lengths[sel]*2).sum()),'original_face_ids':np.flatnonzero(sel).tolist()})
 return ids,groups,registered

def build(stl,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'qa').mkdir(exist_ok=True)
 b,v,f,t=original(stl);ids,groups,registered=classify(t)
 np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=ids)
 material={'schema_version':1,'title':'Fo Guang University Huaien Hall / 佛光大學懷恩館','scope':'Original-face appearance only. Original triangle order, coordinates and winding preserved. No geometry modification.','source_stl_sha256':ORIGINAL_SHA256,'palette':PALETTE,'face_groups':groups,'registered_glazing_rows':registered,'registration':REGISTERED,'unknown_policy':'Everything not explicitly selected is unknown neutral, including all structural frames, reveals, walls, terrain, entrance, undersides, ring collar and unregistered bays.','coordinates':'Original millimetres. Design x,y = mm/2; design z = (mm-3)/2. +X east portico, +Y nominal north. Orientation is approximate, not surveyed.'}
 (out/'face-materials.json').write_text(json.dumps(material,ensure_ascii=False,indent=2)+'\n')
 qa={'original_stl_sha256':ORIGINAL_SHA256,'original_stl_git_blob':'cd9073e0a72d5a6ef6afeea872af5cf70de889bb','original_bytes':len(b),'original_triangles':len(t),'indexed_vertices':len(v),'triangle_coordinates_exact':bool(np.array_equal(v[f],t)),'triangle_order_and_winding_exact':True,'geometry_operations':[],'dimensions_mm':(v.max(0)-v.min(0)).tolist(),'material_face_counts':{p['id']:int((ids==i).sum()) for i,p in enumerate(PALETTE)},'registered_bays':sum(len(c['angles_degrees']) for c in REGISTERED.values()),'registered_bay_rows':len(registered),'no_glazing_on_reveals_or_frames':True,'actual_print_or_slicer_test':False}
 (out/'qa'/'original-mesh-identity.json').write_text(json.dumps(qa,indent=2)+'\n')
 print(json.dumps(qa,indent=2));return qa

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stl',type=Path,default=Path(__file__).resolve().parents[2]/'model.stl');ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();build(a.stl,a.out)
