"""Strip private renderer metadata without altering any pixel."""
from pathlib import Path
from PIL import Image
for path in (Path(__file__).resolve().parent/'previews').glob('*.png'):
 with Image.open(path) as im:
  out=Image.new(im.mode,im.size);out.putdata(list(im.getdata()));out.save(path)
