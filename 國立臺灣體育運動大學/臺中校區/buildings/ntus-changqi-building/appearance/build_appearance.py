#!/usr/bin/env python3
"""Assign appearance only to exact original STL triangles. Never builds or repairs geometry."""
from pathlib import Path
import argparse, hashlib, struct, json, csv, collections
import numpy as np
HERE=Path(__file__).resolve().parent
PIN='957c89bd2ae7e39ef4987e41e4f89803c6031e471c0986b1aa41696e892f9be4'
S=150/68; EPS=2e-5
PALETTE=[
 ('N00','Unverified neutral','#B6B7B4',[],'Unknown surfaces, mixed-boundary triangles, synthetic base; not an observed building finish.'),
 ('M01','Pale yellow tile infill','#D9C79C',['S01:C-10','S01:C-11','S01:C-12','S09'],'Muted representative yellow 45x95 tile; not a measured color.'),
 ('M02','Light projecting tile faces','#E1DED0',['S01:C-10','S01:C-11','S01:C-12'],'Pale hanging-tile faces; small ambiguous trim is excluded.'),
 ('M03','Gray lower brick faces','#727777',['S01:C-10','S01:C-11','S01:C-12','S09'],'Registered lower facade faces only; no blanket height rule.'),
 ('M05','Glazing optical approximation','#405258',['S01:C-11','S01:C-12','S01:C-26','S09'],'Opaque representative optical reading, not a glass coating or transparency measurement.'),
 ('M06','Aluminum frame approximation','#D4DADD',['S01:C-26','S09'],'Only existing projecting mullion front faces; no added frames.'),
 ('M07','Three original green roof patches','#718456',['S01:C-31'],'Vegetation representation on three existing roof bed top surfaces only.'),
 ('M08','Visible main non-green roof','#D0D0C8',['S01:C-25','S01:C-31'],'Main visible light-gray roof floor only; equipment/tower caps excluded.'),
 ('M09','Upper louver screen reading','#494847',['S01:C-11','S01:C-12'],'Dark screen backs in existing upper recesses; no fabricated slats.')]

def load_stl(path):
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==PIN,'Wrong original mesh'
 n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+n*50
 dt=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
 tri=np.frombuffer(b,offset=84,dtype=dt,count=n)['vertices'].copy()
 # Stable exact-coordinate deduplication is an index representation, not a mesh operation.
 vv=[];ff=[];lookup={}
 for t in tri:
  f=[]
  for v in t:
   k=v.tobytes()
   if k not in lookup:lookup[k]=len(vv);vv.append(v.copy())
   f.append(lookup[k])
  ff.append(f)
 v=np.array(vv,dtype=np.float32);f=np.array(ff,dtype=np.int32);assert np.array_equal(v[f],tri)
 return b,v,f,tri

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE);p.add_argument('--input',type=Path,default=HERE.parent/'model.stl');a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True);(out/'qa').mkdir(exist_ok=True)
 raw,v,f,tri=load_stl(a.input);t=tri.astype(np.float64);t[:,:,0]=t[:,:,0]/S+30;t[:,:,1]=-t[:,:,1]/S+13;t[:,:,2]=t[:,:,2]/S-1.2
 lo=t.min(1);hi=t.max(1);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]).astype(float);norm/=np.linalg.norm(norm,axis=1)[:,None];norm[:,1]*=-1
 mi=np.zeros(len(f),np.int16);ri=np.zeros(len(f),np.int16);rules=[{'id':'unknown','material':'N00','evidence':[],'criterion':'No complete triangle registered to a supported visible material region.'}]
 def region(axis,plane,sign,bounds):
  mask=np.all(abs(t[:,:,axis]-plane)<EPS,axis=1)&(norm[:,axis]*sign>.999)
  for ax,(lower,upper) in bounds.items():mask&=(lo[:,ax]>=lower-EPS)&(hi[:,ax]<=upper+EPS)
  return mask
 def put(name,mat,axis,plane,sign,bounds,evidence=None):
  k=next(i for i,x in enumerate(PALETTE)if x[0]==mat);mask=region(axis,plane,sign,bounds)
  # Rules may never quietly overwrite different supported materials.
  assert np.all((mi[mask]==0)|(mi[mask]==k)),name
  rules.append({'id':name,'material':mat,'evidence':evidence or PALETTE[k][3],'plane_axis':'xyz'[axis],'plane_source_m':plane,'outward_sign':sign,'all_vertex_bounds_source_m':{'xyz'[q]:b for q,b in bounds.items()},'criterion':'All three vertices, exact plane tolerance 0.00002 source m, outward normal; never centroid-only.'})
  mi[mask]=k;ri[mask]=len(rules)-1
 # The recessed bay fields are existing separate wall planes.
 put('high_street_infill','M01',0,.15,-1,{1:(0,23),2:(4.65,26.75)})
 put('high_north_infill','M01',1,.15,-1,{0:(0,11.7),2:(4.65,26.75)})
 put('high_south_infill','M01',1,22.85,1,{0:(0,5.5),2:(4.65,26.75)})
 put('low_south_infill','M01',1,31.79,1,{0:(28.6,55.8),2:(8.8,20.6)})
 put('low_north_infill','M01',1,10.66,-1,{0:(26.2,56.2),2:(8.9,20.6)})
 put('south_connector_wall','M01',1,30.5,1,{0:(19.7,28.6),2:(4.65,20.6)})
 put('north_service_wall','M01',1,0,-1,{0:(19.7,26.2),2:(4.65,27.0)})
 # Projecting facade piers: height limits prevent lower-wall inference.
 put('high_street_piers','M02',0,0,-1,{1:(0,23),2:(4.65,26.85)})
 put('high_north_piers','M02',1,0,-1,{0:(0,11.7),2:(4.65,26.85)})
 put('high_south_piers','M02',1,23,1,{0:(0,5.5),2:(4.65,26.85)})
 put('low_south_piers','M02',1,32,1,{0:(28.6,55.8),2:(8.8,20.55)})
 put('low_north_piers','M02',1,10.5,-1,{0:(26.2,56.2),2:(8.9,20.6)})
 put('north_stair_front','M02',1,-5.5,-1,{0:(11.7,19.7),2:(4.8,31)})
 put('south_stair_front','M02',1,30.5,1,{0:(5.5,19.2),2:(4.8,31)})
 put('east_stair_end','M02',0,60,1,{1:(17.8,30.5),2:(4.8,25.05)})
 put('east_stair_south','M02',1,30.5,1,{0:(55.8,60),2:(4.8,25.05)})
 # High parapet and major low-wing front cornice faces are image-registered.
 for name,axis,plane,sg,bounds in [
  ('high_street_parapet',0,-.45,-1,{1:(-.35,23.35),2:(26.85,28.15)}),
  ('high_north_parapet',1,-.35,-1,{0:(-.45,11.25),2:(26.85,28.15)}),
  ('high_south_parapet',1,23.35,1,{0:(-.45,5.05),2:(26.85,28.15)}),
  ('low_north_cornice',1,9.95,-1,{0:(26.2,60.2),2:(20.6,22.2)}),
  ('low_south_cornice',1,32.3,1,{0:(28,56),2:(20.55,22.1)})]:put(name,'M02',axis,plane,sg,bounds)
 # Only known wall planes, never every polygon below a z threshold.
 for name,axis,plane,sg,bounds in [
  ('street_lower_wall',0,0,-1,{1:(0,23),2:(0,4.65)}),
  ('north_high_lower_wall',1,0,-1,{0:(0,11.7),2:(0,4.65)}),
  ('south_high_lower_wall',1,23,1,{0:(0,5.5),2:(0,4.65)}),
  ('south_library_wall',1,32,1,{0:(28.6,55.8),2:(0,8.8)}),
  ('north_library_wall',1,8.4,-1,{0:(26.2,56.2),2:(0,8.15)}),
  ('south_connector_lower_wall',1,30.5,1,{0:(19.7,28.6),2:(0,4.65)}),
  ('north_core_lower_wall',1,0,-1,{0:(19.7,26.2),2:(0,4.65)})]:put(name,'M03',axis,plane,sg,bounds)
 # Window volume locations come from the archived original preview mask. Only
 # their actual planar backs are glazing; reveals and sills remain unverified.
 windows=json.loads((HERE/'window-registration.json').read_text())['windows']
 for j,w in enumerate(windows):
  x0,x1,y0,y1,z0,z1=w
  if j>=len(windows)-2:continue # door-like entrance recesses are not proven glazing
  if abs(x1-x0-.74)<EPS or abs(x1-x0-.57)<EPS:
   axis=0;sg=-1 if x1<13 else 1;pl=x1 if sg<0 else x0
  else:
   axis=1;sg=-1 if y0<11 else 1;pl=y1 if sg<0 else y0
  bounds={0:(x0,x1),1:(y0,y1),2:(z0,z1)}
  put(f'window_back_{j:03d}','M09' if z0>29 else 'M05',axis,pl,sg,bounds)
 # Existing fused mullion fronts only. No framing is invented for other windows.
 for x in [33,43,52]:
  for dx in [-2.2,0,2.2]:
   for name,pl,sg in [('south',32.06,1),('north',8.32,-1)]:put(f'{name}_library_mullion_{x}_{dx}','M06',1,pl,sg,{0:(x+dx-.26,x+dx+.26),2:(.75,3.5)})
 for z,h in [(.75,2.8),(5.1,1.8),(9.35,1.25),(13.55,1.25),(17.75,1.25)]:
  for x in [21.5,24.25,27]:put(f'connector_mullion_{x}_{z}','M06',1,30.57,1,{0:(x-.25,x+.25),2:(z,z+h)})
 for y in [10,13,16,19]:put(f'high_rear_mullion_{y}','M06',0,19.74,1,{1:(y-.25,y+.25),2:(24.4,25.9)})
 for name,pl,x,y in [('high_green',27.85,(.7,15.9),(.8,21.9)),('connector_green',21.65,(20.3,27.5),(11.25,22.4)),('south_green',21.65,(35,54.8),(24.2,30.7))]:put(name,'M07',2,pl,1,{0:x,1:y})
 put('main_light_roof','M08',2,23.15,1,{0:(28.7,55.8),1:(10.5,23)})
 # Explicit unknown reasons, preserving original triangles across mixed zones.
 reasons=[]
 for i in range(len(f)):
  if mi[i]:reasons.append('registered_visible_region');continue
  if hi[i,2]<.02:reason='synthetic_base_or_threshold'
  elif norm[i,2]<-.9:reason='underside_or_soffit_unverified'
  elif (abs(lo[i,1]+3.55)<EPS and abs(hi[i,1]+3.55)<EPS) or (abs(lo[i,1]-28.55)<EPS and abs(hi[i,1]-28.55)<EPS):reason='mixed_stair_vegetation_glazing_no_exact_boundary'
  elif any(all(lo[i,q]>=w[q*2]-EPS and hi[i,q]<=w[q*2+1]+EPS for q in range(3))for w in windows):reason='window_reveal_or_unverified_entrance_not_glass'
  elif lo[i,2]<4.65 and hi[i,2]>4.65:reason='triangle_crosses_lower_upper_material_boundary'
  else:reason='unregistered_return_trim_roof_or_equipment'
  reasons.append(reason)
 np.savez_compressed(out/'mesh-data.npz',vertices=v,faces=f,materials=mi,rule_indices=ri)
 palette=[{'index':i,'id':q[0],'name':q[1],'hex':q[2],'evidence':q[3],'limit':q[4]} for i,q in enumerate(PALETTE)]
 (out/'palette.json').write_text(json.dumps(palette,ensure_ascii=False,indent=2)+'\n')
 (out/'mapping-rules.json').write_text(json.dumps({'coordinate_transform':'source x = mm_x/(150/68)+30; source y = -mm_y/(150/68)+13; source z = mm_z/(150/68)-1.2','rules':rules},ensure_ascii=False,indent=2)+'\n')
 with (out/'face-materials.csv').open('w',newline='')as h:
  wr=csv.writer(h);wr.writerow(['original_stl_triangle_index','material_id','rule_id','certainty','evidence','limitation'])
  for i in range(len(f)):wr.writerow([i,PALETTE[mi[i]][0],rules[ri[i]]['id'],'UNKNOWN'if not mi[i]else'APPROXIMATE_SOURCE_REGISTERED',';'.join(rules[ri[i]]['evidence']),reasons[i]])
 area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
 summary={'source_stl_sha256':PIN,'original_stl_bytes':len(raw),'triangles':len(f),'exact_coordinate_unique_vertices':len(v),'full_original_triangle_sequence_equal':bool(np.array_equal(v[f],tri)),'modified_coordinates':0,'added_removed_subdivided_triangles':0,'original_builder_executed':False,'known_approximate_triangles':int(np.count_nonzero(mi)),'unknown_neutral_triangles':int(np.count_nonzero(mi==0)),'known_approximate_surface_area_fraction':float(area[mi>0].sum()/area.sum()),'materials':{q[0]:int(np.count_nonzero(mi==i))for i,q in enumerate(PALETTE)},'unknown_reasons':dict(collections.Counter(reasons[i]for i in range(len(f))if not mi[i])),'vertical_plant_wall_colored_triangles':0,'vertical_plant_wall_limit':'Existing large backing triangles mix vegetation and glazing; kept neutral without subdivision.','three_green_roof_rule_counts':{r['id']:int(np.count_nonzero(ri==j))for j,r in enumerate(rules)if r['material']=='M07'}}
 (out/'qa'/'mapping-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
