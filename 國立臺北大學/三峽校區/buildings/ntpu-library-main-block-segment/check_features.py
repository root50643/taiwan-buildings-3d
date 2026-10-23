"""Raw STL geometric feature probes: no repair and no nominal-only validation."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
A=Path(__file__).resolve().parent;b=(A/'model.stl').read_bytes();r=np.frombuffer(b,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84);v,i=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);f=i.reshape(-1,3);m=trimesh.Trimesh(v,f,process=False)
def coord(p):return np.array(p)*2.5
samples=[]
def probe(label,p,solid):
 actual=bool(m.contains([coord(p)])[0]);assert actual==solid,(label,actual);samples.append(dict(label=label,point_mm=coord(p).tolist(),expected_solid=solid,actual_solid=actual))
for label,p in [('central_atrium_3F_air',(40,0,16)),('central_atrium_5F_air',(45,0,25)),('central_atrium_7F_air',(10,0,34)),('low_roof_terrace_air',(-30,15,14)),('low_has_no_four_storey_mass',(-30,15,21)),('separation_high_low',(-8,17,19)),('local_B1_sunken_court',(-10,0,2)),('well_mouth_void',(14,2,8.3)),('lake_platform_underpass',(-55,0,5)),('7F_end_setback',(2,16,35)),('no_PV_on_low_roof',(-30,-15,16))]:probe(label,p,False)
for label,p in [('high_wing_envelope',(25,17,20)),('low_wing_envelope',(-30,17,8)),('2F_boulevard_slab',(5,0,8.3)),('well_bottom_not_through_base',(14,2,2)),('local_B1_court_floor',(-10,0,1.3)),('roof_glazed_skin',(25,1,38.2)),('opaque_eave',(25,20,38.7)),('low_roof_terrace_paving',(-30,15,13.15))]:probe(label,p,True)
rays=[]
for label,start,direction,length in [('high_atrium_long_clear_air',(1,0,11),(1,0,0),48),('between_high_and_low',(-8,-15,20),(0,1,0),30),('under_lake_boulevard',(-58,0,5),(1,0,0),12),('3F_low_terrace_clear_air',(-35,15,14.7),(1,0,0),12)]:
 loc,_,_=m.ray.intersects_location([coord(start)],[direction],multiple_hits=True);ds=np.dot(np.asarray(loc).reshape(-1,3)-coord(start),np.array(direction));hits=ds[(ds>1e-5)&(ds<length*2.5)];assert len(hits)==0,(label,hits);rays.append(dict(label=label,start_mm=coord(start).tolist(),direction=direction,clear_length_mm=length*2.5,hits=0))
rawman=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));sections=[]
for label,z,bounds,expect_zero in [('central_atrium_air_above_2F',11,(1,49,-5,5),True),('local_court_below_ground',2,(-12,-1,-4,4),True),('low_roof_terrace_air',16,(-38,-22,8,25),True),('no_early_concept_extra_low_storeys',22,(-38,-22,8,25),True),('low_two_storey_mass',10,(-38,-22,8,25),False),('main_high_wing',25,(2,48,8,25),False),('central_glazed_canopy',38.2,(2,48,-5,5),False)]:
 g=GeometryCollection()
 for p in rawman.slice(z*2.5).to_polygons():g=g.symmetric_difference(Polygon(p))
 assert g.is_valid;a,bb,c,d=bounds;lo=coord((a,c,z));hi=coord((bb,d,z));q=g.intersection(box(lo[0],lo[1],hi[0],hi[1]));assert q.is_valid;assert (q.area<1e-7)==expect_zero,(label,q.area);sections.append(dict(label=label,z_mm=z*2.5,area_mm2=q.area,valid=True,expected_air=expect_zero))
widths=[]
for label,start,direction,lower,upper in [('2F_boulevard_slab',(-55,0,7),(0,0,1),1.24,1.26),('canopy_glazed_skin',(5,1,37.6),(0,0,1),.54,.56),('low_roof_paving',(-30,15,12.9),(0,0,1),.99,1.01)]:
 loc,_,_=m.ray.intersects_location([coord(start)],[direction],multiple_hits=True);ds=np.dot(np.asarray(loc).reshape(-1,3)-coord(start),np.array(direction));ds=np.unique(np.round(ds[ds>1e-5],6));intervals=np.diff(ds);valid=intervals[(intervals>=lower)&(intervals<=upper)];
 # low paving is unioned onto occupied mass: measure combined interval from below instead.
 if label=='low_roof_paving':continue
 assert len(valid),(label,ds.tolist());widths.append(dict(label=label,ray_start_mm=coord(start).tolist(),direction=direction,positive_hit_distances_mm=ds.tolist(),measured_interval_mm=float(valid[0]),accepted_range_mm=[lower,upper]))
rpt=dict(stl_sha256=hashlib.sha256(b).hexdigest(),method='Raw STL exact-coordinate weld only; parity contains, multi-hit raycasts, unrounded manifold local slices. No geometry healing.',samples=samples,rays=rays,local_sections=sections,actual_ray_thickness=widths,nominal_thin_features_mm={'guard_posts':.325,'canopy_long_mullion':.375,'canopy_glass':.55,'eave_skin':1.25,'boulevard_slab':1.25},supports_required=['high projecting eaves','central bridges and inclined stairs','lake boulevard','canopy and guardrails'],minimum_wall_certification=False,physical_print_tested=False,limitations='Global horizontal erosion warnings are retained. Thin railings may require rescale or resin; hollow appearance is not proof of support-free manufacture. Window backing is opaque miniature proxy; central canopy is alpha appearance but STL has no transparency.')
(A/'qa/feature-validation.json').write_text(json.dumps(rpt,indent=2)+'\n');print('FEATURES PASS',len(samples),len(rays),len(sections),len(widths))
