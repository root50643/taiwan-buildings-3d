"""Exact interval coverage of every bridge-tagged actual XY segment.

Reuses our own earlier independent modal/capsule implementation, never the
candidate's audit code. This is planned line footprint coverage, not molten
bead behavior or a physical bridge success test.
"""
from pathlib import Path
import importlib.util,json,hashlib,sys
import numpy as np
R=Path(__file__).resolve().parent
SOURCE=R/'modal_capsule_helpers.py'
spec=importlib.util.spec_from_file_location('previous_independent_capsule_code',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main():
    report={'method':'Independent modal parse; exact query-line intersection with union of previous extrusion capsules (analytic rectangles and circular ends). No path sampling. Distinguishes whole bridge-tagged path from longest consecutive centerline gap. Other support near the prior-object layer is reported separately. Line coverage is a toolpath abstraction, not measured bead coverage or bridge success.',
        'own_prior_implementation_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'parts':[]}
    paths={n:Path('${ORIGINAL_DIAGNOSTIC_GCODE_DIR}')/(n+'-DIAGNOSTIC-ONLY.gcode') for n in ['main_body','roof','column','mast_brace_frame']}
    if len(sys.argv)>1: paths={'REVIEW-ONLY-main-short-axis':Path(sys.argv[1])}
    for n,gpath in paths.items():
        d=m.parse_gcode(gpath)
        bridges=[s for s in d['_segments'] if s['type']=='Bridge infill'];byz=d['_byz']
        objz=sorted(z for z,v in byz.items() if any(s['type'] not in ('Skirt/Brim','Custom','Unclassified') and not s['type'].startswith('Support') for s in v))
        records=[];cache={}
        for s in bridges:
            z=round(s['b'][2],6);p=max((v for v in objz if v<z-1e-6),default=None)
            key=(z,p)
            if key not in cache:
                prev=[v for v in byz.get(p,[]) if not v['type'].startswith('Support') and v['type']!='Skirt/Brim']
                support=[v for q,ls in byz.items() if p is not None and p-.41<=q<z-.09 for v in ls if v['type'].startswith('Support')]
                def indexed(ls):
                    if not ls:return ls,np.empty((0,2)),np.empty((0,2))
                    lo=np.array([[min(t['a'][i],t['b'][i])-max(.45,t['width'])/2 for i in (0,1)] for t in ls]);hi=np.array([[max(t['a'][i],t['b'][i])+max(.45,t['width'])/2 for i in (0,1)] for t in ls]);return ls,lo,hi
                cache[key]=(indexed(prev),indexed(prev+support))
            def evaluate(index,nominal):
                ls,lo,hi=index
                qlo=np.minimum(s['a'][:2],s['b'][:2]);qhi=np.maximum(s['a'][:2],s['b'][:2]);ix=np.flatnonzero(np.all(hi>=qlo-1e-10,axis=1)&np.all(lo<=qhi+1e-10,axis=1))
                return m.coverage(s,[ls[i] for i in ix],nominal)
            prev,withsupport=cache[key]
            nominal=evaluate(prev,True);declared=evaluate(prev,False);support=evaluate(withsupport,False)
            records.append({'line':s['line'],'a':s['a'],'b':s['b'],'path_length_mm':s['length'],'width_mm':s['width'],'height_mm':s['height'],'z_mm':z,'previous_object_z_mm':p,'gaps_nominal_0p45':nominal,'gaps_declared_width':declared,'gaps_with_near_support_declared_width':support})
        part={'part':n,'bridge_tagged_segments':len(bridges),'longest_whole_tagged_segment_mm':max((s['length'] for s in bridges),default=0),'records':records}
        for key in ['gaps_nominal_0p45','gaps_declared_width','gaps_with_near_support_declared_width']:
            cases=[(gap['length_mm'],record,gap) for record in records for gap in record[key]]
            top=sorted(cases,key=lambda t:t[0],reverse=True)[:20]
            part[key+'_max_mm']=max((t[0] for t in cases),default=0)
            part[key+'_top20']=[{'length_mm':a,'line':b['line'],'z_mm':b['z_mm'],'previous_object_z_mm':b['previous_object_z_mm'],'a':b['a'],'b':b['b'],'gap':c} for a,b,c in top]
        report['parts'].append(part)
        print(n,json.dumps({k:v for k,v in part.items() if k!='records' and not k.endswith('_top20')}),flush=True)
    output='all-bridge-coverage.json' if len(sys.argv)==1 else 'REVIEW-ONLY-short-axis-bridge-coverage.json'
    (R/output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
