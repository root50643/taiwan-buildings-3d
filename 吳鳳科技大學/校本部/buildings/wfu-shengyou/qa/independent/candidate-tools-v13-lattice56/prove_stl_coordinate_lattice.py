"""Derive this exact STL's minimal binary32 coordinate lattice independently.

Reads all nine vertex coordinates per original triangle. No producer reports,
candidate parser, geometry predicates, Blender or rendering are used.
Caller owns the shared single-CPU slot. Original inputs remain read-only.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import stat
import struct
import sys

STL_SHA256 = '8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0'
FACES = 20946
STL_BYTES = 84 + 50 * FACES
EXPECTED_COORDINATES = 9 * FACES
EXPECTED_POWER = 56
EXPECTED_LATTICE = 72057594037927936


def require(value, message):
    if not value:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_original(path):
    path = Path(path).absolute()
    require(path.anchor == '/' and all(x not in ('', '.', '..') for x in path.parts[1:]),
            'Unsafe STL path')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    directory = os.open('/', flags)
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=directory)
    finally:
        os.close(directory)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size == STL_BYTES,
                'Wrong STL type or byte count')
        with os.fdopen(fd, 'rb') as stream:
            fd = None
            data = stream.read(STL_BYTES + 1)
            after = os.fstat(stream.fileno())
    finally:
        if fd is not None:
            os.close(fd)
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    require(all(getattr(before, key) == getattr(after, key) for key in fields),
            'STL changed during read')
    require(len(data) == STL_BYTES and digest(data) == STL_SHA256,
            'Exact original STL bytes/hash differ')
    return data


def coordinates(data):
    for face in range(FACES):
        # A binary STL record is 12 normal bytes, 36 vertex bytes, 2 attributes.
        start = 84 + 50 * face + 12
        for index, value in enumerate(struct.unpack_from('<9f', data, start)):
            yield face, index, start + 4 * index, value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(len(os.sched_getaffinity(0)) == 1, 'One CPU required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh proof output required')
    source = Path(__file__).read_bytes()
    data = read_original(args.stl)
    require(struct.unpack_from('<I', data, 80)[0] == FACES, 'Wrong original face count')
    common = 1
    maximum_power = count = old_lattice_failures = 0
    witness = None
    for face, index, offset, value in coordinates(data):
        require(math.isfinite(value), 'Nonfinite original coordinate')
        numerator, denominator = value.as_integer_ratio()
        require(denominator > 0 and denominator & (denominator - 1) == 0,
                'Coordinate denominator is not a power of two')
        power = denominator.bit_length() - 1
        common = math.lcm(common, denominator)
        if power > maximum_power:
            maximum_power = power
            witness = {'face_index': face, 'vertex_index': index // 3,
                       'axis': 'xyz'[index % 3], 'byte_offset': offset,
                       'original_float32_little_endian_hex': data[offset:offset + 4].hex(),
                       'exact_float_hex': value.hex(), 'numerator': str(numerator),
                       'denominator': str(denominator), 'denominator_power_of_two': power}
        old_lattice_failures += int((numerator * (1 << 30)) % denominator != 0)
        count += 1
    require(count == EXPECTED_COORDINATES and common == EXPECTED_LATTICE
            and maximum_power == EXPECTED_POWER and common == 1 << maximum_power,
            'Independently derived minimal coordinate lattice differs')
    require(witness is not None and witness['denominator'] == str(common)
            and old_lattice_failures > 0, 'Missing minimality/old-lattice rejection witness')
    round_trips = signed_zero_coordinates = 0
    for _, _, offset, value in coordinates(data):
        numerator, denominator = value.as_integer_ratio()
        require(common % denominator == 0, 'Derived lattice omits an original coordinate')
        lattice_integer = numerator * (common // denominator)
        recovered = Fraction(lattice_integer, common)
        require(recovered == Fraction(numerator, denominator), 'Exact rational round trip differs')
        recovered_float = float(recovered)
        if numerator == 0:
            # Rational zero has no sign; explicitly retain the original zero sign.
            signed_zero_coordinates += int(math.copysign(1.0, value) < 0)
            recovered_float = math.copysign(0.0, value)
        require(struct.pack('<f', recovered_float) == data[offset:offset + 4],
                'Original binary32 coordinate byte round trip differs')
        round_trips += 1
    require(round_trips == EXPECTED_COORDINATES, 'Incomplete original coordinate round trips')
    require(read_original(args.stl) == data and Path(__file__).read_bytes() == source,
            'Original STL or proof source changed')
    result = {'passed': True, 'completed': True, 'optimization_level': sys.flags.optimize,
              'cpu_affinity': sorted(os.sched_getaffinity(0)), 'stl_sha256': STL_SHA256,
              'stl_bytes': len(data), 'original_faces': FACES,
              'original_coordinate_values_checked': count,
              'coordinate_denominator_lcm': str(common), 'maximum_denominator_power': maximum_power,
              'minimality_witness': witness, 'exact_rational_round_trips': round_trips,
              'binary32_byte_round_trips': round_trips,
              'negative_zero_signs_preserved_explicitly': signed_zero_coordinates,
              'coordinates_not_representable_on_old_2p30_lattice': old_lattice_failures,
              'source_sha256': digest(source), 'original_input_and_source_unchanged': True,
              'producer_reports_read': False, 'candidate_parser_imported': False,
              'geometry_predicates_or_render_rerun': False, 'model_go': False,
              'scope': 'Exact original binary32 vertex-coordinate denominator LCM and round trips only. '
                       'This is an independent case-constant proof, not model/science acceptance.'}
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': True, 'coordinate_count': count, 'lattice_power': maximum_power}))


if __name__ == '__main__':
    main()
