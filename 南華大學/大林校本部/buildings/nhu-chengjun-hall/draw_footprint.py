#!/usr/bin/env python3
"""Authored geometric diagram; no source pixels. Pillow is optional, not part of mesh rebuild."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).resolve().parent
im=Image.new('RGB',(1280,900),'#f6f5f1');d=ImageDraw.Draw(im)
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
F=font(17);B=font(26)
def text(x,y,s,n=17,color='#253038'):d.text((x,y),s,font=font(n),fill=color)
def box(a,fill,line='#41484e'):
 x0,y0,x1,y1=a;d.rectangle((405+x0*3.8,465-y1*3.8,405+x1*3.8,465-y0*3.8),fill=fill,outline=line,width=2)
text(35,25,'Chengjun Hall - authored plan-aligned massing',26)
text(35,61,'Local directions only. Model mm, not measured architectural scale.')
box((-98,-92,98,92),'#e2e5df','#9ba29e')
box((-89,-80,-53,80),'#c8c8c8');box((53,-80,79,80),'#bdbbc0');box((79,-80,90,80),'#f0d7cf','#9a615f')
box((-53,-27,53,35),'#a9949b');box((-47,-39,47,-27),'#987e87');box((-45,-47,45,-39),'#b7aca0')
for x in (-71,71):d.line((405+x*3.8,465-79*3.8,405+x*3.8,465+79*3.8),fill='#786774',width=3)
text(320,90,'LOCAL REAR +Y');text(299,830,'FRONT / ENTRY -Y')
text(338,241,'OPEN AREA',18,'#35614e');text(312,708,'OPEN APPROACH',18,'#35614e')
text(300,424,'4F HIGHER CORE',20);text(286,455,'topology from 1F-4F')
text(299,582,'PROJECTING PORCH',17,'white');text(376,627,'STEPS')
text(70,785,'LOWER WING',15);text(580,785,'MATCHED WING',15)
x=835;y=116
lines=[('Evidence / deliberate limits',21),('',17),('Plans: two lower long wings and',17),('higher central connection, with',17),('open front/rear areas preserved.',17),('',17),('4F gray wing regions do NOT',17),('prove accessible roof terraces.',17),('',17),('Matched +X wing: three levels,',17),('recessed gallery, pale frames,',17),('red panels, pale gable, pitched roof.',17),('',17),('Front: four piers, porch, steps,',17),('two white-screen levels, upper slots.',17),('',17),('Opposite/rear facades: neutral,',17),('not invented detailed mirror copies.',17),('',17),('Central roof and unseen joints:',17),('unverified simple closure only.',17),('',17),('No BF extrusion, background buildings,',17),('terraces, or white roof framework.',17),('',17),('Purple line: inferred ridge family.',17),('Pink strip: recessed outer gallery.',17),('Bottom rectangle: display base only,',17),('not a building slab or site terrain.',17)]
for s,n in lines:text(x,y,s,n);y+=24
text(35,870,'Authored diagram; no third-party plan pixels. NHU official 39-page PDF physical pp11-14; exact dimensions / compass unknown.',14)
im.save(p/'previews'/'footprint.png')
