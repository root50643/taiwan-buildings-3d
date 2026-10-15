"""Summarize every original face sample without discarding short chords or air."""
from pathlib import Path
import csv,gzip,json,hashlib,collections,math
R=Path(__file__).resolve().parent;count=0;short=0;faces=set();bad=[];mins=[]
for r in csv.DictReader(gzip.open(R/'dense-samples.csv.gz','rt')):
 count+=1;t=float(r['first_solid'])
 if t<.8:short+=1;faces.add(int(r['face']))
 if tuple(int(r[k]) for k in ['inside_control','outside_control','mid_control','after_exit_control'])!=(1,0,1,0):bad.append(r)
 mins.append(t)
b=json.loads((R/'dense-sampling-binding.json').read_text());sha=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest();checks={'sample_count_matches_all_seven_per_face':count==b['sample_count'],'bound_to_current_stl':sha==b['stl_sha256'],'all_four_sample_controls_expected':not bad};j={'stl_sha256':sha,'passed':all(checks.values()),'checks':checks,'sample_count':count,'short_first_segments_under_0p8mm':short,'faces_with_short_samples':len(faces),'minimum_first_segment_mm':min(mins),'control_failures':bad,'limits':'Short original normal segments remain in CSV; separate nominated backing/corner-root reports do not alter them or imply global minimum wall thickness.'};(R/'dense-summary.json').write_text(json.dumps(j,indent=2));print({k:v for k,v in j.items() if k!='control_failures'});assert all(checks.values())
