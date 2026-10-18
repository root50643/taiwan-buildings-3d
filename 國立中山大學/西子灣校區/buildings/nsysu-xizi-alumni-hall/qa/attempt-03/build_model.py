"""Original low-detail NSYSU Xizi exterior. Millimetres, independent display scale.

Run python -B source/build_model.py --output-dir PATH. No source images needed.
Polygon coordinates trace the official 1800px PDF pages, with declared page
translations and hand simplification. Exterior heights are photograph estimates.
"""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]

def box(extents, center):
    m=trimesh.creation.box(extents)
    m.apply_translation(center)
    return m

def extrude(poly, bottom, top):
    m=trimesh.creation.extrude_polygon(poly,top-bottom,engine='manifold')
    m.apply_translation([0,0,bottom])
    return m

def build(p):
    m=p['model_mm']; outlines=p['outlines_px']; margin=m['base_margin']
    allp=np.array([v for a in outlines.values() for v in a],float)
    span=np.ptp(allp,axis=0)
    scale=(m['base_longest']-2*margin)/max(span)
    center=(allp.max(axis=0)+allp.min(axis=0))/2
    def xy(coords):
        v=(np.asarray(coords,float)-center)*scale
        v[:,1]*=-1
        return v
    polys={k:Polygon(xy(v)) for k,v in outlines.items()}
    for k,v in polys.items():
        if not v.is_valid: raise ValueError('Invalid traced outline '+k)
    b=m['base_thickness']; h=m['floor_height_estimated']; slab=m['slab_thickness']
    base=box([span[0]*scale+2*margin,span[1]*scale+2*margin,b],[0,0,b/2])
    parts=[base]
    for i in range(1,4):
        parts.append(extrude(polys[f'floor{i}_rooms'],b+(i-1)*h-0.15,b+i*h))
    # Balcony slabs and open-top thickened guard upstands. They are NOT rooms.
    for floor in [2,3]:
        z=b+(floor-1)*h
        for name in [f'terrace{floor}_rectangle',f'terrace{floor}_diagonal']:
            poly=polys[name]
            parts.append(extrude(poly,z-slab,z))
            rail=LineString(xy(p['open_rail_paths_px'][name])).buffer(m['parapet_thickness']/2,cap_style=2,join_style=2)
            parts.append(extrude(rail,z-0.15,z+m['parapet_height']))
    # Only photo-supported broad support rhythm; positions approximate.
    for coord in p['columns_px']:
        x,y=xy([coord])[0]
        parts.append(box([m['column_width'],m['column_width'],h+0.1],[x,y,b+h/2-0.05]))
    # The glass corner is a solid printable volume, taller than the main roof.
    tower=polys['tower']
    parts.append(extrude(tower,b-0.15,b+m['tower_height_above_base_estimated']))
    for i in [3]:
        roof=polys[f'floor{i}_rooms']
        rim=roof.difference(roof.buffer(-m['parapet_thickness'],join_style=2))
        parts.append(extrude(rim,b+i*h-0.15,b+i*h+m['roof_parapet_height']))
    solid=trimesh.boolean.union(parts,engine='manifold')
    # Recesses on the documented terrace/street sides only. Unknown rear is plain.
    # Bevel the TOP inward edge 45 degrees to reduce unsupported recess ceilings.
    cutters=[]
    def recess(a,c,z,width,height,depth):
        a,c=np.array(a,float),np.array(c,float)
        u=(c-a)/np.linalg.norm(c-a); n=np.array([-u[1],u[0]])
        mid=(a+c)/2
        # Caller endpoints orient n into the building. Local y=0 at facade.
        # Carry the 45-degree bevel past the facade rather than terminating a
        # cutter vertex exactly on it. Attempt02's coplanar endpoint produced
        # micron-size triangles which collapsed in binary32 STL export.
        yz=[(-1,z),(depth,z),(depth,z+height-depth),(-1,z+height+1)]
        verts=np.array([[*(mid+u*x+n*y),zz] for x in [-width/2,width/2] for y,zz in yz])
        N=len(yz); faces=[]
        for k in range(1,N-1): faces.extend([[0,k+1,k],[N,N+k,N+k+1]])
        for k in range(N):
            j=(k+1)%N;faces.extend([[k,j,N+j],[k,N+j,N+k]])
        cut=trimesh.Trimesh(verts,faces,process=True);cut.fix_normals()
        if cut.volume<0:cut.invert()
        cutters.append(cut)
    # Three broad repetitive bays on front (positive image y) and terrace facade.
    for level in range(3):
        for xp in [365,470,575,680,780]:
            py=[1006,990,1001][level]
            a,c=xy([[xp-20,py],[xp+20,py]])
            recess(a,c,b+level*h+2.3,m['window_width'],m['window_height'],m['recess_depth'])
        for xp in [365,480,595,710]:
            py=[650,650,695][level]
            a,c=xy([[xp+20,py],[xp-20,py]])
            recess(a,c,b+level*h+2.3,m['window_width'],m['window_height'],m['recess_depth'])
    # Glass-tower pane relief on every exposed side; attached solid, no thin glass.
    coords=xy(outlines['tower'])
    cc=coords.mean(axis=0)
    for a,c in zip(coords,np.roll(coords,-1,axis=0)):
        if (c-a)[0]*(cc-a)[1]-(c-a)[1]*(cc-a)[0]<0: a,c=c,a
        # At lower levels several tower facets merge into the occupied wings.
        # Cutting those hidden facets made sealed interior cavities in attempt01.
        # Retain pane relief only above the main roof, where all facets are exposed.
        recess(a,c,b+3*h+1.8,5.0,5.4,m['recess_depth'])
    model=trimesh.boolean.difference([solid]+cutters,engine='manifold')
    model.remove_unreferenced_vertices()
    context={'pixel_scale_mm_per_pixel':scale,'canonical_center_px':center.tolist(), 'feature_minimum_design_mm':{'rail_xy':m['parapet_thickness'],'slab_z':slab,'column_xy':m['column_width'],'recess_depth':m['recess_depth']},'terraces':'open at top; balcony overhangs and bridge spans require slicer support review', 'floor_levels_mm':[b,b+h,b+2*h,b+3*h], 'print_orientation':'+Z up, plinth bottom z=0 on bed'}
    return model, context

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'models/v1');args=ap.parse_args()
    if (args.output_dir/'model.stl').exists():raise SystemExit('Refusing overwrite: use another output directory')
    param=ROOT/'parameters.json';p=json.loads(param.read_text(encoding='utf-8'))
    model,context=build(p);args.output_dir.mkdir(parents=True,exist_ok=True)
    stl=args.output_dir/'model.stl';stl.write_bytes(trimesh.exchange.stl.export_stl(model))
    mesh=trimesh.load_mesh(stl,process=True)
    report={'stl_sha256':hashlib.sha256(stl.read_bytes()).hexdigest(),'parameters_sha256':hashlib.sha256(param.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'triangles':len(mesh.faces),'bounds_mm':mesh.bounds.tolist(),'extents_mm':mesh.extents.tolist(),'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'positive_volume_mm3':float(mesh.volume),'components':len(mesh.split(only_watertight=False)),'python':platform.python_version(),'packages':{n:version(n) for n in ['numpy','trimesh','manifold3d','shapely']},'repair_after_export':'none; process=True welds identical STL vertices','geometry_context':context}
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
    if not(report['watertight'] and report['winding_consistent'] and report['components']==1 and report['positive_volume_mm3']>0):raise SystemExit(1)

if __name__=='__main__':main()
