"""Check exact original STL topology and normals; no mesh-processing library."""
from pathlib import Path
import argparse
import hashlib
import numpy as np
from qa_common import load_stl, write_json, error_report, checker_inventory


def inspect(stl, expected_longest_mm=None):
    raw, triangles, normals, attributes = load_stl(stl)
    vertices, inverse = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    crosses = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    areas2 = np.linalg.norm(crosses, axis=1)
    unit = np.divide(crosses, areas2[:, None], out=np.zeros_like(crosses), where=areas2[:, None] > 0)
    edges, links = {}, [[] for _ in vertices]
    adjacency = [set() for _ in faces]
    for face_index, (a, b, c) in enumerate(faces):
        for u, v in ((a, b), (b, c), (c, a)):
            edges.setdefault(tuple(sorted((int(u), int(v)))), []).append((face_index, int(u), int(v)))
        for x, u, v in ((a, b, c), (b, c, a), (c, a, b)):
            links[x].append((int(u), int(v)))
    bad_edges = [{'vertices': list(edge), 'incident_directed_faces': records}
                 for edge, records in edges.items() if len(records) != 2]
    bad_winding = [{'vertices': list(edge), 'incident_directed_faces': records}
                   for edge, records in edges.items()
                   if len(records) == 2 and not (records[0][1] == records[1][2] and records[0][2] == records[1][1])]
    for records in edges.values():
        incident = [record[0] for record in records]
        for i in incident:
            adjacency[i].update(j for j in incident if i != j)
    shells, visited = [], set()
    for seed in range(len(faces)):
        if seed in visited:
            continue
        shell, stack = [], [seed]
        while stack:
            item = stack.pop()
            if item in visited:
                continue
            visited.add(item)
            shell.append(item)
            stack.extend(adjacency[item] - visited)
        shells.append(shell)
    bad_links = []
    for vertex, pairs in enumerate(links):
        graph = {}
        for a, b in pairs:
            graph.setdefault(a, []).append(b)
            graph.setdefault(b, []).append(a)
        connected, stack = set(), [next(iter(graph))] if graph else []
        while stack:
            node = stack.pop()
            if node in connected:
                continue
            connected.add(node)
            stack.extend(x for x in graph[node] if x not in connected)
        if (not graph or len(connected) != len(graph) or
                any(len(neighbors) != 2 or len(set(neighbors)) != 2 for neighbors in graph.values())):
            bad_links.append({'vertex_index': vertex, 'coordinate_mm': vertices[vertex].tolist(),
                              'link_edges': pairs})
    _, duplicate_counts = np.unique(np.sort(faces, axis=1), axis=0, return_counts=True)
    reference = vertices.mean(axis=0)
    translated = triangles - reference
    per_face_volume = np.einsum('ij,ij->i', translated[:, 0],
                               np.cross(translated[:, 1], translated[:, 2])) / 6
    volume = float(per_face_volume.sum())
    extents = np.ptp(vertices, axis=0)
    checks = {
        'binary_length_exact': len(raw) == 84 + 50 * len(faces),
        'finite_original_data': bool(np.isfinite(triangles).all() and np.isfinite(normals).all()),
        'all_original_faces_nondegenerate': bool((areas2 > 0).all()),
        'no_duplicate_original_faces': bool((duplicate_counts == 1).all()),
        'original_stored_normals_unit': bool(np.all(np.abs(np.linalg.norm(normals, axis=1) - 1) <= 1e-5)),
        'original_stored_normals_agree_with_directed_faces': bool(np.all(np.abs(normals - unit) <= 1e-5)),
        'exact_coordinate_edges_two_faces': not bad_edges,
        'exact_coordinate_consistent_winding': not bad_edges and not bad_winding,
        'exact_coordinate_vertex_links_single_cycles': not bad_links,
        'single_surface_no_internal_shell': len(shells) == 1,
        'positive_signed_volume': volume > 0,
    }
    if expected_longest_mm is not None:
        checks['requested_longest_extent_mm'] = abs(float(extents.max()) - expected_longest_mm) <= 1e-5
    return {
        'passed': all(checks.values()), 'strict_passed': all(checks.values()), 'checks': checks,
        'stl_sha256': hashlib.sha256(raw).hexdigest(), 'triangles': len(faces),
        'vertices_exact': len(vertices), 'edges_exact': len(edges), 'surface_shells': len(shells),
        'bounds_mm': [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()],
        'extents_mm': extents.tolist(), 'signed_volume_mm3': volume,
        'shell_face_counts': [len(shell) for shell in shells],
        'shell_signed_volumes_mm3': [float(per_face_volume[shell].sum()) for shell in shells],
        'bad_edges': bad_edges, 'bad_winding_edges': bad_winding, 'bad_vertex_links': bad_links,
        'degenerate_original_face_indices': np.flatnonzero(areas2 <= 0).tolist(),
        'bad_stored_normal_face_indices': np.flatnonzero(np.any(np.abs(normals - unit) > 1e-5, axis=1)).tolist(),
        'nonzero_attribute_face_count': int(np.count_nonzero(attributes)),
        'expected_longest_mm': expected_longest_mm, 'checker_sources_sha256': checker_inventory(),
        'method': 'Original little-endian binary records, exact numeric float32 coordinate indexing, directed edges, multigraph vertex links, face-edge BFS, translation-stable signed volume. No repair, rounding, face filtering, or model-specific dimension assumption.',
        'limitations': 'Topology checks do not prove absence of geometric self-intersection or global printable wall thickness.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-longest-mm', type=float)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / 'raw-mesh-check.json'
    try:
        report = inspect(args.stl, args.expected_longest_mm)
        write_json(path, report)
    except Exception as error:
        report = error_report(path, 'raw_mesh', args.stl, error)
    print({'passed': report['passed'], 'report': str(path), 'error': report.get('error')})
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
