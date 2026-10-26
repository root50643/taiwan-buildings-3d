#!/usr/bin/env python3
"""Build color data from exact public legacy STL; never regenerate or repair geometry."""
from pathlib import Path
import argparse,json,shutil,hashlib
import numpy as np
from material_geometry import load_stl,load_materials,bijection,normals,STL_SHA256
from mesh_topology import check_topology
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();src=Path(__file__).resolve().parent;root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
for name in ['model.stl','face-material-map.json','parameters.json','legacy-validation.json']:
 if (src/name).resolve()!=(root/name).resolve():shutil.copyfile(src/name,root/name)
v,f,tri,stored=load_stl(root/'model.stl');mi=load_materials(root);identity=bijection(tri,v[f]);assert np.array_equal(identity,np.arange(len(f)))
normal_delta=float(np.max(np.abs(stored-normals(tri))));assert normal_delta<3e-8
np.savez(root/'mesh-data.npz',vertices=v,faces=f,materials=mi,original_triangle_index=identity)
topology=check_topology(v,f,'unchanged original model.stl');assert topology['all_pass'] and topology['euler_characteristic']==2
audit={'all_pass':True,'source_stl_sha256':STL_SHA256,'stl_bytes':(root/'model.stl').stat().st_size,'source_triangles':len(f),'vertices':len(v),'geometry_changed':False,'source_order_preserved':True,'all_oriented_full_triangle_coordinates_exact':True,'triangle_bijection_complete':True,'independent_normal_max_difference_from_stored':normal_delta,'material_counts':np.bincount(mi,minlength=3).tolist(),'white_door_transom_assignments':0,'excluded_vent_assignments':mi[[5468,5469,5518,5519]].tolist(),'topology':topology,'mesh_repair_performed':False,'limitation':'Topology equals preserved original. Not a physical print test or exact-predicate proof of no global geometric intersections.'}
(root/'qa/geometry-material-validation.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
