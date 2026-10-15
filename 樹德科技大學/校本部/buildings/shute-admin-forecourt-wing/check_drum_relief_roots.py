"""Per-sample source-bounded drum relief roots. Original short chords remain short.
No arbitrary best-direction/longest-chord search. Root is fixed radially inward
into the actual parent drum. For tangent relief-edge normals only, use a
fixed 0.15 inward-normal bias; outer cone surfaces use horizontal radial rays.
"""
from pathlib import Path
import json,gzip,hashlib,collections
import numpy as np,trimesh
from original_rays import OriginalRays
from dense_report import load_dense_report
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m)
r=load_dense_report(R);rows=[];unknown=[]
probe=np.array([.319,.557,.766]);probe/=np.linalg.norm(probe)
def inside(p):return len(ray.hits(p,probe))%2==1
for q in r['short_chords']:
 p=np.array(q['surface_point_mm']);n=np.array(q['original_outward_normal']);x,y,z=p
 xy=p[:2]-[35.,-17.];rho=float(np.linalg.norm(xy));surface_r=22.5+4.5*(z-3)/29.6;depth=surface_r-rho
 # Bounded source family: 0.55-mm panes / 1.0-mm door relief plus original cone-facet sag,
 # only on the forward half of the 29.6-mm-high outward-flared glass drum.
 # Door angular bounds include 0.1 degrees (under 0.05 mm arc) of the
 # adjacent uncut frame, where a face-near-edge sample can lie outside the cut.
 angle=float(np.degrees(np.arctan2(xy[1],xy[0]))%360)
 pane=bool(4.4<=z<=31.0 and 180-1e-6<=angle<=360 and -1e-5<=depth<=.57)
 door=bool(3.5<=z<=11.35 and 282.9<=angle<=305.1 and -1e-5<=depth<=1.03)
 eligible=pane or door
 family='forward_flared_drum_0p55_pane_relief' if pane else 'forward_flared_drum_1p0_door_relief'
 if not eligible:unknown.append(q);continue
 parent=np.array([-xy[0]/rho,-xy[1]/rho,0.]);d=parent.copy() if float(parent@n)<-.05 else parent-.15*n;d/=np.linalg.norm(d)
 nh=q['all_ray_intersections_mm_face'];o=p+n*1e-6
 original_first=nh[1][0]-nh[0][0]
 mid=o-n*((nh[0][0]+nh[1][0])/2)
 gap=nh[2][0]-nh[1][0] if len(nh)>2 else None
 after=o-n*(nh[1][0]+min(1e-5,gap/4 if gap is not None else 1e-5))
 h=ray.hits(p+d*1e-5,d);controls=[inside(p+d*t) for t in [1e-5,.001,.01,.05,.1,.4,.8]]
 checks={'source_bounded_radius_height_and_angle':eligible,'root_enters_actual_surface':float(d@n)<-.05,'first_original_interval_material':inside(mid),'following_original_interval_air':not inside(after),'all_near_root_controls_material':all(controls),'continuous_first_root_ge_0p8mm':bool(h and h[0][0]+1e-5>=.8),'first_root_hit_is_exit':bool(h and np.dot(m.face_normals[h[0][1]],d)>1e-7)}
 rows.append({'original_triangle_index':q['original_triangle_index'],'sample_index':q['sample_index'],'surface_point_mm':p.tolist(),'original_outward_normal':n.tolist(),'source_family':family,'source_angle_degrees':angle,'source_outer_radius_mm':surface_r,'radial_depth_below_outer_cone_mm':depth,'radial_parent_direction':parent.tolist(),'original_first_solid_mm':original_first,'original_following_air_mm':gap,'all_original_normal_hits_mm_face':nh,'fixed_root_rule':'horizontal radial inward if parent dot original normal < -0.05; otherwise radial inward plus 0.15 inward original-normal bias','fixed_root_direction':d.tolist(),'normal_dot_root':float(d@n),'continuous_first_root_mm':h[0][0]+1e-5 if h else None,'all_root_hits_mm_face':h,'near_root_offsets_mm':[1e-5,.001,.01,.05,.1,.4,.8],'near_root_material_controls':controls,'checks':checks,'passed':all(checks.values())})
checks={'all_short_samples_have_bounded_source_family':not unknown,'all_assigned_samples_pass_all_root_and_air_controls':all(x['passed']for x in rows),'every_original_short_sample_retained':len(rows)+len(unknown)==len(r['short_chords'])}
out={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':all(checks.values()),'checks':checks,'original_short_count':len(r['short_chords']),'assigned_count':len(rows),'unclassified':unknown,'minimum_original_first_mm':min([x['original_first_solid_mm']for x in rows],default=None),'minimum_continuous_fixed_root_mm':min([x['continuous_first_root_mm']for x in rows if x['continuous_first_root_mm']is not None],default=None),'maximum_original_following_air_mm':max([x['original_following_air_mm']for x in rows if x['original_following_air_mm']is not None],default=None),'failed_samples':[{'face':x['original_triangle_index'],'sample':x['sample_index'],'checks':x['checks']}for x in rows if not x['passed']],'limits':'All original short normal chords and later air remain recorded. Per-sample direct parent roots establish backed shallow relief only; this does not establish all-direction minimum thickness, slicer toolpaths or physical printability. Independent review required.'}
with (R/'drum-relief-root-samples.json.gz').open('wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as g:g.write(json.dumps(rows,separators=(',',':')).encode())
out['samples_file']='drum-relief-root-samples.json.gz';out['samples_sha256']=hashlib.sha256((R/out['samples_file']).read_bytes()).hexdigest()
(R/'drum-relief-roots.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
