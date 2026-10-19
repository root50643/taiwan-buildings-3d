"""Original-model section diagrams and explicit open-void occupancy probes."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np,trimesh,shapely
from shapely.geometry import Point
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',required=True);args=p.parse_args()
 manifest=Path(args.manifest);root=manifest.parent;data=json.loads(manifest.read_text());out=Path(args.output);out.mkdir(exist_ok=True,parents=True)
 meshes=[]
 for part in data['parts']:
  m=trimesh.load_mesh(root/part['stl'],process=True);m.apply_transform(part['assembly_transform']);meshes.append(m)
 heights=[0.6,5,9.5,12.5,16.9,18.5,25,28,40]
 results=[];geoms=[]
 for z in heights:
  polys=[]
  for m in meshes:
   sec=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
   if sec is not None:
    flat,T=sec.to_2D(to_2D=np.eye(4),check=False);polys.extend(flat.polygons_full)
  g=shapely.union_all(polys);geoms.append(g)
  results.append({'z_mm':z,'area_mm2':float(g.area),'polygon_count':len(g.geoms) if hasattr(g,'geoms') else 1,'probes':{'courtyard_60_70':bool(g.covers(Point(60,70))),'under_bridge_88p9_70':bool(g.covers(Point(88.9,70))),'entrance_void_10_40':bool(g.covers(Point(10,40)))}})
 bounds=trimesh.util.concatenate(meshes).bounds
 fig,axes=plt.subplots(3,3,figsize=(12,10),layout='constrained')
 for ax,z,g in zip(axes.flat,heights,geoms):
  for poly in (g.geoms if hasattr(g,'geoms') else [g]):
   if poly.is_empty:continue
   xy=np.asarray(poly.exterior.coords);ax.fill(xy[:,0],xy[:,1],color='#476b72',linewidth=0)
   for ring in poly.interiors:
    xy=np.asarray(ring.coords);ax.fill(xy[:,0],xy[:,1],color='white',linewidth=0)
  ax.set_title(f'Assembly section Z = {z:g} mm');ax.set_aspect('equal');ax.set_xlim(bounds[0,0]-3,bounds[1,0]+3);ax.set_ylim(bounds[1,1]+3,bounds[0,1]-3);ax.tick_params(labelsize=7);ax.set_xlabel('X (mm)',fontsize=7);ax.set_ylabel('Y (mm)',fontsize=7)
 fig.suptitle('Original reconstructed geometry: assembled horizontal sections',fontsize=14)
 fig.savefig(out/'assembly_sections.png',dpi=150,metadata={'Software':'Matplotlib','Description':'Original model section geometry; millimetres; no source pixels'})
 plt.close(fig)
 report={'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'units':'mm','sections':results,'probe_meaning':'true=solid at selected XY point and section Z; false=open. Point probes are examples, not a complete clearance proof.','method':'Every physical part transformed to assembly coordinates, intersected with exact horizontal plane; section polygon union, no source pixels.','limitations':['Cross-sections are mathematical planes, not support toolpath predictions.','No physical print or fit test.']}
 (out/'assembly_sections.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(results))
if __name__=='__main__':main()
