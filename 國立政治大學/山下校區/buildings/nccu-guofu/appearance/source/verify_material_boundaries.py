import struct,json,math,pathlib
p=pathlib.Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];out={'main_front':[],'left_inner':[]};areas={k:0 for k in out};eps=2e-4
for i in range(n):
 q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+j*3:6+j*3]for j in range(3)]
 def accept(k,x,y,z):
  t=(z-27.2)/4
  if not -eps<=t<=1+eps:return False
  if k=='main_front':return abs(y-(6+9.7*t))<eps and abs(x)<=67.5-18.9*t+eps
  return abs(x-(-36.5-15.035*t))<eps and abs(y-2)<=24-7.68*t+eps
 for k in out:
  if all(accept(k,*w)for w in v):
   out[k].append(i);a=[v[1][j]-v[0][j]for j in range(3)];c=[v[2][j]-v[0][j]for j in range(3)];cross=[a[1]*c[2]-a[2]*c[1],a[2]*c[0]-a[0]*c[2],a[0]*c[1]-a[1]*c[0]];areas[k]+=sum(x*x for x in cross)**.5/2
selected=set(out['main_front']+out['left_inner']);m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];assert selected=={i for i,x in enumerate(m) if x==1};assert n==1020 and len(out['main_front'])==10 and len(out['left_inner'])==9
r={'face_count':n,'selected':out,'counts':{k:len(v)for k,v in out.items()},'areas_mm2':areas,'epsilon_mm':eps,'all_vertex_bounded_full_faces':True,'colored_faces':19,'neutral_faces':1001,'no_subdivision':True,'all_other_slopes_ridges_eaves_walls_windows_base_excluded':True};(p/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
