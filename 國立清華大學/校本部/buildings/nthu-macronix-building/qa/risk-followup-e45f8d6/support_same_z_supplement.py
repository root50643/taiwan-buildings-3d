"""Independent Manifold.slice at the *same failed Z*, preserving original nulls.
Requires --stl --report --output; refuses overwrites and STL/report mismatch.
No original reports, coordinates, sample heights or mesh geometry are edited.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import numpy as np
from manifold3d import Manifold, Mesh64
from shapely.geometry import Point, Polygon


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stl", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError("Existing evidence will not be overwritten.")
    raw = a.stl.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    source = json.loads(a.report.read_text(encoding="utf-8"))
    if sha != source["stl_sha256_before"]:
        raise ValueError("STL/report hash mismatch.")
    rec = np.frombuffer(raw, offset=84, dtype=np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")]))
    tri = rec["v"].astype(float)
    vertices, inverse = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    m = Manifold(Mesh64(np.ascontiguousarray(vertices, dtype=np.float64), np.ascontiguousarray(inverse.reshape(-1, 3), dtype=np.uint64)))
    status = str(m.status())
    if status != "Error.NoError":
        raise ValueError(f"Raw mesh import status {status}; no repair attempted.")
    nulls = [r for r in source["face_measurements"] if r["horizontal_backing_distance_at_original_centroid_mm"] is None]
    sections = []
    rows = []
    for z in sorted({r["horizontal_support_reference_z_mm"] for r in nulls}):
        cross_section = m.slice(z)
        polygons = cross_section.to_polygons()
        region = Polygon()
        valid_each = True
        for coords in polygons:
            poly = Polygon(np.asarray(coords))
            valid_each &= poly.is_valid
            region = region.symmetric_difference(poly)
        if not valid_each or not region.is_valid:
            raise ValueError("Independent slice polygons invalid; no repair attempted.")
        sections.append({"z_mm": z, "same_original_failed_z_without_offset_change": True, "manifold_import_status": status, "contour_count": len(polygons), "all_contour_polygons_valid": valid_each, "even_odd_region_valid": region.is_valid, "region_area_mm2": float(region.area), "region_wkt": region.wkt, "raw_contour_points_xy_mm": [np.asarray(c).tolist() for c in polygons]})
        for r in nulls:
            if r["horizontal_support_reference_z_mm"] != z:
                continue
            point = Point(r["original_centroid_mm"][:2])
            rows.append({"original_face": r["face"], "component_group": r["component_group"], "original_centroid_mm": r["original_centroid_mm"], "original_failed_section_z_mm": z, "original_horizontal_distance_remains_null": True, "independent_slice_point_to_solid_distance_mm": float(point.distance(region))})
    out = {"stl_sha256": sha, "input_report_sha256": hashlib.sha256(a.report.read_bytes()).hexdigest(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "manifold3d_version": importlib.metadata.version("manifold3d"), "method": "Import exact stored float32 STL coordinates promoted to float64 via Mesh64, with only exact-position vertex indexing, require Manifold NoError; slice at each original failed reference Z without changing it; to_polygons contours combined by even-odd symmetric difference in Shapely without repair. Independent of original 0.0001 mm endpoint clustering.", "original_null_count_retained": len(nulls), "supplemental_point_count": len(rows), "sections": sections, "rows": rows, "limitations": ["Manifold and Shapely use floating-point geometry. This is an independent numerical supplement, not an exact-arithmetic proof.", "Original failed contour, degree-1 vertices and 18 null records remain untouched. Supplemental distances are separate evidence at exactly the same original Z.", "Distances to horizontal solid are geometric backing measurements, not support generation, tool clearance or proof of printability."], "support_generation_performed": False, "formal_slicer_run": False, "physical_print_test": False}
    a.output.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"nulls_retained": len(nulls), "points": len(rows), "sections": [{k: v for k, v in s.items() if k not in ("region_wkt", "raw_contour_points_xy_mm")} for s in sections], "distance_range_mm": [min(r["independent_slice_point_to_solid_distance_mm"] for r in rows), max(r["independent_slice_point_to_solid_distance_mm"] for r in rows)]}, indent=2))


if __name__ == "__main__":
    main()
