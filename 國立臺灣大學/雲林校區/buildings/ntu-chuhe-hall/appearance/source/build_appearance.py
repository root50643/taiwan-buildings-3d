"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='896d817270e39a1e9037c4eb8fe46392c6d3be517d97d8c6a0dc4c3e0e24b2f0'
PALETTE=[('neutral_mixed_walls_entry_louvers_canopy_roofs_and_unknown','#AAA79F'),('source_warm_timber_lawn_wing_screens','#9B5E36'),('source_dark_brown_entrance_and_bay_mullions','#634331'),('source_cream_independent_fascias_bay_frame','#CDCBB8'),('source_muted_graygreen_bay_glazing_proxy','#647372')]
def classify(tri):
 t=tri/(150/158);eps=1e-4;color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_mainwall_entry_back_rear_louvers_canopy_roof_ground_neutral',dtype=object)
 def bs(T,lo,hi,axes=range(3)):
  lo=np.array(lo);hi=np.array(hi);inside=np.all((T>=lo-eps)&(T<=hi+eps),axis=(1,2));sur=np.zeros(len(T),bool)
  for a in axes:
   for v in [lo[a],hi[a]]:sur|=np.all(abs(T[:,:,a]-v)<eps,axis=1)
  return inside&sur
 def paint(mask,k,r,count=None):
  if count is not None:assert mask.sum()==count,(r,mask.sum())
  color[mask]=k;why[mask]=r
 ang=np.deg2rad(32);rot=np.array([[np.cos(ang),-np.sin(ang),0],[np.sin(ang),np.cos(ang),0],[0,0,1]]);u=(t-np.array([-43,11,0]))@rot.T
 for x,count in zip(range(-24,25,3),[14,18,18,18,18,18,18,18,18,22,38,30,0,0,0,0,0]):paint(bs(u,[x-.55,16.9,3],[x+.55,19.5,27]),1,'source2019_existing_exposed_angled_lawn_timber_screen_'+str(x),count)
 for x in [-28,-23,-18,-13,-8]:paint(bs(t,[x-.55,-22.1,3.3],[x+.55,-20.1,30.3]),2,'source2022_2023_entrance_timber_vertical_member',26)
 paint(bs(t,[-30,-22.2,16],[-8,-20.2,17.2]),2,'source_entrance_timber_transom_not_mixed_glass_back',59)
 for x in [20,28,36]:paint(bs(t,[x-.5,-27.5,15.5],[x+.5,-25.7,27]),2,'source_projecting_bay_timber_mullion',24)
 paint(bs(t,[17,-27.5,21],[39,-25.7,22]),2,'source_projecting_bay_timber_transom',52)
 paint(bs(t,[-39.5,-23.5,32],[69.5,23.5,34],[1]),3,'source_front_and_rear_main_fascia_vertical_only',4)
 paint(bs(u,[-29,20.5,27],[29,20.5,29],[1]),3,'source2019_lawn_wing_fascia_only',2)
 paint(bs(t,[15,-27,14],[41,-19,29]),3,'source_projecting_bay_cream_original_outer_frame_surfaces',32)
 paint(bs(t,[17,-25.65,15.5],[39,-25.65,27],[1]),4,'source_projecting_bay_glazing_back_behind_separate_timber_grid',2)
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Chuhe Hall Bounded Timber And Fascia Study original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntuchuhe-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Three complete NTU official photos cameraOriginal2019-10-29,2022-05-19,2023-01-31; filename20230406 notcapture. Warmbrown lawn screens,darkbrown entrance/bay members,cream fascias/frame,muted bay glass proxy','scope':'Exact source-box outer surfaces after inverse150/158scale and angledwing inverse32degree transform. Only12of17 generatedscreens externally exposed after originalunion; no missingbars invented. Mainmixedwall,entryback,rearlouverbands,unmodeledgreenfabricawning,roofs/ground unknownneutral. Unchanged original triangles; not2026currentclaim.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
