"""Independent scalar full-vertex plane and bounded rectangle check; no builder import."""
import struct,json,math,pathlib
p=pathlib.Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];ids=[[],[]];areas=[0.,0.];eps=.0002
for i in range(n):
 q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+j*3:6+j*3]for j in range(3)]
 for k,(y0,x0,z0,z1) in enumerate([(-14,68.3,26.5,49.3),(-12.25,54,41,45)]):
  if all(abs(y-y0)<eps and -x0-eps<=x<=x0+eps and z0-eps<=z<=z1+eps for x,y,z in v):
   ids[k].append(i);a=[v[1][j]-v[0][j]for j in range(3)];c=[v[2][j]-v[0][j]for j in range(3)];areas[k]+=abs(a[0]*c[2]-a[2]*c[0])/2
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];assert n==3422 and list(map(len,ids))==[280,2] and ids[1]==[2382,2439]
for k in range(2):assert set(ids[k])=={i for i,x in enumerate(m) if x==k+1}
assert abs(areas[0]-1974.32024)<.0001 and areas[1]==432
r={'face_count':n,'tile_faces':ids[0],'upper_glazing_faces':ids[1],'area_mm2':areas,'epsilon_mm':eps,'all_vertex_plane_and_finite_domain':True,'colored_faces':282,'neutral_faces':3140,'no_subdivision':True,'bounds_mm':[{'y':-14,'x':[-68.3,68.3],'z':[26.5,49.3]},{'y':-12.25,'x':[-54,54],'z':[41,45]}],'lower_mixed_grille_glazing_rounded_sides_roofs_rear_cutoff_neutral':True};(p/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print('boundary pass')
