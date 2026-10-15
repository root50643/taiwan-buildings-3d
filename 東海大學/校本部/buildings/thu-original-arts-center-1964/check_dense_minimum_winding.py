#!/usr/bin/env python3
"""Supplementary independent whole-mesh winding at the lowest 30 sampled chords.
This is additional finite evidence, not a replacement for any dense gate.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,lzma,os,subprocess
import numpy as np
from check_dense_surface import compile_helper, controls, parse, sha, raw

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--threads',type=int,default=4);ap.add_argument('--stl',type=Path);a=ap.parse_args();out=a.out;report=json.loads((out/'dense-audit.json').read_text());stl=a.stl or out/'model.stl';assert sha(stl)==report['stl_sha256']
 assert sha(out/'dense-intervals.npz')==report['artifacts']['dense-intervals.npz']['sha256']
 data=np.load(out/'dense-intervals.npz');chosen=np.argsort(data['first_material_mm'])[:30];wanted={int(i)for i in chosen};rows=[];points=[]
 src=out/report['complete_event_stream']['artifact'];opener=lzma.open if src.suffix=='.xz' else gzip.open
 assert sha(src)==report['artifacts'][src.name]['sha256'],'Event container differs from the audited source'
 with opener(src,'rt')as f:
  for line in f:
   h=line.split('|',1)[0].split(',',2);k=int(h[0])*10+int(h[1])
   if k not in wanted:continue
   fi,si,p,n,valid,parity,events,bounds,groups=parse(line)
   cs=controls(p,n,float(data['entry_t_mm'][k]),float(data['first_exit_t_mm'][k]),float(data['next_entry_t_mm'][k]));assert len(cs)==5
   rows.append({'face':fi,'sample':si,'first_material_mm':float(data['first_material_mm'][k]),'controls':cs,'start':len(points)});points.extend(c['point_mm']for c in cs)
 assert len(rows)==len(wanted)
 work=out/'dense-work';work.mkdir(exist_ok=True);raw(stl)['v'].astype('<f8').tofile(work/'triangles.bin');exe=compile_helper('dense_winding_parallel',work,True);np.asarray(points,dtype='<f8').tofile(work/'minimum-winding-points.bin')
 subprocess.run([str(exe),str(work/'triangles.bin'),str(work/'minimum-winding-points.bin'),str(work/'minimum-winding.csv')],check=True,env={**os.environ,'OMP_NUM_THREADS':str(a.threads)})
 values=np.loadtxt(work/'minimum-winding.csv',delimiter=',',ndmin=2)[:,1];assert len(values)==len(points);maxerror=0
 for row in rows:
  for j,c in enumerate(row['controls']):
   val=float(values[row['start']+j]);err=abs(val-c['expected_winding']);maxerror=max(maxerror,err);c['winding']=val;c['passed']=bool(np.isfinite(val)and err<1e-7)
  del row['start']
 r={'stl_sha256':report['stl_sha256'],'method':'Supplementary compensated whole-original-mesh solid-angle winding, selecting the 30 shortest dense first-material intervals without altering any source row or original normal. Five independent material/air points each; tolerance 1e-7.','samples':len(rows),'point_controls':len(points),'maximum_winding_error':maxerror,'passed':all(c['passed']for row in rows for c in row['controls']),'source_stl':stl.name,'rows':rows}
 (out/'dense-minimum-winding.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='rows'},indent=2));return 0 if r['passed']else 1
if __name__=='__main__':raise SystemExit(main())
