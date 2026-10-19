from pathlib import Path
from collections import Counter,defaultdict
import hashlib,re
import numpy as np
TOK=re.compile(r"([A-Z])\s*([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)")
class Motion:
 def __init__(self):self.xyz=np.zeros(3);self.e=0.;self.a=True;self.ae=True;self.units=1.;self.commands=Counter();self.unsupported=Counter()
 def read(self,s):
  words=TOK.findall(s.split(';',1)[0].upper())
  if not words:return None
  cmd=words[0][0]+str(int(float(words[0][1])));v={k:float(t) for k,t in words[1:]};self.commands[cmd]+=1
  if cmd=='M82':self.ae=True
  elif cmd=='M83':self.ae=False
  elif cmd=='G90':self.a=True
  elif cmd=='G91':self.a=False
  elif cmd=='G20':self.units=25.4
  elif cmd=='G21':self.units=1.
  elif cmd=='G92':
   for i,k in enumerate('XYZ'):
    if k in v:self.xyz[i]=v[k]*self.units
   if 'E' in v:self.e=v['E']*self.units
  elif cmd in ('G0','G1'):
   a=self.xyz.copy();b=a.copy();de=0.
   for i,k in enumerate('XYZ'):
    if k in v:b[i]=v[k]*self.units+(0. if self.a else a[i])
   if 'E'in v:
    ne=v['E']*self.units+(0. if self.ae else self.e);de=ne-self.e;self.e=ne
   self.xyz=b
   return a,b,de
  elif cmd in ('G2','G3','G5','G10','G11'):self.unsupported[cmd]+=1

def fixture():
 p=Motion();r=[]
 for s in ['M82','G90','G92 E0','G0 X1 Y2 Z.2','G1 X3 E1','G92 E0','G1 Y4 E.5','M83','G1 X4 E.25','G1 E-.2','G91','G0 X1 Z.2','G1 Y1 E.1','G90','M82','G92 E4','G1 X7 E4.3']:
  v=p.read(s)
  if v is not None:r.append([*v[1],v[2]])
 expected=[[1,2,.2,0],[3,2,.2,1],[3,4,.2,.5],[4,4,.2,.25],[4,4,.2,-.2],[5,4,.4,0],[5,5,.4,.1],[7,5,.4,.3]]
 assert np.allclose(r,expected,atol=1e-10)
 return True

def parse(path):
 p=Motion();layers=[];l=None;role='Custom';roles=[];width=.45;height=.2;chain=0;lastrole=None;lastend=None;metadata={};comment_counts=Counter();stats=defaultdict(lambda:defaultdict(float));motion_sha=hashlib.sha256();stationary=0.;negative=0.;nonplanar=[]
 for ln,s in enumerate(path.open(encoding='utf8'),1):
  s=s.strip();code=s.split(';',1)[0].strip()
  if code:motion_sha.update((code+'\n').encode())
  if s==';LAYER_CHANGE':l={'z':None,'paths':[]};layers.append(l);chain+=1;lastend=None
  elif s.startswith(';Z:'):l['z']=float(s[3:])
  elif s.startswith(';TYPE:'):
   role=s[6:]
   if role not in roles:roles.append(role)
  elif s.startswith(';WIDTH:'):width=float(s[7:])
  elif s.startswith(';HEIGHT:'):height=float(s[8:])
  if s.startswith('; ') and ' = 'in s:
   k,v=s[2:].split(' = ',1);metadata[k]=v
  r=p.read(s)
  if r is None:continue
  a,b,e=r;length=float(np.linalg.norm(b-a))
  if e<0:negative+=e
  if e<=1e-9 or length<1e-9:
   if e>0:stationary+=e
   if length>1e-9 or e<0:chain+=1;lastend=None
   continue
  if l is None:raise ValueError('Unlayered extrusion '+str(ln))
  if abs(a[2]-b[2])>1e-6:nonplanar.append(ln)
  if lastend is None or np.linalg.norm(a[:2]-lastend)>1e-5 or role!=lastrole:chain+=1
  lastend=b[:2].copy();lastrole=role
  annotation='brim' if '; brim'in s else ('skirt' if '; skirt'in s else '')
  if annotation:comment_counts[annotation]+=1
  # x1,y1,x2,y2,filament E,width,active HEIGHT,line,role index,chain
  l['paths'].append([a[0],a[1],b[0],b[1],e,width,height,ln,roles.index(role),chain])
  for k,v in [('segments',1),('length_mm',length),('positive_e_mm',e)]:stats[role][k]+=v
 for l in layers:l['paths']=np.asarray(l['paths'],dtype=float).reshape(-1,10)
 return {'layers':layers,'roles':roles,'stats':dict(stats),'metadata':metadata,'parser_lines':ln,'commands':dict(p.commands),'unsupported':dict(p.unsupported),'nonplanar_lines':nonplanar,'positive_stationary_e_mm':stationary,'negative_e_mm':negative,'command_sha256':motion_sha.hexdigest(),'comments':dict(comment_counts)}
