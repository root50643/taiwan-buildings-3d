"""CSU 03A/B/C: one photograph-based representative model, two printable parts.

python source/build_model.py --output-dir models/v2
All coordinates are local mm estimates, not a measured plan. No photo files needed.
"""
import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64, CrossSection, OpType

ROOT = Path(__file__).resolve().parents[1]

def box(cx, cy, z, w, d, h):
    return Manifold.cube((w,d,h)).translate((cx-w/2,cy-d/2,z))

def octagon(w,d,c):
    return [(-w/2+c,-d/2),(w/2-c,-d/2),(w/2,-d/2+c),
            (w/2,d/2-c),(w/2-c,d/2),(-w/2+c,d/2),
            (-w/2,d/2-c),(-w/2,-d/2+c)]

def frustum(bottom,top,h):
    verts=np.array([(x,y,0) for x,y in bottom]+[(x,y,h) for x,y in top],float)
    faces=[];n=len(bottom)
    for i in range(1,n-1):
        faces.extend([(0,i+1,i),(n,n+i,n+i+1)])
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j),(i,n+j,n+i)])
    m=Manifold(Mesh64(verts,np.array(faces,dtype=np.uint64)))
    assert m.status().name=='NoError',m.status()
    return m

def gable(w,y0,y1,z,h):
    # Closed solid triangular prism, narrows upward. No hollow porch/ceiling.
    verts=np.array([[-w/2,y0,z],[w/2,y0,z],[0,y0,z+h],
                    [-w/2,y1,z],[w/2,y1,z],[0,y1,z+h]])
    faces=np.array([(0,1,2),(3,5,4),(0,3,4),(0,4,1),
                    (1,4,5),(1,5,2),(2,5,3),(2,3,0)],np.uint64)
    return Manifold(Mesh64(verts,faces))

def mesh(m):
    assert m.status().name=='NoError', m.status()
    a=m.to_mesh64()
    return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=False)

def make(p):
    solids=[];cuts=[];features=[]
    def add(name,cx,cy,z,w,d,h):
        solids.append(box(cx,cy,z,w,d,h))
        features.append(dict(name=name,kind='solid',center_xy=[cx,cy],bottom=z,extents=[w,d,h]))
    def cut(name,cx,cy,z,w,d,h):
        cuts.append(box(cx,cy,z,w,d,h))
        features.append(dict(name=name,kind='cut',center_xy=[cx,cy],bottom=z,extents=[w,d,h]))
    b=p['base'];g=b['thickness'];w=p['wings'];c=p['center'];t=p['parapet'];e=p['entrance']
    add('display plinth',0,0,0,b['width'],b['depth'],g)
    add('central higher main block',0,0,g,c['width'],c['depth'],c['height'])
    for side in [-1,1]:
        lo,hi=sorted([side*w['inner_x'],side*w['span']/2])
        xc=(lo+hi)/2;wc=hi-lo
        add('long wing '+str(side),xc,(w['front_y']+w['rear_y'])/2,g,wc,27,w['height'])
        # End stair/pier outline is visibly broad; filled at miniature scale.
        add('end vertical stair pier '+str(side),side*86,-0.5,g,12,33,65)
        # A shallow terrace, with solid deck below and 2mm rooted parapet.
        outer=box(xc,2.5,g+64,wc,27,t['height'])
        inner=box(xc,2.5,g+64,wc-2*t['thickness'],27-2*t['thickness'],t['height']+1)
        solids.append(outer-inner)
        features.append(dict(name='wing terrace parapet '+str(side),kind='wall',thickness=t['thickness'],bottom=g+64,top=g+66))
        # Grouped front bands and back bands, all with 0.4mm solid-backed relief.
        for level in range(1,9):
            z=g+level*6.4
            for x in np.arange(lo+5,hi-3,5.5):
                if abs(x)>79: continue
                cut('front wing pane',float(x),-10.9,z,3.6,0.6,2.4)
                cut('rear wing pane',float(x),15.9,z,3.6,0.6,2.4)
        for z in [g+9,g+18,g+27,g+36,g+45,g+54]:
            cut('end vertical recessed bay',side*92,1,z,0.8,20,5)
        # v2: omit optional protruding piers; window cuts narrowed their edges
        # to 0.8mm in v1. Retained facade between panes provides visual rhythm.
    # Central facade grid uses fewer deep openings; front clerestory is also relief.
    for z in np.arange(g+34,g+68,6):
        for x in [-19,-12,-5,5,12,19]:
            cut('central front pane',x,-17.9,float(z),4.4,0.6,3.8)
    for z in np.arange(g+7,g+68,6):
        for x in [-18,-10,-2,6,14]:
            cut('central rear pane',x,17.9,float(z),5.4,0.6,3.3)
    cl=p['clerestory']
    add('clerestory solid support',0,0,g+c['height'],cl['width'],cl['depth'],cl['height'])
    for x in [-15,-7.5,0,7.5,15]:
        cut('clerestory front relief',x,-13.9,g+c['height']+2,5.4,0.6,3)
        cut('clerestory rear relief',x,13.9,g+c['height']+2,5.4,0.6,3)
    # Source-visible front raised side shoulders. No speculative rear additions.
    for side in [-1,1]:
        add('central shoulder',side*23.5,-2,g+64,5,32,11)
    add('filled entrance porch',0,e['front_y']+e['depth']/2,g,e['width'],e['depth']+0.4,e['wall_height'])
    solids.append(gable(e['width'],-29,-15.5,g+e['wall_height'],e['gable_rise']))
    features.append(dict(name='filled front gable',kind='solid_prism',bounds=[[-17,-29,g+24],[17,-15.5,g+33]],simplification='Solid-backed porch; no hidden interior or trapped support'))
    cut('entrance shallow door',0,-28.9,g+4,17,0.7,13)
    # Three broad, rooted entry steps. Unmeasured and deliberately shortened.
    for i in range(3):
        add('entry step '+str(i),0,-29.8-i*0.8,g,23,2.8+i*2.4,3.6-i*1.0)
    body=Manifold.batch_boolean(solids,OpType.Add)
    body=body-Manifold.batch_boolean(cuts,OpType.Add)
    r=p['roof']
    roof=frustum(octagon(r['bottom_width'],r['bottom_depth'],r['bottom_chamfer']),
                 octagon(r['top_width'],r['top_depth'],r['top_chamfer']),r['height'])
    placed=roof.translate((0,0,r['assembly_bottom_z']))
    # Display union only: main print route is the two separate flat-bottom parts.
    assembly=body+placed
    return {'body':body,'roof':roof,'assembly':assembly},features

def main():
    a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,default=ROOT/'models/v2');args=a.parse_args()
    p=json.loads((ROOT/'parameters.json').read_text(encoding='utf8'));out=args.output_dir;out.mkdir(parents=True,exist_ok=True);(out/'parts').mkdir(exist_ok=True)
    built,features=make(p);report={'version':p['version'],'units':'mm','parameter_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),'libraries':{n:version(n) for n in ['numpy','trimesh','manifold3d']},'parts':{},'feature_ledger':features}
    for name,m in built.items():
        dest=out/('assembly.stl' if name=='assembly' else 'parts/'+name+'.stl')
        tm=mesh(m);tm.export(dest)
        report['parts'][name]={'path':dest.relative_to(out).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bounds_mm':tm.bounds.tolist(),'triangles':len(tm.faces),'volume_mm3':float(tm.volume),'manifold_status':m.status().name,'printable_route':name!='assembly'}
    report['assembly_placement']={'body_translation_mm':[0,0,0],'roof_translation_mm':[0,0,p['roof']['assembly_bottom_z']],'roof_joint':'flat butt contact at z85; centered in x and y; glue after trial fit','counting':'One representative building model set, two physical print parts'}
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report['parts'],indent=2))

if __name__=='__main__': main()
