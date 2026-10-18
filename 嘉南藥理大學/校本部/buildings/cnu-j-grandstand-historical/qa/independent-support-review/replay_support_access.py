"""Replay the independent finite point/ray/route checks from retained NPZ.

This tests model-only geometry. It does not model support mass, a whole bent
tool, deformation, adhesion or removal forces, and cannot certify removability.
The source review's coordinates and thresholds are intentionally preserved.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

import numpy as np
import trimesh


def replay(package, paths):
    data = np.load(paths, allow_pickle=False)
    mask = np.char.startswith(data['role'], 'Support')
    a = data['a'][mask] - [125, 111, 0]
    b = data['b'][mask] - [125, 111, 0]
    points = []
    for p, q in zip(a, b):
        steps = max(1, math.ceil(float(np.linalg.norm(q - p)) / 1.0))
        points.extend(p + (q - p) * t for t in np.linspace(0, 1, steps + 1))
    points = np.unique(np.round(points, 5), axis=0)
    body_path = package / 'parts/main_body-assembly.stl'
    body = trimesh.load_mesh(body_path, process=True)
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(body)
    directions = np.array([
        [0, -1, 0], [0, 1, 0], [-1, 0, 0], [1, 0, 0],
        [-1, -1, 0], [1, -1, 0], [-1, 1, 0], [1, 1, 0]], float)
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    clear = np.array([
        ~ray.intersects_any(points + d * 1e-5, np.tile(d, (len(points), 1)))
        for d in directions]).T
    flags = points[~np.any(clear, axis=1)]

    def collision(origins, ends):
        delta = ends - origins
        lengths = np.linalg.norm(delta, axis=1)
        unit = delta / lengths[:, None]
        loc, ix, _ = ray.intersects_location(
            origins + unit * 1e-5, unit, multiple_hits=True)
        blocked = np.zeros(len(origins), bool)
        if len(ix):
            dist = np.linalg.norm(loc - origins[ix], axis=1)
            blocked[ix[dist < lengths[ix] - 1e-5]] = True
        return blocked

    first = flags.copy()
    first[:, 1] = -33
    second = first.copy()
    second[:, 0] = np.where(flags[:, 0] < 0, -65, 65)
    last = second.copy()
    last[:, 1] = -60
    blocked = [collision(x, y) for x, y in [
        (flags, first), (first, second), (second, last)]]
    offsets = np.array([
        [0, .5 * math.cos(t), .5 * math.sin(t)]
        for t in np.linspace(0, 2 * math.pi, 65)])
    shaft = []
    for sign in [-1, 1]:
        origins = np.array([sign * 31, -33, 8.]) + offsets
        ends = np.array([sign * 65, -33, 8.]) + offsets
        shaft.append({'side': sign, 'offset_rays': len(offsets),
                      'radius_mm': .5,
                      'blocked_rays': int(collision(origins, ends).sum())})
    return {
        'scope': 'Independent finite support-point replay; not physical removal or a continuous swept-tool guarantee.',
        'input_paths_name': paths.name,
        'input_paths_sha256': hashlib.sha256(paths.read_bytes()).hexdigest(),
        'main_body_assembly_sha256': hashlib.sha256(body_path.read_bytes()).hexdigest(),
        'actual_support_segment_count': len(a),
        'unique_points': len(points),
        'tested_directions': directions.tolist(),
        'direct_y_exterior_clear_count': int(np.any(clear[:, :2], axis=1).sum()),
        'eight_direction_any_clear_count': int(np.any(clear, axis=1).sum()),
        'no_eight_direction_clear_count': len(flags),
        'no_eight_direction_points': flags.tolist(),
        'flagged_sample_points_inside_body_count': int(body.contains(flags).sum()),
        'blocked_point_routes_by_leg': [int(x.sum()) for x in blocked],
        'all_flagged_point_routes_clear': not np.any(blocked),
        'shaft_corridor_limited_radius_checks': shaft,
        'thresholds': {'sample_step_max_mm': 1.0, 'dedup_decimal_places': 5,
                       'ray_endpoint_margin_mm': 1e-5,
                       'route_y_first_mm': -33, 'route_x_side_mm': 65,
                       'route_y_last_mm': -60},
        'limitations': [
            'Model-only finite points and rays, not all surfaces or all directions.',
            'Other support, whole tools, gripped fragments, adhesion and forces are not modeled.',
            'No print, support removal, trial fit, adhesive strength or surface-damage test.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--paths', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; select a new file to preserve prior evidence')
    result = replay(args.package, args.paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k != 'no_eight_direction_points'}, indent=2))


if __name__ == '__main__':
    main()
