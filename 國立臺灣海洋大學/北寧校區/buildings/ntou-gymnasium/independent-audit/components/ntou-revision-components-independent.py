"""NTOU gym revision independent original-STL components and actual-surface roots.
Original binary float32 vertices promoted to double. Never repair/round mesh/sections.
Formal opening only original polygons. True corners include outer and hole turns.
"""
from pathlib import Path
import numpy as np,json,gzip,hashlib,struct,sys,platform,collections
import shapely
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from shapely import wkt
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
B=O.parents[1]
S=B/'model.stl';H='752b4c147bd18874b1c49890596c260e58015520f71f60cebc6ee6144700ef49'
raw=S.read_bytes();assert hashlib.sha256(raw).hexdigest()==H
N=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*N
A=np.frombuffer(raw,offset=84,dtype=[('normal','<f4',3),('t','<f4',(3,3)),('a','<u2')]);T=A['t'].astype(np.float64)
lo=T.min(1);hi=T.max(1);cross=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);nn=cross/np.linalg.norm(cross,axis=1)[:,None]
def save(name,d,gz=False):
 p=O/('ntou-revision-components-'+name+'.json.gz')
 with gzip.open(p,'wt',compresslevel=9) as f:
  json.dump(d,f,ensure_ascii=False,allow_nan=False,default=lambda x:x.item()if isinstance(x,np.generic)else str(x))
 return p.name
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

def components():
 author=read(B/'true-corner-mask.json');byz=collections.defaultdict(list)
 for r in author['original_component_checks']:byz[r['z_mm']].append(r)
 rows=[];layers=[];previous=None;previous_comps=None;previous_paths=None
 for z in np.arange(.071,hi[:,2].max(),.2):
  shape,nloops=section(z);comps=[shape]if shape.geom_type=='Polygon'else list(shape.geoms);az=round(float(z),3);ars=byz[az];assert len(ars)==len(comps);used=set()
  for ci,p in enumerate(comps):
   ai=min((i for i in range(len(ars))if i not in used),key=lambda i:sum((np.array(ars[i]['bounds'])-p.bounds)**2));ar=ars[ai];used.add(ai);assert max(abs(np.array(ar['bounds'])-p.bounds))<1e-10
   er=p.buffer(-.4);op=er.buffer(.4);loss=p.difference(op);fraction=loss.area/p.area;ac=corners(p);mask=unary_union([Point(v['xy_mm']).buffer(.41,quad_segs=64)for v in ac]);outside=loss.difference(mask)
   ap=wkt.loads(ar['original_wkt']);alos=ap.difference(ap.buffer(-.4).buffer(.4));simplified=p.simplify(1e-5,preserve_topology=True);av=[pt for ring in [simplified.exterior,*simplified.interiors]for pt in ring.coords];amask=unary_union([Point(pt).buffer(.41)for pt in av]);aoutside=loss.difference(amask)
   fam='end_rib'if z<30 else'top_rib'
   rr=dict(z_mm=az,z_unrounded_mm=float(z),original_component_index=ci,author_original_component_index=ar['original_component_index'],original_polygon_wkt=p.wkt,original_area_mm2=p.area,eroded_wkt=er.wkt,opening_wkt=op.wkt,loss_wkt=loss.wkt,loss_area_mm2=loss.area,opening_loss_fraction=fraction,retained_fraction=1-fraction,eroded_components=count(er),opened_components=count(op),bounds=list(p.bounds),hole_count=len(p.interiors),true_corners=ac,true_corner_count=len(ac),true_corner_mask_radius_mm=.41,true_corner_mask_quad_segs=64,loss_outside_true_corner_mask_wkt=outside.wkt,true_corner_outside_0_41_mm2=outside.area,author_method_mask_outside_mm2=aoutside.area,warning_family=fam if fraction>.01 else None,author_loss_fraction=ar['opening_loss_fraction'],author_loss_fraction_delta=fraction-ar['opening_loss_fraction'],author_original_wkt=ar['original_wkt'],author_original_wkt_recalculated_loss_fraction=alos.area/ap.area,author_exact_original_symmetric_difference_mm2=ap.symmetric_difference(p).area,intersection_with_previous_layer_mm2=None if previous is None else p.intersection(previous).area,author_previous_layer_overlap_mm2=ar['intersection_with_previous_layer_mm2'],author_original_record=ar)
   links=[] if previous_comps is None else [dict(previous_component_index=i,intersection_area_mm2=p.intersection(g).area)for i,g in enumerate(previous_comps)if p.intersection(g).area>0]
   rr["previous_component_links"]=links
   rr["has_sampled_overlap_path_to_base_layer"]=previous_comps is None or any(previous_paths[k["previous_component_index"]]for k in links)
   rows.append(rr)
  opening=shape.buffer(-.4).buffer(.4);layers.append(dict(z_mm=az,z_unrounded_mm=float(z),original_loops=nloops,original_polygons=len(comps),area_mm2=shape.area,aggregate_loss_fraction=shape.difference(opening).area/shape.area));previous=shape;previous_comps=comps;previous_paths=[r["has_sampled_overlap_path_to_base_layer"]for r in rows[-len(comps):]]
  if len(layers)%50==0:print('LAYER',len(layers),'POLYGONS',len(rows),flush=True)
 warn=[r for r in rows if r['opening_loss_fraction']>.01];families={}
 for fam in sorted(set(r['warning_family']for r in warn)):
  rs=[r for r in warn if r['warning_family']==fam];families[fam]=dict(count=len(rs),z_range_mm=[min(r['z_mm']for r in rs),max(r['z_mm']for r in rs)],min_loss_fraction=min(r['opening_loss_fraction']for r in rs),max_loss_fraction=max(r['opening_loss_fraction']for r in rs),min_retained_fraction=min(r['retained_fraction']for r in rs),max_loss_area_mm2=max(r['loss_area_mm2']for r in rs),max_true_corner_outside_0_41_mm2=max(r['true_corner_outside_0_41_mm2']for r in rs),max_author_method_mask_outside_mm2=max(r['author_method_mask_outside_mm2']for r in rs),nonzero_true_corner_outside_count=sum(r['true_corner_outside_0_41_mm2']>0 for r in rs),true_corner_counts=sorted(set(r['true_corner_count']for r in rs)),min_previous_layer_overlap_mm2=min(r['intersection_with_previous_layer_mm2']for r in rs))
 summary=dict(stl_sha256=H,sampled_layers=len(layers),original_polygons=len(rows),warning_count=len(warn),maximum_individual_loss_fraction=max(r['opening_loss_fraction']for r in rows),minimum_retained_fraction=min(r['retained_fraction']for r in rows),maximum_layer_aggregate_loss_fraction=max(r['aggregate_loss_fraction']for r in layers),all_original_components_survive_unsplit=all(r['eroded_components']==r['opened_components']==1 for r in rows),strict_individual_one_percent_passed=not warn,all_warning_true_corner_outside_0_41_zero=all(r['true_corner_outside_0_41_mm2']==0 for r in warn),maximum_author_reported_loss_fraction_delta=max(abs(r['author_loss_fraction_delta'])for r in rows),maximum_author_wkt_recalculation_delta=max(abs(r['author_original_wkt_recalculated_loss_fraction']-r['author_loss_fraction'])for r in rows),all_polygon_nonzero_true_corner_outside_count=sum(r['true_corner_outside_0_41_mm2']>0 for r in rows),all_polygon_max_true_corner_outside_mm2=max(r['true_corner_outside_0_41_mm2']for r in rows),maximum_author_original_wkt_symmetric_difference_mm2=max(r['author_exact_original_symmetric_difference_mm2']for r in rows),all_above_first_layer_polygons_have_positive_previous_layer_overlap=all(r['intersection_with_previous_layer_mm2']>0 for r in rows if r['intersection_with_previous_layer_mm2']is not None),maximum_previous_layer_overlap_delta_mm2=max(abs(r['intersection_with_previous_layer_mm2']-r['author_previous_layer_overlap_mm2'])for r in rows if r['intersection_with_previous_layer_mm2']is not None),all_original_polygons_have_sampled_overlap_path_to_base_layer=all(r["has_sampled_overlap_path_to_base_layer"]for r in rows),families=families,method='Exact binary float32 vertices promoted to double; canonical unrounded edge interpolation; original closed rings including holes, no repair or rounding. Formal original-Polygon opening radius0.4 with default quad_segs16. True outer/hole corners have angle>0.1degree, no simplify; only corner mask uses radius0.41 quad_segs64. Separate author simplify1e-5/quad16 corner mask recomputed without replacing opening input. Every author original WKT recomputed and matched by bounds only for identity. All layer overlaps are actual original Polygon intersections, finite layer evidence not continuous vertical support proof.',exception_approval=False,not_printability_approval=True)
 save('summary',summary);save('polygons-evidence',dict(summary=summary,layers=layers,original_component_checks=rows),True);print('COMPONENT SUMMARY',json.dumps(summary),flush=True);return rows

if __name__=='__main__':
 save('environment',dict(python=sys.version,numpy=np.__version__,shapely=shapely.__version__,geos=shapely.geos_version_string,platform=platform.platform(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),stl_sha256=H))
 rows=components()
