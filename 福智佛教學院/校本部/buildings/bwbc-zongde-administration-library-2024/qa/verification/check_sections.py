"""Raw STL XY layers: 0.2 mm pitch, three offsets, per-polygon 0.8 mm opening."""
from pathlib import Path
import argparse
import hashlib
import math
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, MultiPoint
from qa_common import (QAError, require, load_stl, polygons, write_json,
                       write_gzip_json, sha256, error_report, checker_inventory)

OFFSETS = (0.031, 0.071, 0.137)
PITCH = 0.2
WIDTH = 0.8
MAX_POLYGON_LOSS = 0.01


def original_section(triangles, z):
    """Canonical interpolation makes shared-edge intersections bit-identical.

    Slice/vertex coincidence is reported as ambiguity, never nudged or repaired.
    Nested valid contours become explicit shell/hole Polygons without a union.
    """
    require(not np.any(triangles[:, :, 2] == z),
            'Layer coincides exactly with an original vertex elevation')
    candidates = np.flatnonzero((triangles[:, :, 2].min(axis=1) < z) &
                               (triangles[:, :, 2].max(axis=1) > z))
    graph, segment_sources = {}, []
    for face_index in candidates:
        triangle = triangles[face_index]
        require(not np.any(triangle[:, 2] == z),
                f'Layer coincides with original triangle vertex on face {face_index}')
        hits = []
        for a, b in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            if tuple(a) > tuple(b):
                a, b = b, a
            if min(a[2], b[2]) < z < max(a[2], b[2]):
                point = a + (b - a) * ((z - a[2]) / (b[2] - a[2]))
                hits.append(tuple(float(value) for value in point[:2]))
        require(len(hits) == 2 and hits[0] != hits[1],
                f'Original face {face_index} has a degenerate or ambiguous slice segment')
        a, b = hits
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)
        segment_sources.append(int(face_index))
    require(graph, 'No section segments inside the original Z bounds')
    require(all(len(neighbors) == 2 and len(set(neighbors)) == 2 for neighbors in graph.values()),
            'Original section has an open, duplicated, touching or branching contour')
    remaining = set(graph)
    rings = []
    while remaining:
        seed = min(remaining)
        previous, current, ring = None, seed, []
        while True:
            require(current in remaining, 'Contour revisits a non-closing original section vertex')
            ring.append(current)
            remaining.remove(current)
            neighbors = graph[current]
            following = neighbors[0] if neighbors[0] != previous else neighbors[1]
            previous, current = current, following
            if current == seed:
                break
        polygon = Polygon(ring)
        require(len(ring) >= 3 and polygon.is_valid and polygon.area > 0,
                f'Invalid original contour: {shapely.is_valid_reason(polygon)}')
        rings.append(polygon)
    rings.sort(key=lambda p: (-p.area, p.bounds))
    parents, depths = [], []
    for i, child in enumerate(rings):
        containers = []
        for j, other in enumerate(rings[:i]):
            require(not child.boundary.intersects(other.boundary),
                    'Original section contours cross or touch')
            if other.contains(child):
                containers.append(j)
            else:
                require(child.disjoint(other), 'Original contours overlap without strict nesting')
        parent = min(containers, key=lambda j: rings[j].area) if containers else None
        parents.append(parent)
        depths.append(depths[parent] + 1 if parent is not None else 0)
    components = []
    for i, ring in enumerate(rings):
        if depths[i] % 2:
            continue
        holes = [list(rings[j].exterior.coords) for j, parent in enumerate(parents) if parent == i]
        polygon = Polygon(ring.exterior.coords, holes)
        require(polygon.is_valid and polygon.area > 0,
                f'Invalid original Polygon with holes: {shapely.is_valid_reason(polygon)}')
        components.append(polygon)
    components.sort(key=lambda p: (p.bounds, -p.area))
    shape = MultiPolygon(components)
    require(shape.is_valid, f'Invalid original MultiPolygon: {shapely.is_valid_reason(shape)}')
    return components, {'segment_count': len(segment_sources), 'contour_count': len(rings),
                        'source_face_indices': segment_sources}


def inspect(stl, out):
    raw, triangles, _, _ = load_stl(stl)
    zmin, zmax = float(triangles[:, :, 2].min()), float(triangles[:, :, 2].max())
    layer_rows, polygon_rows, failures = [], [], []
    for offset in OFFSETS:
        index = 0
        while (z := zmin + offset + PITCH * index) < zmax:
            layer_id = f'{offset:.3f}:{index}'
            row = {'layer_id': layer_id, 'offset_mm': offset, 'layer_index': index, 'z_mm': z}
            index += 1
            try:
                components, detail = original_section(triangles, z)
                row.update(detail)
                row.update({'valid_original_section': True, 'original_polygon_count': len(components),
                            'section_area_mm2': sum(component.area for component in components)})
                for component_index, component in enumerate(components):
                    eroded = component.buffer(-WIDTH / 2, quad_segs=32)
                    opened = eroded.buffer(WIDTH / 2, quad_segs=32)
                    eroded_components, opened_components = polygons(eroded), polygons(opened)
                    loss = component.difference(opened)
                    gained = opened.difference(component)
                    vertices = list(component.exterior.coords)
                    vertices.extend(point for ring in component.interiors for point in ring.coords)
                    rectangle = list(component.minimum_rotated_rectangle.exterior.coords)
                    widths = [math.dist(rectangle[i], rectangle[i + 1]) for i in range(4)]
                    checks = {'original_polygon_valid': bool(component.is_valid),
                              'erosion_valid': bool(eroded.is_valid), 'opening_valid': bool(opened.is_valid),
                              'survives_erosion': len(eroded_components) > 0,
                              'no_split_after_erosion': len(eroded_components) == 1,
                              'survives_opening': len(opened_components) > 0,
                              'no_split_after_opening': len(opened_components) == 1,
                              'individual_polygon_loss_le_one_percent': loss.area / component.area <= MAX_POLYGON_LOSS}
                    record = {'layer_id': layer_id, 'offset_mm': offset, 'layer_index': index - 1,
                              'z_mm': z, 'original_polygon_index': component_index,
                              'bounds_mm': list(component.bounds), 'original_area_mm2': component.area,
                              'original_hole_count': len(component.interiors),
                              'minimum_rotated_bbox_width_mm': min(widths),
                              'eroded_components': len(eroded_components),
                              'opened_components': len(opened_components),
                              'eroded_component_areas_mm2': [item.area for item in eroded_components],
                              'opened_component_areas_mm2': [item.area for item in opened_components],
                              'opening_loss_area_mm2': loss.area,
                              'opening_loss_fraction': loss.area / component.area,
                              'opening_gain_area_mm2': gained.area,
                              'loss_outside_0p41_vertex_disks_mm2':
                                  loss.difference(MultiPoint(vertices).buffer(.41, quad_segs=32)).area,
                              'checks': checks, 'passed': all(checks.values())}
                    polygon_rows.append(record)
                    if not record['passed']:
                        failures.append({**record, 'original_polygon': component.__geo_interface__,
                                         'eroded_geometry': eroded.__geo_interface__,
                                         'opened_geometry': opened.__geo_interface__,
                                         'lost_geometry': loss.__geo_interface__})
                matching = [p for p in polygon_rows if p['layer_id'] == layer_id]
                row['opening_loss_area_mm2'] = sum(p['opening_loss_area_mm2'] for p in matching)
                row['passed'] = all(p['passed'] for p in matching)
            except Exception as error:
                row.update({'valid_original_section': False, 'passed': False,
                            'error_type': type(error).__name__, 'error': str(error)})
                failures.append(row.copy())
            layer_rows.append(row)
    per_offset = [{'offset_mm': offset, 'sampled_layers': sum(row['offset_mm'] == offset for row in layer_rows)}
                  for offset in OFFSETS]
    checks = {
        'all_three_offsets_have_layers': all(row['sampled_layers'] > 0 for row in per_offset),
        'all_original_sections_valid_without_repair': bool(layer_rows) and all(row['valid_original_section'] for row in layer_rows),
        'every_original_polygon_checked': bool(polygon_rows) and sum(row.get('original_polygon_count', 0) for row in layer_rows) == len(polygon_rows),
        'all_original_polygons_survive_erosion_and_opening': bool(polygon_rows) and all(row['checks']['survives_erosion'] and row['checks']['survives_opening'] for row in polygon_rows),
        'no_original_polygon_splits_after_erosion_or_opening': bool(polygon_rows) and all(row['checks']['no_split_after_erosion'] and row['checks']['no_split_after_opening'] for row in polygon_rows),
        'all_opened_and_eroded_polygons_valid': bool(polygon_rows) and all(row['checks']['erosion_valid'] and row['checks']['opening_valid'] for row in polygon_rows),
        'all_individual_polygon_losses_le_one_percent': bool(polygon_rows) and all(row['checks']['individual_polygon_loss_le_one_percent'] for row in polygon_rows),
    }
    details = out / 'section-details.json.gz'
    failed = out / 'section-failures.json.gz'
    write_gzip_json(details, {'layers': layer_rows, 'original_polygon_checks': polygon_rows})
    write_gzip_json(failed, failures)
    return {'passed': all(checks.values()), 'strict_passed': all(checks.values()), 'checks': checks,
            'stl_sha256': hashlib.sha256(raw).hexdigest(), 'z_min_mm': zmin, 'z_max_mm': zmax,
            'pitch_mm': PITCH, 'offsets_from_z_min_mm': list(OFFSETS), 'opening_reference_width_mm': WIDTH,
            'per_polygon_loss_limit': MAX_POLYGON_LOSS, 'per_offset': per_offset,
            'sampled_layers': len(layer_rows), 'original_polygon_count': len(polygon_rows),
            'failed_layer_count': sum(not row['passed'] for row in layer_rows),
            'failed_polygon_count': sum(not row['passed'] for row in polygon_rows),
            'maximum_individual_polygon_loss_fraction': max((row['opening_loss_fraction'] for row in polygon_rows), default=None),
            'detail_file': details.name, 'detail_sha256': sha256(details),
            'failure_file': failed.name, 'failure_sha256': sha256(failed),
            'checker_sources_sha256': checker_inventory(),
            'method': 'Exact original triangles; canonical shared-edge interpolation; closed degree-two contour graphs; strict nesting and explicit valid Polygon holes. Each original Polygon independently eroded and opened with radius 0.4 mm. All per-polygon losses recorded; no area-averaging exemption, contour repair, coordinate rounding or lost-component omission.',
            'limitations': 'Three finite XY layer schedules and morphological screen, not a slicer path or global wall-thickness proof. Original vertex coincidences are rejected rather than displaced.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / 'section-check.json'
    try:
        report = inspect(args.stl, args.out)
        write_json(path, report)
    except Exception as error:
        report = error_report(path, 'sections', args.stl, error)
    print({'passed': report['passed'], 'report': str(path), 'error': report.get('error')})
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
