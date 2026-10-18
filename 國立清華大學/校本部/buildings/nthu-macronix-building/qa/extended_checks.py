"""Reproducible, read-only screens of the exact original binary STL.

Usage (from any directory):
  python qa/extended_checks.py --self-test-only --output qa/controls.json
  python qa/extended_checks.py --output qa/extended-checks.json

Dependencies: Python 3, numpy, shapely. No Blender, mesh repair, rtree, slicer,
or external geometry service is used. The existing validate_model.py remains
responsible for rebuild and editable-scene agreement. This script adds raw STL
topology, an exhaustive floating-point triangle-pair intersection screen, and
sampled inward-normal thickness and downward-face support screens.

Intersection broadphase is an exhaustive axis-aligned sweep. Narrowphase uses
triangle-plane segments and interval overlap for noncoplanar triangles; coplanar
triangles are projected to their dominant plane and intersected with GEOS.
Only contact within the *actually shared* exact-position vertex or edge is
accepted as normal adjacency. No pair is discarded merely for sharing a vertex.
This is a tolerance-based screen, not an exact-arithmetic geometric proof.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import struct
import time

import numpy as np
import shapely
from shapely.geometry import Point, Polygon, LineString


SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parent.parent


def unique_points(points, eps):
    out = []
    for p in points:
        if not any(np.linalg.norm(p - q) <= eps for q in out):
            out.append(p)
    return out


def plane_segment(t, signed, eps):
    points = [t[i] for i in range(3) if abs(signed[i]) <= eps]
    for i, j in ((0, 1), (1, 2), (2, 0)):
        if (signed[i] > eps and signed[j] < -eps) or (signed[j] > eps and signed[i] < -eps):
            points.append(t[i] + (t[j] - t[i]) * (signed[i] / (signed[i] - signed[j])))
    return unique_points(points, eps)


def outside_shared_simplex(points, shared, eps):
    """Does any computed intersection lie outside its legitimate mesh contact?"""
    if not shared:
        return True
    if len(shared) == 1:
        return any(np.linalg.norm(p - shared[0]) > eps for p in points)
    if len(shared) == 2:
        a, b = shared
        ab = b - a
        denom = float(ab @ ab)
        for p in points:
            t = float((p - a) @ ab) / denom
            nearest = a + np.clip(t, 0, 1) * ab
            if np.linalg.norm(p - nearest) > eps:
                return True
        return False
    return True  # duplicate triangles must never be accepted as adjacency


def triangle_pair(a, b, eps):
    """Return an invalid intersection, or None for disjoint/normal adjacency."""
    na = np.cross(a[1] - a[0], a[2] - a[0])
    nb = np.cross(b[1] - b[0], b[2] - b[0])
    la, lb = np.linalg.norm(na), np.linalg.norm(nb)
    if la < 1e-15 or lb < 1e-15:
        return {"kind": "degenerate_triangle_pair"}
    na /= la
    nb /= lb
    da = (a - b[0]) @ nb
    db = (b - a[0]) @ na
    if (np.all(da > eps) or np.all(da < -eps) or np.all(db > eps) or np.all(db < -eps)):
        return None
    # Shared positions are exact raw STL float32 positions, never proximity welds.
    shared = [p for p in a if any(np.array_equal(p, q) for q in b)]
    coplanar = np.max(np.abs(da)) <= eps and np.max(np.abs(db)) <= eps
    if coplanar:
        axis = int(np.argmax(np.abs(na)))
        keep = [i for i in range(3) if i != axis]
        hit = Polygon(a[:, keep]).intersection(Polygon(b[:, keep]))
        if hit.is_empty:
            return None
        if hit.area > eps * eps:
            return {"kind": "coplanar_area_overlap", "projected_area_mm2": float(hit.area), "shared_vertices": len(shared)}
        if len(shared) == 1:
            allowed = Point(shared[0][keep]).buffer(eps)
        elif len(shared) == 2:
            allowed = LineString([p[keep] for p in shared]).buffer(eps)
        else:
            allowed = Polygon()
        if not hit.difference(allowed).is_empty:
            return {"kind": "coplanar_nonadjacent_contact", "shared_vertices": len(shared), "projected_contact_length_mm": float(hit.length)}
        return None
    direction = np.cross(na, nb)
    dl = np.linalg.norm(direction)
    if dl < 1e-12:
        # Parallel distinct planes cannot intersect. Near-parallel ambiguity is
        # reported explicitly rather than silently accepted.
        return {"kind": "near_parallel_numerical_ambiguity", "cross_normal_length": float(dl)}
    direction /= dl
    pa, pb = plane_segment(a, da, eps), plane_segment(b, db, eps)
    if not pa or not pb:
        return None
    ia = [float(p @ direction) for p in pa]
    ib = [float(p @ direction) for p in pb]
    lo, hi = max(min(ia), min(ib)), min(max(ia), max(ib))
    if hi < lo - eps:
        return None
    # Choose a point on the computed plane intersection line, then reconstruct
    # both overlap endpoints. Plane-segment points can have <=eps plane error.
    anchor = pa[0]
    points = [anchor + direction * (t - float(anchor @ direction)) for t in (lo, max(lo, hi))]
    if outside_shared_simplex(points, shared, eps * 4):
        return {"kind": "noncoplanar_intersection", "segment_length_mm": max(0.0, hi - lo), "shared_vertices": len(shared), "points_mm": [p.tolist() for p in points]}
    return None


def self_test(eps):
    a = np.array([[0., 0, 0], [2, 0, 0], [0, 2, 0]])
    tests = [
        ("crossing_nonadjacent", [[.5, .5, -1], [.5, .5, 1], [1.5, .5, 0]], True),
        ("coplanar_area_overlap", [[.2, .2, 0], [1.2, .2, 0], [.2, 1.2, 0]], True),
        ("duplicate_triangle", a.copy(), True),
        ("nonadjacent_point_contact", [[1, 1, 0], [1, 1, 1], [2, 2, 1]], True),
        ("shared_vertex_but_also_crossing", [[0, 0, 0], [1, 1, -1], [1, 1, 1]], True),
        ("shared_edge_coplanar_overlap", [[0, 0, 0], [2, 0, 0], [1, .5, 0]], True),
        ("separated", [[3, 3, 1], [4, 3, 1], [3, 4, 1]], False),
        ("parallel_separated", [[0, 0, .1], [2, 0, .1], [0, 2, .1]], False),
        ("shared_edge_coplanar", [[0, 0, 0], [2, 0, 0], [1, -1, 0]], False),
        ("shared_edge_folded", [[0, 0, 0], [2, 0, 0], [1, 0, 1]], False),
        ("shared_vertex_only", [[0, 0, 0], [-1, 0, 1], [0, -1, 1]], False),
        ("aabb_overlaps_but_disjoint", [[2, 2, 0], [2, .5, 0], [.5, 2, 0]], False),
    ]
    rows = []
    for name, b, expected in tests:
        actual = triangle_pair(a.copy(), np.array(b, dtype=float), eps)
        rows.append({"name": name, "expected_invalid_intersection": expected, "detected_invalid_intersection": actual is not None, "matches_expected": (actual is not None) == expected, "detail": actual})
    return {"passed": all(r["matches_expected"] for r in rows), "cases": rows}


def load_raw(path):
    raw = path.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError("Input must be a length-consistent binary STL; no repair/conversion is performed.")
    rec = np.frombuffer(raw, offset=84, dtype=np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")]), count=count)
    tri = rec["v"].astype(float)
    vertices, inv = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    return raw, rec["normal"].astype(float), tri, vertices, inv.reshape(-1, 3)


def topology(tri, vertices, faces, saved):
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    doubled = np.linalg.norm(cross, axis=1)
    normals = cross / np.maximum(doubled[:, None], 1e-30)
    edges = {}
    links = [[] for _ in vertices]
    parent = list(range(len(faces)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for fi, (i, j, k) in enumerate(faces):
        for u, v in ((i, j), (j, k), (k, i)):
            key = tuple(sorted((int(u), int(v))))
            rows = edges.setdefault(key, [])
            if rows:
                parent[find(fi)] = find(rows[0][0])
            rows.append((fi, int(u), int(v)))
        for v, u, w in ((i, j, k), (j, k, i), (k, i, j)):
            links[v].append((int(u), int(w)))
    badlinks = []
    for vi, pairs in enumerate(links):
        adj = {}
        for u, v in pairs:
            adj.setdefault(u, set()).add(v)
            adj.setdefault(v, set()).add(u)
        seen = set()
        todo = [next(iter(adj))] if adj else []
        while todo:
            v = todo.pop()
            if v not in seen:
                seen.add(v)
                todo.extend(adj[v] - seen)
        if not adj or any(len(n) != 2 for n in adj.values()) or len(seen) != len(adj):
            badlinks.append(vi)
    nonmanifold = [list(k) for k, rows in edges.items() if len(rows) != 2]
    inconsistent = [list(k) for k, rows in edges.items() if len(rows) == 2 and rows[0][1:] == rows[1][1:]]
    volume = float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6)
    components = len({find(i) for i in range(len(faces))})
    checks = {
        "all_original_coordinates_and_saved_normals_finite": bool(np.isfinite(tri).all() and np.isfinite(saved).all()),
        "all_original_faces_nondegenerate": bool((doubled > 1e-9).all()),
        "all_original_saved_normals_unit": bool(np.allclose(np.linalg.norm(saved, axis=1), 1, atol=1e-5)),
        "all_original_saved_normals_match_winding": bool(np.allclose(saved, normals, atol=1e-5)),
        "all_exact_position_edges_have_two_faces": not nonmanifold,
        "all_exact_position_vertex_links_single_cycles": not badlinks,
        "all_shared_edges_oppositely_oriented": not inconsistent,
        "one_face_connected_surface_shell": components == 1,
        "positive_signed_volume": volume > 0,
    }
    return {"passed": all(checks.values()), "checks": checks, "exact_position_vertices": len(vertices), "faces": len(faces), "face_connected_shells": components, "signed_volume_mm3": volume, "nonmanifold_edge_count": len(nonmanifold), "bad_vertex_link_count": len(badlinks), "inconsistent_edge_count": len(inconsistent), "nonmanifold_edges": nonmanifold, "bad_vertex_indices": badlinks, "inconsistent_edges": inconsistent}, normals, doubled / 2


def self_intersections(tri, eps):
    lo, hi = tri.min(axis=1), tri.max(axis=1)
    order = np.argsort(lo[:, 0], kind="stable")
    active = []
    broad = 0
    hits = []
    for raw_i in order:
        i = int(raw_i)
        active = [j for j in active if hi[j, 0] >= lo[i, 0] - eps]
        for j in active:
            if np.any(hi[j, 1:] < lo[i, 1:] - eps) or np.any(hi[i, 1:] < lo[j, 1:] - eps):
                continue
            broad += 1
            hit = triangle_pair(tri[i], tri[j], eps)
            if hit is not None:
                hits.append({"faces": [j, i], "bounds_mm": [np.minimum(lo[i], lo[j]).tolist(), np.maximum(hi[i], hi[j]).tolist()], **hit})
        active.append(i)
    return {"passed": not hits, "absolute_tolerance_mm": eps, "broadphase_candidate_pairs": broad, "tested_pairs_including_adjacent": broad, "invalid_intersection_or_ambiguity_count": len(hits), "findings": hits, "method": "Exhaustive X sweep plus Y/Z AABB overlap; normalized plane sidedness; noncoplanar triangle-plane segment interval overlap; coplanar dominant-plane GEOS polygon intersection. Only exact-position shared-simplex contacts accepted.", "limitations": ["Double-precision floating-point and GEOS predicates with the declared tolerance; not exact arithmetic or a formal proof.", "Geometry within tolerance may be merged in the predicates. Nearly parallel ambiguity is a finding, never silently counted as a pass."]}


def ray_first(tri, origin, direction, source_face, eps):
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    p = np.cross(np.broadcast_to(direction, e2.shape), e2)
    det = np.einsum("ij,ij->i", e1, p)
    valid = np.abs(det) > 1e-12
    inv = np.zeros_like(det)
    inv[valid] = 1 / det[valid]
    tvec = origin - tri[:, 0]
    u = np.einsum("ij,ij->i", tvec, p) * inv
    q = np.cross(tvec, e1)
    v = q @ direction * inv
    t = np.einsum("ij,ij->i", e2, q) * inv
    valid &= (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > eps)
    valid[source_face] = False
    ids = np.flatnonzero(valid)
    if not len(ids):
        return None
    fi = int(ids[np.argmin(t[ids])])
    return fi, float(t[fi])


def ray_screens(tri, normals, areas, eps, width):
    centers = tri.mean(axis=1)
    inward_rows, misses, thin = [], [], []
    rayeps = max(eps * 10, 1e-5)
    for fi, (center, normal) in enumerate(zip(centers, normals)):
        hit = ray_first(tri, center - normal * rayeps, -normal, fi, rayeps)
        if hit is None:
            misses.append(fi)
            continue
        target, travel = hit
        length = travel + rayeps
        row = {"face": fi, "exit_face": target, "distance_mm": length, "face_area_mm2": float(areas[fi]), "start_mm": center.tolist(), "inward_direction": (-normal).tolist(), "exit_faces_outward": bool(normals[target] @ (-normal) > 0)}
        inward_rows.append(row)
        if length < width:
            thin.append(row)
    # This includes all face centroids, not just a random subset. Small triangles
    # still receive one sample each; the area totals expose their weighting.
    thickness = {"screen_width_mm": width, "method": "One inward normal ray from every original triangle centroid; origin offset inward by %.9g mm; brute-force Moller-Trumbore nearest positive hit against every original triangle, source face excluded." % rayeps, "sample_count": len(tri), "successful_samples": len(inward_rows), "missing_exit_count": len(misses), "missing_exit_source_faces": misses, "minimum_sampled_distance_mm": min((r["distance_mm"] for r in inward_rows), default=None), "flagged_sample_count": len(thin), "flagged_face_area_mm2": float(sum(r["face_area_mm2"] for r in thin)), "flagged_samples": thin, "nearest_20_samples": sorted(inward_rows, key=lambda r: r["distance_mm"])[:20], "limitations": ["Finite centroid samples measure normal chord length, not the global minimum wall thickness; edge and vertex tips can be thinner.", "Short chords at tapers, relief and corners are warnings; they do not automatically establish unprintability.", "No extrusion width, toolpath, material, nozzle, bridge or print outcome is modeled."]}
    base = np.max(np.abs(tri[:, :, 2]), axis=1) <= eps
    down = (normals[:, 2] < -math.cos(math.radians(45))) & ~base
    down_rows = []
    for raw_fi in np.flatnonzero(down):
        fi = int(raw_fi)
        center = centers[fi]
        hit = ray_first(tri, center - np.array([0., 0, rayeps]), np.array([0., 0, -1]), fi, rayeps)
        row = {"face": fi, "centroid_mm": center.tolist(), "normal": normals[fi].tolist(), "area_mm2": float(areas[fi]), "xy_projected_area_mm2": float(areas[fi] * -normals[fi, 2]), "angle_from_down_axis_deg": math.degrees(math.acos(float(np.clip(-normals[fi, 2], -1, 1)))), "first_surface_below_face": hit[0] if hit else None, "vertical_air_gap_mm": hit[1] + rayeps if hit else None}
        down_rows.append(row)
    support = {"orientation": "As delivered, base at z=0 on the build plate.", "method": "Every downward-facing original triangle whose normal lies within 45 degrees of -Z, excluding triangles wholly on z=0. Vertical -Z ray from centroid records the first lower surface and air gap. This is an overhang screening metric, not support generation.", "downward_face_count": len(down_rows), "downward_face_area_mm2": float(sum(r["area_mm2"] for r in down_rows)), "xy_projected_area_mm2": float(sum(r["xy_projected_area_mm2"] for r in down_rows)), "maximum_sampled_vertical_gap_mm": max((r["vertical_air_gap_mm"] for r in down_rows if r["vertical_air_gap_mm"] is not None), default=None), "no_lower_surface_count": sum(r["first_surface_below_face"] is None for r in down_rows), "findings": down_rows, "limitations": ["A downward face over a gap may be bridgeable; a vertical ray does not decide whether support is necessary.", "Triangle-centroid rays can miss the worst point and do not evaluate bridge span, support access/removal, cooling, adhesion or deformation.", "No formal slicer run, G-code review or physical print test was performed."]}
    return thickness, support


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stl", type=Path, default=ROOT / "model.stl")
    p.add_argument("--output", type=Path, default=SCRIPT.parent / "extended-checks.json")
    p.add_argument("--self-test-only", action="store_true")
    p.add_argument("--tolerance", type=float, default=1e-7)
    p.add_argument("--thin-width", type=float, default=.8)
    args = p.parse_args()
    started = time.monotonic()
    controls = self_test(args.tolerance)
    report = {"schema_version": 1, "script_sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), "runtime": {"python": platform.python_version(), "numpy": np.__version__, "shapely": shapely.__version__, "geos": shapely.geos_version_string}, "controls": controls, "formal_slicer_run": False, "physical_print_test": False}
    exit_code = 0
    if not controls["passed"]:
        exit_code = 2
        report["execution_status"] = "stopped_due_to_failed_controls"
    elif args.self_test_only:
        report["execution_status"] = "controls_only_no_stl_read"
    else:
        raw, saved, tri, vertices, faces = load_raw(args.stl)
        report["stl_sha256"] = hashlib.sha256(raw).hexdigest()
        report["stl_bytes"] = len(raw)
        report["dimensions_mm"] = np.ptp(tri.reshape(-1, 3), axis=0).tolist()
        report["bounds_mm"] = [tri.min(axis=(0, 1)).tolist(), tri.max(axis=(0, 1)).tolist()]
        topo, normals, areas = topology(tri, vertices, faces, saved)
        report["original_stl_topology"] = topo
        report["self_intersection_screen"] = self_intersections(tri, args.tolerance)
        report["normal_chord_thickness_screen"], report["overhang_support_screen"] = ray_screens(tri, normals, areas, args.tolerance, args.thin_width)
        report["hard_geometry_checks_passed"] = topo["passed"] and report["self_intersection_screen"]["passed"]
        report["execution_status"] = "completed_with_screening_warnings" if (report["normal_chord_thickness_screen"]["flagged_sample_count"] or report["overhang_support_screen"]["downward_face_count"]) else "completed"
        # Thickness and support warnings remain visible and do not get rewritten
        # as pass/fail or silently incorporated into a global printable claim.
        if not report["hard_geometry_checks_passed"]:
            exit_code = 1
    report["elapsed_seconds"] = time.monotonic() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {k: v for k, v in report.items() if k in ("execution_status", "stl_sha256", "hard_geometry_checks_passed", "elapsed_seconds")}
    summary["controls_passed"] = controls["passed"]
    if "self_intersection_screen" in report:
        summary["intersection_findings"] = report["self_intersection_screen"]["invalid_intersection_or_ambiguity_count"]
        summary["thin_samples"] = report["normal_chord_thickness_screen"]["flagged_sample_count"]
        summary["downward_faces"] = report["overhang_support_screen"]["downward_face_count"]
    print(json.dumps(summary, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
