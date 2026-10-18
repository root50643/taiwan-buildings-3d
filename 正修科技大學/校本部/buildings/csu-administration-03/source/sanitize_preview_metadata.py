"""Replace only a private PNG tEXt/File value; never re-encode IDAT or pixels.

Run from the task directory:
  python source/sanitize_preview_metadata.py --private-backup-dir PRIVATE_DIR

PRIVATE_DIR must be inside --task-root (default: the working directory), outside
this deliverable. Original bytes are retained there. Only the 16 named preview
PNGs and the new redaction mapping are written inside the deliverable. Historical
render manifests, scenes, geometry, and other sources are never rewritten.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT/'qa/documentation-revision-1/png-metadata-redaction.json'
SIGNATURE = b'\x89PNG\r\n\x1a\n'
PRIVATE = re.compile(rb'C:[\\/]+Users[\\/]', re.I)
NAMES = ['exploded-two-parts', 'front-elevation', 'front-three-quarter',
         'left-elevation', 'rear-elevation', 'rear-three-quarter',
         'right-elevation', 'top']
TARGETS = [f'previews/{version}/{name}.png' for version in ['v1', 'v2'] for name in NAMES]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def chunks(raw):
    assert raw[:8] == SIGNATURE, 'PNG signature mismatch'
    result = []
    pos = 8
    while pos < len(raw):
        size, kind = struct.unpack_from('>I4s', raw, pos)
        end = pos+size+12
        assert end <= len(raw), 'Truncated PNG chunk'
        data = raw[pos+8:pos+8+size]
        crc = struct.unpack_from('>I', raw, pos+8+size)[0]
        assert zlib.crc32(kind+data) & 0xffffffff == crc, 'PNG CRC mismatch'
        result.append((kind, data, raw[pos:end]))
        pos = end
        if kind == b'IEND':
            break
    assert pos == len(raw) and result[-1][0] == b'IEND', 'Unexpected trailing PNG bytes'
    return result


def decoded_pixels(parts):
    width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', parts[0][1])
    assert parts[0][0] == b'IHDR' and depth == 8 and color in (2, 6)
    assert compression == filtering == interlace == 0, 'Only noninterlaced RGB8/RGBA8 previews are supported'
    channels = 3 if color == 2 else 4
    stride = width*channels
    filtered = zlib.decompress(b''.join(data for kind, data, _ in parts if kind == b'IDAT'))
    assert len(filtered) == height*(stride+1)
    previous = bytearray(stride)
    pixels = bytearray()
    for y in range(height):
        start = y*(stride+1)
        method = filtered[start]
        assert method in range(5), 'Unknown PNG row filter'
        row = bytearray(filtered[start+1:start+1+stride])
        for x in range(stride):
            left = row[x-channels] if x >= channels else 0
            up = previous[x]
            upper_left = previous[x-channels] if x >= channels else 0
            if method == 1:
                predictor = left
            elif method == 2:
                predictor = up
            elif method == 3:
                predictor = (left+up)//2
            elif method == 4:
                p = left+up-upper_left
                distances = (abs(p-left), abs(p-up), abs(p-upper_left))
                predictor = (left, up, upper_left)[distances.index(min(distances))]
            else:
                predictor = 0
            row[x] = (row[x]+predictor) & 255
        pixels.extend(row)
        previous = row
    return bytes(pixels), [width, height], 'RGB8' if channels == 3 else 'RGBA8'


def scrub(raw, relative_scene):
    parts = chunks(raw)
    changed = []
    output = bytearray(SIGNATURE)
    for index, (kind, data, encoded) in enumerate(parts):
        if kind == b'tEXt' and data.split(b'\0', 1)[0] == b'File' and PRIVATE.search(data):
            new_data = b'File\0'+relative_scene.encode('ascii')
            replacement = (struct.pack('>I', len(new_data))+kind+new_data
                           +struct.pack('>I', zlib.crc32(kind+new_data) & 0xffffffff))
            output.extend(replacement)
            changed.append({'index':index, 'type':'tEXt', 'keyword':'File',
                'original_chunk_bytes':len(encoded), 'delivered_chunk_bytes':len(replacement),
                'original_chunk_sha256':sha(encoded), 'delivered_chunk_sha256':sha(replacement),
                'original_value':'[private host path; original bytes retained in private copy]',
                'delivered_value':relative_scene})
        else:
            output.extend(encoded)
    assert len(changed) == 1, 'Expected exactly one private tEXt/File chunk'
    return bytes(output), parts, changed


def metadata_private_flags(path):
    flags = []
    for index, (kind, data, _) in enumerate(chunks(path.read_bytes())):
        if kind in (b'IHDR', b'IDAT', b'IEND', b'PLTE', b'tRNS'):
            continue
        candidates = [data, data.replace(b'\0', b'')]
        if kind == b'zTXt':
            candidates.append(zlib.decompress(data.split(b'\0', 1)[1][1:]))
        elif kind == b'iTXt':
            _, rest = data.split(b'\0', 1)
            compressed, method = rest[0:2]
            text = rest[2:].split(b'\0', 2)[2]
            candidates.append(zlib.decompress(text) if compressed else text)
        if any(PRIVATE.search(value) for value in candidates):
            flags.append({'chunk_index':index, 'chunk_type':kind.decode('ascii')})
    return flags


def audit_all_pngs():
    return [{'path':p.relative_to(ROOT).as_posix(), 'private_path_flags':metadata_private_flags(p)}
            for p in sorted(ROOT.rglob('*.png'))]


def protected_hashes():
    return {p.relative_to(ROOT).as_posix():sha(p.read_bytes())
            for p in sorted(ROOT.rglob('*')) if p.is_file()
            and (p.suffix in ('.stl', '.blend') or p.name == 'render-manifest.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-backup-dir', required=True, type=Path)
    parser.add_argument('--task-root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    task = args.task_root.resolve()
    backup = args.private_backup_dir.resolve()
    backup.relative_to(task)  # Refuse an unaccounted external destination.
    assert not backup.is_relative_to(ROOT), 'Private original PNGs must stay outside the deliverable'
    if REPORT.exists():
        old = json.loads(REPORT.read_text(encoding='utf8'))
        assert [f['path'] for f in old['files']] == TARGETS
        for record in old['files']:
            assert sha((ROOT/record['path']).read_bytes()) == record['delivered_sha256']
            assert sha((task/record['private_copy_path']).read_bytes()) == record['original_sha256']
        assert not any(p['private_path_flags'] for p in audit_all_pngs())
        print('Existing redaction mapping and private originals verified; no files rewritten.')
        return
    frozen_path = ROOT/'qa/documentation-revision-1/frozen-inputs-at-76681.json'
    frozen = {f['path']:f for f in json.loads(frozen_path.read_text(encoding='utf8'))['files']}
    protected_before = protected_hashes()
    prepared = []
    # Prepare and validate all changes before writing any delivered PNG.
    for relative in TARGETS:
        path = ROOT/relative
        original = path.read_bytes()
        assert len(original) == frozen[relative]['bytes'] and sha(original) == frozen[relative]['sha256']
        relative_scene = f'models/{Path(relative).parts[1]}/scene.blend'
        delivered, before, changed = scrub(original, relative_scene)
        after = chunks(delivered)
        assert len(before) == len(after)
        changed_indices = [i for i, (a, b) in enumerate(zip(before, after)) if a[2] != b[2]]
        assert changed_indices == [changed[0]['index']]
        idat_before = b''.join(data for kind, data, _ in before if kind == b'IDAT')
        idat_after = b''.join(data for kind, data, _ in after if kind == b'IDAT')
        pixels_before, dimensions, mode = decoded_pixels(before)
        pixels_after, dimensions_after, mode_after = decoded_pixels(after)
        assert idat_before == idat_after and pixels_before == pixels_after
        assert dimensions == dimensions_after and mode == mode_after
        private_copy = backup/relative
        if private_copy.exists():
            assert private_copy.read_bytes() == original, 'Existing private copy differs'
        prepared.append((path, original, delivered, private_copy, {
            'path':relative, 'original_bytes':len(original), 'original_sha256':sha(original),
            'delivered_bytes':len(delivered), 'delivered_sha256':sha(delivered),
            'idat_sha256_before':sha(idat_before), 'idat_sha256_after':sha(idat_after),
            'pixels_sha256_before':sha(pixels_before), 'pixels_sha256_after':sha(pixels_after),
            'dimensions':dimensions, 'decoded_mode':mode,
            'private_copy_path':private_copy.relative_to(task).as_posix(),
            'chunk_count_before':len(before), 'chunk_count_after':len(after),
            'chunk_changes':changed, 'all_other_chunks_byte_identical':True}))
    for _, original, _, private_copy, _ in prepared:
        private_copy.parent.mkdir(parents=True, exist_ok=True)
        if not private_copy.exists():
            private_copy.write_bytes(original)
        assert private_copy.read_bytes() == original
    for path, _, delivered, _, _ in prepared:
        path.write_bytes(delivered)
        assert path.read_bytes() == delivered
    png_audit = audit_all_pngs()
    protected_after = protected_hashes()
    records = [record for *_, record in prepared]
    checks = {'exact_16_named_targets':len(records)==16 and [r['path'] for r in records]==TARGETS,
        'original_hashes_match_frozen_baseline':all(r['original_sha256']==frozen[r['path']]['sha256'] for r in records),
        'exactly_one_File_chunk_changed_per_png':all(len(r['chunk_changes'])==1 for r in records),
        'all_other_chunks_byte_identical':all(r['all_other_chunks_byte_identical'] for r in records),
        'idat_sha256_unchanged':all(r['idat_sha256_before']==r['idat_sha256_after'] for r in records),
        'decoded_pixels_sha256_unchanged':all(r['pixels_sha256_before']==r['pixels_sha256_after'] for r in records),
        'original_private_copies_verified':all(sha(private_copy.read_bytes())==record['original_sha256'] for _, _, _, private_copy, record in prepared),
        'all_current_png_metadata_free_of_private_paths':not any(p['private_path_flags'] for p in png_audit),
        'protected_STLs_scenes_render_manifests_unchanged':protected_before==protected_after}
    report = {'scope':'Documentation revision 1; private PNG File metadata only; historical render manifests unchanged',
        'source':'source/sanitize_preview_metadata.py', 'source_sha256':sha(Path(__file__).read_bytes()),
        'baseline_commit':'76681c5dcedc88d684946780e795d7914a88c075',
        'pixel_hash_definition':'SHA256 of decoded native RGB8/RGBA8 row-major channel bytes; no PNG row filter bytes. Dimensions and IHDR remain unchanged.',
        'idat_hash_definition':'SHA256 of concatenated IDAT chunk payloads in original order; individual IDAT chunks also byte-identical.',
        'files':records, 'checks':checks, 'current_png_count':len(png_audit),
        'current_png_metadata_audit':png_audit, 'protected_file_hashes':protected_after,
        'passed':all(checks.values())}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'mapping':REPORT.relative_to(ROOT).as_posix(), 'files':len(records),
                      'current_png_count':len(png_audit), 'checks':checks, 'passed':report['passed']},indent=2))
    assert report['passed'], 'Redaction completed but an audit failed; inspect the mapping without altering its flags'


if __name__ == '__main__':
    main()
