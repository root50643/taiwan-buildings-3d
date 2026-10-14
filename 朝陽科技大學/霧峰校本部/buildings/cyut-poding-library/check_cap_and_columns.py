"""Ray checks on original STL, no repair: courtyard and actual recessed portal."""
from pathlib import Path
import json
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False)
def ray(o,d):
 o=np.array(o,dtype=float);d=np.array(d,dtype=float); t=m.triangles
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(np.tile(d,(len(t),1)),e2);det=np.einsum('ij,ij->i',e1,p)
 good=np.abs(det)>1e-10;inv=np.zeros(len(t));inv[good]=1/det[good];s=o-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(v),5) for v in dist[sel]))
S=150/166; Z=S*1.12
checks={};probes=[]
# Probe actual cap faces at every formerly failing layer. The cap is now solid.
# Derive the raw triangle normal, then cast along that normal into the material.
for z in np.arange(54.671,56.072,.2):
 o=np.array((4*S,-60,z));hits=ray(o,(0,1,0));ys=[o[1]+t for t in hits]
 assert len(ys)>=2
 checks[f'cap_{z:.3f}_no_front_skin']=ys[1]-ys[0]>8
 # Locate actual raw triangle at the first hit and check its outward normal.
 pt=np.array((4*S,ys[0],z)); normals=[]
 for tri in m.triangles:
  n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n=n/np.linalg.norm(n)
  if abs(np.dot(pt-tri[0],n))>1e-5:continue
  v0=tri[1]-tri[0];v1=tri[2]-tri[0];v2=pt-tri[0]
  a=np.dot(v0,v0);b=np.dot(v0,v1);c=np.dot(v1,v1);d=np.dot(v2,v0);e=np.dot(v2,v1);den=a*c-b*b
  if abs(den)<1e-20:continue
  u=(c*d-b*e)/den;v=(a*e-b*d)/den
  if u>=-1e-6 and v>=-1e-6 and u+v<=1+1e-6:normals.append(n.tolist())
 assert normals
 normal=np.array(normals[0]); normal_hits=ray(pt+normal*.01,-normal)
 normal_thickness=normal_hits[1]-normal_hits[0]
 assert normal_thickness>8
 probes.append({'z_mm':float(z),'intersection_y_mm':ys,'first_actual_face_normals':normals,'normal_material_thickness_mm':normal_thickness,'normal_ray_hits_mm':normal_hits})
# Probe the relocated shallow vent below the cap: no sealed front skin.
for z in [50.4*Z,50.8*Z,51.0*Z]:
 ys=ray((4*S,-60,z),(0,1,0));assert ys[1]-ys[0]>8
checks['relocated_vent_open_to_exterior_with_thick_back']=True
# The 56 >1% opening-loss samples are the two low porch square columns.
columns=[]
for x in [28.5,43.5]:
 zs=[]
 for z in np.arange(3.071,8.472,.2):
  ys=ray((x*S,-60,z),(0,1,0));thick=ys[1]-ys[0]
  assert abs(thick-2.2*S)<1e-4
  zs.append({'z_mm':float(z),'normal_y_thickness_mm':thick})
 # X-normal first span across this same square column.
 xs=ray(((x-3)*S,-24*S,5),(1,0,0));xthick=xs[1]-xs[0]
 assert abs(xthick-2.2*S)<1e-4
 down=ray((x*S,-24*S,5),(0,0,-1));up=ray((x*S,-24*S,5),(0,0,1))
 assert abs(5-down[0])<1e-5 and abs(5+up[0]-10*Z)<1e-4
 columns.append({'center_xy_mm':[x*S,-24*S],'normal_x_thickness_mm':xthick,'normal_y_samples':zs,'continuous_root_to_base_bottom_z_mm':5-down[0],'continuous_root_to_canopy_top_z_mm':5+up[0]})
checks['two_low_columns_actual_1p98795mm_square']=True
checks['two_low_columns_continuous_to_base_and_canopy']=True
checks={k:bool(v) for k,v in checks.items()}
prior=json.loads((R/'v1-cap-ligament-hold.json').read_text())
comparison=[{'z_mm':old['z_mm'],'v1_front_strip_reported_mm':old['front_strip_actual_normal_thickness_mm'],'v2_actual_cap_face_normal_thickness_mm':new['normal_material_thickness_mm']} for old,new in zip(prior['probes'],probes)]
assert len(comparison)==8
report={'v1_to_v2_failed_layer_comparison':comparison,'passed':all(checks.values()),'checks':checks,'cap_vent_probes':probes,'column_probes':columns,'stl_sha256':__import__('hashlib').sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Unprocessed original STL; actual recessed face normal and normal ray spans; no parameter-only thickness acceptance. Opening corner localization is separately recorded in feature-loss-locations.json.'}
(R/'cap-column-root-check.json').write_text(json.dumps(report,indent=2));print(report['checks']);assert report['passed']
