"""Read-only STL geometry comparison. Does not repair, rebuild, or render meshes.

Usage: python geometry_delta.py --original PATH/TO/original/model.stl
The candidate defaults to ../model.stl; reports are written beside this script.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon

HEIGHTS = [14, 25, 33, 38, 42, 48, 54]
OFFSET = 0.000013
ENDPOINT_TOLERANCE = 0.0001
AREA_TOLERANCE = 0.000001
VOLUME_TOLERANCE = 0.000001


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path, mesh):
    return {
        "file_name": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "face_count": len(mesh.faces),
        "processed_vertex_count": len(mesh.vertices),
        "bounds_mm": mesh.bounds.tolist(),
        "extents_mm": mesh.extents.tolist(),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
    }


def section(mesh, z):
    """Reuse check_layers.py's clustered endpoint/degree-2/even-odd method.

    Exact-plane failures remain failures. No buffer(0), snapping of geometry,
    mesh repair, or silently discarded graph branches is used.
    """
    dz = mesh.vertices[:, 2] - z
    at_plane = np.abs(dz) <= 1e-9
    info = {
        "z_mm": float(z),
        "vertices_on_plane": int(at_plane.sum()),
        "coplanar_face_count": int(at_plane[mesh.faces].all(axis=1).sum()),
        "closed": False,
        "polygon_valid": False,
        "loops": 0,
        "area_mm2": None,
        "failure": None,
    }
    try:
        segments = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z])
        info["segment_count"] = len(segments)
        pts = segments[:, :, :2].reshape(-1, 2)
        parent = list(range(len(pts)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for aa, bb in cKDTree(pts).query_pairs(ENDPOINT_TOLERANCE):
            aa, bb = find(aa), find(bb)
            if aa != bb:
                parent[bb] = aa
        edges = set()
        for i in range(0, len(pts), 2):
            a, b = tuple(pts[find(i)]), tuple(pts[find(i + 1)])
            if a != b:
                edges.add(tuple(sorted((a, b))))
        adjacency = {}
        for a, b in edges:
            adjacency.setdefault(a, set()).add(b)
            adjacency.setdefault(b, set()).add(a)
        histogram = {}
        for neighbours in adjacency.values():
            histogram[str(len(neighbours))] = histogram.get(str(len(neighbours)), 0) + 1
        info["unique_edge_count"] = len(edges)
        info["degree_histogram"] = histogram
        if not edges:
            info["failure"] = "No section edges."
            return info, None
        if not all(len(v) == 2 for v in adjacency.values()):
            info["failure"] = "Section graph has vertices whose degree is not 2."
            return info, None
        unused = set(edges)
        region = Polygon()
        while unused:
            a, b = min(unused)
            start, previous, current = a, a, b
            points = [a]
            unused.remove(tuple(sorted((a, b))))
            while current != start:
                points.append(current)
                following = next(x for x in adjacency[current] if x != previous)
                edge = tuple(sorted((current, following)))
                if edge not in unused:
                    raise ValueError("A contour reuses an edge before closing.")
                unused.remove(edge)
                previous, current = current, following
            poly = Polygon(points)
            if not poly.is_valid:
                info["failure"] = "A closed contour polygon is invalid."
                return info, None
            region = region.symmetric_difference(poly)
            info["loops"] += 1
        info["closed"] = True
        info["polygon_valid"] = bool(region.is_valid)
        info["area_mm2"] = float(region.area)
        if not region.is_valid:
            info["failure"] = "Even-odd combined region is invalid."
            return info, None
        return info, region
    except Exception as exc:
        info["failure"] = f"{type(exc).__name__}: {exc}"
        return info, None


def area_comparison(original, candidate):
    if original is None or candidate is None:
        return {"available": False, "reason": "At least one raw contour failed; no area was invented."}
    added = candidate.difference(original)
    removed = original.difference(candidate)
    symmetric = original.symmetric_difference(candidate)
    return {
        "available": True,
        "original_area_mm2": float(original.area),
        "candidate_area_mm2": float(candidate.area),
        "added_area_mm2": float(added.area),
        "removed_area_mm2": float(removed.area),
        "symmetric_difference_area_mm2": float(symmetric.area),
        "net_area_change_mm2": float(candidate.area - original.area),
        "equal_within_area_tolerance": bool(symmetric.area <= AREA_TOLERANCE),
    }


def compare_section(original, candidate, z):
    original_info, original_region = section(original, z)
    candidate_info, candidate_region = section(candidate, z)
    return {
        "original": original_info,
        "candidate": candidate_info,
        "comparison": area_comparison(original_region, candidate_region),
    }


def manifold_report(original, candidate):
    try:
        from manifold3d import Manifold, Mesh64

        def convert(mesh):
            return Manifold(Mesh64(
                np.ascontiguousarray(mesh.vertices, dtype=np.float64),
                np.ascontiguousarray(mesh.faces, dtype=np.uint64),
            ))

        original_m, candidate_m = convert(original), convert(candidate)

        def stats(m):
            return {
                "status": str(m.status()),
                "empty": bool(m.is_empty()),
                "volume_mm3": float(m.volume()),
                "bounds_mm": None if m.is_empty() else list(m.bounding_box()),
            }

        inputs = {"original": stats(original_m), "candidate": stats(candidate_m)}
        if any(v["status"] != "Error.NoError" for v in inputs.values()):
            return {"available": False, "input_status": inputs, "reason": "Manifold conversion failed; inputs were not repaired."}

        def delta(a, b):
            added, removed = b - a, a - b
            result = {
                "original": stats(a), "candidate": stats(b),
                "added": stats(added), "removed": stats(removed),
                "symmetric_difference_volume_mm3": float(added.volume() + removed.volume()),
                "net_volume_change_mm3": float(b.volume() - a.volume()),
                "equal_within_volume_tolerance": bool(added.volume() + removed.volume() <= VOLUME_TOLERANCE),
                "volume_balance_residual_mm3": float(b.volume() - a.volume() - added.volume() + removed.volume()),
            }
            result["all_operations_no_error"] = all(result[k]["status"] == "Error.NoError" for k in ["original", "candidate", "added", "removed"])
            return result

        # Halfspace crops apply to both actual meshes. The lower Z=0..3 base
        # remains included; the comparisons therefore describe these exact
        # limited volumes and do not prove facade similarity outside them.
        crop_definitions = [
            ("rear_y_ge_10", "Y >= 10 mm; all X and Z", [([0, 1, 0], 10)]),
            ("entrance_x_ge_10_y_le_10", "X >= 10 mm and Y <= 10 mm; all Z. Includes a small part of the oval front body.", [([1, 0, 0], 10), ([0, -1, 0], -10)]),
            ("entrance_x_ge_16_y_le_10_supplement", "X >= 16 mm and Y <= 10 mm; all Z. Narrower entrance/connector zone outside the oval front roof.", [([1, 0, 0], 16), ([0, -1, 0], -10)]),
            ("stair_y_le_minus_50", "Y <= -50 mm; all X and Z. Outer portion of stair/cheek wall only; excludes inner treads overlapping front facade.", [([0, -1, 0], 50)]),
        ]
        crops = []
        for crop_id, description, planes in crop_definitions:
            a, b = original_m, candidate_m
            for normal, distance in planes:
                a, b = a.trim_by_plane(normal, distance), b.trim_by_plane(normal, distance)
            crops.append({"id": crop_id, "description": description, "halfspaces": [{"normal": normal, "origin_offset_mm": distance} for normal, distance in planes], **delta(a, b)})
        return {"available": True, "input_status": inputs, "global": delta(original_m, candidate_m), "crops": crops}
    except Exception as exc:
        return {"available": False, "reason": f"{type(exc).__name__}: {exc}", "note": "Optional Boolean comparison failed; no repair or substitution was performed."}


def make_markdown(report):
    a, b = report["files"]["original"], report["files"]["candidate"]
    lines = [
        "# Actual STL geometry delta", "",
        "Read-only comparison of the original STL at main `08604e70212673240173660584236e361221533f` and the fixed review candidate. All coordinates and measures use miniature millimetres; they are not surveyed building dimensions.", "",
        f"- Original: SHA-256 `{a['sha256']}`, {a['bytes']:,} bytes; {a['face_count']:,} faces; volume {a['volume_mm3']:.6f} mm³; bounds `{a['bounds_mm']}`.",
        f"- Candidate: SHA-256 `{b['sha256']}`, {b['bytes']:,} bytes; {b['face_count']:,} faces; volume {b['volume_mm3']:.6f} mm³; bounds `{b['bounds_mm']}`.",
        f"- Input hashes unchanged during measurement: `{report['input_hashes_stable']}`.", "",
        "## Horizontal sections", "",
        "Triangle/plane intersections follow the existing `check_layers.py`: endpoints clustered within 0.0001 mm; every graph vertex must have degree 2; valid polygon loops are combined with even-odd nesting in Shapely. No contour repair is used. Exact-Z raw attempts and all failure reasons are retained in the JSON. A separate supplement at **Z + 0.000013 mm** avoids coplanar faces/vertices at designed heights; it is not relabelled as the exact-Z result.", "",
        "The table uses the explicitly offset supplements consistently across both meshes. Added = candidate minus original; removed = original minus candidate.", "",
        "| Requested Z | Measured Z | Original area mm² | Candidate area mm² | Added mm² | Removed mm² | Symmetric difference mm² |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["sections"]:
        c = row["offset_supplement"]["comparison"]
        if c["available"]:
            lines.append(f"| {row['requested_z_mm']} | {row['offset_z_mm']:.6f} | {c['original_area_mm2']:.6f} | {c['candidate_area_mm2']:.6f} | {c['added_area_mm2']:.6f} | {c['removed_area_mm2']:.6f} | {c['symmetric_difference_area_mm2']:.6f} |")
        else:
            lines.append(f"| {row['requested_z_mm']} | {row['offset_z_mm']:.6f} | failed | failed | — | — | — |")
    lines.extend(["", "### Raw exact-Z evidence", "", "| Z | Original raw result | Candidate raw result | Coplanar faces (original/candidate) |", "|---:|---|---|---:|"])
    for row in report["sections"]:
        raw = row["exact_z_raw"]
        def raw_label(v):
            return "closed/valid" if v["closed"] and v["polygon_valid"] else v["failure"] or "failed"
        lines.append(f"| {row['requested_z_mm']} | {raw_label(raw['original'])} | {raw_label(raw['candidate'])} | {raw['original']['coplanar_face_count']}/{raw['candidate']['coplanar_face_count']} |")
    bools = report["boolean_3d"]
    lines.extend(["", "## Actual 3D differences and limited crop checks", ""])
    if bools["available"]:
        g = bools["global"]
        lines.extend([
            "Trimesh `process=True` reconstructs shared vertices from STL triangle soup; no hole filling or winding repair is called. Manifold3D receives those STL coordinates as float64. Halfspace trims make closed crops of both input volumes; Boolean subtraction measures added and removed solid. Numerical equivalence threshold is 0.000001 mm³. Raw signed floating residues are retained, including values that round to -0.000000. This is a limited volume comparison, not a proof about every surface detail or an independent self-intersection certificate.", "",
            f"Global added volume: **{g['added']['volume_mm3']:.6f} mm³**; removed: **{g['removed']['volume_mm3']:.6f} mm³**; symmetric difference: **{g['symmetric_difference_volume_mm3']:.6f} mm³**; net change: **{g['net_volume_change_mm3']:.6f} mm³**. All Boolean statuses `NoError`: `{g['all_operations_no_error']}`.", "",
            "| Crop | Original mm³ | Candidate mm³ | Added mm³ | Removed mm³ | Symmetric difference mm³ | Equal within tolerance |",
            "|---|---:|---:|---:|---:|---:|---|",
        ])
        for c in bools["crops"]:
            lines.append(f"| `{c['id']}` | {c['original']['volume_mm3']:.6f} | {c['candidate']['volume_mm3']:.6f} | {c['added']['volume_mm3']:.6f} | {c['removed']['volume_mm3']:.6f} | {c['symmetric_difference_volume_mm3']:.6f} | {c['equal_within_volume_tolerance']} |")
        lines.append("")
        lines.extend(f"- `{c['id']}`: {c['description']}" for c in bools["crops"])
        lines.extend(["", "The rear crop's tiny nonzero Boolean residue is retained as a failed equality comparison at the stated strict tolerance. It must not be described as exact geometric identity. The JSON records full precision and every Boolean status."])
        broad = next(c for c in bools["crops"] if c["id"] == "entrance_x_ge_10_y_le_10")
        if not broad["equal_within_volume_tolerance"]:
            lines.extend(["", "The requested broad entrance crop is **not unchanged**: it includes the altered edge of the oval front body. Its difference is preserved above. The narrower X >= 16 crop separately tests the entrance/connector volume and must not be used to erase the broad crop result."])
    else:
        lines.append(f"3D Boolean comparison unavailable: {bools['reason']}")
    lines.extend([
        "", "## Scope and reproduction", "",
        "Only seven requested planes and the named halfspace volumes are compared. The crop at Y <= -50 verifies the outer stair/cheek wall only. It does not establish every stair tread is unchanged. These comparisons do not establish visual fidelity, minimum feature thickness, support feasibility, successful slicing, or print success. Existing raw QA failures/flags in other reports are unaffected.", "",
        "Run from a Python environment with NumPy, SciPy, Trimesh, Shapely and optional Manifold3D:", "",
        "```text", "python qa/geometry_delta.py --original PATH/TO/original/model.stl", "```", "",
        "The default candidate is the package's `model.stl`; `--candidate` and `--output-dir` can select other paths. Both reports contain actual measured results; the script only reads meshes and writes its own JSON/Markdown.", "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--candidate", type=Path, default=Path(__file__).resolve().parent.parent / "model.stl")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    original = trimesh.load(args.original, force="mesh", process=True)
    candidate = trimesh.load(args.candidate, force="mesh", process=True)
    files = {"original": metadata(args.original, original), "candidate": metadata(args.candidate, candidate)}
    sections = []
    for z in HEIGHTS:
        sections.append({
            "requested_z_mm": z,
            "offset_z_mm": z + OFFSET,
            "exact_z_raw": compare_section(original, candidate, z),
            "offset_supplement": compare_section(original, candidate, z + OFFSET),
        })
    versions = {"python": platform.python_version()}
    for package in ["numpy", "scipy", "trimesh", "shapely", "manifold3d"]:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    report = {
        "method": "Read-only STL triangle-plane closed-loop/even-odd area comparison, exact-Z raw evidence plus separately offset supplements; optional 3D Manifold Boolean differences and halfspace crops.",
        "original_reference_commit": "08604e70212673240173660584236e361221533f",
        "runtime_versions": versions,
        "endpoint_cluster_tolerance_mm": ENDPOINT_TOLERANCE,
        "area_equality_tolerance_mm2": AREA_TOLERANCE,
        "volume_equality_tolerance_mm3": VOLUME_TOLERANCE,
        "offset_mm": OFFSET,
        "files": files,
        "sections": sections,
        "boolean_3d": manifold_report(original, candidate),
        "slicer_run": False,
        "physical_print_test": False,
    }
    end_hashes = {"original": sha256(args.original), "candidate": sha256(args.candidate)}
    report["input_hashes_at_completion"] = end_hashes
    report["input_hashes_stable"] = all(files[k]["sha256"] == end_hashes[k] for k in files)
    report["exact_z_failures"] = [
        {"requested_z_mm": row["requested_z_mm"], "file": k, "failure": row["exact_z_raw"][k]["failure"]}
        for row in sections for k in ["original", "candidate"] if row["exact_z_raw"][k]["failure"]
    ]
    report["offset_supplement_failures"] = [
        {"requested_z_mm": row["requested_z_mm"], "file": k, "failure": row["offset_supplement"][k]["failure"]}
        for row in sections for k in ["original", "candidate"] if row["offset_supplement"][k]["failure"]
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "geometry-delta.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output_dir / "geometry-delta.md").write_text(make_markdown(report), encoding="utf-8")
    print(json.dumps({"input_hashes_stable": report["input_hashes_stable"], "exact_z_failures": report["exact_z_failures"], "offset_supplement_failures": report["offset_supplement_failures"], "boolean_3d_available": report["boolean_3d"]["available"], "report": str(args.output_dir / "geometry-delta.json")}, ensure_ascii=False, indent=2))
    if not report["input_hashes_stable"]:
        raise SystemExit("Input hashes changed during comparison; results are invalid.")


if __name__ == "__main__":
    main()
