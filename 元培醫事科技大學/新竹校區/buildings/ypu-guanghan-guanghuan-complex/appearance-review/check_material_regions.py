from pathlib import Path
import bpy,json,sys,numpy as np,collections
R=Path(__file__).resolve().parent; root=R.parent
C=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else root
bpy.ops.wm.open_mainfile(filepath=str(C/'appearance.blend'))
m=next(o.data for o in bpy.context.scene.objects if o.type=='MESH');V=np.array([v.co[:] for v in m.vertices]);S=1.07;B=1.6;eps=.006
plan=json.loads((R/'material-plan.json').read_text());chains=plan['chains']; rows=[(5.4,8),(9.5,12.2),(13.7,16.4),(17.9,20.6),(22.1,24.8)]
def data(p,s):
 a=np.array(s['a_mm']);u=np.array(s['tangent']);n=np.array(s['normal']);v=V[list(p.vertices)];return v,(v[:,:2]-a)@u,(v[:,:2]-a)@n,np.linalg.norm(np.array(s['b_mm'])-a)
def plane(p,s,off,rr):
 v,t,d,l=data(p,s)
 return min(t)>=-eps and max(t)<=l+eps and max(abs(d-off))<eps and any(min(v[:,2])>=B+lo*S-eps and max(v[:,2])<=B+hi*S+eps for lo,hi in rr)
def perg(p,s):
 v,t,d,l=data(p,s);z=(v[:,2]-B)/S;t=t/S;d=d/S;l=l/S
 good=np.zeros(3,bool)
 for width,lo,hi in [(1.1,26.6,27.6),(1.6,28.3,29.3)]:good|=(t>=-eps)&(t<=l+eps)&(abs(d)<=width/2+eps)&(z>=lo-eps)&(z<=hi+eps)
 a=np.array(s['a_mm'])/S;b=np.array(s['b_mm'])/S
 for tt in np.linspace(0,1,max(2,round(l/3))):
  q=a+(b-a)*tt;good|=(np.max(abs(v[:,:2]/S-q),axis=1)<=.7+eps)&(z>=26.5-eps)&(z<=28.6+eps)
 return all(good)
fail=[];ovalwall=[];counts=collections.Counter();offsets=collections.Counter();oval={'wide':[],'narrow':[]};colored=[]
rot=np.array([[np.cos(-.8),-np.sin(-.8)],[np.sin(-.8),np.cos(-.8)]]);center=np.array([(1152-790)*.13554824373866425,(640-679)*.13554824373866425])*S
for p in m.polygons:
 i=p.material_index;v=V[list(p.vertices)];ok=i==0
 if i==1:ok=any(plane(p,s,0,[(0,26)]) for k in ['Hfront','Lfront','Gface'] for s in chains[k])
 if i in (2,3):
  ks=['Hfront','Lfront'] if i==2 else ['Gface'];rr=rows if i==2 else [(6,8.5),(9.5,12),(13,15.5),(16.5,19),(20,23.3)];dep=(.34 if i==2 else .15)*S
  for k in ks:
   for j,s in enumerate(chains[k]):
    for sign in [-1,1]:
     if plane(p,s,sign*dep,rr):ok=True;offsets[f'{k}_{j}_{sign}']+=1
 local=(v[:,:2]-center)@rot/S;zz=(v[:,2]-B)/S
 unit=local/np.array([7,3.5]); oval_side=False
 if min(local[:,1])>=-.006 and min(zz)>=-.04 and max(zz)<=29.106 and abs(p.normal.z)<.01:
  for k in range(48):
   theta=(k+.5)*2*np.pi/48; nn=np.array([np.cos(theta),np.sin(theta)])
   if max(abs(unit@nn-np.cos(np.pi/48)))<.002 and np.dot(np.array(p.normal[:2])@rot,local.mean(axis=0))>0:oval_side=True
 if i==1 and oval_side:ok=True;ovalwall.append(p.index)
 wide=max(abs(local[:,1]-2.975))<.006 and min(local[:,0])>=-4.006 and max(local[:,0])<=4.006 and any(min(zz)>=lo-.006 and max(zz)<=hi+.006 for lo,hi in rows)
 if i==2 and wide:ok=True
 if i==4:ok=any(perg(p,s) for k in ['Hfront','Lfront'] for s in chains[k])
 if not ok:fail.append({'face':p.index,'material':i,'vertices':v.tolist()})
 counts[i]+=1
 local=(v[:,:2]-center)@rot/S;zz=(v[:,2]-B)/S
 if max(abs(local[:,1]-2.975))<.006 and min(local[:,0])>=-4.006 and max(local[:,0])<=4.006 and any(min(zz)>=lo-.006 and max(zz)<=hi+.006 for lo,hi in rows):oval['wide'].append(p.index)
 if max(abs(local[:,0]-6.35))<.006 and any(min(local[:,1])>=lo-.006 and max(local[:,1])<=hi+.006 for lo,hi in [(-.95,-.25),(.25,.95)]) and min(zz)>=5.994 and max(zz)<=24.406:oval['narrow'].append(p.index)
result={'passed':not fail,'counts':dict(counts),'oval_positive_half_wall_faces':ovalwall,'failures':fail,'actual_window_offset_counts':dict(offsets),'oval_exact_existing_back_faces':oval,'notes':['Full vertices tested against original planes and true pergola primitive footprints, not broad component centroid.','v2 permits source-approved positive-local-v original oval outer facets and ten wide cut backs; no absent narrow slots manufactured.']}
name='clean-material-region-check.json' if 'clean' in C.name else 'material-region-check.json';(R/name).write_text(json.dumps(result,indent=2));print(json.dumps(result))
