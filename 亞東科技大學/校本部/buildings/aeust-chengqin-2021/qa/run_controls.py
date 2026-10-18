"""Run only tiny synthetic regressions; does not read any building model."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import trimesh
import independent_geometry_qa as qa


def main():
    root = Path(__file__).resolve().parent
    controls = qa.printability_controls()
    geometry_controls = qa.geometric_controls()
    paths = root / "control-artifacts"
    paths.mkdir(exist_ok=True)
    cube = trimesh.creation.box(extents=[2, 2, 2])
    thin = trimesh.creation.box(extents=[4, 0.4, 2])
    cli_cases = {}
    for name, mesh, expected_status in [("clean_cube", cube, 0), ("thin_0p4mm_bar", thin, 1)]:
        stl_path = paths / f"{name}.stl"
        json_path = paths / f"{name}.json"
        stl_path.write_bytes(trimesh.exchange.stl.export_stl(mesh))
        process = subprocess.run([sys.executable, str(root / "independent_geometry_qa.py"),
                                  str(stl_path), "--json", str(json_path), "--negative-controls"],
                                 capture_output=True, text=True, encoding="utf-8")
        (paths / f"{name}.stdout.txt").write_text(process.stdout, encoding="utf-8")
        (paths / f"{name}.stderr.txt").write_text(process.stderr, encoding="utf-8")
        report = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else {}
        cli_cases[name] = {"exit_status": process.returncode,
                           "expected_exit_status": expected_status,
                           "exit_status_matches": process.returncode == expected_status,
                           "topology_passes": report.get("topology", {}).get("passes_basic_solid_checks"),
                           "self_intersection_screen_passes": report.get("self_intersections", {}).get("passes_numerical_pair_screen"),
                           "thin_screen_passes": report.get("sections", {}).get("passes_sampled_thin_feature_screen"),
                           "bounded_screen_passes": report.get("passes_bounded_geometry_screen"),
                           "report": json_path.relative_to(root).as_posix()}
    # Explicit gate regression: the thin prism is topologically valid, has no
    # unexpected triangle contacts, and is vertically supported. It must fail
    # only because its section cores vanish under 0.4 mm erosion.
    thin_report = json.loads((paths / "thin_0p4mm_bar.json").read_text(encoding="utf-8"))
    gate_regression = bool(thin_report["topology"]["passes_basic_solid_checks"]
                           and thin_report["self_intersections"]["passes_numerical_pair_screen"]
                           and thin_report["sections"]["passes_sampled_support_screen"]
                           and not thin_report["sections"]["passes_sampled_thin_feature_screen"]
                           and not thin_report["passes_bounded_geometry_screen"])
    passed = (all(r.get("negative_control_detected", r.get("positive_control_passed", False)) for r in controls.values())
              and all(v for k, v in geometry_controls.items() if k.endswith("detected") or k.startswith("clean_cube"))
              and all(r["exit_status_matches"] for r in cli_cases.values())
              and gate_regression)
    evidence = {"scope": "Synthetic controls only; no candidate building was inspected and no Blender render was run.",
                "checker_sha256": hashlib.sha256((root / "independent_geometry_qa.py").read_bytes()).hexdigest(),
                "printability_controls": controls,
                "geometry_controls": geometry_controls,
                "cli_cases": cli_cases,
                "thin_failure_alone_rejects_gate": gate_regression,
                "all_control_expectations_passed": bool(passed)}
    (root / "control-evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
