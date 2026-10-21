"""Recolor exact original STL triangles without changing geometry. Python + numpy."""
from pathlib import Path
import struct,hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
A=Path(__file__).resolve().parents[1];R=A.parent
SOURCE_SHA='f38bc5d22f4d5463adbb6e7b3890f3285d468b488a6b19afb77eb2791d1c61e4'
PALETTE=[('neutral_mixed_walls_bands_portholes_lowentry_rearcolumns','#AAA79F'),('source_silvergray_original_roof_and_metal_rim','#B5BAB8'),('source_muted_bluegreen_portal_tower_glazing_proxy','#547C7B'),('source_dark_metal_tower_horizontal_bars','#555F60')]
def classify(tri):
 from manifold3d import Manifold
 from scipy.spatial import ConvexHull,cKDTree
 t=tri;eps=.0001;n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
 color=np.zeros(len(t),dtype=int);why=np.full(len(t),'mixed_pink_brown_walls_porthole_grilles_lowentry_rearcolumns_unknown_neutral',dtype=object)
 def paint(ids,k,r):color[ids]=k;why[ids]=r
 # Only use supporting source planes plus containment, including Boolean-clipped facets.
 sphere=Manifold.sphere(1,128).scale((68,54,13)).translate((0,0,43)).to_mesh64();eq=ConvexHull(np.asarray(sphere.vert_properties)[:,:3]).equations
 ids=np.flatnonzero(np.all(t[:,:,2]>=43.5-eps,axis=1)&(n[:,2]>eps)&(np.ptp(t[:,:,2],axis=1)>eps));assert len(ids)==4152
 _,near=cKDTree(eq[:,:3]).query(n[ids],k=12);res=np.min(np.max(abs(np.einsum('nki,nvi->nkv',eq[near,:3],t[ids])+eq[near,3,None]),axis=2),axis=1);assert res.max()<eps
 points=np.unique(t[ids].reshape(-1,3),axis=0)
 for i in range(0,len(points),128):assert np.max(points[i:i+128]@eq[:,:3].T+eq[:,3])<eps
 paint(ids,1,'source_original_ellipsoid_convex_hull_supporting_plane_and_containment_including_clipped_faces')
 rim=Manifold.cylinder(2.5,1,1,circular_segments=128).scale((68,54,1)).translate((0,0,41)).to_mesh64();eq=ConvexHull(np.asarray(rim.vert_properties)[:,:3]).equations
 cand=np.flatnonzero(np.all((t[:,:,2]>=41-eps)&(t[:,:,2]<=43.5+eps),axis=1));ids=[]
 for i in cand:
  dist=t[i]@eq[:,:3].T+eq[:,3]
  if np.any(np.max(abs(dist),axis=0)<eps) and np.max(dist)<eps:ids.append(i)
 assert len(ids)==831;paint(ids,1,'source_original_convex_metal_rim_boundary_full_triangle_top_edge_soffit')
 roof_mask=color==1
 for x,count in [(-48,203),(48,198)]:
  mask=np.all(abs(t[:,:,1]+40.5)<eps,axis=1)&np.all((t[:,:,0]>=x-5.25-eps)&(t[:,:,0]<=x+5.25+eps)&(t[:,:,2]>=13-eps)&(t[:,:,2]<=45+eps),axis=1);assert mask.sum()==2;paint(mask,2,'source_front_tower_discrete_glazing_back_not_opaque_wall')
  ids=set()
  for z in np.arange(14,45,3):
   lo=np.array([x-5.8,-43.2,z]);hi=np.array([x+5.8,-40.8,z+1]);inside=np.all((t>=lo-eps)&(t<=hi+eps),axis=(1,2));surface=np.zeros(len(t),bool)
   for a in range(3):
    for v in [lo[a],hi[a]]:surface|=np.all(abs(t[:,:,a]-v)<eps,axis=1)
   ids.update(np.flatnonzero(inside&surface).tolist())
  assert len(ids)==count;paint(sorted(ids),3,'source_front_tower_original_projecting_metal_bar_box_surfaces_only')
 overlap=roof_mask&(color==3);assert overlap.sum()==1
 color[overlap]=0;why[overlap]='coincident_roof_rim_and_tower_bar_joint_unresolved_neutral'
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
 obj=E.SubElement(res,'object',{'id':'1','type':'model','pid':'20','pindex':'1','name':'NTU Sports Center Roof And Entrance Towers Only original surface'});mesh=E.SubElement(obj,'mesh');vs=E.SubElement(mesh,'vertices');ts=E.SubElement(mesh,'triangles')
 for p in v:E.SubElement(vs,'vertex',dict(zip('xyz',[format(float(x),'.17g') for x in p])))
 for t,col in zip(f,colors):E.SubElement(ts,'triangle',{'v1':str(t[0]),'v2':str(t[1]),'v3':str(t[2]),'pid':'20','p1':str(col),'p2':str(col),'p3':str(col)})
 E.SubElement(E.SubElement(model,'build'),'item',{'objectid':'1'})
 writezip(A/'ntusports-appearance.3mf',[
 ('[Content_Types].xml',b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
 ('_rels/.rels',b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
 ('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))])
 (A/'palette.json').write_text(json.dumps({'materials':[{'id':n,'srgb':c} for n,c in PALETTE],'colors':'Two complete official NTU photos: PE venue front captureunknown with blank EXIF placeholders; visitorcenter rear Original2012-03-15. Silvermetal roof and two portal tower glazing/metalbar accents only','scope':'Original sphere/rim convex supporting plane and allvertex containment includes clippedtriangles; no ellipsoid equality holes. Pink/brown mixedwalls,portholegrilles,lowentrywindows,rearcolumns and bands neutral. Original rooftruss omitted,not added. No current2026claim; unchangedSTL.'},ensure_ascii=False,indent=2)+'\n')
 (A/'face-materials.json').write_text(json.dumps({'source_stl_sha256':SOURCE_SHA,'vertices':len(v),'triangles':len(f),'original_triangle_order_unchanged':True,'face_material_indices':colors.tolist(),'face_reasons':why.tolist()},indent=2)+'\n')
 print(json.dumps({'faces':len(f),'vertices':len(v),'materials':dict(zip([x[0] for x in PALETTE],np.bincount(colors).tolist()))}))
if __name__=='__main__':main()
