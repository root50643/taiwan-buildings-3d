from pathlib import Path
import json,hashlib,subprocess,os
# Optional Matplotlib obtains its own temporary cache when --plot is requested.
import numpy as np
from shapely.geometry import LineString,Polygon,Point,box as shbox
from shapely.ops import polygonize,unary_union
import argparse,tempfile
parser=argparse.ArgumentParser(description='Bounded LTU original-STL physical support evidence. Does not approve any thickness exception.')
parser.add_argument('--stl',type=Path,default=Path('model.stl'))
parser.add_argument('--parameters',type=Path,default=Path('source-parameters.json'))
parser.add_argument('--output',type=Path,default=Path('ltu-concave-evidence'))
parser.add_argument('--plot',action='store_true',help='Optionally render sections; requires matplotlib')
args=parser.parse_args();O=args.output;O.mkdir(parents=True,exist_ok=True)
_tmp_context=tempfile.TemporaryDirectory(prefix='ltu-concave-');TMP=Path(_tmp_context.name)
HERE=Path(__file__).resolve().parent
STL=args.stl;PARAMETERS=args.parameters
for source,binary in [('ltu-concave-strict-ray.cpp','strict-ray'),('ltu-concave-winding.cpp','winding')]:
 subprocess.run(['g++','-O2','-std=c++17','-fopenmp',str(HERE/source),'-o',str(TMP/binary)],check=True)
sha=hashlib.sha256(STL.read_bytes()).hexdigest();assert sha=='b83ae9af72a556f200762afe11e13cd55cff55243a5dc03a38760ff971d17f74'
# Independently reread frozen binary STL. Triangle order and original float32 coordinates remain unchanged.
b=STL.read_bytes();count=int.from_bytes(b[80:84],'little');dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);raw=np.frombuffer(b,dt,count=count,offset=84);T=raw['v'].astype(float)
T.tofile(TMP/'original-triangles.bin')
params=json.load(open(PARAMETERS));scale=params['scale_mm_per_m'];rot=np.array(params['rotation_xy']);center=np.array(params['rotated_center_m']);
def toq(x):
 a=np.array(x,dtype=float).copy();a[...,:2]=(a[...,:2]+center*scale)@rot;return a
def tow(x):
 a=np.array(x,dtype=float).copy();a[...,:2]=a[...,:2]@rot.T-center*scale;return a
Q=toq(T); normals=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
keys={(915,1),(910,2),(912,3),(1500,3)};rs=[]
for f,sample,ex,bary in [(915,1,986,[.98,.01,.01]),(910,2,987,[.01,.98,.01]),(912,3,987,[.01,.01,.98]),(1500,3,1501,[.01,.01,.98])]:
 rs.append({'face':f,'sample':sample,'surface_mm':(np.array(bary)@T[f]).tolist(),'normal_exit_face':ex,'normal':{'first_span':None}})
apex=toq(T[915,0]);maxx=Q[1500,:,0].mean();rooty=Q[1500,[0,2],1].mean();pz=rs[-1]['surface_mm'][2]
records=[]
for r in rs:
 q=toq(r['surface_mm']);f=r['face'];ex=r['normal_exit_face'];records.append({'face':f,'sample':r['sample'],'surface_world_mm':r['surface_mm'],'surface_building_mm':q.tolist(),'surface_source_metres':[*list(q[:2]/scale),float(q[2]/scale-.65)],'source_triangle_world_mm':T[f].tolist(),'source_triangle_source_metres':np.c_[Q[f,:,:2]/scale,Q[f,:,2]/scale-.65].tolist(),'source_outward_normal_world':normals[f].tolist(),'exit_face':ex,'exit_triangle_world_mm':T[ex].tolist(),'exit_outward_normal_world':normals[ex].tolist(),'original_normal_first_material_mm':r['normal']['first_span']})
# Every physical direction fixed from source design before measurement: print -Z, front-wall tangent -X,
# front-wall thickness +Y, and fourth rear attachment toward the actual vertical core -Y. No direction search.
queries=[];qr=[]
for r in rs:
 p=np.array(r['surface_mm']);n=-normals[r['face']];inside=p+.01*n;q=toq(inside)
 queries.append([p-1e-5*n,n]);qr.append({'face':r['face'],'sample':r['sample'],'role':'original_normal_independent_recheck','origin_world_mm':(p-1e-5*n).tolist(),'direction_world':n.tolist()})
 for name,dq in [('print_down',[0,0,-1]),(('front_wall_rootward' if r['face']!=1500 else 'rear_corner_toward_core'),([-1,0,0] if r['face']!=1500 else [0,-1,0]))]:
  dw=np.array(dq,dtype=float);dw[:2]=dw[:2]@rot.T;queries.append([inside,dw]);qr.append({'face':r['face'],'sample':r['sample'],'role':name,'original_normal_inset_mm':.01,'origin_world_mm':inside.tolist(),'direction_world':dw.tolist()})
 if r['face']!=1500:
  for station in [0,.25,.5,1.0]:
   origin=toq(p);origin[0]-=station;origin[1]=-.01;dw=np.array([*rot[:,1],0]);queries.append([tow(origin),dw]);qr.append({'face':r['face'],'sample':r['sample'],'role':'front_wall_plus_Y_width','rootward_station_mm':station,'origin_world_mm':tow(origin).tolist(),'direction_world':dw.tolist()})
np.array(queries).tofile(TMP/'queries.bin');subprocess.run([str(TMP/'strict-ray'),str(TMP/'original-triangles.bin'),str(TMP/'queries.bin'),str(O/'ltu-concave-physical-ray-hits.csv')],check=True)
for r,line in zip(qr,(O/'ltu-concave-physical-ray-hits.csv').read_text().splitlines()):
 h,bound=line.split('|');events=[]
 for s in h.split(';')[1:]:
  if s:events.append([float(a)for a in s.split(',')])
 r['raw_events']=events;r['boundary_intervals']=bound
 if r['role']in ['front_wall_plus_Y_width','original_normal_independent_recheck']:r['first_material_width_mm']=events[1][0]-events[0][0]
 else:r['first_exit_mm']=events[0][0]
for rec in records:
 rec['original_normal_first_material_mm']=next(r['first_material_width_mm']for r in qr if r['role']=='original_normal_independent_recheck'and r['face']==rec['face'])
# Finite-volume certificate: no ORIGINAL boundary triangle intersects or lies inside each closed OBB.
# SAT includes box axes, triangle normal, and 9 triangle-edge x box-edge axes; long double.
# A full-mesh winding=1 at the centre then proves the whole connected box interior is material.
boxes=[]
def addbox(name,lo,hi,role,face_samples):
 lo=np.array(lo);hi=np.array(hi);boxes.append({'name':name,'building_mm_bounds':[lo.tolist(),hi.tolist()],'dimensions_mm':(hi-lo).tolist(),'volume_mm3':float(np.prod(hi-lo)),'box_face_areas_mm2':{'xy':float((hi[0]-lo[0])*(hi[1]-lo[1])),'xz':float((hi[0]-lo[0])*(hi[2]-lo[2])),'yz':float((hi[1]-lo[1])*(hi[2]-lo[2]))},'role':role,'face_samples':face_samples})
for r in rs[:3]:
 q=toq(r['surface_mm']);addbox(f'base_beneath_{r["face"]}_{r["sample"]}',[q[0]-.8,q[1]-.8,.05],[q[0]+.8,q[1]+.8,.85],'0.8 mm thick broad solid base directly beneath flagged original point',[[r['face'],r['sample']]])
fs=[[r['face'],r['sample']]for r in rs[:3]]
addbox('southeast_corner_positive_volume_connector',[apex[0]-.5,.005,.05],[apex[0]-.05,.05,1.10],'Contains all three original-normal inset points; overlaps broad base and rootward connector',fs)
addbox('southeast_corner_rootward_connector',[apex[0]-1.5,.005,.05],[apex[0]-.4,.55,1.2],'Overlaps tip connector and bulk root box; physically selected front-wall longitudinal direction',fs)
addbox('southeast_corner_bulk_root',[apex[0]-2.2,.01,.05],[apex[0]-1.2,1.01,1.25],'1 x 1 x 1.2 mm certified bulk root in the same wedge/base material',fs)
addbox('rear_triangle_positive_volume_attachment',[maxx-.4,rooty-.4,pz-.4],[maxx-.005,rooty+.01,pz+.1],'Contains 1500/3 inward-offset point and straddles actual rear-core attachment plane',[[1500,3]])
addbox('rear_triangle_full_height_attachment',[maxx-.4,rooty-.4,float(Q[1500,:,2].min())+.01],[maxx-.005,rooty+.01,float(Q[1500,:,2].max())-.01],'Continuous positive-volume bridge across rear attachment for all but 0.01 mm at either original vertical endpoint',[[1500,3]])
addbox('rear_core_bulk_root',[maxx-.5,rooty-1.,pz-.4],[maxx+.5,rooty-.1,pz+.4],'1 x 0.9 x 0.8 mm certified solid core immediately behind rear triangular corner',[[1500,3]])
A=Q.astype(np.longdouble);edges=np.roll(A,-1,axis=1)-A;axes=[np.broadcast_to(np.eye(3,dtype=np.longdouble)[k],(len(A),3)).copy()for k in range(3)];axes += [np.cross(edges[:,0],edges[:,1])]
for e in range(3):
 for k in range(3):axes.append(np.cross(edges[:,e],np.eye(3,dtype=np.longdouble)[k]))
axes=np.stack(axes,1);lens=np.sqrt(np.sum(axes*axes,axis=-1));good=lens>1e-25;axes[good]/=lens[good,None];axes[~good]=0
centres=[]
for b in boxes:
 lo,hi=np.array(b['building_mm_bounds'],dtype=np.longdouble);c=(lo+hi)/2;half=(hi-lo)/2;local=A-c;pr=np.einsum('fvc,fac->fav',local,axes);rad=np.sum(np.abs(axes)*half,axis=-1);sep=np.maximum(pr.min(2)-rad,-rad-pr.max(2));sep[~good]=-np.inf;best=sep.max(1);bad=np.where(best<=1e-9)[0];b['all_original_triangles_tested']=len(A);b['boundary_intersection_or_ambiguous_faces']=bad.tolist();b['minimum_separating_axis_margin_mm']=float(best.min());b['all_boundary_triangles_strictly_disjoint']=len(bad)==0;b['centre_world_mm']=tow(c).tolist();centres.append(tow(c));print('BOX',b['name'],len(bad),float(best.min()),flush=True)
np.array(centres).tofile(TMP/'centres.bin');subprocess.run([str(TMP/'winding'),str(TMP/'original-triangles.bin'),str(TMP/'centres.bin'),str(O/'ltu-concave-box-winding.csv')],check=True)
for b,line in zip(boxes,(O/'ltu-concave-box-winding.csv').read_text().splitlines()):
 b['full_original_mesh_centre_winding']=float(line.split(',')[1]);b['certified_entire_closed_box_inside_material']=b['all_boundary_triangles_strictly_disjoint']and abs(b['full_original_mesh_centre_winding']-1)<1e-10
# Explicit positive-volume overlap graph and original-normal-inset containment.
box_connections=[]
for i,bi in enumerate(boxes):
 li,hi=np.array(bi['building_mm_bounds'])
 for j,bj in enumerate(boxes[:i]):
  lj,hj=np.array(bj['building_mm_bounds']);over=np.minimum(hi,hj)-np.maximum(li,lj)
  if np.all(over>1e-9):box_connections.append({'a':bi['name'],'b':bj['name'],'overlap_dimensions_mm':over.tolist(),'overlap_volume_mm3':float(np.prod(over)),'overlap_projected_areas_mm2':{'xy':float(over[0]*over[1]),'xz':float(over[0]*over[2]),'yz':float(over[1]*over[2])}})
for r in records:
 p=np.array(r['surface_world_mm']);inside=toq(p-.01*np.array(r['source_outward_normal_world']));r['normal_inset_0_01_building_mm']=inside.tolist();r['inset_strictly_inside_certified_boxes']=[]
 for b in boxes:
  lo,hi=np.array(b['building_mm_bounds']);margin=float(min(np.min(inside-lo),np.min(hi-inside)))
  if margin>1e-9:r['inset_strictly_inside_certified_boxes'].append({'name':b['name'],'containment_margin_mm':margin})
 assert r['inset_strictly_inside_certified_boxes']
# Original-triangle horizontal cuts for location and local shape. Round 8 decimals only to join the
# plotting polygon network; never used by SAT, winding or strict ray predicates.
def section(z):
 seg=[];faces=[]
 for f,t in enumerate(Q):
  d=t[:,2]-z;pts=[]
  for i,j in [(0,1),(1,2),(2,0)]:
   if d[i]*d[j]<0:pts.append(t[i,:2]+(t[j,:2]-t[i,:2])*(-d[i])/(d[j]-d[i]))
  if len(pts)==2:seg.append(np.array(pts));faces.append(f)
 lines=[LineString(np.round(s,8))for s in seg];polys=list(polygonize(unary_union(lines)));return seg,faces,polys
sections=[]
zs=[.5,rs[1]['surface_mm'][2],rs[0]['surface_mm'][2],25.8,pz]
for z in zs:
 seg,faces,polys=section(z);sections.append({'z_world_mm':z,'segment_count':len(seg),'segments_building_xy_mm':np.array(seg).tolist(),'original_triangle_ids':faces,'polygon_join_rounding_mm':1e-8,'joined_polygon_areas_mm2':[p.area for p in polys]})
# Exact 1500 and 1501 intersections with flagged horizontal plane determine protruding triangle edges.
def cutface(f,z):
 t=Q[f];d=t[:,2]-z;pts=[]
 for i,j in [(0,1),(1,2),(2,0)]:
  if d[i]*d[j]<0:pts.append(t[i]+(t[j]-t[i])*(-d[i])/(d[j]-d[i]))
 return np.array(pts)
f1500=cutface(1500,pz);f1501=cutface(1501,pz);# each spans one piece; combined planes define original rear triangle
# Source-oriented rear root line y=rooty, evaluate exact original face planes on z=pz.
Nq=np.cross(Q[:,1]-Q[:,0],Q[:,2]-Q[:,0]);Nq/=np.linalg.norm(Nq,axis=1)[:,None]
def x_at_y(f,y,z):
 n=Nq[f];return float((np.dot(n,Q[f,0])-n[1]*y-n[2]*z)/n[0])
xright=x_at_y(1500,rooty,pz);xleft=x_at_y(1501,rooty,pz);ap=np.array([Q[1500,1,0],Q[1500,1,1]]);width=xright-xleft;depth=ap[1]-rooty;height=float(Q[1500,:,2].max()-Q[1500,:,2].min())
rear={'root_building_y_mm':float(rooty),'attachment_root_width_mm':float(width),'maximum_projection_depth_mm':float(depth),'vertical_attachment_extent_mm':height,'nominal_rectangular_attachment_area_mm2':float(width*height),'horizontal_triangular_projection_area_mm2':float(width*depth/2),'source_mechanism':'G.buffer(-0.15) intersect rear strip and xa=23..32.3 upper step (z16.4..25.1) adjoining vertical core box (xcore±2.75,ycore±4,z0..27.2). Original visible section ends z25.06 because wall/cap Boolean union. keep_core protects core from window cutters, but is a cutter mask, not added material.','caution':'Actual narrow triangle attachment width is approximately 0.589 mm, below 0.8 mm. It is a shallow, continuously side-backed projection onto a certified bulk core, not evidence that every local normal thickness or every attachment transverse width is >=0.8 mm.'}
# Inspectable compact figures, in actual millimetres.
if args.plot:
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axs=plt.subplots(1,2,figsize=(12,6))
 for ax,z,lim,title in [(axs[0],rs[0]['surface_mm'][2],[apex[0]-2.5,apex[0]+.2,-.2,2.5],'Southeast corner at z=1.078406 mm'),(axs[1],pz,[maxx-1.2,maxx+.7,rooty-1.2,rooty+.65],'Rear corner at z=38.406529 mm')]:
  seg,faces,polys=section(z)
  for poly in polys:
   inter=poly.intersection(shbox(*[lim[0],lim[2],lim[1],lim[3]]))
   geoms=[inter]if inter.geom_type=='Polygon'else list(getattr(inter,'geoms',[]))
   for pp in geoms:
    if pp.geom_type=='Polygon':ax.fill(*np.array(pp.exterior.coords).T,color='#b7d4e8',alpha=.8)
  for s,f in zip(seg,faces):
   if np.max(s[:,0])>=lim[0]and np.min(s[:,0])<=lim[1]and np.max(s[:,1])>=lim[2]and np.min(s[:,1])<=lim[3]:ax.plot(*s.T,'k-',lw=1)
  for r in records:
   q=np.array(r['surface_building_mm']);
   if lim[0]<q[0]<lim[1]and lim[2]<q[1]<lim[3]:ax.plot(q[0],q[1],'ro');ax.annotate(f'{r["face"]}/{r["sample"]}',q[:2],xytext=({915:(-18,52),910:(-45,15),912:(-28,33)}.get(r['face'],(5,6))),textcoords='offset points',fontsize=9,arrowprops={'arrowstyle':'-','color':'#b22','lw':.6})
  for b in boxes:
   lo,hi=np.array(b['building_mm_bounds']);
   if lo[2]<z<hi[2]:ax.add_patch(plt.Rectangle(lo[:2],hi[0]-lo[0],hi[1]-lo[1],fill=False,ec='#167f38',lw=1.5))
  ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(title);ax.set_xlabel('Building X (mm)');ax.set_ylabel('Building Y (mm)')
 axs[1].axhline(rooty,color='#a7511c',ls='--',lw=1);axs[1].text(maxx-1.15,rooty+.43,f'Projection depth {depth:.6f} mm\nRoot width {width:.6f} mm',fontsize=9)
 fig.suptitle('Frozen LTU original-STL sections; green rectangles are full-volume SAT+winding certificates',fontsize=11);fig.tight_layout();fig.savefig(O/'ltu-concave-core-sections.png',dpi=180);plt.close(fig)
out={'stl_sha256':sha,'original_triangles':len(T),'status':'Independent physical backing evidence only; acceptance decision belongs to parent reviewer. Strict original-normal thickness still fails.','method':{'coordinate_transform':'Exact source rotation/translation, no geometry changes; original STL float32 triangles preserved','box_proof':'All 7080 original boundary triangles strictly disjoint from each closed oriented box by full 13-axis triangle/box SAT in long double (ambiguity tolerance 1e-9 mm), plus full-original-mesh long-double compensated solid-angle winding at centre = 1. This proves whole box interior material, not merely sampled points.','direction_selection':'Only print -Z and known source wall/core axes. Selected before intersection measurements; no angular maximum search.','slice_limit':'1e-8 mm endpoint joining for figure only; original segment coordinates and face IDs retained.','global_limit':'Does not establish global minimum wall thickness, strength, or general manufacturability.'},'fixed_building_axes_world':{'plus_X':[float(rot[0,0]),float(rot[1,0]),0.],'plus_Y':[float(rot[0,1]),float(rot[1,1]),0.],'print_down':[0.,0.,-1.]},'flagged_points':records,'physical_rays':qr,'solid_box_certificates':boxes,'positive_volume_box_connections':box_connections,'rear_triangle_attachment':rear,'sections':sections}
(O/'ltu-concave-core-proof.json').write_text(json.dumps(out,indent=2,allow_nan=False));print('REAR',rear,flush=True);print('RAYS',[(r['face'],r['role'],r.get('rootward_station_mm'),r.get('first_material_width_mm',r.get('first_exit_mm')))for r in qr],flush=True)
