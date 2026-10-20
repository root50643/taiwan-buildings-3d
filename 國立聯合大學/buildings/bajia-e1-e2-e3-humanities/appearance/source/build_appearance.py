"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='6a5a4b4415b5423da6be30f3455de6678f2cd41d35702bd76cf6d72f8e4b94c8'
PALETTE=[('neutral_unseen','#AAA79F'),('warm_cream_structure','#C8C2AF'),('cool_gray_infill','#A0A8A5'),('muted_grayblue_glazing','#657E87'),('brick_endwall','#AF7258'),('brown_rail_proxy','#8B7770'),('navy_PV','#4D6684'),('dark_original_mullions','#59656A'),('pale_bluegray_concrete_frame','#9CB5BC')]
def classify(tri):
 t=tri;lo=t.min(axis=1);hi=t.max(axis=1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'unknown_rear_and_mixed_corridor_backs_neutral',dtype=object)
 def paint(mask,col,reason):color[mask]=col;why[mask]=reason
 def zz(a,b):return (lo[:,2]>=a-.005)&(hi[:,2]<=b+.005)
 def xx(a,b):return (lo[:,0]>=a-.005)&(hi[:,0]<=b+.005)
 def yy(a,b):return (lo[:,1]>=a-.005)&(hi[:,1]<=b+.005)
 def plane(axis,v):return np.all(abs(t[:,:,axis]-v)<.005,axis=1)
 def box(a,b,c,d,e,f):return xx(a,b)&yy(c,d)&zz(e,f)
 paint((plane(1,-9)&xx(-60,-22)&zz(2.8,26))|(plane(1,-5)&xx(-58,60)&zz(2.8,38)),2,'observed_E2_gray_front_proxy_not_entire_glazing')
 paint(plane(0,-60)&yy(-9,16)&zz(2.8,26),4,'observed_E2_left_lower_brick_end_only')
 paint(box(-7,13,-10,16,2.8,46)&(plane(1,-10)|plane(0,-7)|plane(0,13)),1,'observed_E2_open_tower_exterior_cream_not_inner_backs')
 paint(box(-23,-21,-6,1,3,39),1,'original_E2_front_pier_cream')
 for z in [6,16,26]:paint(box(-21,-7,-5.5,-4.1,z-.3,z+1),1,'original_E2_small_floor_edges_cream')
 for z in [6,16,26,36]:paint(box(-4.5,10.5,-10.2,-8.8,z-.1,z+1.2),1,'original_E2_tower_front_landing_cream')
 for x0,x1,y,z,rows,spacing in [(-56,-24,-9,6,2,9),(-49,-25,-5,30,1,8),(14,58,-5,6,3,9)]:
  for k in range(rows):
   for x in np.arange(x0,x1-3,spacing):
    end=min(x+spacing-1.5,x1);mid=(x+end)/2;z0=z+k*10
    paint(xx(x,end)&zz(z0,z0+6)&plane(1,y+1.1),3,'original_E2_discrete_pane_proxy_real_mixed_door_window_grid_simplified')
    paint(box(mid-.4,mid+.4,y-.05,y+1.3,z0-.1,z0+6.1)|box(x-.1,end+.1,y-.05,y+1.3,z0+2.6,z0+3.4),7,'original_E2_bonded_mullions_dark')
 paint(box(-61,-21,-10,17,25.4,27.2)&(n[:,2]>.9),2,'original_E2_left_terrace_paving_gray')
 paint(box(-61,-21,-10,-8.6,27,29)|box(-61,-59.6,-10,17,27,29),5,'existing_thick_parapet_brown_rail_color_proxy_not_open_rail')
 # E3 corridor frames: no glazing on broad mixed corridor backs.
 for z in [16,28,40]:
  paint(box(-41,34,27.8,35,z-1.2,z+.2),1,'original_E3_corridor_floor_edge_cream')
  paint(box(-40,33,28.1,29.4,z+.1,z+1.6),5,'original_E3_thick_rail_approximation_brown')
 for x in [-42,-27,-9,10,31]:paint(box(x,x+1.8,27.8,35,14,52),1,'original_E3_corridor_piers_cream')
 paint(box(34,51,26,49,11.8,61)&(plane(1,26)|plane(0,34)|plane(0,51)),1,'observed_E3_tower_exterior_cream')
 for z in [16,28,40]:paint(box(36,48,25.8,27.1,z,z+1.3),5,'original_E3_tower_thick_rail_proxy')
 paint(box(-9,-7.2,24.8,30,13,40)|box(14,15.8,24.8,30,13,40)|box(-9,15.8,24.8,30,38.3,40),8,'observed_E3_front_bluegray_CONCRETE_frame_not_glass')
 # E1 existing segmented curved frontage and window-back planes.
 def front(x):return -42+.0018*(x-4)**2
 paint(xx(-13,67.02)&yy(-43,-15)&zz(2.8,14)&(n[:,1]<-.2),2,'observed_E1_curved_gray_front_structure')
 xs=np.linspace(-13,67,33)
 for a,b in zip(xs[:-1],xs[1:]):
  if a>-9 and b<64:
   x0=a+.45;x1=b-.35;v=front(a)+1+(t[:,:,0]-x0)*(front(b)-front(a))/(x1-x0)
   paint(xx(x0,x1)&zz(5.4,11.3)&np.all(abs(t[:,:,1]-v)<.012,axis=1),3,'original_E1_curved_window_back_only')
 paint(xx(-13,67.02)&yy(-43,-14)&plane(2,15.7),2,'original_E1_terrace_paving_gray')
 paint(xx(-13,67.02)&yy(-43,-14)&zz(15.5,17.5)&np.all((t[:,:,1]-front(t[:,:,0])>=-.62)&(t[:,:,1]-front(t[:,:,0])<=.72),axis=1),5,'original_E1_thick_solid_parapet_brown_rail_proxy')
 paint(box(-14,3,-57,-32,3,15.7)&(n[:,2]>.9),2,'original_E1_broad_stair_treads_gray')
 paint(box(52,63,-29,-11,15,25.4)&(n[:,2]>.9),2,'original_upper_terrace_stair_treads_gray')
 paint(box(51,69,-15,3,23.5,25.4)&(n[:,2]>.9),2,'original_upper_terrace_paving')
 paint(box(67.5,69,-15,3,25.2,27)|box(51,69,1.7,3,25.2,27),5,'original_upper_terrace_thick_rail_proxy')
 for x0,x1,y0,y1,z,cols,rows in [(-50,-23,-3,14,39.5,4,3),(-2,58,-3,14,37.9,8,3),(-40,33,30,48,52.9,10,3),(-59,-45,30,48,53.1,2,3)]:
  for i in range(cols):
   for j in range(rows):
    x=x0+(x1-x0)*i/cols;y=y0+(y1-y0)*j/rows
    paint(box(x,x+(x1-x0)/cols-.6,y,y+(y1-y0)/rows-.6,z-.1,z+.8)&(n[:,2]>.9),6,'original_discrete_PV_tile_top_only')
 paint(hi[:,2]<=3.0001,0,'neutral_display_base')
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NUU E1 E2 E3 Humanities original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'nuue-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Official E1 E2 E3 2025 gallery photos1/8; uncalibrated proxies','scope':'Observed cream/gray frames, E2 left brick end, discrete simplified E2/E1 pane backs, existing mullions/rail proxies and PV tile tops. Broad E3 corridors and stairbacks NOT glazing; bluegray front frame is concrete. Unknown rear and unsplit E3 brick edge neutral.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
