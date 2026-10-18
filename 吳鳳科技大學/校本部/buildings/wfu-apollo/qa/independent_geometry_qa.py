"""Independent, conservative mesh QA for a solid low-detail FDM building.

This is geometric screening, not a slicer or a physical print.  XY sections are
sampled through the actual mesh at layer midpoints.  Layer support is compared
with the previous section buffered by layer_height * tan(overhang_angle).
The thin-feature screen checks whether erosion by half the stated feature
width removes or disconnects each section's core; it cannot prove arbitrary
3-D minimum wall thickness.  Sharp roof tips and convex corners need judgment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import shapely
from shapely.geometry import GeometryCollection, LineString, Point, Polygon
from shapely.ops import unary_union
import trimesh


def polygon_count(g):
    if g.is_empty:
        return 0
    if g.geom_type == "Polygon":
        return 1
    if hasattr(g, "geoms"):
        return sum(polygon_count(x) for x in g.geoms)
    return 0


def polygon_parts(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    if hasattr(g, "geoms"):
        return [p for x in g.geoms for p in polygon_parts(x)]
    return []


def section_xy(mesh, z):
    segments = trimesh.intersections.mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
    if not len(segments):
        return GeometryCollection(), []
    geometry = GeometryCollection()
    issues = []
    points = {}
    graph = {}
    edges = []
    for segment in segments:
        keys = [tuple(np.round(p[:2], 7)) for p in segment]
        if keys[0] == keys[1]:
            continue
        edge_id = len(edges)
        edges.append(keys)
        for key, p in zip(keys, segment):
            points[key] = p
            graph.setdefault(key, []).append(edge_id)
    bad_degrees = [key for key, es in graph.items() if len(es) != 2]
    if bad_degrees:
        issues.append(f"noncycle_section_vertices:{len(bad_degrees)}")
    unused = set(range(len(edges)))
    curves = []
    while unused:
        edge_id = min(unused)
        start = edges[edge_id][0]
        current = start
        curve = [points[start]]
        while edge_id in unused:
            unused.remove(edge_id)
            a, b = edges[edge_id]
            current = b if current == a else a
            curve.append(points[current])
            if current == start:
                break
            next_edges = [e for e in graph[current] if e in unused]
            if not next_edges:
                break
            edge_id = min(next_edges)
        curves.append(curve)
    # Every nested closed ring toggles material occupancy.  XOR preserves
    # holes and disconnected islands without depending on optional rtree.
    for i, curve in enumerate(curves):
        curve = np.asarray(curve)
        if len(curve) < 4 or not np.allclose(curve[0], curve[-1], atol=1e-7):
            issues.append(f"open_or_short_loop:{i}")
            continue
        p = Polygon(curve[:, :2])
        if not p.is_valid:
            issues.append(f"invalid_loop:{i}")
            p = shapely.make_valid(p)
        geometry = geometry.symmetric_difference(p)
    if not geometry.is_valid:
        issues.append("invalid_combined_section")
    return geometry, issues


def topology(mesh):
    _, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    normalized = np.sort(mesh.faces, axis=1)
    unique_faces = len(np.unique(normalized, axis=0))
    edge_faces = {}
    for face_id, face in enumerate(mesh.faces):
        for a, b in [(face[0], face[1]), (face[1], face[2]), (face[2], face[0])]:
            edge_faces.setdefault(tuple(sorted((int(a), int(b)))), []).append(face_id)
    adjacent = [[] for _ in mesh.faces]
    for fs in edge_faces.values():
        for f in fs:
            adjacent[f].extend(other for other in fs if other != f)
    unused_faces = set(range(len(mesh.faces)))
    components = []
    while unused_faces:
        pending = [min(unused_faces)]
        members = []
        while pending:
            f = pending.pop()
            if f in unused_faces:
                unused_faces.remove(f)
                members.append(f)
                pending.extend(adjacent[f])
        components.append(trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[members], process=False))
    vertex_link_failures = []
    for v in range(len(mesh.vertices)):
        incident = mesh.faces[np.any(mesh.faces == v, axis=1)]
        link = {}
        for face in incident:
            others = [int(x) for x in face if x != v]
            if len(others) != 2:
                continue
            a, b = others
            link.setdefault(a, []).append(b)
            link.setdefault(b, []).append(a)
        seen = set()
        pending = [next(iter(link))] if link else []
        while pending:
            n = pending.pop()
            if n not in seen:
                seen.add(n)
                pending.extend(link[n])
        if not link or len(seen) != len(link) or any(len(x) != 2 for x in link.values()):
            vertex_link_failures.append(v)
    result = {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bounds_mm": mesh.bounds.tolist(),
        "extents_mm": mesh.extents.tolist(),
        "surface_area_mm2": float(mesh.area),
        "signed_volume_mm3": float(mesh.volume),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
        "degenerate_triangles": int(np.count_nonzero(mesh.area_faces <= 1e-10)),
        "duplicate_triangles": int(len(mesh.faces) - unique_faces),
        "nonmanifold_vertex_links": len(vertex_link_failures),
        "nonmanifold_vertex_indices": vertex_link_failures,
        "connected_components": int(len(components)),
        "component_signed_volumes_mm3": [float(c.volume) for c in components],
        "euler_number": int(mesh.euler_number),
    }
    result["passes_basic_solid_checks"] = bool(
        result["watertight"] and result["winding_consistent"]
        and result["is_volume"] and result["signed_volume_mm3"] > 0
        and result["connected_components"] == 1
        and result["boundary_edges"] == 0
        and result["nonmanifold_edges"] == 0
        and result["degenerate_triangles"] == 0
        and result["duplicate_triangles"] == 0
        and result["nonmanifold_vertex_links"] == 0
    )
    return result


def self_intersections(mesh, tol=1e-6):
    """Numerically inspect every AABB-overlapping triangle pair.

    Plane clipping gives noncoplanar intersection intervals.  Coplanar pairs
    use exact 2-D polygon intersection in Shapely's floating-point kernel.
    Contacts confined to mesh-index shared vertices/edges are permitted.
    """
    triangles = mesh.triangles
    bounds_lo, bounds_hi = triangles.min(axis=1), triangles.max(axis=1)
    normals = mesh.face_normals
    flagged = []
    candidate_count = 0

    def plane_cut(triangle, origin, normal):
        ds = (triangle - origin) @ normal
        if np.all(ds > tol) or np.all(ds < -tol):
            return []
        points = []
        for k in range(3):
            a, b = triangle[k], triangle[(k + 1) % 3]
            da, db = ds[k], ds[(k + 1) % 3]
            if abs(da) <= tol:
                points.append(a)
            if (da < -tol and db > tol) or (da > tol and db < -tol):
                points.append(a + (b - a) * da / (da - db))
        return points

    def expected_contact(points, shared_points):
        if len(shared_points) == 0:
            return False
        if len(shared_points) == 1:
            return all(np.linalg.norm(p - shared_points[0]) <= tol * 4 for p in points)
        a, b = shared_points[:2]
        ab = b - a
        scale = ab @ ab
        for p in points:
            t = np.clip((p - a) @ ab / scale, 0, 1)
            if np.linalg.norm(p - (a + t * ab)) > tol * 4:
                return False
        return True

    for i in range(len(triangles)):
        for j in range(i + 1, len(triangles)):
            if np.any(bounds_hi[i] < bounds_lo[j] - tol) or np.any(bounds_hi[j] < bounds_lo[i] - tol):
                continue
            candidate_count += 1
            a, b = triangles[i], triangles[j]
            na, nb = normals[i], normals[j]
            shared = np.intersect1d(mesh.faces[i], mesh.faces[j])
            shared_points = mesh.vertices[shared]
            direction = np.cross(na, nb)
            norm = np.linalg.norm(direction)
            if norm <= 1e-9:
                if np.max(np.abs((b - a[0]) @ na)) > tol:
                    continue
                keep = [k for k in range(3) if k != int(np.argmax(np.abs(na)))]
                intersection = Polygon(a[:, keep]).intersection(Polygon(b[:, keep]))
                if intersection.is_empty:
                    continue
                if len(shared) == 0:
                    bad = True
                else:
                    xy = shared_points[:, keep]
                    contact = Point(xy[0]) if len(xy) == 1 else LineString(xy[:2])
                    bad = not intersection.difference(contact.buffer(tol * 4)).is_empty
                if bad:
                    flagged.append({"faces": [i, j], "kind": "coplanar_contact_or_overlap", "intersection_area_mm2": float(intersection.area)})
                continue
            direction /= norm
            cut_a = plane_cut(a, b[0], nb)
            cut_b = plane_cut(b, a[0], na)
            if not cut_a or not cut_b:
                continue
            values_a = np.asarray(cut_a) @ direction
            values_b = np.asarray(cut_b) @ direction
            start = max(float(min(values_a)), float(min(values_b)))
            end = min(float(max(values_a)), float(max(values_b)))
            if end < start - tol:
                continue
            origin = cut_a[0]
            points = [origin + (t - origin @ direction) * direction for t in [start, end]]
            if not expected_contact(points, shared_points):
                flagged.append({"faces": [i, j], "kind": "noncoplanar_contact_or_crossing", "intersection_length_mm": max(0, end - start)})
    return {
        "method": "All triangle pairs with overlapping AABBs; noncoplanar plane-cut intervals and coplanar 2-D polygon intersections. Shared mesh edge/vertex contact is permitted.",
        "tolerance_mm": tol,
        "total_triangle_pairs": len(triangles) * (len(triangles) - 1) // 2,
        "aabb_candidate_pairs_checked": candidate_count,
        "unexpected_contacts_or_intersections": flagged,
        "passes_numerical_pair_screen": not flagged,
        "limitation": "Floating-point geometric screening, not a formal exact-arithmetic certificate.",
    }


def sections(mesh, layer_height, angle, feature_width):
    bottom, top = mesh.bounds[:, 2]
    zs = np.arange(bottom + layer_height / 2, top, layer_height)
    reach = layer_height * math.tan(math.radians(angle))
    previous = None
    rows = []
    for z in zs:
        section, issues = section_xy(mesh, float(z))
        parts = polygon_parts(section)
        core = section.buffer(-feature_width / 2, join_style="mitre")
        core_count = polygon_count(core)
        # Tiny naked corners are not treated as thin walls.  Instead preserve
        # erosion status and change in core connectivity for review.
        row = {
            "z_mm": round(float(z), 6),
            "area_mm2": float(section.area),
            "components": len(parts),
            "smallest_component_area_mm2": min((float(p.area) for p in parts), default=0),
            "feature_core_area_mm2": float(core.area),
            "feature_core_components": core_count,
            "core_vanished": bool(not section.is_empty and core.is_empty),
            "core_split": bool(core_count > len(parts)),
            "section_issues": issues,
        }
        if previous is not None:
            unsupported = section.difference(previous.buffer(reach, join_style="round"))
            # Directed distance samples all upper-section boundaries at <=
            # 0.1 mm spacing.  Max distance is approximate (error <=0.05 mm).
            boundary = shapely.segmentize(section.boundary, max_segment_length=0.1)
            coords = shapely.get_coordinates(boundary)
            distances = shapely.distance(shapely.points(coords), previous) if len(coords) else np.array([0])
            row["outside_support_envelope_area_mm2"] = float(unsupported.area)
            row["sampled_max_upper_boundary_distance_to_lower_mm"] = float(np.max(distances))
        rows.append(row)
        previous = section
    support_rows = [r for r in rows if r.get("outside_support_envelope_area_mm2", 0) > 0.01]
    issue_rows = [r for r in rows if r["section_issues"]]
    return {
        "method": "Actual horizontal mesh intersections at layer midpoints; 2-D material parity; previous-layer buffered support envelope.",
        "layer_height_mm": layer_height,
        "support_angle_from_vertical_deg": angle,
        "per_layer_horizontal_reach_mm": reach,
        "support_area_reporting_tolerance_mm2": 0.01,
        "first_section_treated_as_build_plate_supported": True,
        "feature_screen_width_mm": feature_width,
        "feature_screen_method": "Erode each material section by half feature width; report empty or disconnected core. No universal 3-D thickness guarantee.",
        "boundary_distance_sampling_interval_max_mm": 0.1,
        "boundary_distance_sampling_error_bound_mm": 0.05,
        "section_count": len(rows),
        "invalid_or_open_section_count": len(issue_rows),
        "max_section_components": max((r["components"] for r in rows), default=0),
        "unsupported_envelope_layer_count": len(support_rows),
        "worst_unsupported_envelope_area_mm2": max((r.get("outside_support_envelope_area_mm2", 0) for r in rows), default=0),
        "sampled_max_boundary_expansion_mm": max((r.get("sampled_max_upper_boundary_distance_to_lower_mm", 0) for r in rows), default=0),
        "vanished_core_layers": [r["z_mm"] for r in rows if r["core_vanished"]],
        "split_core_layers": [r["z_mm"] for r in rows if r["core_split"]],
        "rows": rows,
        "limitations": [
            "Sampled sections can miss features narrower in Z than the layer spacing.",
            "Support test is a 45-degree style geometric envelope, not extrusion or bridge simulation.",
            "Erosion detects missing/disconnected section cores, but attached thin protrusions may survive this screen unnoticed.",
            "No nozzle path generation, adhesion, cooling, material shrinkage or physical print tested.",
        ],
    }


def controls(mesh):
    missing_face = mesh.copy()
    missing_face.update_faces(np.arange(len(missing_face.faces)) != 0)
    missing_face.remove_unreferenced_vertices()
    flipped = mesh.copy()
    flipped.faces = flipped.faces[:, ::-1]
    detached = trimesh.creation.box(extents=[1, 1, 1])
    detached.apply_translation(mesh.bounds[1] + [3, 3, 3])
    disconnected = trimesh.util.concatenate([mesh, detached])
    specimens = {"missing_triangle": missing_face, "all_faces_reversed": flipped, "detached_cube": disconnected}
    result = {}
    for name, sample in specimens.items():
        r = topology(sample)
        r["negative_control_detected"] = not r["passes_basic_solid_checks"]
        result[name] = r
    return result


def geometric_controls():
    cube = trimesh.creation.box(extents=[2, 2, 2])
    overlapping_cube = cube.copy()
    overlapping_cube.apply_translation([0.5, 0.5, 0.5])
    overlapping = trimesh.util.concatenate([cube, overlapping_cube])
    touching_cube = cube.copy()
    touching_cube.apply_translation([2, 2, 2])
    touching = trimesh.util.concatenate([cube, touching_cube])
    touching.merge_vertices()
    clean_result = self_intersections(cube)
    crossing_result = self_intersections(overlapping)
    vertex_result = topology(touching)
    return {
        "clean_cube_has_no_unexpected_intersections": clean_result["passes_numerical_pair_screen"],
        "overlapping_cubes_crossing_pairs_detected": len(crossing_result["unexpected_contacts_or_intersections"]),
        "overlapping_cubes_negative_control_detected": not crossing_result["passes_numerical_pair_screen"],
        "vertex_touching_cubes_nonmanifold_vertex_links": vertex_result["nonmanifold_vertex_links"],
        "vertex_touching_cubes_negative_control_detected": vertex_result["nonmanifold_vertex_links"] > 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--layer-height", type=float, default=0.2)
    parser.add_argument("--overhang-angle", type=float, default=45)
    parser.add_argument("--feature-width", type=float, default=0.8)
    parser.add_argument("--negative-controls", action="store_true")
    args = parser.parse_args()
    mesh = trimesh.load_mesh(args.mesh, process=True)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    result = {
        "input_file": args.mesh.name,
        "input_identification": "Filename and SHA-256; local workstation paths intentionally omitted.",
        "sha256": hashlib.sha256(args.mesh.read_bytes()).hexdigest(),
        "versions": {"python": sys.version, "trimesh": trimesh.__version__, "numpy": np.__version__, "shapely": shapely.__version__},
        "topology": topology(mesh),
        "self_intersections": self_intersections(mesh),
        "sections": sections(mesh, args.layer_height, args.overhang_angle, args.feature_width),
    }
    if args.negative_controls:
        result["negative_controls"] = controls(mesh)
        result["geometric_controls"] = geometric_controls()
    passed = (result["topology"]["passes_basic_solid_checks"]
              and result["self_intersections"]["passes_numerical_pair_screen"]
              and result["sections"]["invalid_or_open_section_count"] == 0
              and result["sections"]["unsupported_envelope_layer_count"] == 0)
    if args.negative_controls:
        passed = passed and all(r["negative_control_detected"] for r in result["negative_controls"].values())
        passed = passed and all(v for k, v in result["geometric_controls"].items() if k.endswith("detected") or k.startswith("clean_cube"))
    result["passes_bounded_geometry_screen"] = bool(passed)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"json": str(args.json.resolve()), "topology": result["topology"], "self_intersections": result["self_intersections"], "sections": {k:v for k,v in result["sections"].items() if k != "rows"}}
    if "negative_controls" in result:
        summary["negative_controls_detected"] = {k:v["negative_control_detected"] for k,v in result["negative_controls"].items()}
        summary["geometric_controls"] = result["geometric_controls"]
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
