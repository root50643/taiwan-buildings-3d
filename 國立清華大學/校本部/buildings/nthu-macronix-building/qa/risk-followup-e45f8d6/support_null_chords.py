"""Supplement failed-section backing distances with independent raw-STL lines.
No original null is replaced. Four XY cardinal lines from each original null
centroid at its original reference Z are reported. The nearest measured hit is
an upper bound on nearest 2D material distance, not an exact nearest-distance
replacement. Requires --stl --report --output; never overwrite evidence.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ns = {"__name__": "support_full_line_dependency", "__file__": str(HERE / "support_clerestory_r2.py")}
exec(compile((HERE / "support_clerestory_r2.py").read_text(encoding="utf-8"), ns["__file__"], "exec"), ns)


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
    report = json.loads(a.report.read_text(encoding="utf-8"))
    if sha != report["stl_sha256_before"]:
        raise ValueError("STL/report hash mismatch.")
    rec = np.frombuffer(raw, offset=84, dtype=np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")]))
    tri = rec["v"].astype(float)
    rows = []
    for r in report["face_measurements"]:
        if r["horizontal_backing_distance_at_original_centroid_mm"] is not None:
            continue
        center = r["original_centroid_mm"]
        origin = [center[0], center[1], r["horizontal_support_reference_z_mm"]]
        lines = []
        for d in ([1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]):
            line = ns["intersections"](tri, origin, d)
            hits = [x for x in line["unique_crossings"] if x["parameter_mm"] > 1e-7]
            line["first_positive_hit_mm"] = min((x["parameter_mm"] for x in hits), default=None)
            lines.append(line)
        distances = [x["first_positive_hit_mm"] for x in lines if x["first_positive_hit_mm"] is not None]
        rows.append({"original_face": r["face"], "component_group": r["component_group"], "original_centroid_mm": center, "failed_section_z_mm": r["horizontal_support_reference_z_mm"], "original_horizontal_distance_stays_null": True, "minimum_measured_cardinal_distance_to_material_mm": min(distances) if distances else None, "line_measurements": lines})
    out = {"stl_sha256": sha, "input_report_sha256": hashlib.sha256(a.report.read_bytes()).hexdigest(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "null_count_retained": len(rows), "odd_crossing_line_count": sum(not l["even_crossing_count"] for r in rows for l in r["line_measurements"]), "rows": rows, "interpretation": "Independent cardinal full-line evidence at the same original reference Z. The failed contour and null distances remain unchanged. This bounds nearby backing in four measured directions; it does not replace an exact planar nearest-distance query or prove tool removability.", "formal_slicer_run": False, "physical_print_test": False}
    a.output.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"null_count": len(rows), "odd_lines": out["odd_crossing_line_count"], "distance_range_mm": [min(r["minimum_measured_cardinal_distance_to_material_mm"] for r in rows), max(r["minimum_measured_cardinal_distance_to_material_mm"] for r in rows)]}, indent=2))


if __name__ == "__main__":
    main()
