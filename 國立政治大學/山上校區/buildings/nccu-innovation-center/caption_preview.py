"""Attach the mandatory historical-version caption; no source pixels used."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
p=Path(sys.argv[1]);im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im)
f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
d.rectangle((0,im.height-46,im.width,im.height),fill=(243,243,239))
d.text((18,im.height-39),'官方PDF外觀平面參考版；攝年未知、非已核2026現況',font=f,fill=(35,40,43))
im.save(p,format='PNG',compress_level=6)
