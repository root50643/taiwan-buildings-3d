"""Read-only independent face-normal and named-feature probes.

Uses a direct all-triangle Moller--Trumbore implementation, rather than importing
the candidate's QA routines or its saved sample results. This is finite sampling,
not a claim about universal local wall thickness or mechanical strength.
"""
from pathlib import Path
import csv, hashlib, json, struct, time
import numpy as np

ROOT = Path(__file__).resolve().parent
MODEL = ROOT.parent / 'candidate' / 'model.stl'

def triangles(data):
    count=struct.unpack_from('<I', data, 80)[0]
    assert len(data)==84+50*count
    return np.array([[struct.unpack_from('<3f', data, 84+50*i+12+12*j)
                      for j in range(3)] for i in range(count)], dtype=float)

def ray_all(tris, origin, direction, eps=1e-9):
    """Return sorted nonnegative intersections, deduplicating shared-edge hits."""
    origin=np.asarray(origin,dtype=float);direction=np.asarray(direction,dtype=float)
    direction=direction/np.linalg.norm(direction)
    e1=tris[:,1]-tris[:,0];e2=tris[:,2]-tris[:,0]
    p=np.cross(np.broadcast_to(direction,e2.shape),e2)
    det=np.einsum('ij,ij->i',e1,p)
    valid=np.abs(det)>1e-12
    inv=np.zeros_like(det);inv[valid]=1/det[valid]
    tv=origin-tris[:,0]
    u=np.einsum('ij,ij->i',tv,p)*inv
    q=np.cross(tv,e1)
    v=q@direction*inv
    d=np.einsum('ij,ij->i',e2,q)*inv
    ids=np.flatnonzero(valid&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(d>eps))
    out=[]
    for i in ids[np.argsort(d[ids])]:
        if not out or abs(float(d[i])-out[-1]['distance_mm'])>1e-6:
            out.append({'distance_mm':float(d[i]), 'face':int(i),
                        'point_mm':(origin+direction*d[i]).tolist()})
    return out

def chord(tris, name, origin, direction):
    hs=ray_all(tris,origin,direction)
    return {'name':name,'origin_mm':origin,'direction':direction,'hits':hs,
            'solid_interval_lengths_mm':[hs[i+1]['distance_mm']-hs[i]['distance_mm']
                                         for i in range(0,len(hs)-1,2)]}

def main():
    started=time.time();data=MODEL.read_bytes();tris=triangles(data)
    norms=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
    norms=norms/np.linalg.norm(norms,axis=1)[:,None]
    centers=tris.mean(axis=1)
    rows=[]
    for i, (center, normal) in enumerate(zip(centers,norms)):
        hits=ray_all(tris,center,-normal,eps=1e-7)
        rows.append({'face':i,'chord_mm':hits[0]['distance_mm'] if hits else None,
                     'exit_face':hits[0]['face'] if hits else None,
                     'centroid_mm':center.tolist(),'inward_direction':(-normal).tolist()})
    finite=[x for x in rows if x['chord_mm'] is not None]
    minimum=min(x['chord_mm'] for x in finite)
    probes=[
        ('mast_x_diameter_z126',[-100,41,126],[1,0,0]),
        ('mast_y_diameter_z126',[14,-100,126],[0,1,0]),
        ('mast_x_diameter_just_above_roof_z81p5',[-100,41,81.5],[1,0,0]),
        ('lower_crossarm_z_at_x24',[24,41,90],[0,0,1]),
        ('lower_crossarm_y_at_x24_z110',[24,30,110],[0,1,0]),
        ('upper_crossarm_z_at_x20',[20,41,112],[0,0,1]),
        ('upper_crossarm_y_at_x20_z121',[20,30,121],[0,1,0]),
        ('right_wing_slab_z_at_x50_y44',[50,44,45],[0,0,1]),
        ('left_wing_slab_z_at_xminus50_y44',[-50,44,45],[0,0,1]),
        ('right_wing_union_root_z_at_x40_y44',[40,44,-1],[0,0,1]),
        ('left_wing_union_root_z_at_xminus40_y44',[-40,44,-1],[0,0,1]),
        ('right_wing_upstand_x_at_z69',[45,44,69],[1,0,0]),
        ('left_wing_upstand_x_at_z69',[-65,44,69],[1,0,0]),
        ('green_roof_lip_z_at_x34p5',[34.5,45,75],[0,0,1]),
        ('entry_bridge_z_at_xminus75',[-75,-4,-1],[0,0,1]),
        ('entry_bridge_root_z_at_xminus51p5',[-51.5,-4,-1],[0,0,1]),
        ('entry_pier_x',[-100,-6,10],[1,0,0]),
        ('entry_pier_y',[-87.6,-30,10],[0,1,0]),
        ('front_groove_lintel_z_at_xminus18p5',[-18.5,-16.7,-1],[0,0,1]),
    ]
    result={'input_sha256':hashlib.sha256(data).hexdigest(),'file_bytes':len(data),
            'method':'Independent direct all-triangle ray intersection; one inward ray from each face centroid; named axis-line intersections of the stored STL.',
            'face_centroid_chords':{'sample_count':len(rows),'finite_count':len(finite),
                'missing_count':len(rows)-len(finite),'minimum_mm':minimum,
                'percentile_1_mm':float(np.percentile([r['chord_mm'] for r in finite],1)),
                'below_1p2mm_face_count':sum(x['chord_mm']<1.2-1e-6 for x in finite),
                'minimum_faces':[r for r in finite if r['chord_mm']<minimum+1e-5]},
            'named_feature_lines':[chord(tris,*p) for p in probes],
            'limits':['Face-centroid rays and the named lines are finite samples, not an exhaustive wall-thickness proof.',
                      'A local short chord at a corner does not by itself establish a structurally thin wall; each feature needs context.',
                      'No slicer, layer extrusion, support generation, load test or physical print is included.',
                      'The 2.8 mm mast and crossarms remain vulnerable to handling and support removal despite their connected positive cross-sections.'],
            'stl_unchanged':MODEL.read_bytes()==data,'runtime_seconds':time.time()-started}
    (ROOT/'independent-thickness-results.json').write_text(json.dumps(result,indent=2),'utf-8')
    with (ROOT/'independent-face-centroid-chords.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['face','chord_mm','exit_face','centroid_x','centroid_y','centroid_z','inward_x','inward_y','inward_z'])
        for r in rows:writer.writerow([r['face'],r['chord_mm'],r['exit_face'],*r['centroid_mm'],*r['inward_direction']])
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
