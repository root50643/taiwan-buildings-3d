"""Independent scalar complete-vertex plane checks; does not import classifier."""
import struct,json,math,pathlib
p=pathlib.Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];out={'front_upper_wall':[],'front_balcony':[]};areas={k:0 for k in out};eps=.001
for i in range(n):
 q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+j*3:6+j*3]for j in range(3)]
 def accept(k,x,y,z):
  if k=='front_upper_wall':return abs(y+50)<eps and abs(x)<=66+eps and 38.3-eps<=z<=72.8+eps
  return abs(y+66.8)<eps and abs(x)<=35.5+eps and 38.2-eps<=z<=44.5+eps
 for k in out:
  if all(accept(k,*w)for w in v):
   out[k].append(i);a=[v[1][j]-v[0][j]for j in range(3)];c=[v[2][j]-v[0][j]for j in range(3)];cross=[a[1]*c[2]-a[2]*c[1],a[2]*c[0]-a[0]*c[2],a[0]*c[1]-a[1]*c[0]];areas[k]+=sum(x*x for x in cross)**.5/2
selected=set(out['front_upper_wall']+out['front_balcony']);m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];assert selected=={i for i,x in enumerate(m) if x==1};assert n==3110 and len(out['front_upper_wall'])==51 and len(out['front_balcony'])==2
r={'face_count':n,'selected':out,'counts':{k:len(v)for k,v in out.items()},'areas_mm2':areas,'epsilon_mm':eps,'all_vertex_bounded_full_faces':True,'colored_faces':53,'neutral_faces':3057,'no_subdivision':True,'arch_interior_sides_rear_roof_columns_beams_base_excluded':True,'coarse_principal_brick_plane_proxy_not_fine_skin_restoration':True,'unmodeled_gray_caps_lettering_joints_not_reconstructed':True};(p/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
