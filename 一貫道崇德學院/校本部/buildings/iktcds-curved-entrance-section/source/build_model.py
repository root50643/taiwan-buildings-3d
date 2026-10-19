"""Original bounded Chong-De ground-floor entrance facade segment.
Seven selected columns/six bays/three portals, not the entire colonnade or school.
All dimensions, curvature and simplified ornament are visual estimates. No photos
are embedded or required. Existing numpy/trimesh/manifold3d only.
"""
from pathlib import Path
import collections,hashlib,json,math
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh64,CrossSection,OpType
ROOT=Path(__file__).resolve().parents[1]
PALETTE=[('column_cream','#DCCFB5','近照米白柱與簡化柱頭'),('entablature_ivory','#D6C7AC','近照弧簷米白近似'),('granite_gray','#999C94','近階花崗岩灰近似，沒有照片貼圖'),('glazing_graygreen','#53645E','深灰綠玻璃反射近似，不透明表面色'),('frame_pale','#CBCBBE','淺色窗格近似'),('door_wood_redbrown','#633B2C','三組可見門框木褐近似，非樹種鑑定'),('pediment_darkbrown','#3D3027','可見木色門頂深褐近似'),('cut_neutral','#AAA49B','模型裁切面與估計背板，非實物外牆材質')]
MID={p[0]:i for i,p in enumerate(PALETTE)}
RADIUS=118.0;LIMIT=32.7;COL_ANGLES=np.linspace(-28,28,7);PORTALS=[(COL_ANGLES[i]+COL_ANGLES[i+1])/2 for i in [0,2,4]]
def color(s,c):return s.set_properties(1,lambda pos,props:[float(MID[c])])
def union(ps):return Manifold.batch_boolean(ps,OpType.Add)
def cylinder(r,z0,z1,c,n=128):return color(Manifold.cylinder(z1-z0,r,circular_segments=n).translate([0,0,z0]),c)
def box(x0,x1,y0,y1,z0,z1,c='column_cream'):return color(Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0]),c)
def ring(ro,ri,z0,z1,c,n=128):return cylinder(ro,z0,z1,c,n)-cylinder(ri,z0-.1,z1+.1,c,n)
def arrays(s):
 assert s.status().name=='NoError'
 m=s.to_mesh64();v=np.asarray(m.vert_properties);f=np.asarray(m.tri_verts,dtype=np.int64);cs=v[f,3];assert np.max(np.ptp(cs,axis=1))<1e-8;ids=np.rint(cs[:,0]).astype(int)
 xyz=v[:,:3].astype(np.float32).astype(np.float64);lookup={};verts=[];faces=[]
 for face in f:
  row=[]
  for i in face:
   key=tuple(xyz[i])
   if key not in lookup:lookup[key]=len(verts);verts.append(key)
   row.append(lookup[key])
  faces.append(row)
 return np.asarray(verts),np.asarray(faces,dtype=np.int64),ids
def polygon(points,z,h,c):
 if sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))<0:points=list(reversed(points))
 return color(CrossSection([points]).extrude(h).translate([0,0,z]),c)
def arc(ri,ro,a,b,z,h,c):
 angles=np.linspace(math.radians(a),math.radians(b),max(2,int(math.ceil((b-a)/.5))+1));points=[[ro*math.sin(t),ro*math.cos(t)-RADIUS] for t in angles]+[[ri*math.sin(t),ri*math.cos(t)-RADIUS] for t in angles[::-1]]
 return polygon(points,z,h,c)
def localbox(w,d,z,h,a,r,c):
 q=box(-w/2,w/2,-d/2,d/2,z,z+h,c).rotate([0,0,-a]);t=math.radians(a);return q.translate([r*math.sin(t),r*math.cos(t)-RADIUS,0])
def column():
 ps=[cylinder(3.7,0,1.2,'column_cream',96),cylinder(3.2,1.2,2.4,'column_cream',96),cylinder(2.65,2.4,3.7,'column_cream',96)]
 # Twenty broad flute-like grooves are a display simplification, not a measured count.
 pts=[]
 for a in np.linspace(0,2*math.pi,240,endpoint=False):
  r=2.2-.15*(.5+.5*math.cos(20*a));pts.append([r*math.cos(a),r*math.sin(a)])
 ps.append(polygon(pts,3.6,34.4,'column_cream'))
 ps += [cylinder(2.45,37.9,38.8,'column_cream',96),color(Manifold.cylinder(2.4,2.45,3.3,circular_segments=96).translate([0,0,38.7]),'column_cream'),cylinder(3.4,41.0,42.0,'column_cream',96),box(-3.6,3.6,-3.6,3.6,41.9,43.0)]
 return union(ps)
def facade_grid():
 ri=RADIUS+11.0;grid=np.linspace(-math.radians(LIMIT)*ri,math.radians(LIMIT)*ri,43);us=[-math.radians(LIMIT)*ri,math.radians(LIMIT)*ri]
 for u in grid:us.extend([max(grid[0],u-.35),min(grid[-1],u+.35)])
 for a in PORTALS:
  u=math.radians(a)*ri;us.extend(u+x for x in np.arange(-5,5.01,.5));us.extend([u-3.85,u+3.85,u-2.995,u-.445,u+.445,u+2.995])
 us=sorted(set(round(float(u),5) for u in us));zs=sorted(set([0,.8,5,8,8.8,16,16.8,21.2,24,24.2,24.8,25,32,32.8,40,40.8,42.2,43]+list(np.arange(25.5,29.1,.5))))
 verts=[]
 for r in [ri,ri+2.6]:
  for z in zs:
   for u in us:verts.append([r*math.sin(u/ri),r*math.cos(u/ri)-RADIUS,z])
 n=len(us);N=n*len(zs);front=[]
 for j in range(len(zs)-1):
  for i in range(n-1):
   a=j*n+i;b=a+1;c=a+n;d=c+1;front.extend([[a,b,d],[a,d,c]])
 faces=front+[[a+N,c+N,b+N] for a,b,c in front];edges={}
 for f in front:
  for a,b in zip(f,f[1:]+f[:1]):
   if (b,a) in edges:del edges[(b,a)]
   else:edges[(a,b)]=True
 for a,b in edges:faces.extend([[b,a,a+N],[b,a+N,b+N]])
 q=Manifold(Mesh64(np.asarray(verts),np.asarray(faces,dtype=np.uint64)));assert q.status().name=='NoError';return color(q,'glazing_graygreen')
def facade_materials(v,f):
 c=np.full(len(f),MID['cut_neutral']);ri=RADIUS+11;cent=v[f].mean(axis=1);rad=np.hypot(cent[:,0],cent[:,1]+RADIUS);u=np.arctan2(cent[:,0],cent[:,1]+RADIUS)*ri;z=cent[:,2];grid=np.linspace(-math.radians(LIMIT)*ri,math.radians(LIMIT)*ri,43)
 for i in np.where(rad<ri+.1)[0]:
  idx=MID['glazing_graygreen']
  if min(abs(u[i]-grid))<.351 or any(h-.0001<=z[i]<=h+.8001 for h in [0,8,16,24,32,40,42.2]):idx=MID['frame_pale']
  for a in PORTALS:
   du=u[i]-math.radians(a)*ri
   if abs(du)<3.85 and z[i]<24.2:
    idx=MID['door_wood_redbrown']
    if .445<abs(du)<2.995 and 5<z[i]<21.2:idx=MID['glazing_graygreen']
   if 24.2<=z[i]<25 and abs(du)<5:idx=MID['pediment_darkbrown']
   if 25<=z[i]<29 and abs(du)<5*(29-z[i])/4:idx=MID['pediment_darkbrown']
  c[i]=idx
 return c
def main():
 for n in ['parts','qa','previews']:(ROOT/n).mkdir(exist_ok=True)
 base=union([arc(RADIUS-22,RADIUS+15,-LIMIT,LIMIT,0,1.2,'granite_gray'),arc(RADIUS-17,RADIUS+15,-LIMIT,LIMIT,1.15,1.25,'granite_gray'),arc(RADIUS-12,RADIUS+15,-LIMIT,LIMIT,2.35,1.25,'granite_gray'),arc(RADIUS-7,RADIUS+15,-LIMIT,LIMIT,3.55,1.25,'granite_gray')])
 roof=union([arc(RADIUS-4.5,RADIUS+14.0,-LIMIT,LIMIT,0,1.2,'entablature_ivory'),arc(RADIUS-3.5,RADIUS+14.0,-LIMIT,LIMIT,1.15,3.0,'entablature_ivory'),arc(RADIUS-4.8,RADIUS+14.5,-LIMIT,LIMIT,4.1,1.1,'entablature_ivory'),arc(RADIUS-5.2,RADIUS+15.0,-LIMIT,LIMIT,5.15,.85,'entablature_ivory')])
 specs=[('01-curved-stepped-platform',base,'Four platform levels are an explicit low-step display approximation, not measured stair count'),('02-column-prototype',column(),'Print quantity seven; simplified flute count and capital, not exact Corinthian carving'),('03-curved-glazing-and-three-portals',facade_grid(),'Display backing closes the unknown interior; front glazing grids/door frames/pediments are surface-color approximations only; back and ends are cut surfaces'),('04-curved-entablature-section',roof,'Top is a model cut above ground floor; upper building not included')]
 parts=[];origins={}
 for name,solid,note in specs:
  solid=solid if name=='03-curved-glazing-and-three-portals' else solid.simplify(.001);v,f,c=arrays(solid)
  if name=='03-curved-glazing-and-three-portals':c=facade_materials(v,f)
  if name=='04-curved-entablature-section':c[np.all(np.abs(v[f,:,][...,2]-6)<.0002,axis=1)]=MID['cut_neutral']
  # Radial end cuts are neutral and visibly identified in the delivered scene/docs.
  if name!='02-column-prototype':
   cc=v[f].mean(axis=1);theta=np.degrees(np.arctan2(cc[:,0],cc[:,1]+RADIUS));c[np.abs(np.abs(theta)-LIMIT)<.002]=MID['cut_neutral']
  origin=v.min(axis=0);native=(v-origin).astype(np.float32).astype(np.float64);origins[name]=origin
  tm=trimesh.Trimesh(native,f,process=False);cross=np.cross(native[f[:,1]]-native[f[:,0]],native[f[:,2]]-native[f[:,0]]);zero=int(np.count_nonzero(np.linalg.norm(cross,axis=1)==0));assert zero==0,(name,zero)
  valid=Manifold(Mesh64(native,np.asarray(f,dtype=np.uint64)));assert valid.status().name=='NoError' and len(valid.decompose())==1,(name,valid.status());assert tm.is_watertight and tm.is_winding_consistent and tm.volume>0
  p=ROOT/'parts'/(name+'.stl');tm.export(p);parts.append({'id':name,'stl':str(p.relative_to(ROOT)),'stl_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'vertices':native.tolist(),'triangles':f.tolist(),'material_indices':c.tolist(),'native_bounds_mm':tm.bounds.tolist(),'assembly_note':note,'geometry_check':{'triangles':len(f),'vertices':len(native),'watertight':True,'winding_consistent':True,'positive_volume_mm3':float(tm.volume),'connected_components':1,'zero_area_triangles':zero,'pre_export_simplification_tolerance_mm':0 if name=='03-curved-glazing-and-three-portals' else .001},'material_triangle_counts':dict(collections.Counter(PALETTE[i][0] for i in c))})
 instances=[]
 for name,z in [('01-curved-stepped-platform',0),('03-curved-glazing-and-three-portals',4.8),('04-curved-entablature-section',47.8)]:
  T=np.eye(4);T[:3,3]=origins[name]+[0,0,z];instances.append({'id':name,'prototype':name,'transform':T.tolist()})
 for i,a in enumerate(COL_ANGLES):
  t=math.radians(float(a));rot=np.array([[math.cos(t),math.sin(t),0],[-math.sin(t),math.cos(t),0],[0,0,1]]);T=np.eye(4);T[:3,:3]=rot;T[:3,3]=rot@origins['02-column-prototype']+[RADIUS*math.sin(t),RADIUS*math.cos(t)-RADIUS,4.8];instances.append({'id':'column-'+str(i+1),'prototype':'02-column-prototype','transform':T.tolist()})
 point=[];lookup={p['id']:p for p in parts}
 for inst in instances:
  T=np.asarray(inst['transform']);point.append(np.asarray(lookup[inst['prototype']]['vertices'])@T[:3,:3].T+T[:3,3])
 point=np.concatenate(point);d={'units':'millimeter','real_world_scale':'No measured scale; curvature, dimensions and thickness are proportional display estimates','materials':[{'id':n,'srgb':c,'interpretation':t} for n,c,t in PALETTE],'parts':parts,'instances':instances,'assembled_bounds_mm':[point.min(axis=0).tolist(),point.max(axis=0).tolist()],'assembled_dimensions_mm':np.ptp(point,axis=0).tolist(),'source_scope':'A selected ground-floor seven-column/six-bay/three-portal entrance segment only. Not the entire colonnade, teaching building or campus. Left/right/back/top are explicit model cuts.','manufacturing':'Four prototype STL files, ten physical pieces (seven columns). No FFF slicing, physical print, tolerance, adhesive, support removal or tool mapping validated.'}
 (ROOT/'geometry.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n');summary={k:v for k,v in d.items() if k not in ['parts']};summary['parts']=[{k:v for k,v in p.items() if k not in ['vertices','triangles','material_indices']} for p in parts];(ROOT/'qa/build-geometry.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'dimensions':d['assembled_dimensions_mm'],'parts':[(p['id'],p['geometry_check']) for p in parts]},ensure_ascii=False))
if __name__=='__main__':main()
