"""Original public memorial bell-tower interpretation from three official photos.
All dimensions are proportional model-millimeter estimates, not a survey.
No photos, site layout, operational infrastructure or font assets are read.
Requires numpy, trimesh and manifold3d. Four parts, nine appearance materials.
"""
from pathlib import Path
import collections,hashlib,json,math
import numpy as np
import trimesh
from manifold3d import Manifold,Mesh64,CrossSection,OpType
ROOT=Path(__file__).resolve().parents[1]
PALETTE=[('paint_warm_white','#E5E7DD','白柱、環梁及屋帽底面近似'),('cap_red','#C82327','紅帽頂與頂珠近似'),('upper_stone_gray_green','#858D83','上層圓台鋪面近似'),('dark_step_fascia','#434B46','階台深色立邊近似'),('lower_paving_slate','#6C7770','下層圓台灰綠鋪面近似，省略石板紋理'),('bell_dark_bronze','#292B24','逆光吊鐘深色近似，非合金鑑定'),('emblem_gold','#B89844','可見徽記金色側葉的低細節替代'),('emblem_silver','#A4AAA4','可見徽記灰銀形狀的低細節替代'),('emblem_blue','#24465C','可見徽記中央深藍近似')]
MID={p[0]:i for i,p in enumerate(PALETTE)}
def color(s,c):return s.set_properties(1,lambda pos,props:[float(MID[c])])
def union(ps):return Manifold.batch_boolean(ps,OpType.Add)
def cylinder(r,z0,z1,c,n=128):return color(Manifold.cylinder(z1-z0,r,circular_segments=n).translate([0,0,z0]),c)
def box(x0,x1,y0,y1,z0,z1,c='paint_warm_white'):return color(Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0]),c)
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
def curved_column(angle):
 vs=[];fs=[];levels=np.linspace(0,92,47)
 for z in levels:
  q=(z-57)/(57 if z<=57 else 35);r=10.7+(9.3 if z<=57 else 6.0)*q*q;w=4.8+.8*abs(q);depth=3.5
  for x,y in [(r-depth/2,-w/2),(r+depth/2,-w/2),(r+depth/2,w/2),(r-depth/2,w/2)]:vs.append([x,y,z])
 fs += [[0,2,1],[0,3,2]]
 for k in range(len(levels)-1):
  for j in range(4):a=4*k+j;b=4*k+(j+1)%4;fs += [[a,b,b+4],[a,b+4,a+4]]
 k=4*(len(levels)-1);fs += [[k,k+1,k+2],[k,k+2,k+3]]
 s=Manifold(Mesh64(np.asarray(vs),np.asarray(fs,dtype=np.uint64)));assert s.status().name=='NoError'
 return color(s.rotate([0,0,angle]),'paint_warm_white')
def relief_poly(poly,c):
 if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))<0:poly=list(reversed(poly))
 return color(CrossSection([poly]).extrude(1.6).rotate([90,0,0]).translate([0,-11.65,60.5]),c)
def relief_disk(r,c,depth=1.65):
 return color(Manifold.cylinder(depth,r,circular_segments=48).rotate([90,0,0]).translate([0,-11.65,60.5]),c)
def emblem():
 # Simplified original geometry: location, color and broad silhouette only.
 # No claim to reproduce the complete official insignia or its fine lettering.
 ps=[]
 for side in [-1,1]:
  for x,z,a in [(2.5,1.2,25),(3.5,.45,5),(3.6,-.65,-25)]:
   rad=math.radians(a*side);cx=x*side;cy=z
   pts=[]
   for u,v in [(-1.5,0),(-.2,-.45),(1.25,0),(-.2,.45)]:pts.append([cx+u*math.cos(rad)-v*math.sin(rad),cy+u*math.sin(rad)+v*math.cos(rad)])
   ps.append(relief_poly(pts,'emblem_gold'))
 ps += [relief_poly([[-2.2,-1.7],[-1.7,-2.2],[2.0,1.5],[1.5,2.0]],'emblem_silver'),relief_poly([[2.2,-1.7],[1.7,-2.2],[-2.0,1.5],[-1.5,2.0]],'emblem_silver'),relief_disk(1.8,'emblem_silver',1.72),relief_disk(1.5,'emblem_blue',1.82),relief_disk(.64,'paint_warm_white',1.9)]
 for j in range(12):
  a=2*math.pi*j/12;pts=[[.89*math.cos(a-.14),.89*math.sin(a-.14)],[1.35*math.cos(a),1.35*math.sin(a)],[.89*math.cos(a+.14),.89*math.sin(a+.14)]];ps.append(relief_poly(pts,'paint_warm_white').translate([0,-.3,0]))
 return union(ps)
def main():
 for n in ['parts','qa','previews']:(ROOT/n).mkdir(exist_ok=True)
 base=union([cylinder(50,0,1.4,'dark_step_fascia'),cylinder(50,1.4,2.5,'lower_paving_slate'),cylinder(33.5,2.5,4.0,'dark_step_fascia'),cylinder(33.5,4.0,5.0,'upper_stone_gray_green')])
 frameparts=[curved_column(a) for a in [45,135,225,315]]+[ring(12.8,10.2,56,65,'paint_warm_white')]
 for a in [45,135]:frameparts.append(box(-19.0,19.0,-1.7,1.7,90.8,93.5).rotate([0,0,a]))
 em=emblem();frameparts += [em,em.rotate([0,0,90])]
 frame=union(frameparts)
 # Octagonal cap is a photo-based interpretation; exact surveyed plan is unavailable.
 roof=union([cylinder(22,0,1.2,'cap_red',8),color(Manifold.cylinder(9.9,22,.8,circular_segments=8).translate([0,0,1.2]),'cap_red'),cylinder(1.8,10.7,11.5,'cap_red',48),color(Manifold.sphere(1.45,48).translate([0,0,12.0]),'cap_red')]).rotate([0,0,22.5])
 profile=[[2.65,0],[2.65,.55],[2.1,1.0],[1.65,2.0],[1.65,3.6],[1.2,4.2],[0,4.2],[0,3.4],[.9,3.4],[1.0,1.8],[1.8,.3],[1.8,0]]
 cup=color(CrossSection([profile]).revolve(64),'bell_dark_bronze')
 bell=union([cup,cylinder(.65,3.9,7.5,'bell_dark_bronze',32),cylinder(.42,.65,3.6,'bell_dark_bronze',24),color(Manifold.sphere(.68,24).translate([0,0,.85]),'bell_dark_bronze')])
 specs=[('01-two-tier-circular-plinth',base,0,'upright circular plinth; estimated stone thickness'),('02-four-curved-columns-ring-and-crossbeam',frame,5,'upright frame candidate; intermediate ring and top beams need support assessment'),('03-octagonal-red-cap',roof,98.5,'cap underside down; estimated solid roof with white underside and red top'),('04-suspended-bell',bell,88.3,'bell mouth rim on bed; hollow mouth, thickened rigid suspension pin, not a working mechanism')]
 parts=[];points=[]
 for name,s,z,note in specs:
  assert s.status().name=='NoError',(name,s.status());s=s.simplify(.0001);v,f,c=arrays(s);
  if name=='03-octagonal-red-cap':c[np.all(np.abs(v[f,:,][...,2])<1e-8,axis=1)]=MID['paint_warm_white']
  origin=v.min(axis=0);native=(v-origin).astype(np.float32).astype(np.float64);T=np.eye(4);T[:3,3]=origin+[0,0,z]
  tm=trimesh.Trimesh(native,f,process=False);cross=np.cross(native[f[:,1]]-native[f[:,0]],native[f[:,2]]-native[f[:,0]]);zero=int(np.count_nonzero(np.linalg.norm(cross,axis=1)==0));assert zero==0,(name,zero)
  valid=Manifold(Mesh64(native,np.asarray(f,dtype=np.uint64)));assert valid.status().name=='NoError' and len(valid.decompose())==1,(name,valid.status(),len(valid.decompose()));assert tm.is_watertight and tm.is_winding_consistent and tm.volume>0
  p=ROOT/'parts'/(name+'.stl');tm.export(p);rec={'id':name,'stl':str(p.relative_to(ROOT)),'stl_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'vertices':native.tolist(),'triangles':f.tolist(),'material_indices':c.tolist(),'assembly_transform':T.tolist(),'native_bounds_mm':tm.bounds.tolist(),'assembly_note':note,'geometry_check':{'triangles':len(f),'vertices':len(native),'watertight':True,'winding_consistent':True,'positive_volume_mm3':float(tm.volume),'connected_components':1,'zero_area_triangles':zero,'pre_export_simplification_tolerance_mm':.0001},'material_triangle_counts':dict(collections.Counter(PALETTE[i][0] for i in c))};parts.append(rec);points.append(native+T[:3,3])
 pts=np.concatenate(points);d={'units':'millimeter','real_world_scale':'not measured; all model dimensions are proportional estimates','materials':[{'id':n,'srgb':c,'interpretation':t} for n,c,t in PALETTE],'parts':parts,'assembled_bounds_mm':[pts.min(axis=0).tolist(),pts.max(axis=0).tolist()],'assembled_dimensions_mm':np.ptp(pts,axis=0).tolist(),'source_scope':'Three official public memorial views; four curved columns, circular open ring, two-tier round plinth, photo-interpreted octagonal cap and suspended bell. Two visible emblem positions simplified; hidden embellishments omitted.','manufacturing':'Four separate candidates; native orientations are not slicer-validated. No physical print, fitted joint, support removal or tool mapping verified.'}
 (ROOT/'geometry.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n');summary={k:v for k,v in d.items() if k!='parts'};summary['parts']=[{k:v for k,v in p.items() if k not in ['vertices','triangles','material_indices']} for p in parts];(ROOT/'qa/build-geometry.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'dimensions':d['assembled_dimensions_mm'],'parts':[(p['id'],p['geometry_check']) for p in parts]},ensure_ascii=False))
if __name__=='__main__':main()
