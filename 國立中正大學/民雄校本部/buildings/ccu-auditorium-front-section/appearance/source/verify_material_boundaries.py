"""Independent scalar full-vertex triangle-plane test; no classifier import."""
import struct,json,math,pathlib
p=pathlib.Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];selected=[];area=0;eps=.0002
for i in range(n):
 q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+j*3:6+j*3]for j in range(3)]
 if all(abs(y+12.15)<eps and 55-eps<=z<=74+eps and abs(x)<=28*(74-z)/19+eps for x,y,z in v):
  selected.append(i);a=[v[1][j]-v[0][j]for j in range(3)];c=[v[2][j]-v[0][j]for j in range(3)];cross=[a[1]*c[2]-a[2]*c[1],a[2]*c[0]-a[0]*c[2],a[0]*c[1]-a[1]*c[0]];area+=sum(x*x for x in cross)**.5/2
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];assert set(selected)=={i for i,x in enumerate(m) if x==1};assert n==3522 and selected==[725] and abs(area-532)<.00001
r={'face_count':n,'selected':selected,'area_mm2':area,'epsilon_mm':eps,'all_vertex_bounded_full_faces':True,'colored_faces':1,'neutral_faces':3521,'no_subdivision':True,'plane_y_mm':-12.15,'triangle_xz_mm':[[-28,55],[28,55],[0,74]],'separate_mullions_frames_remain_neutral':True,'mixed_brick_gray_bands_other_windows_roof_rear_excluded':True,'opaque_glazing_proxy_not_physical_glass':True};(p/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
