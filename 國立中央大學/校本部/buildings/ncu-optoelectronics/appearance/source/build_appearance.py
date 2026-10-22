"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='f8b49387d3e9237da92bb6c3b8d7ed89f931f412ddae9494de118acf6694c287'
PALETTE=[('neutral_unresolved_envelope_and_base','#AAA79F'),('dark_grey_green_roof_grid_complete_beams','#456161'),('pale_grey_blue_central_glazing_proxy','#8C9E9E')]
def classify(tri):
 x,y,z=tri[:,:,0],tri[:,:,1],tri[:,:,2];n=len(tri);eps=.002
 roof=np.zeros(n,bool);glass=np.zeros(n,bool)
 for cx in range(-57,58,9):
  low=80-(y+54)*4/34
  roof |= np.all((abs(x-cx)<=.75+eps)&(y>=-54-eps)&(y<=-20+eps)&(z>=low-eps)&(z<=low+1.8+eps),axis=1)
 for cy in [-45,-36,-27]:
  low=80-(cy+54)*4/34
  roof |= np.all((abs(x)<=60+eps)&(abs(y-cy)<=.75+eps)&(z>=low-eps)&(z<=low+1.8+eps),axis=1)
 roof |= np.all((abs(x)<=60+eps)&(abs(y+54)<=1+eps)&(z>=80-eps)&(z<=82+eps),axis=1)
 roof |= np.all((abs(x)<=60+eps)&(abs(y+20)<=1+eps)&(z>=76-eps)&(z<=78+eps),axis=1)
 for cx in range(-31,32,9):
  for z0 in [43,54,65]:
   glass |= np.all((abs(y+47.6)<eps)&(abs(x-cx)<=3.6+eps)&(z>=z0-eps)&(z<=z0+8+eps),axis=1)
 assert not np.any(roof&glass)
 assert roof.sum()==1494 and glass.sum()==42
 color=np.zeros(n,dtype=int);color[roof]=1;color[glass]=2
 why=np.full(n,'neutral_unresolved_walls_side_and_back_deep_grid_roofs_and_base',dtype=object)
 why[roof]='contractor_2010_2011_roof_grid_whole_original_beam_triangle'
 why[glass]='central_21_recess_backplanes_only_opaque_glazing_proxy'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NCU Kuo-Ting Optoelectronics Building limited original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ncu-optoelectronics-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Reiju contractor photographs EXIF 2010-11-04 and 2011-02-09; NCU official disaster PDF photo date unknown; viewed 2026-10-22; uncalibrated opaque display proxies, not 2026 condition','scope':'Only complete roof grid beam triangles and central 21 recess backplanes. No glass roof infill; deep side grids and all remaining surfaces stay neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
