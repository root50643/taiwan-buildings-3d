#!/usr/bin/env python3
"""Positive/negative controls for source-preserving root ray mechanics."""
from check_root_supports import *
def test():
 out=HERE/'root_tests';out.mkdir(exist_ok=True);results=[]
 def query(x=0):return {'origin_mm':[-2.,.113,.157],'direction':[1.,0.,0.],'target_t_mm':2+x,'target_point_mm':[x,.113,.157]}
 for name,width,expect in [('thick_box',1.2,True),('minimum_box',.8,True),('thin_box',.79,False)]:
  m=trimesh.creation.box(extents=[width,1.3,1.4]);tri=np.asarray(m.triangles,dtype=np.float64)
  with tempfile.TemporaryDirectory(prefix='root_test_',dir=out)as td:r=run_rays(tri,[query()],Path(td))[0]
  results.append({'case':name,'expected_passed':expect,'actual_passed':r['passed'],'passed':r['passed']==expect,'full_witness':r})
 a=trimesh.creation.box(extents=[.595,1.3,1.4]);a.apply_translation([-.3025,0,0]);b=trimesh.creation.box(extents=[.595,1.3,1.4]);b.apply_translation([.3025,0,0]);tri=np.r_[a.triangles,b.triangles]
 with tempfile.TemporaryDirectory(prefix='root_test_',dir=out)as td:r=run_rays(tri,[query(),query(-.3)],Path(td))
 results.append({'case':'gap_cannot_be_chained_into_material','expected_passed':False,'actual_passed':r[0]['passed'],'passed':not r[0]['passed'] and r[0]['root_interval']is None,'full_witness':r[0]})
 gap=r[1]['root_interval']['next_air_length_mm'];results.append({'case':'next_air_gap_retained','expected_gap_mm':.01,'actual_gap_mm':gap,'passed':abs(gap-.01)<1e-10,'full_witness':r[1]})
 for name,point,expected in [('thick_center',[0,0,0],.6),('thin_center',[0,0,0],.395),('gap_center',[0,0,0],.005)]:
  if name=='gap_center':t=tri
  else:t=trimesh.creation.box(extents=[1.2 if name=='thick_center'else.79,1.3,1.4]).triangles
  v=OriginalIndex(t).clearance(np.array(point,float));results.append({'case':name+'_clearance','expected_mm':expected,'actual_mm':v['distance_lower_bound_mm'],'passed':abs(v['distance_lower_bound_mm']-expected)<1e-10,'witness':v})
 report={'passed':all(v['passed']for v in results),'cases':results,'scope':'Synthetic positive and negative controls only. These do not change or repair the target STL.','validator_sha256':sha(Path(__file__))};writejson(out/'root_controls_report.json',report);print(json.dumps({'passed':report['passed'],'cases':len(results)},indent=2));return report
if __name__=='__main__':raise SystemExit(0 if test()['passed']else 1)
