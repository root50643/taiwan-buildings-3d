"""Split the fixed reference STL into six bed-oriented printable pieces.

Run from the model environment: python -B source/build_split.py
Use --output-dir for an independent deterministic rebuild. No repair, snapping,
simplification, image dependency, or alteration of the reference STL occurs.
"""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
NAMES=['01-base-floor1-upright','02-floor2-slab-inverted',
       '03-floor2-upper-upright','04-floor3-slab-inverted',
       '05-floor3-main-and-tower-upright','06-floor3-diagonal-rail-upright']

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-dir',type=Path,default=ROOT/'models')
    args=ap.parse_args()
    if args.output_dir.exists():raise SystemExit('Refusing overwrite: select a new output directory')
    params_path=ROOT/'parameters.json'
    params=json.loads(params_path.read_text(encoding='utf-8'))
    reference=(ROOT/params['reference_stl']).resolve()
    if digest(reference)!=params['reference_stl_sha256']:
        raise SystemExit('Reference STL SHA-256 differs from the reviewed fixed file')
    mesh=trimesh.load_mesh(reference,process=True)
    args.output_dir.mkdir(parents=True)
    cuts=params['cut_z_assembled_mm']; rows=[]; name_index=0
    for band in range(len(cuts)-1):
        low,top=cuts[band:band+2]
        width=params['cutter_xy_size_mm']
        cutter=trimesh.creation.box([width,width,top-low])
        cutter.apply_translation([0,0,(top+low)/2])
        raw=trimesh.boolean.intersection([mesh,cutter],engine='manifold')
        components=list(raw.split(only_watertight=False))
        components.sort(key=lambda item:-item.volume)
        expected=2 if band==4 else 1
        if len(components)!=expected:
            raise RuntimeError(f'band {band}: expected {expected} components, got {len(components)}')
        transform=np.eye(4)
        if band in params['inverted_bands_zero_based']:
            transform=np.diag([1.,-1.,-1.,1.]);transform[2,3]=top
        else:transform[2,3]=-low
        inverse=np.linalg.inv(transform)
        for component in components:
            name=NAMES[name_index];name_index+=1
            assembled_bounds=component.bounds.tolist()
            oriented=component.copy();oriented.apply_transform(transform)
            file=args.output_dir/(name+'.stl')
            file.write_bytes(trimesh.exchange.stl.export_stl(oriented))
            check=trimesh.load_mesh(file,process=True)
            nondegenerate=bool(np.all(check.area_faces>0))
            row={'id':name,'stl':file.name,'stl_sha256':digest(file),
                'stl_bytes':file.stat().st_size,'horizontal_band':band,
                'assembled_band_z_mm':[low,top], 'assembled_bounds_mm':assembled_bounds,
                'print_bounds_mm':check.bounds.tolist(),
                'transform_assembled_to_print':transform.tolist(),
                'transform_print_to_assembled':inverse.tolist(),
                'watertight':bool(check.is_watertight),
                'winding_consistent':bool(check.is_winding_consistent),
                'edge_connected_components':len(check.split(only_watertight=False)),
                'positive_volume_mm3':float(check.volume),
                'nondegenerate_triangles':nondegenerate,
                'vertices':len(check.vertices),'triangles':len(check.faces),
                'repair_after_export':'none; process=True welds exactly coincident STL coordinates only'}
            rows.append(row)
            if not(row['watertight'] and row['winding_consistent'] and
                   row['edge_connected_components']==1 and nondegenerate and row['positive_volume_mm3']>0):
                raise RuntimeError(f'Failed basic mesh assertions for {name}')
    report={'reference_stl':params['reference_stl'],'reference_stl_sha256':digest(reference),
        'parameters_sha256':digest(params_path),'generator_sha256':digest(Path(__file__)),
        'physical_part_count':len(rows),'horizontal_band_count':len(cuts)-1,
        'reference_volume_mm3':float(mesh.volume),
        'parts_volume_sum_mm3':sum(r['positive_volume_mm3'] for r in rows),
        'volume_difference_mm3':sum(r['positive_volume_mm3'] for r in rows)-float(mesh.volume),
        'reference_bounds_mm':mesh.bounds.tolist(),'parts':rows,
        'python':platform.python_version(),
        'packages':{n:version(n) for n in ['numpy','trimesh','manifold3d','shapely']},
        'claims':'Closed, oriented split geometry only; slicer and physical performance require separate evidence.'}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
