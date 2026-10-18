"""Original low-detail Chengqin exterior. Millimetres; no metric building scale.

Uses the repository's trimesh/manifold workflow (wfu-apollo), with original
curved-link geometry and photo/plan-constrained parameters. No source images
are required to rebuild. Run: python -B source/build_model.py --output-dir PATH
"""
import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import platform

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]


def box(extents, center):
    m = trimesh.creation.box(extents)
    m.apply_translation(center)
    return m


def prism_x(x0, x1, yz):
    n = len(yz)
    vertices = [[x, y, z] for x in (x0, x1) for y, z in yz]
    faces = []
    for k in range(1, n-1):
        faces.extend([[0, k+1, k], [n, n+k, n+k+1]])
    for k in range(n):
        j = (k+1) % n
        faces.extend([[k, j, n+j], [k, n+j, n+k]])
    m = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    m.fix_normals()
    return m


def cubic(a, b, c, d, count):
    a, b, c, d = map(np.asarray, [a,b,c,d])
    return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
            for t in np.linspace(0,1,count+1)]


def connector_outline(params, inset=0):
    c = params['connector']
    count = c['curve_segments']//2
    # Official 4F diagram: a diagonal upper edge and a rounded lower/outer edge.
    # Endpoint A->B is the explicit flat model cut toward the omitted Yuanzhi.
    a, b = np.array(c['cut_endpoint_a_mm']), np.array(c['cut_endpoint_b_mm'])
    chain = cubic([79.6,14.4],[88.5,14.7],[88.7,9],[88.5,-3],count)
    chain += cubic([88.5,-3],[88.6,-18],[91,-22],[*b],count)[1:]
    if inset:
        chain = [p-np.array([inset,0]) for p in chain]
        # Keep the far band endpoint on the same explicit cut plane.
        chain[-1] = b+(a-b)*(inset/10)
    return np.asarray([[79.6,-23.0],a,*reversed(chain)],dtype=float)


def connector_mesh(params):
    m,c = params['model_mm'],params['connector']
    bottom=m['base_z']-0.2
    height=m['body_height_above_base']*c['height_fraction_of_main']
    pitch=height/c['visible_band_count']
    full=connector_outline(params)
    inset=connector_outline(params,c['band_recess_depth'])
    rings=[(bottom,full)]
    # Ten broad horizontal window-band recesses are a photo-based simplification,
    # not a claim that the partially obscured photograph proves ten floors.
    # Unchanged inner edges remain closed; no added open balconies or railings.
    for k in range(c['visible_band_count']):
        z=m['base_z']+k*pitch+3.0
        rings += [(z,full),(z,inset),
                  (z+c['band_height']-c['band_top_chamfer'],inset),
                  (z+c['band_height'],full)]
    rings.append((m['base_z']+height,full))
    n=len(full)
    vertices=np.array([[x,y,z] for z,poly in rings for x,y in poly])
    # triangulate_polygon supports this simple concave diagram outline.
    from shapely.geometry import Polygon
    # The manifold triangulator preserves input order for a simple ring.
    cap_vertices,cap_faces=trimesh.creation.triangulate_polygon(Polygon(full),engine='manifold')
    index={tuple(np.round(p,9)):i for i,p in enumerate(full)}
    mapped=np.array([[index[tuple(np.round(cap_vertices[v],9))] for v in f] for f in cap_faces])
    faces=[list(f[::-1]) for f in mapped]
    faces += [list(f+(len(rings)-1)*n) for f in mapped]
    for r in range(len(rings)-1):
        for k in range(n):
            j=(k+1)%n
            faces += [[r*n+k,r*n+j,(r+1)*n+j],
                      [r*n+k,(r+1)*n+j,(r+1)*n+k]]
    faces=np.asarray(faces)
    tri=vertices[faces]
    areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces[areas>1e-9],process=True)
    mesh.fix_normals()
    if mesh.volume<0:
        mesh.invert()
    if not mesh.is_watertight:
        raise ValueError('Connector ring construction is not watertight')
    return mesh


def build(params):
    m=params['model_mm']
    l,d=m['main_length'],m['slab_depth']
    z,h=m['base_z'],m['body_height_above_base']
    # A printing plinth is visibly distinct from the building and asserts no
    # exposed basement podium. Fit one rectangular print base around both parts.
    outline=connector_outline(params)
    xymin=np.minimum([-l/2,-m['core_depth']/2],outline.min(axis=0))-m['base_margin']
    xymax=np.maximum([l/2,m['core_depth']/2],outline.max(axis=0))+m['base_margin']
    base=box([*(xymax-xymin),z],[*((xymax+xymin)/2),z/2])
    parts=[base,box([l,d,h],[0,0,z+h/2]),connector_mesh(params)]
    for sign in [-1,1]:
        x=sign*(l-m['core_length'])/2
        parts.append(box([m['core_length'],m['core_depth'],h],[x,0,z+h/2]))
        parts.append(box([m['roof_box_length'],m['roof_box_depth'],m['roof_box_height']+0.2],
                         [x,0,z+h+(m['roof_box_height']-0.2)/2]))
    solid=trimesh.boolean.union(parts,engine='manifold')
    cutters=[]
    front=-d/2
    pitch=h/12
    bay=(l-2*m['core_length'])/8
    for level in range(12):
        bottom=z+2.8+pitch*level
        top=bottom+m['window_height']
        depth=m['front_recess_depth']
        for k in range(8):
            x=-l/2+m['core_length']+bay*(k+0.5)
            yz=[(front-2,bottom),(front+depth,bottom),
                (front+depth,top-depth),(front,top),(front-2,top)]
            cutters.append(prism_x(x-m['window_width']/2,x+m['window_width']/2,yz))
    model=trimesh.boolean.difference([solid]+cutters,engine='manifold')
    model.remove_unreferenced_vertices()
    return model


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output-dir',type=Path,default=ROOT/'models/v1')
    args=p.parse_args()
    if (args.output_dir/'model.stl').exists():
        raise SystemExit('Refusing to overwrite model.stl; choose a new output directory')
    params=json.loads((ROOT/'parameters.json').read_text(encoding='utf8'))
    mesh=build(params)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    stl=args.output_dir/'model.stl'
    stl.write_bytes(trimesh.exchange.stl.export_stl(mesh))
    exported=trimesh.load_mesh(stl,process=True)
    report={'stl_sha256':hashlib.sha256(stl.read_bytes()).hexdigest(),
        'parameters_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'vertices':len(exported.vertices),'triangles':len(exported.faces),
        'bounds_mm':exported.bounds.tolist(),'extents_mm':exported.extents.tolist(),
        'watertight':bool(exported.is_watertight),'winding_consistent':bool(exported.is_winding_consistent),
        'positive_volume_mm3':float(exported.volume),'components':len(exported.split(only_watertight=False)),
        'python':platform.python_version(),'packages':{n:version(n) for n in ['numpy','trimesh','manifold3d']},
        'repair_after_export':'none; process=True welds identical STL triangle vertices'}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))
    if not(report['watertight'] and report['winding_consistent'] and report['components']==1 and report['positive_volume_mm3']>0):
        raise SystemExit(1)


if __name__=='__main__':
    main()
