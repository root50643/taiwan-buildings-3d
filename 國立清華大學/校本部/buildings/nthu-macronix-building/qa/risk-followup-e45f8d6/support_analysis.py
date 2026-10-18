"""Derived support measurements of an unchanged original overhang report.

python support_analysis.py --stl input-original.stl \
  --input-report ../extended-checks-initial.json --output support_analysis.json

Does not modify/reflag/resample the original overhang or thin-feature screens.
The 573 original face centroids, areas, vertical gaps and face IDs are reused.
Additional horizontal sections locate backing solid and point-access routes;
they are measurements, not new overhang flags, support generation or slicing.
Input STL/report hashes must match. For a new STL supply its corresponding
unchanged screen report; face IDs from a different mesh may never be reused.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import numpy as np
import trimesh
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

HERE = Path(__file__).resolve().parent
QA = HERE.parent
# Reuse the already-reviewed contour reconstruction without changing its
# 0.0001 mm endpoint tolerance, silently repairing polygons, or writing pycache.
namespace = {"__name__": "support_section_dependency", "__file__": str(QA / "geometry_delta.py")}
exec(compile((QA / "geometry_delta.py").read_text(encoding="utf-8"), str(QA / "geometry_delta.py"), "exec"), namespace)
section = namespace["section"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group_for(row):
    x, y, z = row["centroid_mm"]
    if y > 5:
        if abs(z - 62) < .001:
            return "rear_roof_eaves"
        if min(abs(z - h) for h in (17, 28, 39, 50)) < .001:
            return "rear_window_band_lower_lips"
        return "rear_window_band_heads"
    if x >= 33.5:
        return "entrance_arcade_head" if z < 14 else "entrance_right_fins_window_eaves"
    if x >= 16:
        return "entrance_connector_grille"
    if z >= 53.299:
        return "front_clerestory_cap" if z > 54 else "front_clerestory_slot_head"
    if z >= 39:
        return "front_sloped_roof_eaves"
    if abs(z - 28) < .001 and y < -30:
        return "front_stair_landing"
    return "front_oval_window_heads"


def directions_for(group, point):
    angles = list(np.arange(0, 360, 45, dtype=float))
    if group.startswith("rear_"):
        rotation = -14 if point[0] < 0 else 14
        angles = [rotation - 90] + angles
    if group.startswith("front_"):
        radial = math.degrees(math.atan2(point[1] + 24, point[0] + 22))
        angles = [radial, -90, 90] + angles
    if group.startswith("entrance_"):
        angles = [-90] + angles
    return [(float(a), np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])) for a in dict.fromkeys(angles)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stl", type=Path, default=HERE / "input-original.stl")
    parser.add_argument("--input-report", type=Path, default=QA / "extended-checks-initial.json")
    parser.add_argument("--output", type=Path, default=HERE / "support_analysis.json")
    args = parser.parse_args()
    before = sha(args.stl)
    original = json.loads(args.input_report.read_text(encoding="utf-8"))
    if before != original["stl_sha256"]:
        raise ValueError("STL and original report hashes differ; no face-ID transfer is allowed.")
    records = original["overhang_support_screen"]["findings"]
    raw = args.stl.read_bytes()
    rec = np.frombuffer(raw, offset=84, dtype=np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")]))
    tri = rec["v"].astype(float)
    vertices, inverse = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(vertices=vertices, faces=inverse.reshape(-1, 3), process=False)
    cache = {}
    def contour(z):
        key = round(float(z), 10)
        if key not in cache:
            cache[key] = section(mesh, key)
        return cache[key]
    rows = []
    for old in records:
        fi = old["face"]
        center = np.asarray(old["centroid_mm"])
        if not np.allclose(tri[fi].mean(axis=0), center, atol=1e-10):
            raise ValueError(f"Original centroid does not match exact raw face {fi}.")
        group = group_for(old)
        # Roof skin is inclined; its own nearby underside would invalidate a
        # just-below-centroid horizontal support distance. Use the measured
        # solid upper-storey footprint at Z=33.000013 as vertical backing.
        if group == "front_sloped_roof_eaves":
            ref_z, ref_kind = 33.000013, "Upper-storey solid footprint at Z=33.000013; estimates lateral roof cantilever relative to its vertical backing, not structural load capacity."
        elif group == "front_clerestory_cap":
            ref_z, ref_kind = 53.8, "Actual clerestory solid below cap, above slot head."
        else:
            ref_z, ref_kind = center[2] - .000013, "Actual horizontal solid immediately below original downward-face centroid."
        info, region = contour(ref_z)
        p = Point(center[:2])
        distance, nearest = None, None
        if region is not None:
            distance = float(p.distance(region))
            nearest = list(nearest_points(p, region)[1].coords[0])
        gap = old["vertical_air_gap_mm"]
        mid_z = center[2] - gap / 2 if gap is not None else center[2] - .5
        access_info, air_region = contour(mid_z)
        access = []
        for angle, direction in directions_for(group, center):
            result = {"xy_direction_deg": angle, "xy_direction": direction.tolist()}
            if air_region is None:
                result.update({"available": False, "reason": access_info["failure"]})
            else:
                origin_inside = bool(air_region.contains(p))
                ray = LineString([center[:2], center[:2] + 500 * direction])
                hit = ray.intersection(air_region)
                result.update({"available": True, "origin_inside_solid": origin_inside, "point_route_reaches_exterior_without_solid": bool(not origin_inside and hit.is_empty), "first_horizontal_obstacle_distance_mm": None if hit.is_empty else float(p.distance(hit))})
            access.append(result)
        below_fi = old["first_surface_below_face"]
        rows.append({"face": fi, "component_group": group, "original_centroid_mm": old["centroid_mm"], "original_area_mm2": old["area_mm2"], "original_vertical_gap_mm": gap, "original_first_surface_below_face": below_fi, "first_surface_below_contact_mm": [center[0], center[1], center[2] - gap] if gap is not None else None, "first_surface_below_triangle_bounds_mm": [tri[below_fi].min(axis=0).tolist(), tri[below_fi].max(axis=0).tolist()] if below_fi is not None else None, "downward_triangle_bounds_mm": [tri[fi].min(axis=0).tolist(), tri[fi].max(axis=0).tolist()], "horizontal_support_reference_z_mm": float(ref_z), "horizontal_support_reference": ref_kind, "horizontal_backing_distance_at_original_centroid_mm": distance, "nearest_reference_solid_xy_mm": nearest, "point_route_section_z_mm": float(mid_z), "point_routes": access, "some_tested_straight_point_route_to_exterior": any(a.get("point_route_reaches_exterior_without_solid", False) for a in access)})
    groups = {}
    for name in sorted({r["component_group"] for r in rows}):
        selected = [r for r in rows if r["component_group"] == name]
        face_ids = [r["face"] for r in selected]
        all_tri = tri[face_ids]
        distances = [r["horizontal_backing_distance_at_original_centroid_mm"] for r in selected if r["horizontal_backing_distance_at_original_centroid_mm"] is not None]
        gaps = [r["original_vertical_gap_mm"] for r in selected if r["original_vertical_gap_mm"] is not None]
        groups[name] = {"original_face_count": len(selected), "original_face_ids": face_ids, "original_area_mm2": float(sum(r["original_area_mm2"] for r in selected)), "bounds_mm": [all_tri.min(axis=(0, 1)).tolist(), all_tri.max(axis=(0, 1)).tolist()], "original_centroid_vertical_gap_range_mm": [min(gaps), max(gaps)] if gaps else None, "centroid_horizontal_backing_distance_range_mm": [min(distances), max(distances)] if distances else None, "centroid_horizontal_backing_distance_p95_mm": float(np.percentile(distances, 95)) if distances else None, "point_route_to_exterior_found_count": sum(r["some_tested_straight_point_route_to_exterior"] for r in selected), "point_route_no_straight_exit_found_count": sum(not r["some_tested_straight_point_route_to_exterior"] for r in selected)}
    after = sha(args.stl)
    if before != after:
        raise RuntimeError("Input STL changed during measurement; report aborted.")
    report = {"schema_version": 2, "purpose": "Derived measurements of the supplied unchanged overhang findings; input thresholds, samples, flags and reports remain unchanged.", "stl_sha256_before": before, "stl_sha256_after": after, "input_report_sha256": sha(args.input_report), "script_sha256": sha(Path(__file__)), "section_dependency_sha256": sha(QA / "geometry_delta.py"), "input_face_count": len(tri), "original_overhang_face_count": len(records), "assigned_face_count": len(rows), "original_area_sum_mm2": sum(r["area_mm2"] for r in records), "input_thin_flag_count_unmodified": len(original["normal_chord_thickness_screen"]["flagged_samples"]), "input_thin_screen_threshold_mm_unmodified": original["normal_chord_thickness_screen"]["screen_width_mm"], "support_generation_performed": False, "formal_slicer_run": False, "physical_print_test": False, "groups": groups, "section_measurements": [{"z_mm": z, **data[0]} for z, data in sorted(cache.items())], "section_failure_count": sum(data[1] is None for data in cache.values()), "face_measurements": rows, "limitations": ["Component groups use explicit spatial rules documented in group_for; boundary faces belong to exactly one group but labels are semantic estimates.", "Lateral backing distance is derived at the original face centroid. It is not the maximum geometric cantilever or a structural load/support calculation.", "Roof backing at Z=33.000013 is a vertical support-footprint reference, avoiding a sloped skin counting itself as nearby support.", "A free mid-gap horizontal point ray establishes only a zero-radius straight access route at that height. It does not prove finite tool clearance, extraction of a full support body, or nondestructive removal.", "No automatic support height is inferred from a 59 mm vertical air gap; support strategy depends on short lateral projections, bridging, slicer contact settings and removal access.", "All original thin-ray/layer/overhang warning records remain unchanged; this does not establish printability."]}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"stl_sha256": before, "groups": groups, "section_failure_count": report["section_failure_count"]}, indent=2))


if __name__ == "__main__":
    main()
