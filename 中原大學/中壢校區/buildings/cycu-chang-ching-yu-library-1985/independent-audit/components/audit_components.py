"""CYCU library independent exact original-STL 0.2 mm polygons and 47 local roots.
Original binary float32 vertices promoted to double. Never repair/round mesh/sections.
Formal opening only original polygons. True corners include outer and hole turns.
"""
from pathlib import Path
import numpy as np,json,gzip,hashlib,struct,sys,platform,collections,argparse
import shapely
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from shapely import wkt
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model-dir',type=Path,default=Path(__file__).resolve().parents[2],help='Directory containing original model.stl and feature-loss-locations.json.gz')
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'recheck'/'components',help='Output directory; use a new empty directory')
args=parser.parse_args();B=args.model_dir;O=args.output
assert B.is_dir(), 'Model directory does not exist'
assert O.resolve()!=B.resolve(), 'Do not write into the original model directory'
assert O.resolve()!=Path(__file__).resolve().parent, 'Do not overwrite static reference evidence'
O.mkdir(parents=True,exist_ok=True)
S=B/'model.stl';H='76939c4a6901112a66b76a6c87de5b76829de584bcac9b61e2d5b2a301a36e86'
raw=S.read_bytes();assert hashlib.sha256(raw).hexdigest()==H
N=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*N
A=np.frombuffer(raw,offset=84,dtype=[('normal','<f4',3),('t','<f4',(3,3)),('a','<u2')]);T=A['t'].astype(np.float64)
lo=T.min(1);hi=T.max(1);cross=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);nn=cross/np.linalg.norm(cross,axis=1)[:,None]
def save(name,d,gz=False):
 p=O/('cycu-library-'+name+('.json.gz'if gz else'.json'))
 if gz:
  with gzip.open(p,'wt',compresslevel=9)as f:json.dump(d,f,ensure_ascii=False,allow_nan=False,default=lambda x:x.item()if isinstance(x,np.generic)else str(x))
 else:p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item()if isinstance(x,np.generic)else str(x)))
 return str(p)
def read(p):
 if p.suffix=='.gz':
  with gzip.open(p,'rt')as f:return json.load(f)
 return json.loads(p.read_text())
cache={}
def section(z):
 z=float(z)
 if z in cache:return cache[z]
 adj={};ids=np.flatnonzero((lo[:,2]<z)&(hi[:,2]>z))
 for fi in ids:
  pts=[]
  for ia,ib in [(0,1),(1,2),(2,0)]:
   a,b=T[fi,ia],T[fi,ib]
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2]or b[2]<z<a[2]:pts.append(tuple((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2]))
  assert len(pts)==2
  a,b=pts;assert a!=b
  adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(ns)==2 for ns in adj.values()),(z,'not closed')
 remaining=set(adj);shape=Polygon();loopcount=0
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a);opts=adj[a];b=opts[0]if opts[0]!=last else opts[1];last,a=a,b
   if a==seed or len(loop)>len(adj):break
  g=Polygon(loop);assert a==seed and g.is_valid and g.area>0
  shape=shape.symmetric_difference(g);loopcount+=1
 assert shape.is_valid and not shape.is_empty
 cache[z]=(shape,loopcount);return cache[z]
def count(g):return 0 if g.is_empty else 1 if g.geom_type=='Polygon'else len(g.geoms)
def corners(g):
 out=[]
 for ri,ring in enumerate([g.exterior,*g.interiors]):
  P=np.array(ring.coords[:-1]);u=P-np.roll(P,1,axis=0);v=np.roll(P,-1,axis=0)-P
  for i,p in enumerate(P):
   if min(np.linalg.norm(u[i]),np.linalg.norm(v[i]))<1e-10:continue
   cross2=u[i,0]*v[i,1]-u[i,1]*v[i,0];angle=np.arctan2(abs(cross2),u[i]@v[i])
   if angle>np.radians(.1):out.append(dict(ring_index=ri,vertex_index=i,xy_mm=p.tolist(),turn_degrees=float(np.degrees(angle))))
 assert len(out)>=3
 return out

def components():
 author=read(B/'feature-loss-locations.json.gz');byz=collections.defaultdict(list)
 for r in author['original_component_checks']:byz[r['z_mm']].append(r)
 rows=[];layers=[];deltas=[];wktdeltas=[]
 for z in np.arange(.071,hi[:,2].max(),.2):
  shape,nloops=section(z);comps=[shape]if shape.geom_type=='Polygon'else list(shape.geoms);az=round(float(z),3);ars=byz[az];assert len(ars)==len(comps);used=set()
  for ci,p in enumerate(comps):
   # Match rounded-author polygons by bounds, which here are only identity evidence.
   ai=min((i for i in range(len(ars))if i not in used),key=lambda i:sum((np.array(ars[i]['bounds'])-p.bounds)**2));ar=ars[ai];used.add(ai);assert max(abs(np.array(ar['bounds'])-p.bounds))<1e-5
   er=p.buffer(-.4);op=er.buffer(.4);loss=p.difference(op);fraction=loss.area/p.area;ac=corners(p);mask=unary_union([Point(v['xy_mm']).buffer(.41,quad_segs=64)for v in ac]);outside=loss.difference(mask)
   fam='sloped_parapet'if z<20 else'roof_grid_cell'if p.area<3 else'roof_outer_ring'
   rr=dict(z_mm=az,z_unrounded_mm=float(z),original_component_index=ci,author_original_component_index=ar['original_component_index'],original_polygon_wkt=p.wkt,original_area_mm2=p.area,eroded_wkt=er.wkt,opening_wkt=op.wkt,loss_wkt=loss.wkt,loss_area_mm2=loss.area,opening_loss_fraction=fraction,retained_fraction=1-fraction,eroded_components=count(er),opened_components=count(op),bounds=list(p.bounds),true_corners=ac,true_corner_count=len(ac),true_corner_mask_radius_mm=.41,true_corner_mask_quad_segs=64,loss_outside_true_corner_mask_wkt=outside.wkt,true_corner_outside_0_41_mm2=outside.area,warning_family=fam if fraction>.01 else None,author_loss_fraction=ar['opening_loss_fraction'],author_loss_fraction_delta=fraction-ar['opening_loss_fraction'])
   if fraction>.01:
    ap=wkt.loads(ar['original_polygon_wkt']);alos=ap.difference(ap.buffer(-.4).buffer(.4));rr.update(author_original_polygon_wkt=ar['original_polygon_wkt'],author_original_wkt_recalculated_loss_fraction=alos.area/ap.area,author_exact_original_symmetric_difference_mm2=ap.symmetric_difference(p).area);wktdeltas.append(rr['author_exact_original_symmetric_difference_mm2'])
   rows.append(rr);deltas.append(rr['author_loss_fraction_delta'])
  opening=shape.buffer(-.4).buffer(.4);layers.append(dict(z_mm=az,z_unrounded_mm=float(z),original_loops=nloops,original_polygons=len(comps),area_mm2=shape.area,aggregate_loss_fraction=shape.difference(opening).area/shape.area))
  if len(layers)%50==0:print('LAYER',len(layers),'POLYGONS',len(rows),flush=True)
 warn=[r for r in rows if r['opening_loss_fraction']>.01];families={}
 for fam in sorted(set(r['warning_family']for r in warn)):
  rs=[r for r in warn if r['warning_family']==fam];families[fam]=dict(count=len(rs),z_range_mm=[min(r['z_mm']for r in rs),max(r['z_mm']for r in rs)],min_loss_fraction=min(r['opening_loss_fraction']for r in rs),max_loss_fraction=max(r['opening_loss_fraction']for r in rs),min_retained_fraction=min(r['retained_fraction']for r in rs),max_loss_area_mm2=max(r['loss_area_mm2']for r in rs),max_true_corner_outside_0_41_mm2=max(r['true_corner_outside_0_41_mm2']for r in rs),nonzero_true_corner_outside_count=sum(r['true_corner_outside_0_41_mm2']>0 for r in rs),true_corner_counts=sorted(set(r['true_corner_count']for r in rs)))
 summary=dict(stl_sha256=H,sampled_layers=len(layers),original_polygons=len(rows),warning_count=len(warn),maximum_individual_loss_fraction=max(r['opening_loss_fraction']for r in rows),minimum_retained_fraction=min(r['retained_fraction']for r in rows),maximum_layer_aggregate_loss_fraction=max(r['aggregate_loss_fraction']for r in layers),all_original_components_survive_unsplit=all(r['eroded_components']==r['opened_components']==1 for r in rows),strict_individual_one_percent_passed=not warn,all_warning_true_corner_outside_0_41_zero=all(r['true_corner_outside_0_41_mm2']==0 for r in warn),maximum_author_reported_loss_fraction_delta=max(map(abs,deltas)),maximum_warning_author_reported_loss_fraction_delta=max(abs(r['author_loss_fraction_delta'])for r in warn),maximum_warning_author_wkt_recalculation_delta=max(abs(r['author_original_wkt_recalculated_loss_fraction']-r['author_loss_fraction'])for r in warn),all_polygon_nonzero_true_corner_outside_count=sum(r['true_corner_outside_0_41_mm2']>0 for r in rows),all_polygon_max_true_corner_outside_mm2=max(r['true_corner_outside_0_41_mm2']for r in rows),true_corner_zero_claim_scope='Only the 47 >1% warning polygons, not every original polygon',maximum_author_rounded_original_symmetric_difference_mm2=max(wktdeltas),families=families,method='Original float32 STL promoted exactly to float64. Canonical edge interpolation without rounding, closed original rings composed by symmetric difference. Formal opening uses every original Polygon buffer(-0.4).buffer(0.4) with default Shapely quad_segs=16. Actual outer and hole ring turns >0.1 degree select true corners, no simplify; 0.41 mm disks with quad_segs=64. No bbox or idealized polygon substitution. Bounds only match independently reconstructed components to author rows. Every original polygon WKT, opening, eroded polygon and loss retained. Author rounded warning WKT separately preserved/recomputed.',author_rounding_disclosed=True,exception_approval=False,not_printability_approval=True)
 save('components-independent',summary);save('components-evidence',dict(summary=summary,layers=layers,original_component_checks=rows),True)
 print('COMPONENT SUMMARY',json.dumps(summary),flush=True)
 return rows

LT=T.astype(np.longdouble);e1=LT[:,1]-LT[:,0];e2=LT[:,2]-LT[:,0]
def ray(o,d):
 o=np.asarray(o,dtype=np.float64);d=np.asarray(d,dtype=np.float64);near=np.full(N,-np.inf);far=np.full(N,np.inf);valid=np.ones(N,dtype=bool)
 for k in range(3):
  if d[k]==0:valid&=(lo[:,k]-1e-10<=o[k])&(hi[:,k]+1e-10>=o[k])
  else:
   a=(lo[:,k]-o[k])/d[k];b=(hi[:,k]-o[k])/d[k];near=np.maximum(near,np.minimum(a,b)-1e-10);far=np.minimum(far,np.maximum(a,b)+1e-10)
 ids=np.flatnonzero(valid&(far>=near)&(far>1e-12));a=LT[ids,0];u1=e1[ids];u2=e2[ids];dd=np.asarray(d,dtype=np.longdouble);oo=np.asarray(o,dtype=np.longdouble)
 h=np.cross(np.broadcast_to(dd,u2.shape),u2);det=np.einsum('ij,ij->i',u1,h);ok=abs(det)>1e-24;inv=np.zeros(len(ids),dtype=np.longdouble);inv[ok]=1/det[ok];ss=oo-a;u=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,u1);v=inv*(q@dd);t=inv*np.einsum('ij,ij->i',u2,q)
 local=np.flatnonzero(ok&(u>=-1e-15)&(v>=-1e-15)&(u+v<=1+1e-15)&(t>1e-12));local=local[np.argsort(t[local])];hits=[]
 for k in local:
  fi=int(ids[k]);hit=dict(distance_mm=float(t[k]),original_face=fi,barycentric=[float(1-u[k]-v[k]),float(u[k]),float(v[k])],normal_dot_direction=float(nn[fi]@d))
  if hits and abs(hit['distance_mm']-hits[-1]['distance_mm'])<=1e-11:hits[-1]['coincident_original_faces'].append(fi)
  else:hit['coincident_original_faces']=[fi];hits.append(hit)
 return hits

def winding(p):
 v=LT-np.asarray(p,dtype=np.longdouble);v/=np.linalg.norm(v,axis=2)[:,:,None];num=np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2]));den=1+np.einsum('ij,ij->i',v[:,0],v[:,1])+np.einsum('ij,ij->i',v[:,1],v[:,2])+np.einsum('ij,ij->i',v[:,2],v[:,0]);return float(np.arctan2(num,den).sum()/(2*np.pi))

def local_normals_roots(rows):
 warn=[r for r in rows if r['opening_loss_fraction']>.01];out=[];problems=[]
 for wi,r in enumerate(warn):
  p=wkt.loads(r['original_polygon_wkt']);z=r['z_unrounded_mm'];probes=[]
  for ri,ring in enumerate([p.exterior,*p.interiors]):
   P=np.array(ring.coords[:-1]);true=[c['vertex_index']for c in r['true_corners']if c['ring_index']==ri]
   for edgei,(ia,ib)in enumerate(zip(true,true[1:]+true[:1])):
    a,b=P[ia],P[ib];v=b-a;mid=(a+b)/2;outward=np.array([v[1],-v[0]])/np.linalg.norm(v)
    if not p.contains(Point(mid-outward*1e-5)):outward=-outward
    o=np.array([*(mid+outward*1e-5),z]);d=np.array([*(-outward),0]);h=ray(o,d)
    assert len(h)>=2,(wi,ri,edgei,'XY missing')
    surface=o+d*h[0]['distance_mm'];fi=h[0]['original_face'];n=nn[fi];no=surface+n*1e-5;nh=ray(no,-n)
    xyvalid=h[0]['normal_dot_direction']<0 and h[1]['normal_dot_direction']>0;nv=len(nh)>=2 and nh[0]['normal_dot_direction']<0 and nh[1]['normal_dot_direction']>0
    rr=dict(ring_index=ri,true_side_index=edgei,xy_origin_mm=o.tolist(),xy_inward_direction=d.tolist(),xy_first_chord_mm=h[1]['distance_mm']-h[0]['distance_mm'],xy_entry_exit_orientation_valid=xyvalid,xy_hits=h,original_first_face=fi,original_face_normal=n.tolist(),normal_origin_mm=no.tolist(),actual_normal_first_chord_mm=nh[1]['distance_mm']-nh[0]['distance_mm']if len(nh)>=2 else None,normal_entry_exit_orientation_valid=nv,normal_hits=nh)
    if not(xyvalid and nv):problems.append(dict(warning_index=wi,probe=rr))
    probes.append(rr)
  q=p.representative_point();root=np.array([q.x,q.y,z]);dh=ray(root,[0,0,-1]);uh=ray(root,[0,0,1]);assert dh
  rootcontrols=dict(start=winding(root),mid_to_first_down_exit=winding(root+np.array([0,0,-dh[0]['distance_mm']/2])),after_first_down_exit=winding(root+np.array([0,0,-dh[0]['distance_mm']-1e-5])))
  out.append(dict(z_mm=r['z_mm'],z_unrounded_mm=z,original_component_index=r['original_component_index'],author_original_component_index=r['author_original_component_index'],family=r['warning_family'],original_polygon_wkt=r['original_polygon_wkt'],edge_probes=probes,root_point_mm=root.tolist(),down_hits=dh,up_hits=uh,first_down_exit_z_mm=z-dh[0]['distance_mm'],first_down_exit_normal_dot_direction=dh[0]['normal_dot_direction'],root_solid_angle_controls=rootcontrols))
  print('ROOT',wi+1,len(probes),z-dh[0]['distance_mm'],flush=True)
 families={}
 for fam in sorted(set(r['family']for r in out)):
  rs=[r for r in out if r['family']==fam];ps=[p for r in rs for p in r['edge_probes']];minimum=min(ps,key=lambda p:p['actual_normal_first_chord_mm']if p['actual_normal_first_chord_mm']is not None else-1);nh=minimum['normal_hits'];o=np.array(minimum['normal_origin_mm']);n=np.array(minimum['original_face_normal']);after=nh[1]['distance_mm']+min(1e-5,(nh[2]['distance_mm']-nh[1]['distance_mm'])/2)if len(nh)>2 else nh[1]['distance_mm']+1e-5
  minimum['minimum_probe_winding_controls']=dict(outside=winding(o),inside_mid=winding(o-n*(nh[0]['distance_mm']+nh[1]['distance_mm'])/2),after_first_exit=winding(o-n*after))
  families[fam]=dict(component_samples=len(rs),xy_and_actual_normal_probes=len(ps),minimum_sampled_xy_first_chord_mm=min(p['xy_first_chord_mm']for p in ps),minimum_sampled_actual_normal_first_chord_mm=minimum['actual_normal_first_chord_mm'],under_0_8_actual_normal_probes=sum(p['actual_normal_first_chord_mm']is None or p['actual_normal_first_chord_mm']<.8 for p in ps),first_down_exit_z_range_mm=[min(r['first_down_exit_z_mm']for r in rs),max(r['first_down_exit_z_mm']for r in rs)],minimum_probe=minimum)
 sloped_probes=[p for r in out for p in r['edge_probes']if abs(p['original_face_normal'][2])>1e-3 and abs(p['original_face_normal'][2])<.999]
 summary=dict(stl_sha256=H,sloped_original_face_probes=len(sloped_probes),sloped_original_face_normal_min_first_chord_mm=min(p['actual_normal_first_chord_mm']for p in sloped_probes),sloped_original_face_normal_max_first_chord_mm=max(p['actual_normal_first_chord_mm']for p in sloped_probes),warning_components=len(out),xy_and_actual_normal_probes=sum(len(r['edge_probes'])for r in out),families=families,invalid_entry_exit_orientation_count=len(problems),all_representative_down_roots_first_exit_z_zero=all(r['first_down_exit_z_mm']==0 for r in out),maximum_root_winding_deviation=max(max(abs(r['root_solid_angle_controls'][k]-v)for k,v in [('start',1),('mid_to_first_down_exit',1),('after_first_down_exit',0)])for r in out),method='Original exact high-loss Polygon outer/hole true side midpoints used for XY inward rays; source first original triangle supplies actual outward 3D winding normal for independent inward normal ray. Longdouble Moller-Trumbore intersections with conservative AABB acceleration. Only coincident hit distances grouped at 1e-11 mm; original vertices and triangles unchanged. Original first entry/exit intervals and face IDs/barycentrics retained. Each original Polygon representative point has downward/upward original-STL ray; three solid-angle checks verify start, midpoint to first down exit, after exit. Three family-minimum actual normal rays get outside/mid/after winding controls. Full long raw ring chains remain formal opening input; selected true sides are only probe locations.',not_global_minimum=True,not_contact_everywhere_or_support_free_proof=True,exception_approval=False)
 save('normals-roots-independent',summary);save('normals-roots-evidence',dict(summary=summary,rows=out,problems=problems),True);print('NORMAL ROOT SUMMARY',json.dumps(summary),flush=True)

if __name__=='__main__':
 save('component-environment',dict(python=sys.version,numpy=np.__version__,shapely=shapely.__version__,geos=shapely.geos_version_string,platform=platform.platform(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),stl_sha256=H))
 rows=components();local_normals_roots(rows);assert hashlib.sha256(S.read_bytes()).hexdigest()==H
