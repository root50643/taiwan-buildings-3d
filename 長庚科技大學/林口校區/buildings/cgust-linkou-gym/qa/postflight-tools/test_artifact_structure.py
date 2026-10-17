"""Small synthetic structural controls; run serially under the shared QA lock.

No geometry engine, source model or external files are needed. All test checks
remain effective with python -O. These fixtures prove rejection behavior only;
they do not represent a CGUST geometry result.
"""
import copy
import math
import re
import unittest
from pathlib import Path

import review_artifact_structure as reviewer

import artifact_structure as a


def exact_fixture(boundary=False):
    descriptor = {'face': '10', 'sample': '0'}
    for key in ('x', 'y', 'z', 'nx', 'ny', 'nz', 'origin_x', 'origin_y', 'origin_z', 'dx', 'dy', 'dz'):
        descriptor[key] = '0'
        descriptor[key + '_hex'] = '0x0p+0'
    descriptor['dx'] = '1'; descriptor['dx_hex'] = '0x8p-3'
    descriptor['nx'] = '-1'; descriptor['nx_hex'] = '-0x8p-3'
    reason = ['original_triangle_parity_controls_failed']
    flag = {'original_face_index': 10, 'sample_index': 0,
            'reasons': reason, 'original_cpp_row': descriptor}
    contacts = [
        {'face': 10, 't0': str(a.LATTICE), 't1': str(a.LATTICE), 'coplanar_interval': False,
         'edge_or_vertex_contact': False, 'directed_crossing': -1},
        {'face': 20, 't0': str(2 * a.LATTICE), 't1': str(2 * a.LATTICE), 'coplanar_interval': False,
         'edge_or_vertex_contact': False, 'directed_crossing': 1},
    ]
    states = ['outside', 'inside', 'outside']
    breaks = [0, a.LATTICE, 2 * a.LATTICE]
    if boundary:
        contacts.append({'face': 30, 't0': str(3 * a.LATTICE), 't1': str(4 * a.LATTICE),
                         'coplanar_interval': True, 'edge_or_vertex_contact': True, 'directed_crossing': 0})
        states = ['outside', 'inside', 'outside', 'boundary', 'outside']
        breaks += [3 * a.LATTICE, 4 * a.LATTICE]
    intervals = []
    for i, (low, state) in enumerate(zip(breaks, states)):
        witness = {'direction': [1, 1, 2], 'attempt': 1}
        if state == 'boundary':
            witness['boundary_faces'] = [30]
        else:
            witness.update(crossing_faces=[20] if state == 'inside' else [],
                           crossing_t=['1'] if state == 'inside' else [])
        intervals.append({'t0': str(low), 't1': str(breaks[i + 1]) if i + 1 < len(breaks) else None,
                          'state': state, 'exact_midpoint_parity_witness': witness})
    row = {'original_face_index': 10, 'sample_index': 0,
           'exact_classification_completed': True, 'supplied_lossless_descriptor_line_classified': True,
           'original_run_lossless_descriptor_used': True, 'conservative_first_solid_chord_ge_0p8mm': True,
           'original_cpp_descriptor': copy.deepcopy(descriptor), 'original_numerical_reasons': list(reason),
           'ray_origin_integer_lattice_numerators': [0, 0, 0], 'ray_origin_integer_lattice_denominator': '1',
           'ray_direction_integer_lattice': [1, 0, 0], 'coordinate_lattice_denominator': str(a.LATTICE),
           'all_forward_original_triangle_contacts': contacts, 'classified_open_intervals': intervals,
           'first_entry_t': str(a.LATTICE), 'conservative_first_exit_t': str(2 * a.LATTICE),
           'conservative_first_solid_chord_squared_mm2_exact': '1',
           'conservative_first_solid_chord_mm_approx': 1.0}
    return [row], [copy.deepcopy(flag)]


def section_fixture():
    layers = []; polygons = []
    for offset, count in zip(a.OFFSETS, a.PER_OFFSET_LAYERS):
        for index in range(count):
            identity = {'layer_id': f'{offset:.3f}:{index}', 'offset_mm': offset,
                        'layer_index': index, 'z_mm': offset + .2 * index}
            layers.append(dict(identity, segment_count=3, contour_count=1, source_face_indices=[1, 2, 3],
                               valid_original_section=True, original_polygon_count=1,
                               section_area_mm2=100.0, opening_loss_area_mm2=.5, passed=True))
            polygons.append(dict(identity, original_polygon_index=0, bounds_mm=[0., 0., 10., 10.],
                original_area_mm2=100.0, original_hole_count=0, minimum_rotated_bbox_width_mm=10.0,
                eroded_components=1, opened_components=1, eroded_component_areas_mm2=[85.0],
                opened_component_areas_mm2=[99.5], opening_loss_area_mm2=.5, opening_loss_fraction=.005,
                opening_gain_area_mm2=0.0, loss_outside_0p41_vertex_disks_mm2=0.0,
                checks={key: True for key in a.POLYGON_CHECKS}, passed=True))
    report = {'passed': True, 'strict_passed': True, 'stl_sha256': a.STL_SHA256,
              'checks': {key: True for key in a.SECTION_CHECKS}, 'z_min_mm': 0., 'z_max_mm': 53.0,
              'pitch_mm': .2, 'offsets_from_z_min_mm': list(a.OFFSETS),
              'opening_reference_width_mm': .8, 'per_polygon_loss_limit': .01,
              'per_offset': [{'offset_mm': value, 'sampled_layers': count} for value, count in zip(a.OFFSETS, a.PER_OFFSET_LAYERS)],
              'sampled_layers': 795, 'original_polygon_count': 795,
              'failed_layer_count': 0, 'failed_polygon_count': 0,
              'maximum_individual_polygon_loss_fraction': .005}
    return report, {'layers': layers, 'original_polygon_checks': polygons}, []


def intersection_fixture():
    rows = [
        {'face_indices': [1, 2], 'reason': 'allowed_shared_edge', 'shared_original_vertex_count': 2,
         'intersection': {'dimension': 1, 'vertices_exact_original_units': [['0', '0', '0'], ['1', '0', '0']],
                          'vertices_approx_original_units': [[0., 0., 0.], [1., 0., 0.]]}},
        {'face_indices': [1, 3], 'reason': 'allowed_shared_vertex', 'shared_original_vertex_count': 1,
         'intersection': {'dimension': 0, 'vertices_exact_original_units': [['1', '0', '0']],
                          'vertices_approx_original_units': [[1., 0., 0.]]}},
    ]
    report = {'passed': True, 'strict_passed': True, 'completed': True, 'input_unchanged_during_check': True,
              'stl_sha256': a.STL_SHA256, 'stl_sha256_after_check': a.STL_SHA256,
              'original_face_count': a.FACES, 'face_index_base': 0,
              'total_unordered_original_face_pairs': a.FACES * (a.FACES - 1) // 2,
              'degenerate_original_faces': [], 'bad_pairs': [], 'bad_pair_count': 0,
              'lattice': {'denominator': str(a.LATTICE), 'denominator_power_of_two': 23,
                          'exact_coordinate_round_trips_checked': 9 * a.FACES,
                          'all_original_coordinates_round_trip_exactly': True},
              'broad_phase': {'sweep_axis': 0, 'axis_active_pair_costs': [5, 6, 7],
                              'all_bbox_overlapping_pairs_completed': True, 'candidate_pairs_checked': 5,
                              'candidate_sequence_sha256': '0' * 64},
              'classification_counts': {'allowed_shared_edge': 1, 'allowed_shared_vertex': 1,
                  'disjoint_coplanar': 1, 'disjoint_noncoplanar': 1, 'disjoint_plane_separated': 1},
              'actual_intersection_pair_count': 2,
              'all_actual_intersections': {'record_count': 2, 'path': 'contacts.jsonl.gz', 'sha256': '1' * 64,
                                            'format': 'gzip JSON Lines; one exact intersection per line'}}
    return report, rows


class ExactTests(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(a.LATTICE, 8388608)
        result = a.validate_exact_rows(*exact_fixture())
        self.assertEqual(result['minimum_first_chord_squared_mm2_exact'], '1')
        self.assertEqual(result['interval_count'], 3)

    def test_boundary_positive(self):
        self.assertEqual(a.validate_exact_rows(*exact_fixture(True))['boundary_interval_count'], 1)

    def test_origin_hex_round_trip(self):
        rows, flags = exact_fixture()
        for descriptor in (rows[0]['original_cpp_descriptor'], flags[0]['original_cpp_row']):
            descriptor['origin_x_hex'] = '0x1p-24'
        rows[0]['ray_origin_integer_lattice_numerators'] = [1, 0, 0]
        rows[0]['ray_origin_integer_lattice_denominator'] = '2'
        a.validate_exact_rows(rows, flags)

    def test_short_chord_is_rejected_even_with_true_summary(self):
        rows, flags = exact_fixture()
        row = rows[0]; finish = str(a.LATTICE + a.LATTICE // 2)
        row['all_forward_original_triangle_contacts'][1].update(t0=finish, t1=finish)
        row['classified_open_intervals'][1]['t1'] = finish
        row['classified_open_intervals'][2]['t0'] = finish
        row['conservative_first_exit_t'] = finish
        row['conservative_first_solid_chord_squared_mm2_exact'] = '1/4'
        row['conservative_first_solid_chord_mm_approx'] = .5
        with self.assertRaises(RuntimeError): a.validate_exact_rows(rows, flags)

    def test_mutations_fail_closed(self):
        def change_descriptor(rows, flags):
            for d in (rows[0]['original_cpp_descriptor'], flags[0]['original_cpp_row']):
                d['dx_hex'] = '-0x8p-3'; d['nx_hex'] = '0x8p-3'
        def change_normal(rows, flags):
            for d in (rows[0]['original_cpp_descriptor'], flags[0]['original_cpp_row']): d['nx_hex'] = '0x8p-3'
        mutations = {
            'missing interval': lambda r, f: r[0]['classified_open_intervals'].pop(1),
            'missing final interval': lambda r, f: r[0]['classified_open_intervals'].pop(),
            'missing contact': lambda r, f: r[0]['all_forward_original_triangle_contacts'].pop(),
            'missing witness': lambda r, f: r[0]['classified_open_intervals'][1].pop('exact_midpoint_parity_witness'),
            'wrong parity': lambda r, f: r[0]['classified_open_intervals'][1]['exact_midpoint_parity_witness'].update(crossing_faces=[], crossing_t=[]),
            'wrong witness direction': lambda r, f: r[0]['classified_open_intervals'][1]['exact_midpoint_parity_witness'].update(direction=[1, 1, 3]),
            'wrong contact order': lambda r, f: r[0]['all_forward_original_triangle_contacts'].reverse(),
            'nonpositive contact': lambda r, f: r[0]['all_forward_original_triangle_contacts'][0].update(t0='0', t1='0'),
            'wrong squared chord': lambda r, f: r[0].update(conservative_first_solid_chord_squared_mm2_exact='2'),
            'wrong approximate chord': lambda r, f: r[0].update(conservative_first_solid_chord_mm_approx=2.),
            'origin mismatch': lambda r, f: r[0].update(ray_origin_integer_lattice_numerators=[1, 0, 0]),
            'hex direction mismatch': change_descriptor,
            'hex normal direction mismatch': change_normal,
            'wrong lattice': lambda r, f: r[0].update(coordinate_lattice_denominator='1'),
            'old WFU lattice 2^56': lambda r, f: r[0].update(coordinate_lattice_denominator='72057594037927936'),
            'old AEUST lattice 2^30': lambda r, f: r[0].update(coordinate_lattice_denominator='1073741824'),
            'numeric lattice denominator': lambda r, f: r[0].update(coordinate_lattice_denominator=8388608),
            'boolean lattice denominator': lambda r, f: r[0].update(coordinate_lattice_denominator=True),
            'nonreduced direction': lambda r, f: r[0].update(ray_direction_integer_lattice=[2, 0, 0]),
            'false classification': lambda r, f: r[0].update(exact_classification_completed=False),
            'bool face': lambda r, f: r[0].update(original_face_index=True),
            'wrong flag reasons': lambda r, f: f[0].update(reasons=['short_ray']),
            'changed reasons': lambda r, f: r[0].update(original_numerical_reasons=[]),
            'duplicate rows': lambda r, f: r.append(copy.deepcopy(r[0])),
            'missing rows': lambda r, f: r.clear(),
            'error field': lambda r, f: r[0].update(error='incomplete'),
            'nan approximation': lambda r, f: r[0].update(conservative_first_solid_chord_mm_approx=float('nan')),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                rows, flags = exact_fixture(); mutate(rows, flags)
                with self.assertRaises(RuntimeError): a.validate_exact_rows(rows, flags)

    def test_boundary_mutations(self):
        mutations = [
            lambda row: row['classified_open_intervals'][3]['exact_midpoint_parity_witness'].update(boundary_faces=[]),
            lambda row: row['classified_open_intervals'][3]['exact_midpoint_parity_witness'].update(boundary_faces=[31]),
            lambda row: row['classified_open_intervals'][3].update(state='outside'),
            lambda row: row['all_forward_original_triangle_contacts'][2].update(coplanar_interval=False),
        ]
        for mutate in mutations:
            rows, flags = exact_fixture(True); mutate(rows[0])
            with self.assertRaises(RuntimeError): a.validate_exact_rows(rows, flags)


class SectionTests(unittest.TestCase):
    def test_positive(self):
        result = a.validate_sections(*section_fixture())
        self.assertEqual(result['sampled_layers'], 795)
        self.assertEqual(result['per_offset_layer_counts'], [265, 265, 265])

    def test_cgust_bound_schedule_controls(self):
        mutations = {
            'old WFU identity': lambda r: r.update(stl_sha256='8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0'),
            'old CGUST v8 identity': lambda r: r.update(stl_sha256='bce6cf52cd6f8e14fb92387218f398d15e84bd1f75bc218b3cfbcf39c351af3e'),
            'old WFU height': lambda r: r.update(z_max_mm=114.5),
            'old WFU layer count': lambda r: r.update(sampled_layers=1718),
            'old WFU per-offset count': lambda r: r['per_offset'][0].update(sampled_layers=573),
            'reordered equal-count offsets': lambda r: r['per_offset'].reverse(),
            'old AEUST identity': lambda r: r.update(stl_sha256='46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d'),
            'old AEUST height': lambda r: r.update(z_max_mm=119.0),
            'old AEUST layer count': lambda r: r.update(sampled_layers=1785),
            'old AEUST per-offset count': lambda r: r['per_offset'][0].update(sampled_layers=595),
            'reordered unequal counts': lambda r: (r['per_offset'][0].update(sampled_layers=572), r['per_offset'][2].update(sampled_layers=573)),
            'boolean per-offset count': lambda r: r['per_offset'][0].update(sampled_layers=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                report, detail, failures = section_fixture(); mutate(report)
                with self.assertRaises(RuntimeError): a.validate_sections(report, detail, failures)

    def test_mutations_fail_closed(self):
        mutations = {
            'missing layer': lambda r, d, f: d['layers'].pop(),
            'duplicate layer': lambda r, d, f: d['layers'].__setitem__(1, copy.deepcopy(d['layers'][0])),
            'missing polygon': lambda r, d, f: d['original_polygon_checks'].pop(),
            'duplicate polygon': lambda r, d, f: d['original_polygon_checks'].__setitem__(1, copy.deepcopy(d['original_polygon_checks'][0])),
            'missing polygon check': lambda r, d, f: d['original_polygon_checks'][0]['checks'].pop('erosion_valid'),
            'false polygon check': lambda r, d, f: d['original_polygon_checks'][0]['checks'].update(erosion_valid=False),
            'bad area sum': lambda r, d, f: d['layers'][0].update(section_area_mm2=101.),
            'lost polygon': lambda r, d, f: d['original_polygon_checks'][0].update(eroded_components=0),
            'invented count': lambda r, d, f: r.update(original_polygon_count=99999),
            'loss over limit': lambda r, d, f: d['original_polygon_checks'][0].update(opening_loss_fraction=.02),
            'loss ratio mismatch': lambda r, d, f: d['original_polygon_checks'][0].update(opening_loss_area_mm2=.4),
            'maximum mismatch': lambda r, d, f: r.update(maximum_individual_polygon_loss_fraction=.004),
            'bool index': lambda r, d, f: d['layers'][0].update(layer_index=False),
            'wrong source count': lambda r, d, f: d['layers'][0].update(segment_count=4),
            'bad source face': lambda r, d, f: d['layers'][0].update(source_face_indices=[1, 2, a.FACES]),
            'duplicate source face': lambda r, d, f: d['layers'][0].update(source_face_indices=[1, 2, 2]),
            'wrong hole accounting': lambda r, d, f: d['original_polygon_checks'][0].update(original_hole_count=1),
            'failure artifact': lambda r, d, f: f.append({'failed': True}),
            'wrong model': lambda r, d, f: r.update(stl_sha256='0' * 64),
            'nan loss': lambda r, d, f: d['original_polygon_checks'][0].update(opening_loss_fraction=float('nan')),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                report, detail, failures = section_fixture(); mutate(report, detail, failures)
                with self.assertRaises(RuntimeError): a.validate_sections(report, detail, failures)


class ContactTests(unittest.TestCase):
    def test_positive_iterator(self):
        report, rows = intersection_fixture()
        result = a.validate_intersection_contacts(report, iter(rows))
        self.assertEqual(result['actual_intersection_pair_count'], 2)
        self.assertEqual(result['candidate_pairs_checked'], 5)

    def test_mutations_fail_closed(self):
        mutations = {
            'truncated JSONL': lambda r, rows: rows.pop(),
            'extra JSONL': lambda r, rows: rows.append(copy.deepcopy(rows[0])),
            'duplicate pair': lambda r, rows: rows[1].update(face_indices=[1, 2]),
            'reversed pair': lambda r, rows: rows[0].update(face_indices=[2, 1]),
            'bad face': lambda r, rows: rows[0].update(face_indices=[1, a.FACES]),
            'bool face': lambda r, rows: rows[0].update(face_indices=[True, 2]),
            'unknown classification': lambda r, rows: r['classification_counts'].update(other=1),
            'wrong candidate total': lambda r, rows: r['broad_phase'].update(candidate_pairs_checked=4),
            'incomplete broad phase': lambda r, rows: r['broad_phase'].update(all_bbox_overlapping_pairs_completed=False),
            'wrong sweep axis': lambda r, rows: r['broad_phase'].update(sweep_axis=1),
            'wrong histogram': lambda r, rows: r['classification_counts'].update(allowed_shared_edge=2, allowed_shared_vertex=0),
            'bad reason': lambda r, rows: rows[0].update(reason='coplanar_positive_area_overlap'),
            'wrong dimension': lambda r, rows: rows[0]['intersection'].update(dimension=0),
            'repeated vertices': lambda r, rows: rows[0]['intersection'].update(vertices_exact_original_units=[['0', '0', '0'], ['0', '0', '0']]),
            'approx mismatch': lambda r, rows: rows[0]['intersection']['vertices_approx_original_units'][0].__setitem__(0, .1),
            'wrong artifact count': lambda r, rows: r['all_actual_intersections'].update(record_count=3),
            'escaped basename': lambda r, rows: r['all_actual_intersections'].update(path='../contacts.jsonl.gz'),
            'wrong coordinate lattice': lambda r, rows: r['lattice'].update(denominator='1'),
            'old WFU identity': lambda r, rows: r.update(stl_sha256='8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0'),
            'old CGUST v8 identity': lambda r, rows: r.update(stl_sha256='bce6cf52cd6f8e14fb92387218f398d15e84bd1f75bc218b3cfbcf39c351af3e'),
            'old WFU lattice and power': lambda r, rows: r['lattice'].update(denominator='72057594037927936', denominator_power_of_two=56),
            'old WFU power only': lambda r, rows: r['lattice'].update(denominator_power_of_two=56),
            'old AEUST lattice and power': lambda r, rows: r['lattice'].update(denominator='1073741824', denominator_power_of_two=30),
            'old AEUST power only': lambda r, rows: r['lattice'].update(denominator_power_of_two=30),
            'wrong lattice power 55': lambda r, rows: r['lattice'].update(denominator_power_of_two=55),
            'boolean lattice power': lambda r, rows: r['lattice'].update(denominator_power_of_two=True),
            'float lattice power': lambda r, rows: r['lattice'].update(denominator_power_of_two=23.0),
            'numeric contact denominator': lambda r, rows: r['lattice'].update(denominator=8388608),
            'boolean contact denominator': lambda r, rows: r['lattice'].update(denominator=True),
            'wrong model': lambda r, rows: r.update(stl_sha256='0' * 64),
            'nan coordinate': lambda r, rows: rows[0]['intersection']['vertices_approx_original_units'][0].__setitem__(0, math.nan),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                report, rows = intersection_fixture(); mutate(report, rows)
                with self.assertRaises(RuntimeError): a.validate_intersection_contacts(report, iter(rows))


class ProducerSumRegression(unittest.TestCase):
    """Recorded-value regression: match producer sum exactly, never a tolerance."""
    AREAS = [3624.0928109904253, 4.318929383277009, 4.318934923336203, 3024.4638867451927, 4.3189359773532505, 3.058937024325133, 4.318935977353249, 3.4189354435612254, 3.0589370243251324, 4.31893597735325, 3.418933874224478, 4.3189359773532505, 3.418919748529361, 4.318912654503948, 3.4189197494399615, 3.058924382552505, 4.318912654503947, 3.418918808134831, 3.0589243823363983, 4.318912654288678]
    LOSSES = [0.03927960762394215, 0.0037685919864517223, 0.0027466513160340424, 0.17852563641332286, 0.002746669838030051, 0.0029094780841685793, 0.003528747634152291, 0.0039959952053780215, 0.003516865454017535, 0.0035287476905937155, 0.00376941986493874, 0.002746669838030051, 0.003769762633827392, 0.002747225969272936, 0.0033438741810014705, 0.002933740256238788, 0.0035289965946401526, 0.0037278672722076667, 0.0036968020250865096, 0.0037895583398827627]

    def fixture(self):
        report,details,failures=section_fixture()
        old=details['original_polygon_checks'][0];new=[]
        for i,(area,loss) in enumerate(zip(self.AREAS,self.LOSSES)):
            polygon=copy.deepcopy(old);width=math.sqrt(area)
            polygon.update(original_polygon_index=i,original_area_mm2=area,
                bounds_mm=[0.,0.,width,width],minimum_rotated_bbox_width_mm=width,
                opening_loss_area_mm2=loss,opening_loss_fraction=loss/area,
                eroded_component_areas_mm2=[area*.5],opened_component_areas_mm2=[area-loss])
            new.append(polygon)
        details['original_polygon_checks'][:1]=new
        layer=details['layers'][0];layer.update(original_polygon_count=len(new),
            contour_count=len(new),segment_count=3*len(new),source_face_indices=list(range(3*len(new))),
            section_area_mm2=sum(self.AREAS),opening_loss_area_mm2=sum(self.LOSSES))
        report['original_polygon_count']=len(details['original_polygon_checks'])
        report['maximum_individual_polygon_loss_fraction']=max(x['opening_loss_fraction'] for x in details['original_polygon_checks'])
        return report,details,failures

    def test_builtin_area_accepts_and_naive_sum_rejects(self):
        report,details,failures=self.fixture();a.validate_sections(report,details,failures)
        naive=0.0
        for value in self.AREAS:naive+=value
        self.assertNotEqual(naive,sum(self.AREAS))
        details['layers'][0]['section_area_mm2']=naive
        with self.assertRaises(RuntimeError):a.validate_sections(report,details,failures)

    def test_builtin_loss_accepts_and_naive_sum_rejects(self):
        report,details,failures=self.fixture();a.validate_sections(report,details,failures)
        naive=0.0
        for value in self.LOSSES:naive+=value
        self.assertNotEqual(naive,sum(self.LOSSES))
        details['layers'][0]['opening_loss_area_mm2']=naive
        with self.assertRaises(RuntimeError):a.validate_sections(report,details,failures)


class LogicalMetadataControls(unittest.TestCase):
    def roots(self):
        root = Path('/synthetic-private-root')
        return {'stl': root / 'models/model.stl', 'qa-root': root / 'qa',
                'full-root': root / 'qa/v9-full', 'exact-normal': root / 'qa/v9-exact-normal',
                'exact-optimized': root / 'qa/v9-exact-optimized'}

    def test_exact_logical_roots_and_nested_precedence(self):
        paths = self.roots()
        self.assertEqual(reviewer.logical_path_bindings(paths), {key: key for key in reviewer.ROOT_KEYS})
        cases = [(paths['stl'], 'stl'),
                 (paths['qa-root'] / 'tools/source.py', 'qa-root/tools/source.py'),
                 (paths['full-root'] / 'normal/section.json', 'full-root/normal/section.json'),
                 (paths['full-root'] / 'optimized/contact.gz', 'full-root/optimized/contact.gz'),
                 (paths['exact-normal'] / 'rays.gz', 'exact-normal/rays.gz'),
                 (paths['exact-optimized'] / 'rays.gz', 'exact-optimized/rays.gz'),
                 (paths['full-root'], 'full-root')]
        for path, expected in cases:
            with self.subTest(logical=expected):
                self.assertEqual(reviewer.logical_key(path, paths), expected)

    def test_report_preserves_every_nonpath_value_and_input(self):
        paths = self.roots()
        payload = {'passed': True, 'original_numerical_strict_passed': False, 'model_go': False,
                   'optimization_level': 1, 'cpu_affinity': [0],
                   'input_path_bindings': {key: str(value) for key, value in paths.items()},
                   'modes': {'normal': {'exact': {'value': '16/25', 'actual_hex': '0x1.99999ap-1'},
                                        'nested': [1, 0.8, False, None, {'unanticipated_science': ['x', 'y']}]},
                             'optimized': {'all_records_checked': 10}},
                   'helper_sha256': 'a' * 64, 'unknown_future_scientific_field': {'preserve': [1, 2]}}
        tracked = {str(paths['stl']): {'bytes': 258884, 'sha256': 'b' * 64},
                   str(paths['full-root'] / 'normal/section.json'): {'bytes': 321, 'sha256': 'c' * 64},
                   str(paths['exact-normal'] / 'rays.gz'): {'bytes': 123, 'sha256': 'd' * 64}}
        before = copy.deepcopy((payload, paths, tracked))
        out = reviewer.report_for_output(payload, paths, tracked)
        self.assertEqual(set(out), set(payload) | {'evidence_inventory'})
        self.assertEqual({key: value for key, value in out.items() if key not in ('input_path_bindings', 'evidence_inventory')},
                         {key: value for key, value in payload.items() if key != 'input_path_bindings'})
        self.assertEqual(out['evidence_inventory'], {'stl': tracked[str(paths['stl'])],
            'full-root/normal/section.json': tracked[str(paths['full-root'] / 'normal/section.json')],
            'exact-normal/rays.gz': tracked[str(paths['exact-normal'] / 'rays.gz')]})
        self.assertEqual((payload, paths, tracked), before)
        self.assertNotIn('/synthetic-private-root', str(out))
        self.assertEqual(len(out['evidence_inventory']), len(tracked))

    def test_unscoped_unsafe_or_ambiguous_paths_rejected(self):
        paths = self.roots()
        cases = {
            'outside explicit roots': (lambda: reviewer.logical_key(Path('/elsewhere/file'), paths), 'Evidence path outside explicit CLI roots'),
            'relative evidence path': (lambda: reviewer.logical_key(Path('qa/file'), paths), 'Logical evidence path must be absolute and safe'),
            'parent traversal': (lambda: reviewer.logical_key(paths['qa-root'] / '../secret', paths), 'Logical evidence path must be absolute and safe'),
            'prefix sibling': (lambda: reviewer.logical_key(Path(str(paths['qa-root']) + '-other/file'), paths), 'Evidence path outside explicit CLI roots'),
            'missing root': (lambda: reviewer.logical_path_bindings({k: v for k, v in paths.items() if k != 'stl'}), 'Logical root set differs'),
            'unexpected root': (lambda: reviewer.logical_path_bindings({**paths, 'extra': Path('/extra')}), 'Logical root set differs'),
            'duplicate root aliases': (lambda: reviewer.logical_path_bindings({**paths, 'exact-normal': paths['full-root']}), 'Logical roots must be distinct'),
            'relative root': (lambda: reviewer.logical_path_bindings({**paths, 'qa-root': Path('relative')}), 'Logical roots must be absolute and safe'),
        }
        for name, (call, reason) in cases.items():
            with self.subTest(rejection=name):
                with self.assertRaisesRegex(RuntimeError, '^' + re.escape(reason) + '$'): call()

    def test_logical_inventory_collision_rejected(self):
        paths = self.roots(); name = str(paths['full-root'] / 'normal/file')
        tracked = {name: {'bytes': 1, 'sha256': 'a' * 64},
                   str(paths['full-root']) + '/normal/./file': {'bytes': 1, 'sha256': 'a' * 64}}
        with self.assertRaisesRegex(RuntimeError, 'Logical inventory key collision'):
            reviewer.report_for_output({'passed': False}, paths, tracked)


if __name__ == '__main__':
    unittest.main(verbosity=2)
