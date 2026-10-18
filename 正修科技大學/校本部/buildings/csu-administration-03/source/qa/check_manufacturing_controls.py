"""Positive and negative controls for raw-section/normal/support screens."""
from pathlib import Path
import argparse,json
import numpy as np
import trimesh
from check_manufacturing import normal_chords,support
from check_raw_mesh import inspect as raw_inspect
from check_sections import inspect as section_inspect
from qa_common import sha256,write_json,checker_inventory


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise RuntimeError('Fresh controls output required')
    a.out.mkdir(parents=True)
    box=trimesh.creation.box(extents=[4,4,4]);box.apply_translation([0,0,2])
    thin=trimesh.creation.box(extents=[4,.4,4]);thin.apply_translation([0,0,2])
    detached=trimesh.creation.box(extents=[1,1,1]);detached.apply_translation([8,8,1])
    disjoint=trimesh.util.concatenate([box,detached])
    missing=box.copy();missing.update_faces(np.arange(len(missing.faces))!=0)
    flipped=box.copy();flipped.faces=flipped.faces[:,::-1]
    verts=np.array([[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0],[-3,-1,1],[3,-1,1],[3,1,1],[-3,1,1]],float)
    faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    overhang=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    reports=[]
    for name,mesh,expect in [('solid_box',box,{'raw':True,'sections':True,'chords':True,'support':True}),
                              ('thin_0p4_bar',thin,{'raw':True,'sections':False,'chords':False,'support':True}),
                              ('detached_cube',disjoint,{'raw':False}),('missing_face',missing,{'raw':False}),
                              ('reversed_volume',flipped,{'raw':False}),('over_45_frustum',overhang,{'support':False})]:
        out=a.out/name;out.mkdir();stl=out/'specimen.stl';mesh.export(stl)
        row={'case':name,'stl_sha256':sha256(stl),'expected':expect,'actual':{}}
        if 'raw' in expect:
            r=raw_inspect(stl);write_json(out/'raw.json',r);row['actual']['raw']=r['passed']
        if 'sections' in expect:
            d=out/'sections';d.mkdir();r=section_inspect(stl,d);write_json(d/'section-check.json',r);row['actual']['sections']=r['passed']
        if 'chords' in expect:
            d=out/'chords';d.mkdir();r=normal_chords(mesh.triangles,mesh.face_normals,d,.8);write_json(d/'normal.json',r);row['actual']['chords']=r['passed']
        if 'support' in expect:
            d=out/'support';d.mkdir();r=support(mesh.triangles,mesh.face_normals,d,.2,45,.01);write_json(d/'support.json',r);row['actual']['support']=r['passed']
        row['expectations_verified']=row['expected']==row['actual'];reports.append(row)
    result={'passed':all(x['expectations_verified'] for x in reports),'cases':reports,'checker_sources_sha256':checker_inventory()}
    write_json(a.out/'manufacturing-controls.json',result);print(json.dumps(result));return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
