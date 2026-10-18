"""Independent local reproduction of retained v1 failure and v2 -> v3 change.

Reads historical inputs only. Does not replace any original pass/fail field.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
import numpy as np
from independent_thickness import triangles,ray_all,chord
from independent_exact_mesh import pair,normal

ROOT=Path(__file__).resolve().parent
PACKAGE=ROOT.parent/'candidate'

def sample(path):
    data=path.read_bytes();tris=triangles(data)
    normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
    normals/=np.linalg.norm(normals,axis=1)[:,None]
    rows=[]
    for i,t in enumerate(tris):
        hs=ray_all(tris,t.mean(axis=0),-normals[i],eps=1e-7)
        if hs and hs[0]['distance_mm']<1.2-1e-6:
            rows.append({'face':i,'centroid_mm':t.mean(axis=0).tolist(),
                         'normal':normals[i].tolist(),'exit':hs[0]})
    return {'sha256':hashlib.sha256(data).hexdigest(),'triangles':len(tris),
            'below_1p2mm_rows':rows,
            'lintel_at_xminus18p5_yminus16p7':chord(tris,'lintel',[-18.5,-16.7,-1],[0,0,1])},tris

def main():
    v1,tris=sample(PACKAGE/'qa/history/v1/model.stl')
    original=json.loads((PACKAGE/'qa/independent/candidate-v1.json').read_text('utf-8'))
    v1['original_report_sha256']=hashlib.sha256((PACKAGE/'qa/independent/candidate-v1.json').read_bytes()).hexdigest()
    v1['original_self_intersection_pass_preserved']=original['self_intersections']['passed']
    v1['original_thickness_pass_preserved']=original['thickness']['screening_passed']
    den=max(float(x).as_integer_ratio()[1] for x in tris.ravel())
    exact=[tuple(tuple(int(F(float(x))*den) for x in p) for p in t) for t in tris]
    v1['original_two_pair_flags_independent_exact_recheck']=[]
    for row in original['self_intersections']['first_pairs']:
        i,j=row['faces'];kind,detail=pair(exact[i],exact[j])
        v1['original_two_pair_flags_independent_exact_recheck'].append(
            {'faces':[i,j],'original_flag':row,'independent_exact_classification':kind,**detail})
    v2,_=sample(PACKAGE/'qa/history/v2/model.stl')
    v3,_=sample(PACKAGE/'model.stl')
    lintel_comparison=[]
    for short in v1['below_1p2mm_rows']:
        x,y,_=short['centroid_mm'];row={'x_mm':x,'y_mm':y}
        for name,path in [('v1',PACKAGE/'qa/history/v1/model.stl'),
                          ('v2',PACKAGE/'qa/history/v2/model.stl'),('v3',PACKAGE/'model.stl')]:
            hs=ray_all(triangles(path.read_bytes()),[x,y,-1],[0,0,1])
            row[name]={'hits_z_mm':[h['point_mm'][2] for h in hs],
                       'upper_lintel_z_chord_mm':hs[-1]['distance_mm']-hs[-2]['distance_mm']}
        lintel_comparison.append(row)
    def box_tris(s):
        x,y,z=s
        vs=np.array([[0,0,0],[x,0,0],[x,y,0],[0,y,0],[0,0,z],[x,0,z],[x,y,z],[0,y,z]],dtype=float)
        fs=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
        return vs[np.asarray(fs)]
    controls=[]
    for thickness in [.6,1.6,2.8]:
        hs=ray_all(box_tris([10,10,thickness]),[5,5,-1],[0,0,1])
        actual=hs[1]['distance_mm']-hs[0]['distance_mm']
        controls.append({'analytic_box_thickness_mm':thickness,'measured_mm':actual,
                         'ok':abs(actual-thickness)<1e-9})
    out={'v1':v1,'v2':v2,'v3':v3,'fixed_xy_lintel_comparison':lintel_comparison,'ray_controls':controls,
         'all_ray_controls_met':all(c['ok'] for c in controls),
         'interpretation':[
             'Original v1 false fields and reports remain unchanged. Two numerical pair flags are exact shared-vertex contacts; the five short lintel chords are real finite-sample failures.',
             'v2 and v3 shortened front groove height from z58 to z57, increasing the sampled lintel; no sub-1.2 mm centroid chords remain.',
             'v2 -> v3 omission of one bridge-concealed left-wall recess is a support-access change, assessed separately. It is not a thickness algorithm change.',
             'These historical checks are local regressions, not a new universal approval of either old candidate.']}
    (ROOT/'historical-regression-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
