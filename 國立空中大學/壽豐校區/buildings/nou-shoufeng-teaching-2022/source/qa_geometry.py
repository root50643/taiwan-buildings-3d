"""Independent checks of exported STL files, not the in-memory generator meshes.

Run after build_model.py. Writes qa/geometry-report.json and qa/sections.png.
Requires numpy, trimesh/manifold3d, shapely, matplotlib. Coordinates are millimetres.
This is numerical manufacturing evidence, not a physical print or fit test.
"""
from pathlib import Path
from itertools import combinations
import json, hashlib, datetime, math
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon, GeometryCollection, LineString
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPolygon

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'
QA.mkdir(exist_ok=True)
TOL = 1e-4
VOLUME_TOL = 1e-3
LAYER = .2

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def polygons(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [p for q in getattr(g, 'geoms', []) for p in polygons(q)]

def section(mesh, axis, value):
    """XOR closed section loops in world coordinates; preserves holes."""
    normal = np.eye(3)[axis]
    origin = normal * value
    path = mesh.section(plane_origin=origin, plane_normal=normal)
    dims = [i for i in range(3) if i != axis]
    shape = GeometryCollection()
    if path is not None:
        for loop in path.discrete:
            if len(loop) >= 4 and np.linalg.norm(loop[0] - loop[-1]) < TOL:
                p = Polygon(loop[:, dims])
                if not p.is_valid:
                    p = p.buffer(0)
                shape = shape.symmetric_difference(p)
    return shape

def planar_faces(mesh, axis, value, normal_sign):
    """Union of actual STL triangles in a specified contact plane."""
    dims = [i for i in range(3) if i != axis]
    tri = mesh.triangles
    mask = ((np.abs(tri[:, :, axis] - value).max(axis=1) < TOL)
            & (mesh.face_normals[:, axis] * normal_sign > .999))
    return unary_union([Polygon(t[:, dims]) for t in tri[mask]])

def shared_face(a, b, axis, value, sign_a):
    fa = planar_faces(a, axis, value, sign_a)
    fb = planar_faces(b, axis, value, -sign_a)
    return float(fa.intersection(fb).area), float(fa.area), float(fb.area)

def draw_geom(ax, shape, color, alpha=1):
    for p in polygons(shape):
        ax.add_patch(PlotPolygon(np.asarray(p.exterior.coords), facecolor=color,
                                edgecolor=color, alpha=alpha, linewidth=.4))
        for hole in p.interiors:
            ax.add_patch(PlotPolygon(np.asarray(hole.coords), facecolor='white',
                                    edgecolor=color, linewidth=.4))

def slice_print(mesh):
    z0, z1 = mesh.bounds[:, 2]
    rows = []
    prev = None
    detached = []
    significant = []
    # Mid-layer planes avoid coplanar face ambiguity. All nominal 0.2 mm layers.
    for n, z in enumerate(np.arange(z0 + LAYER / 2, z1, LAYER)):
        shape = section(mesh, 2, float(z))
        pieces = polygons(shape)
        isolated = []
        overhang_area = 0.
        max_extension_sample = 0.
        if prev is not None:
            for k, p in enumerate(pieces):
                if p.intersection(prev.buffer(TOL)).area < 1e-6:
                    isolated.append(k)
            unsupported = shape.difference(prev.buffer(LAYER, join_style=2))
            overhang_area = float(unsupported.area)
            if overhang_area > .001:
                for p in polygons(unsupported):
                    coords = list(p.exterior.coords)
                    pts = coords + [p.representative_point().coords[0]]
                    # Include edge interiors: corners alone miss the centre of a recess lip.
                    for start, end in zip(coords[:-1], coords[1:]):
                        a, b = np.asarray(start), np.asarray(end)
                        for t in np.linspace(0,1,max(2,math.ceil(np.linalg.norm(b-a)/.25)+1)):
                            pts.append(tuple(a+(b-a)*t))
                    for x, y in pts:
                        from shapely.geometry import Point
                        max_extension_sample = max(max_extension_sample,
                                                   Point(x, y).distance(prev))
                significant.append({'layer_index_0': n, 'mid_z_mm': float(z),
                    'area_beyond_45deg_envelope_mm2': overhang_area,
                    'sampled_max_extension_from_previous_slice_mm': max_extension_sample})
        if isolated:
            detached.append({'layer_index_0': n, 'mid_z_mm': float(z),
                             'section_component_indices': isolated})
        rows.append({'layer_index_0': n, 'mid_z_mm': float(z),
                     'area_mm2': float(shape.area), 'section_components': len(pieces),
                     'detached_from_previous_layer': len(isolated)})
        prev = shape
    return {'layer_height_mm': LAYER, 'plane_convention': 'mid-layer; z=0.1,0.3,...',
            'layers_checked': len(rows), 'minimum_z_mm': float(z0),
            'first_slice_bed_area_mm2': rows[0]['area_mm2'],
            'first_slice_components': rows[0]['section_components'],
            'detached_islands': detached, 'overhang_events': significant, 'layers': rows}

def main():
    params = json.loads((ROOT / 'parameters.json').read_text(encoding='utf8'))
    report = {'schema': 'exported-stl-independent-qa-v1',
        'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'units': 'mm', 'mesh_loader': 'trimesh.load(force=mesh, default processing)',
        'parameters_sha256': sha(ROOT / 'parameters.json'),
        'generator_sha256': sha(ROOT / 'source' / 'build_model.py'),
        'numeric_tolerances': {'linear_mm': TOL, 'collision_volume_mm3': VOLUME_TOL},
        'parts': [], 'assembly_pairwise_36': [], 'planar_glue_interfaces': [],
        'arch_side_contacts': [], 'targeted_thickness_probes': [], 'corridor_probes': [],
        'split_part_corridor_top_access': [],
        'limitations': [
            'No physical print, support removal, glue strength, or trial assembly performed.',
            'Thickness results are explicit selected section probes, not exhaustive minimum local thickness or stress analysis.',
            'Mid-layer island and 45 degree envelope checks are numerical geometry screening, not a replacement for the actual slicer.',
            'No machine, material, shrinkage, extrusion calibration, bed adhesion, or dimensional fit is certified.',
            'Glue interfaces have zero nominal design clearance; physical fit and flatness need test coupons / trial assembly.',
            'The large assembly-reference STL is for viewing and is not an approved one-piece print.',
            'Small blind recess ledges exceed a 45 degree envelope. Their shallow spans are recorded; actual bridging quality needs a print test.',
            'Open access is checked at sampled corridor lines and derived from separable ceiling pieces; no support generation/removal was physically tested.'
        ]}
    prints, assembled = [], []
    for p in params['parts']:
        path = ROOT / 'models' / p['stl']
        mesh = tm.load(path, force='mesh')
        am = mesh.copy()
        transform = np.asarray(p['assembly_transform_mm'])
        am.apply_transform(transform)
        prints.append(mesh)
        assembled.append(am)
        counts = np.bincount(mesh.edges_unique_inverse)
        row = {'stl': p['stl'], 'sha256': sha(path), 'sha_matches_manifest': sha(path) == p['sha256'],
            'faces': len(mesh.faces), 'vertices': len(mesh.vertices),
            'watertight': bool(mesh.is_watertight), 'winding_consistent': bool(mesh.is_winding_consistent),
            'positive_volume': bool(mesh.volume > 0), 'is_volume': bool(mesh.is_volume),
            'body_count': int(mesh.body_count), 'volume_mm3': float(mesh.volume),
            'euler_characteristic': int(mesh.euler_number),
            'non_two_manifold_edges': int((counts != 2).sum()),
            'degenerate_faces_area_below_1e-10': int((mesh.area_faces < 1e-10).sum()),
            'print_bounds_mm': mesh.bounds.tolist(), 'assembly_bounds_mm': am.bounds.tolist(),
            'print_bounds_match_manifest': bool(np.allclose(mesh.bounds, p['print_bounds_mm'], atol=TOL)),
            'assembly_bounds_match_manifest': bool(np.allclose(am.bounds, p['assembly_bounds_mm'], atol=TOL)),
            'assembly_rotation_determinant': float(np.linalg.det(transform[:3, :3])),
            'print_layer_screening': slice_print(mesh)}
        report['parts'].append(row)
        print('mesh/slices', p['stl'], flush=True)
    # Every pair, including disjoint pairs, is evaluated and explicitly recorded.
    for i, j in combinations(range(9), 2):
        a, b = assembled[i], assembled[j]
        overlap_extent = np.minimum(a.bounds[1], b.bounds[1]) - np.maximum(a.bounds[0], b.bounds[0])
        row = {'part_a': params['parts'][i]['stl'], 'part_b': params['parts'][j]['stl'],
               'aabb_overlap_extent_mm': overlap_extent.tolist()}
        if np.any(overlap_extent < -TOL):
            row.update(method='AABB separation proves no intersection', intersection_volume_mm3=0.)
        else:
            inter = tm.boolean.intersection([a, b], engine='manifold', check_volume=True)
            row.update(method='manifold exact mesh Boolean intersection',
                       intersection_volume_mm3=float(abs(inter.volume)) if len(inter.faces) else 0.)
        row['positive_volume_collision'] = row['intersection_volume_mm3'] > VOLUME_TOL
        report['assembly_pairwise_36'].append(row)
    for i in range(8):
        # Adjacent print part indices always meet at their nominal horizontal glue plane.
        z = float(assembled[i].bounds[1, 2])
        area, aa, ab = shared_face(assembled[i], assembled[i+1], 2, z, +1)
        report['planar_glue_interfaces'].append({'part_a': params['parts'][i]['stl'],
            'part_b': params['parts'][i+1]['stl'], 'z_mm': z,
            'shared_planar_face_area_mm2': area,
            'a_upward_face_area_mm2': aa, 'b_downward_face_area_mm2': ab,
            'positive_area_contact': area > 1.,
            'access': 'Exposed mating faces when pieces are separate; no locating pins or enclosed sockets. Apply glue before stacking.'})
    for floor in range(4):
        lo, cap = assembled[2*floor], assembled[2*floor+1]
        for axis, val, sign, label in [(0,138.8,+1,'long wing left arch end'),
                (0,149.2,-1,'long wing right arch end'),
                (1,114.8,+1,'short wing first arch end'),
                (1,124.4,-1,'short wing terminal arch end')]:
            area, _, _ = shared_face(lo, cap, axis, val, sign)
            report['arch_side_contacts'].append({'floor':floor+1, 'probe':label,
                'contact_plane_axis':'xyz'[axis], 'coordinate_mm':val,
                'shared_vertical_contact_area_mm2':area, 'positive_area_contact':area > .01,
                'note':'Nominal exact-touch side contact; arch is also integral with its ceiling slab.'})
    # Length of actual mesh-section intersection at explicitly stated positions.
    specs = [('upper-floor grooved railing core',2,2,3.,[(32.2,28.),(32.2,31.)],1.2),
        ('column across x',2,2,5.,[(40.,29.2),(44.,29.2)],1.6),
        ('column across y',2,2,5.,[(42.,27.5),(42.,31.)],1.6),
        ('terminal outer sidewall',2,2,5.,[(153.,25.),(157.,25.)],1.6),
        ('inverted ceiling slab',1,0,60.,[(25.,-.1),(25.,1.5)],1.2),
        ('upper floor slab in corridor',2,0,60.,[(25.,-.1),(25.,2.)],1.6),
        ('roof slab away from headhouses',8,0,60.,[(10.,-.1),(10.,1.5)],1.2),
        ('roof exterior parapet',8,2,2.,[(60.,-1.),(60.,2.)],1.2),
        ('roof court parapet',8,2,2.,[(60.,28.),(60.,31.)],1.2)]
    for label, idx, axis, val, line, expected in specs:
        measured = float(section(prints[idx],axis,val).intersection(LineString(line)).length)
        report['targeted_thickness_probes'].append({'feature':label, 'part':params['parts'][idx]['stl'],
            'section_axis':'xyz'[axis], 'section_coordinate_mm':val, 'line_in_other_two_axes_mm':line,
            'measured_solid_length_mm':measured, 'expected_minimum_mm':expected,
            'passes_with_linear_tolerance':measured >= expected - TOL})
    # Corridor and side access lines use actual assembled sections at a bay without a column.
    for floor in range(4):
        base=2+10*floor
        for axis, val, line, label in [(0,60.,[(22.1,base+6.),(35.,base+6.)],'long wing outward access'),
                (1,60.,[(22.1,base+6.),(35.,base+6.)],'short wing outward access')]:
            solid = unary_union([section(m,axis,val) for m in assembled])
            obstruction=float(solid.intersection(LineString(line)).length)
            report['corridor_probes'].append({'floor':floor+1,'probe':label,
                'section_axis':'xyz'[axis], 'section_coordinate_mm':val,
                'line_in_other_two_axes_mm':line,'obstructed_length_mm':obstruction,
                'clear':obstruction<TOL})
    # A vertical tool/support access prism above each lower part's corridor floor.
    # It excludes the facade columns and terminal sidewalls with a 0.1 mm margin.
    # Exact volume clipping checks the entire prism, not just the plotted sections.
    for floor in range(4):
        idx = floor*2
        bottom = 3.7 if floor==0 else 1.7
        top = float(prints[idx].bounds[1,2]+1.)
        probe_boxes = [(30.,154.3,22.1,28.3,bottom,top),
                       (22.1,28.3,30.,124.3,bottom,top)]
        for wing, bounds in zip(['long','short'],probe_boxes):
            x0,x1,y0,y1,z0,z1 = bounds
            prism = tm.creation.box([x1-x0,y1-y0,z1-z0])
            prism.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2])
            overlap = tm.boolean.intersection([prints[idx],prism],engine='manifold',check_volume=True)
            vol = float(abs(overlap.volume)) if len(overlap.faces) else 0.
            report['split_part_corridor_top_access'].append({'floor':floor+1,'wing':wing,
                'part':params['parts'][idx]['stl'],'probe_prism_bounds_mm':[[x0,y0,z0],[x1,y1,z1]],
                'intersecting_solid_volume_mm3':vol,'clear_to_above_part':vol<VOLUME_TOL,
                'interpretation':'6.2 mm clear vertical corridor strip is open upward before the separate ceiling is attached; does not certify tool clearance at every decorated edge.'})
    refpath=ROOT/'models'/'assembly-reference-do-not-print.stl'
    ref=tm.load(refpath,force='mesh')
    report['assembly_reference']={'sha256':sha(refpath), 'manifest_sha_matches':sha(refpath)==params['reference_stl_sha256'],
        'bounds_mm':ref.bounds.tolist(),'extents_mm':ref.extents.tolist(),
        'watertight':bool(ref.is_watertight),'winding_consistent':bool(ref.is_winding_consistent),
        'is_volume':bool(ref.is_volume),'body_count':int(ref.body_count),'volume_mm3':float(ref.volume)}
    report['summary']={'nine_print_parts_pass_volume_checks':all(p['is_volume'] and p['body_count']==1 for p in report['parts']),
        'pair_count':len(report['assembly_pairwise_36']),
        'positive_volume_collision_count':sum(r['positive_volume_collision'] for r in report['assembly_pairwise_36']),
        'all_eight_planar_glue_interfaces_have_positive_area':all(r['positive_area_contact'] for r in report['planar_glue_interfaces']),
        'all_sixteen_arch_side_contacts_have_positive_area':all(r['positive_area_contact'] for r in report['arch_side_contacts']),
        'all_selected_thickness_probes_pass':all(r['passes_with_linear_tolerance'] for r in report['targeted_thickness_probes']),
        'all_eight_corridor_access_lines_clear':all(r['clear'] for r in report['corridor_probes']),
        'all_eight_split_corridor_top_access_prisms_clear':all(r['clear_to_above_part'] for r in report['split_part_corridor_top_access']),
        'detached_print_slice_island_count':sum(len(p['print_layer_screening']['detached_islands']) for p in report['parts'])}
    report['final_input_binding']={
        'parameters_unchanged_during_run':sha(ROOT/'parameters.json')==report['parameters_sha256'],
        'generator_unchanged_during_run':sha(ROOT/'source'/'build_model.py')==report['generator_sha256'],
        'every_print_stl_unchanged_during_run':all(sha(ROOT/'models'/p['stl'])==p['sha256'] for p in report['parts']),
        'reference_stl_unchanged_during_run':sha(refpath)==report['assembly_reference']['sha256'],
        'all_print_stls_matched_start_manifest':all(p['sha_matches_manifest'] for p in report['parts'])}
    report['summary']['inputs_stable_and_bound_to_manifest']=all(report['final_input_binding'].values())
    (QA/'geometry-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    fig,axs=plt.subplots(2,3,figsize=(15,9),layout='constrained')
    colors=['#d4b36e','#657ca1','#ead397','#7f94b3','#ead397','#7f94b3','#ead397','#7f94b3','#a6b7a0']
    for m,c in zip(assembled,colors): draw_geom(axs[0,0],section(m,2,17.),c)
    axs[0,0].set(title='Assembly plan: z = 17 mm',xlabel='x (mm)',ylabel='y (mm)',xlim=(-3,160),ylim=(-3,130))
    for m,c in zip(assembled,colors): draw_geom(axs[0,1],section(m,0,60.),c)
    axs[0,1].set(title='Open corridor section: x = 60 mm',xlabel='y (mm)',ylabel='z (mm)',xlim=(18,35),ylim=(0,49))
    for m,c in zip(assembled,colors): draw_geom(axs[0,2],section(m,1,29.2),c)
    axs[0,2].set(title='Arcade / arch section: y = 29.2 mm',xlabel='x (mm)',ylabel='z (mm)',xlim=(132,157),ylim=(0,44))
    draw_geom(axs[1,0],section(prints[2],0,60.),colors[2])
    axs[1,0].set(title='Lower part as printed: x = 60 mm',xlabel='y (mm)',ylabel='z (mm)',xlim=(18,32),ylim=(-.2,10))
    draw_geom(axs[1,1],section(prints[1],1,.8),colors[1])
    axs[1,1].set(title='Inverted cap as printed: y = 0.8 mm',xlabel='x (mm)',ylabel='z (mm)',xlim=(132,157),ylim=(-.2,4))
    draw_geom(axs[1,2],section(prints[2],2,3.),colors[2])
    axs[1,2].set(title='Grooved rail section: z = 3 mm',xlabel='x (mm)',ylabel='y (mm)',xlim=(31,40),ylim=(27.5,31))
    for ax in axs.flat:
        ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.2)
    fig.suptitle('Exported STL cross sections | mm | colors identify separate print parts',fontsize=14)
    fig.savefig(QA/'sections.png',dpi=170)
    plt.close(fig)
    print(json.dumps(report['summary'],indent=2),flush=True)
    print('REPORT',QA/'geometry-report.json',flush=True)

if __name__ == '__main__':
    main()
