"""Audit actual ASCII PrusaSlicer G-code without sending it to a printer.

Reads linear G0/G1 motion and extrusion modes, retains every TYPE per layer,
and renders actual first-layer extrusion paths. Bridge infill is reported
separately from support material. A zero support count alone is not evidence
that a mesh needs no support: this run deliberately disables support.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gcode", type=Path)
    ap.add_argument("--stl", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    text = args.gcode.read_text(encoding="utf-8-sig")
    xyz = [0., 0., 0.]
    e = 0.
    relative_e = False
    relative_xyz = False
    role = "Unspecified/custom"
    layer = -1
    layer_declared_z = None
    type_seen = Counter()
    by_layer = {}
    segments = []
    unknown_motion = []
    config = {}
    gcode_time = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if stripped == ";LAYER_CHANGE":
            layer += 1
            layer_declared_z = None
        if stripped.startswith(";Z:"):
            layer_declared_z = float(stripped[3:])
        if stripped.startswith(";TYPE:"):
            role = stripped[6:].strip()
            type_seen[role] += 1
        if "estimated printing time" in stripped:
            gcode_time.append(stripped)
        mc = re.match(r";\s*([a-z][a-z0-9_]*)\s*=\s*(.*)$", stripped)
        if mc:
            config[mc[1]] = mc[2]
        code = stripped.partition(";")[0].strip()
        if not code:
            continue
        command = code.split()[0].upper()
        vals = {m.group(1).upper(): float(m.group(2)) for m in re.finditer(
            r"([XYZEF])\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)", code)}
        if command == "M82":
            relative_e = False
        elif command == "M83":
            relative_e = True
        elif command == "G90":
            relative_xyz = False
        elif command == "G91":
            relative_xyz = True
        elif command == "G92":
            for i, axis in enumerate("XYZ"):
                if axis in vals:
                    xyz[i] = vals[axis]
            if "E" in vals:
                e = vals["E"]
        elif command in {"G0", "G00", "G1", "G01"}:
            nxt = [xyz[i] + vals.get(a, 0.) if relative_xyz else vals.get(a, xyz[i])
                   for i, a in enumerate("XYZ")]
            de = vals.get("E", 0.) if relative_e else vals.get("E", e) - e
            if "E" in vals:
                e = e + vals["E"] if relative_e else vals["E"]
            distance = math.dist(xyz[:2], nxt[:2])
            if de > 1e-7 and distance > 1e-7:
                rec = by_layer.setdefault(layer, {"layer_index": layer,
                    "declared_z_mm": layer_declared_z, "types": {}})
                item = rec["types"].setdefault(role, {"segments": 0,
                    "positive_filament_mm": 0., "xy_path_mm": 0.})
                item["segments"] += 1
                item["positive_filament_mm"] += de
                item["xy_path_mm"] += distance
                segments.append({"line": line_no, "layer": layer, "z": nxt[2],
                    "type": role, "xy0": xyz[:2], "xy1": nxt[:2], "e_mm": de})
            xyz = nxt
        elif command in {"G2", "G02", "G3", "G03"}:
            unknown_motion.append({"line": line_no, "code": code})

    support = [s for s in segments if "support" in s["type"].lower()]
    bridge = [s for s in segments if "bridge" in s["type"].lower()]
    actual_types = Counter(s["type"] for s in segments)
    model_segments = [s for s in segments if s["layer"] >= 0 and
                      "skirt" not in s["type"].lower() and "brim" not in s["type"].lower()]
    first_layer = min((s["layer"] for s in model_segments), default=None)
    first = [s for s in segments if s["layer"] == first_layer]
    bounds = lambda ss: None if not ss else [[min(p[i] for s in ss for p in [s["xy0"],s["xy1"]]) for i in range(2)],
                                            [max(p[i] for s in ss for p in [s["xy0"],s["xy1"]]) for i in range(2)]]
    first_bounds = bounds(first)
    if first_bounds:
        image = Image.new("RGB", (1400, 1400), "white")
        draw = ImageDraw.Draw(image)
        lo, hi = first_bounds
        span = max(hi[0]-lo[0], hi[1]-lo[1])
        scale = 1220/max(span,1)
        center = [(lo[i]+hi[i])/2 for i in range(2)]
        def point(p):
            return (700+(p[0]-center[0])*scale,700-(p[1]-center[1])*scale)
        palette = {"Perimeter": "#154c79", "External perimeter": "#102a43",
                   "Skirt/Brim": "#a5bd36", "Solid infill": "#569343",
                   "Internal infill": "#94bacc", "Top solid infill": "#6d75bf",
                   "Gap fill": "#c55a11", "Bridge infill": "#bb2876"}
        for s in first:
            draw.line([point(s["xy0"]),point(s["xy1"])], fill=palette.get(s["type"],"#444444"), width=2)
        draw.text((35,25), args.gcode.stem + " - ACTUAL FIRST-LAYER TOOLPATH", fill="black")
        draw.text((35,48), "Blue: perimeter; olive: brim; green: solid infill; magenta: bridge", fill="black")
        draw.text((35,71), "Geometry review only. No physical print or machine validation.", fill="black")
        image.save(args.output/"first-layer-toolpaths.png")
    report = {
        "input_stl": str(args.stl.resolve()), "input_stl_sha256": sha(args.stl),
        "gcode": str(args.gcode.resolve()), "gcode_sha256": sha(args.gcode),
        "gcode_bytes": args.gcode.stat().st_size,
        "parser": "Linear G0/G1, G90/G91, M82/M83, G92; counts XY moves with positive filament. No printer execution.",
        "unsupported_arc_commands": unknown_motion,
        "actual_extruding_segment_count": len(segments),
        "type_marker_counts": dict(type_seen),
        "positive_extrusion_segment_counts_by_type": dict(actual_types),
        "support_extrusion_segments": len(support),
        "support_positive_filament_mm": sum(s["e_mm"] for s in support),
        "bridge_infill_segments": len(bridge),
        "bridge_infill_positive_filament_mm": sum(s["e_mm"] for s in bridge),
        "bridge_layers": sorted(set(s["layer"] for s in bridge)),
        "bridge_interpretation": "Bridge infill is reported separately; it is not support material and is not automatically an external unprintable overhang.",
        "layer_count_with_positive_xy_extrusion": len(by_layer),
        "all_extrusion_xy_bounds_mm": bounds(segments),
        "first_model_layer_index": first_layer,
        "first_layer_z_values_mm": sorted(set(s["z"] for s in first)),
        "first_layer_extruding_segments": len(first),
        "first_layer_xy_bounds_mm": first_bounds,
        "first_layer_model_xy_bounds_mm": bounds([s for s in first if
             "skirt" not in s["type"].lower() and "brim" not in s["type"].lower()]),
        "first_layer_image": "first-layer-toolpaths.png" if first_bounds else None,
        "support_related_embedded_config": {k:v for k,v in config.items() if k.startswith("support_material") or k in {"raft_layers","nozzle_diameter","layer_height","first_layer_height","bed_shape","binary_gcode","gcode_flavor"}},
        "estimated_time_comments": gcode_time,
        "per_layer": [by_layer[k] for k in sorted(by_layer)],
        "limitations": ["Support was deliberately disabled. Zero support extrusion is not by itself a proof that supports are unnecessary.",
                        "G-code has not been sent to a printer. Generic geometry-review settings are not a calibrated machine profile.",
                        "First-layer image contains actual extruding XY path centerlines, including brim; it does not model bead squish or bed adhesion."]
    }
    (args.output/"gcode-audit.json").write_text(json.dumps(report,indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in {"per_layer","support_related_embedded_config"}},indent=2))
    if unknown_motion or not model_segments or first_layer is None or not first_bounds:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
