"""Fail-closed, stdlib-only structural/math review of bound CGUST v10 candidate artifacts.

No geometry predicates are rerun. The caller must authenticate every producer,
input and artifact hash, CSV provenance and process outcome separately. Passing
these checks never replaces the unchanged original numerical strict=False.
"""
from collections import Counter
from fractions import Fraction
import math
import re

FACES = 5176
LAYERS = 795
PER_OFFSET_LAYERS = (265, 265, 265)
LATTICE = 1 << 23
STL_SHA256 = '66f0516f35df2df734b6d8a4d37a8f93b73e5685fd47b0b7d74ff15c88ccf978'
OFFSETS = (.031, .071, .137)
REASONS = frozenset({
    'original_crossings_not_alternating_enter_exit',
    'near_coincident_or_opposing_original_crossings',
    'original_triangle_parity_controls_failed',
})
SECTION_CHECKS = frozenset({
    'all_three_offsets_have_layers',
    'all_original_sections_valid_without_repair',
    'every_original_polygon_checked',
    'all_original_polygons_survive_erosion_and_opening',
    'no_original_polygon_splits_after_erosion_or_opening',
    'all_opened_and_eroded_polygons_valid',
    'all_individual_polygon_losses_le_one_percent',
})
POLYGON_CHECKS = frozenset({
    'original_polygon_valid', 'erosion_valid', 'opening_valid',
    'survives_erosion', 'no_split_after_erosion', 'survives_opening',
    'no_split_after_opening', 'individual_polygon_loss_le_one_percent',
})
CONTACT_KINDS = frozenset({'allowed_shared_edge', 'allowed_shared_vertex'})
DISJOINT_KINDS = frozenset({
    'disjoint_coplanar', 'disjoint_noncoplanar', 'disjoint_plane_separated',
})


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def obj(value, label, keys=(), exact=False):
    require(type(value) is dict, label + ': expected object')
    require(all(type(k) is str for k in value), label + ': non-string key')
    require('error' not in value and 'error_type' not in value,
            label + ': error-bearing evidence')
    require(set(value) == set(keys) if exact else set(keys) <= set(value),
            label + ': required/allowed keys differ')
    return value


def seq(value, label, size=None):
    require(type(value) is list, label + ': expected list')
    require(size is None or len(value) == size, label + ': wrong length')
    return value


def integer(value, label, low=None, high=None):
    require(type(value) is int, label + ': expected typed integer')
    require(low is None or value >= low, label + ': below lower bound')
    require(high is None or value <= high, label + ': above upper bound')
    return value


def finite(value, label, low=None, positive=False):
    require(type(value) in (int, float), label + ': expected number')
    try:
        valid = math.isfinite(value)
    except (OverflowError, TypeError):
        valid = False
    require(valid, label + ': nonfinite number')
    require(low is None or value >= low, label + ': below lower bound')
    require(not positive or value > 0, label + ': must be positive')
    return value


def truth(value, label):
    require(value is True, label + ': required true')


def boolean(value, label):
    require(type(value) is bool, label + ': expected typed boolean')
    return value


def rational(value, label):
    require(type(value) is str and re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?', value),
            label + ': expected exact rational string')
    result = Fraction(value)
    require(str(result) == value, label + ': noncanonical rational string')
    return result


def positive_integer_text(value, label):
    result = rational(value, label)
    require(result.denominator == 1 and result > 0, label + ': expected positive integer text')
    return result.numerator


def digest(value, label):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value),
            label + ': invalid SHA256')
    return value


def checks(value, names, label):
    obj(value, label, names, exact=True)
    for key in names:
        truth(value[key], label + '.' + key)


def face_list(value, label, nonempty=False):
    seq(value, label)
    for face in value:
        integer(face, label + '.face', 0, FACES - 1)
    require(len(value) == len(set(value)), label + ': duplicate face')
    require(not nonempty or bool(value), label + ': empty face list')
    return value


def hex_fraction(value, label):
    require(type(value) is str, label + ': expected hexfloat string')
    match = re.fullmatch(r'([+-]?)0[xX]([0-9a-fA-F]+)(?:\.([0-9a-fA-F]*))?[pP]([+-]?[0-9]+)', value)
    require(match is not None, label + ': invalid lossless hexfloat')
    sign, whole, tail, exponent = match.groups()
    tail = tail or ''
    power = int(exponent)
    require(abs(power) <= 20000 and len(whole + tail) <= 10000,
            label + ': unreasonable descriptor size')
    result = Fraction(int(whole + tail, 16), 16 ** len(tail))
    result = result * (2 ** power) if power >= 0 else result / (2 ** -power)
    return -result if sign == '-' else result


def _sample_key(row, label):
    obj(row, label, ('original_face_index', 'sample_index'))
    return (integer(row['original_face_index'], label + '.face', 0, FACES - 1),
            integer(row['sample_index'], label + '.sample', 0, 9))


def validate_exact_rows(rows, flags):
    """Validate complete recorded-ray JSONL rows against unchanged decoded flags.

    Returns recomputed counts and exact minimum chord squared. Does not read CSV
    or authenticate producer hashes; the caller must do both independently.
    """
    seq(rows, 'exact rows'); seq(flags, 'original flags')
    require(bool(flags) and len(rows) == len(flags), 'Exact/flag count differs or is empty')
    flagmap = {}
    for flag in flags:
        key = _sample_key(flag, 'flag')
        require(key not in flagmap, 'Duplicate original flag')
        obj(flag, 'flag', ('original_cpp_row', 'reasons'))
        reasons = seq(flag['reasons'], 'flag reasons')
        require(bool(reasons) and all(type(r) is str and r in REASONS for r in reasons),
                'Unapproved original reason category')
        require(len(reasons) == len(set(reasons)), 'Duplicate original reason')
        obj(flag['original_cpp_row'], 'original CSV row')
        flagmap[key] = flag
    seen = set(); chord_squares = []; contact_count = interval_count = boundary_count = 0
    for row in rows:
        key = _sample_key(row, 'exact row')
        require(key in flagmap and key not in seen, 'Missing, duplicate or unexpected exact sample')
        seen.add(key)
        obj(row, 'exact row', (
            'exact_classification_completed', 'supplied_lossless_descriptor_line_classified',
            'original_run_lossless_descriptor_used', 'conservative_first_solid_chord_ge_0p8mm',
            'original_cpp_descriptor', 'original_numerical_reasons',
            'ray_origin_integer_lattice_numerators', 'ray_origin_integer_lattice_denominator',
            'ray_direction_integer_lattice', 'coordinate_lattice_denominator',
            'all_forward_original_triangle_contacts', 'classified_open_intervals',
            'first_entry_t', 'conservative_first_exit_t',
            'conservative_first_solid_chord_squared_mm2_exact',
            'conservative_first_solid_chord_mm_approx'))
        for field in ('exact_classification_completed', 'supplied_lossless_descriptor_line_classified',
                      'original_run_lossless_descriptor_used', 'conservative_first_solid_chord_ge_0p8mm'):
            truth(row[field], field)
        descriptor = obj(row['original_cpp_descriptor'], 'recorded descriptor')
        require(descriptor == flagmap[key]['original_cpp_row'] and
                row['original_numerical_reasons'] == flagmap[key]['reasons'],
                'Exact descriptor/reasons differ from original flag')
        require(all(type(v) is str for v in descriptor.values()), 'CSV descriptor has non-string values')
        require(descriptor.get('face') == str(key[0]) and descriptor.get('sample') == str(key[1]),
                'Descriptor sample identity differs')
        fields = ('x', 'y', 'z', 'nx', 'ny', 'nz', 'origin_x', 'origin_y', 'origin_z', 'dx', 'dy', 'dz')
        exact = {field: hex_fraction(descriptor.get(field + '_hex'), field) for field in fields}
        require(all(exact['d' + axis] == -exact['n' + axis] for axis in 'xyz'),
                'Recorded direction is not the exact negated original normal')
        den = positive_integer_text(row['coordinate_lattice_denominator'], 'coordinate lattice')
        require(den == LATTICE, 'Wrong frozen coordinate lattice')
        origin = seq(row['ray_origin_integer_lattice_numerators'], 'origin lattice', 3)
        direction = seq(row['ray_direction_integer_lattice'], 'direction lattice', 3)
        for value in origin + direction:
            integer(value, 'lattice coordinate')
        q = positive_integer_text(row['ray_origin_integer_lattice_denominator'], 'origin denominator')
        require(math.gcd(q, *origin) == 1, 'Origin lattice is not reduced')
        require(math.gcd(*direction) == 1, 'Direction lattice is zero or not reduced')
        require(all(Fraction(origin[i], q * den) == exact['origin_' + axis]
                    for i, axis in enumerate('xyz')), 'Origin differs from recorded hexfloat')
        given_direction = [exact['d' + axis] for axis in 'xyz']
        common = math.lcm(*(value.denominator for value in given_direction))
        numerators = [value.numerator * (common // value.denominator) for value in given_direction]
        divisor = math.gcd(*numerators)
        require(divisor != 0 and direction == [value // divisor for value in numerators],
                'Direction differs from recorded hexfloat')
        contacts = seq(row['all_forward_original_triangle_contacts'], 'all ray contacts')
        require(bool(contacts), 'Empty exact contact evidence')
        parsed = []; contacted_faces = set()
        for contact in contacts:
            obj(contact, 'ray contact', ('face', 't0', 't1', 'coplanar_interval',
                                        'edge_or_vertex_contact', 'directed_crossing'), exact=True)
            face = integer(contact['face'], 'ray contact face', 0, FACES - 1)
            require(face not in contacted_faces, 'Duplicate triangle ray contact')
            contacted_faces.add(face)
            low, high = rational(contact['t0'], 'contact t0'), rational(contact['t1'], 'contact t1')
            require(0 < low <= high, 'Recorded outside-origin contact has nonpositive/inverted range')
            coplanar = boolean(contact['coplanar_interval'], 'coplanar flag')
            edge = boolean(contact['edge_or_vertex_contact'], 'edge flag')
            crossing = integer(contact['directed_crossing'], 'directed crossing', -1, 1)
            require((crossing == 0 and edge) if coplanar else (low == high and crossing in (-1, 1)),
                    'Contact kind/dimension/crossing mismatch')
            parsed.append((low, high, face, coplanar, edge, crossing))
        require(parsed == sorted(parsed, key=lambda c: c[:3]), 'Contacts are not in exact producer order')
        breaks = sorted({Fraction(0)} | {value for c in parsed for value in c[:2]})
        require(len(breaks) >= 3, 'No distinct first entry and exit')
        entry, finish = breaks[1:3]
        require(any(c[2] == key[0] and c[0] == c[1] == entry and c[5] == -1 and not c[4]
                    for c in parsed), 'First contact lacks original interior entering face')
        require(rational(row['first_entry_t'], 'first entry') == entry and
                rational(row['conservative_first_exit_t'], 'first exit') == finish,
                'First entry/exit skips an exact contact')
        intervals = seq(row['classified_open_intervals'], 'all open intervals', len(breaks))
        for i, interval in enumerate(intervals):
            obj(interval, 'interval', ('t0', 't1', 'state', 'exact_midpoint_parity_witness'), exact=True)
            low = rational(interval['t0'], 'interval t0')
            high = rational(interval['t1'], 'interval t1') if interval['t1'] is not None else None
            expected_high = breaks[i + 1] if i + 1 < len(breaks) else None
            require(low == breaks[i] and high == expected_high, 'Missing, extra or changed interval boundary')
            state = interval['state']
            require(type(state) is str and state in ('inside', 'outside', 'boundary'), 'Unknown interval state')
            midpoint = (low + high) / 2 if high is not None else low + 1
            covering = {c[2] for c in parsed if c[3] and c[0] < midpoint < c[1]}
            require((state == 'boundary') == bool(covering), 'Boundary state disagrees with coplanar contacts')
            witness = obj(interval['exact_midpoint_parity_witness'], 'parity witness', ('direction', 'attempt'))
            attempt = integer(witness['attempt'], 'parity attempt', 1, 64)
            witness_direction = seq(witness['direction'], 'parity direction', 3)
            for value in witness_direction:
                integer(value, 'parity direction coordinate')
            require(witness_direction == [1, attempt, attempt * attempt + 1], 'Noncanonical parity witness direction')
            if state == 'boundary':
                obj(witness, 'boundary witness', ('direction', 'attempt', 'boundary_faces'), exact=True)
                require(attempt == 1, 'Boundary witness must resolve at first direction')
                faces = face_list(witness['boundary_faces'], 'boundary faces', nonempty=True)
                require(set(faces) == covering, 'Boundary witness omits/adds covering original faces')
                boundary_count += 1
            else:
                obj(witness, 'crossing witness', ('direction', 'attempt', 'crossing_faces', 'crossing_t'), exact=True)
                faces = face_list(witness['crossing_faces'], 'witness crossing faces')
                times = [rational(v, 'parity crossing t') for v in seq(witness['crossing_t'], 'parity crossing times', len(faces))]
                require(all(v > 0 for v in times) and all(a < b for a, b in zip(times, times[1:])),
                        'Nonpositive, repeated or unsorted parity crossing')
                require((len(times) % 2 == 1) == (state == 'inside'), 'Witness parity disagrees with interval')
        require(intervals[0]['state'] == 'outside' and intervals[1]['state'] == 'inside' and
                intervals[-1]['state'] == 'outside', 'First/final interval state fails')
        square = (finish - entry) ** 2 * sum(v * v for v in direction) / (den * den)
        require(rational(row['conservative_first_solid_chord_squared_mm2_exact'], 'first chord squared') == square,
                'Exact chord square differs from lattice ray and first contacts')
        require(square >= Fraction(16, 25), 'Exact conservative first chord is below 0.8 mm')
        approx = finite(row['conservative_first_solid_chord_mm_approx'], 'approximate chord', positive=True)
        require(math.isclose(approx, math.sqrt(float(square)), rel_tol=1e-12, abs_tol=1e-12),
                'Approximate chord contradicts exact chord')
        chord_squares.append(square); contact_count += len(contacts); interval_count += len(intervals)
    require(seen == set(flagmap), 'Incomplete exact flag coverage')
    return {'flag_count': len(flags), 'ray_contact_count': contact_count,
            'interval_count': interval_count, 'boundary_interval_count': boundary_count,
            'minimum_first_chord_squared_mm2_exact': str(min(chord_squares))}


def validate_sections(report, details, failures):
    """Validate all 795 layer records and every original polygon check."""
    obj(report, 'section report', ('checks', 'passed', 'strict_passed', 'stl_sha256',
        'z_min_mm', 'z_max_mm', 'pitch_mm', 'offsets_from_z_min_mm',
        'opening_reference_width_mm', 'per_polygon_loss_limit', 'per_offset',
        'sampled_layers', 'original_polygon_count', 'failed_layer_count',
        'failed_polygon_count', 'maximum_individual_polygon_loss_fraction'))
    truth(report['passed'], 'section passed'); truth(report['strict_passed'], 'section strict_passed')
    require(report['stl_sha256'] == STL_SHA256, 'Section STL identity differs')
    checks(report['checks'], SECTION_CHECKS, 'section checks')
    for field, expected in (('z_min_mm', 0), ('z_max_mm', 53.0), ('pitch_mm', .2),
                            ('opening_reference_width_mm', .8), ('per_polygon_loss_limit', .01)):
        require(finite(report[field], field) == expected, 'Section policy/bounds differ: ' + field)
    offsets = seq(report['offsets_from_z_min_mm'], 'section offsets', 3)
    require(all(finite(v, 'section offset') == expected for v, expected in zip(offsets, OFFSETS)),
            'Wrong layer offsets')
    require(integer(report['sampled_layers'], 'sampled layers') == LAYERS, 'Incomplete layer count')
    per_offset = seq(report['per_offset'], 'per-offset counts', 3)
    for record, expected, count in zip(per_offset, OFFSETS, PER_OFFSET_LAYERS):
        obj(record, 'per-offset record', ('offset_mm', 'sampled_layers'), exact=True)
        require(finite(record['offset_mm'], 'per-offset offset') == expected and
                integer(record['sampled_layers'], 'per-offset count') == count, 'Per-offset coverage differs')
    obj(details, 'section detail', ('layers', 'original_polygon_checks'), exact=True)
    layers = seq(details['layers'], 'section layers', LAYERS)
    polygons = seq(details['original_polygon_checks'], 'original polygon checks')
    require(bool(polygons) and integer(report['original_polygon_count'], 'polygon count', 1) == len(polygons),
            'Original polygon total differs')
    require(integer(report['failed_layer_count'], 'failed layers') == 0 and
            integer(report['failed_polygon_count'], 'failed polygons') == 0,
            'Failed section record count is nonzero')
    require(seq(failures, 'section failures') == [], 'Section failure artifact is nonempty')
    schedule = [(offset, index) for offset, count in zip(OFFSETS, PER_OFFSET_LAYERS) for index in range(count)]
    cursor = 0; losses = []
    for layer, (offset, index) in zip(layers, schedule):
        obj(layer, 'layer', ('layer_id', 'offset_mm', 'layer_index', 'z_mm', 'segment_count',
                            'contour_count', 'source_face_indices', 'valid_original_section',
                            'original_polygon_count', 'section_area_mm2', 'opening_loss_area_mm2', 'passed'))
        identity = f'{offset:.3f}:{index}'; z = offset + .2 * index
        require(type(layer['layer_id']) is str and layer['layer_id'] == identity and
                finite(layer['offset_mm'], 'layer offset') == offset and
                integer(layer['layer_index'], 'layer index') == index and
                finite(layer['z_mm'], 'layer z') == z, 'Missing, duplicated or changed layer schedule')
        truth(layer['valid_original_section'], 'valid original section'); truth(layer['passed'], 'layer passed')
        sources = face_list(layer['source_face_indices'], 'section source faces', nonempty=True)
        require(sources == sorted(sources) and integer(layer['segment_count'], 'segments', 3) == len(sources),
                'Section segment/source-face coverage differs')
        count = integer(layer['original_polygon_count'], 'layer polygon count', 1)
        contours = integer(layer['contour_count'], 'layer contours', 1)
        require(cursor + count <= len(polygons), 'Missing polygon records')
        matching = polygons[cursor:cursor + count]; cursor += count
        holes = 0
        for polygon_index, polygon in enumerate(matching):
            obj(polygon, 'polygon', ('layer_id', 'offset_mm', 'layer_index', 'z_mm', 'original_polygon_index',
                'bounds_mm', 'original_area_mm2', 'original_hole_count', 'minimum_rotated_bbox_width_mm',
                'eroded_components', 'opened_components', 'eroded_component_areas_mm2',
                'opened_component_areas_mm2', 'opening_loss_area_mm2', 'opening_loss_fraction',
                'opening_gain_area_mm2', 'loss_outside_0p41_vertex_disks_mm2', 'checks', 'passed'))
            require(type(polygon['layer_id']) is str and polygon['layer_id'] == identity and
                    finite(polygon['offset_mm'], 'polygon offset') == offset and
                    integer(polygon['layer_index'], 'polygon layer index') == index and
                    finite(polygon['z_mm'], 'polygon z') == z and
                    integer(polygon['original_polygon_index'], 'polygon index') == polygon_index,
                    'Polygon identity/order/coverage differs')
            checks(polygon['checks'], POLYGON_CHECKS, 'polygon checks'); truth(polygon['passed'], 'polygon passed')
            area = finite(polygon['original_area_mm2'], 'original polygon area', positive=True)
            loss = finite(polygon['opening_loss_area_mm2'], 'polygon loss', low=0)
            fraction = finite(polygon['opening_loss_fraction'], 'polygon loss fraction', low=0)
            require(fraction == loss / area and fraction <= .01, 'Polygon loss fraction is inconsistent or exceeds limit')
            bounds = seq(polygon['bounds_mm'], 'polygon bounds', 4)
            for value in bounds: finite(value, 'polygon bound')
            require(bounds[0] < bounds[2] and bounds[1] < bounds[3], 'Degenerate polygon bounds')
            holes += integer(polygon['original_hole_count'], 'polygon hole count', 0)
            finite(polygon['minimum_rotated_bbox_width_mm'], 'polygon bbox width', positive=True)
            for kind in ('eroded', 'opened'):
                require(integer(polygon[kind + '_components'], kind + ' components') == 1,
                        'Polygon disappeared or split')
                values = seq(polygon[kind + '_component_areas_mm2'], kind + ' areas', 1)
                finite(values[0], kind + ' area', positive=True)
            finite(polygon['opening_gain_area_mm2'], 'opening gain', low=0)
            finite(polygon['loss_outside_0p41_vertex_disks_mm2'], 'loss outside vertex disks', low=0)
            losses.append(fraction)
        # Match check_sections.py's original builtin-sum accumulation semantics.
        # Exact equality remains required; no tolerance or threshold is added.
        area_sum = sum(p['original_area_mm2'] for p in matching)
        loss_sum = sum(p['opening_loss_area_mm2'] for p in matching)
        require(contours == count + holes and len(sources) >= 3 * contours, 'Contour/polygon/hole counts differ')
        require(finite(layer['section_area_mm2'], 'layer area', positive=True) == area_sum and
                finite(layer['opening_loss_area_mm2'], 'layer loss', low=0) == loss_sum,
                'Layer area/loss totals differ from all polygon records')
    require(cursor == len(polygons), 'Extra polygon records outside layer coverage')
    maximum = finite(report['maximum_individual_polygon_loss_fraction'], 'maximum polygon loss', low=0)
    require(maximum == max(losses), 'Maximum individual polygon loss summary differs')
    return {'sampled_layers': LAYERS, 'original_polygon_count': len(polygons),
            'maximum_individual_polygon_loss_fraction': maximum,
            'per_offset_layer_counts': list(PER_OFFSET_LAYERS)}


def validate_intersection_contacts(report, iterator):
    """Validate parsed contact objects from an iterator, counts and pair uniqueness.

    The candidate digest is syntax/metadata checked, not recomputed: disjoint
    candidate pairs are absent from the contact artifact by design.
    """
    obj(report, 'intersection report', ('passed', 'strict_passed', 'completed',
        'input_unchanged_during_check', 'stl_sha256', 'stl_sha256_after_check',
        'original_face_count', 'face_index_base', 'total_unordered_original_face_pairs',
        'degenerate_original_faces', 'bad_pairs', 'bad_pair_count', 'lattice',
        'broad_phase', 'classification_counts', 'actual_intersection_pair_count', 'all_actual_intersections'))
    for key in ('passed', 'strict_passed', 'completed', 'input_unchanged_during_check'):
        truth(report[key], 'intersection ' + key)
    require(report['stl_sha256'] == report['stl_sha256_after_check'] == STL_SHA256,
            'Intersection STL identity differs')
    require(integer(report['original_face_count'], 'intersection faces') == FACES and
            integer(report['face_index_base'], 'face index base') == 0 and
            integer(report['total_unordered_original_face_pairs'], 'all face pairs') == FACES * (FACES - 1) // 2,
            'Intersection original-face pair domain differs')
    require(seq(report['degenerate_original_faces'], 'degenerate faces') == [] and
            seq(report['bad_pairs'], 'bad pairs') == [] and
            integer(report['bad_pair_count'], 'bad pair count') == 0, 'Bad/degenerate contact evidence')
    lattice = obj(report['lattice'], 'intersection lattice', ('denominator', 'denominator_power_of_two',
        'exact_coordinate_round_trips_checked', 'all_original_coordinates_round_trip_exactly'))
    require(positive_integer_text(lattice['denominator'], 'intersection denominator') == LATTICE and
            integer(lattice['denominator_power_of_two'], 'denominator power') == 23 and
            integer(lattice['exact_coordinate_round_trips_checked'], 'coordinate round trips') == 9 * FACES,
            'Intersection exact lattice binding differs')
    truth(lattice['all_original_coordinates_round_trip_exactly'], 'exact coordinate round trips')
    broad = obj(report['broad_phase'], 'broad phase', ('sweep_axis', 'axis_active_pair_costs',
        'all_bbox_overlapping_pairs_completed', 'candidate_pairs_checked', 'candidate_sequence_sha256'))
    truth(broad['all_bbox_overlapping_pairs_completed'], 'broad phase completed')
    axis = integer(broad['sweep_axis'], 'sweep axis', 0, 2)
    costs = seq(broad['axis_active_pair_costs'], 'axis active costs', 3)
    total_pairs = FACES * (FACES - 1) // 2
    for cost in costs: integer(cost, 'axis active cost', 0, total_pairs)
    require(axis == min(range(3), key=lambda a: costs[a]), 'Sweep axis does not match deterministic minimum')
    candidates = integer(broad['candidate_pairs_checked'], 'candidate count', 1, total_pairs)
    require(candidates <= costs[axis], 'Closed-AABB candidate count exceeds sweep active count')
    digest(broad['candidate_sequence_sha256'], 'candidate sequence digest')
    counts = obj(report['classification_counts'], 'classification counts')
    require(bool(counts) and set(counts) <= CONTACT_KINDS | DISJOINT_KINDS,
            'Unexpected/empty intersection classification categories')
    for value in counts.values(): integer(value, 'classification count', 1, candidates)
    require(sum(counts.values()) == candidates, 'Candidate count differs from classification total')
    meta = obj(report['all_actual_intersections'], 'contact artifact metadata', ('record_count', 'path', 'sha256', 'format'))
    require(type(meta['path']) is str and bool(meta['path']) and '/' not in meta['path'] and
            '\\' not in meta['path'] and meta['path'] not in ('.', '..'), 'Nonlocal contact artifact basename')
    require(meta['format'] == 'gzip JSON Lines; one exact intersection per line', 'Unexpected contact artifact format')
    digest(meta['sha256'], 'contact artifact digest')
    expected = integer(report['actual_intersection_pair_count'], 'actual contact count', 1, candidates)
    require(integer(meta['record_count'], 'contact metadata count') == expected, 'Contact metadata count differs')
    seen = set(); histogram = Counter(); count = 0
    for record in iterator:
        obj(record, 'intersection contact', ('face_indices', 'reason', 'shared_original_vertex_count', 'intersection'), exact=True)
        pair = seq(record['face_indices'], 'contact pair', 2)
        i, j = (integer(v, 'contact face', 0, FACES - 1) for v in pair)
        require(i < j and (i, j) not in seen, 'Unordered, duplicate or self contact pair')
        seen.add((i, j)); count += 1
        require(count <= expected, 'Extra contact JSONL rows')
        reason = record['reason']
        require(type(reason) is str and reason in CONTACT_KINDS, 'Nonallowed intersection contact')
        size = 2 if reason == 'allowed_shared_edge' else 1
        require(integer(record['shared_original_vertex_count'], 'shared vertex count') == size,
                'Allowed contact shared-vertex count differs')
        geometry = obj(record['intersection'], 'contact geometry',
                       ('dimension', 'vertices_exact_original_units', 'vertices_approx_original_units'), exact=True)
        require(integer(geometry['dimension'], 'contact dimension') == size - 1, 'Allowed contact dimension differs')
        exact_points = seq(geometry['vertices_exact_original_units'], 'exact contact vertices', size)
        approx_points = seq(geometry['vertices_approx_original_units'], 'approximate contact vertices', size)
        points = []
        for exact_point, approx_point in zip(exact_points, approx_points):
            values = tuple(rational(v, 'exact vertex coordinate') for v in seq(exact_point, 'exact vertex', 3))
            approx = seq(approx_point, 'approximate vertex', 3)
            for exact_value, value in zip(values, approx):
                finite(value, 'approximate vertex coordinate')
                require(float(exact_value) == value, 'Approximate vertex differs from exact coordinate')
                require((exact_value * LATTICE).denominator == 1,
                        'Allowed shared vertex is absent from frozen coordinate lattice')
            points.append(values)
        require(points == sorted(set(points)) and len(points) == size,
                'Shared contact vertices are repeated or unsorted')
        histogram[reason] += 1
    require(count == expected, 'Truncated contact JSONL artifact')
    require(dict(histogram) == {k: v for k, v in counts.items() if k in CONTACT_KINDS},
            'Contact JSONL reason counts differ from report')
    disjoint = sum(value for key, value in counts.items() if key in DISJOINT_KINDS)
    require(count + disjoint == candidates, 'Contact/disjoint candidate accounting differs')
    return {'candidate_pairs_checked': candidates, 'actual_intersection_pair_count': count,
            'contact_reason_counts': dict(sorted(histogram.items())),
            'disjoint_candidate_count': disjoint,
            'candidate_sequence_sha256': broad['candidate_sequence_sha256']}
