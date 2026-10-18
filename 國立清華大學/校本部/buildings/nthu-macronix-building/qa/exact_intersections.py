"""Supplemental exact-rational self-contact test; never overwrites initial screen.

python qa/exact_intersections.py --output qa/exact-intersections.json

Binary STL coordinates are dyadic rationals. They are scaled to common Python
integers without changing their value. Plane signed distances and broadphase
are integer predicates. Plane cuts and coplanar clipping use fractions.Fraction.
All AABB-overlapping pairs, including adjacent pairs, are checked. Only contact
contained in an exact shared vertex or shared edge is accepted.

This proves the stated triangle contact property for the saved STL coordinates,
subject to this implementation; it is not a CAD/source accuracy, wall thickness,
slicer, support generation, or physical print proof. It is independent evidence,
not a replacement for the preserved floating-point screen's original findings.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import json
import platform
import time

import numpy as np


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("initial_screen", HERE / "extended_checks.py")
initial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(initial)


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def integer_coordinates(triangles):
    ratios = [[[(float(v).as_integer_ratio()) for v in p] for p in t] for t in triangles]
    scale = max(den for t in ratios for p in t for _, den in p)
    return [tuple(tuple(num * (scale // den) for num, den in p) for p in t) for t in ratios], scale


def cut_plane(t, distances):
    points = [p for p, d in zip(t, distances) if d == 0]
    for i, j in ((0, 1), (1, 2), (2, 0)):
        di, dj = distances[i], distances[j]
        if di * dj < 0:
            points.append(tuple(F(t[i][k] * dj - t[j][k] * di, dj - di) for k in range(3)))
    return list(dict.fromkeys(points))


def contained(p, shared):
    if len(shared) == 1:
        return p == shared[0]
    if len(shared) != 2:
        return False
    a, b = shared
    ap, ab = sub(p, a), sub(b, a)
    if len(p) == 3:
        collinear = cross(ap, ab) == (0, 0, 0)
    else:
        collinear = ap[0] * ab[1] == ap[1] * ab[0]
    return collinear and all(min(a[k], b[k]) <= p[k] <= max(a[k], b[k]) for k in range(len(p)))


def cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]


def coplanar_clip(a, b):
    """Exact Sutherland-Hodgman clipping, retaining zero-area point/edge hits."""
    orientation = cross2(sub(b[1], b[0]), sub(b[2], b[0]))
    sign = 1 if orientation > 0 else -1
    poly = list(a)
    for e0, e1 in ((b[0], b[1]), (b[1], b[2]), (b[2], b[0])):
        if not poly:
            break
        edge = sub(e1, e0)
        out = []
        previous = poly[-1]
        dp = sign * cross2(edge, sub(previous, e0))
        for current in poly:
            dc = sign * cross2(edge, sub(current, e0))
            if (dp < 0 <= dc) or (dc < 0 <= dp):
                ratio = F(dp, dp - dc)
                out.append(tuple(previous[k] + ratio * (current[k] - previous[k]) for k in range(2)))
            if dc >= 0:
                out.append(current)
            previous, dp = current, dc
        poly = list(dict.fromkeys(out))
    return poly


def exact_pair(a, b, scale=1):
    na = cross(sub(a[1], a[0]), sub(a[2], a[0]))
    nb = cross(sub(b[1], b[0]), sub(b[2], b[0]))
    if na == (0, 0, 0) or nb == (0, 0, 0):
        return {"kind": "exact_degenerate_triangle"}
    da = [dot(sub(p, b[0]), nb) for p in a]
    db = [dot(sub(p, a[0]), na) for p in b]
    if (all(d > 0 for d in da) or all(d < 0 for d in da) or all(d > 0 for d in db) or all(d < 0 for d in db)):
        return None
    shared = [p for p in a if p in b]
    direction = cross(na, nb)
    if direction == (0, 0, 0):
        if any(da) or any(db):
            return None
        skip = max(range(3), key=lambda k: abs(na[k]))
        keep = [k for k in range(3) if k != skip]
        projected_a = [tuple(p[k] for k in keep) for p in a]
        projected_b = [tuple(p[k] for k in keep) for p in b]
        polygon = coplanar_clip(projected_a, projected_b)
        if not polygon:
            return None
        area2 = sum(cross2(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon)))
        if area2:
            return {"kind": "exact_coplanar_area_overlap", "projected_area_mm2": float(abs(area2) / (2 * scale * scale)), "shared_vertices": len(shared)}
        projected_shared = [tuple(p[k] for k in keep) for p in shared]
        if not all(contained(p, projected_shared) for p in polygon):
            return {"kind": "exact_coplanar_nonadjacent_contact", "shared_vertices": len(shared), "projected_contact_points_mm": [[float(v / scale) for v in p] for p in polygon]}
        return None
    pa, pb = cut_plane(a, da), cut_plane(b, db)
    if not pa or not pb:
        return None
    axis = max(range(3), key=lambda k: abs(direction[k]))
    lo = max(min(p[axis] for p in pa), min(p[axis] for p in pb))
    hi = min(max(p[axis] for p in pa), max(p[axis] for p in pb))
    if lo > hi:
        return None
    anchor = pa[0]
    points = [tuple(anchor[k] + F(v - anchor[axis], direction[axis]) * direction[k] for k in range(3)) for v in (lo, hi)]
    if not all(contained(p, shared) for p in points):
        return {"kind": "exact_noncoplanar_intersection", "shared_vertices": len(shared), "points_mm": [[float(v / scale) for v in p] for p in points], "segment_length_mm": float(np.linalg.norm(np.array([float(v / scale) for v in sub(points[1], points[0])])))}
    return None


def test_controls():
    original = initial.triangle_pair
    def wrapper(a, b, _eps):
        ab, scale = integer_coordinates([a, b])
        return exact_pair(ab[0], ab[1], scale)
    initial.triangle_pair = wrapper
    try:
        result = initial.self_test(0)
    finally:
        initial.triangle_pair = original
    result["method"] = "The same 12 synthetic crossing, coplanar, duplicate, nonadjacent contact, normal adjacency and disjoint cases as the initial screen, evaluated by exact rational predicates."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stl", type=Path, default=HERE.parent / "model.stl")
    parser.add_argument("--initial-report", type=Path, default=HERE / "extended-checks-initial.json")
    parser.add_argument("--output", type=Path, default=HERE / "exact-intersections.json")
    args = parser.parse_args()
    started = time.monotonic()
    controls = test_controls()
    if not controls["passed"]:
        raise RuntimeError("Exact intersection controls failed; STL run aborted.")
    raw, _, tri, _, _ = initial.load_raw(args.stl)
    integer_tri, scale = integer_coordinates(tri)
    # Exact AABB integer comparisons, no epsilon expansion or exclusion.
    bounds = [(tuple(min(p[k] for p in t) for k in range(3)), tuple(max(p[k] for p in t) for k in range(3))) for t in integer_tri]
    active, findings, candidates = [], [], 0
    for i in sorted(range(len(tri)), key=lambda j: (bounds[j][0][0], j)):
        lo, hi = bounds[i]
        active = [j for j in active if bounds[j][1][0] >= lo[0]]
        for j in active:
            if any(bounds[j][1][k] < lo[k] or hi[k] < bounds[j][0][k] for k in (1, 2)):
                continue
            candidates += 1
            detail = exact_pair(integer_tri[i], integer_tri[j], scale)
            if detail:
                findings.append({"faces": [j, i], **detail})
        active.append(i)
    adjudicated = []
    initial_report_sha = None
    if args.initial_report.is_file():
        earlier_raw = args.initial_report.read_bytes()
        earlier = json.loads(earlier_raw)
        if earlier["stl_sha256"] != hashlib.sha256(raw).hexdigest():
            raise ValueError("Initial report and supplemental input STL hashes differ.")
        initial_report_sha = hashlib.sha256(earlier_raw).hexdigest()
        for row in earlier["self_intersection_screen"]["findings"]:
            i, j = row["faces"]
            result = exact_pair(integer_tri[i], integer_tri[j], scale)
            adjudicated.append({"faces": [i, j], "initial_kind": row["kind"], "exact_invalid_intersection": result is not None, "exact_detail": result})
    report = {"schema_version": 1, "purpose": "Supplemental exact-rational evidence; preserved initial report is not modified.", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "initial_screen_script_sha256": hashlib.sha256((HERE / "extended_checks.py").read_bytes()).hexdigest(), "initial_report_sha256": initial_report_sha, "stl_sha256": hashlib.sha256(raw).hexdigest(), "stl_bytes": len(raw), "runtime": {"python": platform.python_version(), "numpy": np.__version__}, "coordinate_representation": "Saved float32 values promoted without change and represented as Python integers on a common power-of-two scale; intersection coordinates use fractions.Fraction.", "integer_units_per_mm": scale, "controls": controls, "all_aabb_overlapping_pairs_checked_including_adjacent": candidates, "invalid_intersection_count": len(findings), "findings": findings, "exact_triangle_contact_check_passed": not findings, "initial_findings_adjudicated": adjudicated, "initial_findings_confirmed": sum(r["exact_invalid_intersection"] for r in adjudicated), "initial_report_retained": args.initial_report.name, "elapsed_seconds": time.monotonic() - started, "formal_slicer_run": False, "physical_print_test": False, "limitations": ["The stated check concerns stored triangles and exact shared-vertex/shared-edge contact, subject to implementation correctness; it does not verify architectural accuracy.", "It does not make the initial sampled thickness or support warnings disappear and does not prove minimum thickness, support feasibility or printability.", "Synthetic controls exercise important cases but are not a formal verification of the implementation."]}
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("stl_sha256", "all_aabb_overlapping_pairs_checked_including_adjacent", "invalid_intersection_count", "exact_triangle_contact_check_passed", "initial_findings_confirmed", "elapsed_seconds")}, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
