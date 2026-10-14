"""Re-encode actual STL renders as RGB PNG without ancillary metadata."""
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
for p in (R/'previews').glob('*.png'):
 Image.open(p).convert('RGB').save(p)
 assert not Image.open(p).info
