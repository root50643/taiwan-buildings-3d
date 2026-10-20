"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='ba9cfaf8c0c6518e8c5225d3c8116a134a0153007a51037e4344181e02328cd2'
PALETTE=[('neutral_unseen','#AAA79F'),('graywhite_stone','#C1C5C2'),('grayblue_glazing_proxy','#617C89'),('display_plinth','#888C88')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);c=t.mean(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unseen_end_roof_and_simplified_drum_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.0001)&(hi[:,2]<=b+.0001)
 # Photo-supported lake and road-facing vertical stone planes; not unseen east/west ends.
 facade=(abs(n[:,1])>.55)&zz(2.8,18.3)
 paint(facade,1,'two_registered_facades_graywhite_stone')
 # Both glazed slopes and cross-gable are visible in source photographs; no fake PV grid.
 roof=(lo[:,0]>=-54.0001)&(hi[:,0]<=54.0001)&(lo[:,1]>=-10.0001)&(hi[:,1]<=10.0001)&zz(18.1,23)&(n[:,2]>.1)
 paint(roof,2,'existing_pitched_roof_glazing_not_solar_panels')
 paint((lo[:,0]>=-8.2001)&(hi[:,0]<=8.2001)&zz(18.15,23)&np.all(abs(abs(t[:,:,1])-10)<.00015,axis=1),2,'existing_cross_gable_glazing')
 def back(x,y,z,w,h,d):
  mask=(lo[:,0]>=x-w/2-.0001)&(hi[:,0]<=x+w/2+.0001)&zz(z,z+h)
  plane=y+d/2 if y<0 else y-d/2
  paint(mask&np.all(abs(t[:,:,1]-plane)<.00015,axis=1),2,'registered_existing_window_recess_back')
 for sign in [-1,1]:
  for j in range(7):
   for z,h in [(3.3,2.2),(7,2.9),(11.2,2.8)]:back(sign*(29.8+j*4.6),-24.65 if sign<0 else -21.8,z,3.3,h,2.9)
  for xx in [42,47,52,57]:back(sign*xx,21.5,13,3.2,2.6,2.5)
 for y in [-8.5,8.5]:
  for x in np.linspace(-48,48,17):
   if y<0 or abs(x)<23:back(x,y,15.7,4.2,1.6,1.7)
 # Curved north glazing-band back surfaces: interior band and original vertical supports only.
 for sign in [-1,1]:
  rr=np.sqrt((t[:,:,0]-sign*33)**2+(t[:,:,1]-11)**2)
  curved=np.all(abs(rr-8.6)<.0002,axis=1)&(c[:,1]>12)&(abs(c[:,0])>23)
  straight=np.all(abs(t[:,:,1]-19.5)<.00015,axis=1)&(lo[:,0]>= (29.5 if sign>0 else -56.5))&(hi[:,0]<= (56.5 if sign>0 else -29.5))
  for z in [4.2,8.4]:paint((curved|straight)&zz(z,z+2.3),2,'north_lobe_existing_glazing_band_back')
 # Preserve simplified central drum neutral: cannot equate full cylinder with photographed glassbrick.
 paint((lo[:,0]>=-3.5001)&(hi[:,0]<=3.5001)&(lo[:,1]>=-21.5001)&(hi[:,1]<=-14.4999)&zz(2.6,8.9),0,'simplified_central_drum_not_full_glassbrick_inference')
 paint(hi[:,2]<=2.8001,3,'display_base_not_real_ground')
 return color,why

def writezip(path,files):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files:
   info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
def main():
 (A/'qa').mkdir(exist_ok=True);(A/'previews').mkdir(exist_ok=True)
 raw=(R/'model.stl').read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
 tri=np.array([struct.unpack_from('<9f',raw,96+50*i) for i in range(n)],dtype=np.float64).reshape(n,3,3)
 v,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
 colors,why=classify(tri);assert set(colors)==set(range(len(PALETTE)))
 # .17g exactly roundtrips every source float32 value as float64.
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
 model=E.Element('{'+ns+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'});res=E.SubElement(model,'resources');bm=E.SubElement(res,'basematerials',{'id':'20'})
 for name,color in PALETTE:E.SubElement(bm,'base',{'name':name,'displaycolor':color+'FF'})
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'YunTech Student Activity Center original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'student-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Uncalibrated official 2014 and 2017 gallery photographs approximations, not measured material swatches','scope':'Road front 2017 and lake side 2014; unseen ends neutral; roof is glazing not PV; simplified drum not inferred as full glassbrick.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
