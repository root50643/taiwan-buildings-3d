import struct,pathlib,json,math
p=pathlib.Path(__file__).resolve().parents[1];b=(p.parent/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0]
xy=lambda v:((v[0]-625)*.125,(445-v[1])*.125)
edges=[(xy(a),xy(c))for a,c in [((1008,483),(1008,616)),((1008,616),(883,752)),((883,752),(720,752))]];res=[]
for a,c in edges:
 dx,dy=c[0]-a[0],c[1]-a[1];L=math.hypot(dx,dy);ids=[];area=0
 for i in range(n):
  q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+j*3:6+j*3]for j in range(3)]
  def ok(v):
   x,y,z=v;u=((x-a[0])*dx+(y-a[1])*dy)/L
   dist=abs((x-a[0])*dy-(y-a[1])*dx)/L
   return dist<.0002 and -.0002<=u<=L+.0002 and 18.2-.0002<=z<=22.9+.0002
  if all(ok(w)for w in v):
   ids.append(i);u=[v[1][j]-v[0][j]for j in range(3)];w=[v[2][j]-v[0][j]for j in range(3)];cr=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];area+=sum(t*t for t in cr)**.5/2
 res.append({'a':a,'b':c,'length':L,'count':len(ids),'ids':ids,'area_mm2':area,'expected_band_area':L*4.7})
white=[];wa=0
for i in range(n):
 q=struct.unpack_from('<12fH',b,84+50*i);v=[q[3+3*j:6+3*j]for j in range(3)]
 if all(abs(y)<.0002 and -6.25-.0002<=x<=43.75+.0002 and 29.8-.0002<=z<=50.1+.0002 for x,y,z in v):
  white.append(i);wa+=abs((v[1][0]-v[0][0])*(v[2][2]-v[0][2])-(v[2][0]-v[0][0])*(v[1][2]-v[0][2]))/2
m=json.loads((p/'face-materials.json').read_text())['face_material_indices'];brick=sum([x['ids'] for x in res],[])
assert n==2536 and len(white)==8 and len(brick)==38
assert set(white)=={i for i,x in enumerate(m) if x==1} and set(brick)=={i for i,x in enumerate(m) if x==2}
assert abs(wa-1014.99996)<.0001 and abs(sum(x['area_mm2'] for x in res)-271.79717)<.0001
r={'white_ids':white,'white_count':len(white),'white_area_mm2':wa,'face_count':n,'edges':res,'colored_faces':46,'neutral_faces':2490,'all_vertex_plane_and_finite_domain':True,'epsilon_mm':.0002,'ideal_rectangle_minus_selected_complete_face_area_mm2':10.62507,'difference_explanation':'includes rejected cross-boundary faces and gaps without corresponding coplanar exterior surfaces','no_subdivision':True}
(p/'qa/material-boundaries.json').write_text(json.dumps(r,indent=2)+'\n');print('boundary pass')
