"""Read-only author diagnostic of the fixed YPU candidate-v3 STL. No mesh repair."""
from pathlib import Path
import hashlib,json,numpy as np,trimesh
from shapely import wkt
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
from manifold3d import Manifold,Mesh64
import argparse
from original_geometry import output_directory
parser=argparse.ArgumentParser(description="Replay the fixed STL original-Polygon warnings and selected root sections/rays.")
parser.add_argument('--model',type=Path,required=True)
parser.add_argument('--layer-report',type=Path,required=True,help='Canonical current layer-component-check.json with original Polygon WKT.')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
EVIDENCE=Path(__file__).resolve().parents[1]/'evidence'
R=output_directory(args.output,EVIDENCE);F=args.model.resolve()
SHA='f7ccaa9bbb042ec8880ad5f63faec349227a22116f6992f12c5f8bc81167c31a'
assert hashlib.sha256(F.read_bytes()).hexdigest()==SHA
m=trimesh.load(F,force='mesh',process=False);tri=m.triangles;normals=m.face_normals
layer=json.loads(args.layer_report.read_text());assert layer['stl_sha256']==SHA
D={'L': {'matrix': [[-0.35002227667612545, 0.4629093339274277, 493.4623524170127], [-0.4629093339274277, -0.35002227667612545, 1022.7934952105194], [0.0, 0.0, 1.0]]}, 'H': {'matrix': [[-0.5222569105691055, -0.052936585366069266, 1260.2530731707307], [0.052936585366069266, -0.5222569105691055, 914.3751544715467], [0.0, 0.0, 1.0]]}};S=1.07;B=1.6;MPP=.13554824373866425

def xy(p):return np.array([(p[0]-790)*MPP,(640-p[1])*MPP])
def coords(points,k=None):
 p=np.array(points,float)
 if k:p=(np.c_[p,np.ones(len(p))]@np.array(D[k]['matrix']).T)[:,:2]
 return np.array([xy(v)for v in p])
def poly(points):return Polygon(np.round(np.asarray(points)*S,4))
def bar(a,b,width):
 v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2
 return poly([a+n,b+n,b-n,a-n])
def pieces(q):return []if q.is_empty else[q]if q.geom_type=='Polygon'else[g for g in q.geoms if g.geom_type=='Polygon']
def metrics(q):
 return {'area_mm2':q.area,'polygon_count':len(pieces(q)),'polygon_areas_mm2':sorted([p.area for p in pieces(q)],reverse=True),'valid':q.is_valid,'wkt':q.wkt}
Hfront=coords([[910,500],[790,465],[650,450],[530,460],[410,500],[285,560]],'H')
Lfront=coords([[730,610],[650,570],[520,490]],'L')
L=poly(coords([[95,333],[150,313],[210,298],[325,285],[440,290],[555,315],[660,355],[760,413],[820,450],[730,610],[650,570],[520,490],[480,570],[320,540],[260,530],[100,550],[30,420]],'L'))
G=poly(coords([[100,550],[130,640],[210,680],[300,698],[380,680],[450,640],[490,580],[480,570],[320,540],[260,530]],'L'))
Gface=coords([[100,550],[130,640],[210,680],[300,698],[380,680],[450,640],[490,580]],'L')
Lrear=coords([[95,333],[150,313],[210,298],[325,285],[440,290],[555,315],[660,355],[760,413]],'L')
west_tower=poly(coords([[720,495],[795,520],[735,610],[680,570]],'L'))
sl=LineString(Lrear).buffer(4,cap_style=2,join_style=2);slope=poly(np.array(sl.exterior.coords)[:-1])
c=xy([1152,679]);a=np.linspace(0,2*np.pi,48,endpoint=False);rot=np.array([[np.cos(-.80),-np.sin(-.80)],[np.sin(-.80),np.cos(-.80)]])
oval=poly(np.c_[7*np.cos(a),3.5*np.sin(a)]@rot.T+c);inner=poly(np.c_[5.8*np.cos(a),2.3*np.sin(a)]@rot.T+c)
features={};posts=[]
for name,ch in [('H',Hfront),('L',Lfront)]:
 centers=[]
 for a,b in zip(ch[:-1],ch[1:]):
  for t in np.linspace(0,1,max(2,round(np.linalg.norm(b-a)/3))):
   q=(a+(b-a)*t)*S
   if not any(np.linalg.norm(q-old)<1e-8 for old in centers):centers.append(q)
 centers=sorted(centers,key=lambda q:tuple(q))
 for i,q in enumerate(centers):
  p=box(q[0]-.7*S,q[1]-.7*S,q[0]+.7*S,q[1]+.7*S)
  posts.append({'name':f'{name}_post_{i+1:02d}','chain':name,'center':q,'mask':p,'merged_west_tower':name=='L'and west_tower.covers(Point(q))})
 features[name+'_lower_band']=unary_union([bar(a,b,1.1)for a,b in zip(ch[:-1],ch[1:])])
 features[name+'_top_rail']=unary_union([bar(a,b,1.6)for a,b in zip(ch[:-1],ch[1:])])
# Each original Polygon remains unchanged. Direction-change threshold excludes collinear triangulation samples.
classified=[]
for r in layer['original_component_checks']:
 p=wkt.loads(r['original_polygon_wkt']);assert p.is_valid
 corners=[];angles=[]
 for ring in [p.exterior,*p.interiors]:
  co=np.array(ring.coords)[:-1]
  for i in range(len(co)):
   u=co[i]-co[i-1];v=co[(i+1)%len(co)]-co[i];lu=np.linalg.norm(u);lv=np.linalg.norm(v)
   if lu<1e-8 or lv<1e-8:continue
   angle=float(np.arccos(np.clip(u@v/(lu*lv),-1,1)))
   if angle>np.deg2rad(10):corners.append(co[i].tolist());angles.append(float(np.degrees(angle)))
 zones=unary_union([Point(q).buffer(.41)for q in corners]);loss=p.difference(p.buffer(-.4).buffer(.4));outside=loss.difference(zones)
 is_warning=r['opening_loss_fraction']>.01;family='other_original_polygon';physical=None
 if is_warning:
  if p.area<3:
   post=min(posts,key=lambda q:np.linalg.norm(np.asarray(p.centroid.coords[0])-q['center']))
   assert p.centroid.distance(Point(post['center']))<.001
   family=post['chain']+'_free_pergola_posts';physical=post['name']
  else:
   assert r['z_mm']<31.132 and p.bounds[0]>-6 and p.bounds[2]<44
   family='H_continuous_lower_roof_band';physical='H_lower_band'
 classified.append({**r,'warning_over_one_percent':is_warning,'family':family,'physical_feature_id':physical,'true_corner_direction_change_threshold_degrees':10,'true_corner_radius_mm':.41,'true_corner_points_mm':corners,'true_corner_direction_changes_degrees':angles,'loss_outside_true_corner_mm2':outside.area,'loss_outside_true_corner_fraction':outside.area/p.area,'loss_outside_true_corner_wkt':outside.wkt})
families={}
for name in sorted({r['family']for r in classified if r['warning_over_one_percent']}):
 rs=[r for r in classified if r['family']==name]
 families[name]={'actual_distinct_feature_count':len({r['physical_feature_id']for r in rs}),'feature_ids':sorted({r['physical_feature_id']for r in rs}),'cross_layer_polygon_samples':len(rs),'distinct_layer_count':len({r['z_mm']for r in rs}),'z_range_mm':[min(r['z_mm']for r in rs),max(r['z_mm']for r in rs)],'maximum_original_opening_loss_fraction':max(r['opening_loss_fraction']for r in rs),'maximum_loss_outside_true_corners_mm2':max(r['loss_outside_true_corner_mm2']for r in rs),'maximum_loss_outside_true_corners_fraction':max(r['loss_outside_true_corner_fraction']for r in rs),'per_feature':{key:{'samples':len([r for r in rs if r['physical_feature_id']==key]),'z_mm':[r['z_mm']for r in rs if r['physical_feature_id']==key]}for key in sorted({r['physical_feature_id']for r in rs})}}
report={'stl_sha256':SHA,'role':'author diagnostic, not independent QA','original_polygon_count':len(classified),'warning_polygon_sample_count':sum(r['warning_over_one_percent']for r in classified),'physical_post_inventory':[{k:(v.tolist()if isinstance(v,np.ndarray)else v.wkt if isinstance(v,Polygon)else v)for k,v in p.items()}for p in posts],'families':families,'method':'Unmodified original Polygon WKT. Standard radius .4 opening retained; true corners use >10 degree direction changes and radius .41 disks. Nonzero outside-corner remainders are retained. Physical feature counts are location-traced features, not the globally connected STL shell count.','limitations':['No repair or simplification of original Polygons. Small nonzero outside-corner remnants are not automatically exempted or asserted numerical.','This is XY morphological screening, not global minimum wall thickness, slicing, or printability approval.'],'all_original_polygons':classified}
(R/'original-polygon-loss-families.json').write_text(json.dumps(report,indent=2));print('FAMILIES',families,flush=True)

# Fast read-only acceleration, exact coordinate-indexing only.
v,iv=np.unique(m.vertices,axis=0,return_inverse=True);acc=Manifold(Mesh64(v,np.asarray(iv[m.faces],np.uint64)));mm=acc.to_mesh64();tt=np.asarray(mm.vert_properties)[:,:3][np.asarray(mm.tri_verts)]
def key(t):return tuple(sorted(tuple(x)for x in t))
lookup={key(t):i for i,t in enumerate(tri)}
assert len(tt)==len(tri)==len(lookup) and all(key(t)in lookup for t in tt)
face_map=[lookup[key(t)]for t in tt]
assert all(np.dot(np.cross(t[1]-t[0],t[2]-t[0]),normals[face_map[i]])>0 for i,t in enumerate(tt))
paritydirs=np.array([[.3713906763541037,.5570860145311556,.7427813527082074],[-.681123,.417119,.601003]])
paritydirs/=np.linalg.norm(paritydirs,axis=1)[:,None]
def cast(p,d):
 hs=[]
 for x in acc.ray_cast(np.asarray(p).tolist(),(p+d*1000).tolist()):
  if x.distance<=1e-13:continue
  q={'distance_mm':float(x.distance*1000),'original_face_id':face_map[x.face_id],'point_mm':list(x.position),'outward_normal':list(x.normal),'dot_ray_outward_normal':float(d@np.array(x.normal))}
  if not hs or abs(q['distance_mm']-hs[-1]['distance_mm'])>1e-7:hs.append(q)
 return hs

def inside(p):
 values=[len(cast(np.asarray(p),d))%2==1 for d in paritydirs]
 return {'inside_by_two_ray_parities':values,'agree':values[0]==values[1]}

def ray_sample(label,fid,p):
 p=np.asarray(p);n=normals[fid];d=-n;o=p+n*.0001;hits=cast(o,d)
 entryok=len(hits)>=2 and abs(hits[0]['distance_mm']-.0001)<1e-6 and hits[0]['dot_ray_outward_normal']<-.99999 and hits[1]['dot_ray_outward_normal']>1e-8
 span=hits[1]['distance_mm']-hits[0]['distance_mm']if entryok else None
 rec={'label':label,'sample_original_face_id':int(fid),'original_surface_point_mm':p.tolist(),'outward_normal':n.tolist(),'ray_origin_mm':o.tolist(),'inward_direction':d.tolist(),'all_intersection_hits':hits,'entry_and_first_exit_valid':entryok,'first_solid_normal_chord_mm':span}
 if entryok:
  eps=min(.0001,span*.1);mid=o+d*(hits[0]['distance_mm']+hits[1]['distance_mm'])/2
  rec['controls']={'outside_before_entry':inside(p+eps*n),'inside_after_entry':inside(p+eps*d),'first_chord_midpoint':inside(mid),'air_after_first_exit':inside(o+d*(hits[1]['distance_mm']+eps))}
  rec['first_air_gap_mm']=hits[2]['distance_mm']-hits[1]['distance_mm']if len(hits)>2 else None
  rec['later_solid_intervals_mm']=[hits[i+1]['distance_mm']-hits[i]['distance_mm']for i in range(2,len(hits)-1,2)]
  # FIRST exit roots from an interior point, not a jump across the next air interval.
  roots=[]
  for di in np.vstack((np.eye(3),-np.eye(3))):
   hh=cast(mid,di);roots.append({'direction':di.tolist(),'first_exit_distance_mm':hh[0]['distance_mm']if hh else None,'first_exit_original_face_id':hh[0]['original_face_id']if hh else None})
  rec['inside_first_chord_midpoint_mm']=mid.tolist();rec['six_axis_first_exit_root_spans']=roots
 return rec

def plane_hits(z):
 out=[]
 for fi,f in enumerate(tri):
  if not (min(f[:,2])<z<max(f[:,2])):continue
  hh=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:hh.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  if len(hh)==2:out.append((fi,np.asarray(hh)))
 return out
section_cache={}
def section(z):
 if z in section_cache:return section_cache[z]
 adj={}
 for _,h in plane_hits(z):
  a,b=[tuple(p[:2])for p in h]
  if a==b:continue
  adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(q)==2 for q in adj.values()),('degree2',z)
 remaining=set(adj);shape=Polygon()
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a);b=adj[a][0]if adj[a][0]!=last else adj[a][1];last,a=a,b
   if a==seed:break
   assert len(loop)<=len(adj)
  p=Polygon(loop);assert p.is_valid
  if p.area>1e-8:shape=shape.symmetric_difference(p)
 assert shape.is_valid;section_cache[z]=shape;return shape

rays=[]
def add_z_rays(name,z,mask,limit=200):
 candidates=[]
 for fid,h in plane_hits(z):
  p=h.mean(0)
  if mask.buffer(.001).covers(Point(p[:2])) and np.linalg.norm(h[1]-h[0])>.015:
   candidates.append((fid,p))
 if len(candidates)>limit:candidates=[candidates[i]for i in np.linspace(0,len(candidates)-1,limit,dtype=int)]
 for fid,p in candidates:rays.append(ray_sample(name,fid,p))
 return len(candidates)
for p in posts:add_z_rays(p['name'],31.5,p['mask'])
for name,z in [('H_lower_band',30.8),('L_lower_band',30.8),('H_top_rail',32.5),('L_top_rail',32.5)]:add_z_rays(name,z,features[name])
add_z_rays('oval_open_rim',31.5,oval,200)
# Includes recess sides and substrate faces on the convex entrance chain, without treating arbitrary later material as backing.
gfront_zone=LineString(Gface*S).buffer(.9,cap_style=2,join_style=2)
for z in [11.1,23.8]:add_z_rays('convex_entry_backed_windows',z,gfront_zone,80)
for z in [2.0,3.1]:add_z_rays('rear_slope',z,slope,60)
# Original horizontal/sloped face centroid samples, restricted to named feature zones.
for name,mask,zmin,zmax in [('oval_bottom_floor',inner,30.3829,30.3831),('H_top_rail_horizontal',features['H_top_rail'],31.8809,32.9511),('L_top_rail_horizontal',features['L_top_rail'],31.8809,32.9511),('rear_slope_top',slope,1.6001,4.7)]:
 ids=[i for i,p in enumerate(m.triangles_center)if zmin<p[2]<zmax and abs(normals[i,2])>.15 and mask.buffer(.001).covers(Point(p[:2]))]
 for i in ids:rays.append(ray_sample(name,i,m.triangles_center[i]))
raygroups={}
for name in sorted({r['label']for r in rays}):
 rs=[r for r in rays if r['label']==name];vals=[r['first_solid_normal_chord_mm']for r in rs if r['first_solid_normal_chord_mm']is not None]
 raygroups[name]={'representative_original_face_samples':len(rs),'valid_entry_exit_samples':len(vals),'minimum_sampled_first_normal_chord_mm':min(vals)if vals else None,'maximum_sampled_first_normal_chord_mm':max(vals)if vals else None,'below_0_8mm_sample_count':sum(v<.8 for v in vals),'with_later_material_after_air_count':sum(bool(r.get('later_solid_intervals_mm'))for r in rs)}
rayreport={'stl_sha256':SHA,'exact_original_triangles_and_winding_unchanged':True,'original_faces':len(tri),'sample_count':len(rays),'method':'Exact-index Manifold acceleration checked against every original unprocessed STL triangle and winding. Selected original triangle/XY-plane segment midpoint or original centroid, inward normal from +0.0001mm outward offset. FIRST material entry/exit interval; all later air and material retained. Two independent non-axis ray-parity inside controls.','limitations':['Selected feature samples only. No claim of all-direction/global minimum thickness.','Later material after an air gap is never counted as first chord or a connected root.','Six-axis connected first-exit distances originate at the first-chord interior midpoint; these are sample-specific directional spans, not structural strength.'],'families':raygroups,'samples':rays}
(R/'representative-original-normal-rays.json').write_text(json.dumps(rayreport,indent=2));print('RAYS',raygroups,flush=True)

roots=[]
def pair(name,zlo,zhi,mask,kind):
 lo=section(zlo).intersection(mask);hi=section(zhi).intersection(mask);ov=lo.intersection(hi)
 assert lo.is_valid and hi.is_valid and ov.is_valid
 roots.append({'label':name,'kind':kind,'lower_z_mm':zlo,'upper_z_mm':zhi,'region_wkt':mask.wkt,'lower_actual_section':metrics(lo),'upper_actual_section':metrics(hi),'vertical_overlap':metrics(ov),'upper_area_overlap_fraction':ov.area/hi.area if hi.area else None,'overlap_erosion_0_4mm':metrics(ov.buffer(-.4))})
pair('oval_rim_to_solid_pedestal',30.3828,30.3832,oval.buffer(.001),'annular wall onto solid below')
pair('oval_pedestal_across_main_roof_top',30.2758,30.2762,oval.buffer(.001),'solid tower continues through roof height')
pair('slope_to_base',1.5998,1.6002,slope.buffer(.001),'terrain base root')
pair('convex_entry_to_base',1.5998,1.6002,G.buffer(.001),'convex body base root')
for p in posts:
 for suffix,zlo,zhi,kind in [('foot',29.9548,29.9552,'post bottom to roof cap'),('roof_top',30.2758,30.2762,'post and lower band across main roof top'),('top_rail_start',31.8808,31.8812,'post to upper rail overlap')]:pair(p['name']+'_'+suffix,zlo,zhi,p['mask'],kind)
for name in ['H','L']:
 pair(name+'_lower_band_root',30.0618,30.0622,features[name+'_lower_band'].buffer(.001),'lower band starts on roof/post union')
 pair(name+'_top_rail_supports',31.8808,31.8812,features[name+'_top_rail'].buffer(.001),'spanning upper rail; separate supports expected')
pair('L_rail_west_tower_footprint',31.8808,31.8812,features['L_top_rail'].intersection(west_tower).buffer(.001),'upper rail/tower common footprint')
pair('L_rail_above_west_tower_top',32.4158,32.4162,features['L_top_rail'].intersection(west_tower).buffer(.001),'rail continues above tower top')
# Lateral joining: sample rectangular crossing corridors around every source-shared back seam.
lateral=[]
def corridor_check(name,a,b,z,width=.6,length=1.6):
 a=np.asarray(a);b=np.asarray(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]]);c=(a+b)/2
 mask=Polygon([c+u*length/2+n*width,c-u*length/2+n*width,c-u*length/2-n*width,c+u*length/2-n*width]);sec=section(z);clip=sec.intersection(mask)
 probes=[np.r_[c+n*t,z]for t in [-.4,0,.4]]
 lateral.append({'label':name,'z_mm':z,'corridor':metrics(mask),'actual_solid_in_corridor':metrics(clip),'filled_area_fraction':clip.area/mask.area,'erosion_0_4mm':metrics(clip.buffer(-.4)),'seam_three_inside_controls':[{'point_mm':p.tolist(),**inside(p)}for p in probes]})
seam=coords([[100,550],[260,530],[320,540],[480,570]],'L')*S
for j,(a,b)in enumerate(zip(seam[:-1],seam[1:])):
 for z in [11.1,23.8,27.55]:corridor_check(f'convex_entry_L_back_seam_{j+1}',a,b,z)
axis=Lrear[-1]-Lrear[0]
for j,(a,b)in enumerate(zip(Lrear[:-1],Lrear[1:])):
 q=(a+b)/2;u=(q-Lrear[0])@axis/(axis@axis);top=B+(.5+2.3*u)*S;z=B+(top-B)*.4
 corridor_check(f'rear_slope_building_seam_{j+1}',a*S,b*S,z,width=.6,length=1.6)
rootreport={'stl_sha256':SHA,'method':'Read-only original STL strict canonical-edge XY sections. Degree2 and original loop/combined validity asserted; no repair. Named feature masks locate intersections only. Root overlaps report all actual components and areas. Lateral corridors report exact section occupancy plus two-direction parity controls.','limitations':['Vertical-overlap area is not support-free printability or load-bearing strength.','The upper rails bridge separate posts; multiple root patches are expected and not disguised as one root.','Nominal source-derived masks locate the feature; numerical metrics come from actual STL intersections. No mask-clipped polygon replaces an original polygon in canonical QA.'],'vertical_roots':roots,'lateral_connections':lateral}
(R/'root-section-connections.json').write_text(json.dumps(rootreport,indent=2));print('ROOTS',[(r['label'],r['upper_area_overlap_fraction'],r['vertical_overlap']['polygon_count'])for r in roots],flush=True);print('LATERAL',[(r['label'],r['filled_area_fraction'])for r in lateral],flush=True)
summary={'stl_sha256':SHA,'role':'author-side diagnostic only; independent review and global dense surface evidence remain separate','warning_families':families,'representative_ray_families':raygroups,'all_representative_entry_exit_valid':all(r['entry_and_first_exit_valid']for r in rays),'control_failures':[{'label':r['label'],'face_id':r['sample_original_face_id'],'controls':r.get('controls')}for r in rays if r.get('controls')and not(all(x['agree']for x in r['controls'].values())and not r['controls']['outside_before_entry']['inside_by_two_ray_parities'][0]and r['controls']['inside_after_entry']['inside_by_two_ray_parities'][0]and r['controls']['first_chord_midpoint']['inside_by_two_ray_parities'][0]and not r['controls']['air_after_first_exit']['inside_by_two_ray_parities'][0])],'vertical_root_count':len(roots),'lateral_connection_count':len(lateral),'all_lateral_corridors_fully_filled_within_1e_8':all(abs(r['filled_area_fraction']-1)<1e-8 for r in lateral),'stl_unchanged_after_diagnostic':hashlib.sha256(F.read_bytes()).hexdigest()==SHA,'no_repair_used':True,'not_global_minimum_thickness':True,'not_a_slicer_or_print_test':True}
(R/'diagnostic-summary.json').write_text(json.dumps(summary,indent=2));print('SUMMARY',json.dumps({k:v for k,v in summary.items()if k not in ['warning_families','representative_ray_families']},indent=2),flush=True)

# Supplement: genuine inward facade backing, not merely the longest arbitrary axis.
backing=[]
for r in rays:
 if r['label']!='convex_entry_backed_windows' or r['first_solid_normal_chord_mm'] is None or r['first_solid_normal_chord_mm']>=.8:continue
 p=np.array(r['inside_first_chord_midpoint_mm']);s=np.array(r['original_surface_point_mm']);chains=Gface*S
 j=min(range(len(chains)-1),key=lambda i:LineString([chains[i],chains[i+1]]).distance(Point(s[:2])))
 a,b=chains[j],chains[j+1];u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
 if not G.covers(Point((a+b)/2+n*.1)):n=-n
 radial=np.array(G.centroid.coords[0])-p[:2];radial/=np.linalg.norm(radial)
 ds=[('nearest_original_front_segment_inward',np.r_[n,0]),('toward_convex_body_centroid',np.r_[radial,0])];out=[]
 for name,d in ds:
  hs=cast(p,d)
  out.append({'direction_label':name,'direction':d.tolist(),'all_hits':hs,'connected_first_exit_mm':hs[0]['distance_mm']if hs else None,'origin_inside':inside(p),'at_0_4mm_inside':inside(p+d*.4),'at_0_8mm_inside':inside(p+d*.8)})
 backing.append({'original_face_id':r['sample_original_face_id'],'original_surface_point_mm':s.tolist(),'first_solid_chord_midpoint_mm':p.tolist(),'first_solid_normal_chord_mm':r['first_solid_normal_chord_mm'],'nearest_convex_front_segment_index':j,'backing_probes':out})
whole=[]
for name,witness in [('H_top_rail_union',posts[0]['center']),('L_top_rail_and_west_tower_union',next(p['center']for p in posts if p['name']=='L_post_01')),('oval_ring',np.array(oval.exterior.coords[0])*.999+np.array(oval.centroid.coords[0])*.001)]:
 zlo,zhi=(31.8808,31.8812)if'rail'in name else(30.3828,30.3832)
 comps=pieces(section(zhi));upper=min(comps,key=lambda p:p.distance(Point(witness)));assert upper.distance(Point(witness))<.001
 lower=section(zlo);ov=upper.intersection(lower);pp=pieces(ov)
 whole.append({'label':name,'lower_z_mm':zlo,'upper_z_mm':zhi,'upper_entire_original_component':metrics(upper),'actual_overlap_entire_lower_section':metrics(ov),'upper_supported_area_fraction':ov.area/upper.area,'individual_overlap_patch_opening':[{'area_mm2':p.area,'eroded_components':len(pieces(p.buffer(-.4))),'opened_components':len(pieces(p.buffer(-.4).buffer(.4))),'opening_loss_fraction':p.difference(p.buffer(-.4).buffer(.4)).area/p.area}for p in pp]})
supp={'stl_sha256':SHA,'short_convex_window_samples':len(backing),'minimum_nearest_front_inward_connected_root_mm':min(r['backing_probes'][0]['connected_first_exit_mm']for r in backing),'minimum_centroid_directed_connected_root_mm':min(r['backing_probes'][1]['connected_first_exit_mm']for r in backing),'all_backing_0_8mm_probes_inside':all(all(p['at_0_8mm_inside']['inside_by_two_ray_parities'])for r in backing for p in r['backing_probes']),'short_window_backing':backing,'full_original_component_roots':whole,'limitations':['A short initial normal chord at a recess corner remains short; the separate inward root is additional directional evidence, not a replacement value.','Entire original upper components are retained in the supplementary rail/ring roots. For L this includes its already merged west tower; local rail-only masked measurements remain separately labeled.','Partial post foot overlap and spanning rails still require support planning; this diagnostic does not certify global wall thickness or printability.']}
(R/'backing-and-whole-component-roots.json').write_text(json.dumps(supp,indent=2));print('SUPPLEMENT',{k:v for k,v in supp.items()if k not in ['short_window_backing','full_original_component_roots']},flush=True);print('WHOLE',[(x['label'],x['upper_supported_area_fraction'],x['actual_overlap_entire_lower_section']['polygon_count'],[p['eroded_components']for p in x['individual_overlap_patch_opening']])for x in whole],flush=True)
