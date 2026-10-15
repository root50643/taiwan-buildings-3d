from pathlib import Path
import ast,json,csv,gzip
from config import *
def parse(line):
 hpart,bpart=line.split('|');hh=[]
 for val in hpart.split(';')[1:]:
  t,f,u,v,nd=map(float,val.split(','));rec={'face':int(f),'barycentric':[1-u-v,u,v],'nd':nd}
  if hh and abs(t-hh[-1]['t'])<1e-11:hh[-1]['faces'].append(rec)
  else:hh.append({'t':t,'faces':[rec]})
 bb=[]
 for val in bpart.strip().split(';')[1:]:
  a,b,f,plane,nd=map(float,val.split(','));bb.append({'a':a,'b':b,'face':int(f),'plane':plane,'nd':nd})
 return hh,bb
df=list(csv.DictReader(open(W/'ntou-revision-dense.csv')));bounds=[];first=[];diff=[];flags=[];nohits=[];allbounds=[]
for i,line in enumerate(open(W/'ntou-revision-boundary-events.txt')):
 h,b=parse(line);r=df[i]
 if len(h)<2:nohits.append((i,h,b));continue
 a,z=h[0]['t'],h[1]['t'];c=h[2]['t']if len(h)>2 else None
 overlaps=[]
 for q in b:
  for role,l,rr in [('first',a,z),('after',z,c if c is not None else q['b']),('later',c if c is not None else q['b'],q['b'])]:
   lo=max(q['a'],l);hi=min(q['b'],rr)
   if hi-lo>1e-9:overlaps.append({**q,'role':role,'lo':lo,'hi':hi,'length':hi-lo})
 rec=dict(index=i,face=int(r['face']),sample=int(r['sample']),first_span=z-a,after_span=c-z if c else None,events=h,boundaries=overlaps,raw_boundary_candidates=b,raw_dense={k:float(r[k])for k in ['entry','first_solid','air_after','inside_control','outside_control','mid_control','after_exit_control']})
 if overlaps:bounds.append(rec)
 if b:allbounds.append(rec)
 if any(q['role']=='first'for q in overlaps):first.append(rec)
 if abs(z-a-float(r['first_solid']))>1e-7:diff.append(rec)
 if any(float(r[k])!=v for k,v in [('inside_control',1),('outside_control',0),('mid_control',1),('after_exit_control',0)]):flags.append(rec)
j=dict(samples=len(df),first_boundary_rays=len(first),boundary_rays=len(bounds),boundary_triangles=sum(len(r['boundaries'])for r in bounds),raw_boundary_rays=len(allbounds),raw_boundary_triangles=sum(len(r['raw_boundary_candidates'])for r in allbounds),changed_first_events=len(diff),original_parity_flags=len(flags),nohits=nohits,boundaries=bounds,first_boundary=first,changed=diff,flag_events=flags,all_boundary_events=allbounds)
Path(W/'ntou-revision-boundary-events-summary.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items()if not isinstance(v,list)})
for r in flags:print('FLAG',r['face'],r['sample'],'first',r['first_span'],'bounds',[(q['face'],q['role'],q['lo'],q['hi'])for q in r['boundaries']])
