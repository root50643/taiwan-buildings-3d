from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False)
def point(q):x,y,z=q;return np.array([(x-525)/25,(510-y)/25,z])*4
probes=[('left_2F',(240,450,8),True),('long_2F',(700,600,8),True),('elbow_2F',(450,450,8),True),('L_notch_air',(650,450,8),False),('no_newtower',(240,450,11),False),('B1_room_air',(800,600,1),False),('B1_ground_slab',(800,600,.1),True),('no_full_B1_left',(240,450,1),False),('no_full_B1_middle',(500,600,1),False),('B1_NW_notch_wall',(689,497,1),True),('B1_NW_notch_air',(702,501,1),False),('B1_NW_notch_cover',(702,501,3),True),('right_narrow_window_visible',(900,680,8),True),('B1_internal_stair_air',(915,610,4.5),False),('B1_internal_stair_solid',(945,610,1),True),('long_canopy_air',(500,715,5),False),('long_canopy_cover',(500,715,6.35),True),('shortend_canopy_air',(130,500,5),False),('lower_shop_wall',(500,685,5),True),('opaque_upper_screen',(500,690,8),True),('inner_elbow_small_stair',(570,507,2.9),True),('right_outer_stair',(990,700,2.5),True),('left_broad_steps',(90,450,2.3),True),('long_ramp',(500,742,2.5),True),('nonB1_perimeter_ground_contact',(150,450,.5),True),('nonB1_underbody_air_between_contacts',(240,450,.5),False),('leftstairs_grade_contact',(90,450,.5),True),('rightstairs_grade_contact',(990,700,.5),True),('elbowsteps_grade_contact',(570,500,.5),True),('ramp_grade_contact',(500,742,.5),True),('ramp_low_landing',(950,740,1.9),True),('firstfloor_stair_sideportal',(900,550,4.5),False),('secondfloor_stair_sideportal',(900,550,8),False),('firstfloor_body_entry_recess',(890,550,4.5),False),('secondfloor_body_entry_recess',(890,550,8),False)]
for level,floor,head in [('1F',3.23,4.5),('2F',6.68,8.0)]:
 for x in [882,890,899,903,906]:
  for y in [543,550,559]:
   probes += [(f'{level}_threshold_{x}_{y}',(x,y,floor),True),(f'{level}_doorway_head_{x}_{y}',(x,y,head),False)]
for name,xy in [('left',(60,500)),('elbow',(574,478))]+[(f'right_shared_{x}',(x,740)) for x in [936,945,960,970,990,1005]]:
 probes += [(name+'_lowlanding_floor',(*xy,1.99),True),(name+'_lowlanding_head',(*xy,2.10),False)]
for flight in ['B1','upper']:
 for i in range(15):
  top=3.2-i*(2.9/15) if flight=='B1' else 6.65-i*(3.45/15)
  for x in [934,948,960]:
   y=563+i*6;probes.append((f'{flight}_step{i}_x{x}_floor',(x,y,top-.04),True))
   for head in [.1,.8,1.5,1.8]:probes.append((f'{flight}_step{i}_x{x}_head{head}',(x,y,top+head),False))
for floor,label in [(3.25,'1F_northlanding'),(6.70,'2F_northlanding')]:
 for x in [910,922,934,948,960]:
  for y in [543,550,558]:
   probes.append((f'{label}_{x}_{y}_floor',(x,y,floor-.04),True))
   for head in [.1,.8,1.5,1.8]:probes.append((f'{label}_{x}_{y}_head{head}',(x,y,floor+head),False))
for y in [562,580,610,640,652,658]:
 for x in [910,922]:
  probes.append((f'1F_westwell_path_{x}_{y}_floor',(x,y,3.21),True))
  for head in [.1,.8,1.5,1.8]:probes.append((f'1F_westwell_path_{x}_{y}_head{head}',(x,y,3.25+head),False))
for x in [934,948,960]:
 for y in [652,658]:
  probes.append((f'upper_southlanding_{x}_{y}_floor',(x,y,3.21),True))
  for head in [.1,.8,1.5,1.8]:probes.append((f'upper_southlanding_{x}_{y}_head{head}',(x,y,3.25+head),False))
got=t.contains(np.array([point(p) for n,p,e in probes]));out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,p,g,expected)
 out.append({'feature':name,'point_mm':point(p).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=point(q);d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
rays={}
for name,q,h in [('leftroof',(240,450,12),10.2),('rightroof',(700,600,12),10.2),('longcanopy',(500,715,8),6.44)]:
 hits=ray(q,(0,0,-1));assert abs(hits[0]-(q[2]-h)*4)<.004,(name,hits);rays[name]={'hits_mm':hits,'expected_first_height_mm':h*4}
ramp=[]
for x,expected in [(150,3.26),(160,3.26-10/785*1.26),(300,3.26-150/785*1.26),(500,3.26-350/785*1.26),(700,3.26-550/785*1.26),(934,3.26-784/785*1.26),(950,2.0),(990,2.0)]:
 hits=ray((x,740,5),(0,0,-1));height=5-hits[0]/4;assert abs(height-expected)<.002,(x,height,expected);ramp.append({'x605':x,'height_mm':height*4,'expected_mm':expected*4})
grade=[]
for name,x,y,expected in [('left_landing',60,500,2),('left_slope',35,500,1),('right_landing',960,760,2),('right_slope',960,783.5,1),('elbow_landing',574,478,2),('elbow_slope',574,460,1)]:
 hits=ray((x,y,4),(0,0,-1));height=4-hits[0]/4;assert abs(height-expected)<.002,(name,height,expected);grade.append({'feature':name,'height_mm':height*4,'expected_mm':expected*4})
steps=[]
for side in ['left','right','elbow','B1','upper']:
 for i in range(15 if side in ['B1','upper'] else 5 if side=='elbow' else 7):
  if side=='left':q=(72+i*6,450,6);expected=2+(i+1)*1.2/7
  elif side=='right':q=(990,677+i*8,6);expected=3.2-i*1.2/7
  elif side=='elbow':q=(570,487+i*5,6);expected=2+(i+1)*1.2/5
  elif side=='B1':q=(948,563+i*6,3.35-i*(2.9/15));expected=3.2-i*2.9/15
  else:q=(948,563+i*6,6.8-i*(3.45/15));expected=6.65-i*3.45/15
  hits=ray(q,(0,0,-1));height=q[2]-hits[0]/4;assert abs(height-expected)<.001,(side,i,height,expected);steps.append({'side':side,'step':i,'height_mm':height*4,'expected_approx_mm':expected*4})
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'roof_canopy_direct_rays':rays,'five_stair_flights_direct_rays':steps,'ramp_and_two_landings_direct_rays':ramp,'localgrade_landings_and_cutslopes':grade,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'manufacturing_limits':'Not physically printed or toolpath certified. Fine screen/frame/rail/post elements below0.8mm; canopy and exposed B1 undersides may need supports. Groundshop and upper rooms solid exterior proxies notsurveyed interiors. B1 hollow area retained through actual stair throat; resin drain/support access needs slicer/material checks. No supportfree/globalminimumwallcertificate.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print('Feature probes and stair/roof rays pass; sampled thickness warning retained.')
