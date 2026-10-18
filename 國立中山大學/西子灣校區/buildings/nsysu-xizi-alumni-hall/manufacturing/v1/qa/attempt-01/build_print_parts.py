"""Split the fixed v4 exterior into three printable floor modules.

No original source or STL is modified. Two 1.6mm foundation plates within each
upper module's existing XY projection remove its large external overhangs.
Run from any directory: python -B source/build_print_parts.py --output-dir PATH
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as md
from importlib.metadata import version

ROOT=Path(__file__).resolve().parents[1]
MODEL_ROOT=ROOT.parents[1]
EXPECTED='05c1714f8b363075a2eb72cde39d21ef06eb0720f1b46336579eb48edbb1444f'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def to_mesh(solid):
    m=solid.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:,:3],faces=np.asarray(m.tri_verts),process=False)

def build(stl,params,out):
    if digest(stl)!=EXPECTED:raise ValueError('This variant requires the frozen v4 STL')
    mesh=trimesh.load_mesh(stl,process=True)
    solid=md.Manifold(md.Mesh(vert_properties=np.asarray(mesh.vertices,dtype=np.float32),tri_verts=np.asarray(mesh.faces,dtype=np.uint32)))
    if solid.status()!=md.Error.NoError:raise ValueError(str(solid.status()))
    cuts=params['cut_heights_original_mm']
    top,low=solid.split_by_plane((0,0,1),cuts[0])
    high,mid=top.split_by_plane((0,0,1),cuts[1])
    chunks=[low,mid,high]
    offsets=[0,*cuts]
    ids=['A-base-and-1F','B-2F-module','C-3F-and-tower']
    pieces=[];report=[]
    for i,(name,chunk,z0) in enumerate(zip(ids,chunks,offsets)):
        before=chunk
        if i:
            # Positive-fill union is the library's documented way to regularize
            # projected contours. It changes no input STL vertices or QA flags.
            projection=chunk.project()
            outline=md.CrossSection(projection.to_polygons(),md.FillRule.Positive)
            floor=outline.extrude(params['upper_module_floor_thickness_mm']).translate((0,0,z0))
            chunk=chunk+floor
        if chunk.status()!=md.Error.NoError:raise ValueError(name+str(chunk.status()))
        piece=to_mesh(chunk.translate((0,0,-z0)))
        path=out/(name+'.stl');path.write_bytes(trimesh.exchange.stl.export_stl(piece))
        exported=trimesh.load_mesh(path,process=True)
        removed=before-chunk;added=chunk-before
        row={'name':name,'file':path.name,'sha256':digest(path),'assembly_translation_mm':[0,0,z0],
             'bounds_mm':exported.bounds.tolist(),'extents_mm':exported.extents.tolist(),
             'vertices':len(exported.vertices),'triangles':len(exported.faces),
             'watertight':bool(exported.is_watertight),'winding_consistent':bool(exported.is_winding_consistent),
             'components':len(exported.split(only_watertight=False)),'volume_mm3':float(exported.volume),
             'removed_original_volume_mm3':removed.volume(),'added_floor_volume_mm3':added.volume(),
             'floor_projection_preserves_original_xy_envelope':True,'orientation':'as supplied, flat z=0 on bed'}
        report.append(row);pieces.append(chunk)
        if not(row['watertight'] and row['winding_consistent'] and row['components']==1 and row['volume_mm3']>0):raise ValueError(row)
    assembled=pieces[0]+pieces[1]+pieces[2]
    removed=solid-assembled;added=assembled-solid
    assembly=to_mesh(assembled)
    path=out/'assembled-reference.stl';path.write_bytes(trimesh.exchange.stl.export_stl(assembly))
    evidence={'input_v4_sha256':digest(stl),'generator_sha256':digest(Path(__file__)),
              'parameters_sha256':digest(ROOT/'parameters.json'),'parts':report,
              'assembled_reference_sha256':digest(path),'assembled_volume_mm3':assembled.volume(),
              'removed_original_volume_mm3':removed.volume(),'added_manufacturing_volume_mm3':added.volume(),
              'added_volume_fraction_of_original':added.volume()/solid.volume(),
              'original_stl_unchanged':digest(stl)==EXPECTED,
              'packages':{n:version(n) for n in ['numpy','trimesh','manifold3d']},
              'no_slicing_or_physical_print_in_this_script':True}
    (out/'build-report.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
    return evidence

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT/'models');a=p.parse_args()
    if a.output_dir.exists() and any(a.output_dir.iterdir()):raise SystemExit('Refusing to overwrite nonempty output directory')
    a.output_dir.mkdir(parents=True,exist_ok=True)
    params=json.loads((ROOT/'parameters.json').read_text(encoding='utf8'))
    print(json.dumps(build(MODEL_ROOT/'models/v4/model.stl',params,a.output_dir)))

if __name__=='__main__':main()
