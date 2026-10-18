"""Read-only full-line and section measurements of the R2 cap and shallow slot.
Run with --stl PATH --output NEW_PATH. Never overwrites an existing output.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
import trimesh
from shapely.geometry import box, Point

HERE = Path(__file__).resolve().parent
ns = {"__name__": "section_dependency", "__file__": str(HERE.parent / "geometry_delta.py")}
exec(compile((HERE.parent / "geometry_delta.py").read_text(encoding="utf-8"), ns["__file__"], "exec"), ns)


def intersections(tri, origin, direction):
    o, d = np.asarray(origin, dtype=float), np.asarray(direction, dtype=float)
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    p = np.cross(np.broadcast_to(d, e2.shape), e2)
    det = np.einsum("ij,ij->i", e1, p)
    good = np.abs(det) > 1e-12
    inv = np.zeros_like(det)
    inv[good] = 1 / det[good]
    tv = o - tri[:, 0]
    u = np.einsum("ij,ij->i", tv, p) * inv
    q = np.cross(tv, e1)
    v = q @ d * inv
    t = np.einsum("ij,ij->i", e2, q) * inv
    good &= (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9)
    unique = []
    for fi in np.flatnonzero(good)[np.argsort(t[good])]:
        value = float(t[fi])
        if unique and abs(value - unique[-1]["parameter_mm"]) < 1e-5:
            unique[-1]["faces"].append(int(fi))
        else:
            unique.append({"parameter_mm": value, "point_mm": (o + value * d).tolist(), "faces": [int(fi)]})
    return {"origin_mm": list(origin), "direction": list(direction), "unique_crossings": unique, "even_crossing_count": len(unique) % 2 == 0, "solid_parameter_intervals_mm": [[unique[i]["parameter_mm"], unique[i + 1]["parameter_mm"]] for i in range(0, len(unique) - 1, 2)]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stl", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError("Existing evidence will not be overwritten.")
    raw = args.stl.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    rec = np.frombuffer(raw, offset=84, dtype=np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")]))
    tri = rec["v"].astype(float)
    vertices, inv = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(vertices=vertices, faces=inv.reshape(-1, 3), process=False)
    rows = {}
    def line(name, o, d):
        rows[name] = intersections(tri, o, d)
    for z in (53.8, 54.7):
        line(f"center_y_z_{z}", [-22, 0, z], [0, 1, 0])
        line(f"side_x_z_{z}", [0, -10.4, z], [1, 0, 0])
    for x in (-36.9, -30, -22, -14, -7.1, -38, -6):
        line(f"slot_depth_x_{x}", [x, 0, 52.05], [0, 1, 0])
    for y in (-10.49, -10.25, -10.01):
        line(f"slot_width_y_{y}", [0, y, 52.05], [1, 0, 0])
        for x in (-36.9, -22, -7.1):
            line(f"slot_height_x_{x}_y_{y}", [x, y, 0], [0, 0, 1])
    # Exposed cap front, back and side underside access. Full rays retain
    # foreground/background obstacles rather than claiming infinite clearance.
    for x, y in ((-22, -11.49), (-22, -11), (-22, -10.51), (-39.5, -10.4), (-4.5, -10.4), (-22, -5), (-30, -5.9)):
        line(f"cap_vertical_x_{x}_y_{y}", [x, y, 0], [0, 0, 1])
    for name, o, d in (
        ("slot_outward_minus_y", [-22, -10.25, 52.05], [0, -1, 0]),
        ("front_cap_outward_minus_y", [-22, -11, 53.8], [0, -1, 0]),
        ("left_cap_outward_minus_x", [-39.5, -10.4, 53.8], [-1, 0, 0]),
        ("right_cap_outward_plus_x", [-4.5, -10.4, 53.8], [1, 0, 0]),
        ("rear_cap_outward_plus_y", [-22, -5, 53.8], [0, 1, 0]),
    ):
        line(name, o, d)
    sections = {}
    regions = {}
    for name, z in (("backing", 53.8), ("cap", 54.7)):
        info, region = ns["section"](mesh, z)
        sections[name] = info
        regions[name] = None if region is None else region.intersection(box(-41, -12, -3, -3))
    cap_distance = None
    if all(regions[k] is not None for k in ("backing", "cap")):
        b, c = regions["backing"], regions["cap"]
        # These clipped model shapes are convex; for distance to a convex body,
        # the maximum over a convex polygon occurs at one of its vertices.
        points = list(c.exterior.coords) if c.geom_type == "Polygon" else []
        distances = [(float(Point(v).distance(b)), list(v)) for v in points]
        body_center_rear = max(p["point_mm"][1] for p in rows["center_y_z_53.8"]["unique_crossings"] if -15 < p["point_mm"][1] < 0)
        cap_center_rear = max(p["point_mm"][1] for p in rows["center_y_z_54.7"]["unique_crossings"] if -15 < p["point_mm"][1] < 0)
        cap_distance = {"backing_bounds_xy_mm": list(b.bounds), "cap_bounds_xy_mm": list(c.bounds), "backing_convex_area_residual_mm2": float(b.convex_hull.area - b.area), "cap_convex_area_residual_mm2": float(c.convex_hull.area - c.area), "cap_outline_vertex_maximum_distance_to_backing_mm": max(distances)[0], "maximum_distance_vertex_xy_mm": max(distances)[1], "front_axis_projection_mm": b.bounds[1] - c.bounds[1], "left_axis_projection_mm": b.bounds[0] - c.bounds[0], "right_axis_projection_mm": c.bounds[2] - b.bounds[2], "center_rear_axis_projection_mm": cap_center_rear - body_center_rear, "rear_center_projection_note": "Measured from center_y_z_53.8 and center_y_z_54.7 full-line crossings; curved side differences are not uniform Y offsets."}
    report = {"stl_sha256": h, "stl_sha256_after": hashlib.sha256(args.stl.read_bytes()).hexdigest(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "method": "Exact saved STL triangles; brute-force full-line Moller-Trumbore, signed intersections, duplicate crossings merged at 0.00001 mm; even crossings paired into material intervals. Horizontal contours use existing geometry_delta.section without repair.", "line_count": len(rows), "odd_crossing_line_count": sum(not r["even_crossing_count"] for r in rows.values()), "lines": rows, "sections": sections, "cap_projection": cap_distance, "formal_slicer_run": False, "physical_print_test": False, "support_generation_performed": False, "limitations": ["Representative full-lines demonstrate geometric access and aperture dimensions, not the global minimum tool clearance or actual support removal success.", "1 mm cap projection along an axis does not limit front/side corner diagonal distance to 1 mm; the reported polygon-to-backing distance preserves that distinction.", "The new 0.5 mm deep recess is 2.5 mm high and 30 mm wide only where measured; fabrication tolerances and tool shape are not modeled.", "Routes start in air and describe point translations. A complete support body must be detached and fit the opening, which no slicer/tool trial has verified."]}
    if report["stl_sha256_after"] != h:
        raise RuntimeError("STL changed during measurement.")
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"sha": h, "line_count": len(rows), "odd": report["odd_crossing_line_count"], "cap_projection": cap_distance}, indent=2))


if __name__ == "__main__":
    main()
