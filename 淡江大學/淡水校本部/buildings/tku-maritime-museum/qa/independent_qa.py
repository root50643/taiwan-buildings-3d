"""Read-only STL QA. Source meshes are never repaired or rewritten.

Usage: python independent_qa.py model.stl --out independent-report.json
       python independent_qa.py --selftest --out independent-controls.json

Triangle intersection uses double-precision plane sections, coplanar 2D
intersection, a spatial index, and a scale-dependent tolerance. It is a
numerical screen, not an exact-arithmetic proof. Thickness uses one inward
normal ray per face centroid. Overhangs use the supplied STL Z orientation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString, Point


def plane_section(triangle, normal, point, eps):
    d = (triangle - point) @ normal
    pts = [triangle[i] for i in range(3) if abs(d[i]) <= eps]
    for i, j in [(0, 1), (1, 2), (2, 0)]:
        if (d[i] < -eps and d[j] > eps) or (d[j] < -eps and d[i] > eps):
            pts.append(triangle[i] + (triangle[j] - triangle[i]) * d[i] / (d[i] - d[j]))
    unique = []
    for p in pts:
        if not any(np.linalg.norm(p-q) <= eps for q in unique):
            unique.append(p)
    return np.asarray(unique)


def pair_intersection(a, b, shared, eps):
    na = np.cross(a[1]-a[0], a[2]-a[0]); na /= np.linalg.norm(na)
    nb = np.cross(b[1]-b[0], b[2]-b[0]); nb /= np.linalg.norm(nb)
    da = (a-b[0]) @ nb; db = (b-a[0]) @ na
    if (min(da) > eps or max(da) < -eps or min(db) > eps or max(db) < -eps):
        return None
    axis = np.cross(na, nb)
    # Binary STL rounds coordinates to float32: triangles cut from one sloped
    # plane can acquire slightly different normals. Classify coplanarity by
    # BOTH point-to-plane distances, not a normal-angle threshold alone.
    coplanar = max(abs(da)) <= eps and max(abs(db)) <= eps
    if coplanar:
        drop = int(np.argmax(abs(na)))
        pa, pb = np.delete(a, drop, axis=1), np.delete(b, drop, axis=1)
        intersection = Polygon(pa).intersection(Polygon(pb))
        if intersection.is_empty:
            return None
        if not len(shared):
            return {"kind": "coplanar_nonadjacent_contact", "area": float(intersection.area)}
        projected = np.delete(shared, drop, axis=1)
        allowed = Point(projected[0]) if len(shared) == 1 else LineString(projected[:2])
        excess = intersection.difference(allowed.buffer(eps*3))
        if excess.is_empty:
            return None
        return {"kind": "coplanar_overlap_beyond_shared_topology", "area": float(intersection.area)}
    if np.linalg.norm(axis) < 1e-9:
        return None
    axis /= np.linalg.norm(axis)
    sa, sb = plane_section(a, nb, b[0], eps), plane_section(b, na, a[0], eps)
    if not len(sa) or not len(sb):
        return None
    ia, ib = sa @ axis, sb @ axis
    lo, hi = max(min(ia), min(ib)), min(max(ia), max(ib))
    if hi < lo-eps:
        return None
    if len(shared):
        allowed = shared @ axis
        if lo >= min(allowed)-3*eps and hi <= max(allowed)+3*eps:
            return None
    return {"kind": "noncoplanar_intersection_or_touch", "intersection_length": float(max(0, hi-lo))}


def intersections(mesh, eps):
    tris = mesh.triangles
    tree = mesh.triangles_tree
    count = 0; broad = 0; pairs = []
    normals = np.linalg.norm(np.cross(tris[:, 1]-tris[:, 0], tris[:, 2]-tris[:, 0]), axis=1)
    for i, tri in enumerate(tris):
        if normals[i] <= eps*eps:
            continue
        bounds = np.r_[tri.min(axis=0)-eps, tri.max(axis=0)+eps]
        for j in tree.intersection(bounds):
            if j <= i or normals[j] <= eps*eps:
                continue
            broad += 1
            common = np.intersect1d(mesh.faces[i], mesh.faces[j])
            if len(common) == 3:
                result = {"kind": "duplicate_geometric_triangle"}
            else:
                result = pair_intersection(tri, tris[j], mesh.vertices[common], eps)
            if result:
                count += 1
                if len(pairs) < 60:
                    pairs.append({"faces": [int(i), int(j)], "shared_vertex_count": int(len(common)), **result})
    return {"method": "AABB broad phase; plane-section intervals; Shapely coplanar intersections; shared topology subtraction", "tolerance_mm": eps, "broad_phase_pairs": broad, "intersection_pair_count": count, "first_pairs": pairs, "passed": count == 0}


def rays(mesh, origins, directions):
    locations, ray_ids, tri_ids = mesh.ray.intersects_location(origins, directions, multiple_hits=False)
    distances = np.full(len(origins), np.inf)
    distances[ray_ids] = np.linalg.norm(locations-origins[ray_ids], axis=1)
    faces = np.full(len(origins), -1, dtype=int); faces[ray_ids] = tri_ids
    return distances, faces


def inspect(mesh, label, threshold=1.2, run_intersections=True):
    before = len(mesh.vertices)
    mesh = mesh.copy()
    mesh.merge_vertices(digits_vertex=7)
    extents = mesh.extents; eps = max(float(max(extents))*1e-8, 1e-7)
    edge_counts = np.bincount(mesh.edges_unique_inverse)
    cross = np.cross(mesh.triangles[:, 1]-mesh.triangles[:, 0], mesh.triangles[:, 2]-mesh.triangles[:, 0])
    area = np.linalg.norm(cross, axis=1)/2
    components = trimesh.graph.connected_components(mesh.face_adjacency, nodes=np.arange(len(mesh.faces)))
    topology = {"vertices_before_coordinate_merge": before, "merged_vertices": len(mesh.vertices), "faces": len(mesh.faces), "boundary_edge_count": int(sum(edge_counts == 1)), "nonmanifold_edge_count": int(sum(edge_counts > 2)), "degenerate_face_count": int(sum(area <= eps*eps)), "face_component_count": len(components), "winding_consistent": bool(mesh.is_winding_consistent), "signed_volume_mm3": float(mesh.volume), "bounds_mm": mesh.bounds.tolist(), "extents_mm": extents.tolist()}
    topology["passed"] = topology["boundary_edge_count"] == topology["nonmanifold_edge_count"] == topology["degenerate_face_count"] == 0 and topology["face_component_count"] == 1 and topology["winding_consistent"] and topology["signed_volume_mm3"] > 0
    directions = -mesh.face_normals
    distances, opposite = rays(mesh, mesh.triangles_center+directions*eps*5, directions)
    distances += eps*5
    finite = np.isfinite(distances)
    low = finite & (distances < threshold-eps*10)
    first = np.flatnonzero(low)[np.argsort(distances[low])][:40]
    thickness = {"method": "one inward-normal ray per face centroid; local corners can yield short chords", "sample_count": len(mesh.faces), "finite_exit_count": int(sum(finite)), "missing_exit_count": int(sum(~finite)), "threshold_mm": threshold, "minimum_mm": float(min(distances[finite])) if any(finite) else None, "percentile_1_mm": float(np.percentile(distances[finite], 1)) if any(finite) else None, "below_threshold_face_count": int(sum(low)), "below_threshold_face_area_mm2": float(sum(area[low])), "samples": [{"face": int(i), "opposite_face": int(opposite[i]), "thickness_mm": float(distances[i]), "centroid_mm": mesh.triangles_center[i].tolist(), "area_mm2": float(area[i])} for i in first], "screening_passed": not any(low) and all(finite), "limitation": "Centroid rays are a finite sample, not an exhaustive medial-axis wall-thickness proof. Short corner chords require inspection; they are not automatically dismissed."}
    zmin = mesh.bounds[0, 2]
    nz = mesh.face_normals[:, 2]
    overhang = (nz < -math.cos(math.radians(45))) & (mesh.triangles_center[:, 2] > zmin+eps*20)
    ids = np.flatnonzero(overhang)
    down = np.tile([0., 0., -1.], (len(ids), 1))
    origins = mesh.triangles_center[ids] + down*eps*5
    clearances, below = rays(mesh, origins, down) if len(ids) else (np.array([]), np.array([]))
    side_origins = np.repeat(origins, 4, axis=0)
    side_directions = np.tile([[1., 0., 0.], [-1., 0., 0.], [0., 1., 0.], [0., -1., 0.]], (len(ids), 1))
    side_dist, side_faces = rays(mesh, side_origins, side_directions) if len(ids) else (np.array([]), np.array([]))
    side_dist = side_dist.reshape((-1, 4))
    order = np.argsort(-(area[ids]*abs(nz[ids])))[:60]
    hangs = {"orientation": "as supplied, +Z up; 45-degree screening threshold", "face_count": int(len(ids)), "projected_area_mm2": float(sum(area[ids]*abs(nz[ids]))), "horizontal_area_mm2": float(sum(area[(nz < -.999999) & overhang])), "has_true_unsupported_undersides": bool(len(ids)), "samples_with_at_least_one_open_cardinal_horizontal_ray": int(sum(np.any(np.isinf(side_dist), axis=1))) if len(ids) else 0, "largest_faces": [{"face": int(ids[k]), "centroid_mm": mesh.triangles_center[ids[k]].tolist(), "projected_area_mm2": float(area[ids[k]]*abs(nz[ids[k]])), "vertical_clearance_to_geometry_mm": float(clearances[k]) if np.isfinite(clearances[k]) else None, "open_horizontal_directions": [name for index, name in enumerate(["+X", "-X", "+Y", "-Y"]) if np.isinf(side_dist[k,index])]} for k in order], "support_removal_status": "ray access screen only; must inspect width, neighboring walls, and actual generated supports", "sliced": False, "test_printed": False}
    return {"label": label, "topology": topology, "self_intersections": intersections(mesh, eps) if run_intersections else None, "thickness": thickness, "overhangs": hangs}


def selftest():
    box = trimesh.creation.box([10, 10, 10]); box.apply_translation([0, 0, 5])
    thin = trimesh.creation.box([10, 10, .6]); thin.apply_translation([0, 0, .3])
    moved = box.copy(); moved.apply_translation([4, 3, 2])
    other = box.copy(); other.apply_translation([20, 0, 0])
    removed = trimesh.Trimesh(vertices=box.vertices, faces=box.faces[:-1], process=False)
    fixtures = {"closed_box": box, "open_box": removed, "two_disconnected_boxes": trimesh.util.concatenate([box, other]), "overlapping_closed_boxes": trimesh.util.concatenate([box, moved]), "thin_plate_0_6mm": thin}
    reports = {name: inspect(mesh, name) for name, mesh in fixtures.items()}
    rounded_a = np.array([[-40,8.894737243652344,62],[-24,8.894737243652344,62],[-40,17,69.]])
    rounded_b = np.array([[-40,17,69.],[-24,13.526315689086914,66],[-24,17,69.]])
    coplanar_rounding_result = pair_intersection(rounded_a, rounded_b, np.array([[-40,17,69.]]), 1.48e-6)
    checks = {"closed_box_topology_passes": reports["closed_box"]["topology"]["passed"], "closed_box_intersections_passes": reports["closed_box"]["self_intersections"]["passed"], "open_box_detected": reports["open_box"]["topology"]["boundary_edge_count"] > 0, "disconnected_detected": reports["two_disconnected_boxes"]["topology"]["face_component_count"] == 2, "intersection_detected": reports["overlapping_closed_boxes"]["self_intersections"]["intersection_pair_count"] > 0, "thin_plate_detected": reports["thin_plate_0_6mm"]["thickness"]["below_threshold_face_count"] > 0, "float32_rounded_shared_point_coplanar_triangles_accepted": coplanar_rounding_result is None}
    return {"control_checks": checks, "controls_passed": all(checks.values()), "reports": reports}


def main():
    p = argparse.ArgumentParser(); p.add_argument("stl", nargs="?"); p.add_argument("--out", required=True); p.add_argument("--selftest", action="store_true"); p.add_argument("--threshold", type=float, default=1.2)
    args = p.parse_args()
    if Path(args.out).exists():
        raise FileExistsError(f"Refusing to overwrite preserved report: {args.out}")
    if args.selftest:
        report = selftest()
    else:
        path = Path(args.stl)
        content = path.read_bytes()
        mesh = trimesh.load_mesh(path, process=False)
        report = inspect(mesh, path.name, args.threshold)
        report["stl"] = {"path": str(path), "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(), "unchanged_after_checks": hashlib.sha256(path.read_bytes()).hexdigest() == hashlib.sha256(content).hexdigest()}
    report["toolchain"] = {"python": platform.python_version(), "trimesh": trimesh.__version__, "numpy": np.__version__, "qa_revision": "v2 point-to-plane coplanarity"}
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8")
    print(json.dumps({"report": args.out, "control_checks": report.get("control_checks"), "topology": report.get("topology"), "self_intersection_pairs": report.get("self_intersections", {}).get("intersection_pair_count") if report.get("self_intersections") else None, "thickness_below_threshold_faces": report.get("thickness", {}).get("below_threshold_face_count"), "overhang_face_count": report.get("overhangs", {}).get("face_count")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
