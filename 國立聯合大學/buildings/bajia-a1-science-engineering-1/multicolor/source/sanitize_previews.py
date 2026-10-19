"""Remove PNG metadata losslessly; retain exact displayed RGBA samples."""
from pathlib import Path
import hashlib, json, struct
from PIL import Image, __version__ as pillow_version

ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
records=[]
for p in sorted((ROOT/'previews').glob('*.png')):
    original=p.read_bytes()
    with Image.open(p) as image:
        before_info=list(image.info)
        rgba=image.convert('RGBA');pixels=rgba.tobytes();size=rgba.size
    fresh=Image.frombytes('RGBA',size,pixels)
    fresh.save(p,format='PNG',compress_level=9)
    with Image.open(p) as check:
        if check.convert('RGBA').tobytes()!=pixels:raise RuntimeError('Pixel samples changed')
        if check.info:raise RuntimeError('Unexpected PNG metadata')
    raw=p.read_bytes();chunks=[];offset=8
    while offset<len(raw):
        length=struct.unpack_from('>I',raw,offset)[0];name=raw[offset+4:offset+8].decode('ascii');chunks.append(name);offset+=length+12
    if not set(chunks)<={'IHDR','IDAT','IEND'}:raise RuntimeError('Ancillary metadata remains')
    records.append({'file':p.relative_to(ROOT).as_posix(),'dimensions_px':size,'removed_info_keys':before_info,'png_chunks_after':chunks,'original_png_sha256':sha(original),'sanitized_png_sha256':sha(raw),'rgba_pixel_sha256_before_and_after':sha(pixels),'rgba_unchanged':True,'private_metadata_present_after':False})
(ROOT/'qa'/'png-metadata-validation.json').write_text(json.dumps({'pillow_version':pillow_version,'method':'Fresh lossless RGBA PNG, no ancillary metadata; pixel bytes checked before and after.','images':records},indent=2),encoding='utf8')
print(json.dumps({'images':len(records),'pixels_unchanged':True,'metadata_removed':True}))
