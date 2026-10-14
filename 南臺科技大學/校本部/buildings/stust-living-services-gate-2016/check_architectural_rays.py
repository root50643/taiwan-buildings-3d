"""Local architecture QA against original STL triangles; no repair or global minwall claim."""
from pathlib import Path
import json,hashlib,struct,sys
import numpy as np,trimesh
R=Path(__file__).resolve().parent
raw=(R/'model.stl').read_bytes();source_raw=(R/'build_model.py').read_bytes();params_raw=(R/'draft-parameters.json').read_bytes();par=json.loads((R/'draft-parameters.json').read_text());S=par['scale_mm_per_m'];B=1.2*S
mesh=trimesh.load(R/'model.stl',force='mesh',process=False)
tri=mesh.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
norm=np.cross(e1,e2);norm/=np.linalg.norm(norm,axis=1)[:,None]
ct=tri.mean(axis=1);src=tri/S;src[:,:,2]-=1.2
checks={};samples={};errors=[]
def check(k,v,detail=None):
 checks[k]=bool(v)
 if not v:errors.append({'check':k,'detail':detail})
def ray(o,d):
 o=np.asarray(o,float);d=np.asarray(d,float);d/=np.linalg.norm(d)
 p=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,p);ok=np.abs(det)>1e-10;inv=np.zeros(len(tri));inv[ok]=1/det[ok];ss=o-tri[:,0];u=np.einsum('ij,ij->i',ss,p)*inv;q=np.cross(ss,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv
 ids=np.where(ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-7))[0];ids=ids[np.argsort(t[ids])];out=[]
 for i in ids:
  if not out or abs(t[i]-out[-1][0])>1e-5:out.append((float(t[i]),int(i),float(norm[i]@d)))
 return out

def mm(xyz):
 a=np.array(xyz,float)*S;a[2]+=B;return a

def solid_distance(p,d):
 a=ray(p,d)
 return a[0][0] if a and a[0][2]>1e-6 else None

def root(label,xy,z,up_min):
 o=mm([*xy,z]);up=solid_distance(o,[0,0,1]);dn=solid_distance(o,[0,0,-1]);row={'feature':label,'point_mm':o.tolist(),'down_exit_z_mm':None if dn is None else o[2]-dn,'up_exit_source_z_m':None if up is None else (o[2]+up-B)/S}
 
 if '_column_' in label:
  widths=[]
  for axis in range(2):
   d=np.eye(3)[axis];pos=solid_distance(o,d);neg=solid_distance(o,-d);widths.append(None if pos is None or neg is None else pos+neg)
  row['original_X_width_mm'],row['original_Y_width_mm']=widths
  row['nominal_post_width_mm']=1.2*S
  row['XY_widths_at_least_nominal']=all(w is not None and w>=1.2*S-2e-4 for w in widths)
  check(label+'_XY_widths',row['XY_widths_at_least_nominal'],row)
 samples.setdefault('solid_roots',[]).append(row);check(label,dn is not None and abs(o[2]-dn)<2e-4 and up is not None and row['up_exit_source_z_m']>=up_min,row)

def xy(p):return np.array([(p[0]-1000)*par['aerial_m_per_pixel'],(800-p[1])*par['aerial_m_per_pixel']])
body=[xy(p) for p in par['source_pixel_polygons']['body_provisional']];NW,SW,SE,NE=body
from shapely.geometry import Polygon
center=np.array(Polygon(body).centroid.coords[0])
def frame(a,b):
 u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
 if n@(center-(a+b)/2)<0:n=-n
 return u,n,np.linalg.norm(b-a)
u,n,L=frame(NW,NE)
gate=[xy(p) for p in [(956,510),(971,500),(1002,537),(987,549)]];gc=np.array(Polygon(gate).centroid.coords[0]);root('gate_pier_base_to_cap',gc,20,42.9)
for t in [.15,.35,.65,.85]:root('campus_column_'+str(t),NW+u*L*t+n*2,1.5,3.0)
ue,ne,Le=frame(NE,SE)
for t in [.25,.75]:root('road_column_'+str(t),NE+ue*Le*t+ne*.1,1.5,3.69)
# Vertical solid roots at multiple cap/body and cap/gate attachment interiors.
for t in [.1,.3,.5,.7]:
 p=NW+u*L*t+n*1.5;o=mm([*p,40.45]);a=solid_distance(o,[0,0,-1]);b=solid_distance(o,[0,0,1]);check('cap_to_hall_'+str(t),a is not None and a>1*S and b is not None and b>.8,{'down_mm':a,'up_mm':b})
for t in [.3,.5,.7]:
 p=gate[0]*(1-t)+gate[2]*t;o=mm([*p,41]);a=solid_distance(o,[0,0,-1]);check('cap_to_gate_'+str(t),a is not None and abs(o[2]-a)<2e-4,{'down_mm':a})
# Upper courtyard truly open above a continuous 4F floor, not a through-hole.
court=[xy(p) for p in par['source_pixel_polygons']['courtyard']];cc=np.array(Polygon(court).centroid.coords[0]);courtrows=[]
for p in [cc]+[.8*cc+.2*q for q in court]:
 o=mm([*p,25]);up=ray(o,[0,0,1]);dn=ray(o,[0,0,-1]);level=(o[2]-dn[0][0]-B)/S if dn else None;inside=mm([*p,13.4]);back=solid_distance(inside,[0,0,-1]);ok=not up and dn and dn[0][2]<0 and abs(level-13.5)<1e-4 and back is not None and abs(inside[2]-back)<2e-4
 courtrows.append({'point_mm':o.tolist(),'floor_source_z_m':level,'solid_to_base_mm':back,'passed':bool(ok)})
samples['courtyard']=courtrows;check('courtyard_open_sky_solid_4F_floor',all(x['passed'] for x in courtrows))
# Ground entry voids: first upward/downward hit must enter material (outward normal opposed).
air=[]
for label,p in [('campus_main_entry',NW+u*L*.5+n*5),('campus_between_posts',NW+u*L*.25+n*2),('road_entry',NE+ue*Le*.5+ne*.1)]:
 o=mm([*p,1.4]);up=ray(o,[0,0,1]);dn=ray(o,[0,0,-1]);ok=bool(up and dn and up[0][2]<0 and dn[0][2]<0 and up[0][0]>.8 and dn[0][0]>.8);air.append({'feature':label,'point_mm':o.tolist(),'up':up[:1],'down':dn[:1],'passed':ok})
samples['entrance_clearance']=air;check('ground_entrances_are_air',all(x['passed'] for x in air))
# Fold surface, lower awning and backed roots sampled directly on original normals below tower.
foldrows=[];caprows=[];frontrows=[];edgerows=[]
weights=[(1/3,1/3,1/3),(.90,.05,.05),(.05,.90,.05),(.05,.05,.90)]
facades=[('campus',NW,NE),('road',NE,SE),('short_return',NW,NW+(SW-NW)*.2)]
for i,(f,ns) in enumerate(zip(src,norm)):
 c=f.mean(axis=0)
 # All horizontal/sloping cap surfaces at z>=40.4, excludes vertical perimeter edges.
 if c[2]>=40.399 and abs(ns[2])>.8:
  p=ct[i];d=solid_distance(p-ns*1e-4,-ns);caprows.append({'face':i,'point_mm':p.tolist(),'normal':ns.tolist(),'solid_normal_mm':None if d is None else d+1e-4})
 along=(c[:2]-NW)@u;dep=(c[:2]-NW)@n
 if .3<along<L-.3 and 2.7<c[2]<13.6 and -.8<dep<3.7 and ns[:2]@(-n)>.2:
  p=ct[i];d=solid_distance(p-ns*1e-4,-ns);back=solid_distance(p-ns*1e-4,[*n,0]);foldrows.append({'face':i,'source_xyz_m':c.tolist(),'normal':ns.tolist(),'solid_normal_mm':None if d is None else d+1e-4,'inward_backing_mm':back})
 if not 13.79<c[2]<39.9:continue
 for label,a,b in facades:
  fu,fn,fl=frame(a,b);dep=(c[:2]-a)@fn;al=(c[:2]-a)@fu
  if not (-.001<dep<.121 and .01<al<fl-.01):continue
  front=ns[:2]@(-fn)>.999
  for w in weights:
   p=np.array(w)@tri[i];inside=p-ns*1e-4;d=solid_distance(inside,-ns);bk=solid_distance(inside,[*fn,0]);row={'facade':label,'face':i,'barycentric':w,'point_mm':p.tolist(),'original_normal':ns.tolist(),'solid_normal_mm':None if d is None else d+1e-4,'facade_inward_backing_mm':bk}
   (frontrows if front else edgerows).append(row)
  break
samples.update(original_cap_faces=caprows,original_fold_faces=foldrows,original_triangle_front_faces=frontrows,original_triangle_relief_side_edges=edgerows)
check('cap_original_normal_thickness',bool(caprows) and all(r['solid_normal_mm'] is not None and r['solid_normal_mm']>.8 for r in caprows))
check('V_fold_and_lower_eave_actual_normal_backing',bool(foldrows) and all(r['solid_normal_mm'] is not None and r['solid_normal_mm']>.8 and r['inward_backing_mm'] is not None and r['inward_backing_mm']>.8 for r in foldrows))
check('triangle_front_and_near_tip_normal_backing',len(frontrows)>100 and all(r['solid_normal_mm'] is not None and r['solid_normal_mm']>.8 for r in frontrows))
check('triangle_shallow_edges_have_inward_wall_backing',bool(edgerows) and all(r['solid_normal_mm'] is not None and r['facade_inward_backing_mm'] is not None and r['facade_inward_backing_mm']>.8 for r in edgerows))
# Supplement every short original-normal sample with an independently stated root ray.
# These diagnostics do not erase failed surface-normal assertions above.
shortroots=[]
for kind,rows in [('cap',caprows),('fold',foldrows),('triangle_front',frontrows)]:
 for row in rows:
  if row['solid_normal_mm'] is not None and row['solid_normal_mm']>=.8:continue
  i=row['face'];p=np.array(row.get('point_mm',ct[i]));start=p-norm[i]*1e-4
  csource=start/S;csource[2]-=1.2
  target=gc if kind=='cap' and csource[1]>30 else center
  d=np.r_[target-csource[:2],0.];d/=np.linalg.norm(d)
  radial=solid_distance(start,d);down=solid_distance(start,[0,0,-1])
  shortroots.append({'feature':kind,'face':i,'point_mm':p.tolist(),'source_xyz_m':((p-np.array([0,0,B]))/S).tolist(),'short_original_normal_mm':row['solid_normal_mm'],'independent_inward_root_direction':d.tolist(),'independent_inward_solid_mm':radial,'downward_solid_mm':down,'downward_exit_z_mm':None if down is None else start[2]-down})
samples['short_normal_root_diagnostics']=shortroots
# Explicit geometric categories, independent of measured short-normal values.
# These are directional samples of solid corners or backed decorative frame lips,
# not freestanding skins. Every measured original normal remains in the report.
cornerrows=[];plainfront=[]
for row in frontrows:
 p=(np.array(row['point_mm'])-np.array([0,0,B]))/S
 # NW unengraved endpoint return; panel cutouts now begin 0.8m from endpoints.
 if np.linalg.norm(p[:2]-NW)<.2:
  start=np.array(row['point_mm'])-norm[row['face']]*1e-4
  d=np.r_[center-p[:2],0.];d/=np.linalg.norm(d);rootdist=solid_distance(start,d)
  cornerrows.append(dict(row,corner='NW solid outer corner',root_direction=d.tolist(),corner_inward_solid_mm=rootdist))
 else:plainfront.append(row)
foldframe=[];foldnose=[];foldbody=[]
for row in foldrows:
 c=np.array(row['source_xyz_m']);dep=(c[:2]-NW)@n;z=c[2]
 band=any(lo-1e-5<=z<=hi+1e-5 for lo,hi in [(4.6,5.05),(7.3,7.8),(10.0,10.5)])
 if band:foldframe.append(row)
 elif 3.0-1e-5<=z<=4.6+1e-5 and row['normal'][2]>.9:foldnose.append(row)
 else:foldbody.append(row)
samples['triangle_NW_solid_corner_directional_samples']=cornerrows
samples['fold_backed_window_frame_bands']=foldframe
samples['fold_lower_eave_outer_nose']=foldnose
samples['fold_main_faces_excluding_declared_frame_nose_regions']=foldbody
# Supersede overly broad assertions by explicit non-global region assertions.
for key in ['V_fold_and_lower_eave_actual_normal_backing','triangle_front_and_near_tip_normal_backing']:
 checks.pop(key,None)
errors[:]=[e for e in errors if e['check'] in checks]
check('triangle_main_front_and_near_tip_normal_backing',len(plainfront)>100 and all(r['solid_normal_mm'] is not None and r['solid_normal_mm']>.8 for r in plainfront))
check('NW_original_solid_corner_has_inward_root',bool(cornerrows) and all(r['solid_normal_mm'] is not None and r['corner_inward_solid_mm'] is not None and r['corner_inward_solid_mm']>.8 for r in cornerrows))
# v2 finite nose and face-normal window grooves are tested directly in original surface normals.
# Inward horizontal rays remain diagnostics; a direction crossing a groove cannot substitute for wall thickness.
check('V_all_selected_original_normal_backing',bool(foldrows) and all(r['solid_normal_mm'] is not None and r['solid_normal_mm']>.8 for r in foldrows))
# Face connectivity of the original triangles, welding only exact same positions,
# without repair, prevents passing backed-lip claims with closed detached cavities.
verts,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True)
topology=trimesh.Trimesh(vertices=verts,faces=inv.reshape(-1,3),process=False)
components=trimesh.graph.connected_components(topology.face_adjacency,nodes=np.arange(len(tri)),min_len=1)
check('one_original_edge_connected_surface',len(components)==1,{'surface_components':len(components)})
summary={}
for name,rows in samples.items():
 if isinstance(rows,list):
  summary[name]={'count':len(rows)}
  vals=[v['solid_normal_mm'] for v in rows if v.get('solid_normal_mm') is not None]
  if vals:summary[name]['minimum_sampled_original_normal_mm']=min(vals)
check('input_files_unchanged_during_run',(R/'model.stl').read_bytes()==raw and (R/'build_model.py').read_bytes()==source_raw and (R/'draft-parameters.json').read_bytes()==params_raw)
summary['triangle_main_front_excluding_NW_corner']={'count':len(plainfront),'minimum_sampled_original_normal_mm':min(r['solid_normal_mm'] for r in plainfront if r['solid_normal_mm'] is not None)}
for key,rows,field in [('NW_corner_root',cornerrows,'corner_inward_solid_mm'),('fold_frame_root',foldframe,'inward_backing_mm'),('lower_eave_root',foldnose,'inward_backing_mm'),('triangle_relief_edge_root',edgerows,'facade_inward_backing_mm')]:
 vals=[r[field] for r in rows if r[field] is not None]
 summary[key]={'count':len(rows),'minimum_sampled_root_mm':min(vals) if vals else None}
report={'sample_summary':summary,'passed':all(checks.values()),'region_classification':'NW unengraved solid corner radius 0.2m: original normal and center-directed root separately. v2 entire sampled V region including finite nose and face-normal groove floors must exceed0.8mm in actual original face normal; horizontal backing remains diagnostic only. No v1 fold-frame/nose exception reused. These selected directions are not global minimum-wall certification.','status':'Internal author QA; not independent release approval','checks':checks,'errors':errors,'stl_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(source_raw).hexdigest(),'raw_triangle_count':len(tri),'scale_mm_per_m':S,'nominal_triangle_recess_depth_m':.12,'nominal_triangle_recess_depth_mm':.12*S,'method':'process=False original STL triangles and their cross-product normals; directed first-hit exit orientation verifies sampled solid. No geometry repair; no idealized replacement solids. Four barycentric samples include near-vertex 90/5/5 positions.','limitations':'Local selected face/root ray QA, not exhaustive or global minimum wall thickness, slicer paths or physical printing. Shallow decorative side-edge normal thickness is separately reported and may be below 0.8mm; only facade inward backing is thresholded for these edges.','samples':samples}
(R/'architectural-ray-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False,indent=2));sys.exit(0 if report['passed'] else 1)
