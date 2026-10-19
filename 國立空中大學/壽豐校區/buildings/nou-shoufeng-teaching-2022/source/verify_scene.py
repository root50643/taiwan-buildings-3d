"""Read-only independent saved Blender/STL verification; never saves the .blend.

After installing requirements.txt in a supported Python environment, run from the
package root: python source/verify_scene.py. This Windows task's helper is only an
external runner, not a package dependency. Binary STL parsing is independent
of the trimesh import path used by build_scene.py. Coordinates are checked in
physical mm, including the scene's metres-per-BU scale, and triangle membership
is compared without relying on vertex or triangle ordering.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import struct
import numpy as np
import bpy
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
TOL_MM = 1e-4


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_stl(path):
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError(f"Not a binary STL: {path.name}")
    count = struct.unpack_from('<I', raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"Binary STL size/count mismatch: {path.name}")
    dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attr', '<u2')])
    return np.frombuffer(raw, dtype=dtype, count=count, offset=84)['vertices'].astype(np.float64)


def transformed(triangles, matrix):
    flat = triangles.reshape(-1, 3)
    return (flat @ matrix[:3, :3].T + matrix[:3, 3]).reshape(-1, 3, 3)


def bounds(points):
    points = points.reshape(-1, 3)
    return np.stack((points.min(axis=0), points.max(axis=0)))


def canonical_faces(faces):
    faces = np.sort(faces, axis=1)
    return faces[np.lexsort((faces[:, 2], faces[:, 1], faces[:, 0]))]


def coordinate_mesh_sha256(triangles):
    """Ordering-independent mesh digest on a 0.0001 mm coordinate grid."""
    quantized = np.rint(triangles / TOL_MM).astype('<i8')
    canonical = []
    for tri in quantized:
        canonical.append(tri[np.lexsort((tri[:, 2], tri[:, 1], tri[:, 0]))].reshape(9))
    canonical = np.array(canonical, dtype='<i8')
    canonical = canonical[np.lexsort(tuple(canonical[:, i] for i in range(8, -1, -1)))]
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def triangle_comparison(actual_triangles, expected_triangles):
    # Verify every coordinate in each direction; no quantization-based pass.
    actual = actual_triangles.reshape(-1, 3)
    expected = expected_triangles.reshape(-1, 3)
    unique_expected, expected_inverse = np.unique(expected, axis=0, return_inverse=True)
    expected_tree = cKDTree(unique_expected)
    actual_distance, actual_ids = expected_tree.query(actual, k=1)
    reverse_distance, _ = cKDTree(actual).query(unique_expected, k=1)
    coord_error = max(float(actual_distance.max()), float(reverse_distance.max()))
    af = canonical_faces(actual_ids.reshape(-1, 3))
    ef = canonical_faces(expected_inverse.reshape(-1, 3))
    triangle_membership_equal = bool(af.shape == ef.shape and np.array_equal(af, ef))
    return {
        'scene_triangle_count': len(actual_triangles),
        'stl_triangle_count': len(expected_triangles),
        'scene_unique_coordinate_count': len(np.unique(actual, axis=0)),
        'stl_unique_coordinate_count': len(unique_expected),
        'max_mutual_coordinate_distance_mm': coord_error,
        'all_triangle_vertex_memberships_match': triangle_membership_equal,
        'mesh_digest_coordinate_grid_mm': TOL_MM,
        'scene_physical_mesh_canonical_sha256': coordinate_mesh_sha256(actual_triangles),
        'stl_assembly_mesh_canonical_sha256': coordinate_mesh_sha256(expected_triangles),
        'pass': bool(coord_error <= TOL_MM and triangle_membership_equal),
    }


def main():
    parameters_path = ROOT / 'parameters.json'
    parameters = json.loads(parameters_path.read_text(encoding='utf-8'))
    scene_path = ROOT / 'scene.blend'
    scene_sha_before = sha256(scene_path)
    bpy.ops.wm.open_mainfile(filepath=str(scene_path))
    scene = bpy.context.scene
    settings = scene.unit_settings
    mm_per_bu = float(settings.scale_length) * 1000.0
    geometry = [obj for obj in scene.objects if obj.type == 'MESH']
    expected_names = {part['name'] for part in parameters['parts']}
    actual_names = {obj.name for obj in geometry}
    unit_pass = bool(settings.system == 'METRIC' and abs(settings.scale_length - .001) < 1e-9
                     and settings.length_unit == 'MILLIMETERS')
    parts = []
    all_scene_coordinates = []
    all_expected_coordinates = []
    for part in parameters['parts']:
        path = ROOT / 'models' / part['stl']
        actual_stl_sha = sha256(path)
        stl_triangles = binary_stl(path)
        expected = transformed(stl_triangles, np.array(part['assembly_transform_mm'], dtype=float))
        obj = scene.objects.get(part['name'])
        if obj is None or obj.type != 'MESH':
            parts.append({'part': part['name'], 'pass': False, 'error': 'missing MESH object'})
            continue
        obj.data.calc_loop_triangles()
        raw_coords = np.array([vertex.co[:] for vertex in obj.data.vertices], dtype=float)
        matrix = np.array(obj.matrix_world, dtype=float)
        world_coords = raw_coords @ matrix[:3, :3].T + matrix[:3, 3]
        world_mm = world_coords * mm_per_bu
        scene_triangles = world_mm[np.array([triangle.vertices[:] for triangle in obj.data.loop_triangles])]
        comparison = triangle_comparison(scene_triangles, expected)
        actual_bounds = bounds(world_mm)
        expected_bounds = bounds(expected)
        physical_extent = np.ptp(world_mm, axis=0)
        expected_extent = np.ptp(expected.reshape(-1, 3), axis=0)
        bbox_error = float(np.max(np.abs(actual_bounds - expected_bounds)))
        declared_bounds_error = float(np.max(np.abs(expected_bounds - np.array(part['assembly_bounds_mm']))))
        transform_identity = bool(np.allclose(matrix, np.eye(4), atol=1e-9, rtol=0))
        unapplied_modifiers = [modifier.name for modifier in obj.modifiers]
        stl_print_bounds_error = float(np.max(np.abs(bounds(stl_triangles) - np.array(part['print_bounds_mm']))))
        part_pass = bool(comparison['pass'] and actual_stl_sha == part['sha256'] and bbox_error <= TOL_MM
                         and declared_bounds_error <= TOL_MM and transform_identity and not unapplied_modifiers
                         and stl_print_bounds_error <= TOL_MM)
        parts.append({
            'part': part['name'], 'stl': part['stl'],
            'stl_sha256_actual': actual_stl_sha, 'stl_sha256_declared': part['sha256'],
            'stl_hash_matches_parameters': actual_stl_sha == part['sha256'],
            'object_location_BU': list(obj.location), 'object_rotation_euler': list(obj.rotation_euler),
            'object_scale': list(obj.scale), 'matrix_world_identity': transform_identity,
            'modifiers': unapplied_modifiers, 'scene_world_bounds_physical_mm': actual_bounds.tolist(),
            'stl_transformed_bounds_mm': expected_bounds.tolist(),
            'physical_extent_mm': physical_extent.tolist(), 'expected_extent_mm': expected_extent.tolist(),
            'max_bounds_error_mm': bbox_error, 'max_declared_bounds_error_mm': declared_bounds_error,
            'max_print_bounds_error_mm': stl_print_bounds_error,
            'triangle_coordinate_comparison': comparison, 'pass': part_pass,
        })
        all_scene_coordinates.append(world_mm)
        all_expected_coordinates.append(expected.reshape(-1, 3))
    scene_bounds = bounds(np.concatenate(all_scene_coordinates))
    expected_bounds = bounds(np.concatenate(all_expected_coordinates))
    declared_bounds = np.array(parameters['assembly_bounds_mm'], dtype=float)
    assembly_bounds_pass = bool(np.allclose(scene_bounds, expected_bounds, atol=TOL_MM, rtol=0)
                                and np.allclose(scene_bounds, declared_bounds, atol=TOL_MM, rtol=0))
    reference = ROOT / 'models' / 'assembly-reference-do-not-print.stl'
    reference_sha = sha256(reference)
    reference_hash_pass = reference_sha == parameters['reference_stl_sha256']
    scene_sha_after = sha256(scene_path)
    report = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'verifier': 'source/verify_scene.py; read-only saved-file reopen; independent binary STL parser',
        'verifier_sha256': sha256(Path(__file__).resolve()),
        'blender_version': bpy.app.version_string, 'tolerance_mm': TOL_MM,
        'parameters_sha256': sha256(parameters_path),
        'scene_sha256': scene_sha_before, 'scene_file_unchanged': scene_sha_before == scene_sha_after,
        'units': {'system': settings.system, 'scale_length_metres_per_BU': settings.scale_length,
                  'display_length_unit': settings.length_unit, 'physical_mm_per_BU': mm_per_bu,
                  'formula': 'physical mm = world BU * scale_length metres/BU * 1000 mm/metre',
                  'pass': unit_pass},
        'geometry_object_count': len(geometry), 'expected_geometry_object_count': 9,
        'geometry_object_names_exact': expected_names == actual_names,
        'excluded_non_geometry_objects': [{'name': obj.name, 'type': obj.type}
                                          for obj in scene.objects if obj.type != 'MESH'],
        'assembly_bounds_physical_mm': scene_bounds.tolist(),
        'assembly_extents_physical_mm': (scene_bounds[1] - scene_bounds[0]).tolist(),
        'declared_assembly_bounds_mm': declared_bounds.tolist(),
        'assembly_bounds_pass': assembly_bounds_pass,
        'assembly_reference_stl_sha256': reference_sha,
        'assembly_reference_stl_hash_matches_parameters': reference_hash_pass,
        'parts': parts,
        'pass': bool(unit_pass and len(geometry) == 9 and actual_names == expected_names
                     and assembly_bounds_pass and reference_hash_pass and all(part['pass'] for part in parts)
                     and scene_sha_before == scene_sha_after),
        'limitations': ['This verifies digital scene/STL consistency, not physical printing, support removal, or fit.',
                        'Historical appearance and estimates are reviewed separately in scene-visual-review.md.'],
    }
    report_path = ROOT / 'qa' / 'scene-independent-report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pass': report['pass'], 'parts': len(parts), 'assembly_mm': report['assembly_extents_physical_mm'],
                      'scene_sha256': scene_sha_before, 'report': str(report_path)}, ensure_ascii=False))
    if not report['pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
