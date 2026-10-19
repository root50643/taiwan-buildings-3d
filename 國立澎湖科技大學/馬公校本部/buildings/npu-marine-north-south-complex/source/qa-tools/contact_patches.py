"""Measure all coplanar mating face patches for declared adhesive contacts."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np,trimesh,shapely
from shapely.geometry import Polygon
from manufacturing_qa import tree_for

def main():
 p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',required=True);args=p.parse_args();manifest=Path(args.manifest);data=json.loads(manifest.read_text());meshes={};tol=1e-4
 for part in data['parts']:
  m=trimesh.load_mesh(manifest.parent/part['stl'],process=True);m.apply_transform(part['assembly_transform']);meshes[part['id']]=m
 records=[]
 for rule in data['expected_contacts']:
  a,b=meshes[rule['a']],meshes[rule['b']];ta,tb=a.triangles,b.triangles;na,nb=a.face_normals,b.face_normals
  bs=np.column_stack((tb.min(axis=1)-tol,tb.max(axis=1)+tol));tree=tree_for(bs);groups={};pairs=0
  for i,t in enumerate(ta):
   bound=np.r_[t.min(axis=0)-tol,t.max(axis=0)+tol]
   for j in tree.intersection(tuple(bound)):
    if na[i]@nb[j]>-.99999:continue
    if np.max(abs((tb[j]-t[0])@na[i]))>tol:continue
    drop=int(np.argmax(abs(na[i])));g=Polygon(np.delete(t,drop,axis=1)).intersection(Polygon(np.delete(tb[j],drop,axis=1)))
    if g.area<1e-10:continue
    pairs+=1;normal=na[i];offset=float(normal@t[0]);key=tuple(np.round(normal,6))+(round(offset,4),)
    if key not in groups:groups[key]={'normal':normal,'offset':offset,'drop':drop,'geometries':[]}
    groups[key]['geometries'].append(g)
  planes=[];total=0
  for group in groups.values():
   g=shapely.union_all(group['geometries']);area=float(g.area/abs(group['normal'][group['drop']]));total+=area
   connected=g.buffer(tol,join_style=2);count=len(connected.geoms) if hasattr(connected,'geoms') else 1
   planes.append({'normal':group['normal'].tolist(),'normal_plane_offset_mm':group['offset'],'projection_drop_axis':group['drop'],'contact_area_mm2':area,'patch_count_at_0p0001mm_tolerance':count,'projected_bounds_mm':list(g.bounds)})
  records.append({'a':rule['a'],'b':rule['b'],'mating_triangle_pairs':pairs,'contact_area_mm2':total,'coplanar_groups':planes,'has_area_contact':total>1e-6})
  print(rule['a'],rule['b'],round(total,6),'mm2',flush=True)
 report={'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'method':'All AABB triangle candidates for every declared pair; opposing normals; coplanarity within 0.0001 mm; planar intersections unioned per plane. No triangle sample.','contact_plane_tolerance_mm':tol,'pairs':records,'all_expected_pairs_have_nonzero_mating_area':all(x['has_area_contact'] for x in records),'limitations':'Area is mathematical surface coincidence, not proven glue strength, tolerance, print fit or adhesive accessibility. 0.0001 mm coplanarity tolerance only covers STL coordinate roundoff.'}
 Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf-8')
if __name__=='__main__':main()
