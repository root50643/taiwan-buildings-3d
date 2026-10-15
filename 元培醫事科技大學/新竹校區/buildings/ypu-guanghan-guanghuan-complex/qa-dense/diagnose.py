from pathlib import Path
import numpy as np,pandas as pd,json,hashlib
R=Path(__file__).parent;F=R.parent/'model.stl';raw=F.read_bytes();tri=np.frombuffer(raw,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v'].astype(np.longdouble);a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a;D=np.longdouble

def strict(o,v):
 o=np.array(o,dtype=D);v=np.array(v,dtype=D);h=np.cross(np.broadcast_to(v,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-24;inv=np.zeros(len(det),dtype=D);inv[ok]=1/det[ok];ss=o-a;u=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,e1);vv=inv*(q@v);t=inv*np.einsum('ij,ij->i',e2,q);ids=np.where(ok&(u>=-1e-15)&(vv>=-1e-15)&(u+vv<=1+1e-15)&(t>1e-12))[0];ids=ids[np.argsort(t[ids])];res=[]
 for f in ids:
  if not res or abs(float(t[f])-res[-1]['distance_mm'])>1e-11:res.append({'distance_mm':float(t[f]),'face_id':int(f),'barycentric':[float(1-u[f]-vv[f]),float(u[f]),float(vv[f])]})
 return res

def winding(p):
 v=tri-np.array(p,dtype=D);v/=np.linalg.norm(v,axis=2)[:,:,None];num=np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2]));den=1+np.einsum('ij,ij->i',v[:,0],v[:,1])+np.einsum('ij,ij->i',v[:,1],v[:,2])+np.einsum('ij,ij->i',v[:,2],v[:,0]);return float(np.arctan2(num,den).sum()/(2*np.pi))
d=pd.read_csv(R/'all-original.csv');bad=d[(d.inside_control!=1)|(d.outside_control!=0)|(d.mid_control!=1)|(d.after_exit_control!=0)];short=d[d.first_solid<.8];out=[]
for i,r in bad.iterrows():
 p=r[['x','y','z']].to_numpy(float);n=r[['nx','ny','nz']].to_numpy(float);o=p+n*1e-5;h=strict(o,-n);tests=[]
 for role,t in [('origin',0),('surface_inside',1.1e-5),('before',h[0]['distance_mm']-1e-5),('mid',(h[0]['distance_mm']+h[1]['distance_mm'])/2),('after_first',h[1]['distance_mm']+min(1e-5,(h[2]['distance_mm']-h[1]['distance_mm'])/2) if len(h)>2 else h[1]['distance_mm']+1e-5)]:
  pp=o-n*t;tests.append({'role':role,'point_mm':pp.tolist(),'winding':winding(pp)})
 out.append({'csv_index':int(i),'original':r.to_dict(),'strict_hits':h,'strict_first_chord_mm':h[1]['distance_mm']-h[0]['distance_mm'],'tests':tests})
 print(int(i),int(r.face),[(q['role'],round(q['winding'],6))for q in tests],flush=True)
(R/'control-diagnosis.json').write_text(json.dumps({'stl_sha256':hashlib.sha256(raw).hexdigest(),'method':'Original triangles longdouble intersection and solid-angle winding; fixed original controls preserved','rows':out},indent=2))
short.to_csv(R/'short-original.csv',index=False);bad.to_csv(R/'control-flags.csv',index=False);(R/'initial-summary.json').write_text(json.dumps({'samples':len(d),'short_under_0_8':len(short),'control_flags':len(bad),'minimum_first_chord_mm':float(d.first_solid.min()),'status':'short chords under analysis; all original flags retained'},indent=2))
