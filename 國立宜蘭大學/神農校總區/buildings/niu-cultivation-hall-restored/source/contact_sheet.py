from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
out=Image.new('RGB',(1800,900),(240,240,236));d=ImageDraw.Draw(out)
try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
except OSError:font=ImageFont.load_default(size=25)
for i,name in enumerate(['oblique','front','entry-detail','rear','left','top']):
    im=Image.open(ROOT/'previews/v1'/f'{name}.png').convert('RGB');im.thumbnail((590,400))
    x=(i%3)*600+(600-im.width)//2;y=(i//3)*450
    out.paste(im,(x,y));d.text(((i%3)*600+16,y+407),name.upper(),font=font,fill=(30,30,30))
out.save(ROOT/'previews/v1/contact-sheet.png')
