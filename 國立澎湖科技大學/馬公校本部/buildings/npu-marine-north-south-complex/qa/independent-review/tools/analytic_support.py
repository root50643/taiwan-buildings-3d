"""Bounded independent G-code coverage audit. No polygon overlay or mesh edits.
Analytic line/capsule intervals use unchanged G-code coordinates and active widths.
Finite nominal bead footprints are a deposition proxy, not physics or print approval.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,ast,hashlib,json,math,re,time
import numpy as np
TOK=re.compile(r'([A-Z])\s*([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)')
EXCLUDE={'Custom','Skirt/Brim','Support material','Support material interface'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Reuse only the previously reviewed independent parser, never candidate QA code.
def load_parser(path):
 tree=ast.parse(Path(path).read_text());nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['Motion','parse','fixture']]
 assert len(nodes)==3
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),globals())
 assert fixture()
def intervals(a,b,segments,extra=0):
 """Intervals t in [0,1] for A+t(B-A) inside union of straight capsules."""
 if not len(segments):return []
 c=segments[:,:2];e=segments[:,2:4];d=b-a;v=e-c;length=np.sqrt((v*v).sum(1));u=v/length[:,None];r=segments[:,5]/2+extra
 # Rectangular strip of each capsule, exact linear clipping.
 ac=a-c;s=(ac*u).sum(1);ds=u@d;h=u[:,0]*ac[:,1]-u[:,1]*ac[:,0];dh=u[:,0]*d[1]-u[:,1]*d[0]
 lo=np.zeros(len(c));hi=np.ones(len(c));valid=np.ones(len(c),bool)
 for val,delta,mn,mx in [(s,ds,np.zeros(len(c)),length),(h,dh,-r,r)]:
  zero=delta==0;valid &= ~zero | ((val>=mn)&(val<=mx));nz=~zero
  p=np.full(len(c),-np.inf);q=np.full(len(c),np.inf);p[nz]=(mn[nz]-val[nz])/delta[nz];q[nz]=(mx[nz]-val[nz])/delta[nz]
  lo=np.maximum(lo,np.minimum(p,q));hi=np.minimum(hi,np.maximum(p,q))
 valid &= hi>=lo;out=list(zip(lo[valid].tolist(),hi[valid].tolist()))
 # Round ends; no polygon approximation, no snapping, no tolerance dilation.
 aa=float(d@d)
 for center in [c,e]:
  ac=a-center;bb=2*(ac@d);cc=(ac*ac).sum(1)-r*r;disc=bb*bb-4*aa*cc;ok=disc>=0
  root=np.sqrt(np.maximum(disc,0));l=np.maximum(0,(-bb-root)/(2*aa));h=np.minimum(1,(-bb+root)/(2*aa));ok &= h>=l
  out.extend(zip(l[ok].tolist(),h[ok].tolist()))
 merged=[]
 for l,h in sorted(out):
  if not merged or l>merged[-1][1]:merged.append([l,h])
  else:merged[-1][1]=max(merged[-1][1],h)
 return merged
def gaps(iv):
 last=0.;out=[]
 for l,h in iv:
  if l>last:out.append([last,l])
  last=max(last,h)
 if last<1:out.append([last,1.])
 return out
class Grid:
 def __init__(self,a,size=3):
  self.a=a;self.size=size;self.g=defaultdict(list)
  for i,s in enumerate(a):
   r=s[5]/2;self.add(i,np.minimum(s[:2],s[2:4])-r,np.maximum(s[:2],s[2:4])+r)
 def keys(self,lo,hi):
  l=np.floor(lo/self.size).astype(int);h=np.floor(hi/self.size).astype(int)
  for x in range(l[0],h[0]+1):
   for y in range(l[1],h[1]+1):yield x,y
 def add(self,i,lo,hi):
  for k in self.keys(lo,hi):self.g[k].append(i)
 def query(self,a,b,r=0):
  ids=set()
  for k in self.keys(np.minimum(a,b)-r,np.maximum(a,b)+r):ids.update(self.g.get(k,[]))
  return np.array(sorted(ids),int)
def controls():
 def seg(a,b,w):return np.array([[*a,*b,1,w,.2,1,0,0]],float)
 cases=[('full_overlap',[-1,0],[3,0],seg([0,0],[2,0],2),[[0,1]]),('finite_gap',[0,0],[10,0],seg([0,0],[2,0],2),[[0,.3]]),('parallel_tangent',[0,1],[2,1],seg([0,0],[2,0],2),[[0,1]]),('parallel_separate',[0,1.000001],[2,1.000001],seg([0,0],[2,0],2),[]),('cross_capsule',[1,-2],[1,2],seg([0,0],[2,0],2),[[.25,.75]]),('reverse',[10,0],[0,0],seg([0,0],[2,0],2),[[.7,1]])]
 out=[]
 for name,a,b,s,expected in cases:
  actual=intervals(np.array(a,float),np.array(b,float),s);assert np.allclose(actual,expected,atol=1e-14), (name,actual);out.append({'case':name,'actual':actual,'pass':True})
 # Two separated anchors preserve the exact central gap.
 s=np.vstack([seg([0,0],[2,0],1),seg([8,0],[10,0],1)]);actual=gaps(intervals(np.array([0.,0.]),np.array([10.,0.]),s));assert np.allclose(actual,[[.25,.75]])
 out.append({'case':'two_anchors_preserve_gap','actual':actual,'pass':True});return out

def layer_review(a,prev,roles,z,idx):
 grid=Grid(prev);rows=[];direct=np.zeros(len(a),bool)
 for j,s in enumerate(a):
  aa=s[:2];bb=s[2:4];d=bb-aa;length=float(np.linalg.norm(d));ids=grid.query(aa,bb,s[5]/2);ss=prev[ids]
  iv=intervals(aa,bb,ss);direct[j]=bool(intervals(aa,bb,ss,s[5]/2))
  for l,h in gaps(iv):
   gap=(h-l)*length
   if gap<=1e-9:continue
   p=aa+l*d;q=aa+h*d
   rows.append({'layer':idx+1,'z_mm':z,'line':int(s[7]),'role':roles[int(s[8])],'width_mm':float(s[5]),'coords':[p.tolist(),q.tolist()],'length_mm':gap,'endpoint_previous_bead_anchors':[l>0,h<1]})
 # Current layer segment-contact graph: finite nominal capsule contact.
 current=Grid(a);parent=list(range(len(a)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for j,s in enumerate(a):
  ids=current.query(s[:2],s[2:4],s[5]/2);ids=ids[ids<j]
  for k in ids:
   if root(j)!=root(int(k)) and intervals(s[:2],s[2:4],a[k:k+1],s[5]/2):parent[root(j)]=root(int(k))
 groups=defaultdict(list)
 for j in range(len(a)):groups[root(j)].append(j)
 detached=[g for g in groups.values() if not direct[g].any()]
 return rows,{'index':idx+1,'z_mm':z,'segments':len(a),'previous_segments':len(prev),'current_nominal_bead_components':len(groups),'components_without_previous_bead_contact':len(detached),'unanchored_component_lines':[[int(a[j,7]) for j in g] for g in detached],'centerline_gap_count':len(rows),'longest_centerline_gap_mm':max((x['length_mm'] for x in rows),default=0)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--parser',required=True);ap.add_argument('--out',required=True);ap.add_argument('--part');args=ap.parse_args();P=Path(args.package);O=Path(args.out);O.mkdir(parents=True,exist_ok=True);load_parser(args.parser);save(O/'controls.json',controls())
 parts=json.loads((P/'qa/final_slice_evidence.json').read_text())['parts'];summaries=[];seen={}
 for part in parts:
  pid=part['id']
  if args.part and pid!=args.part:continue
  g=P/part['gcode_path'];m=P/part['input_stl'];assert sha(g)==part['gcode_sha256'] and sha(m)==part['input_sha256'];data=parse(g);assert not data['unsupported'] and not data['nonplanar_lines'];key=(sha(g),sha(m));record={'id':pid,'gcode_sha256':sha(g),'stl_sha256':sha(m),'command_sha256':data['command_sha256'],'total_layers':len(data['layers']),'parsed_lines':data['parser_lines']}
  if key in seen:record['same_exact_gcode_and_STL_as']=seen[key];summaries.append(record);continue
  seen[key]=pid;roles=data['roles'];layers=data['layers'];body=[]
  for l in layers:
   a=l['paths'];body.append(a[[roles[int(i)] not in EXCLUDE for i in a[:,8]]])
  if pid.startswith(('01','02','03')):
   selected={i for i,a in enumerate(body) if any(roles[int(x)]=='Bridge infill' for x in a[:,8])}
   selected|={i for i,l in enumerate(layers) if any(abs(l['z']-z)<1e-8 for z in [7.8,8,8.2,16.8,17,17.2,18,18.2,18.4,18.6,19,19.2])}
   if pid.startswith(('02','03')):selected|=set(range(len(layers)-6,len(layers)))
   if pid.startswith('03'):selected|={i for i,l in enumerate(layers) if any(abs(l['z']-z)<1e-8 for z in [27,27.2,27.4,27.6,28,28.2,28.4,28.6,29,29.2])}
   selected={i for i in selected if i>0};scope='All Bridge infill layers plus specified stair-header/roof transition layers and final six fin layers (02/03); bounded, not all-layer coverage.'
  else:selected=set(range(1,len(layers)));scope='Every post-first-layer model extrusion; first layer rests on bed.'
  rows=[];summ=[];start=time.time()
  for i in sorted(selected):
   rr,ss=layer_review(body[i],body[i-1],roles,layers[i]['z'],i);rows+=rr;summ.append(ss)
  save(O/(pid+'-all-residual-gaps.json'),rows);save(O/(pid+'-layers.json'),summ)
  maximum={}
  for r in rows:
   if r['role'] not in maximum or r['length_mm']>maximum[r['role']]['length_mm']:maximum[r['role']]=r
  record.update({'scope':scope,'selected_layer_count':len(summ),'selected_layers':[x['index'] for x in summ],'selected_segments':sum(x['segments'] for x in summ),'all_residual_gaps_over_1e_9_mm_retained':len(rows),'gap_file':pid+'-all-residual-gaps.json','components_without_previous_bead_contact':sum(x['components_without_previous_bead_contact'] for x in summ),'max_gaps_by_role':maximum,'elapsed_seconds':time.time()-start});summaries.append(record);save(O/'summary.json',{'fixed_candidate':'c2172ad91cbfb8189d02615a03dfe2ddf3f15bc1','method':'Analytic straight-segment/capsule intervals; finite active nominal bead widths; no GEOS/no polygon repair/no coordinate snap/no dilation; centerline residual cutoff1e-9mm only. Current-layer contact graph is a digital nominal-footprint observation, not deposition-order, thermal or mechanical proof. Sparse infill gaps are retained and are not automatically free bridge defects.','parser_fixture':True,'parts':summaries});print(pid,'layers',len(summ),'gaps',len(rows),'unanchored',record['components_without_previous_bead_contact'],'seconds',round(time.time()-start,2),flush=True)
if __name__=='__main__':main()
